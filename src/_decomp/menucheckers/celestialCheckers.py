#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\menucheckers\celestialCheckers.py
import evetypes
import inventorycommon.const as invConst
from stargate.client.localGates import FindLocalJumpGateForDestinationPath
from eve.common.script.util.inventoryFlagsCommon import ShouldAllowAdd
import eve.common.lib.appConst as appConst
import dogma.const as dogmaConst
from caching import Memoize
from globalConfig.getFunctions import IsContentComplianceControlSystemActive
from spacecomponents.client.components import linkWithShip, towGameObjective, filamentSpoolup
from spacecomponents.common import componentConst
from structures import STATE_UNKNOWN, OFFLINE_STATES, ALL_UPKEEP_STATES, UPKEEP_STATE_LOW_POWER, TYPES_THAT_NEVER_GO_ABANDONED
from evetypes import GetGroupID, GetCategoryID, IsUpwellStargate, GetGroupNameByGroup
from eveuniverse.security import securityClassZeroSec
from menucheckers.baseCheckers import _BaseItemChecker
from menucheckers.decorators import decorated_checker, explain_failure_with, needs_ballpark_item
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsDeprecatedStation, IsNPC, IsStation, IsCharacter, IsSolarSystem, IsTriglavianSystem
from brennivin.itertoolsext import Bundle
from sovereignty.mercenaryden.client.checkers import is_mercenary_den_owned, is_mercenary_den_close_enough_to_see_option_to_configure
from spacecomponents.common.helper import HasItemTrader, HasScoopComponent, IsActiveComponent, HasCargoBayComponent, HasMicroJumpDriverComponent, HasLinkWithShipComponent, HasUnderConstructionComponent, HasTowGameObjectiveComponent
from spacecomponents.common.components.fitting import IsShipWithinFittingRange, HasFittingComponent
from spacecomponents.common.components.bookmark import IsTypeBookmarkable
from eve.client.script.parklife.states import gbEnemySpotted, selectedForNavigation
from moonmining.miningBeacons import GetMiningBeaconPositionForMoon

@Memoize
def _GetTypesWithRestrictedRenaming():
    return evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_RESTRICTED_RENAMING)


@decorated_checker

class CelestialChecker(_BaseItemChecker):

    def __init__(self, item, cfg, sessionInfo = None, serviceManager = None):
        self.cfg = cfg
        if isinstance(item, tuple):
            typeID = item[1]
            item = Bundle(itemID=item[0], typeID=typeID, groupID=GetGroupID(typeID), categoryID=GetCategoryID(typeID))
        super(CelestialChecker, self).__init__(item, sessionInfo, serviceManager)
        if self.IsSpecificItem():
            self.item.ownerID = self._TryDetermineOwnerID()
            self.item.locationID = self._TryDetermineLocationID()
        self.isMultiSelection = False

    def _TryDetermineOwnerID(self):
        if getattr(self.item, 'ownerID', None) is not None:
            return self.item.ownerID
        itemID = self.item.itemID
        if self.item.typeID == appConst.typeSystem or itemID <= appConst.minStation or IsCharacter(itemID):
            return appConst.ownerSystem
        if IsStation(itemID):
            return cfg.stations.Get(itemID).ownerID
        if self.item.categoryID == invConst.categoryStructure:
            try:
                return self.sm.GetService('structureDirectory').GetStructureInfo(self.item.itemID).ownerID
            except AttributeError:
                pass

    def _TryDetermineLocationID(self):
        if getattr(self.item, 'locationID', None) is not None:
            return self.item.locationID
        try:
            locItem = cfg.evelocations.Get(self.item.itemID)
            if locItem and locItem.solarSystemID:
                return locItem.solarSystemID
        except StandardError:
            pass

        if self.getDistanceToActiveShip() is not None:
            return self.session.solarsystemid
        try:
            return self.sm.StartService('map').GetItem(self.item.itemID).locationID
        except StandardError:
            self.item.locationID = None

    @needs_ballpark_item
    def OfferAbandonCargo(self):
        if not self.IsCargoContainer():
            return False
        if not self.GetBallpark().HaveLootRight(self.item.itemID):
            return False
        if self.IsPlanetaryLaunchContainer():
            return False
        return True

    @needs_ballpark_item
    def OfferAbandonWreck(self):
        if not self.IsWreck():
            return False
        if not self.GetBallpark().HaveLootRight(self.item.itemID):
            return False
        if self.GetBallpark().IsAbandoned(self.item.itemID):
            return False
        return True

    @needs_ballpark_item
    def OfferAbortSelfDestructStructure(self):
        if not (self.IsSovereigntyClaimMarker() or self.IsInfrastructureHub()):
            return False
        if not self.IsOwnedByMyCorp():
            return False
        if not self.IsWithinConfigRange():
            return False
        if not self.session.IsCorpDirector():
            return False
        if not self.IsSelfDestructing():
            return False
        return True

    def OfferAbortSelfDestructShip(self):
        if not self.IsMyActiveShip():
            return False
        return self.IsSelfDestructing()

    @needs_ballpark_item
    def OfferAccessCustomOfficePoco(self):
        if self.IsOrbitalSkyhook():
            return False
        return self.IsCustomsOffice()

    @needs_ballpark_item
    def OfferAccessCustomOfficeSkyhook(self):
        if not self.IsOrbitalSkyhook():
            return False
        if not IsActiveComponent(self.GetBallpark().componentRegistry, self.item.typeID, self.item.itemID):
            return False
        return True

    @needs_ballpark_item
    def OfferAccessMoonMaterialBay(self):
        if not self.IsAutoMoonMiner():
            return False
        if self.session.IsPilotDocked():
            return False
        if not IsActiveComponent(self.GetBallpark().componentRegistry, self.item.typeID, self.item.itemID):
            return False
        if not self.IsWithinInventoryAccessRange():
            return False
        return True

    def OfferAccessHangarTransfer(self):
        if self.session.IsPilotDocked():
            return False
        if self.session.isPilotCloaked():
            return False
        if not self.IsStructureOnline():
            return False
        if self.hasPilotWeaponsTimer():
            return False
        if self.IsOwnedByNPC():
            return False
        if self.IsInEmpireSpace() and self.session.isPilotCriminal():
            return False
        dist = self.getDistanceToActiveShip()
        return dist is not None and dist < self.godma.GetTypeAttribute(self.item.typeID, const.attributeCargoDeliverRange, -1)

    def OfferAccessAutoMoonMinerDetails(self):
        if not idCheckers.IsAutoMoonMiner(self.item.typeID):
            return False
        if not self.IsStructureInSpace():
            return False
        if not self.item.itemID or not self.item.ownerID:
            return False
        return True

    @needs_ballpark_item
    def OfferAccessOrbitalSkyhookOffice(self):
        if not self.IsOrbitalSkyhook():
            return False
        if not self.IsWithinConfigRange():
            return False
        return True

    @needs_ballpark_item
    def OfferAccessMercenaryDen(self):
        return is_mercenary_den_owned(self.item.groupID, self.item.ownerID) and is_mercenary_den_close_enough_to_see_option_to_configure(self.item.itemID)

    @needs_ballpark_item
    def OfferAccessPOSActiveCrystal(self):
        if not self.IsLaserSentry():
            return False
        if not self.IsAnchorable():
            return False
        if not self.IsWithinConfigRange():
            return False
        if not self.IsOwnedByMeMyCorpOrAlliance():
            return False
        if self.IsFree():
            return False
        return True

    @needs_ballpark_item
    def OfferAccessPOSAmmo(self):
        if not self.IsAnchorable():
            return False
        if not self.IsWithinConfigRange():
            return False
        if not self.IsOwnedByMeMyCorpOrAlliance():
            return False
        if self.IsFree():
            return False
        if not self.IsSentry():
            return False
        return True

    @needs_ballpark_item
    def OfferAccessPOSCompression(self):
        if not self.IsCompressionArray():
            return False
        if not self.IsWithinTransferRange():
            return False
        return True

    @needs_ballpark_item
    def OfferAccessPOSCrystalStorage(self):
        return self.OfferAccessPOSActiveCrystal()

    @needs_ballpark_item
    def OfferAccessPOSFuelBay(self):
        if not self.IsControlTower():
            return False
        if not self.IsAnchorable():
            return False
        if not self.IsWithinConfigRange():
            return False
        if not self.IsOwnedByMeMyCorpOrAlliance():
            return False
        if self.IsFree():
            return False
        return True

    @needs_ballpark_item
    def OfferAccessPOSRefinery(self):
        if not self.IsReprocessingArray():
            return False
        if not self.IsWithinTransferRange():
            return False
        if self.IsFree():
            return False
        return True

    @needs_ballpark_item
    def OfferAccessPOSStorage(self):
        if not (self.IsAssemblyArray() or self.IsMobileLaboratory() or self.IsCorpHangarArray() or self.IsPersonalHangarArray() or self.IsSilo() or self.IsReactor()):
            return False
        if not self.IsAnchorable():
            return False
        if not self.IsWithinConfigRange():
            return False
        if not self.IsOwnedByMeMyCorpOrAlliance():
            return False
        if self.IsFree():
            return False
        return True

    @needs_ballpark_item
    def OfferAccessPOSStrontiumBay(self):
        return self.OfferAccessPOSFuelBay()

    @needs_ballpark_item
    def OfferAccessPOSVessels(self):
        if not self.IsPOSMaintainanceArray():
            return False
        if not self.IsAnchorable():
            return False
        if self.IsFree():
            return False
        if not self.IsWithinTransferRange():
            return False
        if not self.IsOwnedByMeMyCorpOrAlliance():
            return False
        return True

    @needs_ballpark_item
    def OfferAccessShippingUnit(self):
        if not self.IsMobileShippingUnit():
            return False
        return getattr(self.item, 'timerInfo', None) is None

    @needs_ballpark_item
    def OfferActivateAutopilot(self):
        if self.session.IsPilotInStructure():
            return False
        if not self.IsMyActiveShip():
            return False
        if self.IsNotOnAutoPilot():
            return True
        return False

    @needs_ballpark_item
    def OfferActivateGate(self):
        if not self.IsWarpGate():
            return False
        if self.session.isPilotWarping():
            return False
        return True

    @needs_ballpark_item
    def OfferActivateJumpBridge(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.session.isPilotWarping() and not self.isPilotWarpingToMe():
            return False
        if not self.IsConnectedJumpBridgeStructure():
            return False
        if not self.IsStructureOnline():
            return False
        return True

    @needs_ballpark_item
    def OfferActivateJumpBridgeDisabled(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.IsConnectedJumpBridgeStructure():
            return False
        if not self.IsStructureOnline():
            return False
        return True

    @needs_ballpark_item
    def OfferActivateMicroJumpDrive(self):
        if self.IsDead():
            return False
        if not IsActiveComponent(self.GetBallpark().componentRegistry, self.item.typeID, self.item.itemID):
            return False
        return HasMicroJumpDriverComponent(self.item.typeID)

    @needs_ballpark_item
    def OfferActivatRandomTraceGate(self):
        if not self.IsRandomTraceJumpGate():
            return False
        if not self.IsOwnedByMe():
            return False
        if self.session.isPilotWarping():
            return False
        if not self.IsComponentActive():
            return False
        failureReason = filamentSpoolup.GetErrorForRandomJumpTraceGate()
        if failureReason is not None:
            self.failure_label = failureReason
            return False
        return True

    @needs_ballpark_item
    def OfferLinkWithShip(self, checkLinkState = True):
        if not self.GetBallpark().GetBall(self.item.itemID):
            return False
        if self.session.isPilotWarping():
            return False
        if self.session.isPilotCloaked():
            return False
        if self.IsDead():
            return False
        if not IsActiveComponent(self.GetBallpark().componentRegistry, self.item.typeID, self.item.itemID):
            return False
        if not HasLinkWithShipComponent(self.item.typeID):
            return False
        if checkLinkState and not linkWithShip.IsAccessibleByCharacter(self.GetBallpark(), self.item):
            return False
        return True

    @needs_ballpark_item
    def OfferTowableMenu(self):
        if not HasTowGameObjectiveComponent(self.item.typeID):
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.GetBallpark().GetBall(self.item.itemID):
            return False
        if self.session.isPilotWarping():
            return False
        if self.session.isPilotCloaked():
            return False
        if self.IsDead():
            return False
        shipItem = self.session.getActiveShipGodmaItem()
        warFactionID = self.session.GetWarFactionID()
        failureReason = towGameObjective.GetFailureReason(self.GetBallpark(), self.item, self.session.charid, shipItem, warFactionID)
        if failureReason is not None:
            self.failure_label = failureReason
            return False
        return True

    def OfferAddFirstWaypoint(self):
        if not self.IsStargate():
            return False
        if self.isWaypoint():
            return False
        return bool(self.GetJumpInfo())

    def OfferAddWaypoint(self):
        if not self.CanBeWaypoint():
            return False
        if self.isWaypoint():
            return False
        return True

    @needs_ballpark_item
    def OfferAlignTo(self):
        if self.OfferApproachObject():
            return False
        if not self.IsPilotFlyingInSameSystem():
            return False
        if self.IsActiveShip():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.session.isInWarpRange(self.getDistanceToActiveShip()):
            return False
        if self.session.isPilotWarping():
            return False
        if self.IsStructure():
            return True
        if self.IsFree():
            return False
        return True

    @needs_ballpark_item
    def OfferAnchorOrbital(self):
        if not (self.IsOrbital() or self.IsPlanetaryCustomsOffice()):
            return False
        if self.IsOrbitalSkyhook():
            return False
        if not self.IsAnchorable():
            return False
        if not self.CanAnchorOrbital():
            return False
        if not self.IsOwnedByMyCorp():
            return False
        return True

    @needs_ballpark_item
    def OfferAnchorPOSObject(self):
        if not self.IsAnchorable():
            return False
        if not self.IsOwnedByMeOrCorp():
            return False
        if not self.IsFree():
            return False
        if not self.IsWithinConfigRange():
            return False
        if not self.GetStateManager().TypeHasEffect(self.item.typeID, dogmaConst.effectAnchorDrop):
            return False
        return True

    @needs_ballpark_item
    def OfferAnchorStructure(self):
        if not self.IsPOSStructure():
            return False
        if not self.IsAnchorable():
            return False
        if not self.IsWithinConfigRange():
            return False
        if not self.IsOwnedByMeMyCorpOrAlliance():
            return False
        if not self.CanAnchorStructure():
            return False
        return True

    @needs_ballpark_item
    def OfferApproachObject(self):
        if self.IsPlanetMoonAsteroidBelt():
            return False
        if not self.IsPilotFlyingInSameSystem() and not self.IsPilotingStructureInSystem():
            return False
        if self.IsActiveShip():
            return False
        if self.session.isPilotWarping():
            return False
        if self.session.IsPilotInShipInSpace() or self.IsPilotControllingStructureWithFightersSelected():
            if self.isInApproachRange(self.getDistanceToActiveShip()):
                return True
        return False

    @needs_ballpark_item
    def OfferAssumeStructureControl(self):
        if not self.IsPOSStructure():
            return False
        if not self.IsAnchorable():
            return False
        if not self.IsOwnedByMeMyCorpOrAlliance():
            return False
        if not self.CanAssumeControlOfStructure():
            return False
        if not self.CanOfflineStructure():
            return False
        if self.IsSovereigntyStructure():
            return False
        if self.hasPlanetViewActive():
            return False
        if self.GetStructureController() is not None:
            return False
        return True

    def OfferAvoidLocation(self):
        if not self.OfferShowLocationOnMap():
            return False
        if self.isAvoided():
            return False
        return True

    @needs_ballpark_item
    def OfferBoardShip(self):
        if not self.IsShip():
            return False
        if self.IsActiveShip():
            return False
        if self.IsInteractive():
            return False
        if self.session.isPilotWarping():
            return False
        dist = self.getDistanceToActiveShip()
        if dist is None:
            return False
        if dist > appConst.maxBoardingDistance:
            return False
        if self.session.IsPilotInShipInSpace() or self.session.IsPilotControllingUndockableStructure():
            return True
        return False

    def OfferBoardPreviousShip(self):
        return self.session.IsPilotControllingUndockableStructure()

    @needs_ballpark_item
    def OfferBoardStructure(self):
        if not self.IsStructure():
            return False
        if self.IsDockableStructure():
            return False
        if not self.IsStructureInSpace():
            return False
        if not self.IsStructureOnline():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        dist = self.getDistanceToActiveShip()
        if dist is None:
            return False
        if dist > appConst.maxBoardingDistance:
            return False
        if self.session.IsElevatedPlayer():
            return True
        return self.sm.GetService('structureControl').MayTakeControl(self.item.itemID)

    def OfferBookmarkLocation(self):
        if not self.IsSpecificItem():
            return False
        if self.IsEntity() or self.IsDrone() or self.IsShip() or self.IsFighter():
            return False
        if self.IsLandmark():
            return False
        if IsDeprecatedStation(self.item.typeID):
            return False
        if not IsTypeBookmarkable(self.item.typeID):
            return False
        if self.IsSolarsystem() or self.IsConstellation() or self.IsRegion():
            return True
        if not self.IsInSpace():
            return False
        return True

    def OfferBroadcastAlignTo(self):
        return self.OfferBroadcastWarpTo()

    @needs_ballpark_item
    def OfferBroadcastEnemySpotted(self):
        if not self.session.IsPilotFleetMember():
            return False
        return bool(self.sm.GetService('fleet').CurrentFleetBroadcastOnItem(self.item.itemID, gbEnemySpotted))

    @needs_ballpark_item
    def OfferBroadcastHealTarget(self):
        if not self.IsPilotFlyingInSameSystem():
            return False
        if not self.session.IsPilotFleetMember():
            return False
        return self.isInFleetBroadcastRange(self.getDistanceToActiveShip())

    @needs_ballpark_item
    def OfferBroadcastJumpTo(self):
        if not self.IsPilotFlyingInSameSystem():
            return False
        if not self.session.IsPilotFleetMember():
            return False
        if self.IsStargate() or self.IsJumpGate():
            return True
        return False

    @needs_ballpark_item
    def OfferBroadcastTarget(self):
        if not self.IsPilotFlyingInSameSystem():
            return False
        if self.IsActiveShip():
            return False
        if not self.session.IsPilotFleetMember():
            return False
        return self.isInFleetBroadcastRange(self.getDistanceToActiveShip())

    def OfferBroadcastTravelTo(self):
        if not self.session.IsPilotFleetMember():
            return False
        if not self.CanBeWaypoint():
            return False
        if self.IsStation and not IsDeprecatedStation(self.item.typeID):
            return True
        if self.IsSolarsystem():
            return True
        return False

    @needs_ballpark_item
    def OfferBroadcastWarpTo(self):
        if not self.IsPilotFlyingInSameSystem():
            return False
        if not self.session.IsPilotFleetMember():
            return False
        if self.IsEntity() or self.IsDrone() or self.IsShip() or self.IsFighter():
            return False
        if self.IsAbyssEntranceGate():
            return False
        return True

    @needs_ballpark_item
    def OfferPilotMenu(self):
        if not self.IsShip():
            return False
        return True

    def OfferCompareButton(self):
        if self.isMultiSelection:
            return False
        if not self.IsComparible():
            return False
        if self.IsShip() or self.IsDrone() or self.IsFighter():
            return bool(self.GetAttributeDict())
        return False

    def OfferConfigureFacility(self):
        if not self.IsSpecificItem():
            return False
        if not self.session.IsStationManager():
            return False
        if not (self.IsAssemblyArray() or self.IsMobileLaboratory()):
            return False
        if not self.IsOwnedByMyCorp():
            return False
        if not self.IsFacility():
            return False
        return True

    @needs_ballpark_item
    def OfferConfigureOrbitalPoco(self):
        if not super(CelestialChecker, self).OfferConfigureOrbital():
            return False
        if self.IsOrbitalSkyhook():
            return False
        if not self.IsOrbitalAnchored():
            return False
        if not self.CanConfigureOrbital():
            return False
        return True

    @needs_ballpark_item
    def OfferConfigureOrbitalSkyhook(self):
        if not super(CelestialChecker, self).OfferConfigureOrbital():
            return False
        if not self.IsOrbitalSkyhook():
            return False
        if not IsActiveComponent(self.GetBallpark().componentRegistry, self.item.typeID, self.item.itemID):
            return False
        if not self.CanConfigureOrbital():
            return False
        return True

    @needs_ballpark_item
    def OfferConfigureShipCloneFacility(self):
        if not self.IsShip():
            return False
        if self.session.IsPilotInStructure():
            return False
        if not self.IsActiveShip():
            return False
        if not self.IsCloneCapableShip():
            return False
        return True

    def OfferCustomsOfficeMenu(self):
        if not self.IsPlanet():
            return False
        if not self.GetBallpark():
            return False
        return bool(self.GetPocoOrbitals())

    @needs_ballpark_item
    def OfferDeactivateAutopilot(self):
        if self.session.IsPilotInStructure():
            return False
        if not self.IsMyActiveShip():
            return False
        if not self.IsOnAutoPilot():
            return False
        return True

    def OfferDock(self):
        if not self.IsDockable():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.session.isPilotWarping():
            return False
        dist = self.getDistanceToActiveShip()
        if dist is None:
            return
        if self.IsStructure() and not self.IsStructureOnline():
            return False
        return True

    def OfferDroneMenu(self):
        if not self.IsDrone():
            return False
        if not self.IsSpecificItem():
            return False
        if None in (self.locationID, self.ownerID):
            return False
        return True

    def OfferEditProfileForStructure(self):
        if self.isMultiSelection:
            return False
        if not self.IsSpecificItem():
            return False
        if not self.IsStructure():
            return False
        if not self.session.IsStationManager():
            return False
        if not self.IsStructureInSpace():
            return False
        if self.IsFree():
            return False
        return self.IsStructureOwnedByMyCorp()

    @needs_ballpark_item
    def OfferEjectFromShip(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.IsMyActiveShip():
            return False
        if self.IsCapsule():
            return False
        if self.session.isPilotWarping():
            return False
        return True

    @needs_ballpark_item
    def OfferEnterStarbasePassword(self):
        if not self.IsShip():
            return False
        if self.session.IsPilotInStructure():
            return False
        if not self.IsActiveShip():
            return False
        return True

    @needs_ballpark_item
    def OfferEnterWormhole(self):
        if not self.IsWormhole():
            return False
        if self.session.isPilotWarping():
            return False
        return True

    def OfferExitPlanetaryProduction(self):
        if not self.IsSpecificItem():
            return False
        if not self.IsPlanet():
            return False
        return self.getViewedPlanet() == self.item.itemID

    def OfferFindInContracts(self):
        if not self.IsPublished():
            return False
        return True

    def OfferFindPersonalAssets(self):
        if self.isMultiSelection:
            return False
        if not self.IsPublished():
            return False
        return True

    @needs_ballpark_item
    def OfferFleetTagItem(self):
        if self.IsActiveShip():
            return False
        if self.IsPlanetMoonAsteroidBelt():
            return False
        if not self.session.IsPilotFleetMember():
            return False
        if not self.session.IsPilotFleetCommander():
            return False
        return True

    @needs_ballpark_item
    def OfferItemTraderAccess(self):
        if self.IsDead():
            return False
        if not IsActiveComponent(self.GetBallpark().componentRegistry, self.item.typeID, self.item.itemID):
            return False
        return HasItemTrader(self.item.typeID)

    @needs_ballpark_item
    def OfferJumpFleetThroughToSystem(self):
        if not self.IsPilotFlyingInSameSystem():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.session.isPilotWarping():
            return False
        if not self.isInStargateJumpRange(self.getDistanceToActiveShip()):
            return False
        if not self.session.isPilotInSameFleetAs(self.item.ownerID):
            return False
        if not self.GetActiveFleetBridge():
            return False
        return True

    def OfferJumpThroughStargate(self):
        if self.GetBallpark() is None:
            return False
        if not self.IsSpecificItem():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        solarsystemID = self.GetWaypointSolarsystemID()
        if solarsystemID is None:
            return False
        if solarsystemID in self.sm.GetService('map').GetNeighbors(self.session.solarsystemid):
            return True
        return False

    def OfferJumpThroughStructureJumpGate(self):
        if self.GetBallpark() is None:
            return False
        if not self.IsSpecificItem():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        solarsystemID = self.GetWaypointSolarsystemID()
        if solarsystemID is None:
            return False
        if solarsystemID == self.session.solarsystemid:
            return False
        return self.IsSolarSystemReachableThroughJumpGate(solarsystemID)

    @needs_ballpark_item
    def OfferKeepAtRange(self):
        if self.IsPlanetMoonAsteroidBelt():
            return False
        if not self.IsPilotFlyingInSameSystem() and not self.IsPilotingStructureInSystem():
            return False
        if self.IsActiveShip():
            return False
        if self.session.isPilotWarping():
            return False
        if not self.IsValidForKeepAtRange():
            return False
        if not self.session.IsPilotInShipInSpace() and not self.IsPilotControllingStructureWithFightersSelected():
            return False
        if self.isInApproachRange(self.getDistanceToActiveShip()):
            return True
        return False

    @needs_ballpark_item
    def OfferLockTarget(self):
        if self.IsActiveShip():
            return False
        if self.IsPlanetMoonAsteroidBelt():
            return False
        if self.session.IsPilotDockedInStructure():
            return False
        if self.session.IsPilotDocked() and not self.session.IsPilotControllingStructure():
            return False
        if not self.IsNotTarget():
            return False
        if self.IsBeingTargetLocked():
            return False
        if self.session.IsPilotInCapsule():
            return False
        if not self.IsWithinTargettingRange():
            return False
        return True

    @needs_ballpark_item
    def OfferLookAtObject(self):
        if self.session.isPilotWarping():
            return False
        if not self.canLookAt():
            return False
        if self.isLookingAtMe():
            return False
        if self.IsPlanet():
            return False
        if self.IsMoon():
            return False
        return True

    @needs_ballpark_item
    def OfferManageControlTower(self):
        if not self.IsAnchorable():
            return False
        if self.IsFree():
            return False
        if not self.IsControlTower():
            return False
        if not self.IsOwnedByMeOrCorp():
            return False
        return True

    @needs_ballpark_item
    def OfferMarkWreckNotViewed(self):
        return self.IsWreck() and self.IsViewedWreck()

    @needs_ballpark_item
    def OfferMarkWreckViewed(self):
        return self.IsWreck() and not self.IsViewedWreck()

    def OfferMoonMiningPointMenu(self):
        return self.IsMoon()

    @needs_ballpark_item
    def OfferMoonMenuOptions(self):
        if not self.IsPlanet():
            return False
        return bool(self.GetMoonsForPlanet())

    @needs_ballpark_item
    def OfferOpenCargo(self):
        if self.session.IsPilotControllingStructure():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.session.isPilotWarping():
            return False
        if not self.IsContainer():
            return False
        if HasItemTrader(self.item.typeID):
            return False
        return True

    @needs_ballpark_item
    def OfferOpenCargoBay(self):
        if not IsActiveComponent(self.GetBallpark().componentRegistry, self.item.typeID, self.item.itemID):
            return False
        if not HasCargoBayComponent(self.item.typeID):
            return False
        if HasUnderConstructionComponent(self.item.typeID):
            return False
        from spacecomponents.client.components import cargobay
        return cargobay.IsAccessibleByCharacter(self.item, self.session.charid)

    @needs_ballpark_item
    def OfferOpenCargoHold(self):
        if not self.IsShip():
            return False
        if self.session.IsPilotInStructure():
            return False
        if not self.IsActiveShip():
            return False
        if self.IsCapsule():
            return False
        return True

    @needs_ballpark_item
    def OfferOpenFleetHangar(self):
        if not self.IsFleetHangarShip():
            return False
        if self.IsActiveShip():
            return True
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.IsOwnedByMe():
            return True
        return self.CanUseShipServices(invConst.flagFleetHangar)

    @needs_ballpark_item
    def OfferOpenInfrastructureHubPanel(self):
        return self.IsControlBunker()

    @needs_ballpark_item
    def OfferOpenShipMaintenanceBay(self):
        if not self.IsSMBShip():
            return False
        if self.IsActiveShip():
            return True
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.IsOwnedByMe():
            return True
        return self.CanUseShipServices(invConst.flagShipHangar)

    @needs_ballpark_item
    def OfferOpenSovFuelDepositWindow(self):
        if not self.IsInfrastructureHub():
            return False
        if self.session.IsPilotControllingStructure():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.session.isPilotWarping():
            return False
        if not self.isInTransferRange(self.getDistanceToActiveShip()):
            return False
        hubInfo = sm.GetService('sov').GetInfrastructureHubInfo(self.session.solarsystemid)
        if not hubInfo or not hubInfo.isSovHubMode:
            return False
        return True

    @needs_ballpark_item
    def OfferOpenSovHubConfigWindow(self):
        if not self.IsInfrastructureHub():
            return False
        if not self.IsOwnedByMyCorp():
            return False
        if not self.session.IsStationManager():
            return False
        hubInfo = sm.GetService('sov').GetInfrastructureHubInfo(self.session.solarsystemid)
        if not hubInfo or not hubInfo.isSovHubMode:
            return False
        return True

    @needs_ballpark_item
    def OfferOpenSovSystemCleanup(self):
        if not self.IsInfrastructureHub():
            return False
        if not self.IsOwnedByMyCorp():
            return False
        return bool(sm.GetService('sov').GetStructuresAvailableToCleanUp())

    @needs_ballpark_item
    def OfferOpenUnderConstruction(self):
        if self.session.IsPilotControllingStructure():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.session.isPilotWarping():
            return False
        if not IsActiveComponent(self.GetBallpark().componentRegistry, self.item.typeID, self.item.itemID):
            return False
        if not HasUnderConstructionComponent(self.item.typeID):
            return False
        if not HasCargoBayComponent(self.item.typeID):
            return False
        from spacecomponents.client.components import cargobay
        return cargobay.IsAccessibleByCharacter(self.item, self.session.charid)

    @needs_ballpark_item
    def OfferOpenUpgradeHold(self):
        from eve.common.script.mgt import entityConst
        if not self.IsOrbital():
            return False
        if not self.IsOwnedByMeOrCorp():
            return False
        if not self.IsSpecialMaterialHoldsItem():
            return False
        if not self.IsPilotFlyingInSameSystem():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if getattr(self.item, 'orbitalState', None) != entityConst.STATE_ANCHORED:
            return False
        if not self.isInTransferRange(self.getDistanceToActiveShip()):
            return False
        if self.IsOrbitalConstructionPlatform():
            return True
        if self.session.IsInZeroSec():
            return True
        return False

    @needs_ballpark_item
    def OfferOrbitObject(self):
        if self.IsPlanetMoonAsteroidBelt():
            return False
        if not self.IsPilotFlyingInSameSystem() and not self.IsPilotingStructureInSystem():
            return False
        if self.IsActiveShip():
            return False
        if self.session.isPilotWarping():
            return False
        if not self.session.IsPilotInShipInSpace() and not self.IsPilotControllingStructureWithFightersSelected():
            return False
        if self.isInOrbitRange(self.getDistanceToActiveShip()):
            return True
        return False

    @needs_ballpark_item
    def OfferOrbitalSkyhook(self):
        if not self.IsPlanet():
            return False
        return bool(self.GetSkyhookOrbitals())

    @needs_ballpark_item
    def OfferPutStructureOffline(self):
        if not self.IsPOSStructure():
            return False
        if not self.IsWithinConfigRange():
            return False
        if not self.IsAnchorable():
            return False
        if not self.IsOwnedByMeMyCorpOrAlliance():
            return False
        if not self.CanOfflineStructure():
            return False
        return True

    @needs_ballpark_item
    def OfferPutStructureOnline(self):
        if not self.IsPOSStructure():
            return False
        if not self.IsAnchorable():
            return False
        if not self.IsWithinConfigRange():
            return False
        if self.IsSovereigntyDisruptor():
            return True
        if not self.IsOwnedByMeMyCorpOrAlliance():
            return False
        if not self.CanOnlineStructure():
            return False
        return True

    @needs_ballpark_item
    def OfferReconnectToLostDrones(self):
        if not self.IsShip():
            return False
        if self.session.IsPilotInStructure():
            return False
        if not self.IsActiveShip():
            return False
        if not self.IsDroneCapableShip():
            return False
        if self.session.isPilotWarping():
            return False
        return True

    def OfferReleaseControl(self):
        return self.session.IsPilotControllingStructure()

    @needs_ballpark_item
    def OfferRelinquishPOSControl(self):
        if not self.IsPOSStructure():
            return False
        if not self.IsAnchorable():
            return False
        if not self.IsOwnedByMeMyCorpOrAlliance():
            return False
        if not self.CanAssumeControlOfStructure():
            return False
        if not self.CanOfflineStructure():
            return False
        if self.IsSovereigntyStructure():
            return False
        if self.hasPlanetViewActive():
            return False
        if not self.IsControlledByPilot():
            return False
        return True

    def OfferToggleOverviewVisibility(self):
        if self.session.IsPilotDocked() and not self.session.IsPilotControllingStructure():
            return False
        if self.IsLandmark():
            return False
        if self.IsIgnoredByOverview():
            return False
        if self.IsSolarsystem() or self.IsConstellation() or self.IsRegion():
            return False
        if sm.GetService('overviewPresetSvc').IsReadOnly():
            return False
        return True

    @explain_failure_with('UI/Menusvc/MenuHints/NotLookingAtItem')
    def OfferResetCamera(self):
        if not self.IsSpecificItem():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.isLookingAtMe():
            return True
        if self.GetCameraInterest() == self.item.itemID:
            return True
        return False

    @needs_ballpark_item
    def OfferSafeLogoff(self):
        if not self.IsShip():
            return False
        if self.session.IsPilotInStructure():
            return False
        if not self.IsActiveShip():
            return False
        if self.session.isPilotWarping():
            return False
        if self.IsLoggingOffSafely():
            return False
        return True

    @needs_ballpark_item
    def OfferScoopToCargoHold(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        return self.IsScoopable()

    @needs_ballpark_item
    def OfferScoopToFighterBay(self):
        if not self.IsFighter():
            return False
        if not self.OfferScoopToCargoHold():
            return False
        shipItem = self.session.getActiveShipGodmaItem()
        return shipItem and shipItem.fighterCapacity

    @needs_ballpark_item
    def OfferScoopToFleetHangar(self):
        if not self.OfferScoopToCargoHold():
            return False
        shipItem = self.session.getActiveShipGodmaItem()
        return shipItem and shipItem.hasFleetHangars

    @needs_ballpark_item
    def OfferScoopToInfrastructureHold(self):
        if not self.OfferScoopToCargoHold():
            return False
        if not self.IsAllowedInFlag(invConst.flagColonyResourcesHold):
            return False
        shipItem = self.session.getActiveShipGodmaItem()
        return shipItem and shipItem.specialColonyResourcesHoldCapacity

    @needs_ballpark_item
    def OfferScoopToShipMaintenanceBay(self):
        if not self.IsShip():
            return False
        if self.IsMyActiveShip():
            return False
        if self.IsCapsule():
            return False
        shipItem = self.session.getActiveShipGodmaItem()
        return shipItem and shipItem.hasShipMaintenanceBay

    @needs_ballpark_item
    def OfferSelfDestructShip(self):
        if self.session.IsPilotInStructure():
            return False
        if not self.IsMyActiveShip():
            return False
        if self.session.isPilotWarping():
            return False
        if self.IsSelfDestructing():
            return False
        return True

    @needs_ballpark_item
    def OfferSelfDestructShipOrPod(self):
        if not (self.IsSovereigntyClaimMarker() or self.IsInfrastructureHub()):
            return False
        if not self.IsOwnedByMyCorp():
            return False
        if not self.IsWithinConfigRange():
            return False
        if not self.session.IsCorpDirector():
            return False
        if self.IsSelfDestructing():
            return False
        return True

    def OfferSetAsCameraInterest(self):
        if not self.IsSpecificItem():
            return False
        if self.GetCameraInterest() == self.item.itemID:
            return False
        if not self.IsPilotFlyingInSameSystem():
            return False
        if self.session.IsPilotControllingStructure():
            return True
        if self.session.IsPilotDocked():
            return False
        return True

    def OfferSetDestination(self):
        if not self.CanBeWaypoint():
            return False
        if self.session.solarsystemid2 == self.item.itemID:
            return False
        waypoints = self.getWaypoints()
        if waypoints and self.item.itemID == waypoints[-1]:
            return False
        return True

    def OfferSetHomeStation(self):
        if not self.IsSpecificItem():
            return False
        if IsDeprecatedStation(self.item.typeID):
            return False
        if self.session.IsPilotInShipInSpace():
            return False
        if self.IsStation():
            stationSolarSystemID = self.GetWaypointSolarsystemID()
            return not IsTriglavianSystem(stationSolarSystemID)
        if self.IsDockableStructure() and self.IsStructureInSpace():
            structureSolarSystemID = self.GetWaypointSolarsystemID()
            return not IsTriglavianSystem(structureSolarSystemID)
        return False

    def OfferSetName(self):
        if not self.IsSpecificItem():
            return False
        if self.IsDrone() or self.IsFighter() or self.IsBiomass():
            return False
        if self.IsCynoField():
            return False
        if self.IsOrbital():
            return False
        if self.IsMercenaryDen():
            return False
        if self.IsMobileWarpDisruptor():
            return False
        if self.IsRenamingRestrictedForType():
            return False
        if self.IsOwnedByMe():
            return True
        if not self.IsOwnedByMyCorp():
            return False
        if self.IsSovereigntyStructure():
            return False
        if self.IsStructure():
            if self.IsFree():
                return False
            if not self.IsStructureInSpace():
                return False
            if self.session.IsStationManager():
                return True
        if self.session.IsCorpDirector():
            return True
        if not self.session.IsEquipmentConfigurator():
            return False
        if not self.IsInPilotLocation():
            return False
        if self.IsDeployable() or self.IsSecureContainer() or self.IsStarbase():
            return True
        return False

    @needs_ballpark_item
    def OfferSetNewConfigPasswordForContainer(self):
        return super(CelestialChecker, self).OfferSetNewConfigPasswordForContainer()

    @needs_ballpark_item
    def OfferSetNewPasswordForContainer(self):
        return super(CelestialChecker, self).OfferSetNewPasswordForContainer()

    @needs_ballpark_item
    def OfferSetNewPasswordForForceField(self):
        if not self.IsAnchorable():
            return False
        if self.IsFree():
            return False
        if not self.IsControlTower():
            return False
        if not self.IsOwnedByMeOrCorp():
            return False
        if not self.IsWithinConfigRange():
            return False
        return True

    def OfferShowLocationOnMap(self):
        if self.IsKnownSpaceSystem():
            return True
        if self.IsKnownSpaceConstellation():
            return True
        if self.IsKnownSpaceRegion():
            return True
        return False

    def OfferSimulateShip(self):
        if self.isMultiSelection:
            return False
        if not self.IsShip():
            return False
        if self.IsSpecificItem():
            return False
        return True

    @needs_ballpark_item
    def OfferStargateJump(self):
        if not self.IsStargate():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.IsInPilotLocation():
            return False
        if self.isPilotWarpingToMe() or not self.session.isPilotWarping():
            return True
        return False

    @needs_ballpark_item
    def OfferShipcasterJump(self):
        if not self.IsShipcasterLauncher():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.IsInPilotLocation():
            return False
        if self.session.isPilotWarping():
            return False
        try:
            shipcasterLauncherComponent = self.GetBallpark().componentRegistry.GetComponentForItem(self.item.itemID, componentConst.SHIPCASTER_LAUNCHER)
        except KeyError:
            return False

        if not self.IsCorrectFactionForShipCaster(shipcasterLauncherComponent):
            return False
        if self.IsShipcasterCharging(shipcasterLauncherComponent):
            return False
        if not self.IsValidTargetForShipcaster(shipcasterLauncherComponent):
            return False
        return self.CanCharacterJumpWithShipcaster(shipcasterLauncherComponent)

    @needs_ballpark_item
    def OfferStartConversation(self):
        if not self.IsSpaceAgent():
            return False
        if not self.IsWithinAgentCommsRange():
            return False
        return True

    @needs_ballpark_item
    def OfferStopMyShip(self):
        if not self.IsMyActiveShip():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        return True

    def OfferStopAvoidingLocation(self):
        if not self.OfferShowLocationOnMap():
            return False
        if self.OfferAvoidLocation():
            return False
        return True

    @needs_ballpark_item
    def OfferStoreVessel(self):
        if not self.IsSMBShip():
            return False
        if self.IsActiveShip():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        activeShip = self.session.getBall()
        if not activeShip:
            return False
        if GetGroupID(activeShip.typeID) == invConst.groupCapsule:
            return False
        if self.IsOwnedByMe():
            return True
        if not self.CanUseShipServices(invConst.flagShipHangar):
            return False
        return self.getDistanceToActiveShip() < appConst.maxConfigureDistance

    @needs_ballpark_item
    def OfferStoreVesselInSMA(self):
        if not self.IsAnchorable():
            return False
        if not self.IsShipMaintainanceArray():
            return False
        if not self.IsWithinConfigRange():
            return False
        if not self.IsOwnedByMeMyCorpOrAlliance():
            return False
        if self.IsFree():
            return False
        shipItem = self.session.getActiveShipGodmaItem()
        return shipItem and shipItem.groupID != invConst.groupCapsule

    def OfferStructureMenu(self):
        return self.IsStructure()

    def OfferTakeControl(self):
        if not self.IsSpecificItem():
            return False
        if not self.IsStructure():
            return False
        if self.session.IsPilotInShipInSpace():
            return False
        if self.session.IsPilotControllingStructure():
            return False
        if not self.session.IsPilotInStructure():
            return False
        if self.session.structureid == self.item.itemID:
            if self.session.IsElevatedPlayer():
                return True
            return self.sm.GetService('structureControl').MayTakeControl(self.item.itemID)
        return False

    def OfferTransferStructureOwnership(self):
        if not self.IsSpecificItem():
            return False
        if not self.IsStructure():
            return False
        if not self.IsStructureInSpace():
            return False
        if not self.IsStructureOnline():
            return False
        if not self.IsStructureOwnedByMyCorp():
            return False
        if not self.session.IsCorpDirector():
            return False
        return True

    @needs_ballpark_item
    def OfferTransferCorporationOwnershipPoco(self):
        if not self.IsOrbital():
            return False
        if self.IsOrbitalSkyhook():
            return False
        if not self.IsOrbitalAnchored():
            return False
        if not self.CanConfigureOrbital():
            return False
        if not self.IsOwnedByMyCorp():
            return False
        if not self.session.IsCorpDirector():
            return False
        if len(self.GetOrbitalsAtPlanet()) > 1:
            return False
        return True

    @needs_ballpark_item
    def OfferTransferCorporationOwnershipSkyhook(self):
        if not self.IsOrbitalSkyhook():
            return False
        if not self.CanConfigureOrbital():
            return False
        if not self.IsOwnedByMyCorp():
            return False
        if not self.session.IsCorpDirector():
            return False
        if len(self.GetOrbitalsAtPlanet()) > 1:
            return False
        return True

    @needs_ballpark_item
    def OfferTransferSovStructureOwnership(self):
        if not (self.IsSovereigntyClaimMarker() or self.IsInfrastructureHub()):
            return False
        if not self.IsOwnedByMyCorp():
            return False
        if not self.session.IsCorpDirector():
            return False
        if not self.IsWithinConfigRange():
            return False
        return True

    @needs_ballpark_item
    def OfferUnanchorOrbital(self):
        if not (self.IsOrbital() or self.IsPlanetaryCustomsOffice()):
            return False
        if not self.IsAnchorable():
            return False
        if not self.IsOrbitalAnchored():
            return False
        if not self.CanUnanchorOrbital():
            return False
        if not self.IsOwnedByMyCorp():
            return False
        return True

    @needs_ballpark_item
    def OfferUnanchorPOSObject(self):
        if not self.IsAnchorable():
            return False
        if not self.IsWithinConfigRange():
            return False
        if not self.IsOwnedByMeOrCorp():
            return False
        if self.IsFree():
            return False
        if not self.GetStateManager().TypeHasEffect(self.item.typeID, dogmaConst.effectAnchorLift):
            return False
        return True

    @needs_ballpark_item
    def OfferUnanchorStructure(self):
        if not self.IsPOSStructure():
            return False
        if not self.IsAnchorable():
            return False
        if not self.IsWithinConfigRange():
            return False
        if not (self.IsOwnedByMeMyCorpOrAlliance() or self.IsOrphanedStructure()):
            return False
        if not self.CanUnanchorStructure():
            return False
        return True

    def OfferUndock(self):
        if self.session.IsPilotControllingStructure():
            return False
        if not self.session.IsPilotInStructure():
            return False
        if self.item.itemID == self.session.structureid:
            return True
        return False

    @needs_ballpark_item
    def OfferUnlockStructureTarget(self):
        if not self.IsPOSStructure():
            return False
        if self.IsSovereigntyStructure():
            return False
        if not self.IsAnchorable():
            return False
        if not self.IsOwnedByMeMyCorpOrAlliance():
            return False
        if not self.CanAssumeControlOfStructure():
            return False
        if not self.IsControlledByPilot():
            return False
        if self.GetStructureTarget() is None:
            return False
        return True

    @needs_ballpark_item
    def OfferUnlockTarget(self):
        return self.IsTarget() and not self.IsBeingTargetLocked()

    @needs_ballpark_item
    def OfferCancelLockTarget(self):
        return self.IsBeingTargetLocked()

    @needs_ballpark_item
    def OfferUseFittingService(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.session.IsPilotControllingStructure():
            return False
        if not self.IsInPilotLocation():
            return False
        if HasFittingComponent(self.item.typeID):
            if IsShipWithinFittingRange(self.session.getActiveShipGodmaItem(), self.item, self.GetBallpark()):
                return True
        elif self.IsSMBShip():
            if self.session.isPilotInSameCorpAs(self.item.ownerID) or self.session.isPilotInSameFleetAs(self.item.ownerID):
                return True
        elif self.IsPOSMaintainanceArray():
            if self.IsFree():
                return False
            if not self.IsOwnedByMeMyCorpOrAlliance():
                return False
            if not self.IsWithinConfigRange():
                return False
            return True
        return False

    @needs_ballpark_item
    def OfferViewLog(self):
        return super(CelestialChecker, self).OfferViewLog()

    def OfferViewPlanetaryProduction(self):
        if not self.IsSpecificItem():
            return False
        if not self.IsPlanet():
            return False
        return self.getViewedPlanet() != self.item.itemID

    def OfferViewTypesMarketDetails(self):
        if self.GetMarketGroup() is None:
            return False
        return True

    @needs_ballpark_item
    def OfferWarpTo(self):
        return self._CanWarpToItem()

    @needs_ballpark_item
    def OfferWarpToMoonMiningPoint(self):
        if not self.IsMoon():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.IsInPilotLocation():
            return False
        position = self.GetMiningBeaconPosition()
        if not position:
            return False
        if self.session.isPilotWarping():
            return False
        distance = self.getDistanceToActiveShip()
        if not self.session.isInWarpRange(distance):
            return False
        return True

    def IsAllowedInFlag(self, flagID):
        return ShouldAllowAdd(flagID, self.item.categoryID, self.item.groupID, self.item.typeID) is None

    def isAvoided(self):
        return self.item.itemID in self.sm.GetService('clientPathfinderService').GetAvoidanceItems()

    @explain_failure_with('UI/Menusvc/MenuHints/BeingTargeted')
    def IsBeingTargetLocked(self):
        return self.sm.StartService('target').BeingTargeted(self.item.itemID)

    @explain_failure_with('UI/Menusvc/MenuHints/NotActive')
    def IsComponentActive(self):
        return IsActiveComponent(self.GetBallpark().componentRegistry, self.item.typeID, self.item.itemID)

    def IsConnectedJumpBridgeStructure(self):
        if not IsUpwellStargate(self.item.typeID):
            return False
        if not getattr(self.item, 'targetSolarsystemID', None):
            return False
        return True

    def IsControlledByPilot(self):
        return self.GetStructureController() == self.session.charid

    @explain_failure_with('UI/Menusvc/MenuHints/ShipcasterIncorrectFaction')
    def IsCorrectFactionForShipCaster(self, shipcasterLauncherComponent):
        warFactionID = self.session.GetWarFactionID()
        if warFactionID not in shipcasterLauncherComponent.validFactionIDsForUse:
            return False
        if warFactionID == shipcasterLauncherComponent.nextTargetFactionID:
            return True
        return False

    def IsDead(self):
        ball = self.GetBall()
        return ball is None or ball.isMoribund

    def IsDockable(self):
        return self.IsStation() or self.IsDockableStructure()

    def IsFacility(self):
        return self.sm.GetService('facilitySvc').IsFacility(self.item.itemID)

    @explain_failure_with('UI/Menusvc/MenuHints/CantWarpTo')
    def IsFree(self):
        try:
            return self.GetBall().isFree
        except AttributeError:
            return False

    @explain_failure_with('UI/Menusvc/MenuHints/NotInApproachRange')
    def isInApproachRange(self, distance):
        return distance is not None and distance < appConst.maxApproachDistance

    def IsInEmpireSpace(self):
        if self.sm.GetService('map').GetSecurityClass(self.session.solarsystemid2) != securityClassZeroSec:
            return True
        return False

    @staticmethod
    def isInFleetBroadcastRange(distance):
        return distance is not None and distance < appConst.maxFleetBroadcastTargetDistance

    @explain_failure_with('UI/Menusvc/MenuHints/NotInOrbitRange')
    def isInOrbitRange(self, distance):
        return distance is not None and distance < appConst.maxApproachDistance

    def IsInSpace(self):
        return IsSolarSystem(getattr(self.item, 'locationID', 0))

    @explain_failure_with('UI/Menusvc/MenuHints/NotWithingMaxJumpDist')
    def isInStargateJumpRange(self, distance):
        return distance is not None and distance < appConst.maxStargateJumpingDistance

    @explain_failure_with('UI/Menusvc/MenuHints/LocationNotInSystem')
    def IsPilotFlyingInSameSystem(self):
        return self.session.IsPilotInShipInSpace() and self.item.locationID == self.session.solarsystemid

    @explain_failure_with('UI/Menusvc/MenuHints/LocationNotInSystem')
    def IsPilotingStructureInSystem(self):
        return self.session.IsPilotControllingStructure() and not self.session.IsPilotControllingUndockableStructure() and self.item.locationID == self.session.solarsystemid

    @explain_failure_with('UI/Menusvc/MenuHints/ShipAlreadyPiloted')
    def IsInteractive(self):
        ball = self.GetBall()
        return ball and ball.isInteractive

    def isInTransferRange(self, distance):
        return distance is not None and distance < max(getattr(self.GetStateManager().GetType(self.item.typeID), 'maxOperationalDistance', 0), const.maxCargoContainerTransferDistance)

    def IsLoggingOffSafely(self):
        return self.sm.GetService('viewState').SafeLogoffInProgress()

    @explain_failure_with('UI/Menusvc/MenuHints/AlreadyLookingAtItem')
    def isLookingAtMe(self):
        return self.sm.GetService('sceneManager').GetActiveSpaceCamera().GetLookAtItemID() == self.item.itemID

    def IsPilotControllingStructureWithFightersSelected(self):
        if not self.session.IsPilotControllingStructure():
            return False
        shipItem = self.session.getActiveShipGodmaItem()
        if not shipItem:
            return False
        if not bool(self.godma.GetType(shipItem.typeID).fighterCapacity):
            return False
        selectedItemIDs = set(sm.GetService('stateSvc').GetStatesForFlag(selectedForNavigation))
        if not selectedItemIDs:
            return False
        return bool({f for f in self.sm.GetService('fighters').shipFighterState.GetAllFighterIDsInSpace()} & selectedItemIDs)

    @explain_failure_with('UI/Menusvc/MenuHints/AutopilotNotActive')
    def IsOnAutoPilot(self):
        return bool(self.sm.StartService('autoPilot').GetState())

    def IsOrbitalAnchored(self):
        from eve.common.script.mgt import entityConst
        return hasattr(self.item, 'orbitalState') and self.item.orbitalState == entityConst.STATE_ANCHORED

    def IsOrphanedStructure(self):
        return self.sm.GetService('pwn').StructureIsOrphan(self.item.itemID)

    @explain_failure_with('UI/Menusvc/MenuHints/AutopilotActive')
    def IsNotOnAutoPilot(self):
        return not self.IsOnAutoPilot()

    @explain_failure_with('UI/Menusvc/MenuHints/Unavailable')
    def IsOwnedByNPC(self):
        return IsNPC(self.item.ownerID)

    def isPilotWarpingToMe(self):
        if not self.session.isPilotWarping():
            return False
        try:
            return sm.GetService('space').warpDestinationCache[0] == self.item.itemID
        except StandardError:
            return False

    @explain_failure_with('UI/Menusvc/MenuHints/BadGroupForAction', groupName=(GetGroupNameByGroup, 'groupID'))
    def IsPlanetMoonAsteroidBelt(self):
        return self.IsPlanet() or self.IsMoon() or self.IsAsteroidBelt()

    def IsPOSStructure(self):
        return self.IsStarbase() or self.IsSovereigntyStructure()

    def IsScoopable(self):
        if self.IsNonScoopableType():
            return False
        shipItem = self.session.getActiveShipGodmaItem()
        if shipItem is None:
            return False
        if self.IsBiomass() or self.IsDrone():
            return True
        if self.IsStructure() and self.IsFree():
            return True
        if self.IsDead():
            return False
        if HasScoopComponent(self.item.typeID) and IsActiveComponent(self.GetBallpark().componentRegistry, self.item.typeID, self.item.itemID):
            return self.IsOwnedByMe()
        if shipItem.groupID in (invConst.groupFreighter, invConst.groupJumpFreighter):
            if self.IsFreightContainer():
                return True
            if self.IsAnchorable() and self.IsFree() and not (self.IsSecureAuditLogContainer() or self.IsSecureContainer() or self.IsCargoContainer()):
                return True
            return False
        if self.IsAnchorable() and self.IsFree():
            return True
        if self.IsCargoContainer() or self.IsFreightContainer():
            return True
        if self.IsFighter() and self.sm.GetService('fighters').shipFighterState.GetFighterInSpaceByID(self.item.itemID) is None:
            return True
        return False

    def IsSelfDestructing(self):
        return getattr(self.item, 'selfDestructTime', None) is not None

    @explain_failure_with('UI/Menusvc/MenuHints/ShipcasterIsCharging')
    def IsShipcasterCharging(self, shipcasterLauncherComponent):
        return shipcasterLauncherComponent.IsCharging()

    def IsSolarSystemReachableThroughJumpGate(self, solarsystemID):
        jumpGateSlimItem = FindLocalJumpGateForDestinationPath(solarsystemID)
        if jumpGateSlimItem:
            return True
        return False

    @explain_failure_with('UI/Menusvc/MenuHints/IsNotAnAgent')
    def IsSpaceAgent(self):
        return self.item.groupID in (invConst.groupAgentsinSpace, invConst.groupDestructibleAgentsInSpace) and bool(self.godma.GetType(self.item.typeID).agentID)

    def IsSpecialMaterialHoldsItem(self):
        return bool(self.GetStateManager().GetType(self.item.typeID).specialMaterialBayCapacity)

    def IsSpecificItem(self):
        return hasattr(self.item, 'itemID') and isinstance(self.item.itemID, (int, long)) and self.item.itemID > 0

    def IsStation(self):
        return self.item.groupID == invConst.groupStation

    def IsStructureInSpace(self):
        if not self.IsStructure():
            return False
        if not self.IsSpecificItem():
            return False
        structureDirectory = self.sm.GetService('structureDirectory')
        structureInfo = structureDirectory.GetStructureInfo(self.item.itemID)
        if structureInfo is None:
            return False
        if not structureInfo.inSpace:
            return False
        solarsystemID = structureInfo.solarSystemID
        if solarsystemID == self.session.solarsystemid2 and self.session.IsPilotInShipInSpace() or self.session.IsPilotControllingStructure():
            bp = self.GetBallpark()
            if bp:
                return self.item.itemID in bp.balls
        return True

    @explain_failure_with('UI/Menusvc/MenuHints/StructureIsNotOnline')
    def IsStructureOnline(self):
        if not self.IsSpecificItem():
            return False
        if not self.IsStructure():
            return False
        return getattr(self.item, 'state', STATE_UNKNOWN) not in OFFLINE_STATES

    def IsStructureInState(self, stateID):
        if not self.IsSpecificItem():
            return False
        if not self.IsStructure():
            return False
        return getattr(self.item, 'state', STATE_UNKNOWN) == stateID

    def IsStructureUpkeep(self, upkeepState):
        if upkeepState not in ALL_UPKEEP_STATES:
            raise ValueError('upkeepState must be one of ALL_UPKEEP_STATES')
        if not self.IsSpecificItem():
            return False
        if not self.IsStructure():
            return False
        return getattr(self.item, 'upkeepState', None) == upkeepState

    def CanEditAbandonTimer(self):
        return self.IsStructureUpkeep(UPKEEP_STATE_LOW_POWER) and self.item.typeID not in TYPES_THAT_NEVER_GO_ABANDONED

    def IsStructureOwnedByMyCorp(self):
        if not self.IsStructure():
            return False
        if not self.IsSpecificItem():
            return False
        structureInfo = self.sm.GetService('structureDirectory').GetStructureInfo(self.item.itemID)
        if not structureInfo:
            return False
        return structureInfo.ownerID == self.session.corpid

    @explain_failure_with('UI/Menusvc/MenuHints/NotInTargets')
    def IsTarget(self):
        return self.item.itemID in self.sm.StartService('target').GetTargets()

    @explain_failure_with('UI/Menusvc/MenuHints/AlreadyTargeted')
    def IsNotTarget(self):
        return not self.IsTarget()

    def IsRandomTraceJumpGate(self):
        return self.item.typeID in [const.typeTriglavianSpaceTrace, const.typeYoiulTrace, const.typeNeedlejackTrace]

    def IsRenamingRestrictedForType(self):
        if not IsContentComplianceControlSystemActive(self.sm.GetService('machoNet')):
            return False
        return self.item.typeID in _GetTypesWithRestrictedRenaming()

    @explain_failure_with('UI/Menusvc/MenuHints/CannotKeepInRange', groupName=(GetGroupNameByGroup, 'groupID'))
    def IsValidForKeepAtRange(self):
        if self.item.categoryID == const.categoryAsteroid:
            return False
        if self.item.groupID in {invConst.groupHarvestableCloud,
         invConst.groupMiningDrone,
         invConst.groupCargoContainer,
         invConst.groupSecureCargoContainer,
         invConst.groupAuditLogSecureContainer,
         invConst.groupStation,
         invConst.groupStargate,
         invConst.groupFreightContainer,
         invConst.groupWreck}:
            return False
        return True

    @explain_failure_with('UI/Menusvc/MenuHints/NotValidTargetForShipcaster')
    def IsValidTargetForShipcaster(self, shipcasterLauncherComponent):
        if shipcasterLauncherComponent.targetSolarsystemID:
            return True
        return False

    def IsViewedWreck(self):
        if not self.IsWreck():
            return False
        return self.sm.GetService('wreck').IsViewedWreck(self.item.itemID)

    def isWaypoint(self, itemID = None):
        checkID = itemID or self.item.itemID
        return checkID in self.getWaypoints()

    @explain_failure_with('UI/Menusvc/MenuHints/NotAccelerationGate')
    def IsWarpGate(self):
        return self.item.groupID == invConst.groupWarpGate or self.IsAbyssEntranceGate()

    def IsWithinAgentCommsRange(self):
        dist = self.getDistanceToActiveShip()
        if dist is None:
            return False
        return dist < self.godma.GetType(self.item.typeID).agentCommRange

    @explain_failure_with('UI/Menusvc/MenuHints/NotWithinMaxConfigDist')
    def IsWithinConfigRange(self):
        bp = self.GetBallpark()
        if bp is None:
            return False
        try:
            distance = self.GetBall().surfaceDist
        except AttributeError:
            return False

        if distance < appConst.maxConfigureDistance:
            return True
        if bp.IsShipInRangeOfStructureControlTower(self.session.shipid, self.item.itemID):
            return True

    @explain_failure_with('UI/Menusvc/MenuHints/NotInTargetRange')
    def IsWithinTargettingRange(self):
        dist = self.getDistanceToActiveShip()
        if dist is None:
            return False
        shipItem = self.session.getActiveShipGodmaItem()
        return shipItem and dist < shipItem.maxTargetRange

    @explain_failure_with('UI/Menusvc/MenuHints/NotWithinMaxTranferDistance')
    def IsWithinTransferRange(self):
        bp = self.GetBallpark()
        return bp and bp.IsShipInRangeOfStructureControlTower(self.session.shipid, self.item.itemID)

    @explain_failure_with('UI/Menusvc/MenuHints/NotWithinMaxTranferDistance')
    def IsWithinInventoryAccessRange(self):
        dist = self.getDistanceToActiveShip()
        if dist is None:
            return False
        return dist < const.maxCargoContainerTransferDistance

    def IsWormhole(self):
        return self.item.groupID == invConst.groupWormhole

    def IsWreck(self):
        return self.item.groupID == invConst.groupWreck

    @explain_failure_with('UI/Menusvc/MenuHints/ShipcasterCantJump')
    def CanCharacterJumpWithShipcaster(self, shipcasterLauncherComponent):
        return shipcasterLauncherComponent.CanCharacterJump(self.session.GetWarFactionID())

    def CanConfigureOrbital(self):
        return self.GetBall() and not self.IsOrbitalConstructionPlatform()

    @explain_failure_with('UI/Menusvc/MenuHints/OutsideLookingRange')
    def canLookAt(self):
        return self.GetBall() is not None

    def CanOfflineStructure(self):
        return self.GetBall() and self.sm.GetService('pwn').CanOfflineStructure(self.item.itemID)

    def CanOnlineStructure(self):
        if self.IsDeprecatedPosModule():
            return False
        return self.GetBall() and self.sm.GetService('pwn').CanOnlineStructure(self.item.itemID)

    def CanAnchorOrbital(self):
        from eve.common.script.mgt import entityConst
        return hasattr(self.item, 'orbitalState') and self.item.orbitalState in (None, entityConst.STATE_UNANCHORED)

    def CanAnchorStructure(self):
        if self.IsDeprecatedPosModule():
            return False
        return self.GetBall() and self.sm.GetService('pwn').CanAnchorStructure(self.item.itemID)

    def CanAssumeControlOfStructure(self):
        return self.GetBall() and self.sm.GetService('pwn').CanAssumeControlStructure(self.item.itemID)

    def CanBeWaypoint(self):
        if not self.IsSpecificItem():
            return False
        return bool(self.GetWaypointSolarsystemID())

    def CanUnanchorOrbital(self):
        return self.GetBall() and self.IsOrbitalConstructionPlatform()

    def CanUnanchorStructure(self):
        return self.GetBall() and self.sm.GetService('pwn').CanUnanchorStructure(self.item.itemID)

    def CanUseShipServices(self, serviceFlag):
        shipOwner = self.item.ownerID
        inSameCorp = self.session.isPilotInSameCorpAs(shipOwner)
        inSameFleet = self.session.isPilotInSameFleetAs(shipOwner)
        if not (inSameCorp or inSameFleet):
            return False
        config = self.GetShipConfig(self.item.itemID)
        if serviceFlag == invConst.flagFleetHangar and config['FleetHangar_AllowCorpAccess'] and inSameCorp or config['FleetHangar_AllowFleetAccess'] and inSameFleet:
            return True
        if serviceFlag == invConst.flagShipHangar and config['SMB_AllowCorpAccess'] and inSameCorp or config['SMB_AllowFleetAccess'] and inSameFleet:
            return True
        return False

    def _CanWarpToItem(self):
        if self.IsActiveShip():
            return False
        if not self.IsInPilotLocation():
            return False
        if self.session.isPilotWarping():
            return False
        if not self.session.isInWarpRange(self.getDistanceToActiveShip()):
            return False
        if not self.IsPilotFlyingInSameSystem():
            return False
        if self.IsAsteroid():
            return True
        if self.IsStructure():
            return True
        if self.IsOrbital():
            return True
        if self.ShouldNotTreatBookmarkAsSolarSystem():
            return True
        if self.IsShip() and self.session.isPilotInSameFleetAs(self.item.ownerID):
            return True
        if not self.IsFree():
            return True
        return False

    def GetActiveFleetBridge(self):
        return self.sm.GetService('fleet').GetActiveBridgeForShip(self.item.itemID)

    def GetAttributeDict(self):
        return self.sm.GetService('info').GetAttributeDictForType(self.item.typeID)

    def GetBall(self):
        if not self.IsSpecificItem():
            return None
        return self.session.getBall(self.item.itemID)

    def GetCameraInterest(self):
        activeCamera = self.sm.GetService('sceneManager').GetActiveSpaceCamera()
        if activeCamera:
            return activeCamera.GetTrackItemID()

    def GetJumpInfo(self):
        return getattr(self.item, 'jumps', [None])[0]

    @explain_failure_with('UI/Moonmining/MoonHasNoMiningPoint')
    def GetMiningBeaconPosition(self):
        return GetMiningBeaconPositionForMoon(self.item.itemID)

    def GetMoonsForPlanet(self):
        return self.sm.GetService('map').GetPlanetMoonsInPlayerSystem(self.item.itemID)

    def GetOrbitalsAtPlanet(self):
        return list(self.sm.GetService('planetInfo').GetOrbitalsAtPlanet(self.item.itemID))

    def GetPocoOrbitals(self):
        return list(self.sm.GetService('planetInfo').GetPocosForPlanet(self.item.itemID))

    def GetSkyhookOrbitals(self):
        return list(self.sm.GetService('planetInfo').GetSkyhooksAtPlanet(self.item.itemID))

    def GetShipConfig(self, shipID):
        return self.sm.GetService('shipConfig').GetShipConfig(shipID)

    def GetStructureController(self):
        return getattr(self.item, 'controllerID', None)

    def GetStructureTarget(self):
        ball = self.GetBall()
        if ball:
            return self.sm.GetService('pwn').GetCurrentTarget(self.item.itemID)

    def GetWaypointSolarsystemID(self):
        if self.IsSolarsystem():
            return self.item.itemID
        if self.IsStation() and not IsDeprecatedStation(self.item.typeID):
            return self.cfg.stations.Get(self.item.itemID).solarSystemID
        if self.IsStructure():
            try:
                structureInfo = self.cfg.evelocations.Get(self.item.itemID)
                if structureInfo.solarSystemID:
                    return structureInfo.solarSystemID
            except (KeyError, ValueError):
                pass

            structureInfo = self.sm.GetService('structureDirectory').GetStructureInfo(self.item.itemID)
            if structureInfo and structureInfo.inSpace:
                return structureInfo.solarSystemID

    def getWaypoints(self):
        return self.sm.GetService('starmap').GetWaypoints()
