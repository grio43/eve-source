#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\journey\journey_messanger.py
import logging
from journey.tracker import create_journey_id_link
from eveProto.generated.eve_public.public_pb2 import JourneyLinked
logger = logging.getLogger(__name__)

class JourneyMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def linked(self, reason = 'Unknown'):
        event = JourneyLinked()
        event.journey = create_journey_id_link()
        event.reason = reason
        self.public_gateway.publish_event_payload(event)
        logger.info('Creating new journey link with reason= %s' % reason)
