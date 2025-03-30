#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\careergoals\client\messenger\notice_messenger.py
import logging
import uuid
from careergoals.client.messenger.messenger_signal import *
from eveProto.generated.eve_public.app.eveonline.career.goal_pb2 import ProgressedNotice, CompletedNotice
logger = logging.getLogger(__name__)

class PublicCareerGoalNoticeMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(ProgressedNotice, self._on_progressed_notice)
        self.public_gateway.subscribe_to_notice(CompletedNotice, self._on_completed_notice)

    def _on_progressed_notice(self, notice_payload, _notice_primitive):
        logger.info('CAREER GOALS - progressed notice %s' % notice_payload)
        on_goal_progressed(uuid.UUID(bytes=notice_payload.goal.uuid), notice_payload.amount)

    def _on_completed_notice(self, notice_payload, _notice_primitive):
        logger.info('CAREER GOALS - completed notice %s' % notice_payload)
        on_goal_completed(uuid.UUID(bytes=notice_payload.goal.uuid))
