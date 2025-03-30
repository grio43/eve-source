#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\client\goals\goalMessenger.py
import datetime
import corporation.client.goals.goalMessengerSignals as messenger_signals
import datetimeutils
import gametime
import httplib
import logging
import uuid
from corporation.client.goals.errors import GoalMessengerError, AtGoalCapacity, GoalError, GoalNotFound, BadRequestToReserveAsset, WalletAccessForbidden, InternalErrorReservingAsset, InvalidExpirationTime
from corporation.client.goals.goalMessengerUtil import goal_formatter, add_contribution_method
from dateutil.relativedelta import relativedelta
from eveProto.generated.eve_public.corporationgoal.api.notices_pb2 import RedeemedNotice, ExpiredNotice
from eveProto.generated.eve_public.corporationgoal.api.requests_pb2 import GetActiveRequest, GetActiveResponse, GetMyContributorSummaryForGoalRequest, GetMyContributorSummaryForGoalResponse, GetInactiveRequest, GetInactiveResponse, GetContributorSummariesForGoalRequest, GetContributorSummariesForGoalResponse, RedeemMyRewardsRequest, RedeemMyRewardsResponse, GetMineWithRewardsRequest, GetMineWithRewardsResponse
from eveProto.generated.eve_public.goal.api.notices_pb2 import ClosedNotice, CompletedNotice, CreatedNotice, DeletedNotice, ProgressedNotice, NameChangedNotice, DescriptionChangedNotice
from eveProto.generated.eve_public.goal.api.requests_pb2 import CreateRequest, CreateResponse, GetRequest, GetResponse, CloseRequest, CloseResponse, DeleteRequest, DeleteResponse, SetCurrentProgressRequest, SetCurrentProgressResponse, GetCapacityResponse, GetCapacityRequest
from eveProto.generated.eve_public.goal.contribution.api.notices_pb2 import ContributedNotice
from eveProto.generated.eve_public.goal.goal_pb2 import RewardPool, PaymentPeriod
from eveProto.monolith_converters.isk import split_isk
from goals.common.goalConst import CareerPathId, UPDATE_TIMEOUT_SECONDS
from stackless_response_router.exceptions import TimeoutException
logger = logging.getLogger('corporation_goals')
CAREER_PATH_RESOLVER = {CareerPathId.UNSPECIFIED: CreateRequest.Career.CAREER_UNSPECIFIED,
 CareerPathId.EXPLORER: CreateRequest.Career.CAREER_EXPLORER,
 CareerPathId.INDUSTRIALIST: CreateRequest.Career.CAREER_INDUSTRIALIST,
 CareerPathId.SOLDIER_OF_FORTUNE: CreateRequest.Career.CAREER_SOLDIER_OF_FORTUNE,
 CareerPathId.ENFORCER: CreateRequest.Career.CAREER_ENFORCER}
PAGE_SIZE = 25
MIN_PROJECT_TIME = 15
MAX_PROJECT_TIME = 1

class GoalMessenger(object):
    _instance = None
    public_gateway = None

    @classmethod
    def get_instance(cls, public_gateway):
        if not cls._instance:
            cls._instance = GoalMessenger(public_gateway)
        return cls._instance

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self._subscribe_to_notices()

    def _subscribe_to_notices(self):
        self.public_gateway.subscribe_to_notice(RedeemedNotice, lambda payload, _: self.on_redeemed(goal_id=uuid.UUID(bytes=payload.goal.uuid), quantity=payload.quantity))
        self.public_gateway.subscribe_to_notice(ClosedNotice, lambda payload, _: self.on_goal_closed(goal_id=uuid.UUID(bytes=payload.goal.uuid)))
        self.public_gateway.subscribe_to_notice(CompletedNotice, lambda payload, _d: self.on_goal_completed(goal_id=uuid.UUID(bytes=payload.goal.uuid)))
        self.public_gateway.subscribe_to_notice(CreatedNotice, lambda payload, _: self.on_goal_created(goal_id=uuid.UUID(bytes=payload.id.uuid), goal_data=payload.goal))
        self.public_gateway.subscribe_to_notice(DeletedNotice, lambda payload, _: self.on_goal_deleted(goal_id=uuid.UUID(bytes=payload.goal.uuid)))
        self.public_gateway.subscribe_to_notice(ContributedNotice, lambda payload, _: self.on_goal_contribution(goal_id=uuid.UUID(bytes=payload.goal.uuid), previous_progress=payload.previous_progress, current_progress=payload.current_progress))
        self.public_gateway.subscribe_to_notice(ProgressedNotice, lambda payload, _: self.on_goal_progressed(goal_id=uuid.UUID(bytes=payload.goal.uuid), current_progress=payload.current_progress))
        self.public_gateway.subscribe_to_notice(NameChangedNotice, lambda payload, _: self.on_name_changed(goal_id=uuid.UUID(bytes=payload.goal.uuid), new_name=payload.admin_designated_new_name))
        self.public_gateway.subscribe_to_notice(DescriptionChangedNotice, lambda payload, _: self.on_description_changed(goal_id=uuid.UUID(bytes=payload.goal.uuid), new_description=payload.admin_designated_new_description))
        self.public_gateway.subscribe_to_notice(ExpiredNotice, lambda payload, _: self.on_goal_expired(goal_id=uuid.UUID(bytes=payload.goal.uuid)))

    def get_goal(self, goal_id):
        request = GetRequest()
        request.goal.uuid = goal_id.bytes
        logger.info('GetRequest - sending for goal %s', goal_id)
        payload = self._send_request(request, GetResponse)
        formatted_goal = goal_formatter(goal_id=goal_id, goal=payload.goal)
        logger.info('GetRequest - received data for goal %s: %s', goal_id, formatted_goal)
        return formatted_goal

    def get_active_goal_ids(self, token = '', size = PAGE_SIZE):
        request = GetActiveRequest()
        request.page.size = size
        request.page.token = token
        payload = self._send_request(request, GetActiveResponse)
        goal_ids = [ uuid.UUID(bytes=goal_id.uuid) for goal_id in payload.goal_ids ]
        token = payload.next_page.token
        return (token, goal_ids)

    def get_unclaimed_goal_ids(self, token = '', size = PAGE_SIZE):
        request = GetMineWithRewardsRequest()
        request.page.size = size
        request.page.token = token
        payload = self._send_request(request, GetMineWithRewardsResponse)
        goal_ids = [ uuid.UUID(bytes=goal_id.uuid) for goal_id in payload.identifiers ]
        token = payload.next_page.token
        return (token, goal_ids)

    def get_inactive_goal_ids(self, start_time, duration, token = '', size = PAGE_SIZE):
        request = GetInactiveRequest()
        request.ended_timespan.start_time.FromSeconds(start_time)
        request.ended_timespan.duration.FromSeconds(duration)
        request.page.size = size
        request.page.token = token
        payload = self._send_request(request, GetInactiveResponse)
        goal_ids = [ uuid.UUID(bytes=goal_id.uuid) for goal_id in payload.goal_ids ]
        token = payload.next_page.token
        return (token, goal_ids)

    def get_my_contributor_summary(self, goal_id):
        request = GetMyContributorSummaryForGoalRequest()
        request.goal.uuid = goal_id.bytes
        payload = self._send_request(request, GetMyContributorSummaryForGoalResponse, not_found_as_none=True)
        if payload is None:
            progress = 0
            unclaimed = 0
        else:
            progress = payload.summary.progress
            if payload.summary.earnings:
                unclaimed = payload.summary.earnings[0].quantity.total
            else:
                unclaimed = 0
        return {'progress': progress,
         'rewards_unclaimed': unclaimed}

    def get_all_contributor_summaries_for_goal(self, goal_id, token = '', size = PAGE_SIZE):
        request = GetContributorSummariesForGoalRequest()
        request.goal.uuid = goal_id.bytes
        request.page.size = size
        request.page.token = token
        payload = self._send_request(request, GetContributorSummariesForGoalResponse)
        summaries = []
        for summary in payload.summaries:
            summaries.append((summary.contributor.sequential, summary.progress))

        next_token = payload.next_page.token
        return (next_token, summaries)

    def get_capacity(self):
        request = GetCapacityRequest()
        payload = self._send_request(request, GetCapacityResponse)
        return payload.capacity

    def redeem_reward(self, goal_id):
        request = RedeemMyRewardsRequest()
        request.goal_id.uuid = goal_id.bytes
        self._send_request(request, RedeemMyRewardsResponse)

    def on_redeemed(self, goal_id, quantity):
        logger.info('Emitting Goal Redeemed Notice for goal %s and quantity %s' % (goal_id, quantity))
        messenger_signals.on_goal_redeemed_internal(goal_id, quantity)

    def on_goal_created(self, goal_id, goal_data):
        logger.info('Emitting Goal Created Notice %s' % goal_id)
        format_goal_data = goal_formatter(goal_id, goal_data)
        messenger_signals.on_goal_created_internal(goal_id, format_goal_data)

    def on_goal_deleted(self, goal_id):
        logger.info('Emitting Goal Deleted Notice %s' % goal_id)
        messenger_signals.on_goal_deleted_internal(goal_id)

    def on_goal_closed(self, goal_id):
        logger.info('Emitting Goal Closed Notice %s' % goal_id)
        messenger_signals.on_goal_closed_internal(goal_id)

    def on_goal_completed(self, goal_id):
        logger.info('Emitting Goal Completed Notice %s' % goal_id)
        messenger_signals.on_goal_completed_internal(goal_id)

    def on_goal_contribution(self, goal_id, previous_progress, current_progress):
        progress_added = current_progress - previous_progress
        logger.info('Emitting OnGoalProgressAdded Notice %s, incrementing by %s, setting progress to %s', goal_id, progress_added, current_progress)
        messenger_signals.on_goal_contribution_internal(goal_id, progress_added, current_progress)

    def on_goal_progressed(self, goal_id, current_progress):
        logger.info('Emitting OnGoalProgressSet Notice %s, progress set to %s', goal_id, current_progress)
        messenger_signals.on_goal_progress_set_internal(goal_id, current_progress)

    def on_name_changed(self, goal_id, new_name):
        logger.info('Emitting OnGoalNameChanged Notice %s, name set to %s', goal_id, new_name)
        messenger_signals.on_goal_name_changed_internal(goal_id, new_name)

    def on_description_changed(self, goal_id, new_description):
        logger.info('Emitting OnGoalDescriptionChanged Notice %s, name set to %s', goal_id, new_description)
        messenger_signals.on_goal_description_changed_internal(goal_id, new_description)

    def on_goal_expired(self, goal_id):
        logger.info('Emitting Goal Expired Notice %s' % goal_id)
        messenger_signals.on_goal_expired_internal(goal_id)

    def create_goal(self, name, description, desired_progress, method_id, contribution_fields, career_path, payment = None, expiration = None, validate_end_date = True, participation_limit = None, coverage_limit = None, multiplier = None):
        request = CreateRequest()
        request.name = name
        request.description = description
        request.desired_progress = desired_progress
        add_contribution_method(request, method_id, contribution_fields)
        if career_path in CAREER_PATH_RESOLVER:
            request.career = request.career = CAREER_PATH_RESOLVER[career_path]
        else:
            raise ValueError('Career path not supported')
        if payment:
            units, nanos = split_isk(payment)
            reward = RewardPool()
            reward.period = PaymentPeriod.PAYMENT_PERIOD_CONTRIBUTION
            reward.isk.amount.units = units
            reward.isk.amount.nanos = nanos
            request.reward_pools.append(reward)
        if expiration:
            expiration_datetime = datetimeutils.filetime_to_datetime(expiration)
            if validate_end_date:
                now = gametime.now()
                min_datetime = now + relativedelta(minutes=MIN_PROJECT_TIME)
                max_datetime = datetime.datetime.combine(now + relativedelta(years=MAX_PROJECT_TIME), datetime.time.max)
                if max_datetime < expiration_datetime or expiration_datetime < min_datetime:
                    raise InvalidExpirationTime('Expiration time too short or long')
            request.timestamp.FromDatetime(expiration_datetime)
        else:
            request.no_expiry = True
        if participation_limit:
            request.limit = participation_limit
        else:
            request.unlimited = True
        if coverage_limit is not None:
            request.contribution_limit = coverage_limit
        else:
            request.contribution_unlimited = True
        if multiplier:
            request.scalar = multiplier
        else:
            request.default = True

        def _response_handler(primitive, payload):
            status_code = primitive.status_code
            status_message = primitive.status_message
            if status_code != httplib.OK:
                logger.info('Unexpected error when creating a goal - statusCode: %d, statusMessage: %s', status_code, status_message)
                if status_message == 'at capacity of active goals':
                    raise AtGoalCapacity(status_message)
                if 'unable to reserve backing asset for the rewards specified' in status_message:
                    if status_code == httplib.BAD_REQUEST:
                        raise BadRequestToReserveAsset(status_message)
                    elif status_code == httplib.FORBIDDEN:
                        raise WalletAccessForbidden(status_message)
                    else:
                        raise InternalErrorReservingAsset(status_message)
                raise GoalError(status_message)
            goal_id = uuid.UUID(bytes=payload.goal.uuid)
            logger.info('Goal created successfully - Identifier: %s', repr(goal_id))

        def _timeout_handler(timeout_exception):
            logger.error('create_goal timed out: %s' % timeout_exception, exc_info=True)
            raise GoalError(timeout_exception)

        logger.info('Sending CreateGoalRequest with data %s', request)
        self._send_request_and_wait_for_response(request, CreateResponse, _response_handler, _timeout_handler)

    def close_goal(self, goal_id):
        request = CloseRequest()
        request.goal.uuid = goal_id.bytes

        def _response_handler(primitive, _payload):
            if primitive.status_code != httplib.OK:
                logger.error('unexpected error when closing goal %s - statusCode: %s, statusMessage: %s', goal_id, primitive.status_code, primitive.status_message)
                if primitive.status_code == httplib.NOT_FOUND:
                    raise GoalNotFound(goal_id, session.corpid)
                raise GoalError(primitive.status_message)

        def _timeout_handler(timeout_exception):
            logger.error('close_goal timed out: %s' % timeout_exception, exc_info=True)
            raise GoalError(timeout_exception)

        self._send_request_and_wait_for_response(request, CloseResponse, _response_handler, _timeout_handler)

    def delete_goal(self, goal_id):
        request = DeleteRequest()
        request.goal.uuid = goal_id.bytes

        def _response_handler(primitive, _payload):
            if primitive.status_code != httplib.OK:
                logger.error('unexpected error when deleting goal %s - statusCode: %s, statusMessage: %s', goal_id, primitive.status_code, primitive.status_message)
                if primitive.status_code == httplib.NOT_FOUND:
                    raise GoalNotFound(goal_id, session.corpid)
                raise GoalError(primitive.status_message)

        def _timeout_handler(timeout_exception):
            logger.error('delete_goal timed out: %s' % timeout_exception, exc_info=True)
            raise GoalError(timeout_exception)

        self._send_request_and_wait_for_response(request, DeleteResponse, _response_handler, _timeout_handler)

    def set_manual_goal_progress(self, goal_id, current_progress, updated_progress):
        request = SetCurrentProgressRequest()
        request.goal.uuid = goal_id.bytes
        request.current_progress = current_progress
        request.new_progress = updated_progress

        def _response_handler(primitive, _payload):
            if primitive.status_code != httplib.OK:
                logger.error('unexpected error when setting progress of goal %s - statusCode: %s, statusMessage: %s', goal_id, primitive.status_code, primitive.status_message)
                if primitive.status_code == httplib.NOT_FOUND:
                    raise GoalNotFound(goal_id, session.corpid)
                raise GoalError(primitive.status_message)

        def _timeout_handler(timeout_exception):
            logger.error('set_current_progress timed out: %s' % timeout_exception, exc_info=True)
            raise GoalError(timeout_exception)

        self._send_request_and_wait_for_response(request, SetCurrentProgressResponse, _response_handler, _timeout_handler)

    def _send_request_and_wait_for_response(self, request, expected_response_class, response_handler, timeout_handler = None):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, expected_response_class, UPDATE_TIMEOUT_SECONDS)
        try:
            response_primitive, payload = response_channel.receive()
            response_handler(response_primitive, payload)
        except TimeoutException as e:
            if timeout_handler is not None:
                timeout_handler(e)

    def _send_request(self, request, response_class, not_found_as_none = False):
        logger.info('Sending Request %s:\n%s', request.__class__.__name__, request)
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code == httplib.OK:
            logger.info('Send Request Response %s:\nRequest:\n%s\nResponse:\n%s', request.__class__.__name__, request, payload)
            return payload
        if not_found_as_none and response_primitive.status_code == httplib.NOT_FOUND:
            logger.warning('%s returned with statusCode %s, statusMessage: %s', request.DESCRIPTOR.name, response_primitive.status_code, response_primitive.status_message)
            return None
        logger.error('%s returned with statusCode %s, statusMessage: %s', request.DESCRIPTOR.name, response_primitive.status_code, response_primitive.status_message)
        raise GoalMessengerError(request.DESCRIPTOR.name, response_primitive.status_code)
