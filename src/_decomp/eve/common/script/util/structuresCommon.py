#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\structuresCommon.py
import evetypes
import structures
from caching.memoize import Memoize
from eve.common.lib import appConst as const
from evestations.data import get_station_services_for_operation
from evestations.data import service_in_station_operation
from eveuniverse.security import is_high_security_solar_system
from structures.types import IsFlexStructure
MAX_STRUCTURE_BIO_LENGTH = 1000
STATION_SERVICE_MAPPING = {const.stationServiceBountyMissions: structures.SERVICE_MISSION,
 const.stationServiceAssassinationMissions: structures.SERVICE_MISSION,
 const.stationServiceCourierMission: structures.SERVICE_MISSION,
 const.stationServiceInterbus: None,
 const.stationServiceReprocessingPlant: structures.SERVICE_REPROCESSING,
 const.stationServiceRefinery: structures.SERVICE_REPROCESSING,
 const.stationServiceMarket: structures.SERVICE_MARKET,
 const.stationServiceBlackMarket: None,
 const.stationServiceStockExchange: None,
 const.stationServiceCloning: structures.SERVICE_MEDICAL,
 const.stationServiceSurgery: structures.SERVICE_MEDICAL,
 const.stationServiceDNATherapy: structures.SERVICE_MEDICAL,
 const.stationServiceRepairFacilities: structures.SERVICE_REPAIR,
 const.stationServiceFactory: structures.SERVICE_INDUSTRY,
 const.stationServiceLaboratory: structures.SERVICE_INDUSTRY,
 const.stationServiceGambling: None,
 const.stationServiceFitting: structures.SERVICE_FITTING,
 const.stationServiceNews: None,
 const.stationServiceStorage: None,
 const.stationServiceInsurance: structures.SERVICE_INSURANCE,
 const.stationServiceDocking: structures.SERVICE_DOCKING,
 const.stationServiceOfficeRental: structures.SERVICE_OFFICES,
 const.stationServiceJumpCloneFacility: structures.SERVICE_JUMP_CLONE,
 const.stationServiceLoyaltyPointStore: structures.SERVICE_LOYALTY_STORE,
 const.stationServiceNavyOffices: structures.SERVICE_FACTION_WARFARE,
 const.stationServiceSecurityOffice: structures.SERVICE_SECURITY_OFFICE}
STRUCTURE_VISIBILITY_SETTINGIDS = {const.groupUpwellCynoBeacon: (structures.SETTING_CYNO_BEACON, structures.SETTING_DEFENSE_CAN_CONTROL_STRUCTURE),
 const.groupUpwellCynoJammer: (structures.SETTING_DEFENSE_CAN_CONTROL_STRUCTURE,),
 const.groupUpwellJumpGate: (structures.SETTING_JUMP_BRIDGE_ACTIVATION, structures.SETTING_DEFENSE_CAN_CONTROL_STRUCTURE)}

def GetStationService(serviceID):
    return STATION_SERVICE_MAPPING.get(serviceID)


@Memoize
def GetSettingIdControllingVisibility(typeID):
    defaultSettingIDs = (structures.SETTING_HOUSING_CAN_DOCK,)
    if not IsFlexStructure(typeID):
        return defaultSettingIDs
    return STRUCTURE_VISIBILITY_SETTINGIDS.get(evetypes.GetGroupID(typeID), defaultSettingIDs)


def IsRepairServiceAvailable(solarSystemID):
    return solarSystemID and is_high_security_solar_system(solarSystemID)


def IsStationServiceAvailable(solarSystemID, stationItem, serviceID):
    if serviceID == const.stationServiceRepairFacilities:
        if IsRepairServiceAvailable(solarSystemID):
            return True
    return service_in_station_operation(stationItem.operationID, serviceID)


def GetStationServices(solarSystemID, stationItem):
    servicesAtStation = set(get_station_services_for_operation(stationItem.operationID))
    if IsStationServiceAvailable(solarSystemID, stationItem, const.stationServiceRepairFacilities):
        servicesAtStation.add(const.stationServiceRepairFacilities)
    return servicesAtStation


def GetServices(solarSystemID, stationItem):
    services = set()
    for serviceID in GetStationServices(solarSystemID, stationItem):
        services.add(STATION_SERVICE_MAPPING.get(serviceID))

    services.discard(None)
    return services
