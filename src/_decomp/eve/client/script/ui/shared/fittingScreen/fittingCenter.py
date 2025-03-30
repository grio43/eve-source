#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingCenter.py
import blue
import math
import uthread
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui.control.scenecontainer import SceneContainerBaseNavigation, STENCIL_MAP_DEFAULT
from eve.client.script.ui.inflight.shipHud.groupAllIcon import GroupAllButton
from eve.client.script.ui.shared.fitting.fittingUtil import GetScaleFactor, EatSignalChangingErrors
from eve.client.script.ui.shared.fitting.shipSceneContainer import ShipSceneContainer
from eve.client.script.ui.shared.fitting.slotAdder import SlotAdder
from eve.client.script.ui.shared.fittingScreen.feedbackLabelCont import FeedbackLabelCont
from eve.client.script.ui.shared.fittingScreen.fittingLayout import FittingLayout
from eve.client.script.ui.shared.fittingScreen.fittingRadialMenu import RadialMenuIcon
from eve.client.script.ui.shared.fittingScreen.slot import FittingSlot
from eve.client.script.ui.station.fitting.stanceSlot import StanceSlots
from eve.common.script.sys.eveCfg import IsControllingStructure
from eveservices.menu import GetMenuService
from eveui.decorators import lock_and_set_pending
from inventorycommon import const as invconst
from localization import GetByLabel
from menu import MenuLabel, MenuList
from signals.signalUtil import ChangeSignalConnect

class FittingCenter(FittingLayout):
    default_align = uiconst.CENTER
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        FittingLayout.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.ChangeSignalConnection(connect=True)
        self.slots = {}
        self.slotList = []
        self.menuSlots = {}
        self.AddSlots()
        self.AddFeedbackLabel()
        self.AddSceneContainer()
        uthread.new(self.AnimateSlots)
        self.UpdateGauges()
        self.SetShipStance()
        self.UpdateRadialMenuAndGroupAllDisplay()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_stats_changed, self.UpdateGaugesOnSignal),
         (self.controller.on_gauge_preview_changed, self.UpdatePreviewGauges),
         (self.controller.on_new_itemID, self.OnNewItem),
         (self.controller.on_slots_with_menu_changed, self.OnSlotsWithMenuChanged),
         (self.controller.on_simulation_state_changed, self.OnSimulationStateChanged),
         (self.controller.on_slots_updated, self.CheckGroupAllButton)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnNewItem(self, *args):
        self.UpdateGauges()
        self.SetShipStance()

    def GetSlots(self):
        return self.slots

    def AddToSlotsWithMenu(self, slot):
        self.menuSlots[slot] = 1

    def ClearSlotsWithMenu(self):
        for slot in self.menuSlots.iterkeys():
            slot.HideUtilButtons()

        self.menuSlots = {}

    def AddSceneContainer(self):
        size = 550 * GetScaleFactor()
        self.sceneContainerParent = ShipSceneParent(parent=self, align=uiconst.CENTER, width=size, height=size, controller=self.controller)
        self.sceneContainer = self.sceneContainerParent.sceneContainer
        self.sceneNavigation = self.sceneContainerParent.sceneNavigation

    def AddFeedbackLabel(self):
        FeedbackLabelCont(parent=self, idx=0, align=uiconst.CENTERBOTTOM, top=150)

    def AddSlots(self):
        self.slotCont = Container(parent=self, name='slotCont', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, idx=0)
        self.slotList = []
        slotAdder = SlotAdder(self.controller, FittingSlot)
        for groupIdx, group in self.controller.GetSlotsByGroups().iteritems():
            if groupIdx < 0:
                continue
            arcStart, arcLength = self.controller.SLOTGROUP_LAYOUT_ARCS[groupIdx]
            slotAdder.StartGroup(arcStart, arcLength, len(group))
            for slotIdx, slotController in enumerate(group):
                slot = slotAdder.AddSlot(self.slotCont, slotController.flagID)
                self.slotList.append(slot)
                self.slots[slotController.flagID] = slot

        self.stances = StanceSlots(parent=self.slotCont, shipID=self.controller.GetItemID(), angleToPos=lambda angle: slotAdder.GetPositionNumbers(angle), typeID=self.controller.GetTypeID(), controller=self.controller)
        self.slotList.extend(self.stances.GetStanceContainers())
        self.AddRadialMenuIcons()

    def AddRadialMenuIcons(self):
        rad = int(243 * self.scaleFactor)
        cX = cY = self.baseShapeSize / 2
        size = int(22 * GetScaleFactor())

        def GetLocation(angle, size):
            cos = math.cos(angle * math.pi / 180.0)
            sin = math.sin(angle * math.pi / 180.0)
            left = int(round(rad * cos + cX - size / 2))
            top = int(round(rad * sin + cY - size / 2))
            return (left, top)

        left, top = GetLocation(227, size)
        self.allHiSlotsIcon = RadialMenuIcon(name='hiSlotRadial', parent=self.slotCont, texturePath='res:/ui/Texture/classes/RadialMenu/fitting/high.png', pos=(left,
         top,
         size,
         size), mouseDownFunc=self.TryOpenRadialMenu, flags=invconst.hiSlotFlags, iconSize=size, hint=GetByLabel('UI/Fitting/FittingWindow/RadialMenu/RadialMenuHighSlots'))
        left, top = GetLocation(315, size)
        self.allMedSlotsIcon = RadialMenuIcon(name='medSlotRadial', parent=self.slotCont, texturePath='res:/ui/Texture/classes/RadialMenu/fitting/med.png', pos=(left,
         top,
         size,
         size), mouseDownFunc=self.TryOpenRadialMenu, flags=invconst.medSlotFlags, iconSize=size, hint=GetByLabel('UI/Fitting/FittingWindow/RadialMenu/RadialMenuMedSlots'))
        left, top = GetLocation(45, size)
        texturePath = 'res:/ui/Texture/classes/RadialMenu/fitting/low.png'
        self.allLoSlotsIcon = RadialMenuIcon(name='loSlotRadial', parent=self.slotCont, texturePath=texturePath, pos=(left,
         top,
         size,
         size), mouseDownFunc=self.TryOpenRadialMenu, flags=invconst.loSlotFlags, iconSize=size, hint=GetByLabel('UI/Fitting/FittingWindow/RadialMenu/RadialMenuLowSlots'))
        left, top = GetLocation(227, size)
        self.groupAllButton = GroupAllButton(parent=self, idx=0, pos=(left,
         top,
         size,
         size))

    def CheckGroupAllButton(self):
        if self.groupAllButton is not None and not self.groupAllButton.destroyed:
            self.groupAllButton.CheckGroupAllButton()

    def TryOpenRadialMenu(self, icon, slotList, mouseButton, *args):
        if mouseButton != uiconst.MOUSELEFT:
            return
        uthread.new(self.ExpandRadialMenu, icon, slotList)

    def ExpandRadialMenu(self, anchorObject, slotList, *args):
        from eve.client.script.ui.shared.fittingScreen.fittingRadialMenu import RadialMenuFitting
        radialMenu = RadialMenuFitting(name='radialMenuFitting', parent=uicore.layer.menu, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, anchorObject=anchorObject, slotList=slotList, isStructure=self.controller.ControllerForCategory() == const.categoryStructure)
        uicore.layer.menu.radialMenu = radialMenu
        uicore.uilib.SetMouseCapture(radialMenu)

    def ChangeRadialMenuIconDisplay(self, displayState):
        for element in [self.allHiSlotsIcon, self.allMedSlotsIcon, self.allLoSlotsIcon]:
            element.display = displayState

    def AnimateSlots(self):
        uthread.new(self.EntryAnimation, self.slotList)

    def EntryAnimation(self, toAnimate):
        for obj in toAnimate:
            obj.opacity = 0.0

        for i, obj in enumerate(toAnimate):
            if obj.state == uiconst.UI_DISABLED:
                endOpacity = 0.05
            else:
                endOpacity = 1.0
                sm.GetService('audio').SendUIEvent('msg_fittingSlotHi_play')
            uicore.animations.FadeTo(obj, 0.0, endOpacity, duration=0.3)
            blue.synchro.SleepWallclock(5)

    def UpdatePreviewGauges(self, cpuLoad, powerLoad, calibrationLoad, *args):
        if self.controller is None or not self.controller.CurrentShipIsLoaded():
            return
        cpuOutput = self.controller.GetCPUOutput()
        portion = self.GetPortion(cpuLoad, cpuOutput.value)
        self.cpuGaugePreview.SetValue(portion, animate=False)
        powerOutput = self.controller.GetPowerOutput()
        portion = self.GetPortion(powerLoad, powerOutput.value)
        self.powerGaugePreview.SetValue(portion, animate=False)
        calibrationOutput = self.controller.GetCalibrationOutput()
        if calibrationLoad and calibrationOutput.value > 0:
            portion = calibrationLoad / calibrationOutput.value
        else:
            portion = 0.0
        self.calibrationGaugePreview.SetValue(portion, animate=False)

    def UpdateGaugesOnSignal(self):
        uthread.new(self.UpdateGauges)

    @lock_and_set_pending()
    def UpdateGauges(self):
        if self.controller is None or not self.controller.CurrentShipIsLoaded():
            return
        self.UpdatePowerGauge()
        self.UpdateCPUGauge()
        self.UpdateCalibrationGauge()

    def UpdatePowerGauge(self):
        powerLoad = self.controller.GetPowerLoad()
        powerOutput = self.controller.GetPowerOutput()
        portion = self.GetPortion(powerLoad.value, powerOutput.value)
        self.powerGauge.SetValue(portion)

    def UpdateCPUGauge(self):
        cpuLoad = self.controller.GetCPULoad()
        cpuOutput = self.controller.GetCPUOutput()
        portion = self.GetPortion(cpuLoad.value, cpuOutput.value)
        self.cpuGauge.SetValue(portion)

    def GetPortion(self, loadValue, outputValue):
        portion = 0.0
        if loadValue:
            if outputValue == 0.0:
                portion = 1.0
            else:
                portion = loadValue / outputValue
        return portion

    def UpdateCalibrationGauge(self):
        calibrationLoad = self.controller.GetCalibrationLoad()
        calibrationOutput = self.controller.GetCalibrationOutput()
        if calibrationLoad.value and calibrationOutput.value > 0:
            portion = calibrationLoad.value / calibrationOutput.value
        else:
            portion = 0.0
        self.calibrationGauge.SetValue(portion)
        self.calibrationGauge.SetCalibrationNumbers(calibrationLoad.value, calibrationOutput.value)

    def SetShipStance(self):
        if self.controller.HasStance():
            self.ShowStanceButtons()
        else:
            self.HideStanceButtons()

    def ShowStanceButtons(self):
        self.stances.display = True
        self.stances.ShowStances(self.controller.GetItemID(), self.controller.GetTypeID())

    def HideStanceButtons(self):
        self.stances.display = False

    def GetTooltipPosition(self):
        return (uicore.uilib.x - 5,
         uicore.uilib.y - 5,
         10,
         10)

    def OnSlotsWithMenuChanged(self, oldFlagID, newFlagID):
        slot = self.slots.get(oldFlagID, None)
        if slot is not None:
            slot.HideUtilButtons()

    def OnSimulationStateChanged(self):
        self.UpdateRadialMenuAndGroupAllDisplay()

    def UpdateRadialMenuAndGroupAllDisplay(self):
        isSimulated = self.controller.IsSimulated()
        if isSimulated:
            displayState = True
        else:
            displayState = False
        self.ChangeRadialMenuIconDisplay(displayState=displayState)
        self.groupAllButton.display = not isSimulated

    def Close(self):
        with EatSignalChangingErrors(errorMsg='fitting center'):
            self.ChangeSignalConnection(connect=False)
        FittingLayout.Close(self)


class ShipSceneParent(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.stencilMask = attributes.Get('stencilMask', STENCIL_MAP_DEFAULT)
        self.ChangeSignalConnection(connect=True)
        self.sceneContainer = ShipSceneContainer(align=uiconst.TOALL, parent=self, state=uiconst.UI_DISABLED, controller=self.controller)
        self.SetScene()
        self.sceneContainer.LoadShipModel()
        scaleFactor = GetScaleFactor()
        self.sceneNavigation = SceneContainerBaseNavigation(parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), idx=0, state=uiconst.UI_NORMAL, pickRadius=225 * scaleFactor)
        self.sceneNavigation.Startup(self.sceneContainer)
        self.sceneNavigation.OnDropData = self.OnDropData
        self.sceneNavigation.GetMenu = self.GetShipMenu

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_new_itemID, self.OnNewShipLoaded)]
        ChangeSignalConnect(signalAndCallback, connect)

    def SetScene(self):
        scenePath = self.controller.scenePath
        self.sceneContainer.PrepareSpaceScene(scenePath=scenePath)
        self.sceneContainer.SetStencilMap(self.stencilMask)

    def OnNewShipLoaded(self, *_args):
        self.ReloadShipModel()

    def OnDropData(self, dragObj, nodes):
        if hasattr(self.controller, 'OnDropData'):
            self.controller.OnDropData(dragObj, nodes)

    def ReloadShipModel(self):
        self.SetScene()
        self.sceneContainer.ReloadShipModel(animate=False)

    def GetShipMenu(self, *args):
        itemID = self.controller.itemID
        if itemID is None:
            return MenuList()
        m = MenuList()
        if self.controller.IsSimulated():
            typeID = self.controller.GetTypeID()
            m += GetMenuService().GetMenuFromItemIDTypeID(None, typeID=typeID, includeMarketDetails=True)
            m += [[MenuLabel('UI/Inventory/ItemActions/StripFitting'), self.controller.StripFitting, []]]
            return m.filter(['UI/Fitting/FittingWindow/SimulateShip'])
        if IsControllingStructure():
            m += GetMenuService().CelestialMenu(session.structureid)
        elif session.stationid or session.structureid:
            hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
            hangarItems = [hangarInv.GetItem()] + hangarInv.List(const.flagHangar)
            for each in hangarItems:
                if each and each.itemID == self.controller.itemID:
                    m += GetMenuService().InvItemMenu(each)

        elif session.solarsystemid:
            m += GetMenuService().CelestialMenu(session.shipid)
        return m

    def Close(self):
        with EatSignalChangingErrors(errorMsg='ShipSceneParent'):
            self.ChangeSignalConnection(connect=False)
            Container.Close(self)
