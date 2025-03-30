#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\sovHub\sovHubWnd.py
import eveicon
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control.loadingContainer import LoadingContainer
from eve.client.script.ui.shared.mapView.mapViewConst import VIEWMODE_MARKERS_SETTINGS, MAPVIEW_PRIMARY_ID, MARKERS_OPTION_SOV_HUBS
from eve.client.script.ui.shared.mapView.mapViewSettings import GetMapViewSetting, SetMapViewSetting
from eve.client.script.ui.shared.mapView.settings import classic_map_enabled_setting
from eve.client.script.ui.shared.sov.sovHub.changesWarning import LoadSaveBtnTooltipPanel
from eve.client.script.ui.shared.sov.sovHub.hubController import HubController
import carbonui
from eve.client.script.ui.shared.sov.sovHub.resourceConts import PowerCont, WorkforceCont
from eve.client.script.ui.shared.sov.sovHub.fuelConts import FuelMagmaCont, FuelIceCont, StartupCostCont
from eve.client.script.ui.shared.sov.sovHub.editSections import TransitCont, AclSectionCont
from eve.client.script.ui.shared.sov.sovHub.summaryCont import SummaryCont
from eve.client.script.ui.shared.sov.sovHub.upgradeScrollCont import UpgradeScrollCont
from eve.client.script.ui.shared.sov.threadedLoader import ThreadedLoader
from eveexceptions import ExceptionEater
from localization import GetByLabel
import carbonui.const as uiconst

def OpenSovHubWnd(itemID, solarSystemID):
    wnd = SovHubWnd.GetIfOpen(windowInstanceID=itemID)
    if wnd and not wnd.destroyed:
        wnd.Maximize()
        if not wnd.hubController.IsSameItemID(itemID):
            wnd.LoadWindow(itemID, solarSystemID)
    else:
        SovHubWnd.Open(itemID=itemID, solarSystemID=solarSystemID, windowInstanceID=itemID)


class SovHubWnd(Window):
    __guid__ = 'SovHubWnd'
    default_minSize = [960, 590]
    default_windowID = 'sovHubWnd'
    default_captionLabelPath = 'UI/Sovereignty/SovHub/HubWnd/SovHub'
    default_isCompact = True

    def DebugReload(self, *args):
        itemID = self.hubController.itemID
        solarSystemID = self.hubController.solarSystemID
        self.Close()
        OpenSovHubWnd(itemID, solarSystemID)

    def ApplyAttributes(self, attributes):
        self.hubController = None
        self.scrollCont = None
        self.threadedLoader = ThreadedLoader('SovHubWnd')
        super(SovHubWnd, self).ApplyAttributes(attributes)
        itemID = attributes.itemID
        solarSystemID = attributes.solarSystemID
        self.hubController = HubController(itemID, solarSystemID)
        self.caption = self.hubController.GetHubName()
        if session.role & ROLE_PROGRAMMER:
            reloadBtn = Button(parent=self.content, label='Reload', align=carbonui.Align.BOTTOMLEFT, func=self.DebugReload, top=0, idx=0)
        self.ConstructUI()
        classic_map_enabled_setting.on_change.connect(self.OnClassicMapChanged)
        self.hubController.on_order_changed.connect(self.OnOrderChanged)
        self.hubController.on_online_state_changed.connect(self.OnOnlineStateChanged)
        self.hubController.on_upgrades_changed.connect(self.OnUpgradesChanged)
        self.hubController.workforceController.on_workforce_changed.connect(self.OnWorkforceChanged)
        self.on_end_scale.connect(self.OnEndScale)
        self.loadingCont.LoadContent(loadCallback=self.LoadWindow)

    def ConstructUI(self):
        self.loadingCont = LoadingContainer(parent=self.content, failureStateMessage=GetByLabel('UI/Sovereignty/SovHub/HubWnd/FailedToFetchData'), retryBtnLabel=GetByLabel('UI/Personalization/PaintTool/ErrorRetry'))
        self.rightCont = Container(name='rightCont', parent=self.loadingCont, align=carbonui.Align.TORIGHT, width=300, clipChildren=True, padLeft=24)
        self.leftCont = Container(name='leftCont', parent=self.loadingCont, align=carbonui.Align.TOALL)
        btnGroup = ButtonGroup(parent=self.leftCont)
        self.saveChangesBtn = Button(label=GetByLabel('UI/Sovereignty/SovHub/HubWnd/SaveChanges'), func=self.SaveChanges)
        self.saveChangesBtn.LoadTooltipPanel = self.LoadSaveBtnTooltipPanel
        self.saveChangesBtn.Disable()
        btnGroup.add_button(self.saveChangesBtn)
        self.topCont = ContainerAutoSize(name='topCont', parent=self.leftCont, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP)
        self.nameLabel = carbonui.TextHeader(parent=self.topCont, text=self.hubController.GetHubName(), align=carbonui.Align.TOTOP, maxLines=1, top=0, padLeft=26)
        self.mapBtn = ButtonIcon(parent=self.topCont, align=carbonui.Align.TOPLEFT, pos=(6, 4, 16, 16), texturePath=eveicon.location, func=self.ShowOnMap)
        self.SetMapBtnStateAndHint()
        self.summaryCont = SummaryCont(parent=self.topCont, hubController=self.hubController, top=6, padLeft=10)
        self.scrollCont = UpgradeScrollCont(parent=self.leftCont, hubController=self.hubController)
        self.ConstructRightSide()

    def LoadWindow(self):
        self.hubController.PrimeData()
        self.threadedLoader.StartLoading(self.LoadScroll_thread, self)
        self.threadedLoader.StartLoading(self.LoadTopCont_thread, self)
        self.powerCont.LoadContAsync()
        self.workforceCont.LoadContAsync()
        self.threadedLoader.StartLoading(self.transitCont.LoadSection, self.transitCont)
        self.threadedLoader.StartLoading(self.aclSectionCont.LoadSection, self.aclSectionCont)
        self.threadedLoader.StartLoading(self.fuelCont.LoadUI, self.fuelCont)
        self.threadedLoader.StartLoading(self.iceCont.LoadUI, self.iceCont)
        self.threadedLoader.StartLoading(self.startupCont.LoadUI, self.startupCont)

    def LoadScroll_thread(self):
        self.scrollCont.LoadScroll()

    def SaveChanges(self, *args):
        with self.saveChangesBtn.busy_context:
            try:
                self.UpdateWndState()
                self.hubController.SaveChanges()
            finally:
                uthread2.StartTasklet(self.UpdateWndState)

    def UpdateWndState(self):
        if self.saveChangesBtn.busy:
            self.scrollCont.Disable()
        else:
            self.scrollCont.Enable()

    def UpdateBtn(self):
        if self.hubController.AreThereUnsavedChanges():
            self.saveChangesBtn.Enable()
        else:
            self.saveChangesBtn.Disable()

    def OnOrderChanged(self):
        self._UpdateWnd()

    def OnOnlineStateChanged(self, typeID):
        self.UpdateBtn()

    def OnUpgradesChanged(self):
        self._UpdateWnd()

    def OnWorkforceChanged(self):
        self._UpdateWnd()

    def _UpdateWnd(self):
        self.threadedLoader.StartLoading(self.LoadScroll_thread, self)
        self.UpdateBtn()

    def LoadTopCont_thread(self):
        self.summaryCont.LoadSummary()

    def ConstructRightSide(self):
        cont = ContainerAutoSize(parent=self.rightCont, align=carbonui.Align.TOTOP)
        self.powerCont = PowerCont(parent=self.rightCont, controller=self.hubController)
        self.hubController.on_online_state_changed.connect(self.powerCont.LoadContAsync)
        self.hubController.on_upgrades_changed.connect(self.powerCont.LoadContAsync)
        self.workforceCont = WorkforceCont(parent=self.rightCont, controller=self.hubController, top=10)
        self.hubController.on_online_state_changed.connect(self.workforceCont.LoadContAsync)
        self.hubController.workforceController.on_workforce_changed.connect(self.workforceCont.LoadContAsync)
        self.hubController.on_upgrades_changed.connect(self.workforceCont.LoadContAsync)
        self.transitCont = TransitCont(parent=self.rightCont, align=carbonui.Align.TOTOP, workforceController=self.hubController.workforceController)
        self.aclSectionCont = AclSectionCont(parent=self.rightCont, align=carbonui.Align.TOTOP, controller=self.hubController, top=20, canEdit=self.hubController.CanEditACL())
        header = carbonui.TextDetail(parent=self.rightCont, text=GetByLabel('UI/Sovereignty/SovHub/HubWnd/FuelLevels'), color=carbonui.TextColor.SECONDARY, align=carbonui.Align.TOTOP, pickState=carbonui.PickState.ON, top=20)
        cont = Container(parent=self.rightCont, align=carbonui.Align.TOTOP, height=120, top=0)
        fuelGrid = LayoutGrid(parent=cont, columns=2, cellSpacing=10, align=carbonui.Align.CENTER)
        self.fuelCont = FuelMagmaCont(parent=fuelGrid, hubController=self.hubController)
        self.iceCont = FuelIceCont(parent=fuelGrid, hubController=self.hubController)
        self.startupCont = StartupCostCont(parent=self.rightCont, hubController=self.hubController, top=10)

    def LoadSaveBtnTooltipPanel(self, tooltipPanel, *args):
        LoadSaveBtnTooltipPanel(tooltipPanel, self.hubController)

    def OnEndScale(self, *args):
        if self.scrollCont is None or self.scrollCont.destroyed:
            return
        self.scrollCont.OnWndEndScale()

    def OnClassicMapChanged(self, *args):
        self.SetMapBtnStateAndHint()

    def SetMapBtnStateAndHint(self):
        usingOldMap = classic_map_enabled_setting.is_enabled()
        if usingOldMap:
            self.mapBtn.Disable()
            self.mapBtn.hint = GetByLabel('UI/Sovereignty/ShowSovHubOnMapOldMapActive')
        else:
            self.mapBtn.Enable()
            self.mapBtn.hint = GetByLabel('UI/Sovereignty/ShowSovHubOnMap')

    def ShowOnMap(self, *args):
        self.ForceMarkersOn()
        solarSystemID = self.hubController.solarSystemID
        sm.GetService('menu').ShowInMap(itemID=solarSystemID)

    def ForceMarkersOn(self):
        settingGroupKey = VIEWMODE_MARKERS_SETTINGS
        mapViewID = MAPVIEW_PRIMARY_ID
        currentActive = set(GetMapViewSetting(settingGroupKey, mapViewID))
        if MARKERS_OPTION_SOV_HUBS in currentActive:
            return
        currentActive.add(MARKERS_OPTION_SOV_HUBS)
        SetMapViewSetting(settingGroupKey, list(currentActive), mapViewID)
        sm.ScatterEvent('OnSovHubMarkersChanged')

    def CloseByUser(self, *args):
        if self.hubController and self.hubController.AreThereUnsavedChanges():
            if eve.Message('ConfirmCloseSovHubWnd', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return
        super(SovHubWnd, self).CloseByUser()

    def Close(self, *args, **kwds):
        with ExceptionEater('Closing SovHubWnd'):
            self.hubController.Disconnect()
            self.hubController = None
            self.on_end_scale.disconnect(self.OnEndScale)
            classic_map_enabled_setting.on_change.disconnect(self.OnClassicMapChanged)
        super(SovHubWnd, self).Close(*args, **kwds)
