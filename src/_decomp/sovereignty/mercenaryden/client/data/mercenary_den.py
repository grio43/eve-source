#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\data\mercenary_den.py
from eveProto.generated.eve_public.character.character_pb2 import Identifier as CharacterIdentifier
from eveProto.generated.eve_public.planet.skyhook.skyhook_pb2 import Identifier as SkyhookIdentifier
from eveProto.generated.eve_public.solarsystem.solarsystem_pb2 import Identifier as SolarSystemIdentifier
from eveProto.generated.eve_public.planet.planet_pb2 import Identifier as PlanetIdentifier
from eveProto.generated.eve_public.sovereignty.mercenaryden.mercenaryden_type_pb2 import Identifier as MercenaryDenTypeID
from eveProto.generated.eve_public.sovereignty.mercenaryden.mercenaryden_pb2 import Attributes as MercenaryDenAttributes
from logging import getLogger
from sovereignty.mercenaryden.client.data.evolution import EvolutionInfo
from sovereignty.mercenaryden.client.data.infomorphs import InfomorphsInfo
logger = getLogger('mercenary_den')

class MercenaryDenInfo(object):

    @property
    def item_id(self):
        return self._item_id

    @property
    def type_id(self):
        return self._type_id

    @property
    def owner_id(self):
        return self._owner_id

    @property
    def skyhook_id(self):
        return self._skyhook_id

    @property
    def solar_system_id(self):
        return self._solar_system_id

    @property
    def planet_id(self):
        return self._planet_id

    @property
    def is_enabled(self):
        return self._is_enabled

    @property
    def infomorphs(self):
        return self._infomorphs_info.count

    @property
    def infomorphs_info(self):
        return self._infomorphs_info

    @property
    def evolution_info(self):
        return self._evolution_info

    @evolution_info.setter
    def evolution_info(self, value):
        self._evolution_info = value

    @property
    def is_cargo_extraction_enabled(self):
        return self._is_cargo_extraction_enabled

    @property
    def is_evolution_paused(self):
        return self.evolution_info.simulation.is_paused

    @property
    def skyhook_owner_id(self):
        return self._skyhook_owner_id

    def __init__(self, item_id, type_id, owner_id, skyhook_id, solar_system_id, planet_id, is_enabled, infomorphs_info, evolution_info, is_cargo_extraction_enabled, skyhook_owner_id):
        self._item_id = item_id
        self._type_id = type_id
        self._owner_id = owner_id
        self._skyhook_id = skyhook_id
        self._solar_system_id = solar_system_id
        self._planet_id = planet_id
        self._is_enabled = is_enabled
        self._infomorphs_info = infomorphs_info
        self._evolution_info = evolution_info
        self._is_cargo_extraction_enabled = is_cargo_extraction_enabled
        self._skyhook_owner_id = skyhook_owner_id

    def __repr__(self):
        return '<MercenaryDenInfo item_id=%s owner_id=%s skyhook_id=%s solar_system_id=%s is_enabled=%s, infomorphs=%s, evolution=%s, skyhook_owner_id=%s>' % (self.item_id,
         self.owner_id,
         self.skyhook_id,
         self.solar_system_id,
         self.is_enabled,
         self.infomorphs_info,
         self.evolution_info,
         self.skyhook_owner_id)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.item_id == other.item_id and self.type_id == other.type_id and self.owner_id == other.owner_id and self.skyhook_id == other.skyhook_id and self.solar_system_id == other.solar_system_id and self.planet_id == other.planet_id and self.is_enabled == other.is_enabled and self.infomorphs_info == other.infomorphs_info and self.evolution_info == other.evolution_info and self.skyhook_owner_id == other.skyhook_owner_id

    def __ne__(self, other):
        return not self == other

    @classmethod
    def create_from_proto(cls, item_id, attributes, is_enabled, evolution, infomorphs, is_cargo_extraction_enabled, skyhook_owner):
        return MercenaryDenInfo(item_id=item_id, type_id=attributes.type.sequential, owner_id=attributes.owner.sequential, skyhook_id=attributes.skyhook.sequential, solar_system_id=attributes.solar_system.sequential, planet_id=attributes.planet.sequential, is_enabled=is_enabled, infomorphs_info=InfomorphsInfo.create_from_proto(infomorphs), evolution_info=EvolutionInfo.create_from_proto(evolution), is_cargo_extraction_enabled=is_cargo_extraction_enabled, skyhook_owner_id=skyhook_owner.sequential)

    def get_proto_for_attributes(self):
        return MercenaryDenAttributes(type=MercenaryDenTypeID(sequential=self.type_id), owner=CharacterIdentifier(sequential=self.owner_id), skyhook=SkyhookIdentifier(sequential=self.skyhook_id), solar_system=SolarSystemIdentifier(sequential=self.solar_system_id), planet=PlanetIdentifier(sequential=self.planet_id))

    def get_proto_for_infomorphs(self):
        return self._infomorphs_info.get_proto()

    def get_proto_for_evolution(self):
        return self._evolution_info.get_proto()

    def get_current_infomorph_generation_rates_per_second(self):
        lower_per_tick, upper_per_tick = self.get_current_infomorph_generation_rates_per_tick()
        lower_per_second = self._convert_from_tick_to_seconds(lower_per_tick)
        upper_per_second = self._convert_from_tick_to_seconds(upper_per_tick)
        return (lower_per_second, upper_per_second)

    def get_current_infomorph_generation_rates_per_tick(self):
        development_stage = self._evolution_info.development_stage
        return self._get_infomorph_generation_rates_per_tick_by_development_stage(development_stage)

    def get_infomorph_generation_rates_per_second_by_development_stage(self, development_stage):
        lower_per_tick, upper_per_tick = self._get_infomorph_generation_rates_per_tick_by_development_stage(development_stage)
        lower_per_second = self._convert_from_tick_to_seconds(lower_per_tick)
        upper_per_second = self._convert_from_tick_to_seconds(upper_per_tick)
        return (lower_per_second, upper_per_second)

    def _get_infomorph_generation_rates_per_tick_by_development_stage(self, development_stage):
        if self._infomorphs_info.generation_rate_tick_seconds <= 0:
            return (0, 0)
        try:
            lower_per_tick, upper_per_tick = self._infomorphs_info.generation_rates[development_stage]
        except KeyError:
            logger.exception('Failed to find infomorph generation rates for development stage %s', development_stage)
            return (0, 0)

        return (lower_per_tick, upper_per_tick)

    def _convert_from_tick_to_seconds(self, infomorph_generation_rate):
        if self._infomorphs_info.generation_rate_tick_seconds <= 0:
            return 0.0
        return float(infomorph_generation_rate) / self._infomorphs_info.generation_rate_tick_seconds
