#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\careergoals\client\messenger\request_messenger.py
import logging
from publicGateway.grpc.exceptions import GenericException
from eveProto.generated.eve_public.app.eveonline.career.goal_pb2 import GetAllRequest, GetAllResponse, ClaimRewardRequest, ClaimRewardResponse
from eveProto.generated.eve_public.career.goal.api.admin.requests_pb2 import CompleteRequest, CompleteResponse, ProgressRequest, ProgressResponse
from stackless_response_router.exceptions import TimeoutException
_TIMEOUT_SECONDS = 3
logger = logging.getLogger(__name__)

class PublicCareerGoalRequestMessenger(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get_goals_and_progress_request(self):
        request = GetAllRequest()
        info_log = 'CAREER GOALS - Get all goals and progress requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetAllResponse)
            if response_payload is None:
                info_log += 'Response: no data found. '
                return []
            info_log += 'Response: {amount} goals found. '.format(amount=len(response_payload.goals))
            return [ x for x in response_payload.goals ]
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get all goals and progress: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get all goals and progress: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def get_goals_definition_request(self):
        pass

    def get_goals_and_rewards_progress_request(self):
        pass

    def admin_complete_goal_request(self, goal_id):
        request = CompleteRequest()
        request.goal.uuid = goal_id.bytes
        info_log = 'CAREER GOALS - admin complete request for goal {goal_id}. '.format(goal_id=goal_id)
        try:
            self._blocking_request(request, CompleteResponse)
            info_log += 'Response: admin goal completed.'
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get admin complete goal: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to admin complete goal: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def admin_progress_goal_request(self, goal_id, progress):
        request = ProgressRequest()
        request.goal.uuid = goal_id.bytes
        request.progress = progress
        info_log = 'CAREER GOALS - admin progress request to progress {progress} for goal {goal_id}. '.format(progress=progress, goal_id=goal_id)
        try:
            self._blocking_request(request, ProgressResponse)
            info_log += 'Response: admin goal progressed.'
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get admin progress goal: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to admin progress goal: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def claim_reward_request(self, goal_id):
        request = ClaimRewardRequest()
        request.goal.uuid = goal_id.bytes
        info_log = 'CAREER GOALS - Claim reward requested, goal id %s. ' % goal_id
        try:
            self._blocking_request(request, ClaimRewardResponse)
            info_log += 'Response: claim successful. '
            return True
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to claim reward: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to claim reward: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def _blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, _TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code != 200:
            raise GenericException(request_primitive, response_primitive)
        return (response_primitive, payload)
