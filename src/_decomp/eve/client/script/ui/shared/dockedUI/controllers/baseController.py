#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\controllers\baseController.py
from eve.client.script.environment.invControllers import StationCorpHangar
from eve.client.script.ui.shared.inventory.invConst import GetInventoryContainerClass
from eve.client.script.ui.station import stationServiceConst
from eve.common.lib import appConst as const
from eve.common.script.sys.idCheckers import IsStation
from utillib import KeyVal
from globalConfig.getFunctions import IsContentComplianceControlSystemActive

class BaseStationController(object):

    def __init__(self, itemID = None):
        self.serviceAccessCache = {}
        self.officeManager = sm.GetService('officeManager')

    @property
    def corpOffice(self):
        return self.officeManager.GetCorpOfficeAtLocation()

    def Undock(self):
        sm.GetService('undocking').UndockBtnClicked()

    def ChangeDockedMode(self, viewState):
        pass

    def CorpsWithOffices(self):
        return self.officeManager.GetCorporationsWithOffices()

    def GetNumberOfUnrentedOffices(self):
        return self.officeManager.GetNumberOfUnrentedOffices()

    def CanRent(self):
        return self._HasRole(const.corpRoleCanRentOffice)

    def CanMoveHQ(self):
        return self._HasRole(const.corpRoleDirector)

    def CanUnrent(self):
        return self._HasRole(const.corpRoleDirector)

    def IsHqAllowed(self):
        return True

    def _HasRole(self, corpRole):
        return session.corprole & corpRole == corpRole

    def IsMyHQ(self):
        return False

    def MyCorpIsOwner(self):
        return False

    def GetCostForOpeningOffice(self):
        return self.officeManager.GetPriceQuote()

    def RentOffice(self, cost):
        self.officeManager.RentOffice(cost)

    def GetMyCorpOffice(self):
        return self.corpOffice

    def IsEmptyOffice(self):
        return len(StationCorpHangar(divisionID=None).GetItems()) == 0

    def UnrentOffice(self):
        self.officeManager.UnrentOffice()

    def SetHQ(self):
        pass

    def GetCostForGettingCorpJunkBack(self):
        return self.officeManager.GetImpoundReleasePrice()

    def ReleaseImpoundedItems(self, cost):
        self.officeManager.GetItemsFromImpound(cost)

    def GetServices(self):
        if IsStation(self.itemID):
            return self.GetServicesInStation()
        else:
            return self.GetServicesInStructure()

    def GetGuests(self):
        return {}

    def PerformAndGetErrorForStandingCheck(self, stationServiceID):
        return None

    def RemoveServiceFromCache(self, serviceID):
        pass

    def GetAgents(self):
        return []

    def GetOwnerID(self):
        return None

    def HasCorpItemsImpounded(self):
        return self.officeManager.HasCorpImpoundedItemsAtStation()

    def GetStationItemsAndShipsClasses(self):
        return (None, None)

    def GetShipInventoryClass(self):
        return GetInventoryContainerClass(self._GetShipInventoryType())

    def GetItemInventoryClass(self):
        return GetInventoryContainerClass(self._GetItemInventoryType())

    def _GetShipInventoryType(self):
        return None

    def _GetItemInventoryType(self):
        return None

    def GetItemID(self):
        return None

    def InProcessOfUndocking(self):
        return False

    def HasDockModes(self):
        return False

    def IsExiting(self):
        return sm.GetService('undocking').IsExiting()

    def GetDisabledDockingModeHint(self):
        return None

    def GetDockedModeTextPath(self, viewName = None):
        return None

    def GetCurrentStateForService(self, serviceID):
        return KeyVal(isEnabled=True)

    def _GetServiceInfoAvailable(self, servicesAtLocation):
        haveServices = []
        for serviceData in stationServiceConst.serviceData:
            if not serviceData.command:
                continue
            if serviceData.name == 'charcustomization' and IsContentComplianceControlSystemActive(sm.GetService('machoNet')):
                continue
            if stationServiceConst.serviceIDAlwaysPresent in serviceData.stationServiceIDs:
                haveServices.append(serviceData)
            elif serviceData.serviceID in servicesAtLocation:
                haveServices.append(serviceData)

        return haveServices

    def IsControlable(self):
        return False

    def TakeControl(self):
        pass

    def MayTakeControl(self, structureID):
        return False

    def GetStructurePilot(self, structureID):
        return None
