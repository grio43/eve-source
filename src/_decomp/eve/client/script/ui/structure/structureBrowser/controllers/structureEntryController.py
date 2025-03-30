#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\controllers\structureEntryController.py
from evePathfinder.core import IsUnreachableJumpCount
import eveformat.client
from eve.client.script.ui.structure.structureBrowser.controllers.reinforceTimersBundle import ReinforcementBundle
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.station import stationServiceConst
import evetypes
from localization import GetByLabel
from signals import Signal
import structures
from utillib import KeyVal

class StructureEntryController(object):

    def __init__(self, structureInfo):
        self.structureInfo = KeyVal(structureInfo)
        self.structureInfo.reinforceTimers = ReinforcementBundle(reinforceWeekday=structureInfo.get('reinforce_weekday'), reinforceHour=structureInfo.get('reinforce_hour'), nextReinforceWeekday=structureInfo.get('next_reinforce_weekday'), nextReinforceHour=structureInfo.get('next_reinforce_hour'), nextReinforceApply=structureInfo.get('next_reinforce_apply'))
        self.systemAndStructureName = None
        self.requiredHours = None
        self.filterText = None
        self.on_structure_state_changed = Signal(signalName='on_structure_state_changed')

    def GetNumJumps(self):
        jumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(self.GetSolarSystemID())
        return jumps

    def GetNumJumpsText(self):
        jumps = self.GetNumJumps()
        if IsUnreachableJumpCount(jumps):
            return '-'
        else:
            return jumps

    def GetSecurity(self):
        return sm.GetService('map').GetSecurityStatus(self.GetSolarSystemID())

    def GetSolarSystemID(self):
        return self.structureInfo.solarSystemID

    def GetSecurityWithColor(self):
        return eveformat.solar_system_security_status(self.GetSolarSystemID())

    def GetName(self):
        if self.systemAndStructureName:
            return self.systemAndStructureName
        locationName = cfg.evelocations.Get(self.GetSolarSystemID()).name
        structureName = cfg.evelocations.Get(self.GetItemID()).name
        solarsystemName = cfg.evelocations.Get(self.GetSolarSystemID()).name
        categoryID = evetypes.GetCategoryID(self.GetTypeID())
        if categoryID == const.categoryStation:
            stationInfo = cfg.stations.GetIfExists(self.GetItemID())
            if stationInfo:
                locationName = cfg.evelocations.Get(stationInfo.orbitID).name
                structureName = structureName.replace(locationName, '')
                structureName = structureName.replace(' - ', '', 1)
        elif categoryID == const.categoryStructure:
            if structureName.startswith(solarsystemName):
                structureName = structureName.replace('%s - ' % solarsystemName, '')
        if not structureName:
            structureName = evetypes.GetName(self.GetTypeID())
        solarsystemLink = GetShowInfoLink(const.typeSolarSystem, solarsystemName, self.GetSolarSystemID())
        locationName = locationName.replace(solarsystemName, solarsystemLink)
        systemAndStructureName = '<br>'.join([locationName, structureName])
        self.systemAndStructureName = systemAndStructureName
        return self.systemAndStructureName

    def GetFilterText(self):
        if self.filterText is not None:
            return self.filterText
        regionID = self.GetRegionID()
        regionText = cfg.evelocations.Get(regionID).name if regionID else ''
        textList = [self.GetCleanName(),
         self.GetOwnerName(),
         self.GetSystemName(),
         evetypes.GetName(self.GetTypeID()),
         regionText]
        text = ' '.join(textList)
        text = text.lower()
        self.filterText = text
        return text

    def GetCleanName(self):
        return cfg.evelocations.Get(self.GetItemID()).name

    def GetSystemName(self):
        return cfg.evelocations.Get(self.GetSolarSystemID()).name

    def GetOwnerID(self):
        return self.structureInfo.ownerID

    def GetOwnerName(self):
        return cfg.eveowners.Get(self.GetOwnerID()).name

    def GetTypeID(self):
        return self.structureInfo.typeID

    def GetItemID(self):
        return self.structureInfo.structureID

    def GetProfileID(self):
        return self.structureInfo.profileID

    def GetRegionID(self):
        regionID = sm.GetService('map').GetRegionForSolarSystem(self.GetSolarSystemID())
        return regionID

    def GetServices(self):
        return GetStuctureServices(self.GetSolarSystemID(), self.structureInfo.services, ownerID=self.GetOwnerID())

    def GetServicesAndOnlineStatus(self):
        return GetStuctureServicesAndOnlineStatus(self.GetSolarSystemID(), self.structureInfo.services, ownerID=self.GetOwnerID())

    def HasService(self, serviceID):
        if self.IsServiceAlwaysAvailable(serviceID):
            return True
        for eachService in self.GetServices():
            if eachService.name == serviceID:
                return True

        return False

    def IsServiceAlwaysAvailable(self, serviceID):
        serviceData = stationServiceConst.serviceDataByNameID.get(serviceID, None)
        if serviceData and serviceData.serviceID == stationServiceConst.serviceIDAlwaysPresent:
            return True
        return False

    def GetStateLabel(self):
        return GetByLabel(structures.STATE_LABELS.get(self.GetState(), '.unknown)'))

    def GetInfoForExtraColumns(self, serviceID):
        if serviceID in self.structureInfo.services:
            info = self.structureInfo.services.get(serviceID)
            return info

    def GetFuelExpiry(self):
        return self.structureInfo.fuelExpires

    def IsLowPower(self):
        return self.structureInfo.upkeepState == structures.UPKEEP_STATE_LOW_POWER

    def IsAbandoned(self):
        return self.structureInfo.upkeepState == structures.UPKEEP_STATE_ABANDONED

    def GetState(self):
        return self.structureInfo.state

    def GetTimerEnd(self):
        return self.structureInfo.timerEnd

    def GetReinforcementTime(self):
        return self.structureInfo.reinforceTimers.GetReinforcementTime()

    def GetNextReinforcementTime(self):
        return self.structureInfo.reinforceTimers.GetNextReinforcementTime()

    def GetGetNextApplyReinforcementTime(self):
        return self.structureInfo.reinforceTimers.GetNextApply()

    def CanUnanchor(self):
        if not session.corprole & const.corpRoleDirector:
            return False
        if structures.STATE_CANCELS_UNANCHOR.get(self.GetState()) is True:
            return False
        if not self.IsUnanchoring():
            return True
        return False

    def CanCancelUnanchor(self):
        if session.corprole & const.corpRoleDirector:
            if self.IsUnanchoring():
                return True
        return False

    def IsUnanchoring(self):
        return self.GetUnanchorTime() is not None

    def GetUnanchorTime(self):
        return self.structureInfo.unanchoring

    def StructureStateChanged(self, structureID, newStructureState):
        self.structureInfo.state = newStructureState
        self.on_structure_state_changed(structureID)

    def GetLiquidOzoneQty(self):
        return self.structureInfo.liquidOzoneQty

    def GetWars(self):
        return self.structureInfo.wars


def GetStuctureServices(solarSystemID, structureServices, ownerID):
    sortedServices, _ = GetStuctureServicesAndOnlineStatus(solarSystemID, structureServices, ownerID)
    return sortedServices


def GetStuctureServicesAndOnlineStatus(solarSystemID, structureServices, ownerID):
    if structureServices is None:
        return ([], {})
    sortServices = set()
    securitySvc = sm.GetService('securityOfficeSvc')
    onlineStatusByServiceID = {}
    for eachServiceID, eachServiceValue in structureServices.iteritems():
        onlineStatus = eachServiceValue
        if eachServiceID in structures.INDUSTRY_SERVICES:
            eachServiceID = structures.SERVICE_INDUSTRY
            if onlineStatusByServiceID.get(eachServiceID, None) == structures.SERVICE_STATE_ONLINE:
                onlineStatus = structures.SERVICE_STATE_ONLINE
        elif eachServiceID == structures.SERVICE_SECURITY_OFFICE:
            if ownerID not in const.stationOwnersWithSecurityService or not securitySvc.CanAccessServiceInSolarSystem(solarSystemID):
                continue
        serviceInfo = stationServiceConst.serviceDataByServiceID.get(eachServiceID, None)
        if serviceInfo is None:
            continue
        sortServices.add((serviceInfo.label, serviceInfo))
        onlineStatusByServiceID[eachServiceID] = onlineStatus

    if sortServices:
        sortServices = SortListOfTuples(sortServices)
    return (sortServices, onlineStatusByServiceID)
