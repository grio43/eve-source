#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\messagebus\fleetMessenger.py
from eveProto.generated.eve_public.app.eveonline.fleet.analytics_pb2 import Created
from eveProto.generated.eve_public.app.eveonline.fleet.analytics_pb2 import AppliedToJoin

class FleetMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def fleet_created(self, fleet_id, ui_source):
        event = Created()
        event.fleet.generated = fleet_id
        event.ui_source = ui_source
        self.public_gateway.publish_event_payload(event)

    def applied_to_join(self, fleet_id, ui_source):
        event = AppliedToJoin()
        event.fleet.generated = fleet_id
        event.ui_source = ui_source
        self.public_gateway.publish_event_payload(event)
