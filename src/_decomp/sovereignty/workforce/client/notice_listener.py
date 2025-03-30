#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\workforce\client\notice_listener.py
from eveProto.generated.eve_public.sovereignty.hub.workforce.api.notices_pb2 import ConfiguredNotice, StateChangedNotice
from signals import Signal
from sovereignty.workforce.client.data_types import WorkforceConfiguration, WorkforceState

class ExternalNoticeListener(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(ConfiguredNotice, self._on_hub_workforce_configured_notice)
        self.public_gateway.subscribe_to_notice(StateChangedNotice, self._on_hub_workforce_state_changed_notice)
        self.on_hub_workforce_configured_notice = Signal()
        self.on_hub_workforce_state_changed_notice = Signal()

    def _on_hub_workforce_configured_notice(self, payload, *args, **kwargs):
        solar_system_id = payload.solar_system.sequential
        hub_id = payload.hub.sequential
        old_configuration = payload.old_configuration
        old_workforce_configuration = WorkforceConfiguration.create_from_proto(hub_id, old_configuration)
        new_configuration = payload.new_configuration
        new_workforce_configuration = WorkforceConfiguration.create_from_proto(hub_id, new_configuration)
        self.on_hub_workforce_configured_notice(solar_system_id, hub_id, old_workforce_configuration, new_workforce_configuration)

    def _on_hub_workforce_state_changed_notice(self, payload, *args, **kwargs):
        solar_system_id = payload.solar_system.sequential
        hub_id = payload.hub.sequential
        old_state = payload.old_state
        old_workforce_state = WorkforceState.create_from_proto(hub_id, old_state)
        new_state = payload.new_state
        new_workforce_state = WorkforceState.create_from_proto(hub_id, new_state)
        self.on_hub_workforce_state_changed_notice(solar_system_id, hub_id, old_workforce_state, new_workforce_state)
