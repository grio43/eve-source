#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\data\evolution_simulation.py
from eveProto.generated.eve_public.sovereignty.mercenaryden.evolution_pb2 import EvolutionSimulation, DevelopmentSimulation, AnarchySimulation
from eveProto.monolith_converters.time import timestamp_to_blue

class EvolutionSimulationInfo(object):

    @property
    def base_development_level(self):
        return self._base_development_level

    @property
    def development_level(self):
        return self._development_level

    @development_level.setter
    def development_level(self, value):
        self._development_level = value

    @property
    def development_stage(self):
        return self._development_stage

    @property
    def base_anarchy_level(self):
        return self._base_anarchy_level

    @property
    def anarchy_level(self):
        return self._anarchy_level

    @anarchy_level.setter
    def anarchy_level(self, value):
        self._anarchy_level = value

    @property
    def is_paused(self):
        return self._is_paused

    @property
    def development_last_paused_at(self):
        if self._development_last_paused_at:
            return timestamp_to_blue(self._development_last_paused_at)

    @property
    def anarchy_last_paused_at(self):
        if self._anarchy_last_paused_at:
            return timestamp_to_blue(self._anarchy_last_paused_at)

    @property
    def development_last_simulated_at(self):
        if self._development_last_simulated_at:
            return timestamp_to_blue(self._development_last_simulated_at)

    @property
    def anarchy_last_simulated_at(self):
        if self._anarchy_last_simulated_at:
            return timestamp_to_blue(self._anarchy_last_simulated_at)

    @property
    def anarchy_stage(self):
        return self._anarchy_stage

    def __init__(self, development_level, development_stage, anarchy_level, anarchy_stage, is_paused, development_last_paused_at = None, anarchy_last_paused_at = None, development_last_simulated_at = None, anarchy_last_simulated_at = None):
        self._base_development_level = development_level
        self._development_level = development_level
        self._development_stage = development_stage
        self._base_anarchy_level = anarchy_level
        self._anarchy_level = anarchy_level
        self._anarchy_stage = anarchy_stage
        self._is_paused = is_paused
        self._development_last_paused_at = development_last_paused_at
        self._anarchy_last_paused_at = anarchy_last_paused_at
        self._development_last_simulated_at = development_last_simulated_at
        self._anarchy_last_simulated_at = anarchy_last_simulated_at

    def __repr__(self):
        return '<EvolutionSimulationInfo development_level=%s development_stage=%s anarchy_level=%s anarchy_stage=%s>' % (self.development_level,
         self.development_stage,
         self.anarchy_level,
         self.anarchy_stage)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (self.development_level,
         self.development_stage,
         self.anarchy_level,
         self.anarchy_stage) == (other.development_level,
         other.development_stage,
         other.anarchy_level,
         other.anarchy_stage)

    def __ne__(self, other):
        return not self == other

    @classmethod
    def create_from_proto(cls, evolution_simulation):
        is_paused = evolution_simulation.paused
        if is_paused:
            return EvolutionSimulationInfo(development_level=evolution_simulation.development.level, development_stage=int(evolution_simulation.development.stage), anarchy_level=evolution_simulation.anarchy.level, anarchy_stage=int(evolution_simulation.anarchy.stage), is_paused=True, development_last_paused_at=evolution_simulation.development.paused_at, anarchy_last_paused_at=evolution_simulation.anarchy.paused_at)
        else:
            return EvolutionSimulationInfo(development_level=evolution_simulation.development.level, development_stage=int(evolution_simulation.development.stage), anarchy_level=evolution_simulation.anarchy.level, anarchy_stage=int(evolution_simulation.anarchy.stage), is_paused=False, development_last_simulated_at=evolution_simulation.development.simulated_at, anarchy_last_simulated_at=evolution_simulation.anarchy.simulated_at)

    def get_proto(self):
        if self.is_paused:
            return EvolutionSimulation(development=DevelopmentSimulation(level=self.development_level, stage=self.development_stage, paused_at=self._development_last_paused_at), anarchy=AnarchySimulation(level=self.anarchy_level, stage=self.anarchy_stage, paused_at=self._anarchy_last_paused_at), paused=True)
        else:
            return EvolutionSimulation(development=DevelopmentSimulation(level=self.development_level, stage=self.development_stage, simulated_at=self._development_last_simulated_at), anarchy=AnarchySimulation(level=self.anarchy_level, stage=self.anarchy_stage, simulated_at=self._anarchy_last_simulated_at), paused=False)
