#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\careergoals\client\messenger\event_messenger.py
import logging
from eveProto.generated.eve_public.app.eveonline.career.career_pb2 import Selected as CareerSelected
from eveProto.generated.eve_public.app.eveonline.career.goal_pb2 import Tracked, Selected
from eveProto.generated.eve_public.app.eveonline.career.group_pb2 import Selected as GroupSelected
from eveexceptions import EatsExceptions
logger = logging.getLogger(__name__)
UPDATE_TIMEOUT_SECONDS = 10

class PublicCareerGoalEventMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    @EatsExceptions('protoClientLogs')
    def goal_tracked(self, goal_id):
        tracked = Tracked()
        tracked.goal.uuid = goal_id.bytes
        self.public_gateway.publish_event_payload(tracked)
        logger.info('CAREER GOALS - Tracked event published, payload: %s' % tracked)

    @EatsExceptions('protoClientLogs')
    def career_selected(self, goal_id):
        if not goal_id:
            return
        selected = CareerSelected()
        selected.goal.uuid = goal_id.bytes
        self.public_gateway.publish_event_payload(selected)
        logger.info('CAREER GOALS - CareerSelected event published, payload: %s' % selected)

    @EatsExceptions('protoClientLogs')
    def group_selected(self, group_name, career_name):
        selected = GroupSelected()
        selected.group = group_name
        selected.career = career_name
        self.public_gateway.publish_event_payload(selected)
        logger.info('CAREER GOALS - GroupSelected event published, payload: %s' % selected)

    @EatsExceptions('protoClientLogs')
    def goal_selected(self, goal_id):
        selected = Selected()
        selected.goal.uuid = goal_id.bytes
        self.public_gateway.publish_event_payload(selected)
        logger.info('CAREER GOALS - GoalSelected event published, payload: %s' % selected)
