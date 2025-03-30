#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemissions\client\missioncontroller.py
from agentinteraction.reward import Reward, RewardType
from caching import Memoize
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbon.common.script.util.format import FmtTimeInterval, FmtAmt
from characterdata.npccharacter import NpcCharacter
from eve.client.script.ui.eveColor import SUCCESS_GREEN_HEX
from eve.client.script.ui.station.agents.agentConst import LABEL_BY_BUTTON_TYPE
from eve.common.lib.appConst import agentMissionStateCompleted, agentMissionStateDeclined, agentMissionStateQuit, agentMissionStateFailed, agentMissionStateCantReplay, agentMissionModified, agentDialogueButtonLocateCharacter, agentTypeResearchAgent, agentTypeHeraldry, agentDialogueButtonViewMission, agentDialogueButtonRequestMission, agentDialogueButtonContinue, agentDialogueButtonQuit, agentDialogueButtonCancelResearch, agentMissionBriefingKeywords, agentMissionBriefingTitleID, agentMissionBriefingBriefingID, agentMissionBriefingDeclineTime, agentMissionBriefingExpirationTime, agentMissionBriefingAcceptTimestamp, corpDivisionHeraldry
from eve.common.script.sys.idCheckers import IsCapsule, IsFaction, IsNPCCorporation
from evemissions.client.data import get_fixed_lp_rewards
from evemissions.client.mission import Mission
from evemissions.client.objectives import ObjectiveState, ObjectivesType, TalkToAgentObjective, CargoObjective, PickUpObjective, DropOffObjective, DungeonObjective, ShipRestrictions
from gametime import MIN
from inventorycommon.const import typeLoyaltyPoints, typeLoyaltyPointsHeraldry, typeResearch
from localization import GetByLabel
from logging import getLogger
from random import choice
from signals import Signal
logger = getLogger(__name__)
ACTION_TO_STATE = {'missionCompleted': agentMissionStateCompleted,
 'missionDeclined': agentMissionStateDeclined,
 'missionQuit': agentMissionStateQuit,
 'missionCantReplay': agentMissionStateCantReplay}

class BaseMissionController(object):

    def __init__(self, npc_character_id):
        self.npc_character_id = npc_character_id
        self.npc_character = NpcCharacter(self.npc_character_id)
        self.mission_id = None
        self.mission = None
        self.on_ship_changed = Signal()
        self.on_station_changed = Signal()
        self.on_mission_modified = Signal()

    def get_mission_name(self):
        return self.mission.name

    def get_mission_title(self):
        if self._should_show_title_mission_completed():
            return 'UI/Agents/DefaultMessages/MissionCompleted'
        elif self._should_show_title_mission_unavailable():
            return 'UI/Agents/DefaultMessages/MissionUnavailable'
        else:
            return self.get_mission_name()

    def get_no_mission_message(self, time_left):
        if self.npc_character.get_division_id() == corpDivisionHeraldry:
            if time_left:
                label = 'UI/Agents/DefaultMessages/NoMissionHeraldryTimer'
            else:
                label = 'UI/Agents/DefaultMessages/NoMissionHeraldry'
        else:
            label = choice(['UI/Agents/DefaultMessages/NoMission1', 'UI/Agents/DefaultMessages/NoMission2'])
        return GetByLabel(label)

    def _should_show_title_mission_completed(self):
        return self.mission and self.is_mission_completed() and self.has_time_based_restriction()

    def _should_show_title_mission_unavailable(self):
        if not self.mission:
            return False
        if self.mission.is_completed():
            return False
        if not self._is_heraldry_agent():
            return False
        return not self.mission.mission_id or self.has_time_based_restriction()

    def _is_heraldry_agent(self):
        return self.npc_character.get_agent_type() == agentTypeHeraldry

    def get_standing_gain(self):
        return self.mission.get_standing_gain()

    def get_standing_gain_by_entity_id(self):
        return self.mission.get_standing_gain_by_entity_id()

    def has_standing_rewards(self):
        return self.mission.has_standing_rewards()

    def show_standings(self):
        return not self._is_heraldry_agent() and self.has_standing_rewards()

    def get_objectives(self):
        return self.mission.objectives

    def get_objectives_type(self):
        return self.mission.objectives_type

    def get_actions(self):
        return []

    def get_dungeon_id(self):
        return self.mission.dungeon_id

    def get_granted_items(self):
        return self.mission.granted_items

    def get_normal_rewards(self):
        return self.mission.normal_rewards

    def get_bonus_rewards(self):
        return self.mission.bonus_rewards

    def get_collateral(self):
        return self.mission.collateral

    def can_run_in_current_ship(self):
        return True

    def get_ship_restrictions(self):
        return self.mission.ship_restrictions

    def get_lore(self):
        if not self.mission or not self.mission.briefing:
            return ''
        lore = self.mission.briefing
        special_interactions = self.mission.special_interactions
        if special_interactions:
            lore += u'<br><br>{special_interactions}'.format(special_interactions=special_interactions)
        timer = self.mission.timer
        if timer:
            lore += u'<br><br>{timer}'.format(timer=timer)
        time_left = self.mission.time_left
        if time_left:
            lore += u'<br><br>{time_left}'.format(time_left=time_left)
        return lore

    def has_time_based_restriction(self):
        return bool(self.mission.time_left)

    def is_mission_active(self):
        return self.mission.mission_id and self.mission.is_active() and not self.mission.time_left and not self.mission.is_disabled()

    def is_mission_completed(self):
        return self.mission.mission_id and self.mission.is_completed()

    def can_replay_mission(self):
        return self.mission.can_replay() and not self.mission.is_disabled()

    def is_mission_important(self):
        return self.mission.is_important

    def get_mission_importance_text(self):
        if not self.is_mission_important():
            return (None, None, None)
        header = GetByLabel('UI/Agents/StandardMission/ImportantMission')
        if self.is_mission_completed():
            return (header, None, None)
        standings_gains = self.get_standing_gain_by_entity_id()
        text = GetByLabel('UI/Agents/StandardMission/ImportantStandingsWarning')
        if not standings_gains:
            return (header, text, None)
        standing_list = []
        for entity_id, value in standings_gains.iteritems():
            if FloatCloseEnough(value, 0):
                continue
            formatted_value = u'+{}'.format(FmtAmt(value, showFraction=2))
            standing_list.append((self.__get_npc_sort_value(entity_id), (cfg.eveowners.Get(entity_id).name, formatted_value)))

        if not standing_list:
            return (header, text, None)
        standing_list = [ x[1] for x in sorted(standing_list, key=lambda data: data[0]) ]
        return (header, text, standing_list)

    def __get_npc_sort_value(self, entity_id):
        if IsFaction(entity_id):
            return 0
        if IsNPCCorporation(entity_id):
            return 1
        return 2


class OldMissionController(BaseMissionController):
    __notifyevents__ = ['OnSessionChanged', 'OnAgentMissionChange']

    def __init__(self, npc_character_id):
        super(OldMissionController, self).__init__(npc_character_id)
        self.agent_service = sm.GetService('agents')
        self.agent = self.agent_service.GetAgentMoniker(self.npc_character_id)
        sm.RegisterNotify(self)

    def get_actions(self):
        actions = []
        for action_id, action in self.mission.actions:
            if type(action) is int:
                action_data = self._build_action_data(action_id, action)
                actions.append(action_data)

        return actions

    def should_add_close_action(self):
        actions = self.mission.actions
        if not actions:
            return True
        if len(actions) < 3:
            if any((self._is_close_action(action) for action_id, action in actions)):
                return True
            if self.mission.time_left:
                return True
        return False

    def get_standing_gain(self):
        standing_gains = self._get_standing_gain_for_mission_id(self.mission_id)
        effective_standing_gain = sm.GetService('standing').AddToEffectiveStandingWithAgent(standingGains=standing_gains, agentID=self.npc_character_id)
        return effective_standing_gain

    @Memoize(0.08)
    def _get_standing_gain_for_mission_id(self, mission_id):
        standing_gains = self.agent.GetStandingGainsForMission(mission_id)
        return standing_gains

    def get_standing_gain_by_entity_id(self):
        standing_gains = self._get_standing_gain_for_mission_id(self.mission_id)
        standing_svc = sm.GetService('standing')
        newStandingsWithBonus, currentStandings = standing_svc.GetNewAndCurrentStandings(standing_gains, agentID=self.npc_character_id)
        standing_gains_by_entity = {}
        for entity_id, value in newStandingsWithBonus.iteritems():
            current = currentStandings.get(entity_id, 0)
            current_with_bonus = standing_svc.GetStandingWithSkillBonusFromValue(current, entity_id, session.charid)
            standing_gains_by_entity[entity_id] = value - current_with_bonus

        return standing_gains_by_entity

    def can_run_in_current_ship(self):
        return self.mission.can_run_in_current_ship()

    def get_disclaimer(self):
        if self._is_heraldry_agent():
            return GetByLabel('UI/Agents/DefaultMessages/HeraldryDisclaimer')

    def get_mission_restrictions(self):
        return self.mission.get_ship_restrictions()

    def update_objectives(self):
        objective_info = self.agent.GetMissionObjectiveInfo() or {}
        self.mission.update_objective_info(objective_info)

    def update_mission(self, action_id):
        (agent_says, actions), last_action_info = self.agent.DoAction(action_id)
        if action_id is None and len(actions):
            first_action = actions[0]
            first_action_id, first_action_message = first_action
            if first_action_message in (agentDialogueButtonRequestMission, agentDialogueButtonViewMission) and (len(actions) == 1 or not self._is_locator_agent(actions) and not self._is_research_agent()):
                (agent_says, actions), last_action_info = self.agent.DoAction(first_action_id)
        _, self.mission_id = agent_says
        mission_state = self._build_mission_state(last_action_info)
        if self.mission and self.mission.mission_id == self.mission_id:
            self.mission.update_state(mission_state)
            self.mission.actions = actions
        else:
            self.mission = Mission(self.mission_id, self.npc_character_id, state=mission_state, actions=actions)
        time_left = last_action_info.get('missionCantReplay', None)
        if not self.mission_id and not time_left or self.mission.is_disabled():
            briefing = self.get_no_mission_message(time_left=None)
            self.mission.update_info(briefing)
            return
        if self.mission.can_replay():
            briefing = self.agent_service.ProcessMessage(agent_says, self.npc_character_id)
        else:
            briefing = self.get_no_mission_message(time_left)
        if briefing:
            if time_left:
                time_left = GetByLabel('UI/Agents/DefaultMessages/MissionCantReplay', timeLeft=FmtTimeInterval(time_left, breakAt='min' if time_left > MIN else 'sec'), timerColor=SUCCESS_GREEN_HEX)
                self.mission.update_info(briefing, time_left=time_left)
            else:
                briefing_data = self.agent_service.GetMissionBriefingInfo(self.npc_character_id)
                special_interactions = self._build_special_interactions()
                timer = self._build_mission_time(briefing_data)
                accept_time = briefing_data[agentMissionBriefingAcceptTimestamp] if briefing_data else None
                self.mission.update_info(briefing, special_interactions, timer, accept_time)

    def _is_research_agent(self):
        return self.npc_character.get_agent_type() == agentTypeResearchAgent

    def _is_locator_agent(self, actions):
        for _, dialogue in actions:
            if dialogue == agentDialogueButtonLocateCharacter:
                return True

        return False

    def _is_talk_to_agent_objective(self, objective_type):
        return objective_type == ObjectivesType.TALK_TO_AGENT

    def _is_transport_objective(self, objective_type):
        return objective_type == ObjectivesType.TRANSPORT

    def _is_fetch_objective(self, objective_type):
        return objective_type == ObjectivesType.FETCH

    def _build_objective_entries(self, objective_type, objective_data):
        objective_entries = []
        if self._is_talk_to_agent_objective(objective_type):
            agent_id, location = objective_data
            objective = TalkToAgentObjective(agent_id, location, state=ObjectiveState.IN_PROGRESS)
            objective_entries.append(objective)
        elif self._is_transport_objective(objective_type):
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
            objective_entries.append(objective)
            state = ObjectiveState.COMPLETED if is_pickup_complete else ObjectiveState.IN_PROGRESS
            objective = PickUpObjective(location=pickup, state=state)
            objective_entries.append(objective)
            state = ObjectiveState.COMPLETED if is_dropoff_complete else ObjectiveState.IN_PROGRESS
            objective = DropOffObjective(location=dropoff, state=state)
            objective_entries.append(objective)
        elif self._is_fetch_objective(objective_type):
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
            objective_entries.append(objective)
            state = ObjectiveState.COMPLETED if is_dropoff_complete else ObjectiveState.IN_PROGRESS
            objective = DropOffObjective(location=dropoff, state=state)
            objective_entries.append(objective)
        return objective_entries

    def _build_dungeon_objective(self, dungeon_data):
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
        self.mission.ship_restrictions = ship_restrictions
        is_killing_optional = bool(dungeon_data.get('optional', False))
        briefing = dungeon_data.get('briefingMessage', None)
        if briefing:
            briefing = sm.GetService('agents').ProcessMessage(briefing, self.npc_character_id)
        location = dungeon_data.get('location', None)
        dungeon_id = dungeon_data['dungeonID']
        self.mission.dungeon_id = dungeon_id
        return DungeonObjective(dungeon_id, ship_restrictions, is_killing_optional, briefing, location, state)

    def _build_granted_items(self, objective_info):
        granted_items = []
        try:
            for type_id, quantity, extra in objective_info.get('agentGift', []):
                reward = Reward(RewardType.GRANTED, type_id, quantity, extra)
                granted_items.append(reward)

        except KeyError:
            pass

        return granted_items

    def _build_normal_rewards(self, objective_info):
        normal_rewards = []
        try:
            for type_id, quantity, extra in objective_info.get('normalRewards', []):
                reward = Reward(RewardType.NORMAL, type_id, quantity, extra)
                normal_rewards.append(reward)

            lp = objective_info.get('loyaltyPoints', 0)
            if lp > 0:
                fixed_alpha_lp, fixed_omega_lp = get_fixed_lp_rewards(self.mission_id)
                type_id = typeLoyaltyPointsHeraldry if self._is_heraldry_agent() else typeLoyaltyPoints
                reward = Reward(RewardType.NORMAL, type_id, lp, alpha_quantity=fixed_alpha_lp, omega_quantity=fixed_omega_lp)
                normal_rewards.append(reward)
            rp = round(objective_info.get('researchPoints', 0), 0)
            if rp > 0:
                reward = Reward(RewardType.NORMAL, typeResearch, rp)
                normal_rewards.append(reward)
        except KeyError:
            pass

        return normal_rewards

    def _build_bonus_rewards(self, objective_info):
        mission_accepted_time = self.mission.accept_time
        bonus_rewards = []
        try:
            for time_remaining, type_id, quantity, extra, timeBonusIntervalMin in objective_info.get('bonusRewards', []):
                reward = Reward(RewardType.BONUS, type_id, quantity, extra, timeBonusIntervalMin, mission_accepted_time)
                bonus_rewards.append(reward)

        except KeyError:
            pass

        return bonus_rewards

    def _build_collateral(self, objective_info):
        collateral = []
        try:
            for type_id, quantity, extra in objective_info.get('collateral', []):
                reward = Reward(RewardType.COLLATERAL, type_id, quantity, extra)
                collateral.append(reward)

        except KeyError:
            pass

        return collateral

    def _build_mission_state(self, last_action_info):
        for action, state in ACTION_TO_STATE.iteritems():
            if last_action_info.get(action, None):
                return state

    def _build_special_interactions(self):
        special_interactions = ''
        for action_id, action in self.mission.actions:
            if type(action) != dict:
                continue
            action_keywords = action[agentMissionBriefingKeywords]
            self.agent_service.PrimeMessageArguments(self.npc_character_id, self.mission_id, action_keywords)
            message = (action[agentMissionBriefingTitleID], self.mission_id)
            mission_title = self.agent_service.ProcessMessage(message, self.npc_character_id)
            special_interactions += '\n                <span id=subheader><a href="localsvc:method=AgentDoAction&agentID=%d&actionID=%d">%s</a> &gt;&gt;</span><br>\n            ' % (self.npc_character_id, action_id, mission_title)
            action_briefing_id = action[agentMissionBriefingBriefingID]
            if action_briefing_id is not None:
                if isinstance(action_briefing_id, basestring) or action_briefing_id > 0:
                    message = (action_briefing_id, self.mission_id)
                    action_briefing = self.agent_service.ProcessMessage(message, self.npc_character_id)
                else:
                    action_briefing = GetByLabel('UI/Agents/Dialogue/StandardMission/CorruptBriefing')
                special_interactions += '\n                        <div id=basetext>%s</div>\n                        <br>\n                    ' % action_briefing

        return special_interactions

    def _build_mission_time(self, briefing_data):
        if briefing_data:
            decline_time = briefing_data[agentMissionBriefingDeclineTime]
            expiration_time = briefing_data[agentMissionBriefingExpirationTime]
            if decline_time is not None:
                if decline_time == -1:
                    return ''
                else:
                    time_break_at = 'min' if decline_time > MIN else 'sec'
                    time_remaining = FmtTimeInterval(decline_time, breakAt=time_break_at)
                    return GetByLabel('UI/Agents/StandardMission/DeclineMessageTimeLeft', timeRemaining=time_remaining)
            elif expiration_time is not None:
                return GetByLabel('UI/Agents/Dialogue/ThisMissionExpiresAt', expireTime=expiration_time)
        return ''

    def _build_action_data(self, action_id, action):
        label_path = LABEL_BY_BUTTON_TYPE.get(action, None)
        if label_path:
            label = GetByLabel(label_path)
        else:
            logger.error('Unknown button ID for agent action, id =', action)
            label = 'Unknown ID ' + str(action)
        action_data = (label, sm.GetService('agents').DoAction, {'args': (self.npc_character_id, action_id),
          'uiName': u'{}_Button'.format(label_path.split('/')[-1])})
        return action_data

    def _is_close_action(self, action):
        return action in [agentDialogueButtonRequestMission,
         agentDialogueButtonContinue,
         agentDialogueButtonQuit,
         agentDialogueButtonCancelResearch]

    def OnSessionChanged(self, isRemote, sess, change):
        if 'shipid' in change:
            self.on_ship_changed()
        if 'stationid' in change:
            self.on_station_changed()

    def OnAgentMissionChange(self, action, agentID):
        if action == agentMissionModified and self.npc_character_id == agentID:
            self.on_mission_modified()
