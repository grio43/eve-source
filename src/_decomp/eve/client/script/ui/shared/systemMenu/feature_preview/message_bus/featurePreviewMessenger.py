#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\feature_preview\message_bus\featurePreviewMessenger.py
from eveProto.generated.eve_public.app.eveonline.settings.featurepreview.analytics_pb2 import Toggled

class FeaturePreviewMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def feature_toggled(self, feature_name, state):
        event = Toggled()
        event.feature_name = feature_name
        event.state = state
        self.public_gateway.publish_event_payload(event)
