#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\util\clientPathfinderService.py
import gametime
import logging
import pyEvePathfinder
import uthread2
import six
from carbon.common.lib import telemetry
from carbon.common.script.sys.service import Service
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsSolarSystem
from evePathfinder.eveMapWrapper import EveMapWrapper
from evePathfinder.pathfinder import ClientPathfinder
from evePathfinder.stateinterface import AutopilotPathfinderInterface, StandardPathfinderInterface
from signals import Signal
from stargate.client.gate_signals import on_lock_changed, on_lock_added, on_lock_removed, on_lock_changed_in_restricted_system
from stargate.client.gateLockController import GateLockController
from stargate.client import get_gate_lock_messenger
from threadutils import be_nice
logger = logging.getLogger(__name__)
PATHFINDER_WAIT_TIMEOUT_SECONDS = 60

def ConvertStationIDToSolarSystemIDIfNecessary(waypointID):
    if idCheckers.IsStation(waypointID):
        return cfg.stations.Get(waypointID).solarSystemID
    if idCheckers.IsSolarSystem(waypointID):
        return waypointID
    structure = sm.GetService('structureDirectory').GetStructureInfo(waypointID)
    if structure is not None:
        return structure.solarSystemID
    return waypointID


def GetCurrentSolarSystemID():
    return session.solarsystemid2


def UpdatesAutopilot(func):

    def Wrapper(*args, **kwargs):
        func(*args, **kwargs)
        sm.ScatterEvent('OnAutopilotUpdated')

    return Wrapper


class PathfinderWaitTimoutError(Exception):
    pass


def WaitForPathfinderInitialization(func):

    def Wrapper(self, *args, **kwargs):
        startTime = gametime.GetWallclockTime()
        while not self.initialized or self.clientPathfinder is None:
            if gametime.GetSecondsSinceWallclockTime(startTime) > PATHFINDER_WAIT_TIMEOUT_SECONDS:
                raise PathfinderWaitTimoutError()
            uthread2.sleep(0.1)

        return func(self, *args, **kwargs)

    return Wrapper


class ClientPathfinderService(Service):
    __exportedcalls__ = {}
    __guid__ = 'svc.clientPathfinderService'
    __servicename__ = 'pathfinderSvc'
    __displayname__ = 'Client Pathfinder Service'
    __dependencies__ = ['settings',
     'map',
     'objectCaching',
     'securitySvc']
    __notifyevents__ = ['OnCharacterSessionChanged', 'OnSecurityModified', 'OnSessionReset']
    _PATHFINDER_IGNORED_GATES = ()

    def Run(self, memStream = None):
        self.clientPathfinder = None
        self.lastJumpGatesLoaded = {}
        self._gate_lock_controller = GateLockController.get_instance(get_gate_lock_messenger(sm.GetService('publicGatewaySvc')))
        self.on_pathfinder_initialized = Signal('on_pathfinder_initialized')
        self.initialized = False
        self.LogInfo('Starting Client Pathfinder Service')

    def OnCharacterSessionChanged(self, _oldCharacterID, newCharacterID):
        if newCharacterID is not None:
            self.Initialize()

    def OnSessionReset(self):
        self.lastJumpGatesLoaded.clear()
        self.initialized = False

    def OnSecurityModified(self, solarSystemID, modifierAmount, newSecurity):
        if self.clientPathfinder is not None:
            self.clientPathfinder.pathfinderCore.newPathfinderMap.SetSolarSystemSecurity(solarSystemID, newSecurity)
            sm.GetService('autoPilot').OptimizeRoute()
            sm.ScatterEvent('OnAutopilotUpdated')

    def UpdateJumpGates(self):
        availableJumpThroughStructures = self.GetAvailableJumpGateJumps(cfg.mapJumpCache)
        if self.lastJumpGatesLoaded == availableJumpThroughStructures:
            return
        self.lastJumpGatesLoaded = availableJumpThroughStructures
        self.ForceUpdatePathfinderCore()

    def ForceUpdatePathfinderCore(self):
        pathfinderCore = self.CreatePathfinderCore(cfg.mapRegionCache, cfg.mapSystemCache, cfg.mapJumpCache, self.securitySvc.get_modified_security_level, self.GetJumpGateTuple(self.lastJumpGatesLoaded), ClientPathfinderService._PATHFINDER_IGNORED_GATES)
        self.clientPathfinder.UpdatePathfinderCore(pathfinderCore)

    @telemetry.ZONE_METHOD
    def CreatePathfinderCore(self, mapRegionCache, mapSystemCache, mapJumpCache, get_security_level_func, one_way_jump_tuples = (), ignored_stargate_ids = ()):
        eve_map = EveMapWrapper()
        eve_map.add_regions(mapRegionCache)
        eve_map.add_solar_systems(mapSystemCache, get_security_level_func)
        restricted_system_ids = self._gate_lock_controller.get_restricted_systems()
        solar_system_to_emanation_lock_details_dict = self._gate_lock_controller.get_solar_system_to_lock_details_dict()
        for jump in mapJumpCache:
            if jump.stargateID in ignored_stargate_ids:
                logger.info('ClientPathfinderService - client pathfinder has ignored (excluded) jump from Stargate %s (in SolarSystem %s) to reach SolarSystem %s', jump.stargateID, jump.fromSystemID, jump.toSystemID)
            elif jump.fromSystemID in restricted_system_ids or jump.toSystemID in restricted_system_ids:
                opposite_gate_id = cfg.mapStargateIdMappingCache[jump.stargateID]
                for fromSystemID, toSystemID, stargateID in ((jump.fromSystemID, jump.toSystemID, jump.stargateID), (jump.toSystemID, jump.fromSystemID, opposite_gate_id)):
                    if session.solarsystemid2 != fromSystemID and fromSystemID in restricted_system_ids:
                        logger.info('Emanation Lock - client pathfinder has excluded jumping from Stargate %s (in SolarSystem %s) to reach SolarSystem %s', stargateID, fromSystemID, toSystemID)
                        continue
                    emanation_lock_details = solar_system_to_emanation_lock_details_dict.get(fromSystemID)
                    logger.info('Emanation Lock - %s', emanation_lock_details)
                    if emanation_lock_details is not None and stargateID != emanation_lock_details.gate_id:
                        logger.info('Emanation Lock - client pathfinder has excluded jumping from Stargate %s (in SolarSystem %s) to reach SolarSystem %s', stargateID, fromSystemID, toSystemID)
                        continue
                    logger.info('Emanation Lock - client pathfinder has included jump from Stargate %s (in SolarSystem %s) to reach SolarSystem %s', stargateID, fromSystemID, toSystemID)
                    eve_map.add_jump(fromSystemID, toSystemID)

            else:
                eve_map.add_jump(jump.fromSystemID, jump.toSystemID)
                eve_map.add_jump(jump.toSystemID, jump.fromSystemID)
            be_nice()

        eve_map.add_one_way_jumps(one_way_jump_tuples)
        eve_map.finalize()
        return eve_map.create_core()

    def on_emanation_lock_added(self, lock_details):
        if not self.initialized:
            self.on_pathfinder_initialized.connect(self._on_emanation_lock_updated_delayed)
            return
        self._on_emanation_locks_updated()

    def _on_emanation_lock_updated_delayed(self):
        self.on_pathfinder_initialized.disconnect(self._on_emanation_lock_updated_delayed)
        self._on_emanation_locks_updated()

    def on_emanation_lock_removed(self, lock_details):
        self._on_emanation_locks_updated()

    def on_lock_changed_in_restricted_system(self, lock_details, previous_lock):
        if not self.initialized:
            self.on_pathfinder_initialized.connect(self._on_emanation_lock_updated_delayed)
            return
        self._on_emanation_locks_updated()

    def on_emanation_lock_changed(self, lock_details, previous_lock):
        if lock_details is None and previous_lock is None:
            return
        self._on_emanation_locks_updated()

    def _on_emanation_locks_updated(self):
        self.ForceUpdatePathfinderCore()
        sm.GetService('starmap').UpdateRoute()

    def Initialize(self):
        self.LogInfo('Initializing the pathfinding internals')
        self.lastPKversionNumber = -1
        self.lastTrigTaleVersionNumber = -1
        if self.clientPathfinder is None:
            on_lock_changed.connect(self.on_emanation_lock_changed)
            on_lock_changed_in_restricted_system.connect(self.on_lock_changed_in_restricted_system)
            on_lock_added.connect(self.on_emanation_lock_added)
            on_lock_removed.connect(self.on_emanation_lock_removed)
        availableJumpThroughStructures = self.GetAvailableJumpGateJumps(cfg.mapJumpCache)
        self.lastJumpGatesLoaded = availableJumpThroughStructures
        pathfinderCore = self.CreatePathfinderCore(cfg.mapRegionCache, cfg.mapSystemCache, cfg.mapJumpCache, self.securitySvc.get_modified_security_level, self.GetJumpGateTuple(availableJumpThroughStructures), ClientPathfinderService._PATHFINDER_IGNORED_GATES)
        autopilotStateInterface = AutopilotPathfinderInterface(self.map, self.UpdatePodKillList, self.GetTriglavianTaleAvoidanceSystems, self.GetEdencomSystemsAvoidanceList, settings.char.ui)
        standardStateInterface = StandardPathfinderInterface()
        self.clientPathfinder = ClientPathfinder(pathfinderCore, standardStateInterface, autopilotStateInterface, ConvertStationIDToSolarSystemIDIfNecessary, GetCurrentSolarSystemID)
        self.initialized = True
        self.on_pathfinder_initialized()

    def GetAvailableJumpGateJumps(self, mapJumpCache):
        availableJumpGates = {}
        if not settings.char.ui.Get('pathFinder_includeJumpGates', False):
            return availableJumpGates
        stargateJumps = set()
        for jump in mapJumpCache:
            stargateJumps.add((jump.fromSystemID, jump.toSystemID))
            stargateJumps.add((jump.toSystemID, jump.fromSystemID))

        mapsSvc = sm.GetService('map')
        mapsSvc.GetJumpBridgesWithMyAccess.clear_memoized()
        jumpBridgesGates, hasAccessTo, hasNoAccessTo = mapsSvc.GetJumpBridgesWithMyAccess()
        for structureA, structureB in jumpBridgesGates:
            solarSystemA = structureA.solarSystemID
            solarSystemB = structureB.solarSystemID
            if not IsSolarSystem(solarSystemA) or not IsSolarSystem(solarSystemB):
                continue
            if structureA.structureID in hasAccessTo and (solarSystemA, solarSystemB) not in stargateJumps:
                availableJumpGates[solarSystemA, solarSystemB] = structureA.structureID
            if structureB.structureID in hasAccessTo and (solarSystemB, solarSystemA) not in stargateJumps:
                availableJumpGates[solarSystemB, solarSystemA] = structureB.structureID

        return availableJumpGates

    def GetJumpGateTuple(self, availableJumps):
        return [ (k[0], k[1], v) for k, v in availableJumps.iteritems() ]

    def UpdatePodKillList(self, podKillList):
        args = (const.mapHistoryStatKills, 24)
        if self.lastPKversionNumber == -1 or self.lastPKversionNumber != self.objectCaching.GetCachedMethodCallVersion(None, 'map', 'GetHistory', args):
            unfilteredSystemHistory = sm.RemoteSvc('map').GetHistory(*args)
            self.lastPKversionNumber = self.objectCaching.GetCachedMethodCallVersion(None, 'map', 'GetHistory', args)
            podKillList = []
            for system in unfilteredSystemHistory:
                if system.value3 > 0:
                    podKillList.append(system.solarSystemID)

            podKillList.sort()
        return podKillList

    def GetTriglavianTaleAvoidanceSystems(self):
        return sm.GetService('map').GetTriglavianMinorVictorySystems()

    def GetEdencomSystemsAvoidanceList(self):
        return sm.GetService('map').GetEdencomAvoidanceSystems()

    def AddAvoidanceItem(self, *args, **kwds):
        self.clientPathfinder.AddAvoidanceItem(*args, **kwds)
        sm.ScatterEvent('OnAutopilotUpdated')
        sm.ScatterEvent('OnAvoidanceItemsChanged')

    def RemoveAvoidanceItem(self, *args, **kwds):
        self.clientPathfinder.RemoveAvoidanceItem(*args, **kwds)
        sm.ScatterEvent('OnAutopilotUpdated')
        sm.ScatterEvent('OnAvoidanceItemsChanged')

    def GetLastKnownJumpGates(self):
        return self.lastJumpGatesLoaded

    def GetMandatoryAvoidanceItems(self):
        return self._gate_lock_controller.get_restricted_systems()

    @WaitForPathfinderInitialization
    def GetAvoidanceItems(self, *args, **kwargs):
        return self.clientPathfinder.GetAvoidanceItems(*args, **kwargs)

    @WaitForPathfinderInitialization
    def GetAutopilotRouteType(self, *args, **kwargs):
        return self.clientPathfinder.GetAutopilotRouteType(*args, **kwargs)

    @WaitForPathfinderInitialization
    def GetWaypointPath(self, *args, **kwargs):
        return self.clientPathfinder.GetWaypointPath(*args, **kwargs)

    @WaitForPathfinderInitialization
    def GetJumpCountsBetweenSystemPairs(self, *args, **kwargs):
        return self.clientPathfinder.GetJumpCountsBetweenSystemPairs(*args, **kwargs)

    @WaitForPathfinderInitialization
    def GetPathBetween(self, *args, **kwargs):
        return self.clientPathfinder.GetPathBetween(*args, **kwargs)

    @WaitForPathfinderInitialization
    def GetAutopilotPathBetween(self, *args, **kwargs):
        return self.clientPathfinder.GetAutopilotPathBetween(*args, **kwargs)

    @WaitForPathfinderInitialization
    def GetJumpCount(self, *args, **kwargs):
        return self.clientPathfinder.GetJumpCount(*args, **kwargs)

    @WaitForPathfinderInitialization
    def GetAutopilotJumpCount(self, *args, **kwargs):
        return self.clientPathfinder.GetAutopilotJumpCount(*args, **kwargs)

    @WaitForPathfinderInitialization
    def GetJumpCountFromCurrent(self, *args, **kwargs):
        return self.clientPathfinder.GetJumpCountFromCurrent(*args, **kwargs)

    @WaitForPathfinderInitialization
    def GetSystemsWithinAutopilotJumpRange(self, *args, **kwargs):
        return self.clientPathfinder.GetSystemsWithinAutopilotJumpRange(*args, **kwargs)

    @WaitForPathfinderInitialization
    def GetSystemsWithinJumpRange(self, *args, **kwargs):
        return self.clientPathfinder.GetSystemsWithinJumpRange(*args, **kwargs)

    @WaitForPathfinderInitialization
    def GetExpandedAvoidanceItems(self, *args, **kwargs):
        return self.clientPathfinder.GetExpandedAvoidanceItems(*args, **kwargs)

    @WaitForPathfinderInitialization
    def GetNoRouteFoundText(self, *args, **kwargs):
        return self.clientPathfinder.GetNoRouteFoundText(*args, **kwargs)

    @WaitForPathfinderInitialization
    def GetNoRouteFoundTextAutopilot(self, *args, **kwargs):
        return self.clientPathfinder.GetNoRouteFoundTextAutopilot(*args, **kwargs)

    @UpdatesAutopilot
    def SetPodKillAvoidance(self, *args, **kwargs):
        self.clientPathfinder.SetPodKillAvoidance(*args, **kwargs)

    @UpdatesAutopilot
    def SetTriglavianTaleAvoidance(self, *args, **kwargs):
        self.clientPathfinder.SetTriglavianTaleAvoidance(*args, **kwargs)

    @UpdatesAutopilot
    def SetEdencomSystemsAvoidance(self, *args, **kwargs):
        self.clientPathfinder.SetEdencomSystemsAvoidance(*args, **kwargs)

    @UpdatesAutopilot
    def SetSystemAvoidance(self, *args, **kwargs):
        self.clientPathfinder.SetSystemAvoidance(*args, **kwargs)

    @UpdatesAutopilot
    def SetAutopilotRouteType(self, *args, **kwargs):
        self.clientPathfinder.SetAutopilotRouteType(*args, **kwargs)

    @UpdatesAutopilot
    def SetSecurityPenaltyFactor(self, *args, **kwargs):
        self.clientPathfinder.SetSecurityPenaltyFactor(*args, **kwargs)
