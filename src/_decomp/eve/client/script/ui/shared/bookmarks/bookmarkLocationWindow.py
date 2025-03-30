#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\bookmarks\bookmarkLocationWindow.py
from collections import defaultdict
import eveicon
import localization
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.common.lib.appConst import MAX_BOOKMARK_NAME_LENGTH, MAX_BOOKMARK_DESCRIPTION_LENGTH
from carbon.common.script.util.format import FmtDate
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.button.group import ButtonGroup
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.common.script.mgt.bookmarkConst import BOOKMARK_EXPIRY_NONE, BOOKMARK_EXPIRY_3HOURS, BOOKMARK_EXPIRY_2DAYS
from eveexceptions import UserError
from inventorycommon.const import ownerSystem
from localization import GetByLabel
BOOKMARK_EXPIRY_STRINGS = {BOOKMARK_EXPIRY_NONE: 'UI/AclBookmarks/ExpireNever',
 BOOKMARK_EXPIRY_3HOURS: 'UI/AclBookmarks/ExpireIn3Hours',
 BOOKMARK_EXPIRY_2DAYS: 'UI/AclBookmarks/ExpireIn2Days'}
ROW_PADDING = (2, 2, 2, 2)

class BookmarkLocationWindow(Window):
    __guid__ = 'form.BookmarkLocationWindow'
    __notifyevents__ = ['OnRefreshBookmarks']
    default_windowID = 'bookmarkLocationWindow'
    default_width = 340
    default_height = 340
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.locationID = attributes.get('locationID')
        locationName = attributes.get('locationName')
        note = attributes.get('note', '')
        self.typeID = attributes.get('typeID')
        self.scannerInfo = attributes.get('scannerInfo')
        self.parentID = attributes.get('parentID')
        self.bookmark = attributes.get('bookmark')
        self.expireIn = None
        self.expiryCancel = 0
        self.folderSelection = None
        if self.bookmark is None:
            self.caption = GetByLabel('UI/PeopleAndPlaces/NewBookmark')
        else:
            self.caption = GetByLabel('UI/PeopleAndPlaces/EditLocation')
        mainCont = Container(name='mainCont', parent=self.sr.main, align=uiconst.TOALL)
        labelContainer = ContainerAutoSize(name='labelContainer', parent=mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        EveLabelMedium(text=GetByLabel('UI/PeopleAndPlaces/Label'), parent=labelContainer, align=uiconst.CENTERLEFT, width=60)
        self.labelEdit = SingleLineEditText(name='labelEdit', setvalue=locationName, parent=labelContainer, align=uiconst.TOTOP, padLeft=60, autoselect=True, maxLength=MAX_BOOKMARK_NAME_LENGTH, OnReturn=self.Confirm)
        uicore.registry.SetFocus(self.labelEdit)
        self.forcedFolderID = None
        if self.bookmark is None:
            self.folderSelection = settings.char.ui.Get('bookmarkFolderAndSubfolder', (None, None))
        else:
            self.folderSelection = (self.bookmark.folderID, self.bookmark.subfolderID)
            self.forcedFolderID = self.bookmark.folderID
        self._AddExpiryContainer(mainCont)
        folderContainer = ContainerAutoSize(name='folderContainer', parent=mainCont, align=uiconst.TOBOTTOM, alignMode=uiconst.TOTOP, top=8)
        EveLabelMedium(parent=Container(parent=folderContainer, align=uiconst.TOLEFT, width=60), align=uiconst.CENTERLEFT, text=GetByLabel('UI/PeopleAndPlaces/Folder'))
        folders = attributes.get('folders')
        subfolders = attributes.get('subfolders')
        options, personalFolderFound = self.GetFolderAndSubfolderOptions(folders, subfolders)
        self.noPersonalFolderWarningIcon = ContainerAutoSize(name='warningIcon', parent=folderContainer, align=uiconst.TOLEFT, padding=(0, 0, 4, 0))
        Sprite(parent=self.noPersonalFolderWarningIcon, align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=16, height=16, texturePath='res:/UI/Texture/classes/agency/iconExclamation.png', color=eveColor.WARNING_ORANGE, hint=GetByLabel('UI/AclBookmarks/NoPersonalFolderAvailable'))
        if personalFolderFound:
            self.noPersonalFolderWarningIcon.display = False
        else:
            self.noPersonalFolderWarningIcon.display = True
        self.folderCombo = Combo(name='folderCombo', parent=folderContainer, align=uiconst.TOTOP, select=self.folderSelection, options=options, callback=self.OnFolderChange)
        descriptionContainer = Container(name='descriptionContainer', parent=mainCont, align=uiconst.TOALL, top=8, padding=(0, 0, 0, 8))
        EveLabelMedium(text=GetByLabel('UI/PeopleAndPlaces/Notes'), parent=descriptionContainer, align=uiconst.TOLEFT, width=60)
        self.notesEdit = EditPlainText(name='notesEdit', parent=descriptionContainer, align=uiconst.TOALL, setvalue=note, maxLength=MAX_BOOKMARK_DESCRIPTION_LENGTH, countWithTags=True)
        buttonGroup = ButtonGroup(name='buttonGroup', parent=self.sr.main, idx=0)
        submitButton = buttonGroup.AddButton(label=GetByLabel('UI/Common/Submit'), func=self.Confirm)
        buttonGroup.AddButton(label=GetByLabel('UI/Common/Cancel'), func=self.Cancel)
        submitButton.OnSetFocus()

    def _AddExpiryContainer(self, parent):
        if self.bookmark is None:
            self.expiryContainer = ContainerAutoSize(name='expiryContainer', parent=parent, align=uiconst.TOBOTTOM, alignMode=uiconst.TOTOP, top=8)
            self._LoadExpiryOptions()
        else:
            expiryContainer = ContainerAutoSize(name='expiryContainer', parent=parent, align=uiconst.TOBOTTOM, alignMode=uiconst.TOTOP, top=8)
            EveLabelMedium(parent=expiryContainer, align=uiconst.TOLEFT, width=60, text=GetByLabel('UI/AclBookmarks/AutoExpire'))
            if self.bookmark.expiry:
                label = FmtDate(self.bookmark.expiry, 'ls')
            else:
                label = GetByLabel(BOOKMARK_EXPIRY_STRINGS[BOOKMARK_EXPIRY_NONE])
            EveLabelMedium(text=label, parent=expiryContainer, align=uiconst.TOTOP)
            if self.bookmark.expiry:
                self.expiryResetCheckBox = Checkbox(parent=expiryContainer, align=uiconst.TOTOP, text=GetByLabel('UI/AclBookmarks/CancelAutomatedExpiry'), settingsKey='isPersonal', checked=False, callback=self.OnExpiryCancelCheckBoxChange)

    def _LoadExpiryOptions(self):
        self.expiryContainer.Flush()
        folderID, subfolderID = self.folderSelection
        self.expireIn = settings.char.ui.Get('bookmarkExpiryByFolder_%s_%s' % (folderID, subfolderID), 0)
        EveLabelMedium(text=GetByLabel('UI/AclBookmarks/AutoExpire'), parent=self.expiryContainer, align=uiconst.TOLEFT, width=60)
        infoContainer = Container(name='infoContainer', parent=self.expiryContainer, align=uiconst.TORIGHT, width=24)
        MoreInfoIcon(parent=infoContainer, hint=GetByLabel('UI/AclBookmarks/ExpiryOptionsHelpText'), align=uiconst.CENTER)
        RadioButton(parent=self.expiryContainer, align=uiconst.TOTOP, text=GetByLabel(BOOKMARK_EXPIRY_STRINGS[BOOKMARK_EXPIRY_NONE]), groupname='expirySelection', settingsKey='isPersonal', checked=self.expireIn == BOOKMARK_EXPIRY_NONE, retval=0, callback=self.OnExpiryCheckBoxChange)
        RadioButton(parent=self.expiryContainer, align=uiconst.TOTOP, text=GetByLabel(BOOKMARK_EXPIRY_STRINGS[BOOKMARK_EXPIRY_2DAYS]), groupname='expirySelection', settingsKey='isPersonal', checked=self.expireIn == BOOKMARK_EXPIRY_2DAYS, retval=2, callback=self.OnExpiryCheckBoxChange)
        RadioButton(parent=self.expiryContainer, align=uiconst.TOTOP, text=GetByLabel(BOOKMARK_EXPIRY_STRINGS[BOOKMARK_EXPIRY_3HOURS]), groupname='expirySelection', settingsKey='isPersonal', checked=self.expireIn == BOOKMARK_EXPIRY_3HOURS, retval=1, callback=self.OnExpiryCheckBoxChange)

    def GetFolderAndSubfolderOptions(self, folders, subfolders):
        optionsTemp = []
        options = []
        personalFolderFound = False
        for folder in folders:
            if folder.isPersonal:
                personalFolderFound = True
            activeStr = GetByLabel('UI/AclBookmarks/Active') if folder.isActive else GetByLabel('UI/AclBookmarks/NotActive')
            label = folder.folderName + ' (' + activeStr + ')'
            sortKey = (-folder.isPersonal, -folder.isActive, label.lower())
            data = (label, folder)
            optionsTemp.append((sortKey, data))

        optionsTemp = SortListOfTuples(optionsTemp)
        subFoldersByParentFolderID = defaultdict(list)
        for subfolder in subfolders:
            subFoldersByParentFolderID[subfolder.folderID].append(subfolder)

        for label, folder in optionsTemp:
            currentFolderID = folder.folderID
            isPersonal = folder.isPersonal
            returnValue = (currentFolderID, None)
            if isPersonal:
                texturePath = eveicon.folder
                hint = GetByLabel('UI/AclBookmarks/PersonalFolderType')
            else:
                texturePath = eveicon.shared_folder
                hint = GetByLabel('UI/AclBookmarks/SharedFolderType')
            options.append((label,
             returnValue,
             hint,
             texturePath))
            sub = subFoldersByParentFolderID[currentFolderID]
            subfolderOptions = []
            for eachSubFolder in sub:
                if eachSubFolder.creatorID == ownerSystem:
                    continue
                x = (eachSubFolder.subfolderName,
                 (eachSubFolder.folderID, eachSubFolder.subfolderID),
                 hint,
                 texturePath,
                 1)
                subfolderOptions.append(x)

            subfolderOptions = localization.util.Sort(subfolderOptions, key=lambda x: x[0].lower())
            options.extend(subfolderOptions)

        return (options, personalFolderFound)

    def OnRefreshBookmarks(self):
        folders, subfolders = sm.GetService('bookmarkSvc').GetFilteredFoldersAndSubfolders(self.forcedFolderID)
        options, personalFolderFound = self.GetFolderAndSubfolderOptions(folders, subfolders)
        if options:
            self.folderCombo.entries = options
            if personalFolderFound:
                self.noPersonalFolderWarningIcon.display = False
            else:
                self.noPersonalFolderWarningIcon.display = True
        else:
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/AclBookmarks/NoValidFolder')})
            self.Close()

    def OnFolderChange(self, combo, text, value):
        self.folderSelection = value
        if self.bookmark is None:
            self._LoadExpiryOptions()

    def OnExpiryCheckBoxChange(self, checkbox):
        self.expireIn = checkbox.GetReturnValue()

    def OnExpiryCancelCheckBoxChange(self, checkbox):
        self.expiryCancel = checkbox.checked

    def Confirm(self, *args):
        label = self.labelEdit.GetValue()
        if label.strip() == '':
            raise UserError('CustomInfo', {'info': GetByLabel('UI/Map/MapPallet/msgPleaseTypeSomething')})
        label = label.replace('\t', ' ')
        note = self.notesEdit.GetValue()
        self._ConfirmAclBookmark(label, note)
        self.Close()

    def _ConfirmAclBookmark(self, label, note):
        folderID, subfolderID = self.folderCombo.GetValue()
        if self.bookmark is None:
            if self.scannerInfo is not None:
                sm.GetService('bookmarkSvc').ACLBookmarkScanResult(self.locationID, label, note, self.scannerInfo.id, folderID, self.expireIn, subfolderID=subfolderID)
            else:
                sm.GetService('bookmarkSvc').ACLBookmarkLocation(self.locationID, folderID, label, note, self.typeID, self.expireIn, subfolderID=subfolderID)
            settings.char.ui.Set('bookmarkExpiryByFolder_%s_%s' % (folderID, subfolderID), self.expireIn)
        else:
            sm.GetService('bookmarkSvc').UpdateACLBookmark(self.bookmark.bookmarkID, self.bookmark.folderID, label, note, subfolderID, folderID, self.expiryCancel)
        settings.char.ui.Set('bookmarkFolderAndSubfolder', (folderID, subfolderID))

    def Cancel(self, *args):
        self.Close()
