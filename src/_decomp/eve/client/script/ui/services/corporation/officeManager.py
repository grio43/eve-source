#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\corporation\officeManager.py
import log
from carbon.common.script.net.moniker import Moniker
from carbon.common.script.sys.service import Service
from eve.common.script.sys.idCheckers import IsNPCCorporation
REMOTESVC = 'officeManager'

class OfficeManager(Service):
    __guid__ = 'svc.officeManager'
    __servicename__ = 'Office Manager'
    __displayname__ = 'Office Manager'
    __dependencies__ = []
    __notifyevents__ = ['DoSessionChanging', 'OnOfficeRentalChange', 'OnSessionChanged']

    def __init__(self):
        super(self.__class__, self).__init__()
        self._offices = None
        self._corp_offices = None
        self._station = None

    @property
    def offices(self):
        stationID = session.stationid or session.structureid
        if not stationID:
            return []
        if self._offices is None:
            self._offices = self.station.GetCorporationsWithOffices()
            cfg.eveowners.Prime(self._offices)
        return self._offices

    @property
    def corp_offices(self):
        if self._corp_offices is None:
            self._corp_offices = sm.RemoteSvc(REMOTESVC).GetMyCorporationsOffices()
            cfg.evelocations.Prime({o.stationID for o in self._corp_offices})
        return self._corp_offices

    @property
    def station(self):
        if self._station is None:
            stationID = session.stationid or session.structureid
            if stationID:
                self._station = Moniker(REMOTESVC, stationID)
                self._station.SetSessionCheck({'stationid': session.stationid,
                 'structureid': session.structureid})
                self._station.isPrimed = False
        return self._station

    def DoSessionChanging(self, isRemote, session, change):
        if {'stationid', 'structureid'} & set(change):
            self._offices = self._station = None

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' in change:
            self._corp_offices = None
        if {'stationid', 'structureid'} & set(change):
            self._offices = self._station = None

    def OnOfficeRentalChange(self, corporationID, officeID):
        log.LogInfo('officeManager::OnOfficeRentalChange', corporationID, officeID, '- clearing station office cache.')
        self._offices = None
        if corporationID == session.corpid:
            log.LogInfo('officeManager::OnOfficeRentalChange', corporationID, officeID, '- clearing corporation office cache.')
            self._corp_offices = None
        log.LogInfo('officeManager::OnOfficeRentalChange', corporationID, officeID, '- notifying lobby window.')
        sm.ScatterEvent('OnOfficeRentalChanged', corporationID, officeID)

    def GetCorporationsWithOffices(self):
        return self.offices

    def GetMyCorporationsOffices(self):
        return self.corp_offices

    def GetMyCorporationsOffice(self, officeID):
        for office in self.GetMyCorporationsOffices():
            if office.officeID == officeID:
                return office

    def GetCorpOfficeAtLocation(self, locationID = None):
        stationID = locationID or session.stationid or session.structureid
        if stationID is None:
            return
        for office in self.corp_offices:
            if office.stationID == stationID:
                if locationID is None and not self.station.isPrimed:
                    self.station.isPrimed = True
                    self.station.PrimeOfficeItem()
                return office

    def GetPriceQuote(self):
        return self.station.GetPriceQuote(session.corpid)

    def RentOffice(self, cost):
        self.station.RentOffice(cost)

    def UnrentOffice(self):
        sm.GetService('objectCaching').InvalidateCachedMethodCall('corpmgr', 'GetAssetInventoryForLocation', session.corpid, session.stationid or session.structureid, 'offices')
        self.station.UnrentOffice()

    def UnrentRemoteOffice(self, stationID):
        if stationID in (session.stationid, session.structureid):
            self.UnrentOffice()
        else:
            Moniker(REMOTESVC, stationID).UnrentOffice()

    def GetNumberOfUnrentedOffices(self):
        if session.structureid:
            return None
        return self.station.GetEmptyOfficeCount()

    def HasCorpImpoundedItemsAtStation(self):
        if IsNPCCorporation(session.corpid):
            return False
        if self.GetCorpOfficeAtLocation():
            return False
        return self.station.HasCorpImpoundedItems()

    def GetImpoundReleasePrice(self):
        if not self.HasCorpImpoundedItemsAtStation():
            return None
        return self.station.GetImpoundReleasePrice()

    def GetItemsFromImpound(self, quotedPrice):
        self.station.GetItemsFromImpound(quotedPrice)

    @staticmethod
    def TrashImpoundAtStation(stationID):
        Moniker(REMOTESVC, stationID).TrashImpoundedOffice()
