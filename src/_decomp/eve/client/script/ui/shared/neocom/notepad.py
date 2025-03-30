#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\notepad.py
import blue
import evelink
import uthread
import localization
from bannedwords.client import bannedwords
from carbonui import uiconst
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import SortListOfTuples
from carbonui.uicore import uicore
from carbonui.control.button import Button
from eve.client.script.ui.control.divider import Divider
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.userentry import User
from eve.client.script.ui.util.utilWindows import NamePopup
from menu import MenuLabel
from utillib import KeyVal
from eve.common.lib import appConst as const

class NotepadWindow(Window):
    __guid__ = 'form.Notepad'
    __notifyevents__ = []
    default_width = 400
    default_height = 300
    default_windowID = 'notepad'
    default_captionLabelPath = 'UI/Notepad/Notepad'
    default_iconNum = 'res:/ui/Texture/WindowIcons/notepad.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetMinSize((350, 200))
        self.sr.main.padding = const.defaultPadding
        self.sr.nav = Container(name='nav', align=uiconst.TOLEFT, width=settings.user.ui.Get('notepadscrollistwidth', 128), parent=self.sr.main, idx=0)
        divider = Divider(name='divider', align=uiconst.TOLEFT, idx=1, width=const.defaultPadding, parent=self.sr.main, state=uiconst.UI_NORMAL)
        divider.Startup(self.sr.nav, 'width', 'x', 100, 256)
        self.sr.navbuttons = Container(name='navbuttons', align=uiconst.TOBOTTOM, parent=self.sr.nav, height=38)
        self.sr.newfolder = Button(parent=self.sr.navbuttons, label=localization.GetByLabel('UI/Notepad/NewFolder'), padTop=4, align=uiconst.TOTOP, func=self.NewFolderClick)
        self.sr.newnote = Button(parent=self.sr.navbuttons, label=localization.GetByLabel('UI/Notepad/NewNote'), padTop=4, align=uiconst.TOTOP, func=self.NewNote, args=(0,))
        self.sr.navbuttons.height = sum([ each.height + each.padTop + each.padBottom for each in self.sr.navbuttons.children ]) + 4
        self.sr.senderlist = Scroll(name='senderlist', parent=self.sr.nav)
        self.sr.senderlist.OnDelete = self.OnDelete
        self.sr.senderlist.multiSelect = 0
        self.sr.note = Container(name='notecontainer', align=uiconst.TOALL, parent=self.sr.main, pos=(0, 0, 0, 0))
        self.sr.titlecont = Container(name='titlecontainer', align=uiconst.TOTOP, height=48, parent=self.sr.note)
        self.sr.icon = Icon(parent=self.sr.titlecont, pos=(0, 0, 32, 32))
        self.sr.titletext = EveLabelMedium(parent=self.sr.titlecont, align=uiconst.TOTOP, padding=(40, 5, 5, 0))
        self.sr.titletext.OnSizeChanged = self.OnTitleSizeChanged
        self.sr.browser = EditPlainText(parent=self.sr.note, showattributepanel=1, counterMax=3900, countWithTags=True)
        self.sr.browser.sr.window = self
        self.sr.browser.allowPrivateDrops = 1
        self.OnScale_ = self._OnResize
        divider.OnSizeChanging = self.OnDividerMove
        self.starting = 1
        import log
        log.LogInfo('Starting Notepad')
        self.folders = {}
        self.notes = {}
        self.charnotes = {}
        self.settings = {}
        self.settingStrs = {}
        self.notedata = {}
        self.lastid = 0
        uthread.new(self.LoadNotesData)

    def OnTitleSizeChanged(self, *args, **kwds):
        self.sr.titlecont.height = max(48, self.sr.titletext.textheight + self.sr.titletext.padTop * 2)

    def LoadNotesData(self):
        notes = sm.RemoteSvc('charMgr').GetOwnerNoteLabels()
        self.folderIDs = []
        badNotes = [ note for note in notes if note.label[0] not in ('I', 'N', 'S') ]
        for entry in notes:
            if entry.label[0] in ('I', 'N') and entry.label[1] == ':':
                n = KeyVal()
                n.noteID = entry.noteID
                n.text = None
                if entry.label[0] == 'N':
                    n.label = entry.label[2:]
                    self.notes['N:' + str(entry.noteID)] = n
            if entry.label.startswith('S:'):
                label = entry.label[2:]
                if self.settings.has_key(label):
                    self.settings[label].append(entry.noteID)
                else:
                    self.settings[label] = [entry.noteID]

        parallelCalls = []
        for note in badNotes:
            parallelCalls.append((sm.RemoteSvc('charMgr').RemoveOwnerNote, (note.noteID,)))

        if len(parallelCalls):
            uthread.parallel(parallelCalls)
        folders = self.GetSetting('Folders')
        if folders is not None:
            for entry in folders.split('|'):
                tmp = entry.split('::')
                if len(tmp) != 4:
                    continue
                id, _type, parentID, label = tmp
                n = KeyVal()
                n.type = _type
                if parentID == 'None':
                    parentID = 0
                n.parent = int(parentID)
                n.data = label
                self.folders[int(id)] = n
                self.lastid = max(self.lastid, int(id))

        else:
            n = KeyVal()
            n.type = 'F'
            n.parent = 0
            n.data = localization.GetByLabel('UI/Notepad/Main')
            self.folders[1] = n
            self.lastid = 1
        self.starting = 0
        self.LoadNotes()
        self.sr.autosaveTimer = AutoTimer(60000, self.SaveNote)
        self.activeNode = None
        self.ShowNote(settings.char.notepad.Get('activeNote', None))

    def CloseByUser(self, *args):
        if not self.SaveNote():
            return
        settings.user.ui.Set('notepadscrollistwidth', self.sr.nav.width)
        self.SaveFolders()
        Window.CloseByUser(self)

    def SaveFolders(self):
        folderstr = ''
        for key, value in self.folders.items():
            folderstr += '%s::%s::%s::%s|' % (key,
             value.type,
             value.parent,
             value.data)

        uthread.new(self.SetSetting, 'Folders', folderstr)

    def SetSetting(self, id, string):
        if self.settingStrs.has_key(id) and self.settingStrs[id] == string:
            return
        if self.settings.has_key(id):
            dbIDs = self.settings[id]
            dbIDs.sort()
        else:
            dbIDs = []
        idStr = 'S:' + str(id)
        newIDs = []
        while len(string) > 0:
            part = string[:6000]
            string = string[6000:]
            if len(dbIDs):
                noteID = int(dbIDs.pop(0))
                sm.RemoteSvc('charMgr').EditOwnerNote(noteID, idStr, part)
            else:
                noteID = sm.RemoteSvc('charMgr').AddOwnerNote(idStr, part)
            newIDs.append(noteID)

        parallelCalls = []
        for noteID in dbIDs:
            parallelCalls.append((sm.RemoteSvc('charMgr').RemoveOwnerNote, (int(noteID),)))

        if len(parallelCalls):
            uthread.parallel(parallelCalls)
        self.settings[id] = newIDs

    def GetSetting(self, id):
        if self.settingStrs.has_key(id):
            return self.settingStrs[id]
        if not self.settings.has_key(id):
            return None
        parallelCalls = []
        for noteID in self.settings[id]:
            parallelCalls.append((sm.RemoteSvc('charMgr').GetOwnerNote, (int(noteID),)))

        if len(parallelCalls):
            notes = uthread.parallel(parallelCalls)
        self.settingStrs[id] = ''
        for note in notes:
            self.settingStrs[id] += note[0].note

        return self.settingStrs[id]

    def WriteNote(self, name, text, folderID, noteID = None):
        if not noteID:
            noteID = sm.RemoteSvc('charMgr').AddOwnerNote('N:' + name, '<br>')
        self.AddNote(folderID, 'N', noteID)
        n = KeyVal()
        n.noteID = noteID
        n.label = name
        n.text = text
        self.notes['N:' + str(noteID)] = n
        uthread.pool('notepad::SetNote', sm.RemoteSvc('charMgr').EditOwnerNote, int(noteID), 'N:' + self.notes['N:' + str(noteID)].label, text)
        return noteID

    def GetNotesByType(self, t = 'N'):
        notes = []
        for n in self.notes:
            if n.find(t + ':') == 0:
                v = self.notes[n]
                v.parentID = self.GetParentFolder(v.noteID)
                v.parentName = ''
                parent = self.folders.get(v.parentID)
                if parent:
                    v.parentName = parent.data
                notes.append(v)

        return notes

    def GetFolders(self):
        folders = []
        for f in self.folders:
            folder = self.folders[f]
            if folder.type == 'F':
                v = KeyVal()
                v.noteID = f
                v.label = folder.data
                folders.append(v)

        return folders

    def GetNoteText(self, noteID):
        ret = None
        ret = note = self.notes.get('N:' + str(noteID), None)
        if not note or note.text is None:
            _note = sm.RemoteSvc('charMgr').GetOwnerNote(noteID)
            note = KeyVal()
            note.text = _note[0].note.strip()
            note.label = _note[0].label[2:]
            self.notes['N:' + str(noteID)].text = note.text
            self.notes['N:' + str(noteID)].label = note.label
            ret = note
        return ret

    def _OnResize(self, *etc):
        self.OnDividerMove()

    def OnDividerMove(self, *etc):
        if not self.destroyed:
            self.sr.nav.width = max(100, min(self.sr.nav.width, self.displayWidth - 154))

    def GoTo(self, URL, data = None, args = {}, scrollTo = None):
        uicore.cmd.OpenBrowser(URL, data=data, args=args)

    def LoadNotes(self):
        while self.starting:
            blue.pyos.BeNice()

        scrolllist = []
        notes = self.GetNotes(0)
        for id, n in notes.items():
            groupID = ('notepad', id)
            scrolllist.append((n.data.lower(), GetFromClass(ListGroup, {'GetSubContent': self.GetGroupSubContent,
              'label': n.data,
              'id': groupID,
              'groupItems': self.GroupGetContentIDList(groupID),
              'iconMargin': 18,
              'showlen': 1,
              'state': 0,
              'sublevel': 0,
              'MenuFunction': self.GroupMenu,
              'allowGuids': ['listentry.User',
                             'listentry.Sender',
                             'listentry.PlaceEntry',
                             'listentry.NoteItem'],
              'DropData': self.GroupDropNode,
              'ChangeLabel': self.GroupChangeLabel,
              'DeleteFolder': self.GroupDeleteFolder,
              'GetContentIDList': self.GroupGetContentIDList,
              'CreateEntry': self.GroupCreateEntry,
              'RefreshScroll': self.RefreshNotes})))

        scrolllist = SortListOfTuples(scrolllist)
        scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetAllFolderContent,
         'label': localization.GetByLabel('UI/Notepad/AllNotes'),
         'id': ('All Notes', 0),
         'groupItems': self.notes,
         'iconMargin': 18,
         'showlen': 1,
         'state': 0,
         'sublevel': 0,
         'showicon': 'res:/ui/Texture/WindowIcons/notegroup.png',
         'state': 'locked'}))
        if not self.destroyed:
            self.sr.senderlist.Load(fixedEntryHeight=17, contentList=scrolllist, scrollTo=self.sr.senderlist.GetScrollProportion())
            self.sr.senderlist.hiliteSorted = 0

    def RefreshNotes(self):
        self.LoadNotes()

    def GetAllFolderContent(self, nodedata, newitems = 0):
        scrolllist = []
        for key, note in self.notes.iteritems():
            noteID = 'N:' + str(note.noteID)
            entry = GetFromClass(NoteItem, self.GetNoteItemData(noteID=noteID, noteType='NA'))
            if entry is not None:
                scrolllist.append((note.label.lower(), entry))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def GetGroupSubContent(self, nodedata, newitems = 0):
        scrolllist = []
        notelist = self.GetNotes(nodedata.id[1])
        if len(notelist):
            qi = 1
            NoteListLength = len(notelist)
            for id, note in notelist.items():
                entry = self.GroupCreateEntry((note.data, id), nodedata.sublevel + 1)
                if entry is not None:
                    scrolllist.append((entry.label.lower(), entry))

            if len(nodedata.groupItems) != len(scrolllist):
                nodedata.groupItems = self.GroupGetContentIDList(nodedata.id)
        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def GroupMenu(self, node):
        m = []
        if node.sublevel < 5:
            m.append((MenuLabel('UI/Notepad/NewFolder'), self.NewFolder, (node.id[1], node)))
        m.append((MenuLabel('UI/Notepad/NewNote'), self.NewNote, (node.id[1], node)))
        return m

    def GroupDropNode(self, id, nodes):
        for node in nodes:
            nodeMoved = False
            if node.__guid__ in ('listentry.User', 'listentry.Sender') and node.charID != eve.session.charid:
                self.AddNote(id[1], 'I', node.charID)
                nodeMoved = True
            if node.__guid__ == 'listentry.NoteItem' and not self.NoteAlreadyExistsInFolder(node.noteID, id[1]):
                noteID = node.noteID
                if noteID in self.notes:
                    noteID = self.notes[noteID].noteID
                self.AddNote(id[1], 'N', str(noteID))
                nodeMoved = True
            if nodeMoved and not uicore.uilib.Key(uiconst.VK_SHIFT):
                if node.id:
                    self.RemoveFolder(node.id[1], ask=0)

        self.LoadNotes()

    def GroupChangeLabel(self, id, newname):
        self.RenameFolder(id[1], name=newname)

    def GroupDeleteFolder(self, id):
        noteID = id[1]
        parentID = self.GetParentFolder(noteID)
        notes = self.GetNotes(noteID)
        for id, note in notes.items():
            if note.type == 'F':
                self.GroupDeleteFolder((0, id))
                continue
            self.DeleteFolderNote(id)

        self.DeleteFolderNote(noteID)
        self.LoadNotes()
        self.SaveFolders()

    def GroupCreateEntry(self, id, sublevel):
        note, id = self.folders[id[1]], id[1]
        if note.type == 'F':
            groupID = ('notepad', id)
            return GetFromClass(ListGroup, {'GetSubContent': self.GetGroupSubContent,
             'label': note.data,
             'id': groupID,
             'groupItems': self.GroupGetContentIDList(groupID),
             'iconMargin': 18,
             'showlen': 1,
             'state': 0,
             'sublevel': sublevel,
             'MenuFunction': self.GroupMenu,
             'allowGuids': ['listentry.User', 'listentry.Sender', 'listentry.NoteItem'],
             'DropData': self.GroupDropNode,
             'ChangeLabel': self.GroupChangeLabel,
             'DeleteFolder': self.GroupDeleteFolder,
             'GetContentIDList': self.GroupGetContentIDList,
             'CreateEntry': self.GroupCreateEntry,
             'RefreshScroll': self.RefreshNotes})
        if note.type == 'I':
            charinfo = cfg.eveowners.Get(note.data)
            return GetFromClass(User, {'charID': int(note.data),
             'id': (note.data, id),
             'info': charinfo,
             'color': None,
             'GetMenu': self.GetCharMenu,
             'OnClick': self.OnCharClick,
             'sublevel': sublevel,
             'noteID': 'I:' + str(note.data),
             'label': charinfo.name})
        if note.type == 'N':
            noteID = 'N:' + str(note.data)
            if noteID in self.notes:
                return GetFromClass(NoteItem, self.GetNoteItemData(noteID=noteID, noteType='N', sublevel=sublevel, folderID=id))
        del self.folders[id]

    def GetNoteItemData(self, noteID, noteType, sublevel = 1, folderID = None):
        note = self.notes[noteID]
        return {'itemID': None,
         'typeID': None,
         'id': (note.label, folderID or noteID),
         'label': note.label,
         'sublevel': sublevel,
         'noteID': noteID,
         'type': noteType,
         'ignoreRightClick': 1,
         'get_link': lambda : evelink.Link(url=format_note_url(noteID), text=note.label),
         'is_private': True}

    def GroupGetContentIDList(self, id):
        ids = self.GetNotes(id[1])
        return [ (self.folders[id].data, id) for id in ids ]

    def GetCharMenu(self, node):
        m = [None] + [(localization.GetByLabel('UI/Notepad/RemoveCharacter'), self.RemoveFolder, (node.id[1],))]
        return m

    def OnDelete(self, *args):
        if not self.destroyed:
            sel = self.sr.senderlist.GetSelected()
            for entry in sel[:]:
                if not entry.noteID:
                    continue
                if entry.noteID.startswith('F'):
                    self.GroupDeleteFolder(entry.id)
                elif entry.noteID.startswith('N') and entry.type == 'NA':
                    self.DeleteNote(entry.id[1])
                else:
                    self.RemoveFolder(entry.id[1])

            self.LoadNotes()

    def OnCharClick(self, entry):
        self.ShowNote(entry.sr.node.noteID)

    def OnBookmarkClick(self, entry):
        self.ShowNote(entry.sr.node.noteID)

    def ShowNote(self, id, force = 0):
        while getattr(self.sr.browser, 'loading', 0):
            blue.pyos.synchro.Yield()

        if not force and hasattr(self, 'activeNode') and id is not None and self.activeNode == id:
            return True
        if not force and not self.SaveNote():
            return False
        if id is None or not id.upper().startswith('I:') and str(id) not in self.notes:
            self.sr.titletext.text = (localization.GetByLabel('UI/Notepad/GeneralInformation'),)
            self.sr.icon.LoadIcon('res:/ui/Texture/WindowIcons/notepad.png')
            self.sr.icon.width = self.sr.icon.height = 32
            self.sr.browser.SetValue(localization.GetByLabel('UI/Notepad/NotepadIntro'))
            self.sr.browser.ReadOnly()
            self.activeNote = None
            return True
        self.sr.browser.Editable()
        noteID = id.split(':')
        if len(noteID) != 2:
            return True
        t, id = noteID
        if not force and self.activeNode == t + ':' + str(id):
            return True
        if t == 'I':
            charid = int(id)
            note = sm.RemoteSvc('charMgr').GetNote(charid)
            charinfo = cfg.eveowners.Get(charid)
            sm.GetService('photo').GetPortrait(charid, 64, self.sr.icon)
            self.sr.titletext.text = charinfo.name
            self.sr.browser.SetValue(note)
        if t == 'N':
            if 'N:' + str(id) in self.notes:
                noteID = int(id)
                if self.notes['N:' + str(id)].text is None:
                    note = sm.RemoteSvc('charMgr').GetOwnerNote(noteID)
                    self.notes['N:' + str(id)].text = note[0].note.strip()
                    self.notes['N:' + str(id)].label = note[0].label[2:]
                self.sr.icon.LoadIcon('res:/ui/Texture/WindowIcons/note.png')
                self.sr.icon.SetSize(32, 32)
                self.sr.titletext.text = self.notes['N:' + str(id)].label
                self.sr.browser.SetValue(self.notes['N:' + str(id)].text)
        self.activeNode = t + ':' + str(id)
        settings.char.notepad.Set('activeNote', self.activeNode)
        uicore.registry.SetFocus(self.sr.browser)
        return True

    def SaveNote(self, *args):
        if self.destroyed:
            self.sr.autosaveTimer = None
            return
        if getattr(self, 'activeNode', None) is not None:
            t, id = self.activeNode.split(':')
            txt = self.sr.browser.GetValue()
            if len(txt) > 3900:
                return not eve.Message('NoteTooLong', {'total': len(txt)}, uiconst.YESNO) == uiconst.ID_YES
            if t == 'I':
                uthread.pool('notepad::SetNote', sm.RemoteSvc('charMgr').SetNote, int(id), txt)
            if t == 'N':
                if 'N:' + str(id) in self.notes and self.notes['N:' + str(id)].text != txt:
                    self.notes['N:' + str(id)].text = txt
                    uthread.pool('notepad::SetNote', sm.RemoteSvc('charMgr').EditOwnerNote, int(id), 'N:' + self.notes['N:' + str(id)].label, txt)
        return True

    def GetNotes(self, folderID):
        notes = {}
        for id, n in self.folders.iteritems():
            if n.parent != folderID:
                continue
            notes[id] = n

        return notes

    def GetNote(self, noteID):
        if noteID in self.folders.keys():
            return self.folders[noteID]

    def GetParentFolder(self, nodeID):
        n = self.folders.get(nodeID, None)
        if n:
            return n.parent
        else:
            return

    def RenameFolder(self, folderID = 0, entry = None, name = None, *args):
        if name is None:
            ret = NamePopup(localization.GetByLabel('UI/Notepad/FolderName'), localization.GetByLabel('UI/Notepad/TypeNewFolderName'), maxLength=20)
            if ret is None:
                return self.folders[folderID].data
            name = ret
        bannedwords.check_words_allowed(name)
        if self.AlreadyExists('F', name):
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Notepad/FolderAlreadyExists')})
            return
        self.folders[folderID].data = name
        return name

    def NewFolder(self, folderID = 0, node = None, *args):
        ret = NamePopup(localization.GetByLabel('UI/Notepad/FolderName'), localization.GetByLabel('UI/Notepad/TypeNewFolderName'), maxLength=20)
        if ret is not None:
            name = ret
            bannedwords.check_words_allowed(name)
            if self.AlreadyExists('F', name):
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Notepad/FolderAlreadyExists')})
                return
            self.AddNote(folderID, 'F', name)
            data = {'label': name,
             'folderid': self.lastid,
             'parent': folderID}
            self.LoadNotes()
            self.SaveFolders()
            return data

    def NewFolderClick(self, *args):
        self.NewFolder()

    def RemoveFolder(self, folderID = 0, entry = None, ask = 1):
        if folderID in self.folders:
            if not ask or eve.Message('DeleteEntry', {}, uiconst.YESNO) == uiconst.ID_YES:
                if self.activeNode == self.folders[folderID].type + ':' + str(self.folders[folderID].data):
                    self.activeNode = None
                    self.ShowNote(None)
                parent = self.GetParentFolder(folderID)
                del self.folders[folderID]
                self.LoadNotes()

    def NewNote(self, folderID = 0, node = None, *args):
        ret = NamePopup(localization.GetByLabel('UI/Notepad/NoteName'), localization.GetByLabel('UI/Notepad/TypeNewNoteLabel'), maxLength=80)
        if ret is not None:
            name = ret
            if self.AlreadyExists('N', name):
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Notepad/NoteAlreadyExists')})
                return
            noteID = sm.RemoteSvc('charMgr').AddOwnerNote('N:' + name, '<br>')
            if folderID:
                self.AddNote(folderID, 'N', noteID)
            n = KeyVal()
            n.noteID = noteID
            n.label = name
            n.text = '<br>'
            self.notes['N:' + str(noteID)] = n
            self.LoadNotes()
            self.ShowNote('N:' + str(noteID))

    def RenameNote(self, noteID):
        if noteID in self.folders:
            noteID = self.folders[noteID].type + ':' + str(self.folders[noteID].data)
        if noteID not in self.notes:
            return
        ret = NamePopup(localization.GetByLabel('UI/Notepad/NoteName'), localization.GetByLabel('UI/Notepad/TypeNewNoteLabel'), self.notes[noteID].label, maxLength=80)
        if ret is not None:
            if self.AlreadyExists('N', ret):
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Notepad/NoteAlreadyExists')})
                return
            self.notes[noteID].label = ret
            sm.RemoteSvc('charMgr').EditOwnerNote(self.notes[noteID].noteID, 'N:' + ret)
            self.LoadNotes()
            if getattr(self, 'activeNode', None) == noteID:
                self.sr.titletext.text = ret

    def NoteAlreadyExistsInFolder(self, noteID, folderID):
        notesInFolder = self.GetNotes(folderID)
        noteIdsInFolder = [ n.data for n in notesInFolder.itervalues() ]
        actualId = noteID
        if noteID in self.notes:
            actualId = self.notes[noteID].noteID
        if str(actualId) in noteIdsInFolder:
            return True
        else:
            return False

    def AlreadyExists(self, type, name):
        if type == 'N':
            for key, value in self.notes.iteritems():
                if value.label == name:
                    return True

        if type == 'F':
            for key, value in self.folders.iteritems():
                if value.type == type and value.data == name:
                    return True

        return False

    def AddNote(self, parent, type, data):
        self.lastid += 1
        n = KeyVal()
        n.type = type
        n.parent = parent
        n.data = data
        self.folders[self.lastid] = n

    def DeleteFolderNote(self, noteID):
        del self.folders[noteID]

    def DeleteNote(self, noteID):
        if noteID in self.notes:
            if eve.Message('DeleteNote', {}, uiconst.YESNO) == uiconst.ID_YES:
                if self.activeNode == noteID:
                    self.activeNode = None
                    self.ShowNote(None)
                t, id = noteID.split(':')
                for key, value in self.folders.items():
                    if value.type == t and str(value.data) == id:
                        del self.folders[key]

                note = self.notes[noteID]
                sm.RemoteSvc('charMgr').RemoveOwnerNote(int(note.noteID))
                del self.notes[noteID]
                self.LoadNotes()


class NoteItem(Generic):
    __guid__ = 'listentry.NoteItem'
    isDragObject = True

    def Startup(self, *args):
        Generic.Startup(self, *args)
        self.sr.icon = Icon(icon='res:/ui/Texture/WindowIcons/note.png', parent=self, left=0, top=-4, size=24, ignoreSize=True)

    def Load(self, node):
        Generic.Load(self, node)
        sublevelCorrection = self.sr.node.scroll.sr.get('sublevelCorrection', 0)
        sublevel = max(0, node.Get('sublevel', 0) - sublevelCorrection)
        self.sr.icon.state = uiconst.UI_NORMAL
        self.sr.label.left = 24 + max(0, sublevel * 16)
        self.sr.icon.left = 0 + max(0, sublevel * 16)
        self.sr.label.text = node.label
        self.sr.label.Update()

    def OnClick(self, *args):
        if self.sr.node:
            if not uicore.uilib.Key(uiconst.VK_CONTROL):
                noteWindow = NotepadWindow.GetIfOpen()
                if noteWindow and not noteWindow.ShowNote(self.sr.node.noteID):
                    return
            self.sr.node.scroll.SelectNode(self.sr.node)

    def GetMenu(self):
        m = Generic.GetMenu(self)
        noteWindow = NotepadWindow.Open()
        if self.sr.node.type == 'N':
            m += [(MenuLabel('UI/Notepad/RenameNote'), noteWindow.RenameNote, (self.sr.node.id[1],))]
            m += [(MenuLabel('UI/Notepad/RemoveNote'), noteWindow.RemoveFolder, (self.sr.node.id[1],))]
        if self.sr.node.type == 'NA':
            m += [(MenuLabel('UI/Notepad/RenameNote'), noteWindow.RenameNote, (self.sr.node.id[1],))]
            m += [(MenuLabel('UI/Notepad/DeleteNote'), noteWindow.DeleteNote, (self.sr.node.id[1],))]
        return m

    def GetHeight(self, *args):
        return 18

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes


LINK_SCHEME = 'note'

def register_link_handlers(registry):
    registry.register(LINK_SCHEME, handle_note_link, hint='UI/Notepad/ShowNote')


def handle_note_link(url):
    note_id = parse_note_url(url)
    note_window = NotepadWindow.Open()
    note_window.ShowNote(note_id)


def parse_note_url(url):
    return url[url.index(':') + 1:]


def format_note_url(note_id):
    return u'{}:{}'.format(LINK_SCHEME, note_id)
