#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\objectivetests.py
from evemissions.client.objectives import TalkToAgentObjective, CargoObjective, PickUpObjective, DropOffObjective, DungeonObjective, ObjectivesType, ObjectiveState, ShipRestrictions
TEST_LOCATION_SOLAR_SYSTEM = {'solarsystemID': 30005316,
 'locationID': 30005316,
 'typeID': 5}
TEST_LOCATION_STATION = {'solarsystemID': 30005316,
 'locationID': 60011521,
 'typeID': 1930}
TEST_OBJECTIVE_SETS = {ObjectivesType.TALK_TO_AGENT: [TalkToAgentObjective(agent_id=3009789, location=TEST_LOCATION_STATION, state=ObjectiveState.IN_PROGRESS)],
 ObjectivesType.TRANSPORT: [CargoObjective(type_id=35, quantity=200, volume=1.0, state=ObjectiveState.COMPLETED), PickUpObjective(location=TEST_LOCATION_STATION, state=ObjectiveState.COMPLETED), DropOffObjective(location=TEST_LOCATION_STATION, state=ObjectiveState.IN_PROGRESS)],
 ObjectivesType.FETCH: [CargoObjective(type_id=35, quantity=200, volume=1.0, state=ObjectiveState.COMPLETED), DropOffObjective(location=TEST_LOCATION_STATION, state=ObjectiveState.IN_PROGRESS)],
 ObjectivesType.DUNGEON: [DungeonObjective(dungeon_id=213, ship_restrictions=ShipRestrictions.SPECIAL, is_killing_optional=True, briefing='This is a test dungeon briefing', location=TEST_LOCATION_SOLAR_SYSTEM, state=ObjectiveState.IN_PROGRESS)]}
