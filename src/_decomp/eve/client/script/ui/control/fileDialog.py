#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\fileDialog.py
import ctypes
import os
import blue
import localization
import utillib
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import eveIcon, eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
SELECT_FILES = 0
SELECT_FOLDERS = 1
SELECT_FILESANDFOLDERS = 2

class FileDialogEntry(Generic):
    __guid__ = 'listentry.FileDialog'

    def Startup(self, *args):
        Generic.Startup(self)
        self.sr.icon = eveIcon.Icon(icon='res:/ui/Texture/WindowIcons/smallfolder.png', parent=self, pos=(6, 0, 16, 16), ignoreSize=1)

    def Load(self, node):
        Generic.Load(self, node)
        if self.sr.node.isDir:
            self.sr.icon.state = uiconst.UI_DISABLED
        elif self.sr.icon:
            self.sr.icon.state = uiconst.UI_HIDDEN


class FileDialog(Window):
    __guid__ = 'form.FileDialog'
    default_path = None
    default_fileExtensions = None
    default_multiSelect = False
    default_selectionType = SELECT_FILES
    default_fixedWidth = 430
    default_fixedHeight = 400
    _ok_button = None

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        path = attributes.path
        fileExtensions = attributes.fileExtensions
        multiSelect = attributes.multiSelect or self.default_multiSelect
        selectionType = attributes.selectionType or self.default_selectionType
        if not multiSelect:
            caption = {SELECT_FILES: localization.GetByLabel('UI/Control/FileDialog/SelectFile'),
             SELECT_FOLDERS: localization.GetByLabel('UI/Control/FileDialog/SelectFolder'),
             SELECT_FILESANDFOLDERS: localization.GetByLabel('UI/Control/FileDialog/SelectFileOrfolder')}.get(selectionType)
        else:
            caption = {SELECT_FILES: localization.GetByLabel('UI/Control/FileDialog/SelectFiles'),
             SELECT_FOLDERS: localization.GetByLabel('UI/Control/FileDialog/SelectFolders'),
             SELECT_FILESANDFOLDERS: localization.GetByLabel('UI/Control/FileDialog/SelectFilesOrFolders')}.get(selectionType)
        if fileExtensions:
            caption = localization.GetByLabel('UI/Control/FileDialog/CaptionWithFileExtensions', caption=caption, fileExtensions=localization.formatters.FormatGenericList(fileExtensions))
        self.SetCaption(caption)
        self.selectionType = selectionType
        if fileExtensions:
            self.fileExtensions = [ f.replace('.', '').lower() for f in fileExtensions ]
        else:
            self.fileExtensions = None
        topCont = Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 40), padding=(0, 20, 0, 0))
        icon = eveIcon.Icon(icon='res:/ui/Texture/WindowIcons/smallfolder.png', parent=self.sr.main, pos=(3, 16, 28, 28), ignoreSize=1)
        options = self.GetAvailableDrives()
        self.sr.pathEdit = SingleLineEditText(name='currentLocationEdit', parent=topCont, pos=(38,
         0,
         290 if options else 350,
         0), label=localization.GetByLabel('UI/Common/Location'))
        self.sr.pathEdit.OnReturn = self.OnPathEnteredIntoEdit
        if options:
            self.sr.driveSelectCombo = Combo(parent=self.sr.main, label=localization.GetByLabel('UI/Control/FileDialog/Drive'), options=options, name='driveSelectCombo', select=None, callback=self.OnDriveSelected, pos=(340, 22, 0, 0), width=60, align=uiconst.TOPLEFT)
        self.sr.standardBtns = ButtonGroup(parent=self.content, align=uiconst.TOBOTTOM)
        self._ok_button = Button(parent=self.sr.standardBtns, label=localization.GetByLabel('UI/Common/Buttons/OK'), func=self.OnOK, args=())
        Button(parent=self.sr.standardBtns, label=localization.GetByLabel('UI/Common/Buttons/Cancel'), func=self.OnCancel, args=())
        self.SetOKButtonState(enabled=self.selectionType != SELECT_FILES)
        scrollCont = Container(name='scrollCont', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 6, 6))
        self.sr.scroll = eveScroll.Scroll(parent=scrollCont, name='fileFolderScroll', padLeft=5)
        self.sr.scroll.multiSelect = multiSelect
        self.sr.scroll.OnSelectionChange = self.VerifySelectedEnties
        self.sr.scroll.Sort = lambda *args, **kw: None
        if path is None or not os.path.isdir(path):
            path = settings.user.ui.Get('fileDialogLastPath', None)
            if path is None:
                path = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE')
                if not os.path.isdir(path):
                    path = blue.sysinfo.GetUserDocumentsDirectory()
        self.LoadDirToScroll(path)

    def GetAvailableDrives(self):
        try:
            length = ctypes.windll.kernel32.GetLogicalDriveStringsA(0, '')
            buffer = ctypes.create_string_buffer(length + 1)
            length = ctypes.windll.kernel32.GetLogicalDriveStringsA(length, buffer)
            drives = buffer.raw[:length].split('\x00')
        except:
            return []

        ret = []
        for i, d in enumerate(drives):
            if d:
                ret.append((d, i))

        return ret

    def Confirm(self):
        if len(self.GetSelected(multi=True)) > 0:
            self.OnDblClick()

    def OnDriveSelected(self, combo, drive, index):
        if os.path.isdir(drive):
            self.LoadDirToScroll(drive)
        else:
            eve.Message('FileDialogUnableToAccessDrive', {}, uiconst.OK)

    def OnPathEnteredIntoEdit(self):
        path = self.sr.pathEdit.GetValue()
        if os.path.isdir(path):
            self.LoadDirToScroll(path)

    def OnOK(self):
        selected = self.GetSelected()
        self.result = self.GetReturnValue()
        settings.user.ui.Set('fileDialogLastPath', self.lastEnteredPath)
        self.SetModalResult(1)

    def GetReturnValue(self):
        selected = self.GetSelected(multi=True)
        retval = utillib.KeyVal(files=[], folders=[])
        if len(selected) == 0 and self.selectionType != SELECT_FILES:
            retval.folders.append(self.sr.pathEdit.GetValue())
        for s in selected:
            if s.isDir:
                if s.isFolderUp:
                    retval.folders.append(self.sr.pathEdit.GetValue())
                else:
                    retval.folders.append(s.filePath)
            else:
                retval.files.append(s.filePath)

        return retval

    def OnCancel(self):
        self.Close()

    def GetSelected(self, multi = False):
        selected = self.sr.scroll.GetSelected()
        if not selected:
            return []
        elif not multi:
            return selected[0]
        else:
            return selected

    def OnDblClick(self, *args):
        selected = self.GetSelected()
        if selected.isDir:
            self.LoadDirToScroll(selected.filePath)
            self.sr.scroll.SelectNode(self.sr.scroll.GetNode(0))
        else:
            self.OnOK()

    def VerifySelectedEnties(self, *args):
        selected = self.GetSelected(multi=True)
        sm.ScatterEvent('OnFileDialogSelection', selected)
        for s in selected:
            if self._IsEntryInvalid(s):
                self.SetOKButtonState(enabled=False)
                return

        self.SetOKButtonState(enabled=True)

    def _IsEntryInvalid(self, entry):
        return entry.isFolderUp and self.selectionType == SELECT_FILES or entry.isDir and self.selectionType == SELECT_FILES or not entry.isDir and self.selectionType == SELECT_FOLDERS

    def SetOKButtonState(self, enabled):
        if self._ok_button:
            if enabled:
                self._ok_button.Enable()
            else:
                self._ok_button.Disable()

    def EntryShouldBeDisplayed(self, filePath, isDir):
        if self.selectionType == SELECT_FOLDERS and not isDir:
            return False
        extension = os.path.splitext(filePath)[1].replace('.', '').lower()
        if not isDir and self.fileExtensions and extension not in self.fileExtensions:
            return False
        return True

    def LoadDirToScroll(self, path):
        scrolllist = []
        path = os.path.abspath(path)
        try:
            fileList = os.listdir(path)
        except:
            eve.Message('FileDialogUnableToAccessFolder')
            return

        self.lastEnteredPath = path
        fileList.append('..')
        for f in fileList:
            f = unicode(f)
            data = utillib.KeyVal()
            data.label = u'<t>%s' % f
            data.hint = f
            data.filePath = os.path.join(path, f)
            data.isDir = os.path.isdir(data.filePath)
            data.OnDblClick = self.OnDblClick
            data.charIndex = f
            if not self.EntryShouldBeDisplayed(f, data.isDir):
                continue
            sortBy = f.lower()
            if data.isDir:
                if f == '..':
                    sortBy = '  ' + sortBy
                    data.isFolderUp = True
                else:
                    sortBy = ' ' + sortBy
            scrolllist.append((sortBy, GetFromClass(FileDialogEntry, data=data)))

        scrolllist = SortListOfTuples(scrolllist)
        self.sr.scroll.Load(contentList=scrolllist, headers=['', localization.GetByLabel('UI/Common/Name')])
        self.sr.pathEdit.SetValue(path)

    @classmethod
    def _Select(cls, *args, **kwds):
        wnd = cls.Open(*args, **kwds)
        if wnd.ShowModal() == 1:
            return wnd.result
        else:
            return None

    @classmethod
    def SelectFiles(cls, **kwds):
        return cls._Select(selectionType=SELECT_FILES, **kwds)

    @classmethod
    def SelectFolders(cls, **kwds):
        return cls._Select(selectionType=SELECT_FOLDERS, **kwds)

    @classmethod
    def SelectFilesAndFolders(cls, **kwds):
        return cls._Select(selectionType=SELECT_FILESANDFOLDERS, **kwds)
