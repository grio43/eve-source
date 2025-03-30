#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\message_bus\videoMessenger.py
from eveProto.generated.eve_public.app.eveonline.generic_ui.video.video_pb2 import Looped as VideoLooped
from eveProto.generated.eve_public.app.eveonline.generic_ui.video.video_pb2 import Seeked as VideoSeeked
from eveProto.generated.eve_public.app.eveonline.generic_ui.video.video_pb2 import Started as VideoStarted
from eveProto.generated.eve_public.app.eveonline.generic_ui.video.video_pb2 import Stopped as VideoStopped

class VideoMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def video_looped(self, hierarchy_path, video_path):
        event = VideoLooped()
        event.context.hierarchy_path = hierarchy_path
        event.video_path = video_path
        event.timestamp.GetCurrentTime()
        self.public_gateway.publish_event_payload(event)

    def video_seeked(self, hierarchy_path, video_path, new_position):
        event = VideoSeeked()
        event.context.hierarchy_path = hierarchy_path
        event.video_path = video_path
        event.new_position = new_position
        event.timestamp.GetCurrentTime()
        self.public_gateway.publish_event_payload(event)

    def video_started(self, hierarchy_path, video_path):
        event = VideoStarted()
        event.context.hierarchy_path = hierarchy_path
        event.video_path = video_path
        event.timestamp.GetCurrentTime()
        self.public_gateway.publish_event_payload(event)

    def video_stopped(self, hierarchy_path, video_path, played_to):
        event = VideoStopped()
        event.context.hierarchy_path = hierarchy_path
        event.video_path = video_path
        event.played_to = played_to
        event.timestamp.GetCurrentTime()
        self.public_gateway.publish_event_payload(event)
