#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\milestoneTimer\milestoneTimerMessenger.py
import logging
from eveProto.generated.eve_public.app.eveonline.login.milestone.tooltip_pb2 import Displayed
logger = logging.getLogger(__name__)

class MilestoneTimerMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def tooltip_displayed(self, milestone_id):
        if milestone_id is None:
            return
        event = Displayed()
        event.milestone.sequential = milestone_id
        self.public_gateway.publish_event_payload(event)
