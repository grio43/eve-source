#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\data\evolution.py
from eveProto.generated.eve_public.sovereignty.mercenaryden.evolution_pb2 import Evolution
from logging import getLogger
from sovereignty.mercenaryden.client.data.evolution_definition import EvolutionDefinitionInfo
from sovereignty.mercenaryden.client.data.evolution_simulation import EvolutionSimulationInfo
logger = getLogger('mercenary_den')

class EvolutionInfo(object):

    @property
    def development_level(self):
        return self._simulation.development_level

    @property
    def development_stage(self):
        return self._simulation.development_stage

    @property
    def development_unit_increase_time_seconds(self):
        return self._definition.development_unit_increase_time_seconds

    @property
    def development_level_bands_by_stage(self):
        return self._definition.development_level_bands_by_stage

    @property
    def anarchy_level(self):
        return self._simulation.anarchy_level

    @property
    def anarchy_stage(self):
        return self._simulation.anarchy_stage

    @property
    def anarchy_unit_increase_time_seconds(self):
        return self._definition.anarchy_unit_increase_time_seconds

    @property
    def anarchy_level_bands_by_stage(self):
        return self._definition.anarchy_level_bands_by_stage

    @property
    def anarchy_workforce_consumption_by_stage(self):
        return self._definition._anarchy_workforce_consumption_by_stage

    @property
    def definition(self):
        return self._definition

    @definition.setter
    def definition(self, value):
        self._definition = value

    @property
    def simulation(self):
        return self._simulation

    @simulation.setter
    def simulation(self, value):
        self._simulation = value

    def __init__(self, definition, simulation):
        self._definition = definition
        self._simulation = simulation

    def __repr__(self):
        return '<EvolutionInfo definition=%s simulation=%s' % (self._definition, self._simulation)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (self._definition, self._simulation) == (other._definition, other._simulation)

    def __ne__(self, other):
        return not self == other

    @classmethod
    def create_from_proto(cls, evolution):
        return EvolutionInfo(definition=EvolutionDefinitionInfo.create_from_proto(evolution.definition), simulation=EvolutionSimulationInfo.create_from_proto(evolution.simulation))

    def get_proto(self):
        anarchy_stages = list(set(self.anarchy_level_bands_by_stage.keys()).intersection(self.anarchy_workforce_consumption_by_stage.keys()))
        return Evolution(definition=self._definition.get_proto(), simulation=self._simulation.get_proto())

    def get_level_bands_for_current_development_stage(self):
        try:
            return self.development_level_bands_by_stage[self.development_stage]
        except KeyError:
            logger.exception('Failed to find development level bands for stage %s', self.development_stage)
            return (None, None)

    def get_level_bands_for_current_anarchy_stage(self):
        try:
            return self.anarchy_level_bands_by_stage[self.anarchy_stage]
        except KeyError:
            logger.exception('Failed to find anarchy level bands for stage %s', self.anarchy_stage)
            return (None, None)

    def get_current_workforce_cost(self):
        return self.get_workforce_cost_by_anarchy_stage(self.anarchy_stage)

    def get_workforce_cost_by_anarchy_stage(self, anarchy_stage):
        try:
            workforce_cost = self.anarchy_workforce_consumption_by_stage[anarchy_stage]
        except KeyError:
            logger.exception('Failed to find workforce cost for anarchy stage %s', anarchy_stage)
            return 0

        return workforce_cost
