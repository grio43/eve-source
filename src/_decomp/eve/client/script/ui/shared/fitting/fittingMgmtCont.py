#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\fittingMgmtCont.py
from collections import Counter
import blue
import evetypes
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui import ButtonStyle, uiconst
from carbonui.control.button import Button
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.shared.fittingScreen.missingItemsPopup import OpenBuyAllBox
from eve.common.lib.appConst import corpRoleFittingManager, maxLengthFittingDescription
from eveexceptions import UserError
from inventorycommon.const import categoryStructure, numVisibleSubsystems
from inventorycommon.util import IsModularShip, IsSubsystemFlag
from localization import GetByLabel
from shipfitting.exportFittingUtil import AreModulesTranslated
from utillib import KeyVal

class FittingMgmtCont(Container):
    default_align = uiconst.TOALL
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.saveCallback = attributes.get('saveCallback', None)
        self.fittingSvc = sm.GetService('fittingSvc')
        self.saveDeleteButtonsCont = ButtonGroup(name='buttonParent', parent=self, align=uiconst.TOBOTTOM, padTop=8, button_size_mode=ButtonSizeMode.STRETCH)
        self.mainPanel = Container(name='rightMainPanel', parent=self, align=uiconst.TOALL)
        topParent = Container(name='topParent', parent=self.mainPanel, align=uiconst.TOTOP, height=64)
        self.topLeftParent = Container(name='topLeftParent', parent=topParent, align=uiconst.TOLEFT, width=64, padRight=8)
        self.topRightParent = Container(name='topRightParent', parent=topParent, align=uiconst.TOALL)
        self.bottomParent = Container(name='bottomParent', parent=self.mainPanel)
        self.AddTypeIcons()
        self.AddFittingNameElements()
        self.AddDescriptionField()
        self.AddButtons()

    def AddTypeIcons(self):
        self.shipIcon = FittingDraggableIcon2(name='shipIcon', parent=self.topLeftParent, state=uiconst.UI_NORMAL, pos=(0, 0, 64, 64))
        self.shipIcon.fitting = {}
        self.shipIcon.hint = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FittingIconHint')
        self.shipIcon.OnClick = self.ClickDragIcon

    def AddFittingNameElements(self):
        shipInfoCont = Container(name='shipInfoCont', parent=self.topRightParent, align=uiconst.TOTOP, height=SingleLineEditText.default_height, padTop=12)
        iconCont = ContainerAutoSize(name='iconCont', align=uiconst.TORIGHT, parent=shipInfoCont)
        self.infoicon = InfoIcon(parent=iconCont, state=uiconst.UI_HIDDEN, align=uiconst.CENTERRIGHT)
        UtilMenu(menuAlign=uiconst.TOPRIGHT, parent=iconCont, align=uiconst.CENTERRIGHT, pos=(20, 0, 16, 16), GetUtilMenu=self.SettingMenu, texturePath='res:/UI/Texture/SettingsCogwheel.png', hint=GetByLabel('UI/Common/Settings'), iconSize=18)
        self.fittingTypeIcon = Sprite(parent=ContainerAutoSize(parent=shipInfoCont, align=uiconst.TOLEFT), pos=(0, 0, 20, 20), texturePath='res:/UI/Texture/WindowIcons/member.png', align=uiconst.CENTERLEFT)
        self.fittingName = SingleLineEditText(name='fittingName', parent=shipInfoCont, align=uiconst.TOTOP, padding=(4, 0, 4, 0), maxLength=40, label=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FittingName'), fontsize=12, configName='edit_fittingName', maxWidth=120, OnFocusLost=self.OnEditFieldLostFocus, OnSetFocus=self.OnEditFieldSetFocus)
        self.OnEditFieldLostFocus()
        truncatedText = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/Truncated')
        self.truncatedLabel = EveLabelMedium(text=truncatedText, parent=self.topRightParent, pos=(0, 3, 60, 20), state=uiconst.UI_NORMAL, align=uiconst.TOTOP)
        self.truncatedLabel.display = True

    def OnEditFieldLostFocus(self, *args):
        self.fittingName.opacity = 0.5
        self.fittingName.textLabel.opacity = 2.0

    def OnEditFieldSetFocus(self, *args):
        self.fittingName.opacity = 1.0
        self.fittingName.textLabel.opacity = 1.0

    def AddDescriptionField(self):
        self.fittingDescription = EditPlainText(setvalue=None, parent=self.bottomParent, align=uiconst.TOALL, maxLength=maxLengthFittingDescription)
        self.fittingInfo = Scroll(name='fittingInfoScroll', parent=self.bottomParent)
        tabs = [[GetByLabel('UI/Fitting/FittingWindow/FittingManagement/Fittings'),
          self.fittingInfo,
          self,
          None,
          self.fittingInfo], [GetByLabel('UI/Common/Description'),
          self.fittingDescription,
          self,
          None,
          self.fittingDescription]]
        self.fittingInfoTab = TabGroup(name='tabparent', parent=self.bottomParent, idx=0)
        self.fittingInfoTab.Startup(tabs, 'fittingInfoTab')
        self.fittingInfo.Startup()

    def AddButtons(self):
        pass

    def AddFitSaveBtns(self):
        self.fitBtn = Button(parent=self.saveDeleteButtonsCont, label=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/Fit'), func=self.Fit)
        self.saveBtn = Button(parent=self.saveDeleteButtonsCont, label=GetByLabel('UI/Common/Buttons/Save'), func=self.Save, get_menu_entry_data_func=self._get_save_sub_menu_data)
        self.saveBtn.LoadTooltipPanel = self.LoadSaveBtnTooltipPanel

    def _get_save_sub_menu_data(self):
        sub_menu = []
        if session.allianceid:
            alliance = sm.GetService('alliance').GetAlliance(session.allianceid)
            if alliance.executorCorpID == session.corpid:
                sub_menu.append(MenuEntryData(text=GetByLabel('UI/Fitting/FittingWindow/SaveForAlliance'), func=lambda : self.SaveForOwner(session.allianceid)))
        sub_menu.append(MenuEntryData(text=GetByLabel('UI/Fitting/FittingWindow/SaveForCorp'), func=lambda : self.SaveForOwner(session.corpid)))
        sub_menu.append(MenuEntryData(text=GetByLabel('UI/Fitting/FittingWindow/SaveForCharacter', charID=session.charid), func=lambda : self.SaveForOwner(session.charid)))
        return MenuEntryData(text=GetByLabel('UI/Common/Buttons/Save'), func=self.Save, subMenuData=sub_menu)

    def AddDeleteBtn(self):
        self.deleteBtn = Button(parent=self.saveDeleteButtonsCont, label=GetByLabel('UI/Common/Buttons/Delete'), func=self.Delete, style=ButtonStyle.DANGER)

    def TryAddSimulationBtn(self):
        self.simulateButton = Button(parent=self.saveDeleteButtonsCont, label=GetByLabel('UI/Fitting/FittingWindow/Simulate'), func=self.SimulateFitting)

    def AddExportBtn(self):
        self.exportBtn = Button(parent=self.saveDeleteButtonsCont, label=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ExportToClipboard'), func=self.ExportFittingToClipboard, hint=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ExportToClipboardHint'))
        if AreModulesTranslated(session):
            self.exportBtn.LoadTooltipPanel = self.LoadExportTooltipPanel

    def AddMultiBuyBtn(self):
        import shipfitting.multiBuyUtil as multiBuyUtil
        multiBuyUtil.AddBuyButton(parent=self.saveDeleteButtonsCont, fittingMgmtWnd=self)

    def SettingMenu(self, menuParent):
        nameCbChecked = settings.user.ui.Get('useFittingNameForShips', 0)
        menuParent.AddCheckBox(text=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/UseFittingNameForShip'), checked=bool(nameCbChecked), callback=(settings.user.ui.Set, 'useFittingNameForShips', not nameCbChecked))

    def LoadSaveBtnTooltipPanel(self, tooltipPanel, *args):
        hasCorpRoles = bool(session.corprole & corpRoleFittingManager)
        if not hasCorpRoles:
            return
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.columns = 1
        tooltipPanel.margin = (12, 12, 12, 12)
        tooltipPanel.cellPadding = 0
        tooltipPanel.cellSpacing = 10
        saveAllianceBtn = None
        if session.allianceid and sm.GetService('alliance').GetAlliance(session.allianceid).executorCorpID == session.corpid:
            saveAllianceBtn = Button(parent=tooltipPanel, label=GetByLabel('UI/Fitting/FittingWindow/SaveForAlliance'), func=self.SaveForOwner, args=(session.allianceid,), align=uiconst.CENTER)
        saveCorpBtn = Button(parent=tooltipPanel, label=GetByLabel('UI/Fitting/FittingWindow/SaveForCorp'), func=self.SaveForOwner, args=(session.corpid,), align=uiconst.CENTER)
        savePersonalBtn = Button(parent=tooltipPanel, label=GetByLabel('UI/Fitting/FittingWindow/SaveForCharacter', charID=session.charid), func=self.SaveForOwner, args=(session.charid,), align=uiconst.CENTER)
        maxWidth = max(saveCorpBtn.width, savePersonalBtn.width)
        if saveAllianceBtn:
            maxWidth = max(maxWidth, saveAllianceBtn.width)
        saveCorpBtn.width = savePersonalBtn.width = maxWidth
        if saveAllianceBtn:
            saveAllianceBtn.width = maxWidth

    def LoadExportTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.columns = 1
        tooltipPanel.margin = (12, 12, 12, 12)
        tooltipPanel.cellPadding = 0
        tooltipPanel.cellSpacing = 10
        exportBtn = Button(parent=tooltipPanel, label=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ExportToClipboardLocalized'), func=self._ExportFittingToClipboard, args=(True,), align=uiconst.CENTER)
        exportEnglishBtn = Button(parent=tooltipPanel, label=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ExportToClipboard'), func=self._ExportFittingToClipboard, args=(False,), align=uiconst.CENTER)
        maxWidth = max(exportEnglishBtn.width, exportBtn.width)
        exportEnglishBtn.width = exportBtn.width = maxWidth

    def SetFittingTypeIcon(self, fittingOwner):
        if fittingOwner == session.charid:
            texturePath = 'res:/UI/Texture/WindowIcons/member.png'
            text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/PersonalFitting')
        elif fittingOwner == session.corpid:
            texturePath = 'res:/UI/Texture/WindowIcons/corporation.png'
            text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/CorporationFitting')
        else:
            self.fittingTypeIcon.display = False
            return
        self.fittingTypeIcon.display = True
        self.fittingTypeIcon.hint = text
        self.fittingTypeIcon.texturePath = texturePath

    def LoadNewFitting(self, fitting, isTruncated = False):
        self.ShowPanel()
        self.fitting = fitting
        self.fittingName.SetValue(fitting.name)
        self.fittingDescription.SetText(fitting.description)
        self.fittingDescription.SetText(fitting.description)
        shipName = GetShowInfoLink(fitting.shipTypeID, evetypes.GetName(fitting.shipTypeID))
        self.shipIcon.SetTypeID(fitting.shipTypeID)
        self.shipIcon.fitting = fitting
        self.infoicon.Show()
        self.infoicon.SetTypeID(fitting.shipTypeID)
        if isTruncated:
            self.truncatedLabel.display = True
        else:
            self.truncatedLabel.display = False
        fittingOwner = fitting.ownerID
        self.SetFittingTypeIcon(fittingOwner)
        scrolllist = self.fittingSvc.GetFittingInfoScrollList(fitting)
        self.fittingInfo.Load(contentList=scrolllist)
        if evetypes.GetCategoryID(fitting.shipTypeID) == categoryStructure:
            self.fitBtn.Disable()
        else:
            self.fitBtn.Enable()

    def HidePanel(self):
        self.display = False
        self.fitting = None

    def ShowPanel(self):
        self.display = True

    def GetSelectedFitting(self):
        return self.fitting

    def ClickDragIcon(self, *args):
        subsystems = {}
        if IsModularShip(self.fitting.shipTypeID):
            for typeID, flag, qty in self.fitting.fitData:
                if IsSubsystemFlag(flag):
                    subsystems[evetypes.GetGroupID(typeID)] = typeID

            if len(subsystems) != numVisibleSubsystems:
                raise UserError('NotEnoughSubSystemsNotify', {})
        sm.GetService('preview').PreviewType(self.fitting.shipTypeID, subsystems)

    def ShowInfo(self, *args):
        if self.fitting is not None:
            sm.GetService('info').ShowInfo(self.fitting.shipTypeID, None)

    def Fit(self, *args):
        fitting = self.fitting
        failedToLoad = self.fittingSvc.LoadFitting(fitting, getFailedDict=True)
        failedToLoadCounter = Counter({x[0]:x[1] for x in failedToLoad})
        if failedToLoadCounter:
            OpenBuyAllBox(failedToLoadCounter, fitting)
        else:
            from eve.client.script.ui.shared.fittingScreen.fittingWnd import FittingWindow
            wnd = FittingWindow.GetIfOpen()
            if wnd:
                sm.GetService('ghostFittingSvc').TryExitSimulation(askQuestion=True)

    def Save(self, *args):
        if self.fitting.ownerID == session.corpid and bool(session.corprole & corpRoleFittingManager):
            return self.SaveForOwner(session.corpid)
        else:
            return self.SaveForOwner(session.charid)

    def SaveForOwner(self, ownerID):
        if self.fitting.ownerID:
            self.SaveExistingFitting(ownerID)
        else:
            self.SaveNewFitting(ownerID)

    def Delete(self, *args):
        pass

    def SimulateFitting(self, *args):
        SimulateFitting(self.fitting)

    def ExportFittingToClipboard(self, *args):
        self._ExportFittingToClipboard()

    def _ExportFittingToClipboard(self, isLocalized = False):
        sm.GetService('fittingSvc').ExportFittingToClipboard(self.fitting, isLocalized)

    def SaveExistingFitting(self, newOwnerID):
        if self.fitting is None:
            return
        newFitting = None
        if newOwnerID != self.fitting.ownerID:
            return self.SaveNewFitting(newOwnerID)
        if newFitting is not None:
            fitting = newFitting
        else:
            fitting = self.fitting
        newName = self.fittingName.GetValue()
        newDescription = self.fittingDescription.GetValue()
        blue.synchro.Yield()
        self.fittingSvc.ChangeNameAndDescription(fitting.fittingID, fitting.ownerID, newName, newDescription)
        sm.ScatterEvent('OnRedrawFittingMgmt')
        sm.ScatterEvent('OnFittingsUpdated', self.fitting)
        if self.saveCallback:
            self.saveCallback()

    def SaveNewFitting(self, ownerID):
        name = self.fittingName.GetValue()
        description = self.fittingDescription.GetValue()
        fittingID = self.fittingSvc.PersistFitting(ownerID, name, description, fit=(self.fitting.shipTypeID, self.fitting.fitData))
        if fittingID > 0 and self.saveCallback:
            self.saveCallback()


class FittingMgmtContInWnd(FittingMgmtCont):

    def Delete(self, *args):
        if eve.Message('DeleteFitting', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        if not self.fitting:
            return
        ownerID = self.fitting.ownerID
        fittingID = self.fitting.fittingID
        self.fittingSvc.DeleteFitting(ownerID, fittingID)
        self.HidePanel()

    def AddButtons(self):
        self.AddFitSaveBtns()
        self.AddMultiBuyBtn()
        self.TryAddSimulationBtn()
        self.AddExportBtn()
        self.AddDeleteBtn()


class FittingMgmtContInStandalone(FittingMgmtCont):

    def AddButtons(self):
        self.AddFitSaveBtns()
        self.AddMultiBuyBtn()
        self.TryAddSimulationBtn()


class FittingDraggableIcon2(ItemIcon):
    __guid__ = 'xtriui.FittingDraggableIcon2'
    isDragObject = True

    def Startup(self, fitting):
        self.fitting = fitting

    def GetDragData(self, *args):
        entry = KeyVal()
        entry.fitting = self.fitting
        entry.__guid__ = 'listentry.FittingEntry'
        return [entry]


def SimulateFitting(fitting):
    from eve.client.script.ui.shared.fittingScreen.fittingWnd import FittingWindow
    wnd = FittingWindow.GetIfOpen()
    if wnd:
        wnd.Maximize()
    else:
        uicore.cmd.OpenFitting()
    sm.GetService('ghostFittingSvc').SimulateFitting(fitting)
