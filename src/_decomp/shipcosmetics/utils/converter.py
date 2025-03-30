#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\utils\converter.py
from cosmetics.client.messengers.entitlements.character.ship import KEY_SHIP_TYPE, KEY_TYPE
from eve.common.script.mgt.entitlements.types import SHIP_LOGO_ALLIANCE, SHIP_LOGO_CORPORATION
from shipcosmetics.common.const import CosmeticsType
_ENTITLEMENT_TYPES_TO_COSMETICS_TYPES = {SHIP_LOGO_ALLIANCE: CosmeticsType.ALLIANCE_LOGO,
 SHIP_LOGO_CORPORATION: CosmeticsType.CORPORATION_LOGO}

def get_entitlement_ship_type_id(entitlement):
    return entitlement.get(KEY_SHIP_TYPE, None)


def get_entitlement_cosmetic_type(entitlement):
    return _ENTITLEMENT_TYPES_TO_COSMETICS_TYPES.get(entitlement.get(KEY_TYPE, 0), CosmeticsType.NONE)
