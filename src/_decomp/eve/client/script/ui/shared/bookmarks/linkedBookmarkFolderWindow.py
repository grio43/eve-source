#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\bookmarks\linkedBookmarkFolderWindow.py
import eve.common.lib.appConst as appConst
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.button.group import ButtonGroup
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from carbonui.control.window import Window
from eve.client.script.ui.control.glowSprite import GlowSprite
from localization import GetByLabel
import ownergroups.client
from utillib import KeyVal

class LinkedBookmarkFolderWindow(Window):
    __guid__ = 'form.LinkedBookmarkFolderWindow'
    default_windowID = 'LinkedBookmarkFolderWindow'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.folder = attributes.get('folder', None)
        self.alreadyKnown = attributes.get('alreadyKnown', False)
        if self.folder.isPersonal:
            iconPath = 'res:/UI/Texture/classes/Bookmarks/personalFolderAddress_64.png'
        else:
            iconPath = 'res:/UI/Texture/classes/Bookmarks/sharedFolderAddress_64.png'
        self.icon = iconPath
        self.topParent = Container(parent=self.GetMainArea(), name='topParent', align=uiconst.TOTOP, height=52)
        self.mainIcon = GlowSprite(parent=self.topParent, name='mainicon', pos=(0, -4, 64, 64), state=uiconst.UI_DISABLED, texturePath=self.iconNum)
        if self.alreadyKnown:
            self.SetCaption(GetByLabel('UI/AclBookmarks/FolderInformation'))
        else:
            self.SetCaption(GetByLabel('UI/AclBookmarks/AddFolderToLists'))
        self.isPersonal = self.folder.isPersonal
        self.isActive = True
        if self.alreadyKnown:
            self.isActive = self.folder.isActive
        if not self.isPersonal:
            self.mainIcon.isDragObject = True
            self.mainIcon.state = uiconst.UI_NORMAL
            self.mainIcon.GetDragData = self.GetDragDataForIcon
        self.mainCont = Container(name='mainCont', parent=self.sr.main, align=uiconst.TOALL, left=4, width=4, clipChildren=True)
        buttonGroup = ButtonGroup(name='buttonGroup', parent=self.mainCont)
        if self.alreadyKnown or self.isPersonal:
            if not self.isActive:
                btn = buttonGroup.AddButton(GetByLabel('UI/AclBookmarks/MarkFolderActive'), self.MarkFolderAsActive, isDefault=True)
            else:
                btn = buttonGroup.AddButton(GetByLabel('UI/AclBookmarks/MarkFolderAsInactive'), self.MarkFolderAsInactive, isDefault=True)
            buttonGroup.AddButton(GetByLabel('UI/Common/Close'), self.Cancel)
        else:
            btn = buttonGroup.AddButton(GetByLabel('UI/AclBookmarks/AddFolder'), self.AddFolder, isDefault=True)
            buttonGroup.AddButton(GetByLabel('UI/Common/Cancel'), self.Cancel)
        labelContainer = ContainerAutoSize(name='labelContainer', parent=self.topParent, align=uiconst.TOTOP, padLeft=70, padTop=4)
        EveLabelMedium(text=GetByLabel('UI/AclBookmarks/FolderNameHeader'), parent=labelContainer, align=uiconst.TOTOP)
        EveLabelLarge(text=self.folder.folderName, parent=labelContainer, align=uiconst.TOTOP)
        ROW_PADDING = (2, 2, 2, 2)
        maxTextWidth = 60
        activeContainer = Container(name='activeContainer', parent=self.mainCont, align=uiconst.TOBOTTOM, top=8, height=50, padding=ROW_PADDING)
        mainGrid = LayoutGrid(columns=2, parent=self.mainCont, align=uiconst.TOBOTTOM, cellPadding=2)
        typeRow = mainGrid.AddRow()
        typeLabel = EveLabelMedium(text=GetByLabel('UI/AclBookmarks/FolderType'), parent=typeRow)
        if self.isPersonal:
            text = GetByLabel('UI/AclBookmarks/PersonalFolderType')
        else:
            text = GetByLabel('UI/AclBookmarks/SharedFolderType')
        EveLabelMedium(text=text, parent=typeRow)
        if not self.folder.isPersonal:
            accessRow = mainGrid.AddRow()
            accessLabel = EveLabelMedium(text=GetByLabel('UI/AclBookmarks/YourAccess'), parent=accessRow)
            if self.folder.accessLevel == appConst.ACCESS_ADMIN:
                text = GetByLabel('UI/AclBookmarks/AdminAccess')
            elif self.folder.accessLevel == appConst.ACCESS_MANAGE:
                text = GetByLabel('UI/AclBookmarks/ManageAccess')
            elif self.folder.accessLevel == appConst.ACCESS_USE:
                text = GetByLabel('UI/AclBookmarks/UseAccess')
            elif self.folder.accessLevel == appConst.ACCESS_VIEW:
                text = GetByLabel('UI/AclBookmarks/ViewAccess')
            else:
                text = GetByLabel('UI/Common/Unknown')
            EveLabelMedium(text=text, parent=accessRow)
            creatorRow = mainGrid.AddRow()
            creatorLabel = EveLabelMedium(text=GetByLabel('UI/AclBookmarks/Creator'), parent=creatorRow)
            creatorID = getattr(self.folder, 'creatorID', None)
            if creatorID is not None:
                creatorName = cfg.eveowners.Get(creatorID).name
                characterLink = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=creatorName, info=('showinfo', appConst.typeCharacter, creatorID))
            else:
                characterLink = ''
            EveLabelMedium(text=characterLink, parent=creatorRow, state=uiconst.UI_NORMAL)
            maxTextWidth = max(maxTextWidth, accessLabel.textwidth, creatorLabel.textwidth)
        if self.alreadyKnown and self.folder.isActive:
            countBookmarks = sum((1 for bm in sm.GetService('bookmarkSvc').GetBookmarks().itervalues() if bm.folderID == self.folder.folderID))
            bookmarkRow = mainGrid.AddRow()
            bookmarksLabel = EveLabelMedium(text=GetByLabel('UI/PeopleAndPlaces/Locations'), parent=bookmarkRow)
            EveLabelMedium(text=countBookmarks, parent=bookmarkRow)
            countSubfolders = len(sm.GetService('bookmarkSvc').GetSubfoldersInFolder(self.folder.folderID))
            subfolderRow = mainGrid.AddRow()
            subfolderLabel = EveLabelMedium(text=GetByLabel('UI/AclBookmarks/Subfolders'), parent=subfolderRow)
            EveLabelMedium(text=countSubfolders, parent=subfolderRow)
            maxTextWidth = max(maxTextWidth, bookmarksLabel.textwidth, subfolderLabel.textwidth)
        if not self.folder.isPersonal:
            accessListConfig = EveLabelMedium(text=GetByLabel('UI/AclBookmarks/AccessConfiguration'))
            mainGrid.AddCell(cellObject=accessListConfig, colSpan=2)
            maxTextWidth = self.AddAccessGroupRow(mainGrid, GetByLabel('UI/AclBookmarks/AdminAccess'), self.folder.adminGroupID, maxTextWidth)
            maxTextWidth = self.AddAccessGroupRow(mainGrid, GetByLabel('UI/AclBookmarks/ManageAccess'), self.folder.manageGroupID, maxTextWidth)
            maxTextWidth = self.AddAccessGroupRow(mainGrid, GetByLabel('UI/AclBookmarks/UseAccess'), self.folder.useGroupID, maxTextWidth)
            maxTextWidth = self.AddAccessGroupRow(mainGrid, GetByLabel('UI/AclBookmarks/ViewAccess'), self.folder.viewGroupID, maxTextWidth)
        cbCont = Container(name='cbCont', parent=activeContainer)
        if self.alreadyKnown:
            path = 'UI/AclBookmarks/Status'
        else:
            path = 'UI/AclBookmarks/AddFolderAs'
        addAsLabel = EveLabelMedium(text=GetByLabel(path), parent=activeContainer, align=uiconst.TOPLEFT)
        if self.alreadyKnown:
            if self.isActive:
                text = GetByLabel('UI/AclBookmarks/Active')
            else:
                text = GetByLabel('UI/AclBookmarks/NotActive')
            EveLabelMedium(text=text, parent=cbCont, align=uiconst.TOPLEFT, padding=(4, 2, 2, 2))
            activeContainer.height = 20
        else:
            RadioButton(text=GetByLabel('UI/AclBookmarks/ActiveFolderCb'), groupname='isActiveSelection', parent=cbCont, settingsKey='isPersonal', checked=self.isActive, retval=True, state=False, align=uiconst.TOTOP, callback=self.OnIsActiveCheckBoxChange)
            RadioButton(text=GetByLabel('UI/AclBookmarks/InactiveFolderCb'), groupname='isActiveSelection', parent=cbCont, settingsKey='isPersonal', checked=not self.isActive, retval=False, align=uiconst.TOTOP, callback=self.OnIsActiveCheckBoxChange)
        descriptionContainer = Container(name='descriptionContainer', parent=self.mainCont, align=uiconst.TOALL, top=8, padding=ROW_PADDING)
        descLabel = EveLabelMedium(text=GetByLabel('UI/PeopleAndPlaces/Notes'), parent=descriptionContainer, align=uiconst.TOPLEFT, width=60)
        self.notesEdit = EditPlainText(name='notesEdit', setvalue=self.folder.description, parent=descriptionContainer, align=uiconst.TOALL, maxLength=400, countWithTags=True, readonly=True)
        maxTextWidth = max(maxTextWidth, descLabel.textwidth, typeLabel.textwidth, addAsLabel.textwidth)
        left = maxTextWidth + descLabel.left + 4
        self.notesEdit.padLeft = cbCont.padLeft = typeLabel.width = left
        height = 210 + mainGrid.height + activeContainer.height
        width = 310
        self.SetMinSize([width, height])
        self.SetSize(width, height)
        btn.OnSetFocus()

    def AddAccessGroupRow(self, mainGrid, label, groupID, textWidth):
        accessRow = mainGrid.AddRow()
        accessLabel = EveLabelMedium(text=label, parent=accessRow)
        try:
            link = ownergroups.client.access_group_link(groupID)
        except Exception:
            link = '-'

        EveLabelMedium(text=link, parent=accessRow, state=uiconst.UI_NORMAL)
        return max(textWidth, accessLabel.textwidth)

    def GetDragDataForIcon(self):
        if self.isPersonal:
            return []
        ret = KeyVal(nodeType='BookmarkFolderEntry', folderID=self.folder.folderID, label=self.folder.folderName)
        return [ret]

    def OnIsActiveCheckBoxChange(self, checkbox):
        self.isActive = checkbox.GetReturnValue()

    def AddFolder(self, *args):
        sm.GetService('bookmarkSvc').AddToKnownFolders(self.folder.folderID, self.isActive)
        self.Close()

    def MarkFolderAsActive(self, *args):
        sm.GetService('bookmarkSvc').UpdateFolderActiveState(self.folder.folderID, True)
        self.Close()

    def MarkFolderAsInactive(self, *args):
        sm.GetService('bookmarkSvc').UpdateFolderActiveState(self.folder.folderID, False)
        self.Close()

    def Cancel(self, *args):
        self.Close()
