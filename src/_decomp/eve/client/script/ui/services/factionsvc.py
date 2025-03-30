#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\factionsvc.py
from carbon.common.script.sys.service import Service
from collections import defaultdict
import telemetry
from characterdata.factions import get_faction_ids
from npcs.npccorporations import get_npc_corporation_ids

class Faction(Service):
    __exportedcalls__ = {'GetFactionLocations': [],
     'GetFactionOfSolarSystem': [],
     'GetPirateFactionsOfRegion': []}
    __guid__ = 'svc.faction'
    __notifyevents__ = ['OnSessionChanged']
    __servicename__ = 'account'
    __displayname__ = 'Faction Service'

    def Run(self, memStream = None):
        self.LogInfo('Starting Faction Svc')
        self.factionRegions = None
        self.factionConstellations = None
        self.factionSolarSystems = None
        self.factionRaces = None
        self.solarSystemFactions = None
        self.currentFactionID = None

    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid2' in change:
            self.currentFactionID = (eve.session.solarsystemid2, self.GetFactionOfSolarSystem(eve.session.solarsystemid2))

    @telemetry.ZONE_FUNCTION
    def GetCurrentFactionID(self):
        if self.currentFactionID is None:
            self.currentFactionID = (eve.session.solarsystemid2, self.GetFactionOfSolarSystem(eve.session.solarsystemid2))
        return self.currentFactionID[1]

    @telemetry.ZONE_METHOD
    def GetFactionOfSolarSystem(self, solarsystemID):
        if self.solarSystemFactions is None:
            self.GetData()
        return self.solarSystemFactions.get(solarsystemID, None)

    def GetFactionsOfConstellation(self, constellationID):
        if self.factionsByConstellation is None:
            self.GetData()
        return self.factionsByConstellation.get(constellationID, [])

    def GetFactionsOfRegion(self, regionID):
        if self.factionsByRegion is None:
            self.GetData()
        return self.factionsByRegion.get(regionID, [])

    def GetPirateFactionsOfRegion(self, regionID):
        return {10000001: (500019,),
         10000002: (500010,),
         10000003: (500010,),
         10000005: (500011,),
         10000006: (500011,),
         10000007: (500011,),
         10000008: (500011,),
         10000009: (500011,),
         10000010: (500010,),
         10000011: (500011,),
         10000012: (500011,),
         10000014: (500019,),
         10000015: (500010,),
         10000016: (500010,),
         10000020: (500019,),
         10000022: (500019,),
         10000023: (500010,),
         10000025: (500011,),
         10000028: (500011,),
         10000029: (500010,),
         10000030: (500011,),
         10000031: (500011,),
         10000032: (500020,),
         10000033: (500010,),
         10000035: (500010,),
         10000036: (500019,),
         10000037: (500020,),
         10000038: (500012,),
         10000039: (500019,),
         10000041: (500020,),
         10000042: (500011,),
         10000043: (500019,),
         10000044: (500020,),
         10000045: (500010,),
         10000046: (500020,),
         10000047: (500019,),
         10000048: (500020,),
         10000049: (500012, 500019),
         10000050: (500012,),
         10000051: (500020,),
         10000052: (500012,),
         10000054: (500012,),
         10000055: (500010,),
         10000056: (500011,),
         10000057: (500020,),
         10000058: (500020,),
         10000059: (500019,),
         10000060: (500012,),
         10000061: (500011,),
         10000062: (500011,),
         10000063: (500012,),
         10000064: (500020,),
         10000065: (500012,),
         10000067: (500012,),
         10000068: (500020,)}.get(regionID, ())

    def GetFactionLocations(self, factionID):
        if self.factionRegions is None:
            self.GetData()
        return (self.factionRegions.get(factionID, []), self.factionConstellations.get(factionID, []), self.factionSolarSystems.get(factionID, []))

    def Stop(self, memStream = None):
        self.factionRegions = None
        self.factionConstellations = None
        self.factionSolarSystems = None
        self.factionAllies = None
        self.factionEnemiesNone = None

    @telemetry.ZONE_METHOD
    def GetData(self):
        self.factionRegions = defaultdict(list)
        self.factionConstellations = defaultdict(list)
        self.factionSolarSystems = defaultdict(list)
        self.solarSystemFactions = {}
        self.factionsByConstellation = defaultdict(list)
        self.factionsByRegion = defaultdict(list)
        ownersToPrime = set()
        ownersToPrime.update(get_npc_corporation_ids())
        ownersToPrime.update(get_faction_ids())
        for regionID, region in cfg.mapRegionCache.iteritems():
            if hasattr(region, 'factionID'):
                self.factionRegions[region.factionID].append(regionID)
                self.factionsByRegion[regionID].append(region.factionID)

        for constellationID, constellation in cfg.mapConstellationCache.iteritems():
            if hasattr(constellation, 'factionID'):
                self.factionConstellations[constellation.factionID].append(constellationID)
                self.factionsByConstellation[constellationID].append(constellation.factionID)

        for solarSystemID, solarSystem in cfg.mapSystemCache.iteritems():
            if hasattr(solarSystem, 'factionID'):
                self.factionSolarSystems[solarSystem.factionID].append(solarSystemID)
                self.solarSystemFactions[solarSystemID] = solarSystem.factionID

        if len(ownersToPrime):
            cfg.eveowners.Prime(ownersToPrime)
