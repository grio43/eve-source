#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\hub\client\notice_listener.py
from eveProto.generated.eve_public.sovereignty.hub.api.notices_pb2 import ResourcesSimulatedNotice
from signals import Signal
from sovereignty.resource.client.data_types import AvailableHubResources

class ExternalNoticeListener(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(ResourcesSimulatedNotice, self._on_resources_simulated_notice)
        self.on_resources_simulated_notice = Signal()

    def _on_resources_simulated_notice(self, payload, *args, **kwargs):
        hub_id = payload.hub.sequential
        solarsystem_id = payload.solar_system.sequential
        availableHubResources = AvailableHubResources(payload.power.allocated, payload.power.available, payload.power.local_harvest, payload.workforce.allocated, payload.workforce.available, payload.workforce.local_harvest)
        self.on_resources_simulated_notice(hub_id, solarsystem_id, availableHubResources)
