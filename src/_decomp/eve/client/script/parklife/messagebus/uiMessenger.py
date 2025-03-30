#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\messagebus\uiMessenger.py
from eveProto.generated.eve_public.app.eveonline.generic_ui.input.idle_pb2 import IdleThresholdReached, ActivityResumed

class UIMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def idle_threshold_reached(self, threshold):
        event = IdleThresholdReached()
        event.threshold.FromTimedelta(threshold)
        self.public_gateway.publish_event_payload(event)

    def activity_resumed(self):
        event = ActivityResumed()
        self.public_gateway.publish_event_payload(event)
