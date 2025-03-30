#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\client\goals\goalFormsMessenger.py
import logging
from eveProto.generated.eve_public.goal.api.events_pb2 import CloneFormOpened
logger = logging.getLogger('corporation_goals')

class GoalFormsMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def clone_form_opened(self, goalID):
        event = CloneFormOpened()
        event.id.uuid = goalID.bytes
        self.public_gateway.publish_event_payload(event)
        logger.info('Clone Form Opened for goal_id: %s' % goalID)
