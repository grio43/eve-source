#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\skyhook\skyhookWnd.py
import datetimeutils
import gametime
import numbers
import carbonui
import eveicon
import evetypes
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import TextColor, TextAlign
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.window import Window
import carbonui.uiconst as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from const import MIN
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.toggleSwitch import ToggleSwitch
from eve.client.script.ui.shared.skyhook import NOT_AVAILABLE
from eve.client.script.ui.shared.skyhook.uiController import CurrentSkyhookUiController
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions import ExceptionEater
from eveservices.menu import GetMenuService
from eveui import animation
from inventorycommon.typeHelpers import GetAveragePrice
from localization import GetByLabel
import logging
from localization.formatters import FormatTimeIntervalShortWritten
from sovereignty.skyhook.shared.skyhook_type_inference import is_reagent_skyhook
from spacecomponents.client.components.orbitalSkyhook import IsCharacterAuthorisedToTakeFromSkyhook
logger = logging.getLogger(__name__)

def OpenSkyhookWindow(itemID):
    wnd = SkyhookWnd.GetIfOpen()
    if wnd and not wnd.destroyed:
        wnd.Maximize()
        if not wnd.dataController.IsSameItemID(itemID):
            wnd.LoadWindow(itemID)
    else:
        SkyhookWnd.Open(itemID=itemID)


PRODUCING_THREAD = 'producingThread'
ONLINE_STATE_THREAD = 'onlineStateThread'
REAGENTS_QTY_THREAD = 'reagentsQtyThread'
REAGENTS_TYPES_THREAD = 'reagentsTypesThread'

class SkyhookWnd(Window):
    __guid__ = 'SkyhookWnd'
    default_minSize = [520, 250]
    default_windowID = 'obitalSkyhookWnd'
    default_captionLabelPath = 'UI/OrbitalSkyhook/OrbitalSkyhook'
    default_iconNum = 'res:/ui/Texture/WindowIcons/skyhook.png'
    __notifyevents__ = ['OnReagentsUpdated', 'OnSessionChanged']

    def DebugReload(self, *args):
        itemID = self.dataController.itemID
        self.Close()
        OpenSkyhookWindow(itemID)

    def ApplyAttributes(self, attributes):
        self.threadedLoader = ThreadedLoader()
        self._reagentsLoaded = False
        self.regentStorageLabel = None
        self.constructionDone = False
        self.progressThread = None
        super(SkyhookWnd, self).ApplyAttributes(attributes)
        itemID = attributes.itemID
        self.dataController = self.CreateDataController(itemID)
        self.product = None
        self.ConstructUI()
        self.LoadWindow(itemID)

    def CreateDataController(self, itemID):
        isAuthorisedToTake = IsCharacterAuthorisedToTakeFromSkyhook(itemID)
        controller = CurrentSkyhookUiController(itemID, isAuthorisedToTake)
        controller.on_linked_ship_updated.connect(self.OnLinkedShipChanged)
        return controller

    def ConstructUI(self):
        bottomPad = 8
        self.topSection = ContainerAutoSize(name='topSection', parent=self.content, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, padBottom=bottomPad)
        padding = self.content_padding[0]
        self.topSection.bgFill = Fill(bgParent=self.topSection, color=eveThemeColor.THEME_FOCUSDARK, opacity=0.25, padding=(-padding,
         0,
         -padding,
         -bottomPad))
        topCont = ContainerAutoSize(parent=self.topSection, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, top=6, padLeft=8, PadTop=4)
        self.buttonCont = ContainerAutoSize(parent=topCont, align=carbonui.Align.TORIGHT, left=8)
        self.onlineOfflineCont = OnlineOfflineCont(parent=self.buttonCont, dataController=self.dataController, align=carbonui.Align.TORIGHT, alignMode=uiconst.TOPLEFT)
        self.processingTimer = ProcessingTimer(parent=self.topSection, align=carbonui.Align.TOPRIGHT, alignMode=uiconst.TOPLEFT, dataController=self.dataController, pickState=carbonui.PickState.ON, top=40, left=8)
        self.nameLabel = carbonui.TextHeadline(parent=topCont, align=carbonui.Align.TOTOP)
        self.ownerValueLabel, _ = self.ConstructLabelContainers(self.topSection, GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/Owner'), top=16)
        self.supplyingValueLabel, _ = self.ConstructLabelContainers(self.topSection, GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/Supplying'))
        self.producingValueLabel, _ = self.ConstructLabelContainers(self.topSection, GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/Producing'))
        self.producingRichnessSprite = Sprite(name='producingRichnessSprite', parent=self.producingValueLabel.parent, pos=(4, 0, 16, 16), align=carbonui.Align.CENTERLEFT, opacity=0.75)
        self.producingValueLabel.left = 20
        self.vulnerabilityValueLabel, self.vulnerabilityCont = self.ConstructLabelContainers(self.topSection, GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/VulnerabilityLabel'))
        self.vulnerabilityValueLabel.display = False
        self.vulnerabilityCont.display = False
        self.ConstructReagentSection()
        self.btnGroup = ButtonGroup(parent=self.content, align=uiconst.BOTTOMRIGHT, pos=(8, 8, 0, 0))
        self.takeBtn = Button(label=GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/TakeReagents', volume=0), func=self.TakeReagents, enabled=False)
        self.btnGroup.add_button(self.takeBtn)
        self.btnGroup.display = False
        self.constructionDone = True

    def ConstructLabelContainers(self, parent, headerText, labelClass = carbonui.TextBody, textAlign = TextAlign.LEFT, top = 1):
        minLineHeight = 20
        lineCont = ContainerAutoSize(name='lineCont', parent=parent, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, top=top, minHeight=minLineHeight, padLeft=8)
        headerCont = ContainerAutoSize(name='headerCont', parent=lineCont, align=carbonui.Align.TOLEFT)
        headerLabel = labelClass(name='headerLabel', parent=headerCont, text=headerText, align=carbonui.Align.TOPLEFT, color=TextColor.SECONDARY)
        rightLineCont = ContainerAutoSize(name='rightLineCont', parent=lineCont, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, minHeight=minLineHeight)
        valueLabel = labelClass(name='valueLabel', parent=rightLineCont, text='', align=carbonui.Align.TOTOP, padLeft=4, state=uiconst.UI_NORMAL, textAlign=textAlign)
        loadingWheelAlign = carbonui.Align.CENTERRIGHT if textAlign == TextAlign.RIGHT else carbonui.Align.CENTERLEFT
        valueLabel.loadingWheel = LoadingWheel(parent=rightLineCont, align=loadingWheelAlign, pos=(8, 0, 16, 16), opacity=0.0)
        return (valueLabel, lineCont)

    def ConstructReagentSection(self):
        self.bayCont = ContainerAutoSize(name='bayCont', parent=self.content, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, minHeight=16, padRight=8, padLeft=8)
        self.bayCont.loadingWheel = LoadingWheel(parent=self.bayCont, align=carbonui.Align.CENTERTOP, pos=(0, 0, 16, 16))
        self.typesCont = ContainerAutoSize(name='typesCont', parent=self.bayCont, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, minHeight=16)
        self.bayCont.display = False

    def TakeReagents(self, *args):
        with self.takeBtn.busy_context:
            self.dataController.ExtractReagentsToShip()

    def UpdateTakeBtn(self, qty):
        self.dataController.selectedQty = qty
        volume = self.dataController.GetSelectedVolume()
        text = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/TakeReagents', volume=volume)
        self.takeBtn.SetLabel(text)
        self.UpdateTakeBtnState()

    def UpdateTakeBtnState(self):
        self.takeBtn.enabled = self._reagentsLoaded and self.dataController.selectedQty > 0 and not self.dataController.linkedShipID

    def LoadWindow(self, itemID):
        if not self.dataController.IsSameItemID(itemID):
            with ExceptionEater('Failed disconnecting signal'):
                self.dataController.on_linked_ship_updated.disconnect(self.OnLinkedShipChanged)
            self.dataController = self.CreateDataController(itemID)
        self.onlineOfflineCont.SetDataController(self.dataController)
        self.nameLabel.text = self.dataController.GetSkyhookName()
        self.ownerValueLabel.text = self.dataController.GetOwnerName()
        self.supplyingValueLabel.text = self.dataController.GetResourceDestName()
        self.threadedLoader.StartLoading(self.LoadProducing_thread)
        self.onlineOfflineCont.LoadCont()
        self.btnGroup.display = False
        self.bayCont.display = False
        if self.dataController.isAuthorisedToTake:
            self.threadedLoader.StartLoading(self.LoadAuthorized_thread)

    def LoadProducing_thread(self):
        animation.fade_in(self.producingValueLabel.loadingWheel)
        animation.fade_in(self.vulnerabilityValueLabel.loadingWheel)
        try:
            self.producingValueLabel.text = ''
            self.product = self.dataController.GetProduct()
            productName, texturePath, hintLabel, textHint = self.dataController.GetProductNameAndRichnessTexture()
            if self.destroyed:
                return
            self.producingValueLabel.text = productName
            self.producingValueLabel.hint = textHint if textHint else ''
            self.producingValueLabel.left = 20 if texturePath else 0
            self.producingRichnessSprite.SetTexturePath(texturePath)
            self.producingRichnessSprite.hint = GetByLabel(hintLabel) if hintLabel else ''
            if is_reagent_skyhook(self.product):
                self.vulnerabilityValueLabel.display = True
                self.vulnerabilityCont.display = True
                self.UpdateVulnerabilityTime()
            self.UpdateWindowSize()
        finally:
            animation.fade_out(self.producingValueLabel.loadingWheel, duration=0.1)
            animation.fade_out(self.vulnerabilityValueLabel.loadingWheel, duration=0.1)

    def LoadAuthorized_thread(self):
        onlineState = self.dataController.GetOnlineState()
        if not onlineState or onlineState == NOT_AVAILABLE:
            return
        reagentTypeID = self.dataController.GetPlanetReagentType()
        if reagentTypeID and reagentTypeID != NOT_AVAILABLE:
            self.btnGroup.display = True
            self.bayCont.display = True
            self.threadedLoader.StartLoading(self.LoadStorage_thread)
            self.UpdateWindowSize()
        else:
            self.bayCont.display = False

    def LoadStorage_thread(self):
        self._reagentsLoaded = False
        if not self.bayCont:
            return
        animation.fade_in(self.bayCont.loadingWheel)
        try:
            self.typesCont.Flush()
            typeID, secureAmount, insecureAmount = self.dataController.GetReagentsInSkyhook()
            secureMaxAmount, insecureMaxAmount = self.dataController.GetStorageQtyAndCapacity()
            if self.destroyed:
                return
            if typeID is NOT_AVAILABLE:
                carbonui.TextBody(name='failureLabel', parent=self.typesCont, text=GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/NoDataAvailable'), align=carbonui.Align.TOTOP, color=TextColor.SECONDARY, textAlign=TextAlign.CENTER)
                return
            storageGrid = GridContainer(name='storageGrid', parent=self.typesCont, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, height=REAGENT_ICON_SIZE, contentSpacing=(16, 1), columns=2)
            StorageCont(parent=storageGrid, labelText=GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/SecureBay', units=secureAmount), typeID=typeID, amount=secureAmount, maxAmount=secureMaxAmount, top=10)
            StorageCont(parent=storageGrid, labelText=GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/SurplusBay', units=insecureAmount), typeID=typeID, amount=insecureAmount, maxAmount=insecureMaxAmount, top=10)
            ReagentTypeCont(parent=self.typesCont, typeID=typeID, amount=secureAmount, onEditChangeFunc=self.UpdateTakeBtn, top=10)
            self._reagentsLoaded = True
            self.UpdateTakeBtnState()
            self.UpdateWindowSize()
        finally:
            animation.fade_out(self.bayCont.loadingWheel, duration=0.1)
            self.progressThread = AutoTimer(500.0, self.UpdateProgress_thread)

    def UpdateProgress_thread(self):
        if self.destroyed:
            if self.progressThread:
                self.progressThread.KillTimer()
            self.progressThread = None
            return
        if is_reagent_skyhook(self.product):
            self.UpdateVulnerabilityTime()
        nextTimestamp, amount, progress, isFull = self.dataController.GetNextReagentHarvestTimeAndAmount()
        if nextTimestamp == NOT_AVAILABLE and amount == NOT_AVAILABLE and progress == NOT_AVAILABLE and isFull is False:
            return
        timeRemaining = nextTimestamp - gametime.GetWallclockTime()
        self.processingTimer.SetValue(progress, timeRemaining)

    def _CalcTimeDeltaFromNowAndClampToOneMinute(self, time):
        now = gametime.GetWallclockTime()
        delta = time - now
        delta = max(MIN, delta)
        return delta

    def UpdateVulnerabilityTime(self):
        vulnerabiltyData = self.dataController.GetTheftVulnerabilityForSkyhook()
        if vulnerabiltyData is None:
            self.vulnerabilityValueLabel.text = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/NoDataAvailable')
            return
        end_blue = datetimeutils.datetime_to_filetime(vulnerabiltyData.end)
        start_blue = datetimeutils.datetime_to_filetime(vulnerabiltyData.start)
        vulnerable = vulnerabiltyData.vulnerable
        if vulnerable:
            delta = self._CalcTimeDeltaFromNowAndClampToOneMinute(end_blue)
            countdown = FormatTimeIntervalShortWritten(delta, 'day', 'minute')
            vulnerabilityText = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/VulnerableToTheft', countdown=countdown)
            color = eveColor.DANGER_RED
        else:
            delta = self._CalcTimeDeltaFromNowAndClampToOneMinute(start_blue)
            countdown = FormatTimeIntervalShortWritten(delta, 'day', 'minute')
            vulnerabilityText = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/SecureFromTheft', countdown=countdown)
            self.vulnerabilityValueLabel.text = vulnerabilityText
            color = TextColor.NORMAL
        self.vulnerabilityValueLabel.text = vulnerabilityText
        self.vulnerabilityValueLabel.SetTextColor(color)

    def UpdateWindowSize(self):
        newHeight = self.sr.headerParent.height + self.content_padding[1] + self.content_padding[3] + 30
        newHeight += self.topSection.height
        if self.bayCont.display:
            newHeight += self.bayCont.height
        if self.btnGroup.display:
            newHeight += self.btnGroup.height
        self.SetMinSize([self.minsize[0], max(self.minsize[1], newHeight)])

    def OnReagentsUpdated(self, planetID, skyhookID):
        if skyhookID != self.dataController.itemID or not self.constructionDone:
            return
        self.LoadWindow(skyhookID)

    def OnLinkedShipChanged(self, linkItemID, linkedShipID):
        self.UpdateTakeBtnState()

    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid' in change or 'structureid' in change:
            self.Close()

    def Close(self, setClosed = False, *args, **kwds):
        with ExceptionEater('Failed disconnecting signal'):
            self.dataController.on_linked_ship_updated.disconnect(self.OnLinkedShipChanged)
            self.dataController = None
        super(SkyhookWnd, self).Close(setClosed=setClosed, *args, **kwds)

    def GetMenuMoreOptions(self):
        menu_data = super(SkyhookWnd, self).GetMenuMoreOptions()
        if session.role & ROLE_PROGRAMMER:
            menu_data.AddEntry('QA Reload', self.DebugReload)
        return menu_data


class ThreadedLoader(object):

    def __init__(self):
        self.threadDict = {}

    def StartLoading(self, func):
        funcName = func.func_name
        existingThread = self.threadDict.pop(funcName, None)
        if existingThread:
            existingThread.kill()
        self.threadDict[funcName] = uthread2.start_tasklet(self._CallFunc_thread, func, funcName)

    def _CallFunc_thread(self, func, funcName):
        try:
            func()
        finally:
            self.threadDict.pop(funcName, None)


REAGENT_ICON_SIZE = 64

class StorageCont(ContainerAutoSize):
    default_align = carbonui.Align.TOTOP
    default_alignMode = carbonui.Align.TOTOP
    default_minHeight = REAGENT_ICON_SIZE

    def ApplyAttributes(self, attributes):
        super(StorageCont, self).ApplyAttributes(attributes)
        typeID = attributes.typeID
        amount = attributes.amount
        maxAmount = attributes.maxAmount
        labelText = attributes.labelText
        self.ConstructUI(typeID, labelText, amount, maxAmount)

    def ConstructUI(self, typeID, labelText, amount, maxAmount):
        self.storageLabel = carbonui.TextBody(name='storageLabel', parent=self, text=labelText, align=carbonui.Align.TOTOP, color=TextColor.SECONDARY)
        self.gauge = Gauge(parent=self, color=eveThemeColor.THEME_FOCUS, align=uiconst.TOTOP, gaugeHeight=20, padLeft=0, padTop=8)
        self.gauge.SetValue(float(amount) / maxAmount if maxAmount != 0 else 1)
        self.gauge.SetValueText(GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/CurrentVolumeAndMax', maxVolume=maxAmount * evetypes.GetVolume(typeID), volume=amount * evetypes.GetVolume(typeID)))


class ProcessingTimer(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(ProcessingTimer, self).ApplyAttributes(attributes)
        self.time_text = ''
        self.dataController = attributes.dataController
        self.ConstructUI()

    def ConstructUI(self):
        self.gaugeCont = ContainerAutoSize(name='gaugeCont', parent=self, pickState=carbonui.PickState.OFF)
        self.gauge = GaugeCircular(parent=self.gaugeCont, colorStart=eveThemeColor.THEME_FOCUS, colorEnd=eveThemeColor.THEME_FOCUS, align=carbonui.Align.CENTER, radius=20, showMarker=False, glowBrightness=0.8)
        self.gauge.display = False
        self.icon = Sprite(parent=self.gaugeCont, texturePath=eveicon.inventory, align=carbonui.Align.CENTER, width=16, height=16, opacity=0.75, state=uiconst.UI_NORMAL)
        self.icon.display = False
        self.loadingWheel = LoadingWheel(parent=self, align=carbonui.Align.CENTER, pos=(0, 4, 16, 16), opacity=0.0)
        animation.fade_in(self.loadingWheel)
        self.storageLabel = carbonui.TextDetail(name='storageLabel', parent=self, text='', color=TextColor.SECONDARY, align=carbonui.Align.CENTER, top=30)

    def SetValue(self, value, time_left):
        self.gauge.SetValue(value, False)
        self.time_text = FormatTimeIntervalShortWritten(time_left, showFrom='hour', showTo='second')
        self.storageLabel.text = self.time_text
        self.gauge.display = True
        self.icon.display = True
        animation.fade_out(self.loadingWheel)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadStandardSpacing()
        securedAmount, unsecuredAmount = self.dataController.GetNextReagentHarvestAmounts()
        securedText = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/SecureBay', units=securedAmount)
        surplusText = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/SurplusBay', units=unsecuredAmount)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/NextOutput', countdown=self.time_text))
        tooltipPanel.AddLabelMedium(text=securedText, align=carbonui.Align.TOPLEFT)
        tooltipPanel.AddLabelMedium(text=surplusText, align=carbonui.Align.TOPLEFT)


class ReagentTypeCont(ContainerAutoSize):
    default_align = carbonui.Align.TOTOP
    default_alignMode = carbonui.Align.TOTOP
    default_minHeight = REAGENT_ICON_SIZE

    def ApplyAttributes(self, attributes):
        super(ReagentTypeCont, self).ApplyAttributes(attributes)
        self.onEditChangeFunc = attributes.onEditChangeFunc
        typeID = attributes.typeID
        amount = attributes.amount
        self.ContructUI()
        self.LoadType(typeID, amount)

    def ContructUI(self):
        spriteCont = Container(name='spriteCont', parent=self, align=carbonui.Align.TOLEFT, width=REAGENT_ICON_SIZE)
        self.reagentSprite = ItemIcon(name='reagentSprite', parent=spriteCont, align=carbonui.Align.CENTERLEFT, pos=(0,
         0,
         REAGENT_ICON_SIZE,
         REAGENT_ICON_SIZE), state=uiconst.UI_NORMAL)
        amountCont = ContainerAutoSize(name='amountCont', parent=self, align=carbonui.Align.TORIGHT, minHeight=REAGENT_ICON_SIZE)
        restCont = ContainerAutoSize(name='restCont', parent=self, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, padLeft=10)
        self.typeNameLabel = carbonui.TextBody(name='valueLabel', parent=restCont, text='', align=carbonui.Align.TOTOP)
        self.secureLabel = carbonui.TextDetail(name='secureLabel', parent=restCont, text=GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/ReagentsAvailable'), align=carbonui.Align.TOTOP, top=10, color=TextColor.SECONDARY)
        self.secureValueLabel = carbonui.TextBody(name='secureValueLabel', parent=restCont, text='', align=carbonui.Align.TOTOP)
        self.amountEdit = SingleLineEditInteger(name='amountEdit', parent=amountCont, align=uiconst.CENTERRIGHT, width=100, OnChange=self.OnEditChanged)

    def OnEditChanged(self, *args):
        self.onEditChangeFunc(self.amountEdit.GetValue())

    def LoadType(self, typeID, amount):
        self.reagentSprite.SetTypeID(typeID)
        self.typeNameLabel.text = evetypes.GetName(typeID)
        self.amountEdit.SetValue(amount)
        self.amountEdit.SetMaxValue(amount)
        averagePrice = GetAveragePrice(typeID)
        if averagePrice is None:
            averagePrice = 0
        self.secureValueLabel.text = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/ProcessedUnits', units=amount, price=FmtISK(averagePrice))
        self.reagentSprite.GetMenu = lambda *args: GetMenuService().GetMenuFromItemIDTypeID(None, typeID)
        self.reagentSprite.OnClick = lambda *args: sm.GetService('info').ShowInfo(typeID=typeID)


class OnlineOfflineCont(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        self.toggleSwitch = None
        self.threadedLoader = ThreadedLoader()
        super(OnlineOfflineCont, self).ApplyAttributes(attributes)
        self._dataController = attributes.dataController
        self.unknowStateLabel = carbonui.TextDetail(name='unknowStateLabel', parent=self, text=GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/UnknownOnlineState'), align=carbonui.Align.TOPLEFT)
        self.unknowStateLabel.display = False
        self.loadingWheel = LoadingWheel(parent=self, align=carbonui.Align.TOPLEFT, pos=(8, 0, 16, 16), opacity=0.0)
        self.onlineBtnGrid = LayoutGrid(parent=self, cellSpacing=3, top=8)

    def LoadCont(self):
        self.threadedLoader.StartLoading(self.LoadOnlineState_thread)

    def LoadOnlineState_thread(self):
        animation.fade_in(self.loadingWheel)
        try:
            self.onlineBtnGrid.Flush()
            self.unknowStateLabel.display = False
            onlineState = self._dataController.GetOnlineState()
            if onlineState == NOT_AVAILABLE:
                self.unknowStateLabel.display = True
            elif self.CanEditSkyhookOnlineState(onlineState):
                self.AddToggleButtons(onlineState)
            else:
                self.ReloadReadOnlyStatus(onlineState)
        finally:
            animation.fade_out(self.loadingWheel, duration=0.1)

    def CanEditSkyhookOnlineState(self, onlineState):
        if not self._dataController.HasConfigRoles():
            return False
        if not onlineState:
            return True
        reagentTypeID = self._dataController.GetPlanetReagentType()
        if reagentTypeID > 0:
            return False
        return True

    def AddToggleButtons(self, onlineState):
        self.toggleSwitch = ToggleSwitch(parent=self.onlineBtnGrid, align=carbonui.Align.TOPLEFT, adjustSize=True, checked=bool(onlineState), onText=GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/On').upper(), offText=GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/Off').upper(), confirmFunc=self.ConfirmOnlineStateChange)
        self.toggleSwitch.GetHint = self.GetToggleSwitchHint
        self.toggleSwitch.on_switch_changed.connect(self.ChangeOnlineState)

    def UpdateToggleSwitch(self):
        onlineState = self._dataController.GetOnlineState()
        self.toggleSwitch.SetValue(onlineState, report=False)

    def SetDataController(self, dataController):
        self._dataController = dataController

    def ReloadReadOnlyStatus(self, onlineState):
        onlineState = self._dataController.GetOnlineState()
        if onlineState == NOT_AVAILABLE:
            self.unknowStateLabel.display = True
        if onlineState:
            text = GetByLabel('UI/Common/Online')
            iconColor = eveColor.SUCCESS_GREEN
            hint = ''
        else:
            text = GetByLabel('UI/Common/Offline')
            iconColor = eveColor.DANGER_RED
            hint = GetByLabel('Tooltips/StructureUI/SkyhookIsOfflineNonOwner')
        STATUS_ICON_SIZE = 14
        onlineStateIcon = Sprite(name='onlineStateIcon', parent=self.onlineBtnGrid, align=carbonui.Align.CENTERLEFT, pos=(0,
         0,
         STATUS_ICON_SIZE,
         STATUS_ICON_SIZE), state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/Contacts/onlineIcon.png', outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.8, hint=hint)
        onlineStateIcon.SetRGBA(*iconColor)
        label = carbonui.TextDetail(parent=self.onlineBtnGrid, text=text, align=carbonui.Align.CENTERLEFT, state=uiconst.UI_NORMAL)
        label.hint = hint

    def ChangeOnlineState(self, toggleSwitch, onlineState):
        with toggleSwitch.busy_context:
            if onlineState:
                self._dataController.SetOnline()
            else:
                self._dataController.SetOffline()
            self.UpdateToggleSwitch()

    def GetToggleSwitchHint(self):
        onlineState = self._dataController.GetOnlineState()
        if onlineState == NOT_AVAILABLE:
            return ''
        if onlineState:
            labelPath = 'Tooltips/StructureUI/SkyhookTurnOffline'
        else:
            labelPath = 'Tooltips/StructureUI/SkyhookTurnOnline'
        return GetByLabel(labelPath)

    def ConfirmOnlineStateChange(self, currentState):
        if not currentState:
            return True
        if isinstance(self._dataController.GetProduct(), numbers.Number):
            if eve.Message('SkyhookOfflineConfirmReagent', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return False
        elif eve.Message('SkyhookOfflineConfirmResources', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return False
        return True

    def Close(self):
        with ExceptionEater('Closing OnlineOfflineCont'):
            if self.toggleSwitch:
                self.toggleSwitch.on_switch_changed.connect(self.ChangeOnlineState)
            self.dataController = None
        super(OnlineOfflineCont, self).Close()
