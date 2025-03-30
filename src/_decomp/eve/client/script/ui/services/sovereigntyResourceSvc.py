#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\sovereigntyResourceSvc.py
import logging
import traceback
import uthread
from caching import Memoize
from carbon.common.script.sys.service import Service
from gametime import GetWallclockTime
from publicGateway.grpc.exceptions import GenericException
from sovereignty.resource.client.data_sources import ConfigurationDataSource, get_current_planetary_data, get_versioned_planetary_data
from sovereignty.resource.client.reagent_split_production_simulation import get_next_split_harvest_time_and_amount, get_reagent_split_production_data_at_time, get_next_split_amounts
from sovereignty.resource.shared.planetary_resources_cache import DataUnavailableError, PlanetaryResourcesCache, TTL
from sovereignty.skyhook.client.data_sources import SkyhooksLocalDataSource
from sovereignty.resource.client.messenger import SovereigntyResourceMessenger, FakeResourceExternalMessenger
from sovereignty.skyhook.client.notice_listener import ExternalNoticeListener as SkyhookNoticeListener
from sovereignty.hub.client.notice_listener import ExternalNoticeListener as HubNoticeListener
from sovereignty.skyhook.client.errors import SkyhookAccessForbiddenError, SkyhookNotFoundError
from sovereignty.skyhook.client.messenger import SkyhookMessenger, FakeSkyhookMessenger
from spacecomponents.client.components.orbitalSkyhook import UpdateSkyhookOnReagentsUpdated, UpdateSkyhookOnTheftVulnerabilityChanged
from stackless_response_router.exceptions import TimeoutException
logger = logging.getLogger(__name__)

class SovereigntyResourceSvc(Service):
    __guid__ = 'svc.sovereigntyResourceSvc'
    __servicename__ = 'Sovereignty Resources'
    __displayname__ = 'Sovereignty Resources Service'
    __startupdependencies__ = ['publicGatewaySvc']
    __notifyevents__ = ['OnSessionChanged', 'OnSkyhookFirstActivation']
    sovResourceMessenger = None
    planetProductionStaticData = None
    localSkyhooksData = None
    skyhookNoticeListener = None
    hubNoticeListener = None
    skyhookMessenger = None

    def __init__(self):
        super(SovereigntyResourceSvc, self).__init__()

    def Run(self, memStream = None):
        super(SovereigntyResourceSvc, self).Run(memStream=memStream)
        USE_FAKE_DATA = False
        if USE_FAKE_DATA:
            self.sovResourceMessenger = FakeResourceExternalMessenger()
            self.skyhookMessenger = FakeSkyhookMessenger()
        else:
            self.sovResourceMessenger = SovereigntyResourceMessenger(self.publicGatewaySvc)
            self.skyhookMessenger = SkyhookMessenger(self.publicGatewaySvc)
        planet_data_cache = PlanetaryResourcesCache(lambda current_version: get_current_planetary_data(self.sovResourceMessenger, current_version), lambda version: get_versioned_planetary_data(self.sovResourceMessenger, version), TTL)
        self.planetProductionStaticData = ConfigurationDataSource(self.sovResourceMessenger, planet_data_cache)
        self.localSkyhooksData = SkyhooksLocalDataSource(self.skyhookMessenger)
        self.skyhookNoticeListener = SkyhookNoticeListener(self.publicGatewaySvc)
        self.skyhookNoticeListener.on_reagent_simulation_notice.connect(self._OnReagentSimUpdatedNotice)
        self.skyhookNoticeListener.on_reagent_definition_notice.connect(self._OnReagentDefinitionUpdatedNotice)
        self.skyhookNoticeListener.on_theft_vulnerability_window_started_notice.connect(self._OnTheftVulnerabilityWindowStartedNotice)
        self.skyhookNoticeListener.on_theft_vulnerability_window_ended_notice.connect(self._OnTheftVulnerabilityWindowEndedNotice)
        self.skyhookNoticeListener.on_theft_vulnerability_window_scheduled_notice.connect(self._OnTheftVulnerabilityWindowScheduledNotice)
        self.skyhookNoticeListener.on_all_in_system_notice.connect(self._OnAllInSystemNotice)
        self.skyhookNoticeListener.on_activation_changed_notice.connect(self._OnActivationChangedNotice)
        self.skyhookNoticeListener.on_workforce_changed_notice.connect(self._OnWorkforceChanged)
        self.localSkyhooksData.on_theft_vulnerability_status_changed.connect(self._OnCachedTheftVulnerabilityStatusChanged)
        self.hubNoticeListener = HubNoticeListener(self.publicGatewaySvc)
        self.hubNoticeListener.on_resources_simulated_notice.connect(self._OnResourcesSimulatedNotice)

    def OnSessionChanged(self, isRemove, sess, change):
        if 'solarsystemid2' in change:
            self.localSkyhooksData.on_solarsystem_changed(sess.solarsystemid2)
            self.GetMyCorporationSkyhooksMemoized.clear_memoized()

    def OnSkyhookFirstActivation(self, skyhookID, planetID):
        self.localSkyhooksData.flush_all_data()
        vulnerability_data = self.GetTheftVulnerabilityForSkyhook(skyhookID)
        vulnerable = vulnerability_data and vulnerability_data.vulnerable
        UpdateSkyhookOnTheftVulnerabilityChanged(skyhookID, is_vulnerable_to_theft=vulnerable)

    def _OnReagentSimUpdatedNotice(self, planetID, skyhookID, reagent_production_data_list):
        self.localSkyhooksData.update_skyhook_simulations(skyhookID, reagent_production_data_list)
        sm.ScatterEvent('OnReagentsUpdated', planetID, skyhookID)
        UpdateSkyhookOnReagentsUpdated(planetID, skyhookID)

    def _OnReagentDefinitionUpdatedNotice(self, planetID, skyhookID, reagent_production_data_list, resource_version):
        self.localSkyhooksData.update_skyhook_configurations(skyhookID, reagent_production_data_list, resource_version)
        sm.ScatterEvent('OnReagentsUpdated', planetID, skyhookID)
        UpdateSkyhookOnReagentsUpdated(planetID, skyhookID)

    def _OnAllInSystemNotice(self, solar_system_id, skyhook_data):
        self.localSkyhooksData.flush_all_data()
        self.localSkyhooksData.prime_from_notice(solar_system_id, skyhook_data)

    def _OnTheftVulnerabilityWindowStartedNotice(self, skyhookID, end_datetime):
        self.localSkyhooksData.update_skyhook_vulnerability_endtime(skyhookID, end_datetime, True)

    def _OnTheftVulnerabilityWindowEndedNotice(self, skyhookID):
        self.localSkyhooksData.update_skyhook_vulnerability(skyhookID, False)

    def _OnTheftVulnerabilityWindowScheduledNotice(self, skyhookID, start_datetime, end_datetime):
        self.localSkyhooksData.update_skyhook_vulnerability_schedule(skyhookID, start_datetime, end_datetime)

    def _OnCachedTheftVulnerabilityStatusChanged(self, skyhookID, vulnerability_data):
        vulnerable = vulnerability_data is not None and vulnerability_data.vulnerable
        UpdateSkyhookOnTheftVulnerabilityChanged(skyhookID, is_vulnerable_to_theft=vulnerable)

    def _OnWorkforceChanged(self, skyhookID, workforce):
        self.localSkyhooksData.update_workforce(skyhookID, workforce)

    def _OnResourcesSimulatedNotice(self, hubID, solarsystemID, availableHubResources):
        sm.ScatterEvent('OnSovHubResourcesSimulated', hubID, solarsystemID, availableHubResources)

    def _OnActivationChangedNotice(self, skyhookID, activationStatus):
        self.localSkyhooksData.update_skyhook_activation_status(skyhookID, activationStatus)

    def GetPlanetReagentType(self, planetID, version = None):
        production_data = self.planetProductionStaticData.get_first_reagent_definition(planetID, version)
        if production_data is not None:
            return production_data.type_id

    def GetPlanetReagentMaxAmounts(self, planetID, version = None):
        production_data = self.planetProductionStaticData.get_first_reagent_definition(planetID, version)
        if production_data is not None:
            return (production_data.split_configuration.secure_capacity, production_data.split_configuration.insecure_capacity)
        return (0, 0)

    def GetPlanetReagentAmountAndPeriod(self, planetID, version = None):
        productionData = self.planetProductionStaticData.get_first_reagent_definition(planetID, version)
        if productionData is not None:
            return (productionData.split_configuration.amount_per_period, productionData.split_configuration.period)
        return (0, 0)

    def GetAllPlanetPowerProduction(self, version = None):
        return self.planetProductionStaticData.get_all_power_production(version)

    def GetPlanetPowerProduction(self, planetID, version = None):
        return self.planetProductionStaticData.get_power_production(planetID, version)

    def GetAllPlanetWorkforceProduction(self, version = None):
        return self.planetProductionStaticData.get_all_workforce_production(version)

    def GetPlanetWorkforceProduction(self, planetID, version = None):
        return self.planetProductionStaticData.get_workforce_production(planetID, version)

    def IsProductionActiveAtSkyhook(self, skyhookID):
        return self.localSkyhooksData.get_skyhook(skyhookID).active

    def ActivateSkyhook(self, skyhookID):
        return self.skyhookMessenger.activate(skyhookID)

    def DeactivateSkyhook(self, skyhookID):
        return self.skyhookMessenger.deactivate(skyhookID)

    def GetReagentsInSkyhookNow(self, skyhookID):
        skyhook = self.localSkyhooksData.get_skyhook(skyhookID)
        if skyhook and len(skyhook.reagent_data) > 0:
            now = GetWallclockTime()
            production_data_now = get_reagent_split_production_data_at_time(skyhook.get_first_simulation(), skyhook.get_first_configuration(), now)
            secure_amount = production_data_now.secure_amount
            insecure_amount = production_data_now.insecure_amount
            return (secure_amount, insecure_amount)
        return (None, None)

    def GetNextReagentHarvestTimeAndAmount(self, skyhookID):
        skyhook = self.localSkyhooksData.get_skyhook(skyhookID)
        if skyhook:
            first_simulation = skyhook.get_first_simulation()
            first_configuration = skyhook.get_first_configuration()
            if first_simulation and first_configuration:
                nextHarvestTime, amount, bothFull = get_next_split_harvest_time_and_amount(first_simulation, first_configuration, GetWallclockTime())
                return (nextHarvestTime, amount, bothFull)
        return (None, None, False)

    def GetNextReagentHarvestAmounts(self, skyhookID):
        skyhook = self.localSkyhooksData.get_skyhook(skyhookID)
        if skyhook:
            first_simulation = skyhook.get_first_simulation()
            first_configuration = skyhook.get_first_configuration()
            if first_simulation and first_configuration:
                secured, unsecured = get_next_split_amounts(first_simulation, first_configuration, GetWallclockTime())
                return (secured, unsecured)
        return (None, None)

    def GetNextHarvestPeriod(self, skyhookID):
        skyhook = self.localSkyhooksData.get_skyhook(skyhookID)
        if skyhook:
            first_configuration = skyhook.get_first_configuration()
            return first_configuration.period

    def PrimeStaticDataForPlanets(self):
        return self.planetProductionStaticData.prime_data()

    def GetPlanetResourceInfoParallel(self, planetID, version = None):
        parallelCalls = [(self.GetPlanetReagentType, (planetID, version)),
         (self.GetPlanetReagentAmountAndPeriod, (planetID, version)),
         (self.GetPlanetPowerProduction, (planetID, version)),
         (self.GetPlanetWorkforceProduction, (planetID, version))]
        reagentTypeID, reagentAmountsInfo, power, workforce = uthread.parallel(parallelCalls)
        return (reagentTypeID,
         reagentAmountsInfo,
         power,
         workforce)

    def GetPlanetResourceInfo(self, planetID, version = None):
        power = None
        workforce = None
        reagentAmountsInfo = None
        reagentTypeID = self.GetPlanetReagentType(planetID, version)
        if reagentTypeID:
            reagentAmountsInfo = self.GetPlanetReagentAmountAndPeriod(planetID, version)
        if not reagentTypeID:
            power = self.GetPlanetPowerProduction(planetID, version)
            if not power:
                workforce = self.GetPlanetWorkforceProduction(planetID, version)
        return (reagentTypeID,
         reagentAmountsInfo,
         power,
         workforce)

    def GetAvailableHubResources(self, hubID):
        return self.sovResourceMessenger.get_available_hub_resources(hubID)

    def GetMaxPowerAndWorkforce(self, solarSystemID, version = None):
        solarSystemInfo = cfg.mapSystemCache.Get(solarSystemID)
        planetItemIDs = solarSystemInfo.planetItemIDs
        maxPower = 0
        maxWorkforce = 0
        for planetID in planetItemIDs:
            power = self.planetProductionStaticData.get_power_production(planetID, version)
            workforce = self.planetProductionStaticData.get_workforce_production(planetID, version)
            maxPower += max(power, 0)
            maxWorkforce += max(workforce, 0)

        starID = cfg.mapSolarSystemContentCache[solarSystemID].star.id
        starPower = self.planetProductionStaticData.get_power_production_for_star(starID)
        maxPower += max(starPower, 0)
        return (maxPower, maxWorkforce)

    def GetMyCorporationSkyhooks(self):
        return self.GetRemoteSvc().GetMyCorporationSkyhooks()

    @Memoize(5)
    def GetMyCorporationSkyhooksMemoized(self):
        return self.GetMyCorporationSkyhooks()

    def GetRemoteSvc(self):
        return sm.RemoteSvc('colonyResourcesMgr')

    def GetMyCorporationsSkyhookDetails(self):
        try:
            return self.skyhookMessenger.get_all_corporation(session.corpid)
        except (GenericException, TimeoutException) as e:
            raise DataUnavailableError(e)

    @Memoize(5)
    def GetMyCorporationsSkyhookDetailsMemoized(self):
        return self.GetMyCorporationsSkyhookDetails()

    @Memoize(5)
    def GetSolarSystemsWithTheftVulnerableSkyhooks(self):
        try:
            return self.skyhookMessenger.get_solar_systems_with_theft_vulnerable_skyhooks()
        except (GenericException, TimeoutException) as e:
            raise DataUnavailableError(e)

    def GetPlanetIDsAndTheftVulnerabilityExpiry(self, solarSystemID):
        vulnerability_data = self.skyhookMessenger.get_theft_vulnerable_skyhooks_in_solar_system(solarSystemID)
        expiry_by_planet = {data.planet_id:data.expiry for data in vulnerability_data}
        return expiry_by_planet

    def GetTheftVulnerabilityForSkyhook(self, skyhookID):
        try:
            local_skyhook_vulnerability_data = self.localSkyhooksData.get_skyhook_vulnerability(skyhookID)
        except SkyhookNotFoundError:
            local_skyhook_vulnerability_data = self._GetSkyhookData(skyhookID).vulnerability_data

        return local_skyhook_vulnerability_data

    def GetCurrentWorkforceForSkyhook(self, skyhookID):
        local_skyhook_workforce = self.localSkyhooksData.get_skyhook_workforce(skyhookID)
        if local_skyhook_workforce is not None:
            logger.info(local_skyhook_workforce)
            return local_skyhook_workforce
        workforce = self._GetSkyhookData(skyhookID).workforce
        return workforce

    def GetSkyhook(self, skyhookID):
        skyhook = self.localSkyhooksData.get_skyhook(skyhookID)
        if skyhook is not None:
            return skyhook
        return self._GetSkyhookData(skyhookID)

    def _GetSkyhookData(self, skyhookID):
        try:
            skyhook = self.skyhookMessenger.get(skyhookID)
        except (GenericException, TimeoutException, SkyhookAccessForbiddenError) as e:
            logger.warning('Failed to get skyhook data for skyhook %s - %s', skyhookID, traceback.format_exc())
            raise DataUnavailableError(e)

        return skyhook
