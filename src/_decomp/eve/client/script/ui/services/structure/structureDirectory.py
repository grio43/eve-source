#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\structure\structureDirectory.py
import locks
import structures
import expiringdict
from carbon.common.script.sys.service import Service
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsStructure
from caching.memoize import Memoize
REMOTESVC = 'structureDirectory'

class StructureDirectory(Service):
    __guid__ = 'svc.structureDirectory'
    __notifyevents__ = ['OnCorporationStructuresUpdated',
     'OnSessionChanged',
     'OnDockingRequestWasDenied',
     'OnDockingAccessChangedForCurrentSolarSystem',
     'OnSlimItemChange',
     'OnWarChanged',
     'OnCfgDataChanged',
     'OnStructureRemovedFromSpace']
    __dependencies__ = ['objectCaching']

    def Run(self, memStream = None):
        self.knownStructures = expiringdict.ExpiringDict(1000, 3600)
        self.marketLocationByRegionID = expiringdict.ExpiringDict(1000, 1800)

    def GetStructureInfo(self, structureID):
        if not idCheckers.IsPlayerItem(structureID):
            return None
        if structureID not in self.knownStructures:
            self.knownStructures[structureID] = sm.RemoteSvc(REMOTESVC).GetStructureInfo(structureID)
        return self.knownStructures[structureID]

    def IsStructure(self, structureID):
        return self.GetStructureInfo(structureID) is not None

    @Memoize(5)
    def GetStructures(self):
        return sm.RemoteSvc(REMOTESVC).GetMyCharacterStructures()

    @Memoize(5)
    def GetCorporationStructures(self):
        return sm.RemoteSvc(REMOTESVC).GetMyCorporationStructures()

    @Memoize(5)
    def GetStructuresInCurrentSystem(self):
        solarSystemID = session.solarsystemid2
        if solarSystemID:
            return sm.RemoteSvc(REMOTESVC).GetMyDockableStructures(solarSystemID)
        return set()

    def GetMarketDockableLocationsInRegion(self):
        regionID = session.regionid
        if not regionID:
            return set()
        with locks.TempLock('GetMarketDockableLocationsInRegion'):
            if regionID not in self.marketLocationByRegionID:
                myDockableLocations = sm.RemoteSvc(REMOTESVC).GetMyCharacterStructures()
                marketDockableLocations = set()
                for structureID, structureInfo in myDockableLocations.iteritems():
                    if structures.SERVICE_MARKET in structureInfo['services']:
                        marketDockableLocations.add(structureID)

                self.marketLocationByRegionID[regionID] = marketDockableLocations
        return self.marketLocationByRegionID.get(regionID, set())

    @Memoize(3)
    def GetStructureMapData(self, solarsystemID):
        return sm.RemoteSvc(REMOTESVC).GetStructureMapData(solarsystemID)

    @Memoize(1)
    def GetAccessibleOnlineCynoBeaconStructures(self):
        return sm.RemoteSvc(REMOTESVC).GetMyAccessibleOnlineCynoBeaconStructures()

    @Memoize(1)
    def GetSolarSystemsWithBeacons(self):
        return sm.RemoteSvc(REMOTESVC).GetSolarSystemsWithBeacons()

    def CanContractFrom(self, structureID):
        return self.GetStructureInfo(structureID) is not None

    def OnCorporationStructuresUpdated(self):
        self.GetCorporationStructures.clear_memoized()
        sm.ScatterEvent('OnCorporationStructuresReloaded')

    def Reload(self):
        self.GetStructuresInCurrentSystem.clear_memoized()
        self.GetStructures.clear_memoized()
        self.GetCorporationStructures.clear_memoized()
        self.knownStructures.clear()
        sm.ScatterEvent('OnStructuresReloaded')

    def OnSessionChanged(self, isRemote, sess, change):
        scatterReload = False
        if 'charid' in change and change['charid'][1] is not None:
            self.GetStructures.clear_memoized()
            self.GetCorporationStructures.clear_memoized()
            self.GetStructuresInCurrentSystem.clear_memoized()
            self.GetStructureMapData.clear_memoized()
            self.GetAccessibleOnlineCynoBeaconStructures.clear_memoized()
            self.GetSolarSystemsWithBeacons.clear_memoized()
            self.knownStructures.clear()
            self.marketLocationByRegionID.clear()
            scatterReload = True
        if 'solarsystemid2' in change:
            oldSolarSystemID, newSolarSystemID = change['solarsystemid2']
            if oldSolarSystemID:
                self.GetStructuresInCurrentSystem.clear_memoized()
                self.GetStructureMapData.clear_memoized()
            scatterReload = True
        if 'regionid' in change:
            oldRegionID, newRegionID = change['regionid']
            if oldRegionID is not None:
                self.GetStructures.clear_memoized()
                scatterReload = True
        if scatterReload:
            sm.ScatterEvent('OnStructuresReloaded')

    def OnDockingRequestWasDenied(self, structureID):
        structureProximityTrackerSvc = sm.GetService('structureProximityTracker')
        if not structureProximityTrackerSvc.IsStructureDockable(structureID):
            return
        self.Reload()
        sm.ScatterEvent('OnRefreshWhenDockingRequestDenied', structureID)

    def OnDockingAccessChangedForCurrentSolarSystem(self):
        self.GetStructuresInCurrentSystem.clear_memoized()
        sm.ScatterEvent('OnDockingAccessChangedForCurrentSolarSystem_Local')

    def OnSlimItemChange(self, oldSlim, newSlim):
        if oldSlim.ownerID != newSlim.ownerID and IsStructure(newSlim.categoryID):
            self.knownStructures.pop(oldSlim.itemID)
            self.GetStructuresInCurrentSystem.clear_memoized()
            if session.corpid in (oldSlim.ownerID, newSlim.ownerID):
                self.GetCorporationStructures.clear_memoized()

    def OnWarChanged(self, war, ownerIDs, _):
        if ownerIDs & {session.corpid, session.allianceid}:
            self.GetCorporationStructures.clear_memoized()
        try:
            if self.knownStructures[war.warHQ].solarSystemID == session.solarsystemid2:
                self.GetStructuresInCurrentSystem.clear_memoized()
        except KeyError:
            pass

        self.knownStructures.pop(war.warHQ)

    def OnCfgDataChanged(self, what, data):
        if what == 'evelocations':
            self.knownStructures.pop(data[0], None)

    def OnStructureRemovedFromSpace(self, structureID):
        self.knownStructures.pop(structureID, None)

    @staticmethod
    def GetJbStructureDestination(structureID):
        return sm.RemoteSvc('structureJumpBridgeMgr').GetJbStructureDestination(structureID)

    @staticmethod
    def GetValidWarHQs():
        ownerID = session.allianceid or session.corpid
        return sm.RemoteSvc(REMOTESVC).GetValidWarHQs(ownerID)
