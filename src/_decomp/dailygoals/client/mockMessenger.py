#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dailygoals\client\mockMessenger.py
import httplib
import logging
import uuid
import datetime
import blue
from carbon.common.script.sys.serviceConst import ROLE_QA, ROLE_PROGRAMMER
from dailygoals.client.utils import format_goal_from_payload
import dailygoals.client.qa_settings as daily_goals_qa_settings
from dailygoals.client.const import DailyGoalCategory
from eveProto.generated.eve_public.dailygoal.api.requests_pb2 import GetRequest, GetResponse, GetAllCurrentRequest, GetAllCurrentResponse, GetAllWithRewardsRequest, GetAllWithRewardsResponse, RedeemRequest, RedeemResponse
from eveProto.generated.eve_public.dailygoal.api.admin.admin_pb2 import ProgressRequest, ProgressResponse
from eveProto.generated.eve_public.dailygoal.api.notices_pb2 import ProgressedNotice, CompletedNotice, CurrentGoalsNotice, RedeemedNotice
import dailygoals.client.goalMessengerSignals as messenger_signals
from dailygoals.client.errors import GoalMessengerError, GoalNotRedeemableToCurrentLocation
from dailygoals.client.const import RewardType, DailyGoalCategory
logger = logging.getLogger(__name__)
MONTHLY_GOAL_TEMPLATE = {'contribution_fields': {'daily_goal': None,
                         'daily_goal_category': 2},
 'assigner_id': 1000413,
 'progress': 3,
 'career_id': None,
 'contribution_method_id': 'CompleteGoal',
 'category': DailyGoalCategory.CATEGORY_MONTHLY_BONUS,
 'active_after': None,
 'target': None,
 'desc_id': 699209,
 'has_earnings': False,
 'help_text_id': 699210,
 'goal_id': None,
 'name_id': 699211,
 'active_until': None,
 'omega': False}

def _create_base_monthly_goal():
    goal = MONTHLY_GOAL_TEMPLATE.copy()
    goal['active_after'] = datetime.datetime.now()
    goal['active_until'] = datetime.datetime.now() + datetime.timedelta(1)
    return goal


def get_mock_monthly_goals():
    goals_dict = {}
    for num in range(1, 5):
        key = 'monthly_goal_{}'.format(num)
        goals_dict[key] = _create_base_monthly_goal()
        goals_dict[key]['target'] = 3 * num
        goals_dict[key]['is_omega'] = False
        goals_dict[key]['goal_id'] = uuid.uuid4()
        key = 'monthly_omega_goal_{}'.format(num)
        goals_dict[key] = _create_base_monthly_goal()
        goals_dict[key]['target'] = 3 * num
        goals_dict[key]['is_omega'] = True
        goals_dict[key]['goal_id'] = uuid.uuid4()

    goals_dict['monthly_goal_1']['rewards'] = [{'reward_type': RewardType.LOYALTY_POINTS,
      'amount': 5000}]
    goals_dict['monthly_goal_1']['has_earnings'] = True
    goals_dict['monthly_omega_goal_1']['rewards'] = [{'reward_type': RewardType.LOYALTY_POINTS,
      'amount': 10000,
      'is_omega_restricted': True}]
    goals_dict['monthly_omega_goal_1']['has_earnings'] = True
    goals_dict['monthly_goal_2']['rewards'] = [{'reward_type': RewardType.ITEM,
      'amount': 1,
      'item_type_id': 83679}]
    goals_dict['monthly_omega_goal_2']['rewards'] = [{'reward_type': RewardType.ITEM,
      'amount': 1,
      'item_type_id': 83639}]
    goals_dict['monthly_goal_3']['rewards'] = [{'reward_type': RewardType.ISK,
      'amount': 8000000}]
    goals_dict['monthly_omega_goal_3']['rewards'] = [{'reward_type': RewardType.PLEX,
      'amount': 5}]
    goals_dict['monthly_goal_4']['rewards'] = [{'reward_type': RewardType.SKILL_POINTS,
      'amount': 25000}]
    goals_dict['monthly_omega_goal_4']['rewards'] = [{'reward_type': RewardType.SKILL_POINTS,
      'amount': 150000}]
    return goals_dict


class MockDailyGoalMessenger(object):
    _instance = None
    public_gateway = None

    @classmethod
    def get_instance(cls, public_gateway):
        if not cls._instance:
            cls._instance = MockDailyGoalMessenger(public_gateway)
        return cls._instance

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.mock_goal_dict = None
        self.mock_id_list = None
        self._subscribe_to_notices()

    def _subscribe_to_notices(self):
        self.public_gateway.subscribe_to_notice(CurrentGoalsNotice, lambda payload, _: self.on_current_goals_received(payload))
        self.public_gateway.subscribe_to_notice(CompletedNotice, lambda payload, _: self.on_goal_completed(payload))
        self.public_gateway.subscribe_to_notice(ProgressedNotice, lambda payload, _: self.on_goal_progressed(payload))
        self.public_gateway.subscribe_to_notice(RedeemedNotice, lambda payload, _: self.on_goal_redeemed(payload))

    def _is_programmer(self):
        return session and session.role & ROLE_PROGRAMMER

    def get_mock_monthly_list(self):
        if self.mock_goal_dict is None:
            self.mock_goal_dict = get_mock_monthly_goals()
            self.mock_id_list = [ goal['goal_id'] for goal in self.mock_goal_dict.itervalues() ]
        return [ goal for goal in self.mock_goal_dict.itervalues() ]

    def get_mock_goal_ids(self):
        goal_list = self.get_mock_monthly_list()
        return [ goal['goal_id'] for goal in goal_list ]

    def get_mock_goal(self, goal_id):
        for goal in self.get_mock_monthly_list():
            if goal['goal_id'] == goal_id:
                return goal

    def iter_format_goals(self, goals):
        for goal in goals:
            yield format_goal_from_payload(goal_id=uuid.UUID(bytes=goal.id.uuid), goal_attributes=goal.goal, goal_progress=goal.current_progress, earnings=goal.earnings)

    def get_current_goals(self):
        if self._is_programmer():
            if daily_goals_qa_settings.daily_goals_get_goals_force_delay.get() > 0:
                blue.synchro.Sleep(daily_goals_qa_settings.daily_goals_get_goals_force_delay.get() * 1000)
            if daily_goals_qa_settings.daily_goals_get_goals_force_errors.get():
                if daily_goals_qa_settings.daily_goals_get_goals_randomize_errors.get():
                    import random
                    if random.random() > 0.5:
                        raise Exception
                else:
                    raise Exception
        logger.info('Daily Goals: sending GetAllCurrentRequest')
        request = GetAllCurrentRequest()
        payload = self._send_request(request, GetAllCurrentResponse)
        data = [ goal for goal in self.iter_format_goals(payload.goals) if goal['category'] != DailyGoalCategory.CATEGORY_MONTHLY_BONUS ]
        for goal in data:
            goal['omega'] = False

        data.extend(self.get_mock_monthly_list())
        return data

    def get_goal(self, goal_id):
        logger.info(u'Daily Goals: sending GetRequest for goal %s' % goal_id)
        if goal_id in self.get_mock_goal_ids():
            mock_goal = self.get_mock_goal(goal_id)
            return mock_goal
        request = GetRequest()
        request.goal.uuid = goal_id.bytes
        payload = self._send_request(request, GetResponse)
        goal_data = format_goal_from_payload(goal_id=goal_id, goal_attributes=payload.goal, goal_progress=payload.progress, earnings=payload.earnings)
        return goal_data

    def get_all_with_rewards_page(self, token = '', size = 100):
        logger.info('Daily Goals: sending GetAllWithRewardsRequest')
        request = GetAllWithRewardsRequest()
        request.page.size = size
        request.page.token = token
        try:
            logger.info('GetAllWithRewardsRequest sent with data %s', request)
            payload = self._send_request(request, GetAllWithRewardsResponse)
            logger.info('GetAllWithRewardsResponse received with data %s', payload)
        except GoalMessengerError as gme:
            logger.error('Daily Goals: Unable to get page with token %s' % token)
            raise gme

        goal_id_list = [ uuid.UUID(bytes=identifier.uuid) for identifier in payload.ids ]
        goal_id_list.extend(self.get_mock_goal_ids())
        return (payload.next_page.token, goal_id_list)

    def redeem_reward(self, goal_id, do_redeem_current_location):
        logger.info('Daily Goals: sending RedeemRequest for goal %s' % goal_id)
        request = RedeemRequest()
        request.goal.uuid = goal_id.bytes
        request.redeem_current_location = do_redeem_current_location
        try:
            self._send_request(request, RedeemResponse)
        except GoalMessengerError as gme:
            logger.error('Daily Goals: error while redeeming reward for goal %s' % goal_id)
            if do_redeem_current_location and gme.status_code == httplib.FORBIDDEN:
                raise GoalNotRedeemableToCurrentLocation(goal_id, session.locationid)

    def set_goal_progress(self, goal_id, character_id, progress_to_add):
        logger.info('Daily Goals: sending ProgressRequest for goal %s, progress +=%s' % (goal_id, progress_to_add))
        if session and session.role & ROLE_QA:
            request = ProgressRequest()
            request.goal.uuid = goal_id.bytes
            request.character.sequential = character_id
            request.progress = progress_to_add
            self._send_request(request, ProgressResponse)

    def on_current_goals_received(self, _payload):
        messenger_signals.on_current_goals_received_internal()

    def on_goal_completed(self, payload):
        logger.info('Daily Goals: goal %s Completed Notice' % payload.goal)
        goal_id = uuid.UUID(bytes=payload.goal.uuid)
        messenger_signals.on_goal_completed_internal(goal_id)

    def on_goal_progressed(self, payload):
        goal_id = uuid.UUID(bytes=payload.goal.uuid)
        current_progress = payload.current_progress
        messenger_signals.on_goal_progressed_internal(goal_id, current_progress)

    def on_goal_redeemed(self, payload):
        goal_id = uuid.UUID(bytes=payload.goal.uuid)
        messenger_signals.on_goal_redeemed_internal(goal_id)

    def _send_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code != httplib.OK:
            logger.error('%s returned with statusCode %s, statusMessage: %s', request.DESCRIPTOR.name, response_primitive.status_code, response_primitive.status_message)
            raise GoalMessengerError(request.DESCRIPTOR.name, response_primitive.status_code)
        return payload
