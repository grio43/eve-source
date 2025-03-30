#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evePathfinder\stateinterface.py
import hashlib
import math
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem
from evePathfinder.pathfinderconst import ROUTE_TYPE_SHORTEST
from evePathfinder.pathfinderconst import ROUTE_TYPE_SAFE
from evePathfinder.pathfinderconst import DEFAULT_SECURITY_PENALTY_VALUE
from evePathfinder.pathfinderconst import SECURITY_PENALTY_FACTOR
from evePathfinder.pathfinderconst import DEFAULT_SECURITY_PENALTY
from inventorycommon.const import solarSystemJita, solarSystemZarzakh
DEFAULT_AVOIDANCE = [solarSystemJita, solarSystemZarzakh]

def GetCurrentStateHash(stateInterface, fromSolarSystemID):
    m = hashlib.md5()
    m.update(str(fromSolarSystemID))
    m.update(stateInterface.GetRouteType())
    m.update(str(stateInterface.GetSecurityPenalty()))
    m.update(str(stateInterface.GetAvoidanceList()))
    return m.hexdigest()


class StandardPathfinderInterface(object):

    def __init__(self):
        self.routeType = ROUTE_TYPE_SHORTEST

    def GetSecurityPenalty(self):
        return DEFAULT_SECURITY_PENALTY_VALUE

    def GetAvoidanceList(self):
        return []

    def SetRouteType(self, routeType):
        self.routeType = routeType

    def GetRouteType(self):
        return self.routeType

    def GetCurrentStateHash(self, fromSolarSystemID):
        return GetCurrentStateHash(self, fromSolarSystemID)


class AutopilotPathfinderInterface(object):

    def __init__(self, mapSvc, updatePodKillListFunc, getTriglavianTaleAvoidanceSystemsFunc, getEdencomSystemsAvoidanceList, autopilotSettings):
        self.podKillList = []
        self.lastPKversionNumber = -1
        self.mapSvc = mapSvc
        self.UpdatePodKillList = updatePodKillListFunc
        self.GetTriglavianTaleAvoidanceSystems = getTriglavianTaleAvoidanceSystemsFunc
        self.GetEdencomSystemsAvoidanceList = getEdencomSystemsAvoidanceList
        self.autopilotSettings = autopilotSettings

    def GetPodkillSystemList(self):
        self.podKillList = self.UpdatePodKillList(self.podKillList)
        return self.podKillList

    def GetSecurityPenalty(self):
        return math.exp(SECURITY_PENALTY_FACTOR * self.autopilotSettings.Get('pfPenalty', DEFAULT_SECURITY_PENALTY))

    def GetAvoidanceList(self):
        items = []
        if self.IsAvoidanceEnabled():
            avoidedItems = self.autopilotSettings.Get('autopilot_avoidance2', DEFAULT_AVOIDANCE)
            avoidedSystems = self.mapSvc.ExpandItems(avoidedItems)
            items.extend(avoidedSystems)
        if self.IsPodkillAvoidanceEnabled():
            items.extend(self.GetPodkillSystemList())
        if self.IsTriglavianTaleAvoidanceEnabled():
            items.extend(self.GetTriglavianTaleAvoidanceSystems())
        if self.IsEdencomSystemsAvoidanceEnabled():
            items.extend(self.GetEdencomSystemsAvoidanceList())
        items = [ solarSystemID for solarSystemID in items if IsKnownSpaceSystem(solarSystemID) ]
        items.sort()
        return items

    def GetAvoidanceItems(self, expandSystems):
        items = self.autopilotSettings.Get('autopilot_avoidance2', DEFAULT_AVOIDANCE)
        if expandSystems:
            items = self.mapSvc.ExpandItems(items)
        return items

    def SetAvoidanceItems(self, items):
        self.autopilotSettings.Set('autopilot_avoidance2', items)

    def SetSystemAvoidance(self, pkAvoid = None):
        self.autopilotSettings.Set('pfAvoidSystems', pkAvoid)

    def SetRouteType(self, routeType):
        self.autopilotSettings.Set('pfRouteType', routeType)

    def GetRouteType(self):
        return self.autopilotSettings.Get('pfRouteType', ROUTE_TYPE_SAFE)

    def SetPodKillAvoidance(self, pkAvoid):
        self.autopilotSettings.Set('pfAvoidPodKill', pkAvoid)

    def SetTriglavianTaleAvoidance(self, avoid):
        self.autopilotSettings.Set('pfAvoidTriglavianTales', avoid)

    def SetEdencomSystemsAvoidance(self, avoid):
        self.autopilotSettings.Set('pfAvoidEdencomSystems', avoid)

    def IsAvoidanceEnabled(self):
        return self.autopilotSettings.Get('pfAvoidSystems', 1)

    def IsPodkillAvoidanceEnabled(self):
        return self.autopilotSettings.Get('pfAvoidPodKill', 0)

    def IsTriglavianTaleAvoidanceEnabled(self):
        return self.autopilotSettings.Get('pfAvoidTriglavianTales', 0)

    def IsEdencomSystemsAvoidanceEnabled(self):
        return self.autopilotSettings.Get('pfAvoidEdencomSystems', 0)

    def GetCurrentStateHash(self, fromSolarSystemID):
        return GetCurrentStateHash(self, fromSolarSystemID)

    def SetSecurityPenaltyFactor(self, securityPenalty):
        self.autopilotSettings.Set('pfPenalty', securityPenalty)
