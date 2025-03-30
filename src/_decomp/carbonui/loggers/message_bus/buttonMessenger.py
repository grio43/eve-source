#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\loggers\message_bus\buttonMessenger.py
from eveProto.generated.eve_public.app.eveonline.generic_ui.button.analytics_pb2 import Clicked as ButtonClicked

class ButtonMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def button_clicked(self, hierarchy_path, unique_name):
        event = ButtonClicked()
        event.context.hierarchy_path = hierarchy_path
        event.button.name = str(unique_name)
        self.public_gateway.publish_event_payload(event)
