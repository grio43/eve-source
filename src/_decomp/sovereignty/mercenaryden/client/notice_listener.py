#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\notice_listener.py
import uuid
from eveProto.generated.eve_public.sovereignty.mercenaryden.activity.api.notices_pb2 import AddedNotice, ExpiryChangedNotice, StartedNotice, CompletedNotice, RemovedNotice
from eveProto.generated.eve_public.sovereignty.mercenaryden.api.notices_pb2 import EvolutionStateChangedNotice, DefinitionsUpdatedNotice
from signals import Signal
from sovereignty.mercenaryden.client.data.activity import MercenaryDenActivity
from sovereignty.mercenaryden.client.data.evolution_definition import EvolutionDefinitionInfo
from sovereignty.mercenaryden.client.data.evolution_simulation import EvolutionSimulationInfo
from sovereignty.mercenaryden.client.data.infomorphs import InfomorphsDefinition
import logging
logger = logging.getLogger('mercenary_den')

class CompletedActivity(object):

    def __init__(self, den_id, activity_id, development_impact, anarchy_impact, infomorph_bonus):
        self.den_id = den_id
        self.activity_id = activity_id
        self.development_impact = development_impact
        self.anarchy_impact = anarchy_impact
        self.infomorph_bonus = infomorph_bonus

    def __eq__(self, other):
        return self.den_id == other.den_id and self.activity_id == other.activity_id and self.development_impact == other.development_impact and self.infomorph_bonus == other.infomorph_bonus and self.anarchy_impact == other.anarchy_impact

    def __neg__(self, other):
        return not self.__eq__(other)


class ExternalNoticeListener(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(AddedNotice, self._on_added_notice)
        self.public_gateway.subscribe_to_notice(ExpiryChangedNotice, self._on_expiry_changed_notice)
        self.public_gateway.subscribe_to_notice(StartedNotice, self._on_started_notice)
        self.public_gateway.subscribe_to_notice(CompletedNotice, self._on_completed_notice)
        self.public_gateway.subscribe_to_notice(RemovedNotice, self._on_removed_notice)
        self.public_gateway.subscribe_to_notice(EvolutionStateChangedNotice, self._on_evolution_simulation_changed_notice)
        self.public_gateway.subscribe_to_notice(DefinitionsUpdatedNotice, self._on_mercenary_den_definitions_updated_notice)
        self.on_added_notice = Signal()
        self.on_expiry_changed_notice = Signal()
        self.on_started_notice = Signal()
        self.on_completed_notice = Signal()
        self.on_removed_notice = Signal()
        self.on_evolution_simulation_changed_notice = Signal()
        self.on_mercenary_den_definitions_updated_notice = Signal()

    def _on_added_notice(self, payload, *args, **kwargs):
        activity = MercenaryDenActivity.create_from_id_and_attributes_proto(uuid.UUID(bytes=payload.id.uuid), payload.activity)
        logger.info('MTO Notices - On Added %s to system %s', activity, payload.solar_system.sequential)
        self.on_added_notice(payload.solar_system.sequential, activity)

    def _on_expiry_changed_notice(self, payload, *args, **kwargs):
        activity = MercenaryDenActivity.create_from_id_and_attributes_proto(uuid.UUID(bytes=payload.id.uuid), payload.activity)
        logger.info('MTO Notices - On Expiry %s with previous expiry %s', activity, payload.previous_expiry.ToDatetime())
        self.on_expiry_changed_notice(payload.previous_expiry.ToDatetime(), activity)

    def _on_started_notice(self, payload, *args, **kwargs):
        activity = MercenaryDenActivity.create_from_id_and_attributes_proto(uuid.UUID(bytes=payload.id.uuid), payload.activity)
        logger.info('MTO Notices - On Started %s', activity)
        self.on_started_notice(activity)

    def _on_completed_notice(self, payload, *args, **kwargs):
        logger.info('MTO Notices - On Completed %s for merc den %s', uuid.UUID(bytes=payload.id.uuid), payload.mercenary_den.sequential)
        self.on_completed_notice(CompletedActivity(payload.mercenary_den.sequential, uuid.UUID(bytes=payload.id.uuid), payload.development_impact, payload.anarchy_impact, payload.infomorph_bonus))

    def _on_removed_notice(self, payload, *args, **kwargs):
        logger.info('MTO Notices - On Removed %s for merc den %s', uuid.UUID(bytes=payload.id.uuid), payload.mercenary_den.sequential)
        self.on_removed_notice(payload.mercenary_den.sequential, uuid.UUID(bytes=payload.id.uuid))

    def _on_evolution_simulation_changed_notice(self, payload, *args, **kwargs):
        mercenary_den_id = payload.mercenary_den.sequential
        new_simulation_simulation = EvolutionSimulationInfo.create_from_proto(payload.state)
        self.on_evolution_simulation_changed_notice(mercenary_den_id, new_simulation_simulation)

    def _on_mercenary_den_definitions_updated_notice(self, payload, *args, **kwargs):
        mercenary_den_id = payload.mercenary_den.sequential
        evolution_definition = EvolutionDefinitionInfo.create_from_proto(payload.evolution)
        infomorphs_definition = InfomorphsDefinition.create_from_proto(payload.infomorphs)
        self.on_mercenary_den_definitions_updated_notice(mercenary_den_id, evolution_definition, infomorphs_definition)
