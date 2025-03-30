#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\skyhook\client\notice_listener.py
from eveProto.generated.eve_public.sovereignty.skyhook.api.notices_pb2 import ReagentSimulationsNotice, ReagentDefinitionsNotice, AllInSolarSystemNotice, TheftVulnerabilityWindowStartedNotice, TheftVulnerabilityWindowEndedNotice, TheftVulnerabilityWindowScheduledNotice, ActivationNotice, WorkforceChangedNotice
from signals import Signal
from sovereignty.resource.client.data_types import HarvestSplitSimulationState, ReagentProductionSplitDynamicData, ReagentDefinition
from semantic_version import SemanticVersion
from sovereignty.skyhook.data_type import get_skyhook_object
import logging
logger = logging.getLogger('skyhook')

class ExternalNoticeListener(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(ReagentSimulationsNotice, self._on_reagent_simulation_notice)
        self.public_gateway.subscribe_to_notice(ReagentDefinitionsNotice, self._on_reagent_definition_notice)
        self.public_gateway.subscribe_to_notice(AllInSolarSystemNotice, self._on_all_in_system_notice)
        self.public_gateway.subscribe_to_notice(TheftVulnerabilityWindowScheduledNotice, self._on_theft_vulnerability_window_scheduled_notice)
        self.public_gateway.subscribe_to_notice(TheftVulnerabilityWindowStartedNotice, self._on_theft_vulnerability_window_started_notice)
        self.public_gateway.subscribe_to_notice(TheftVulnerabilityWindowEndedNotice, self._on_theft_vulnerability_window_ended_notice)
        self.public_gateway.subscribe_to_notice(ActivationNotice, self._on_activation_changed_notice)
        self.public_gateway.subscribe_to_notice(WorkforceChangedNotice, self._on_workforce_changed_notice)
        self.on_reagent_simulation_notice = Signal()
        self.on_reagent_definition_notice = Signal()
        self.on_all_in_system_notice = Signal()
        self.on_theft_vulnerability_window_scheduled_notice = Signal()
        self.on_theft_vulnerability_window_started_notice = Signal()
        self.on_theft_vulnerability_window_ended_notice = Signal()
        self.on_activation_changed_notice = Signal()
        self.on_workforce_changed_notice = Signal()

    def _on_workforce_changed_notice(self, payload, *args, **kwargs):
        logger.info('_on_workforce_changed_notice %s', payload)
        skyhook_id = payload.skyhook.sequential
        workforce = payload.workforce
        self.on_workforce_changed_notice(skyhook_id, workforce)

    def _on_reagent_simulation_notice(self, payload, *args, **kwargs):
        planet_id = payload.planet.sequential
        skyhook_id = payload.skyhook.sequential
        reagent_production_data_list = []
        for simulation in payload.simulations:
            reagent_production_data = ReagentProductionSplitDynamicData(simulation.reagent_type.sequential, HarvestSplitSimulationState.create_from_proto(simulation.simulation))
            reagent_production_data_list.append(reagent_production_data)

        self.on_reagent_simulation_notice(planet_id, skyhook_id, reagent_production_data_list)

    def _on_reagent_definition_notice(self, payload, *args, **kwargs):
        planet_id = payload.planet.sequential
        skyhook_id = payload.skyhook.sequential
        resource_version = SemanticVersion.from_proto(payload.planet_resources_definitions_version)
        reagent_definitions = []
        for definition in payload.definition:
            reagent_production_data = ReagentDefinition.create_from_proto(definition.reagent_type.sequential, definition.definition)
            reagent_definitions.append(reagent_production_data)

        self.on_reagent_definition_notice(planet_id, skyhook_id, reagent_definitions, resource_version)

    def _on_all_in_system_notice(self, payload, *args, **kwargs):
        logger.info('_on_all_in_system_notice %s', payload)
        solar_system_id = payload.solar_system.sequential
        if session.solarsystemid2 != solar_system_id:
            return
        skyhooks = []
        for skyhook in payload.skyhooks:
            vulnerability_data = None
            if skyhook.WhichOneof('vulnerability') == 'theft_vulnerability':
                vulnerability_data = skyhook.theft_vulnerability
            workforce = None
            effective_workforce = skyhook.effective_workforce
            if effective_workforce.WhichOneof('available') == 'amount':
                workforce = effective_workforce.amount
            resource_version = SemanticVersion.from_proto(skyhook.planet_resources_definitions_version)
            skyhook = get_skyhook_object(skyhook.skyhook.sequential, skyhook.active, skyhook.reagent_simulations, skyhook.reagent_definitions, vulnerability_data, workforce, resource_version)
            skyhooks.append(skyhook)

        self.on_all_in_system_notice(solar_system_id, skyhooks)

    def _on_theft_vulnerability_window_scheduled_notice(self, payload, *args, **kwargs):
        logger.info('_on_theft_vulnerability_window_scheduled_notice %s', payload)
        skyhook_id = payload.skyhook.sequential
        start_datetime = payload.start_time.ToDatetime()
        end_datetime = payload.end_time.ToDatetime()
        self.on_theft_vulnerability_window_scheduled_notice(skyhook_id, start_datetime, end_datetime)

    def _on_theft_vulnerability_window_started_notice(self, payload, *args, **kwargs):
        logger.info('_on_theft_vulnerability_window_started_notice %s', payload)
        skyhook_id = payload.skyhook.sequential
        end_datetime = payload.end_time.ToDatetime()
        self.on_theft_vulnerability_window_started_notice(skyhook_id, end_datetime)

    def _on_theft_vulnerability_window_ended_notice(self, payload, *args, **kwargs):
        logger.info('_on_theft_vulnerability_window_ended_notice %s', payload)
        skyhook_id = payload.skyhook.sequential
        self.on_theft_vulnerability_window_ended_notice(skyhook_id)

    def _on_activation_changed_notice(self, payload, *args, **kwargs):
        logger.info('_on_activation_changed_notice %s', payload)
        skyhook_id = payload.skyhook.sequential
        self.on_activation_changed_notice(skyhook_id, payload.active)
