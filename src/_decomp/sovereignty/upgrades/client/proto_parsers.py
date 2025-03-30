#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\upgrades\client\proto_parsers.py
import sovereignty.upgrades.const as upgrades_const
try:
    from typing import List
except ImportError:
    pass

from eveProto.generated.eve_public.sovereignty.hub.upgrade.upgrade_pb2 import HubUpgrades
from eveProto.generated.eve_public.sovereignty.hub.upgrade.upgrade_pb2 import PowerState
from sovereignty.upgrades.client.data_types import InstalledUpgradeData
_proto_powerstate_to_python_powerstate = {PowerState.POWER_STATE_OFFLINE: upgrades_const.POWER_STATE_OFFLINE,
 PowerState.POWER_STATE_ONLINE: upgrades_const.POWER_STATE_ONLINE,
 PowerState.POWER_STATE_LOW: upgrades_const.POWER_STATE_LOW,
 PowerState.POWER_STATE_PENDING: upgrades_const.POWER_STATE_PENDING}

def parse_hub_upgrades(hub_upgrades):
    installed_upgrade_data = [ InstalledUpgradeData(upgrade_data.attributes.definition.installation_type.sequential, _proto_powerstate_to_python_powerstate.get(upgrade_data.attributes.power_state, None), (upgrade_data.identifier.hub.sequential, upgrade_data.identifier.upgrade_type.sequential)) for upgrade_data in hub_upgrades.upgrades ]
    return installed_upgrade_data
