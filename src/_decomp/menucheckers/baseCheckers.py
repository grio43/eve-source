#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\menucheckers\baseCheckers.py
import weakref
from menucheckers import explain_failure_with
import inventorycommon.const as invConst
from spacecomponents.common.helper import HasShipcasterComponent
from eve.common.script.mgt.helpers.bookmark import should_treat_bookmark_as_solar_system
from eve.common.script.sys import idCheckers
from eve.common.lib.appConst import OVERVIEW_IGNORE_TYPES
from evetypes import GetGroupNameByGroup, GetIsGroupAnchorableByGroup, GetMarketGroupID, IsPublished
from inventoryrestrictions import can_view_market_details
from spacecomponents.common import componentConst
from spacecomponents.common.data import type_has_space_component
from structures import SERVICE_REPROCESSING
from menu import CONTAINERGROUPS

class _ServiceAccessChecker(object):

    def __init__(self, serviceManager):
        self.cache = {}
        self._godma = None
        self.sm = serviceManager
        if self.sm is None:
            self.sm = globals()['__builtins__']['sm']

    @property
    def godma(self):
        if self._godma is None:
            self._godma = self.sm.GetService('godma')
        return self._godma

    def IsPilotCEO(self):
        return self.sm.GetService('corp').UserIsCEO()

    def isStructureServiceAvailableToPilot(self, serviceID):
        return self.sm.GetService('structureServices').IsServiceAvailableForCharacter(serviceID)

    def isPilotInLimitedEngagementWith(self, ownerID):
        return self.sm.GetService('crimewatchSvc').HasLimitedEngagmentWith(ownerID)

    def canCompress(self):
        return self.isStructureServiceAvailableToPilot(SERVICE_REPROCESSING)

    def hasInFlightViewActive(self):
        return self.sm.GetService('viewState').IsViewActive('inflight')

    @explain_failure_with('UI/Menusvc/MenuHints/YouHaveWeaponsTimer')
    def hasPilotWeaponsTimer(self):
        return self.sm.GetService('crimewatchSvc').HaveWeaponsTimer()

    def hasPlanetViewActive(self):
        return self.sm.GetService('viewState').IsViewActive('planet')

    def hasSkillQueueOpen(self):
        return self.sm.GetService('skillqueue').IsQueueWndOpen()

    def GetBlockedRoles(self):
        return self.sm.GetService('corp').UserBlocksRoles()

    def getImplants(self):
        return self.sm.GetService('skills').GetImplants()

    def getBoosters(self):
        return self.sm.GetService('skills').GetBoosters()

    def getSkills(self):
        return self.sm.GetService('skills').GetSkillsIncludingLapsed()

    def GetStateManager(self):
        return self.godma.GetStateManager()

    def getViewedPlanet(self):
        if not self.hasPlanetViewActive():
            return None
        return self.sm.GetService('planetUI').planetID

    def getBallpark(self):
        return self.sm.GetService('michelle').GetBallpark()


class _BaseSessionWrappingChecker(_ServiceAccessChecker):

    def __init__(self, sessionInfo = None, serviceManager = None):
        super(_BaseSessionWrappingChecker, self).__init__(serviceManager)
        from menucheckers import SessionChecker
        if isinstance(sessionInfo, SessionChecker):
            self.session = sessionInfo
        elif sessionInfo is None:
            self.session = SessionChecker(globals()['__builtins__']['session'], self.sm)
        else:
            self.session = SessionChecker(sessionInfo, self.sm)
        self._failure_label = None
        self._label_arguments = None

        def _delChecker(refobject, session = self.session):
            delattr(session, '_checker')

        self.session._checker = weakref.proxy(self, _delChecker)

    @property
    def label_args(self):
        try:
            return {argName:argFunction[0](getattr(self, argFunction[1])) for argName, argFunction in self._label_arguments.iteritems()}
        except AttributeError:
            return {}


class _BaseItemChecker(_BaseSessionWrappingChecker):

    def __init__(self, item, sessionInfo = None, serviceManager = None):
        super(_BaseItemChecker, self).__init__(sessionInfo, serviceManager)
        self.item = item

    @property
    def failure_label(self):
        return self._failure_label

    @failure_label.setter
    def failure_label(self, value):
        self._failure_label = value

    def __getattr__(self, attr):
        return getattr(self.item, attr)

    def __repr__(self):
        return '%s for item %s' % (self.__class__.__name__, self.item)

    def OfferConfigureOrbital(self):
        if not self.IsOrbital():
            return False
        if self.IsOrbitalConstructionPlatform():
            return False
        if not self.session.IsStationManager():
            return False
        if not self.IsOwnedByMyCorp():
            return False
        return True

    def OfferOpenCargoHold(self):
        raise NotImplementedError

    def OfferOpenAmmoHold(self):
        return self.OfferOpenCargoHold() and self.IsAmmoHoldShip()

    def OfferOpenBoosterBay(self):
        return self.OfferOpenCargoHold() and self.IsBoosterBayShip()

    def OfferOpenDroneBay(self):
        return self.OfferOpenCargoHold() and self.IsDroneCapableShip()

    def OfferOpenCommandCenterHold(self):
        return self.OfferOpenCargoHold() and self.IsCommandCenterHoldShip()

    def OfferOpenCorpseBay(self):
        return self.OfferOpenCargoHold() and self.IsCorpseBayShip()

    def OfferOpenFighterBay(self):
        return self.OfferOpenCargoHold() and self.IsFighterCapableShip()

    def OfferOpenFrigateEscapeBay(self):
        return self.OfferOpenCargoHold() and self.IsFrigateEscapeBayCapableShip()

    def OfferOpenFuelBay(self):
        return self.OfferOpenCargoHold() and self.IsFuelBayShip()

    def OfferOpenGasHold(self):
        return self.OfferOpenCargoHold() and self.IsGasHoldShip()

    def OfferOpenIndustrialShipHold(self):
        return self.OfferOpenCargoHold() and self.IsIndustrialHoldShip()

    def OfferOpenLargeShipHold(self):
        return self.OfferOpenCargoHold() and self.IsLargeShipHoldShip()

    def OfferOpenMediumShipHold(self):
        return self.OfferOpenCargoHold() and self.IsMediumShipHoldShip()

    def OfferOpenMineralHold(self):
        return self.OfferOpenCargoHold() and self.IsMineralHoldShip()

    def OfferOpenGeneralMiningHold(self):
        return self.OfferOpenCargoHold() and self.IsGeneralMiningHoldShip()

    def OfferOpenPlanetaryCommoditiesHold(self):
        return self.OfferOpenCargoHold() and self.IsPlanetaryCommoditiesHoldShip()

    def OfferOpenQuafeBay(self):
        return self.OfferOpenCargoHold() and self.IsQuafeBayShip()

    def OfferOpenSalvageHold(self):
        return self.OfferOpenCargoHold() and self.IsSalvageHoldShip()

    def OfferOpenShipHold(self):
        return self.OfferOpenCargoHold() and self.IsShipHoldShip()

    def OfferOpenSmallShipHold(self):
        return self.OfferOpenCargoHold() and self.IsSmallShipHoldShip()

    def OfferOpenSubsystemBay(self):
        return self.OfferOpenCargoHold() and self.IsSubsystemBayShip()

    def OfferOpenMobileDepotHold(self):
        return self.OfferOpenCargoHold() and self.IsMobileDepotHoldShip()

    def OfferOpenColonyResourcesHold(self):
        return self.OfferOpenCargoHold() and self.IsColonyResourcesHoldShip()

    def OfferSetNewConfigPasswordForContainer(self):
        if not self.IsSecureAuditLogContainer():
            return False
        if not self.IsInPilotLocation():
            return False
        return True

    def OfferSetNewPasswordForContainer(self):
        if not self.IsSecureContainer():
            return False
        if not self.IsInPilotLocation():
            return False
        return True

    def OfferViewTypesMarketDetails(self):
        return can_view_market_details(self.item.typeID) and not self.IsStation()

    def OfferViewLog(self):
        if not self.IsSecureAuditLogContainer():
            return False
        if not self.IsInPilotLocation():
            return False
        if not self.IsOwnedByMeOrCorp():
            return False
        return True

    OfferConfigureALSC = OfferRetrievePasswordALSC = OfferViewLog

    def IsAbyssEntranceGate(self):
        return self.item.typeID == invConst.typeAbyssEntranceGate

    @explain_failure_with('UI/Menusvc/MenuHints/IsYourShip')
    def IsActiveShip(self):
        return self.item.itemID == self.session.shipid

    def IsAmmoHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialAmmoHoldCapacity)

    def IsAnchorable(self):
        return GetIsGroupAnchorableByGroup(self.item.groupID)

    def IsAssemblyArray(self):
        return self.item.groupID == invConst.groupAssemblyArray

    def IsAsteroid(self):
        return self.item.categoryID == invConst.categoryAsteroid

    def IsAsteroidBelt(self):
        return self.item.groupID == invConst.groupAsteroidBelt

    def IsBeacon(self):
        return self.item.groupID == invConst.groupBeacon

    def IsBiomass(self):
        return self.item.groupID == invConst.groupBiomass

    def IsBoosterBayShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialBoosterHoldCapacity)

    @explain_failure_with('UI/Menusvc/MenuHints/YouAreInCapsule')
    def IsCapsule(self):
        return idCheckers.IsCapsule(self.item.groupID)

    def IsCargoContainer(self):
        return self.item.groupID == invConst.groupCargoContainer

    def IsCloneCapableShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).canReceiveCloneJumps)

    def IsCommandCenterHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialCommandCenterHoldCapacity)

    def IsComparible(self):
        return self.item.categoryID in invConst.compareCategories

    def IsCompressionArray(self):
        return self.item.typeID == invConst.typeCompressionArray

    def IsConstellation(self):
        return self.item.groupID == invConst.groupConstellation

    def IsContainer(self):
        return self.item.groupID in CONTAINERGROUPS

    def IsControlBunker(self):
        return self.item.groupID == invConst.groupControlBunker

    def IsControlTower(self):
        return self.item.groupID == invConst.groupControlTower

    def IsCorpHangarArray(self):
        return self.item.groupID == invConst.groupCorporateHangarArray

    def IsCorpseBayShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialCorpseHoldCapacity)

    def IsCustomsOffice(self):
        return self.item.groupID == invConst.groupPlanetaryCustomsOffices

    def IsCynoField(self):
        return self.item.groupID == invConst.groupCynosuralField

    def IsDeployable(self):
        return self.item.categoryID == invConst.categoryDeployable

    def IsDeprecatedPosModule(self):
        return self.item.groupID in invConst.DEPRECATED_POS_MODULE_GROUPS

    def IsDockableStructure(self):
        return idCheckers.IsDockableStructure(self.item.typeID)

    @explain_failure_with('UI/Menusvc/MenuHints/BadGroupForAction', groupName=(GetGroupNameByGroup, 'groupID'))
    def IsDrone(self):
        return self.item.categoryID == invConst.categoryDrone

    def IsDroneCapableShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).droneCapacity) or self.IsModularShip()

    def IsEntity(self):
        return self.item.categoryID == invConst.categoryEntity

    def IsFighter(self):
        return self.item.categoryID == invConst.categoryFighter

    def IsFighterCapableShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).fighterCapacity)

    def IsFrigateEscapeBayCapableShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).frigateEscapeBayCapacity)

    def IsFleetHangarShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).hasFleetHangars)

    def IsFreightContainer(self):
        return self.item.groupID == invConst.groupFreightContainer

    def IsFuelBayShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialFuelBayCapacity)

    def IsGasHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialGasHoldCapacity)

    def IsIgnoredByOverview(self):
        return self.item.typeID in OVERVIEW_IGNORE_TYPES

    def IsIndustrialHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialIndustrialShipHoldCapacity)

    def IsInfrastructureHub(self):
        return self.item.groupID == invConst.groupInfrastructureHub

    def IsJumpGate(self):
        return self.item.groupID == invConst.groupUpwellJumpGate

    def IsKnownSpaceConstellation(self):
        return idCheckers.IsKnownSpaceConstellation(self.item.itemID)

    def IsKnownSpaceRegion(self):
        return idCheckers.IsKnownSpaceConstellation(self.item.itemID)

    def IsKnownSpaceSystem(self):
        return idCheckers.IsKnownSpaceSystem(self.item.itemID)

    def IsLandmark(self):
        return self.item.itemID and self.item.itemID < 0

    def IsLargeShipHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialLargeShipHoldCapacity)

    def IsLaserSentry(self):
        return self.item.groupID == invConst.groupMobileLaserSentry

    def IsMediumShipHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialMediumShipHoldCapacity)

    def IsMercenaryDen(self):
        return self.item.groupID == invConst.groupMercenaryDen

    def IsMineralHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialMineralHoldCapacity)

    def IsMobileLaboratory(self):
        return self.item.groupID == invConst.groupMobileLaboratory

    def IsMobileShippingUnit(self):
        return self.item.typeID == invConst.typeMobileShippingUnit

    def IsMobileWarpDisruptor(self):
        return self.item.groupID == invConst.groupMobileWarpDisruptor

    def IsModularShip(self):
        return self.item.groupID == invConst.groupStrategicCruiser

    @explain_failure_with('UI/Menusvc/MenuHints/BadGroupForAction', groupName=(GetGroupNameByGroup, 'groupID'))
    def IsMoon(self):
        return self.item.groupID == invConst.groupMoon

    @explain_failure_with('UI/Menusvc/MenuHints/NotYourShip')
    def IsMyActiveShip(self):
        return self.IsShip() and self.IsActiveShip()

    def IsNonScoopableType(self):
        return self.item.typeID in invConst.nonScoopableTypes

    def IsOrbital(self):
        return idCheckers.IsOrbital(self.item.categoryID)

    def IsOrbitalConstructionPlatform(self):
        return self.item.groupID == invConst.groupOrbitalConstructionPlatforms

    def IsGeneralMiningHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).generalMiningHoldCapacity)

    def IsPersonalHangarArray(self):
        return self.item.groupID == invConst.groupPersonalHangar

    def IsOrbitalSkyhook(self):
        return idCheckers.IsSkyhook(self.item.typeID)

    def IsAutoMoonMiner(self):
        return idCheckers.IsAutoMoonMiner(self.item.typeID)

    @explain_failure_with('UI/Menusvc/MenuHints/BadGroupForAction', groupName=(GetGroupNameByGroup, 'groupID'))
    def IsPlanet(self):
        return self.item.groupID == invConst.groupPlanet

    def IsPlanetaryCommoditiesHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialPlanetaryCommoditiesHoldCapacity)

    def IsPlanetaryCustomsOffice(self):
        return self.item.categoryID == invConst.categoryOrbital

    def IsPlanetaryLaunchContainer(self):
        return self.item.typeID == invConst.typePlanetaryLaunchContainer

    def IsPOSMaintainanceArray(self):
        return self.item.groupID in (invConst.groupShipMaintenanceArray, invConst.groupAssemblyArray)

    def IsPublished(self):
        return IsPublished(self.item.typeID)

    def IsQuafeBayShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialQuafeHoldCapacity)

    def IsReactor(self):
        return self.item.groupID == invConst.groupMobileReactor

    def IsRegion(self):
        return self.item.groupID == invConst.groupRegion

    def IsReprocessingArray(self):
        return self.item.groupID == invConst.groupReprocessingArray

    def IsSalvageHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialSalvageHoldCapacity)

    def IsSecureAuditLogContainer(self):
        return self.item.groupID == invConst.groupAuditLogSecureContainer

    def IsSecureContainer(self):
        return self.IsSecureAuditLogContainer() or self.item.groupID == invConst.groupSecureCargoContainer

    def IsSentry(self):
        return self.item.groupID in (invConst.groupMobileMissileSentry, invConst.groupMobileProjectileSentry, invConst.groupMobileHybridSentry)

    def IsShip(self):
        return self.item.categoryID == invConst.categoryShip

    def IsShipHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialShipHoldCapacity)

    def IsShipMaintainanceArray(self):
        return self.item.groupID == invConst.groupShipMaintenanceArray

    def IsSilo(self):
        return self.item.groupID == invConst.groupSilo

    def IsSolarsystem(self):
        return self.item.typeID == invConst.typeSolarSystem

    def IsSovereigntyClaimMarker(self):
        return self.item.groupID == invConst.groupSovereigntyClaimMarkers

    def IsSovereigntyDisruptor(self):
        return self.item.groupID == invConst.groupSovereigntyDisruptionStructures

    def IsSingleton(self):
        return bool(self.item.singleton)

    def IsSmallShipHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialSmallShipHoldCapacity)

    def IsSMBShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).hasShipMaintenanceBay)

    def IsSovereigntyStructure(self):
        return self.item.categoryID == invConst.categorySovereigntyStructure

    def IsStarbase(self):
        return self.item.categoryID == invConst.categoryStarbase

    @explain_failure_with('UI/Menusvc/MenuHints/IsNotStargate')
    def IsStargate(self):
        return self.item.groupID == invConst.groupStargate

    def IsStation(self):
        return idCheckers.IsStation(self.item.itemID)

    def IsStructure(self):
        return self.item.categoryID == invConst.categoryStructure

    def IsShipcasterLauncher(self):
        return HasShipcasterComponent(self.item.typeID)

    def IsSubsystemBayShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialSubsystemHoldCapacity)

    def IsMobileDepotHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialMobileDepotHoldCapacity)

    def IsColonyResourcesHoldShip(self):
        return self.IsShip() and bool(self.godma.GetType(self.item.typeID).specialColonyResourcesHoldCapacity)

    def IsInPilotLocation(self):
        if getattr(self.item, 'locationID', None) is None:
            return False
        if self.item.locationID in (self.session.structureid, self.session.stationid):
            return True
        if self.item.locationID == self.session.shipid and self.item.flagID != invConst.flagShipHangar:
            return True
        if self.session.solarsystemid == self.item.locationID:
            return True
        return False

    @explain_failure_with('UI/Menusvc/MenuHints/NotOwnedByYou')
    def IsOwnedByMe(self):
        return self.item.ownerID == self.session.charid

    def IsOwnedByMyCorp(self):
        return self.item.ownerID == self.session.corpid

    def IsOwnedByMyAlliance(self):
        return self.session.allianceid is not None and self.session.allianceid in (self.item.ownerID, getattr(self.item, 'allianceID', None))

    def IsOwnedByMeOrCorp(self):
        return self.IsOwnedByMe() or self.IsOwnedByMyCorp()

    @explain_failure_with('UI/Corporations/Common/NotOwnedByYouOrCorpOrAlliance')
    def IsOwnedByMeMyCorpOrAlliance(self):
        return self.IsOwnedByMeOrCorp() or self.IsOwnedByMyAlliance()

    def ShouldNotTreatBookmarkAsSolarSystem(self):
        if not should_treat_bookmark_as_solar_system(category_id=self.item.categoryID, group_id=self.item.groupID, type_id=self.item.typeID):
            return True
        return False

    def GetMarketGroup(self):
        return GetMarketGroupID(self.item.typeID)

    def GetBallpark(self):
        return self.getBallpark()

    @explain_failure_with('UI/Menusvc/MenuHints/NotInRange')
    def getDistanceToActiveShip(self):
        bp = self.GetBallpark()
        if bp is None:
            return
        if self.session.shipid not in bp.balls:
            return
        if self.item.itemID not in bp.balls:
            return
        return bp.DistanceBetween(self.session.shipid, self.item.itemID)
