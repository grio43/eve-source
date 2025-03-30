#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\shipUtil.py
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType

def get_active_ship_item_id():
    return session.shipid


def is_currently_applied_skin(skin_hex):
    applied_skin = get_active_ship_skin_state()
    if applied_skin.skin_type != ShipSkinType.THIRD_PARTY_SKIN:
        return False
    return applied_skin.skin_data.skin_id == skin_hex


def get_active_ship_type_id():
    return sm.GetService('godma').GetItem(get_active_ship_item_id()).typeID


def get_active_ship_skin_state():
    return sm.GetService('cosmeticsSvc').GetAppliedSkinState(session.charid, get_active_ship_item_id())


def apply_first_party_skin(skin_id):
    sm.RemoteSvc('shipCosmeticsMgr').ApplySkinToShip(get_active_ship_item_id(), skin_id)
