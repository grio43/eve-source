#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\data\infomorphs.py
from eveProto.generated.eve_public.sovereignty.mercenaryden.infomorph.itemtype.identifier_pb2 import Identifier as InfomorphTypeIdentifier
from eveProto.generated.eve_public.sovereignty.mercenaryden.infomorphs_pb2 import Infomorphs, InfomorphsContents, InfomorphsGenerationDefinition
from eveProto.monolith_converters.time import timestamp_to_blue

class InfomorphsDefinition(object):

    def __init__(self, type_id, capacity, generation_rate_tick_seconds, generation_rates):
        self._type_id = type_id
        self._capacity = capacity
        self._generation_rate_tick_seconds = generation_rate_tick_seconds
        self._generation_rates = generation_rates

    @property
    def capacity(self):
        return self._capacity

    @property
    def generation_rates(self):
        return self._generation_rates

    @property
    def generation_rate_tick_seconds(self):
        return self._generation_rate_tick_seconds

    @property
    def type_id(self):
        return self._type_id

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (self.capacity,
         self.type_id,
         self.generation_rates,
         self.generation_rate_tick_seconds) == (other.capacity,
         other.type_id,
         other.generation_rates,
         other.generation_rate_tick_seconds)

    def __ne__(self, other):
        return not self == other

    @classmethod
    def create_from_proto(cls, definition_proto):
        return InfomorphsDefinition(capacity=int(definition_proto.cargo_capacity), generation_rates={int(band.stage):(band.lower_band, band.upper_band) for band in definition_proto.generation_bands}, generation_rate_tick_seconds=int(definition_proto.generation_tick_seconds), type_id=int(definition_proto.infomorph_type.sequential))

    def get_proto(self):
        return InfomorphsGenerationDefinition(infomorph_type=InfomorphTypeIdentifier(sequential=self.type_id), generation_tick_seconds=self.generation_rate_tick_seconds, generation_bands=[ InfomorphsGenerationDefinition.GenerationBand(stage=stage, lower_band=band[0], upper_band=band[1]) for stage, band in self.generation_rates.iteritems() ], cargo_capacity=self.capacity)


class InfomorphsInfo(object):

    @property
    def count(self):
        return self._count

    @property
    def capacity(self):
        return self._definition.capacity

    @property
    def generation_rates(self):
        return self._definition.generation_rates

    @property
    def generation_rate_tick_seconds(self):
        return self._definition.generation_rate_tick_seconds

    @property
    def last_generation_tick(self):
        return timestamp_to_blue(self._last_generation_tick)

    @property
    def type_id(self):
        return self._definition.type_id

    def set_definition(self, definition):
        self._definition = definition

    def __init__(self, count, last_generation_tick, definition):
        self._count = count
        self._last_generation_tick = last_generation_tick
        self._definition = definition

    def __repr__(self):
        return '<InfomorphsInfo count=%s capacity=%s generation_rates=%s generation_rate_tick_seconds=%s type_id=%s>' % (self.count,
         self.capacity,
         self.generation_rates,
         self.generation_rate_tick_seconds,
         self.type_id)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (self.last_generation_tick, self.count, self._definition) == (other.last_generation_tick, other.count, other._definition)

    def __ne__(self, other):
        return not self == other

    @classmethod
    def create_from_proto(cls, infomorphs):
        return InfomorphsInfo(count=int(infomorphs.contents.infomorphs_count), definition=InfomorphsDefinition.create_from_proto(infomorphs.definition), last_generation_tick=infomorphs.contents.last_generation_tick)

    def get_proto(self):
        return Infomorphs(definition=self._definition.get_proto(), contents=InfomorphsContents(infomorphs_count=self.count, last_generation_tick=self._last_generation_tick))
