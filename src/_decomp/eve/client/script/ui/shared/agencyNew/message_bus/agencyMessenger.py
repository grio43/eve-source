#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\message_bus\agencyMessenger.py
import logging
from stackless_response_router.exceptions import TimeoutException
from eveProto.generated.eve_public.app.eveonline.agency.ui.action_pb2 import Taken as ActionTaken
from eveProto.generated.eve_public.app.eveonline.agency.ui.bookmark_pb2 import Added as BookmarkAdded
from eveProto.generated.eve_public.app.eveonline.agency.ui.filter_pb2 import Changed as FilterChanged
from eveProto.generated.eve_public.app.eveonline.agency.ui.content_pb2 import CardClicked as ContentCardClicked
from eveProto.generated.eve_public.app.eveonline.agency.ui.group_pb2 import CardClicked as GroupCardClicked
from eveProto import split_precision
from eveProto.generated.eve_public.app.eveonline.agency.ui.help.video.link_pb2 import Created, Clicked
logger = logging.getLogger(__name__)

class AgencyMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def action_taken(self, action_id, content_id):
        event = ActionTaken()
        event.action = action_id
        event.content = content_id
        self.public_gateway.publish_event_payload(event)

    def bookmark_added(self, group_id):
        event = BookmarkAdded()
        event.group = group_id
        self.public_gateway.publish_event_payload(event)

    def filter_changed(self, filter_id, group_id, filter_value):
        event = FilterChanged()
        event.filter = filter_id
        event.group = group_id
        event.value = filter_value
        self.public_gateway.publish_event_payload(event)

    def content_card_clicked(self, content_id, num_jumps, security_status):
        event = ContentCardClicked()
        units, nanos = split_precision(security_status)
        event.content = content_id
        event.jumps = num_jumps
        event.security_status.units = units
        event.security_status.nanos = nanos
        self.public_gateway.publish_event_payload(event)

    def group_card_clicked(self, group_id):
        event = GroupCardClicked()
        event.group = group_id
        self.public_gateway.publish_event_payload(event)

    def help_video_link_created(self, video_path):
        event = Created()
        event.video_path = video_path
        self.public_gateway.publish_event_payload(event)

    def help_video_link_clicked(self, video_path):
        event = Clicked()
        event.video_path = video_path
        self.public_gateway.publish_event_payload(event)

    def _send_request_and_wait_for_response(self, request, expected_response_class, response_handler, timeout_handler = None):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, expected_response_class, 10)
        try:
            response_primitive, payload = response_channel.receive()
            response_handler(response_primitive, payload)
        except TimeoutException as e:
            if timeout_handler is not None:
                timeout_handler(e)
