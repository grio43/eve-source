#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\mocks\data.py
from google.protobuf.timestamp_pb2 import Timestamp
from sovereignty.mercenaryden.client.data.evolution import EvolutionInfo
from sovereignty.mercenaryden.client.data.evolution_definition import EvolutionDefinitionInfo
from sovereignty.mercenaryden.client.data.evolution_simulation import EvolutionSimulationInfo
from sovereignty.mercenaryden.client.data.infomorphs import InfomorphsInfo, InfomorphsDefinition
from sovereignty.mercenaryden.client.data.mercenary_den import MercenaryDenInfo
SKYHOOK_ID = 1000000269697L
PLANET_ID = 40294748
DEN_TYPE_ID = 85230

def create_mercenary_den_mock(item_id, character_id, solar_system_id, skyhook_owner_id):
    return MercenaryDenInfo(item_id=item_id, type_id=DEN_TYPE_ID, owner_id=character_id, skyhook_id=SKYHOOK_ID, solar_system_id=solar_system_id, planet_id=PLANET_ID, is_enabled=True, infomorphs_info=create_infomorphs_mock(), evolution_info=create_evolution_mock(), is_cargo_extraction_enabled=True, skyhook_owner_id=skyhook_owner_id)


def create_infomorphs_mock():
    return InfomorphsInfo(count=100, definition=InfomorphsDefinition(type_id=85746, capacity=170000, generation_rates={1: (85, 115),
     2: (97, 132),
     3: (106, 143),
     4: (114, 155),
     5: (127, 172)}, generation_rate_tick_seconds=3600), last_generation_tick=_get_timestamp(seconds_ago=5))


def create_evolution_mock():
    return EvolutionInfo(definition=create_evolution_definition_mock(), simulation=create_evolution_simulation_mock())


def create_evolution_definition_mock():
    return EvolutionDefinitionInfo(development_unit_increase_time_seconds=17280, development_level_bands_by_stage={1: (0, 19),
     2: (20, 39),
     3: (40, 69),
     4: (70, 99),
     5: (100, 100)}, anarchy_unit_increase_time_seconds=17280, anarchy_level_bands_by_stage={1: (0, 19),
     2: (20, 39),
     3: (40, 69),
     4: (70, 99),
     5: (100, 100)}, anarchy_workforce_consumption_by_stage={1: 0,
     2: 0,
     3: 886,
     4: 1772,
     5: 3544})


def create_evolution_simulation_mock():
    is_paused = True
    if is_paused:
        return EvolutionSimulationInfo(development_level=36, development_stage=2, anarchy_level=41, anarchy_stage=3, is_paused=is_paused, development_last_paused_at=_get_timestamp(seconds_ago=5), anarchy_last_paused_at=_get_timestamp(seconds_ago=5))


def _get_timestamp(seconds_ago = 0):
    current_timestamp = Timestamp()
    current_timestamp.GetCurrentTime()
    return Timestamp(seconds=current_timestamp.ToSeconds() - seconds_ago)
