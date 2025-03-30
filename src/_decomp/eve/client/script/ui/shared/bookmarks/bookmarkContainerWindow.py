#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\bookmarks\bookmarkContainerWindow.py
import carbonui.const as uiconst
import eveicon
from carbonui.control.combo import Combo
from menu import MenuLabel
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.button.group import ButtonGroup
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.shared.bookmarks.link import bookmark_folder_link
from eve.client.script.ui.structure.structureSettings import AreGroupNodes, GetGroupIDFromNode
from eve.common.lib.appConst import MAX_ACTIVE_PERSONAL_BOOKMARK_FOLDERS, MAX_ACTIVE_SHARED_BOOKMARK_FOLDERS, MAX_BOOKMARKS_IN_PERSONAL_FOLDER, MAX_BOOKMARKS_IN_SHARED_FOLDER, MAX_FOLDER_DESCRIPTION_LENGTH, MAX_FOLDER_NAME_LENGTH, MAX_KNOWN_BOOKMARK_FOLDERS
from eve.common.script.sys.idCheckers import IsNPCCorporation
from eveexceptions import UserError
from localization import GetByLabel

class BookmarkContainerWindow(Window):
    __guid__ = 'BookmarkContainerWindow'
    default_windowID = 'bookmarkFolderWindow'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.folder = attributes.get('folder', None)
        accessGroups = self.GetAccessGroups()
        self.accessGroupOptions = []
        for accessGroupID, accessGroup in accessGroups.iteritems():
            groupDisplayName = cfg.eveowners.Get(accessGroup.creatorID).name if IsNPCCorporation(accessGroup.creatorID) else accessGroup.name
            self.accessGroupOptions.append((groupDisplayName, accessGroupID))

        self.accessGroupOptions.sort()
        self.accessGroupOptions.append((GetByLabel('UI/AclBookmarks/NoAccessList'), -1))
        if self.folder is None:
            self.SetCaption(GetByLabel('UI/AclBookmarks/NewFolder'))
            self.isNew = True
            self.isPersonal = True
        else:
            self.SetCaption(GetByLabel('UI/AclBookmarks/EditBookmarkFolder'))
            self.isNew = False
            self.isPersonal = self.folder.isPersonal
            if not self.isPersonal:
                groupIDs = {self.folder.viewGroupID,
                 self.folder.useGroupID,
                 self.folder.manageGroupID,
                 self.folder.adminGroupID}
                for groupID in groupIDs:
                    if groupID not in accessGroups:
                        self.AddGroup(groupID)

        self.SetMinSize([280, 420])
        rowPadding = (0, 4, 0, 4)
        self.mainCont = Container(name='mainCont', parent=self.sr.main, align=uiconst.TOALL, left=4, width=4)
        buttonGroup = ButtonGroup(name='buttonGroup', parent=self.mainCont, padTop=8)
        submitButton = buttonGroup.AddButton(GetByLabel('UI/Common/Submit'), self.Confirm)
        buttonGroup.AddButton(GetByLabel('UI/Common/Cancel'), self.Cancel)
        labelContainer = ContainerAutoSize(name='labelContainer', parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=rowPadding)
        self.accessGroupOptionsContainer = ContainerAutoSize(name='accessGroupOptionsContainer', parent=self.mainCont, align=uiconst.TOBOTTOM, alignMode=uiconst.TOTOP, padding=rowPadding)
        nameLabel = EveLabelMedium(text=GetByLabel('UI/PeopleAndPlaces/Name'), parent=labelContainer, align=uiconst.CENTERLEFT)
        self.nameEdit = SingleLineEditText(name='nameEdit', setvalue=self.folder.folderName if self.folder else '', parent=labelContainer, align=uiconst.TOTOP, width=0, maxLength=MAX_FOLDER_NAME_LENGTH, OnReturn=self.Confirm)
        typeContainer = Container(name='typeContainer', parent=self.mainCont, align=uiconst.TOBOTTOM, top=8, height=40, padding=rowPadding)
        typeLabel = EveLabelMedium(name='typeLabel', parent=typeContainer, text=GetByLabel('UI/AclBookmarks/FolderType'), align=uiconst.TOPLEFT)
        infoContainer = Container(name='infoContainer', parent=typeContainer, align=uiconst.TORIGHT, width=20)
        selectionContainer = Container(name='selectionContainer', parent=typeContainer, align=uiconst.TOALL)
        if self.isNew:
            RadioButton(text=GetByLabel('UI/AclBookmarks/PersonalFolderType'), groupname='isPersonalSelection', parent=selectionContainer, settingsKey='isPersonal', checked=self.isPersonal, retval=True, align=uiconst.TOTOP, callback=self.OnIsPersonalCheckBoxChange)
            RadioButton(text=GetByLabel('UI/AclBookmarks/SharedFolderType'), groupname='isPersonalSelection', parent=selectionContainer, settingsKey='isPersonal', checked=not self.isPersonal, retval=False, align=uiconst.TOTOP, callback=self.OnIsPersonalCheckBoxChange)
        else:
            if self.isPersonal:
                text = GetByLabel('UI/AclBookmarks/PersonalFolderType')
                texturePath = eveicon.folder
                hint = GetByLabel('UI/AclBookmarks/PersonalFolderType')
            else:
                text = GetByLabel('UI/AclBookmarks/SharedFolderType')
                texturePath = eveicon.shared_folder
                hint = GetByLabel('UI/AclBookmarks/SharedFolderType')
            Sprite(parent=selectionContainer, align=uiconst.TOPLEFT, pos=(0, 0, 16, 16), texturePath=texturePath, hint=hint)
            folderTypeLabel = EveLabelMedium(text=text, parent=selectionContainer, align=uiconst.TOTOP, left=20)
            typeContainer.height = max(20, folderTypeLabel.textheight, typeLabel.textheight)
        helpText = GetByLabel('UI/AclBookmarks/CreateFolderHelpText', maxPersonalBookmarks=MAX_BOOKMARKS_IN_PERSONAL_FOLDER, maxSharedBookmarks=MAX_BOOKMARKS_IN_SHARED_FOLDER, maxPersonalFolders=MAX_ACTIVE_PERSONAL_BOOKMARK_FOLDERS, maxSharedFolders=MAX_ACTIVE_SHARED_BOOKMARK_FOLDERS)
        MoreInfoIcon(parent=infoContainer, hint=helpText, align=uiconst.CENTER)
        descriptionContainer = Container(name='descriptionContainer', parent=self.mainCont, align=uiconst.TOALL, top=8, padding=rowPadding)
        descLabel = EveLabelMedium(text=GetByLabel('UI/PeopleAndPlaces/Notes'), parent=descriptionContainer, align=uiconst.TOPLEFT)
        self.notesEdit = EditPlainText(name='notesEdit', setvalue=self.folder.description if self.folder else '', parent=descriptionContainer, align=uiconst.TOALL, maxLength=MAX_FOLDER_DESCRIPTION_LENGTH, countWithTags=True)
        left = max(nameLabel.left + nameLabel.textwidth, descLabel.left + descLabel.textwidth, typeLabel.left + typeLabel.textwidth)
        self.nameEdit.padLeft = self.notesEdit.padLeft = selectionContainer.padLeft = left + 10
        if self.isPersonal:
            self.HideAccessGroupOptions()
        else:
            self.LoadAccessGroupOptions()
        submitButton.OnSetFocus()

    def LoadAccessGroupOptions(self):
        self.accessGroupOptionsContainer.Flush()
        self.accessGroupOptionsContainer.display = True
        self.viewGroupContainer, self.viewGroupCombo, viewLabel = self.GetAccessGroupComboAndCont('viewGroup', GetByLabel('UI/AclBookmarks/ViewAccess'), self.OnDroppedGroupView, self.folder.viewGroupID if self.folder else None)
        self.useGroupContainer, self.useGroupCombo, useLabel = self.GetAccessGroupComboAndCont('useGroup', GetByLabel('UI/AclBookmarks/UseAccess'), self.OnDroppedGroupUse, self.folder.useGroupID if self.folder else None)
        self.manageGroupContainer, self.manageGroupCombo, manageLabel = self.GetAccessGroupComboAndCont('manageGroup', GetByLabel('UI/AclBookmarks/ManageAccess'), self.OnDroppedGroupManage, self.folder.manageGroupID if self.folder else None)
        self.adminGroupContainer, self.adminGroupCombo, adminLabel = self.GetAccessGroupComboAndCont('adminGroup', GetByLabel('UI/AclBookmarks/AdminAccess'), self.OnDroppedGroupAdmin, self.folder.adminGroupID if self.folder else None)
        left = max(useLabel.textwidth, viewLabel.textwidth, manageLabel.textwidth, adminLabel.textwidth, 80)
        left += useLabel.left + 4
        for each in (self.viewGroupCombo,
         self.useGroupCombo,
         self.manageGroupCombo,
         self.adminGroupCombo):
            each.padLeft = left

    def GetAccessGroupComboAndCont(self, configName, text, dropFunc, selectedGroupID):
        if not selectedGroupID:
            selectedGroupID = -1
        cont = ContainerAutoSize(name='%sCont' % configName, parent=self.accessGroupOptionsContainer, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padBottom=4)
        label = EveLabelMedium(text=text, parent=cont, align=uiconst.CENTERLEFT)
        combo = DropCombo(parent=cont, name='%sCombo' % configName, align=uiconst.TOTOP, options=self.accessGroupOptions, select=selectedGroupID, dropped=dropFunc)
        return (cont, combo, label)

    def HideAccessGroupOptions(self):
        self.accessGroupOptionsContainer.display = False

    def GetAccessGroups(self):
        accessGroupsController = sm.GetService('structureControllers').GetAccessGroupController()
        return accessGroupsController.GetMyGroups()

    def OnIsPersonalCheckBoxChange(self, radioButton):
        self.isPersonal = radioButton.GetReturnValue()
        if self.isPersonal:
            self.HideAccessGroupOptions()
        else:
            self.LoadAccessGroupOptions()

    def AddGroup(self, newGroupID):
        if newGroupID:
            newGroup = sm.GetService('structureControllers').GetAccessGroupController().GetGroupInfoFromID(newGroupID, fetchToServer=True)
            groupDisplayName = cfg.eveowners.Get(newGroup.creatorID).name if IsNPCCorporation(newGroup.creatorID) else newGroup.name
            self.accessGroupOptions.append((groupDisplayName, newGroupID))

    def OnDroppedGroupView(self, newGroupID):
        for groupName, groupID in self.accessGroupOptions:
            if groupID == newGroupID:
                self.viewGroupCombo.SetValue(newGroupID)
                return

        self.AddGroup(newGroupID)
        self.viewGroupCombo.entries = self.accessGroupOptions
        self.viewGroupCombo.SetValue(newGroupID)

    def OnDroppedGroupUse(self, newGroupID):
        for groupName, groupID in self.accessGroupOptions:
            if groupID == newGroupID:
                self.useGroupCombo.SetValue(newGroupID)
                return

        self.AddGroup(newGroupID)
        self.useGroupCombo.entries = self.accessGroupOptions
        self.useGroupCombo.SetValue(newGroupID)

    def OnDroppedGroupManage(self, newGroupID):
        for groupName, groupID in self.accessGroupOptions:
            if groupID == newGroupID:
                self.manageGroupCombo.SetValue(newGroupID)
                return

        self.AddGroup(newGroupID)
        self.manageGroupCombo.entries = self.accessGroupOptions
        self.manageGroupCombo.SetValue(newGroupID)

    def OnDroppedGroupAdmin(self, newGroupID):
        for groupName, groupID in self.accessGroupOptions:
            if groupID == newGroupID:
                self.adminGroupCombo.SetValue(newGroupID)
                return

        self.AddGroup(newGroupID)
        self.adminGroupCombo.entries = self.accessGroupOptions
        self.adminGroupCombo.SetValue(newGroupID)

    def Confirm(self, *args):
        name = self.nameEdit.GetValue()
        name = name.strip()
        if not name:
            raise UserError('CustomInfo', {'info': GetByLabel('UI/Map/MapPallet/msgPleaseTypeSomething')})
        description = self.notesEdit.GetValue()
        isPersonal = self.isPersonal
        if isPersonal:
            adminGroupID = None
            manageGroupID = None
            useGroupID = None
            viewGroupID = None
        else:
            adminGroupID = self.adminGroupCombo.GetValue()
            if not adminGroupID or adminGroupID == -1:
                raise UserError('AdminAccessRequired')
            manageGroupID = self.manageGroupCombo.GetValue()
            if manageGroupID == -1:
                manageGroupID = None
            useGroupID = self.useGroupCombo.GetValue()
            if useGroupID == -1:
                useGroupID = None
            viewGroupID = self.viewGroupCombo.GetValue()
            if viewGroupID == -1:
                viewGroupID = None
        folders = sm.GetService('bookmarkSvc').GetFolders()
        currentFolderID = self.folder.folderID if self.folder else None
        if self.isNew:
            if len(folders) >= MAX_KNOWN_BOOKMARK_FOLDERS:
                raise UserError('TooManyKnownFolders', {'maxKnownFolders': MAX_KNOWN_BOOKMARK_FOLDERS})
            activeFolders = len([ folder.folderID for folder in folders.itervalues() if folder.isActive and folder.isPersonal == isPersonal ])
            maxActiveFolders = MAX_ACTIVE_PERSONAL_BOOKMARK_FOLDERS if isPersonal else MAX_ACTIVE_SHARED_BOOKMARK_FOLDERS
            if activeFolders >= maxActiveFolders:
                if isPersonal:
                    if not eve.Message('ConfirmCreateAsInactivePersonalFolder', {'maxPersonalFolders': MAX_ACTIVE_PERSONAL_BOOKMARK_FOLDERS}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
                        return
                elif not eve.Message('ConfirmCreateAsInactiveSharedFolder', {'maxSharedFolders': MAX_ACTIVE_SHARED_BOOKMARK_FOLDERS}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
                    return
        existingFolderNames = {x.folderName for x in folders.itervalues() if x.folderID != currentFolderID}
        if name in existingFolderNames:
            if not eve.Message('ConfirmCreateFolderWithDuplicateName', {}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
                return
        if self.isNew:
            folder = sm.GetService('bookmarkSvc').CreateBookmarkFolder(isPersonal, name, description, adminGroupID, manageGroupID, useGroupID, viewGroupID)
            self.DisplaySuccessPopup(folder)
        else:
            sm.GetService('bookmarkSvc').UpdateBookmarkFolder(self.folder.folderID, name, description, adminGroupID, manageGroupID, useGroupID, viewGroupID)
        self.Close()

    def DisplaySuccessPopup(self, folder):
        if not folder or folder.isPersonal:
            return
        link = bookmark_folder_link(folder.folderID, folder.folderName)
        eve.Message('SharedLocationFolderCreated', {'folderName': folder.folderName,
         'folderLink': link}, modal=False)

    def Cancel(self, *args):
        self.Close()


class DropCombo(Combo):
    default_name = 'dropCombo'
    default_dropped = None

    def ApplyAttributes(self, attributes):
        Combo.ApplyAttributes(self, attributes)
        self._emptyTooltip = attributes.get('emptyTooltip', '')
        self.OnDroppedData = attributes.get('dropped', self.default_dropped)

    def OnDropData(self, dragSource, dragData):
        if not dragData:
            return
        if not AreGroupNodes(dragData):
            return
        groupIDsToAdd = filter(None, [ GetGroupIDFromNode(eachNode) for eachNode in dragData ])
        if groupIDsToAdd:
            groupIDToAdd = groupIDsToAdd[0]
            self.OnDroppedData(groupIDToAdd)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        groupID = self.GetValue()
        if not groupID or groupID == -1:
            self._TryLoadEmptyTooltip(tooltipPanel)
            return
        from eve.client.script.ui.structure.accessGroups.groupInfoWnd import GetGroupInfo
        groupInfo = GetGroupInfo(groupID)
        if not groupInfo:
            self._TryLoadEmptyTooltip(tooltipPanel)
            return
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.margin = (8, 8, 8, 8)
        groupDisplayName = cfg.eveowners.Get(groupInfo.creatorID).name if IsNPCCorporation(groupInfo.creatorID) else groupInfo['name']
        groupDesc = groupInfo['description']
        EveLabelMedium(parent=tooltipPanel, text=groupDisplayName, align=uiconst.TOTOP)
        admins = groupInfo['admins']
        if groupDesc:
            tooltipPanel.AddLabelMedium(text=groupDesc, padTop=6)
        text = GetByLabel('UI/Structures/AccessGroups/GroupOwner', ownerName='')
        tooltipPanel.AddLabelMedium(text=text, padTop=6)
        cfg.eveowners.Prime(admins)
        adminNames = [ cfg.eveowners.Get(adminID).name for adminID in admins ]
        maxAdmins = 6
        for charName in adminNames[:maxAdmins]:
            tooltipPanel.AddLabelMedium(text=charName)

        if len(adminNames) > maxAdmins:
            tooltipPanel.AddLabelMedium(text='...')

    def _TryLoadEmptyTooltip(self, tooltipPanel):
        if not self._emptyTooltip:
            return
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.margin = (8, 8, 8, 8)
        tooltipPanel.AddLabelMedium(text=self._emptyTooltip, maxWidth=200)

    def GetMenu(self, *args):
        groupID = self.GetValue()
        if not groupID:
            return []
        return [(MenuLabel('UI/AclBookmarks/ShowAccessListInfo'), self.ShowAccessGroupInfo)]

    def ShowAccessGroupInfo(self):
        from eve.client.script.ui.structure.accessGroups.groupInfoWnd import GroupInfoWnd
        groupID = self.GetValue()
        GroupInfoWnd.Open(groupID=groupID, windowID='groupInfoWnd_%s' % groupID)

    def OnMouseDown(self, button, *args):
        if button == uiconst.MOUSERIGHT:
            return
        if self._disabled:
            return
        Combo.OnMouseDown(self, button, *args)
