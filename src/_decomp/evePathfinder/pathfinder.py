#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evePathfinder\pathfinder.py
from collections import defaultdict
import sys
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem, IsTriglavianSystem, IsWormholeSystem
from evePathfinder.pathfinderconst import UNREACHABLE_JUMP_COUNT

class ClientPathfinder(object):

    def __init__(self, pathfinderCore, standardStateInterface, autopilotStateInterface, convertStationIDToSolarSystemIDIfNecessaryMethod, getCurrentSystemMethod):
        self._standardStateInterface = standardStateInterface
        self._autopilotStateInterface = autopilotStateInterface
        self.pathfinderCore = pathfinderCore
        self.pathfinderCore.SetGetCachedEntryMethod(self.GetCachedEntry)
        self.pathfinderCacheByStateInterfaceAndRouteType = defaultdict(self.pathfinderCore.CreateCacheEntry)
        self.ConvertStationIDToSolarSystemIDIfNecessary = convertStationIDToSolarSystemIDIfNecessaryMethod
        self.GetCurrentSystem = getCurrentSystemMethod

    def UpdatePathfinderCore(self, pathfinderCore):
        self.pathfinderCore = pathfinderCore
        self.pathfinderCore.SetGetCachedEntryMethod(self.GetCachedEntry)
        self.pathfinderCacheByStateInterfaceAndRouteType.clear()
        self.pathfinderCacheByStateInterfaceAndRouteType.default_factory = self.pathfinderCore.CreateCacheEntry

    def GetCachedEntry(self, stateInterface, fromID):
        return self.pathfinderCacheByStateInterfaceAndRouteType[id(stateInterface), stateInterface.GetRouteType()]

    def SetSecurityPenaltyFactor(self, securityPenalty):
        self._autopilotStateInterface.SetSecurityPenaltyFactor(securityPenalty)

    def SetPodKillAvoidance(self, pkAvoid):
        self._autopilotStateInterface.SetPodKillAvoidance(pkAvoid)

    def SetTriglavianTaleAvoidance(self, avoid):
        self._autopilotStateInterface.SetTriglavianTaleAvoidance(avoid)

    def SetEdencomSystemsAvoidance(self, avoid):
        self._autopilotStateInterface.SetEdencomSystemsAvoidance(avoid)

    def SetSystemAvoidance(self, pkAvoid = None):
        self._autopilotStateInterface.SetSystemAvoidance(pkAvoid)

    def GetAvoidanceItems(self):
        return self._autopilotStateInterface.GetAvoidanceItems(expandSystems=False)

    def GetExpandedAvoidanceItems(self):
        return self._autopilotStateInterface.GetAvoidanceItems(expandSystems=True)

    def AddAvoidanceItem(self, itemID):
        items = self.GetAvoidanceItems()
        items.append(itemID)
        self._autopilotStateInterface.SetAvoidanceItems(items)

    def RemoveAvoidanceItem(self, itemID):
        items = self.GetAvoidanceItems()
        if itemID in items:
            items.remove(itemID)
            self._autopilotStateInterface.SetAvoidanceItems(items)
            self.SetSystemAvoidance()

    def SetAutopilotRouteType(self, routeType):
        self._autopilotStateInterface.SetRouteType(routeType)

    def GetAutopilotRouteType(self):
        return self._autopilotStateInterface.GetRouteType()

    def GetCompleteWaypointList(self, waypointWithOnlySystems, waypoints):
        completeWaypointList = []
        currentWaypointIndex = 1
        currentSolarSystem = None
        for pathWithSolarSystems in waypointWithOnlySystems:
            if len(pathWithSolarSystems) == 0:
                continue
            pathEndpoint = pathWithSolarSystems[-1]
            pathStartPoint = pathWithSolarSystems[0]
            currentWaypoint = waypoints[currentWaypointIndex]
            if pathWithSolarSystems[-1] != currentWaypoint:
                pathWithSolarSystems.append(currentWaypoint)
            if pathStartPoint == currentSolarSystem:
                pathWithSolarSystems.pop(0)
            currentSolarSystem = pathEndpoint
            completeWaypointList.extend(pathWithSolarSystems)
            currentWaypointIndex += 1

        return completeWaypointList

    def GetWaypointPath(self, waypoints):
        solarSystemWaypoints = list(map(self.ConvertStationIDToSolarSystemIDIfNecessary, waypoints))
        waypointListsContainingOnlySystems = self.pathfinderCore.GetListOfWaypointPaths(self._autopilotStateInterface, self.GetCurrentSystem(), solarSystemWaypoints)
        return self.GetCompleteWaypointList(waypointListsContainingOnlySystems, waypoints)

    def GetJumpCountsBetweenSystemPairs(self, sourceDestinationPairList):
        return self.pathfinderCore.GetJumpCountsBetweenSystemPairs(self._standardStateInterface, sourceDestinationPairList)

    def _GetPathBetween(self, stateInterface, fromID, toID):
        if not IsKnownSpaceSystem(fromID) or not IsKnownSpaceSystem(toID):
            return []
        return self.pathfinderCore.GetPathBetween(stateInterface, fromID, toID)

    def GetPathBetween(self, fromID, toID):
        return self._GetPathBetween(self._standardStateInterface, fromID, toID)

    def GetAutopilotPathBetween(self, fromID, toID):
        convertedFromID = self.ConvertStationIDToSolarSystemIDIfNecessary(fromID)
        convertedToID = self.ConvertStationIDToSolarSystemIDIfNecessary(toID)
        return self._GetPathBetween(self._autopilotStateInterface, convertedFromID, convertedToID)

    def _GetJumpCount(self, stateInterface, fromID, toID):
        if fromID is None or toID is None:
            return
        if fromID == toID:
            return 0
        if not IsKnownSpaceSystem(fromID) or not IsKnownSpaceSystem(toID):
            return UNREACHABLE_JUMP_COUNT
        return self.pathfinderCore.GetJumpCountBetween(stateInterface, fromID, toID)

    def GetJumpCount(self, fromID, toID):
        return self._GetJumpCount(self._standardStateInterface, fromID, toID)

    def GetAutopilotJumpCount(self, fromID, toID):
        return self._GetJumpCount(self._autopilotStateInterface, fromID, toID)

    def GetJumpCountFromCurrent(self, toID):
        return self._GetJumpCount(self._standardStateInterface, self.GetCurrentSystem(), toID)

    def _GetSystemsWithinJumpRange(self, stateInterface, fromID, jumpCountMin, jumpCountMax):
        if not IsKnownSpaceSystem(fromID):
            return {}
        return self.pathfinderCore.GetSystemsWithinJumpRange(stateInterface, fromID, jumpCountMin, jumpCountMax)

    def GetSystemsWithinJumpRange(self, fromID, jumpCountMin, jumpCountMax):
        return self._GetSystemsWithinJumpRange(self._standardStateInterface, fromID, jumpCountMin, jumpCountMax)

    def GetSystemsWithinAutopilotJumpRange(self, fromID, jumpCountMin, jumpCountMax):
        return self._GetSystemsWithinJumpRange(self._autopilotStateInterface, fromID, jumpCountMin, jumpCountMax)

    def _GetNoRouteFoundText(self, solarSystemID, shouldConsiderAutopilotSettings = False):
        import localization
        if IsTriglavianSystem(solarSystemID) or IsWormholeSystem(solarSystemID):
            return localization.GetByLabel('UI/Generic/NoGateToGateRoute')
        clientPathfinderService = sm.GetService('clientPathfinderService')
        if shouldConsiderAutopilotSettings:
            if clientPathfinderService.GetAutopilotPathBetween(const.solarSystemJita, solarSystemID):
                return localization.GetByLabel('UI/Generic/NoGateToGateRoute')
        elif clientPathfinderService.GetPathBetween(const.solarSystemJita, solarSystemID):
            return localization.GetByLabel('UI/Generic/NoGateToGateRoute')
        return localization.GetByLabel('UI/Generic/Unreachable')

    def GetNoRouteFoundText(self, solarSystemID):
        return self._GetNoRouteFoundText(solarSystemID, shouldConsiderAutopilotSettings=False)

    def GetNoRouteFoundTextAutopilot(self, solarSystemID):
        return self._GetNoRouteFoundText(solarSystemID, shouldConsiderAutopilotSettings=True)
