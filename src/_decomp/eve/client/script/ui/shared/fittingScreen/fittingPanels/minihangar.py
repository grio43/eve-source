#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingPanels\minihangar.py
from collections import defaultdict
import evetypes
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from eve.client.script.environment import invControllers as invCtrl
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetColoredText
from eve.common.lib import appConst as const
from eve.common.script.sys import eveCfg
from shipfitting.fittingWarnings import GetColorForLevel
from signals.signalUtil import ChangeSignalConnect
from inventorycommon.util import IsShipFittingFlag, IsShipFittable
import uthread
import carbonui.const as uiconst
import localization
from carbonui.uicore import uicore

class CargoSlots(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.warningFrame = None
        self.controller = attributes.controller
        self.ChangeSignalConnection(connect=True)
        invController = self.GetInvController()
        getMenuFunc = attributes.getMenuFunc
        if getMenuFunc:
            self.itemUtilMenu = self.AddUtilMenu(getMenuFunc)
            self.itemUtilMenu.OnDropData = self.OnDropData
        else:
            self.itemUtilMenu = None
        self.sr.icon = eveIcon.Icon(parent=self, size=32, state=uiconst.UI_DISABLED, ignoreSize=True, icon=invController.GetIconName())
        self.sr.hilite = Fill(parent=self, name='hilite', align=uiconst.RELATIVE, state=uiconst.UI_HIDDEN, idx=-1, width=32, height=self.height)
        self.sr.icon.opacity = 0.8
        Container(name='push', parent=self, align=uiconst.TOLEFT, width=32)
        self.sr.statusCont = Container(name='statusCont', parent=self, align=uiconst.TOLEFT, width=50)
        self.sr.statustext1 = eveLabel.EveLabelMedium(text='status', parent=self.sr.statusCont, name='cargo_statustext', left=0, top=2, idx=0, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        self.sr.statustext2 = eveLabel.EveLabelMedium(text='status', parent=self.sr.statusCont, name='cargo_statustext', left=0, top=14, idx=0, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        m3TextCont = Container(name='m3Cont', parent=self, align=uiconst.TOLEFT, width=12)
        self.sr.m3Text = eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Fitting/FittingWindow/CubicMeters'), parent=m3TextCont, name='m3', left=4, top=14, idx=0)
        sm.GetService('inv').Register(self)
        self.invReady = 1
        self.Update()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_stats_changed, self.Update), (self.controller.on_new_itemID, self.Update), (self.controller.on_warning_display_changed, self.ChangeWarningDisplay)]
        ChangeSignalConnect(signalAndCallback, connect)

    def ConstructWarningFrame(self):
        if self.warningFrame and not self.warningFrame.destroyed:
            return
        self.warningFrame = Frame(bgParent=self, frameConst=uiconst.FRAME_BORDER1_CORNER9, padding=(-2, -2, -4, 0))

    def AddUtilMenu(self, expandMenuFunc):
        invController = self.GetInvController()
        if invController:
            iconName = invController.GetIconName()
        else:
            iconName = ''
        utilMenu = UtilMenu(menuAlign=uiconst.TOPLEFT, parent=self, align=uiconst.TOPLEFT, GetUtilMenu=expandMenuFunc, texturePath=iconName, idx=0, iconSize=32, pos=(0, 0, 32, 32))
        return utilMenu

    def IsItemHere(self, item):
        return True

    def AddItem(self, item):
        self.Update()

    def UpdateItem(self, item, *etc):
        self.Update()

    def RemoveItem(self, item):
        self.Update()

    def OnClick(self, *args):
        if self.controller.IsSimulated():
            if self.itemUtilMenu:
                self.itemUtilMenu.OnClick()
        else:
            self.OnHoldClicked()
        PlaySound(uiconst.SOUND_BUTTON_CLICK)

    def OnHoldClicked(self):
        pass

    def OnMouseEnter(self, *args):
        self.DoMouseEntering()
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnMouseEnterDrone(self, *args):
        if eve.session.stationid:
            self.DoMouseEntering()

    def DoMouseEntering(self):
        self.Hilite(1)
        self.sr.statustext1.OnMouseEnter()
        self.sr.statustext2.OnMouseEnter()
        self.sr.m3Text.OnMouseEnter()

    def OnMouseExit(self, *args):
        self.Hilite(0)
        self.sr.statustext1.OnMouseExit()
        self.sr.statustext2.OnMouseExit()
        self.sr.m3Text.OnMouseExit()
        uthread.new(self.Update)

    def Hilite(self, state):
        self.sr.icon.opacity = [0.8, 1.0][state]

    def SetStatusText(self, text1, text2, color):
        self.sr.statustext1.text = text1
        self.sr.statustext2.text = localization.GetByLabel('UI/Fitting/FittingWindow/CargoUsage', color=color, text=text2)
        self.sr.statusCont.width = max(0, self.sr.statustext1.textwidth, self.sr.statustext2.textwidth)

    def OnDropData(self, dragObj, nodes):
        self.Hilite(0)

    def Update(self, *args):
        uthread.new(self._Update)

    def _Update(self):
        if not self.controller.CurrentShipIsLoaded():
            return
        if not self.controller.IsValidItemAndSimulationState():
            return
        try:
            cap = self.GetCapacity()
        except RuntimeError as e:
            sm.GetService('fittingSvc').LogWarn('Failed to get cap for ship: ', e)
            return

        if not cap or not self or self.destroyed:
            return
        try:
            capacityInfo = self.GetCapacityInfo()
        except KeyError:
            self.SetStatusText('-', '-', '')
            return

        cap2 = capacityInfo.value
        used = FmtAmt(cap.used, showFraction=1)
        cap2 = FmtAmt(cap2, showFraction=1)
        coloredText = GetColoredText(isBetter=capacityInfo.isBetterThanBefore, text=cap2)
        self.SetStatusText(used, coloredText, '')
        self.SetMenuState()

    def GetCapacity(self, flag = None):
        if self.controller.IsSimulated():
            return self.GetSimulatedCapacity()
        else:
            return self.GetInvController().GetCapacity()

    def GetSimulatedCapacity(self):
        pass

    def GetCapacityInfo(self):
        pass

    def GetInvController(self):
        pass

    def SetMenuState(self):
        if self.itemUtilMenu is None:
            return
        if self.controller.IsSimulated():
            self.itemUtilMenu.display = True
        else:
            self.itemUtilMenu.display = False

    def ChangeWarningDisplay(self, warningModuleSlotDict, *args):
        pass

    def Close(self):
        with EatSignalChangingErrors(errorMsg='Container'):
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)


class CargoDroneSlots(CargoSlots):

    def ChangeSignalConnection(self, connect = True):
        CargoSlots.ChangeSignalConnection(self, connect=connect)
        signalAndCallback = [(self.controller.on_drone_bay_open, self.OnClick)]
        ChangeSignalConnect(signalAndCallback, connect)

    def GetInvController(self):
        if self.controller.IsSimulated():
            itemID = None
        else:
            itemID = self.controller.GetItemID()
        return invCtrl.ShipDroneBay(itemID)

    def OnDropData(self, dragObj, nodes):
        if self.controller.IsSimulated():
            self.AddSimulatedDrones(nodes)
        else:
            shipID = eveCfg.GetActiveShip()
            invCtrl.ShipDroneBay(shipID).OnDropData(nodes)
        CargoSlots.OnDropData(self, dragObj, nodes)

    def OnHoldClicked(self, *args):
        uicore.cmd.OpenDroneBayOfActiveShip()

    def GetCapacityInfo(self, flag = None):
        return self.controller.GetDroneCapacity()

    def GetSimulatedCapacity(self):
        shipID = self.controller.GetItemID()
        return self.controller.dogmaLocation.GetCapacity(shipID, None, const.flagDroneBay)

    def AddSimulatedDrones(self, nodes):
        qtyByTypeIDs = GetQtyByTypeAndItemIDs(nodes)
        for typeID, itemID in qtyByTypeIDs.keys():
            if evetypes.GetCategoryID(typeID) != const.categoryDrone:
                qtyByTypeIDs.pop(typeID, None)

        sm.GetService('ghostFittingSvc').TryFitDronesToDroneBay(qtyByTypeIDs)


class CargoCargoSlots(CargoSlots):

    def GetInvController(self):
        if self.controller.IsSimulated():
            itemID = None
        else:
            itemID = self.controller.GetItemID()
        return invCtrl.ShipCargo(itemID)

    def OnDropData(self, dragObj, nodes):
        if self.controller.IsSimulated():
            return self.AddSimulatedCargo(nodes)
        self.Hilite(0)
        if len(nodes) == 1:
            item = nodes[0].item
            if item and IsShipFittingFlag(item.flagID):
                dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                shipID = eveCfg.GetActiveShip()
                if IsShipFittable(item.categoryID):
                    return dogmaLocation.UnloadModuleToContainer(shipID, item.itemID, (shipID,), flag=const.flagCargo)
                if item.categoryID == const.categoryCharge:
                    return dogmaLocation.UnloadAmmoToContainer(shipID, item, (shipID, session.charid, const.flagCargo))
        invCtrl.ShipCargo(eveCfg.GetActiveShip()).OnDropData(nodes)
        CargoSlots.OnDropData(self, dragObj, nodes)

    def AddSimulatedCargo(self, nodes):
        qtyByTypeIDs = GetQtyByTypeIDs(nodes)
        sm.GetService('ghostFittingSvc').TryFitItemsToCargo(qtyByTypeIDs)

    def OnHoldClicked(self, *args):
        uicore.cmd.OpenCargoHoldOfActiveShip()

    def GetCapacityInfo(self, flag = None):
        return self.controller.GetCargoCapacity()

    def GetSimulatedCapacity(self):
        shipID = self.controller.GetItemID()
        return self.controller.dogmaLocation.GetCapacity(shipID, None, const.flagCargo)

    def ChangeWarningDisplay(self, warningModuleSlotDict, *args):
        invCtrl = self.GetInvController()
        warningLevel = warningModuleSlotDict.get(invCtrl.locationFlag, None)
        if warningLevel:
            color = GetColorForLevel(warningLevel)
            self.ConstructWarningFrame()
            self.warningFrame.display = True
            self.warningFrame.SetRGBA(*color)
        elif self.warningFrame:
            self.warningFrame.display = False


class CargoFighterSlots(CargoSlots):

    def ChangeSignalConnection(self, connect = True):
        CargoSlots.ChangeSignalConnection(self, connect=connect)
        signalAndCallback = [(self.controller.on_drone_bay_open, self.OnClick)]
        ChangeSignalConnect(signalAndCallback, connect)

    def GetInvController(self):
        if self.controller.IsSimulated():
            itemID = None
        else:
            itemID = self.controller.GetItemID()
        return invCtrl.ShipFighterBay(itemID)

    def OnDropData(self, dragObj, nodes):
        if self.controller.IsSimulated():
            self.AddSimulatedFighters(nodes)
        else:
            self.GetInvController().OnDropData(nodes)
            CargoSlots.OnDropData(self, dragObj, nodes)

    def OnHoldClicked(self, *args):
        uicore.cmd.OpenFighterBayOfActiveShip()

    def GetCapacityInfo(self, flag = None):
        return self.controller.GetFighterCapacity()

    def GetSimulatedCapacity(self):
        shipID = self.controller.GetItemID()
        return self.controller.dogmaLocation.GetCapacity(shipID, None, const.flagFighterBay)

    def AddSimulatedFighters(self, nodes):
        qtyByTypeIDs = GetQtyByTypeIDs(nodes)
        for typeID in qtyByTypeIDs.keys():
            if evetypes.GetCategoryID(typeID) != const.categoryFighter:
                qtyByTypeIDs.pop(typeID, None)

        if qtyByTypeIDs:
            sm.GetService('ghostFittingSvc').TryFitFightersToTubeOrBay(qtyByTypeIDs)

    def ChangeWarningDisplay(self, warningModuleSlotDict, *args):
        invCtrl = self.GetInvController()
        warningLevel = None
        for eachFlag in [invCtrl.locationFlag] + const.fighterTubeFlags:
            warningLevel = max(warningLevel, warningModuleSlotDict.get(eachFlag, None))

        if warningLevel:
            color = GetColorForLevel(warningLevel)
            self.ConstructWarningFrame()
            self.warningFrame.display = True
            self.warningFrame.SetRGBA(*color)
        elif self.warningFrame:
            self.warningFrame.display = False


class CargoStructureAmmoBay(CargoSlots):

    def GetInvController(self):
        return invCtrl.StructureAmmoBay(self.controller.GetItemID())

    def OnDropData(self, dragObj, nodes):
        if self.controller.IsSimulated():
            return self.AddSimulatedCargo(nodes)
        self.GetInvController().OnDropData(nodes)
        CargoSlots.OnDropData(self, dragObj, nodes)

    def OnHoldClicked(self, *args):
        itemID = self.controller.GetItemID()
        invID = ('StructureAmmoBay', itemID)
        from eve.client.script.ui.shared.inventory.invWindow import Inventory
        Inventory.OpenOrShow(invID, usePrimary=False, toggle=True)

    def GetCapacityInfo(self, flag = None):
        return self.controller.GetCargoCapacity()

    def GetSimulatedCapacity(self):
        shipID = self.controller.GetItemID()
        return self.controller.dogmaLocation.GetCapacity(shipID, None, const.flagCargo)

    def AddSimulatedCargo(self, nodes):
        qtyByTypeIDs = GetQtyByTypeIDs(nodes)
        sm.GetService('ghostFittingSvc').TryFitItemsToCargo(qtyByTypeIDs)


def GetQtyByTypeIDs(nodes):
    qtyByTypeIDs = defaultdict(int)
    for eachNode in nodes:
        typeID = getattr(eachNode, 'typeID', None)
        if typeID is None and getattr(eachNode, 'rec', None):
            typeID = eachNode.rec.typeID
        if typeID:
            qtyByTypeIDs[typeID] += 1

    return qtyByTypeIDs


def GetQtyByTypeAndItemIDs(nodes):
    qtyByTypeIDs = defaultdict(int)
    for eachNode in nodes:
        typeID = getattr(eachNode, 'typeID', None)
        itemID = getattr(eachNode, 'itemID', None)
        if typeID is None and getattr(eachNode, 'rec', None):
            typeID = eachNode.rec.typeID
        if typeID:
            qtyByTypeIDs[typeID, itemID] += 1

    return qtyByTypeIDs
