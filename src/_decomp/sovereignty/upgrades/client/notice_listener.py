#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\upgrades\client\notice_listener.py
from eveProto import timestamp_to_blue
from eveProto.generated.eve_public.sovereignty.hub.upgrade.api.notices_pb2 import HubUpgradesConfiguredNotice, HubUpgradesSimulatedNotice
from signals import Signal
from sovereignty.upgrades.client.proto_parsers import parse_hub_upgrades

class ExternalNoticeListener(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(HubUpgradesConfiguredNotice, self._on_hub_upgrades_configured_notice)
        self.public_gateway.subscribe_to_notice(HubUpgradesSimulatedNotice, self._on_hub_upgrades_state_changed_notice)
        self.on_hub_upgrades_configured_notice = Signal()
        self.on_hub_upgrades_state_changed_notice = Signal()

    def _on_hub_upgrades_configured_notice(self, payload, *args, **kwargs):
        hub_id = payload.hub_upgrades.hub.sequential
        installed_upgrade_data = parse_hub_upgrades(payload.hub_upgrades)
        fuel_last_updated = timestamp_to_blue(payload.hub_upgrades.last_updated)
        self.on_hub_upgrades_configured_notice(hub_id, installed_upgrade_data, fuel_last_updated)

    def _on_hub_upgrades_state_changed_notice(self, payload, *args, **kwargs):
        hub_id = payload.hub_upgrades.hub.sequential
        installed_upgrade_data = parse_hub_upgrades(payload.hub_upgrades)
        fuel_last_updated = timestamp_to_blue(payload.hub_upgrades.last_updated)
        self.on_hub_upgrades_state_changed_notice(hub_id, installed_upgrade_data, fuel_last_updated)
