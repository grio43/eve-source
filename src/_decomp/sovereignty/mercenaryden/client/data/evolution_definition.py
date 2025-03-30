#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\data\evolution_definition.py
from eveProto.generated.eve_public.sovereignty.mercenaryden.evolution_pb2 import EvolutionDefinition, DevelopmentDefinition, AnarchyDefinition

class EvolutionDefinitionInfo(object):

    @property
    def development_unit_increase_time_seconds(self):
        return self._development_unit_increase_time_seconds

    @property
    def development_level_bands_by_stage(self):
        return self._development_level_bands_by_stage

    @property
    def anarchy_unit_increase_time_seconds(self):
        return self._anarchy_unit_increase_time_seconds

    @property
    def anarchy_level_bands_by_stage(self):
        return self._anarchy_level_bands_by_stage

    @property
    def anarchy_workforce_consumption_by_stage(self):
        return self._anarchy_workforce_consumption_by_stage

    def __init__(self, development_unit_increase_time_seconds, development_level_bands_by_stage, anarchy_unit_increase_time_seconds, anarchy_level_bands_by_stage, anarchy_workforce_consumption_by_stage):
        self._development_unit_increase_time_seconds = development_unit_increase_time_seconds
        self._development_level_bands_by_stage = development_level_bands_by_stage
        self._anarchy_unit_increase_time_seconds = anarchy_unit_increase_time_seconds
        self._anarchy_level_bands_by_stage = anarchy_level_bands_by_stage
        self._anarchy_workforce_consumption_by_stage = anarchy_workforce_consumption_by_stage

    def __repr__(self):
        return '<EvolutionDefinitionInfo development_increase_seconds=%s development_level_bands=%s anarchy_increase_seconds=%s anarchy_level_bands=%s anarchy_workforce_by_stage=%s>' % (self.development_unit_increase_time_seconds,
         self.development_level_bands_by_stage,
         self.anarchy_unit_increase_time_seconds,
         self.anarchy_level_bands_by_stage,
         self.anarchy_workforce_consumption_by_stage)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (self.development_unit_increase_time_seconds,
         self.development_level_bands_by_stage,
         self.anarchy_unit_increase_time_seconds,
         self.anarchy_level_bands_by_stage,
         self.anarchy_workforce_consumption_by_stage) == (other.development_unit_increase_time_seconds,
         other.development_level_bands_by_stage,
         other.anarchy_unit_increase_time_seconds,
         other.anarchy_level_bands_by_stage,
         other.anarchy_workforce_consumption_by_stage)

    def __ne__(self, other):
        return not self == other

    @classmethod
    def create_from_proto(cls, evolution_definition):
        return EvolutionDefinitionInfo(development_unit_increase_time_seconds=evolution_definition.development.unit_increase_time_seconds, development_level_bands_by_stage={int(band.stage):(int(band.level_lower_bound), int(band.level_upper_bound)) for band in evolution_definition.development.stages}, anarchy_unit_increase_time_seconds=evolution_definition.anarchy.unit_increase_time_seconds, anarchy_level_bands_by_stage={int(band.stage):(int(band.level_lower_bound), int(band.level_upper_bound)) for band in evolution_definition.anarchy.stages}, anarchy_workforce_consumption_by_stage={int(band.stage):int(band.workforce_consumption) for band in evolution_definition.anarchy.stages})

    def get_proto(self):
        anarchy_stages = list(set(self.anarchy_level_bands_by_stage.keys()).intersection(self.anarchy_workforce_consumption_by_stage.keys()))
        return EvolutionDefinition(development=DevelopmentDefinition(unit_increase_time_seconds=self.development_unit_increase_time_seconds, stages=[ DevelopmentDefinition.DevelopmentStage(stage=stage, level_lower_bound=band[0], level_upper_bound=band[1]) for stage, band in self.development_level_bands_by_stage.iteritems() ]), anarchy=AnarchyDefinition(unit_increase_time_seconds=self.anarchy_unit_increase_time_seconds, stages=[ AnarchyDefinition.AnarchyStage(stage=stage, level_lower_bound=self.anarchy_level_bands_by_stage[stage][0], level_upper_bound=self.anarchy_level_bands_by_stage[stage][1], workforce_consumption=self.anarchy_workforce_consumption_by_stage[stage]) for stage in anarchy_stages ]))
