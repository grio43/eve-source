#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemissions\client\mission.py
import blue
from agentinteraction.reward import Reward, RewardType
from eve.common.lib.appConst import agentMissionStateAllocated, agentMissionStateOffered, agentMissionStateAccepted, agentMissionStateCompleted, agentMissionStateDeclined, agentMissionStateQuit, agentMissionStateCantReplay, agentMissionStateFailed, agentTypeHeraldry
from evedungeons.client.util import GetDungeonShipRestrictions
from evemissions.client.objectives import ObjectiveState, ObjectivesType, TalkToAgentObjective, CargoObjective, PickUpObjective, DropOffObjective, DungeonObjective, ShipRestrictions
from evemissions.client.const import CAREER_PATH_BY_DIVISION
from evemissions.client.data import get_mission, has_standing_rewards
from evemissions.client.data import get_fixed_lp_rewards
from inventorycommon.const import typeLoyaltyPoints, typeLoyaltyPointsHeraldry, typeResearch
import log
_dungeon_restrictions = {}

class Mission(object):

    def __init__(self, mission_id, agent_id, state = None, actions = None, expiration_time = None, is_important = False):
        self.mission_id = mission_id
        self.agent_id = agent_id
        self.expiration_time = expiration_time
        self.state = state
        self.briefing = None
        self.special_interactions = None
        self.timer = None
        self.accept_time = None
        self.time_left = None
        self.objectives = []
        self.objectives_type = None
        self.objective_info = None
        self.actions = actions or []
        self.is_important = is_important
        self.is_cheat_complete = False
        self.dungeon_id = None
        self._mission = get_mission(mission_id)
        self._agent = None
        self.granted_items = []
        self.normal_rewards = []
        self.bonus_rewards = []
        self.collateral = []
        self.ship_restrictions = None

    @property
    def name(self):
        return getattr(self._mission, 'nameID', None)

    @property
    def agent(self):
        if self._agent is None:
            self._agent = self.agent_service.GetAgentByID(self.agent_id)
        return self._agent

    @property
    def division_id(self):
        return self.agent.divisionID

    @property
    def career_path_id(self):
        return CAREER_PATH_BY_DIVISION.get(self.division_id, None)

    @property
    def level(self):
        return self.agent.level

    @property
    def corporation_id(self):
        return self.agent.corporationID

    @property
    def faction_id(self):
        return self.agent.factionID

    @property
    def agent_type_id(self):
        return self.agent.agentTypeID

    @property
    def content_tag_ids(self):
        return self._mission.contentTags or []

    def is_accepted(self):
        return self.state == agentMissionStateAccepted

    def is_offered(self):
        return self.state in [agentMissionStateAllocated, agentMissionStateOffered]

    def is_completed(self):
        return self.state == agentMissionStateCompleted

    def is_disabled(self):
        return self.agent_service.IsMissionDisabled(self.mission_id)

    def can_replay(self):
        return self.state != agentMissionStateCantReplay

    def is_active(self):
        if self.state is None:
            return False
        return self.state not in [agentMissionStateCompleted,
         agentMissionStateDeclined,
         agentMissionStateQuit,
         agentMissionStateCantReplay]

    def is_expired(self):
        if not self.expiration_time:
            return False
        return self.expiration_time - blue.os.GetWallclockTime() < 0

    def has_expiration_time(self):
        return bool(self.expiration_time) and self.is_active() and not self.is_expired()

    def update_info(self, briefing, special_interactions = None, timer = None, accept_time = None, time_left = None):
        self.briefing = briefing
        self.special_interactions = special_interactions
        self.timer = timer
        self.accept_time = accept_time
        self.time_left = time_left

    def update_state(self, state):
        self.state = state

    def mark_as_important(self):
        self.is_important = True

    def mark_as_cheat_complete(self):
        self.is_cheat_complete = True

    def get_message_id(self, message_id):
        return self._mission.messages.get(message_id, None)

    def get_standings(self):
        return self._mission.extraStandings

    def get_ship_restrictions(self):
        if not self.dungeon_id:
            return None
        return GetDungeonShipRestrictions(self.dungeon_id)

    def can_run_in_current_ship(self):
        if self.agent_type_id == agentTypeHeraldry:
            return True
        restrictions = self.get_ship_restrictions()
        if not restrictions:
            return True
        ship_type_id, ship_group_id = _get_current_ship_info()
        if ship_type_id in restrictions.restrictedShipTypes:
            return False
        if ship_type_id in restrictions.allowedShipTypes:
            return True
        return True

    def has_standing_rewards(self):
        return has_standing_rewards(self.mission_id)

    def update_objective_info(self, objective_info):
        if objective_info.get('contentID', None) != self.mission_id:
            return
        self.objective_info = objective_info
        self._update_objectives(objective_info)
        self._update_rewards(objective_info)

    def _update_objectives(self, objective_info):
        if objective_info.get('importantStandings', False):
            self.mark_as_important()
        mission_state = objective_info.get('missionState', None)
        completion_status = objective_info.get('completionStatus', 0)
        is_cheat_complete = completion_status == 2
        is_mission_failed = mission_state == agentMissionStateFailed
        self.update_state(mission_state)
        if is_cheat_complete:
            self.mark_as_cheat_complete()
        objectives_type = None
        objectives = []
        for objective_type, objective_data in objective_info.get('objectives', []):
            objectives += _build_objective_entries(objective_type, objective_data)
            objectives_type = objective_type

        for dungeon_data in objective_info.get('dungeons', []):
            if is_mission_failed:
                dungeon_data['completionStatus'] = 0
                dungeon_data['objectiveCompleted'] = 0
            objective = _build_dungeon_objective(dungeon_data, self.agent_id, self.agent_service)
            if objective:
                self.ship_restrictions = objective.ship_restrictions
                self.dungeon_id = objective.dungeon_id
                objectives.append(objective)
            if objectives_type is None:
                objectives_type = ObjectivesType.DUNGEON

        self.objectives = objectives or []
        self.objectives_type = objectives_type

    def _update_rewards(self, objective_info):
        self.granted_items = _build_granted_items(objective_info)
        self.normal_rewards = _build_normal_rewards(objective_info, self.mission_id, self.agent_type_id)
        self.bonus_rewards = _build_bonus_rewards(objective_info, self.accept_time)
        self.collateral = _build_collateral(objective_info)

    @property
    def agent_service(self):
        return sm.GetService('agents')


def _build_objective_entries(objective_type, objective_data):
    try:
        if objective_type == ObjectivesType.TALK_TO_AGENT:
            return _build_talk_to_agent_objectives(objective_data)
        if objective_type == ObjectivesType.TRANSPORT:
            return _build_transport_objectives(objective_data)
        if objective_type == ObjectivesType.FETCH:
            return _build_fetch_objectives(objective_data)
        log.LogError('Trying to construct unknown objective type {}'.format(objective_type))
    except:
        log.LogException('Failed to construct objective type {}'.format(objective_type))

    return []


def _build_talk_to_agent_objectives(objective_data):
    agent_id, location = objective_data
    objective = TalkToAgentObjective(agent_id, location, state=ObjectiveState.IN_PROGRESS)
    return [objective]


def _build_transport_objectives(objective_data):
    objectives = []
    _, pickup, _, dropoff, cargo = objective_data
    type_id = cargo['typeID']
    quantity = cargo['quantity']
    volume = cargo['volume']
    has_cargo = cargo['hasCargo']
    pickup_location = pickup.get('locationID', None)
    dropoff_location = dropoff.get('locationID', None)
    is_at_pickup_location = pickup_location == session.locationid
    is_at_dropoff_location = dropoff_location == session.locationid
    is_pickup_complete = is_at_pickup_location or has_cargo
    is_dropoff_complete = is_at_dropoff_location and is_pickup_complete
    state = ObjectiveState.COMPLETED if has_cargo else ObjectiveState.IN_PROGRESS
    objective = CargoObjective(type_id, quantity, volume, state)
    objectives.append(objective)
    state = ObjectiveState.COMPLETED if is_pickup_complete else ObjectiveState.IN_PROGRESS
    objective = PickUpObjective(location=pickup, state=state)
    objectives.append(objective)
    state = ObjectiveState.COMPLETED if is_dropoff_complete else ObjectiveState.IN_PROGRESS
    objective = DropOffObjective(location=dropoff, state=state)
    objectives.append(objective)
    return objectives


def _build_fetch_objectives(objective_data):
    objectives = []
    _, dropoff, cargo = objective_data
    type_id = cargo['typeID']
    quantity = cargo['quantity']
    volume = cargo['volume']
    has_cargo = cargo['hasCargo']
    dropoff_location = dropoff.get('locationID', None)
    is_at_dropoff_location = dropoff_location == session.locationid
    is_pickup_complete = has_cargo
    is_dropoff_complete = is_at_dropoff_location and is_pickup_complete
    state = ObjectiveState.COMPLETED if has_cargo else ObjectiveState.IN_PROGRESS
    objective = CargoObjective(type_id, quantity, volume, state)
    objectives.append(objective)
    state = ObjectiveState.COMPLETED if is_dropoff_complete else ObjectiveState.IN_PROGRESS
    objective = DropOffObjective(location=dropoff, state=state)
    objectives.append(objective)
    return objectives


def _build_dungeon_objective(dungeon_data, agent_id, agent_service):
    completion_data = dungeon_data.get('objectiveCompleted', None)
    state = ObjectiveState.IN_PROGRESS
    if completion_data == 0:
        state = ObjectiveState.FAILED
    elif completion_data == 1:
        state = ObjectiveState.COMPLETED
    ship_restriction_data = dungeon_data.get('shipRestrictions', None)
    ship_restrictions = ShipRestrictions.NONE
    if ship_restriction_data == 0:
        ship_restrictions = ShipRestrictions.NORMAL
    elif ship_restriction_data == 1:
        ship_restrictions = ShipRestrictions.SPECIAL
    is_killing_optional = bool(dungeon_data.get('optional', False))
    briefing = dungeon_data.get('briefingMessage', None)
    if briefing is not None:
        briefing = agent_service.ProcessMessage(briefing, agent_id)
    location = dungeon_data.get('location', None)
    dungeon_id = dungeon_data['dungeonID']
    return DungeonObjective(dungeon_id, ship_restrictions, is_killing_optional, briefing, location, state)


def _build_granted_items(objective_info):
    granted_items = []
    try:
        for type_id, quantity, extra in objective_info.get('agentGift', []):
            reward = Reward(RewardType.GRANTED, type_id, quantity, extra)
            granted_items.append(reward)

    except KeyError:
        pass

    return granted_items


def _build_normal_rewards(objective_info, mission_id, agent_type_id):
    normal_rewards = []
    try:
        for type_id, quantity, extra in objective_info.get('normalRewards', []):
            reward = Reward(RewardType.NORMAL, type_id, quantity, extra)
            normal_rewards.append(reward)

        lp = objective_info.get('loyaltyPoints', 0)
        if lp > 0:
            fixed_alpha_lp, fixed_omega_lp = get_fixed_lp_rewards(mission_id)
            type_id = typeLoyaltyPointsHeraldry if agent_type_id == agentTypeHeraldry else typeLoyaltyPoints
            reward = Reward(RewardType.NORMAL, type_id, lp, alpha_quantity=fixed_alpha_lp, omega_quantity=fixed_omega_lp)
            normal_rewards.append(reward)
        rp = round(objective_info.get('researchPoints', 0), 0)
        if rp > 0:
            reward = Reward(RewardType.NORMAL, typeResearch, rp)
            normal_rewards.append(reward)
    except KeyError:
        pass

    return normal_rewards


def _build_bonus_rewards(objective_info, mission_accepted_time):
    bonus_rewards = []
    try:
        for time_remaining, type_id, quantity, extra, timeBonusIntervalMin in objective_info.get('bonusRewards', []):
            reward = Reward(RewardType.BONUS, type_id, quantity, extra, timeBonusIntervalMin, mission_accepted_time)
            bonus_rewards.append(reward)

    except KeyError:
        pass

    return bonus_rewards


def _build_collateral(objective_info):
    collateral = []
    try:
        for type_id, quantity, extra in objective_info.get('collateral', []):
            reward = Reward(RewardType.COLLATERAL, type_id, quantity, extra)
            collateral.append(reward)

    except KeyError:
        pass

    return collateral


def _get_current_ship_info():
    ship_id = session.shipid
    if ship_id is not None:
        ship = sm.GetService('invCache').GetInventoryFromId(ship_id).GetItem()
        if ship:
            return (ship.typeID, ship.groupID)
    return (None, None)
