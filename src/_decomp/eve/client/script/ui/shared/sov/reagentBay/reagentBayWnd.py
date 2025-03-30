#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\reagentBay\reagentBayWnd.py
import evetypes
import locks
import mathext
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbon.common.script.util.format import FmtAmt
from carbonui import TextColor, uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.window import Window
import carbonui
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.control.loadingContainer import LoadingContainer
from eve.client.script.ui.shared.sov.reagentBay.controllers import ReagentBayWndController, InputItemController
from eve.client.script.ui.shared.sov.threadedLoader import ThreadedLoader
from eveservices.menu import GetMenuService
from eveui import animation
from inventorycommon.const import shipColonyResourcesHold
from localization import GetByLabel
import inventorycommon.const as invConst
from sovereignty.client.quasarCallWrapper import DATA_NOT_AVAILABLE
from threadutils import throttled
import math
import logging
logger = logging.getLogger(__name__)

def OpenReagnetBay(sovHubID, solarSystemID, isStationMgr):
    wnd = ReagnetBayWnd.GetIfOpen(windowInstanceID=sovHubID)
    if wnd and not wnd.destroyed:
        wnd.Maximize()
        if not wnd.wnController.IsSameItemID(sovHubID):
            wnd.LoadWnd(sovHubID, solarSystemID, isStationMgr)
    else:
        ReagnetBayWnd.Open(sovHubID=sovHubID, solarSystemID=solarSystemID, isStationMgr=isStationMgr)


class ReagnetBayWnd(Window):
    __guid__ = 'ReagnetBayWnd'
    default_minSize = [500, 290]
    default_windowID = 'reagnetBayWnd'
    default_captionLabelPath = 'UI/Sovereignty/SovHub/ReagentBay/SovereigntyHubReagentBay'
    __notifyevents__ = ['OnSessionChanged', 'OnItemChange']

    def DebugReload(self, *args):
        sovHubID = self.wnController.sovHubID
        solarSystemID = self.wnController.solarSystemID
        isStationMgr = self.wnController.isStationMgr
        self.Close()
        OpenReagnetBay(sovHubID, solarSystemID, isStationMgr)

    def ApplyAttributes(self, attributes):
        super(ReagnetBayWnd, self).ApplyAttributes(attributes)
        sovHubID = attributes.sovHubID
        solarSystemID = attributes.solarSystemID
        isStationMgr = attributes.isStationMgr
        self.wnController = ReagentBayWndController(sovHubID, solarSystemID, isStationMgr)
        self.inputEntriesByTypeID = {}
        self.threadedLoader = ThreadedLoader('ReagnetBayWnd')
        self.ConstructUI()
        sm.RegisterNotify(self)

    def ConstructUI(self):
        self.loadingCont = LoadingContainer(parent=self.content, failureStateMessage=GetByLabel('UI/Sovereignty/SovHub/HubWnd/FailedToFetchData'), retryBtnLabel=GetByLabel('UI/Personalization/PaintTool/ErrorRetry'))
        btnGroup = ButtonGroup(parent=self.loadingCont, button_alignment=carbonui.AxisAlignment.END)
        self.upgradesLabel = carbonui.TextBody(parent=self.loadingCont, text='', align=carbonui.Align.BOTTOMLEFT)
        self.comboParent = ContainerAutoSize(parent=self.loadingCont, name='comboParent', align=carbonui.Align.TOTOP)
        self.sourceCombo = Combo(parent=self.comboParent, align=carbonui.Align.TOPRIGHT, prefskey=self.wnController.GetComboPrefsKey(), callback=self.OnComboChanged)
        reagentParentCont = ContainerAutoSize(parent=self.loadingCont, name='reagentParentCont', align=carbonui.Align.TOTOP, minHeight=64, alignMode=carbonui.Align.TOTOP)
        self.reagentCont = ContainerAutoSize(parent=reagentParentCont, name='reagentCont', align=carbonui.Align.TOTOP)
        self.reagentLoadingWheel = LoadingWheel(parent=reagentParentCont, align=carbonui.Align.CENTER, width=64, height=64)
        noReagentDataText = GetByLabel('UI/Sovereignty/SovHub/ReagentBay/NoReagentDataAvailable')
        self.noReagentDataAvailableLabel = carbonui.TextBody(parent=reagentParentCont, align=carbonui.Align.CENTER, text=noReagentDataText)
        self.noReagentDataAvailableLabel.display = False
        depositText = GetByLabel('UI/Sovereignty/SovHub/ReagentBay/DepositReagentBtn')
        self.depositBtn = Button(parent=self.loadingCont, label=depositText, func=self.Deposit)
        btnGroup.add_button(self.depositBtn)
        self.loadingCont.LoadContent(loadCallback=self.LoadWnd)

    def LoadWnd(self):
        self.wnController.PrimeFuelByTypeID()
        self.reagentCont.Flush()
        self.LoadCombo()
        self.threadedLoader.StartLoading(self.LoadReagents_thread, self)
        self.threadedLoader.StartLoading(self.LoadInstalledUpgrades_thread, self)
        self.UpdateBtn()
        solarSystemName = cfg.evelocations.Get(self.wnController.solarSystemID).name
        self.caption = GetByLabel('UI/Sovereignty/SovHub/ReagentBay/SovereigntyHubReagentBayWithSystemName', solarSystemName=solarSystemName)

    def LoadCombo(self):
        sourceOptions = self.wnController.GetSourceOptions()
        self.comboParent.display = bool(sourceOptions)
        if not sourceOptions:
            self.comboParent.display = False
            return
        self.sourceCombo.LoadOptions(sourceOptions)
        self._SetUseResourceHoldValue(self.sourceCombo.GetValue())

    def LoadInstalledUpgrades_thread(self):
        self.upgradesLabel.text = ''
        if not self.wnController.CanSeeUpgrades():
            return
        installedUpgradesText = self.wnController.GetNumOnlineAndInstalledUpgradesText()
        if installedUpgradesText == DATA_NOT_AVAILABLE:
            self.upgradesLabel.text = GetByLabel('UI/Sovereignty/SovHub/ReagentBay/NoDataAvailable')
        self.upgradesLabel.text = installedUpgradesText

    def LoadReagents_thread(self):
        if self.destroyed:
            return
        animation.fade_in(self.reagentLoadingWheel)
        self.noReagentDataAvailableLabel.Hide()
        try:
            fuelByTypeID = self.wnController.GetFuelByTypeID()
            if self.destroyed:
                return
            if fuelByTypeID == DATA_NOT_AVAILABLE:
                self.noReagentDataAvailableLabel.Show()
                return
            self._LoadReagents(fuelByTypeID)
        finally:
            animation.fade_out(self.reagentLoadingWheel, duration=0.1)

    def _LoadReagents(self, fuelByTypeID):
        self.inputEntriesByTypeID.clear()
        cargoQtyByTypeID = self.wnController.GetQtyByTypeID_InHold()
        for typeID, fuel in fuelByTypeID.iteritems():
            itemController = InputItemController(typeID, fuel.amount_now, fuel.burned_per_hour)
            qtyInCargo = cargoQtyByTypeID.get(typeID, 0)
            inputEntry = ReagentBayInputItem(parent=self.reagentCont, align=carbonui.Align.TOTOP, itemController=itemController, wndController=self.wnController, inputFieldChangedCallback=self.OnInputChanged, qtyInCargo=qtyInCargo, paddingValue=3, padBottom=1)
            self.inputEntriesByTypeID[typeID] = inputEntry

        self.Refresh()

    def OnInputChanged(self, *args):
        self.Refresh()

    def OnComboChanged(self, cb, key, val):
        self._SetUseResourceHoldValue(val)
        self.Refresh()

    def _SetUseResourceHoldValue(self, val):
        if val and val[0] == shipColonyResourcesHold:
            useResourceHold = True
        else:
            useResourceHold = False
        self.wnController.useResourceHold = useResourceHold

    def Refresh(self):
        self._RefreshThrottled()

    @throttled(0.5)
    def _RefreshThrottled(self):
        if self.wnController.busyDepositingItems:
            return
        self.UpdateInputEntries()
        self.UpdateBtn()

    def UpdateInputEntries(self):
        sovHubFuelByTypeID = self.wnController.GetFuelByTypeID()
        cargoQtyByTypeID = self.wnController.GetQtyByTypeID_InHold()
        for typeID, inputEntry in self.inputEntriesByTypeID.iteritems():
            if inputEntry.destroyed:
                continue
            fuelInSovHub = sovHubFuelByTypeID.get(typeID, 0)
            qtyInCargo = cargoQtyByTypeID.get(typeID, 0)
            amountInSovHub = fuelInSovHub.amount_now
            inputEntry.UpdateEntry(amountInSovHub, qtyInCargo, fuelInSovHub.burned_per_hour)

    def UpdateBtn(self):
        if self.wnController.depositBtnDelay:
            return
        numItems = sum((qty for qty in self.GetTypeIDsAndQtyFromInputEntries().itervalues()))
        if numItems > 0:
            self.depositBtn.Enable()
        else:
            self.depositBtn.Disable()

    def Deposit(self, *args):
        with locks.TempLock('ReagnetBayWnd_DepositItems_%s' % self.wnController.sovHubID):
            sucessfulDeposit = False
            try:
                self.wnController.busyDepositingItems = True
                self.wnController.depositBtnDelay = True
                self.depositBtn.Disable()
                self.depositBtn.busy = True
                qtyByTypeID = self.GetTypeIDsAndQtyFromInputEntries()
                if self.DepositConfirmed(qtyByTypeID):
                    failedToMove = self.wnController.DoDepositItems(qtyByTypeID)
                    sucessfulDeposit = not failedToMove
            finally:
                self.depositBtn.busy = False
                self.wnController.busyDepositingItems = False
                if sucessfulDeposit:
                    self.Close()
                else:
                    uthread2.call_after_wallclocktime_delay(self.EnableBtnAfterDeposit, 1.0)
                self.Refresh()

    def EnableBtnAfterDeposit(self):
        self.wnController.depositBtnDelay = False
        self.UpdateBtn()

    def GetTypeIDsAndQtyFromInputEntries(self):
        qtyByTypeID = {}
        for typeID, inputEntry in self.inputEntriesByTypeID.iteritems():
            inputQty = inputEntry.GetInputQty()
            qtyByTypeID[typeID] = inputQty

        return qtyByTypeID

    def DepositConfirmed(self, qtyByTypeID):
        if self.wnController.useResourceHold:
            dialogKey = 'ConfirmReagentDepositFromReagentBay'
        else:
            dialogKey = 'ConfirmReagentDepositFromCargo'
        depositTextList = [ u'\u2022 %s' % GetByLabel('UI/Common/QuantityAndItem', quantity=qty, item=typeID) for typeID, qty in qtyByTypeID.iteritems() if qty ]
        depositText = '<br>'.join(depositTextList)
        if eve.Message(dialogKey, {'itemList': depositText,
         'rewardText': ''}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            return True
        return False

    def OnSessionChanged(self, isRemote, sess, change):
        if 'shipid' in change:
            self.LoadCombo()
            self.Refresh()

    def OnItemChange(self, item, change, location):
        validFlags = {invConst.flagCargo, invConst.flagColonyResourcesHold}
        if item.locationID == session.shipid and item.flagID in validFlags:
            self.Refresh()
        elif change.get(const.ixLocationID, None) == session.shipid and change.get(const.ixFlag, None) in validFlags:
            self.Refresh()

    def GetMenuMoreOptions(self):
        menu_data = super(ReagnetBayWnd, self).GetMenuMoreOptions()
        if session.role & ROLE_PROGRAMMER:
            menu_data.AddEntry('QA Reload', self.DebugReload)
        return menu_data


class ReagentBayInputItem(ContainerAutoSize):
    default_align = carbonui.Align.TOTOP
    default_minHeight = 88
    default_alignMode = carbonui.Align.TOTOP

    def ApplyAttributes(self, attributes):
        super(ReagentBayInputItem, self).ApplyAttributes(attributes)
        self.wndController = attributes.wndController
        self.inputItemController = attributes.itemController
        self.inputFieldChangedCallback = attributes.inputFieldChangedCallback
        self.paddingValue = attributes.paddingValue or 0
        qtyInCargo = attributes.qtyInCargo
        self.ConstructTypeIcon()
        self.ConstructInput(qtyInCargo)
        self.ConstructLabels()

    def ConstructTypeIcon(self):
        iconSize = 64
        gaugeSize = iconSize + 10
        leftCont = Container(parent=self, name='leftCont', align=carbonui.Align.TOLEFT, width=gaugeSize, left=10)
        self.iconGaugeCont = IconGaugeCont(parent=leftCont, align=carbonui.Align.CENTERLEFT, pos=(0,
         0,
         gaugeSize,
         gaugeSize), gaugeSize=gaugeSize, iconSize=iconSize, typeID=self.inputItemController.typeID)

    def ConstructInput(self, qtyInCargo):
        rightPad = self.paddingValue + 10
        rightCont = Container(parent=self, name='rightCont', align=carbonui.Align.TORIGHT, width=100, left=rightPad)
        self.inputEdit = SingleLineEditInteger(parent=rightCont, width=100, OnChange=self.OnInputFieldChanged, setvalue=qtyInCargo, align=carbonui.Align.CENTERRIGHT)

    def ConstructLabels(self):
        textCont = ContainerAutoSize(parent=self, name='textCont', align=carbonui.Align.TOTOP, padLeft=12)
        grid = LayoutGrid(parent=textCont, align=carbonui.Align.TOPLEFT, columns=2, cellSpacing=(10, 6), top=16)
        carbonui.TextBody(parent=grid, align=carbonui.Align.CENTERLEFT, text=evetypes.GetName(self.inputItemController.typeID))
        self.timeLeftLabel = carbonui.TextDetail(parent=grid, align=carbonui.Align.CENTERLEFT, text='', color=TextColor.SECONDARY)
        self.currentLabel = carbonui.TextBody(text='', color=TextColor.SECONDARY)
        grid.AddCell(self.currentLabel, colSpan=2)
        self.burnRateLabel = carbonui.TextBody(text='', color=TextColor.SECONDARY)
        grid.AddCell(self.burnRateLabel, colSpan=2)

    def RefreshNumbers(self):
        maxToAdd = self.inputItemController.maxToAdd
        self.inputEdit.SetMaxValue(maxToAdd)
        self.currentLabel.text = GetByLabel('UI/Sovereignty/SovHub/ReagentBay/CurrentInHub', qtyInHub=FmtAmt(self.inputItemController.unitsInSovHub))
        rateText = GetByLabel('UI/Sovereignty/AmountPerHour', value=self.inputItemController.burnRate)
        self.burnRateLabel.text = GetByLabel('UI/Sovereignty/SovHub/ReagentBay/FuelBurnRate', burnRate=rateText)
        self.timeLeftLabel.text = self.inputItemController.GetTimesLeft(self.GetInputQty())
        self.inputEdit.Show()
        value = self.GetInputQty()
        self.inputItemController.currentValueIfSelected = min(value, maxToAdd)
        if value > maxToAdd:
            self.inputEdit.SetValue(maxToAdd, False)
        self.UpdateGaugeProgress()

    def UpdateGaugeProgress(self):
        unitsInWnd = self.GetInputQty()
        progressInHub, progressInWnd = self.inputItemController.GetProgress(unitsInWnd)
        self.iconGaugeCont.SetProgress(progressInHub, mathext.clamp(progressInHub + progressInWnd, 0, 1))

    def GetInputQty(self):
        return self.inputEdit.GetValue()

    def OnInputFieldChanged(self, *args):
        if self.inputFieldChangedCallback:
            self.inputFieldChangedCallback(*args)

    def UpdateEntry(self, unitsInSovHub, qtyInCargo, burnRate):
        self.inputItemController.unitsInSovHub = unitsInSovHub
        self.inputItemController.qtyInCargo = qtyInCargo
        self.inputItemController.burnRate = burnRate
        self.RefreshUI()

    def RefreshUI(self):
        self.RefreshNumbers()
        self.UpdateEnabledLook()

    def UpdateEnabledLook(self):
        if self.inputItemController.qtyInCargo:
            self.opacity = 1.0
        else:
            self.opacity = 0.25
        self.UpdateInputHint()

    def UpdateInputHint(self):
        if self.inputItemController.qtyInCargo:
            hintPath = self.wndController.GetQtyInCargoHintPath()
            hint = GetByLabel(hintPath, qty=self.inputItemController.qtyInCargo)
        else:
            hint = GetByLabel(self.wndController.GetNoQtyInCargoHintPath())
        self.inputEdit.hint = hint


class IconGaugeCont(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(IconGaugeCont, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID
        iconSize = attributes.iconSize
        gaugeSize = attributes.gaugeSize
        self.typeCont = Container(parent=self, name='typeCont', align=uiconst.CENTER, pos=(0,
         0,
         iconSize,
         iconSize))
        typeIcon = Sprite(parent=self.typeCont, name='typeIcon', align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, pos=(0,
         0,
         iconSize,
         iconSize))
        sm.GetService('photo').GetIconByType(typeIcon, self.typeID)
        gaugeCont = Container(parent=self, name='gaugeCont', pos=(0,
         0,
         gaugeSize,
         gaugeSize), align=uiconst.CENTERRIGHT)
        self.gauge = GaugeCircular(parent=gaugeCont, colorStart=eveColor.CRYO_BLUE, colorEnd=eveColor.CRYO_BLUE, radius=gaugeSize / 2, align=uiconst.CENTER, state=uiconst.UI_DISABLED, colorBg=(0, 0, 0, 0), showMarker=False, startAngle=math.pi / 2)
        self.inWndGauge = GaugeCircular(parent=gaugeCont, radius=gaugeSize / 2, colorStart=eveColor.SILVER_GREY, colorEnd=eveColor.SILVER_GREY, align=uiconst.CENTER, state=uiconst.UI_DISABLED, showMarker=False, startAngle=math.pi / 2)

    def OnClick(self, *args):
        return sm.GetService('info').ShowInfo(self.typeID)

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(None, self.typeID)

    def SetProgress(self, unitsInContainerProgress, unitsInWndProgress):
        self.gauge.SetValue(unitsInContainerProgress)
        self.inWndGauge.SetValue(unitsInWndProgress)
