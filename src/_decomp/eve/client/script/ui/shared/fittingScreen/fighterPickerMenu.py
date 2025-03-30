#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fighterPickerMenu.py
from collections import defaultdict
import carbonui.const as uiconst
import evetypes
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.inflight.squadrons.fighterInvCont import SquadronLightContainer, SquadronSupportContainer, SquadronHeavyContainer
from eve.client.script.ui.inflight.squadrons.squadronCont import SquadronContEmpty, SquadronCont
from eve.client.script.ui.inflight.squadrons.squadronsUI import SQUADRON_WIDTH
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from eve.client.script.ui.shared.fittingScreen.itemPickerMenu import ItemPickerBase, BaseHoldItemPickerMenu
from eve.client.script.ui.shared.fittingScreen.skillRequirements import GetMissingSkills_HighestLevelByTypeID
from eve.client.script.ui.shared.fittingScreen.tryFit import FAKE_ITEM_GUID, FAKE_ITEM_LOCATION_GUID
from fighters import GetMaxSquadronSize
from fighters.client import GetFighterTubesForShipAndDogmaLocation, GetLightSupportHeavySlotsForShipAndDogmaLocation, GetSquadronTypes
from shipfitting.fittingDogmaLocationUtil import GetFittingItemDragData
from inventorycommon.util import IsFighterTubeFlag
from shipfitting.fittingWarnings import GetColorForLevel
from signals.signalUtil import ChangeSignalConnect
from carbonui.util.color import Color
from eve.common.script.mgt.fighterConst import COLOR_OPEN
import fighters
import gametime

class ItemFighterPicker(ItemPickerBase):
    __guid__ = 'listentry.ItemFighterPicker'

    def OnDblClick(self, *args):
        data = self.sr.node
        sm.GetService('ghostFittingSvc').FitFighterToEmptyTube(data.typeID)

    def OnDropData(self, dragObj, nodes):
        self.sr.node.onDroppedInListFunc(nodes)


class FighterBayItemPickerMenu(BaseHoldItemPickerMenu):
    entryClass = ItemFighterPicker
    flagID = const.flagFighterBay
    emptyLabelPath = 'UI/Fitting/FittingWindow/NoFightersSimulated'

    def __init__(self, controller, menuParent):
        self.squadrons = []
        self.fightersAllowedCont = Container(name='fightersAllowedCont', parent=menuParent, align=uiconst.TOTOP, height=20, padTop=10)
        self.tubeCont = Container(name='tubeCont', parent=menuParent, align=uiconst.TOTOP, height=116, padLeft=4)
        BaseHoldItemPickerMenu.__init__(self, controller, menuParent)
        self.controller = controller
        self.AddTubeConts()
        self.LoadFighters()
        self.AddFighterAllowed()
        self.initDone = True
        self.UpdateSquadronTypes()
        self.ChangeSignalConnection(connect=True)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_stats_changed, self.UpdateNumbers), (self.controller.on_slots_updated, self.OnSlotsUpdated), (self.controller.on_warning_display_changed, self.HiliteProblematicEntries)]
        ChangeSignalConnect(signalAndCallback, connect)

    def DisconnectController(self):
        with EatSignalChangingErrors(errorMsg='FighterBayItemPickerMenu'):
            self.ChangeSignalConnection(connect=False)
        self.controller = False

    def GetExtraDataForType(self, itemIDs, activeItemsSet, typeID):
        return {'onDroppedInListFunc': self.OnDroppedInList}

    def GetNoItemDropFunc(self):
        return self.GetExtraDataForType(None, None, None)

    def OnDroppedInList(self, nodes):
        self._TryRemoveItemsFromTube(nodes)
        self._TryAddToFighterBay(nodes)
        self.ghostFittingSvc.SendFittingSlotsChangedEvent()
        self.ghostFittingSvc.SendOnStatsUpdatedEvent()
        self.LoadItemScroll()

    def _TryRemoveItemsFromTube(self, nodes):
        for eachNode in nodes:
            itemKey = getattr(eachNode, 'itemID', None)
            if itemKey is None:
                continue
            currentFlag = getattr(eachNode, 'flagID', None)
            if currentFlag in const.fighterTubeFlags:
                self.ghostFittingSvc.UnfitModule(itemKey, scatter=False)

    def _TryAddToFighterBay(self, nodes):
        qtyByTypeIDs = defaultdict(int)
        for eachNode in nodes:
            typeID = getattr(eachNode.rec, 'typeID', None)
            if typeID and evetypes.GetCategoryID(typeID) == const.categoryFighter:
                stacksize = getattr(eachNode.rec, 'stacksize', 1)
                qtyByTypeIDs[typeID] += stacksize

        if qtyByTypeIDs:
            self.ghostFittingSvc.TryFitItemsToFighterBay(qtyByTypeIDs)

    def OnSlotsUpdated(self):
        self.LoadFighters()
        self.LoadItemScroll()

    def UpdateNumbers(self):
        self.UpdateSquadronTypes()

    def AddFighterAllowed(self):
        self.lightSquadrons = SquadronLightContainer(parent=self.fightersAllowedCont, left=2)
        self.supportSquadrons = SquadronSupportContainer(parent=self.fightersAllowedCont, left=12)
        self.heavySquadrons = SquadronHeavyContainer(parent=self.fightersAllowedCont, left=12)
        self.ConstructSquadronTypes()

    def AddTubeConts(self):
        self.tubeCont.Flush()
        shipID = self.fittingDogmaLocation.GetCurrentShipID()
        numOfTubes = GetFighterTubesForShipAndDogmaLocation(shipID, self.fittingDogmaLocation)
        for i, tubeFlagID in enumerate(const.fighterTubeFlags):
            squadron = SingleTube(parent=self.tubeCont, tubeFlagID=tubeFlagID, dogmaLocation=self.fittingDogmaLocation, left=2)
            self.squadrons.append(squadron)
            if i >= numOfTubes:
                squadron.SetAsDisabled()

    def LoadFighters(self):
        for eachSquadron in self.squadrons:
            eachSquadron.LoadFighterInfo()

        self.UpdateSquadronTypes()

    def GetEntryWidth(self, *args):
        return 454

    def ConstructSquadronTypes(self):
        light, support, heavy = GetLightSupportHeavySlotsForShipAndDogmaLocation(self.fittingDogmaLocation, self.fittingDogmaLocation.GetActiveShipID())
        contAndNumSlosts = [(self.heavySquadrons, heavy), (self.supportSquadrons, support), (self.lightSquadrons, light)]
        for cont, numSlots in contAndNumSlosts:
            cont.SetTotalSlots(numSlots)
            cont.display = bool(numSlots)

    def UpdateSquadronTypes(self):
        if getattr(self, 'initDone', False):
            heavy, support, light = GetSquadronTypes(self.fittingDogmaLocation.GetFighterNumByTypeIDsInTubes())
            self.heavySquadrons.SetUsedSlots(heavy)
            self.supportSquadrons.SetUsedSlots(support)
            self.lightSquadrons.SetUsedSlots(light)

    def RemoveAll(self, *args):
        BaseHoldItemPickerMenu.RemoveAll(self, *args)
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        for eachTubeID in const.fighterTubeFlags:
            fightersInfo = self.fittingDogmaLocation.GetFightersInTubeInfo(eachTubeID)
            if fightersInfo:
                ghostFittingSvc.UnfitModule(fightersInfo.itemID, scatter=False)

        ghostFittingSvc.SendFittingSlotsChangedEvent()
        ghostFittingSvc.SendOnStatsUpdatedEvent()
        self.LoadItemScroll()

    def DoShowBtnWhenScollIsEmpty(self):
        heavy, support, light = GetSquadronTypes(self.fittingDogmaLocation.GetFighterNumByTypeIDsInTubes())
        return bool(heavy + support + light)

    def UpdateProblematicFigtersInTubes(self, warningSlotDict):
        allTypeIDsInTubes = {x.fighterTypeID for x in self.squadrons}
        _, typeIDsMissingSkills = GetMissingSkills_HighestLevelByTypeID(allTypeIDsInTubes)
        for eachFighter in self.squadrons:
            func = getattr(eachFighter, 'SetFittingWarningColor', None)
            if not func:
                continue
            warningLevelForFighter = warningSlotDict.get(eachFighter.tubeFlagID)
            color = GetColorForLevel(warningLevelForFighter)
            if eachFighter.fighterTypeID in typeIDsMissingSkills:
                func(color)
            else:
                func(None)

    def HiliteProblematicEntries(self, warningSlotDict):
        self.UpdateProblematicFigtersInTubes(warningSlotDict)
        warningLevel = warningSlotDict.get(self.flagID, None)
        self.UpdateProblematicEntries(warningLevel)


class SingleTube(Container):
    default_width = SQUADRON_WIDTH + 6
    default_height = 116
    default_name = 'singleTube'
    default_align = uiconst.TOLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.tubeFlagID = attributes.tubeFlagID
        self.fittingWarning = None
        self.fighterTypeID = None
        self.fighterID = None
        self.fittingDogmaLocation = attributes.dogmaLocation
        tubeController = SimulatedSquadronController()
        self.squadronCont = SimulatedSquadronCont(parent=self, controller=tubeController, align=uiconst.TOPLEFT, tubeFlagID=self.tubeFlagID, state=uiconst.UI_NORMAL, doDamageUpdates=False)
        self.squadronCont.isDragObject = True
        self.squadronCont.GetDragData = self.GetSquadronDragData
        self.squadronCont.tooltipIdentifier = 'SimulatedFighterTooltip'
        self.squadronCont.GetMenu = self.GetSquadronMenu
        self.squadronContEmpty = SimulatedSquadronContEmpty(parent=self, controller=tubeController, fighterID=self.fighterID, fighterTypeID=self.fighterTypeID, align=uiconst.BOTTOMLEFT, tubeFlagID=self.tubeFlagID)
        self.squadronCont.OnDropData = self.OnDropDataOnTube
        self.squadronContEmpty.OnDropData = self.OnDropDataOnTube
        self.frame = Frame(parent=self, texturePath='res:/UI/Texture/classes/CarrierBay/simulateTube3.png')
        self.frame.SetRGBA(*COLOR_OPEN)
        self.btnCont = Container(name='btnCont', parent=self.squadronCont, align=uiconst.TOBOTTOM_NOPUSH, height=24, idx=0)
        self.addFighterBtn = ButtonIcon(name='removeFighterBtn', parent=self.btnCont, align=uiconst.CENTERTOP, pos=(-10, 0, 16, 16), iconSize=10, texturePath='res:/ui/texture/classes/shipui/minus.png', func=self.RemoveFighter)
        self.removeFighterBtn = ButtonIcon(name='addFighterBtn', parent=self.btnCont, align=uiconst.CENTERTOP, pos=(10, 0, 16, 16), iconSize=10, texturePath='res:/ui/texture/classes/shipui/plus.png', func=self.AddFighter)

    def SetFittingWarningColor(self, color):
        if color is None:
            if self.fittingWarning:
                self.fittingWarning.display = False
        else:
            self.ConstructFittingWarning()
            self.fittingWarning.display = True
            self.fittingWarning.SetRGBA(*color)

    def ConstructFittingWarning(self):
        if self.fittingWarning and not self.fittingWarning.destroyed:
            return
        self.fittingWarning = Sprite(parent=self, name='fittingWarning', state=uiconst.UI_DISABLED, align=uiconst.BOTTOMLEFT, pos=(4, 40, 16, 16), texturePath='res:/UI/Texture/classes/Fitting/slotWarningIcon.png', idx=0)

    def GetSquadronMenu(self, *args):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(self.fighterID, self.fighterTypeID, includeMarketDetails=True)

    def RemoveFighter(self, *args):
        return self.ChangeNumFighters(-1)

    def AddFighter(self, *args):
        return self.ChangeNumFighters(1)

    def ChangeNumFighters(self, change):
        fightersInfo = self.fittingDogmaLocation.GetFightersInTubeInfo(self.tubeFlagID)
        if not fightersInfo:
            return
        squadronSize = fightersInfo.squadronSize
        wanted = max(0, squadronSize + change)
        sm.GetService('ghostFittingSvc').ModifyFighterStackSize(fightersInfo.typeID, wanted, self.tubeFlagID)
        self.UpdateUI()

    def LoadFighterInfo(self):
        fightersInfo = self.fittingDogmaLocation.GetFightersInTubeInfo(self.tubeFlagID)
        if fightersInfo:
            squadronSize = fightersInfo.squadronSize
            self.fighterTypeID = fightersInfo.typeID
            self.fighterID = fightersInfo.itemID
            self.squadronCont.SetNewSquadron(self.fighterID, self.fighterTypeID, squadronSize)
            self.HideEmpty()
        else:
            self.fighterID = None
            self.fighterTypeID = None
            self.ShowEmpty()

    def ShowEmpty(self):
        self.squadronContEmpty.display = True
        self.squadronCont.display = False

    def HideEmpty(self):
        self.squadronContEmpty.display = False
        self.squadronCont.display = True

    def OnDropData(self, dragSource, nodes):
        return self.OnDropDataOnTube(dragSource, nodes)

    def GetSquadronDragData(self):
        return GetFittingItemDragData(self.fighterID, self.fittingDogmaLocation)

    def OnDropDataOnTube(self, dragSource, nodes):
        recs = []
        fakeRecs = []
        for node in nodes:
            if getattr(node, 'rec', None):
                recs.append(node.rec)
            elif node.__guid__ in FAKE_ITEM_GUID:
                fakeRecs.append(node)
            elif node.__guid__ in FAKE_ITEM_LOCATION_GUID and getattr(node, 'typeID', None):
                if evetypes.GetCategoryID(node.typeID) == const.categoryStructure:
                    fakeRecs.append(node)

        for each in fakeRecs + recs:
            typeID = each.typeID
            sm.GetService('ghostFittingSvc').FitFighterToTube(typeID, self.tubeFlagID, qty=GetMaxSquadronSize(typeID))

        self.UpdateUI()

    def SetAsDisabled(self):
        self.squadronContEmpty.actionLabel.text = ''
        self.Disable()
        self.opacity = 0.3

    def UpdateUI(self):
        self.LoadFighterInfo()


class SimulatedSquadronCont(SquadronCont):

    def ApplyAttributes(self, attributes):
        SquadronCont.ApplyAttributes(self, attributes)
        self.removeSquadronBtn = ButtonIcon(name='removeSquadronBtn', parent=self, align=uiconst.TOPRIGHT, pos=(2, 2, 16, 16), iconSize=16, texturePath='res:/UI/Texture/Icons/73_16_210.png', func=self.RemoveSquadron)

    def RemoveSquadron(self, *args):
        if self.fighterItemID:
            sm.GetService('ghostFittingSvc').UnfitModule(self.fighterItemID)


class SimulatedSquadronContEmpty(SquadronContEmpty):

    def ApplyAttributes(self, attributes):
        SquadronContEmpty.ApplyAttributes(self, attributes)
        self.fighterCont.OnDropData = self.parent.OnDropData


class SimulatedSquadronController(object):

    def __init__(self):
        pass

    def GetSquadronVelocity(self, tubeFlagID):
        return None

    def GetSquadronDistance(self, tubeFlagID):
        return None

    def GetSquadronBallInfo(self, tubeFlagID):
        return None

    def GetFightersBall(self, fightersItemID):
        return None

    def GetTimeNow(self):
        return gametime.GetSimTime()

    def GetFightersInSpaceItemID(self, tubeFlagID):
        return None

    def GetIsInSpace(self, tubeFlagID):
        return False

    def GetSquadronAction(self, tubeFlagID):
        stateText = 'UI/Fitting/FittingWindow/FightersSimulated'
        stateColor = Color(*COLOR_OPEN)
        stateColor.a = 0.8
        return (stateText, stateColor)

    def GetAbilities(self, fighterTypeID):
        if fighterTypeID:
            abilities = fighters.IterTypeAbilities(fighterTypeID)
            return abilities

    def GetIncomingEwarEffects(self, fighterID):
        return []
