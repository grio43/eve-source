#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\controllers\stationController.py
import blue
import carbonui.const as uiconst
from eve.client.script.ui.shared.dockedUI.controllers.baseController import BaseStationController
from eve.client.script.ui.shared.inventory.invConst import ContainerType
from eve.client.script.ui.station import stationServiceConst
from eve.common.lib import appConst
from eve.common.script.util.structuresCommon import GetServices
import structures
import sys

class StationController(BaseStationController):

    def __init__(self, itemID = None):
        BaseStationController.__init__(self)
        self.corpStationMgr = None
        self.itemID = self.stationID = itemID

    def IsMyHQ(self):
        return sm.GetService('corp').GetCorporation().stationID == session.stationid

    def SetHQ(self):
        if eve.Message('MoveHQHere', {}, uiconst.YESNO) == uiconst.ID_YES:
            sm.GetService('corp').GetCorpStationManager().MoveCorpHQHere()

    def GetServicesInStation(self):
        stationItem = sm.GetService('station').stationItem
        servicesAtStation = GetServices(session.solarsystemid2, stationItem)
        haveServices = self._GetServiceInfoAvailable(servicesAtStation)
        for serviceData in stationServiceConst.serviceData:
            if serviceData not in haveServices:
                continue
            if serviceData.serviceID == structures.SERVICE_FACTION_WARFARE:
                if not sm.GetService('facwar').CheckStationElegibleForMilitia():
                    haveServices.remove(serviceData)
            elif serviceData.serviceID == structures.SERVICE_SECURITY_OFFICE:
                if not sm.GetService('securityOfficeSvc').CanAccessServiceInStation(session.stationid):
                    haveServices.remove(serviceData)

        return haveServices

    def GetGuests(self):
        return sm.GetService('station').GetGuests()

    def PerformAndGetErrorForStandingCheck(self, stationServiceID):
        time, result = self._GetResultFromCache(stationServiceID)
        now = blue.os.GetWallclockTime()
        if time and time + const.MIN * 5 > now:
            return result
        try:
            self._DoStandingCheckForServices(stationServiceID)
            result = None
        except Exception as e:
            sys.exc_clear()
            result = e

        self._AddServiceToCache(stationServiceID, now, result)
        return result

    def _DoStandingCheckForServices(self, stationServiceID):
        if stationServiceID in (appConst.stationServiceCloning,
         appConst.stationServiceSurgery,
         appConst.stationServiceDNATherapy,
         appConst.stationServiceJumpCloneFacility,
         appConst.stationServiceNavyOffices):
            return
        if self.corpStationMgr is None:
            self.corpStationMgr = sm.GetService('corp').GetCorpStationManager()
        self.corpStationMgr.DoStandingCheckForStationService(stationServiceID)

    def _AddServiceToCache(self, serviceID, timestamp, error):
        self.serviceAccessCache[serviceID] = (timestamp, error)

    def RemoveServiceFromCache(self, serviceID):
        if serviceID in self.serviceAccessCache:
            del self.serviceAccessCache[serviceID]

    def _GetResultFromCache(self, serviceID):
        if serviceID in self.serviceAccessCache:
            time, result = self.serviceAccessCache[serviceID]
            return (time, result)
        return (None, None)

    def GetAgents(self):
        return sm.GetService('agents').GetAgentsByStationID()[session.stationid]

    def GetOwnerID(self):
        return sm.GetService('station').stationItem.ownerID

    def _GetShipInventoryType(self):
        return ContainerType.STATION_SHIPS

    def _GetItemInventoryType(self):
        return ContainerType.STATION_ITEMS

    def GetItemID(self):
        return sm.GetService('station').stationItem.itemID

    def InProcessOfUndocking(self):
        return sm.GetService('undocking').PastUndockPointOfNoReturn()

    def GetDisabledDockingModeHint(self):
        return 'UI/Station/CannotEnterCaptainsQuarters'

    def IsControlable(self):
        return False
