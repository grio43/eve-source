#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\industry\facilitySvc.py
import uthread
import telemetry
from carbon.common.script.sys.service import Service
from eve.common.script.util import industryCommon
from caching.memoize import Memoize
from eveexceptions import UserError
from inventorycommon.const import typeOffice

class FacilityService(Service):
    __guid__ = 'svc.facilitySvc'
    __servicename__ = 'Facility Service'
    __displayname__ = 'Facility Service'
    __dependencies__ = ['clientPathfinderService']
    __notifyevents__ = ['OnSessionChanged', 'OnSystemActivityUpdated', 'OnFacilitiesUpdated']

    def Run(self, *args, **kwargs):
        Service.Run(self, *args, **kwargs)
        self.facilities = {}
        self.maxActivityModifiers = None
        self.loadedRegion = None
        self.loading = uthread.Semaphore()
        self.facilityManager = sm.RemoteSvc('facilityManager')

    def OnSessionChanged(self, isRemote, session, change):
        if 'regionid' in change:
            self.Reload()
        if 'solarsystemid2' in change or 'stationid' in change:
            map(self._UpdateFacilityDistance, self.facilities.itervalues())
            sm.ScatterEvent('OnFacilitiesReloaded', None)

    def OnSystemActivityUpdated(self):
        self.maxActivityModifiers = None
        self.Reload()

    def OnFacilitiesUpdated(self, facilityIDs):
        for facilityID in facilityIDs:
            self.facilities.pop(facilityID, None)
            try:
                self._PrimeFacility(self.facilityManager.GetFacility(facilityID))
            except UserError:
                pass

        sm.ScatterEvent('OnFacilitiesReloaded', facilityIDs)

    @telemetry.ZONE_METHOD
    def GetFacilities(self, facilityIDs = None):
        if facilityIDs is None or self.loadedRegion is None:
            self._PrimeFacilities()
        if facilityIDs:
            fetch = set(facilityIDs) - set(self.facilities.keys())
            if fetch:
                for facility in self.facilityManager.GetFacilitiesByID(facilityIDs):
                    self._PrimeFacility(facility)

        return [ f for k, f in self.facilities.iteritems() if facilityIDs is None or k in facilityIDs ]

    @telemetry.ZONE_METHOD
    def GetFacility(self, facilityID, prime = True):
        if facilityID:
            if self.loadedRegion is None:
                self._PrimeFacilities()
            if prime and facilityID not in self.facilities:
                self._PrimeFacility(self.facilityManager.GetFacility(facilityID))
            return self.facilities[facilityID]

    def GetMaxActivityModifier(self, activityID = None):
        self.InitMaxActivityModifiers()
        if activityID:
            return self.maxActivityModifiers.get(activityID, 1.0)
        else:
            return max(self.maxActivityModifiers.values()) or 1.0

    def InitMaxActivityModifiers(self):
        if self.maxActivityModifiers is None:
            self.maxActivityModifiers = self.facilityManager.GetMaxActivityModifiers()

    def GetFacilityTaxes(self, facilityID):
        return self.facilityManager.GetFacilityTaxes(facilityID, session.corpid)

    def SetFacilityTaxes(self, facilityID, taxRateValues):
        self.facilityManager.SetFacilityTaxes(facilityID, session.corpid, taxRateValues)

    def Reload(self, facilityID = None):
        if facilityID is None:
            self.facilities.clear()
            self.loadedRegion = None
        else:
            self.facilities.pop(facilityID, None)
            self._PrimeFacility(self.facilityManager.GetFacility(facilityID))
        sm.ScatterEvent('OnFacilitiesReloaded', {facilityID})

    def GetFreshFacility(self, facilityID):
        with self.loading:
            if facilityID in self.facilities and self.facilities[facilityID].rigModifiers:
                del self.facilities[facilityID]
        return self.GetFacility(facilityID)

    @Memoize(1)
    def GetFacilityLocations(self, facilityID, ownerID):
        if facilityID is None:
            return []
        locations = self.facilityManager.GetFacilityLocations(facilityID, ownerID)
        cfg.evelocations.Prime(set([ location.itemID for location in locations if location.typeID != typeOffice ]))
        return locations

    def IsFacility(self, itemID):
        self._PrimeFacilities()
        if itemID in self.facilities:
            return True
        return False

    def _PrimeFacilities(self, force = False):
        with self.loading:
            if not force and self.loadedRegion == session.regionid:
                return
            self.facilities.clear()
            for data in self.facilityManager.GetFacilities():
                self._PrimeFacility(data)

            cfg.eveowners.Prime(set([ facility.ownerID for facility in self.facilities.itervalues() ]))
            cfg.evelocations.Prime(set([ facility.facilityID for facility in self.facilities.itervalues() ]))
            self.loadedRegion = session.regionid

    def _PrimeFacility(self, data):
        facility = industryCommon.Facility(data)
        self.facilities[facility.facilityID] = facility
        self._UpdateFacilityDistance(facility)

    def _UpdateFacilityDistance(self, facility):
        facility.distance = self.clientPathfinderService.GetJumpCountFromCurrent(facility.solarSystemID)
