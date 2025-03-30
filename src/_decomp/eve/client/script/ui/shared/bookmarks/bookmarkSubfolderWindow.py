#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\bookmarks\bookmarkSubfolderWindow.py
import eveicon
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.common.lib.appConst import MAX_FOLDER_NAME_LENGTH
from eveexceptions import UserError
from localization import GetByLabel
ROW_PADDING = (2, 2, 2, 2)

class BookmarkSubfolderWindow(Window):
    default_windowID = 'bookmarkSubfolderWindow'
    __notifyevents__ = ['OnRefreshBookmarks']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.subfolder = attributes.get('subfolder', None)
        self.folderID = attributes.folderID
        if self.subfolder is None:
            self.SetCaption(GetByLabel('UI/AclBookmarks/NewSubfolder'))
            self.isNew = True
            if self.folderID is None:
                self.folderID = settings.char.ui.Get('bookmarkSubfolderDefaultFolder', None)
        else:
            self.SetCaption(GetByLabel('UI/AclBookmarks/EditSubfolder'))
            self.isNew = False
            self.folderID = self.subfolder.folderID
        if self.folderID:
            try:
                self.folder = sm.GetService('bookmarkSvc').GetBookmarkFolder(self.folderID)
            except KeyError:
                if self.isNew:
                    self.folder = None
                    self.folderID = None
                else:
                    raise UserError('FolderAccessDenied')

        else:
            self.folder = None
        self.SetMinSize(size=(400, 180))
        main = Container(name='main', parent=self.sr.main, align=uiconst.TOALL, left=4, width=4)
        labelContainer = Container(name='labelContainer', parent=main, align=uiconst.TOTOP, top=8, height=20, padding=ROW_PADDING)
        EveLabelMedium(text=GetByLabel('UI/PeopleAndPlaces/Name'), parent=labelContainer, align=uiconst.TOLEFT, width=60)
        self.nameEdit = SingleLineEditText(name='nameEdit', setvalue=self.subfolder.subfolderName if self.subfolder else '', parent=labelContainer, align=uiconst.TOALL, maxLength=MAX_FOLDER_NAME_LENGTH, width=0, OnReturn=self.Confirm)
        sectionContainer = Container(name='sectionContainer', parent=main, align=uiconst.TOTOP, top=8, height=20, padding=ROW_PADDING)
        EveLabelMedium(text=GetByLabel('UI/PeopleAndPlaces/Folder'), parent=sectionContainer, align=uiconst.TOLEFT, width=60)
        if self.isNew:
            options = self.GetFolderOptions()
            self.sectionCombo = Combo(name='sectionCombo', parent=sectionContainer, align=uiconst.TOALL, width=0, select=self.folderID, options=options)
        else:
            sectionName = self.folder.folderName
            if self.folder.isPersonal:
                texturePath = eveicon.folder
                hint = GetByLabel('UI/AclBookmarks/PersonalFolderType')
            else:
                texturePath = eveicon.shared_folder
                hint = GetByLabel('UI/AclBookmarks/SharedFolderType')
            Sprite(parent=sectionContainer, align=uiconst.CENTERLEFT, pos=(60, 0, 16, 16), texturePath=texturePath, hint=hint)
            EveLabelMedium(text=sectionName, parent=sectionContainer, align=uiconst.TOALL, width=60, left=20)
        buttonGroup = ButtonGroup(name='buttonGroup', parent=main)
        submitButton = buttonGroup.AddButton(GetByLabel('UI/Common/Submit'), self.Confirm)
        buttonGroup.AddButton(GetByLabel('UI/Common/Cancel'), self.Cancel)
        submitButton.OnSetFocus()

    def GetFolderOptions(self):
        folders = sm.GetService('bookmarkSvc').GetFilteredFolders()
        options = []
        for folder in folders:
            label = folder.folderName
            if folder.isPersonal:
                texturePath = eveicon.folder
                hint = GetByLabel('UI/AclBookmarks/PersonalFolderType')
            else:
                texturePath = eveicon.shared_folder
                hint = GetByLabel('UI/AclBookmarks/SharedFolderType')
            entry = (label,
             folder.folderID,
             hint,
             texturePath)
            sortKey = (-folder.isPersonal, label.lower())
            options.append((sortKey, entry))

        options = SortListOfTuples(options)
        return options

    def OnRefreshBookmarks(self):
        if self.isNew:
            options = self.GetFolderOptions()
            if options:
                self.sectionCombo.entries = self.GetFolderOptions()
            else:
                eve.Message('CustomNotify', {'notify': GetByLabel('UI/AclBookmarks/NoValidFolder')})
                self.Close()

    def Confirm(self, *args):
        name = self.nameEdit.GetValue()
        name = name.strip()
        if not name:
            raise UserError('CustomInfo', {'info': GetByLabel('UI/Map/MapPallet/msgPleaseTypeSomething')})
        if self.isNew:
            self.folderID = self.sectionCombo.GetValue()
        bookmarkSvc = sm.GetService('bookmarkSvc')
        subfolders = bookmarkSvc.GetSubfolders()
        currentSubfolderID = self.subfolder.subfolderID if self.subfolder else None
        existingSubfolderNames = {x.subfolderName for x in subfolders.itervalues() if x.subfolderID != currentSubfolderID and x.folderID == self.folderID}
        if name in existingSubfolderNames:
            raise UserError('CustomInfo', {'info': GetByLabel('UI/Notepad/FolderAlreadyExists')})
        if self.isNew:
            bookmarkSvc.CreateSubfolder(self.folderID, name)
        else:
            bookmarkSvc.UpdateSubfolder(self.folderID, self.subfolder.subfolderID, name)
        settings.char.ui.Set('bookmarkSubfolderDefaultFolder', self.folderID)
        self.Close()

    def Cancel(self, *args):
        self.Close()
