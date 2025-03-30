#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\message_bus\viewMessenger.py
from eveProto.generated.eve_public.app.eveonline.generic_ui.view.view_pb2 import Activated
from eveProto.generated.eve_public.app.eveonline.generic_ui.view.view_pb2 import Deactivated

class ViewMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def view_activated(self, view_name):
        event = Activated()
        event.view_unique_name = view_name
        self.public_gateway.publish_event_payload(event)

    def view_deactivated(self, view_name, seconds_active, nanoseconds_active):
        event = Deactivated()
        event.view_unique_name = view_name
        event.duration_active.seconds = seconds_active
        event.duration_active.nanos = nanoseconds_active
        self.public_gateway.publish_event_payload(event)
