#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\entitlements\character\ship\__init__.py
from eveProto.generated.eve_public.entitlement.character.ship.corplogo_pb2 import Identifier as CorpLogo
from eveProto.generated.eve_public.entitlement.character.ship.alliancelogo_pb2 import Identifier as AllianceLogo
from eve.common.script.mgt.entitlements import types
KEY_TYPE = 'entitlement_type'
KEY_SHIP_TYPE = 'ship_type_id'

def new_entitlement_from_type(pb_entitlement_type):
    entitlement_pb = getattr(pb_entitlement_type, pb_entitlement_type.WhichOneof('entitlement_type'))
    return new_entitlement(entitlement_pb)


def new_entitlement(pb_entitlement):
    f = character_ship_entitlement_factory[pb_entitlement.__class__]
    return f(pb_entitlement)


def new_alliance_logo_entitlement(alliance_logo_pb):
    return {KEY_TYPE: types.SHIP_LOGO_ALLIANCE,
     KEY_SHIP_TYPE: alliance_logo_pb.ship_type.sequential}


def new_corporation_logo_entitlement(corp_logo_pb):
    return {KEY_TYPE: types.SHIP_LOGO_CORPORATION,
     KEY_SHIP_TYPE: corp_logo_pb.ship_type.sequential}


character_ship_entitlement_factory = {CorpLogo: new_corporation_logo_entitlement,
 AllianceLogo: new_alliance_logo_entitlement}
