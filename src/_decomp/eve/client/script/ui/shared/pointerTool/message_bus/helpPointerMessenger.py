#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\message_bus\helpPointerMessenger.py
from eveProto.generated.eve_public.app.eveonline.helperpointer.ui.link_pb2 import Created as LinkCreated
from eveProto.generated.eve_public.app.eveonline.helperpointer.ui.analytics_pb2 import Created as PointerCreated

class HelpPointerMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def pointer_created(self, pointer_unique_name, source_location_id):
        event = PointerCreated()
        event.pointer_unique_name = pointer_unique_name
        event.source_location = source_location_id
        self.public_gateway.publish_event_payload(event)

    def link_created(self, pointer_unique_name):
        event = LinkCreated()
        event.pointer_unique_name = pointer_unique_name
        self.public_gateway.publish_event_payload(event)
