#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\cosmeticsConst.py
from eve.common.lib import appConst
from shipcosmetics.common.const import CosmeticsType
from eve.common.lib.appConst import corpHeraldry
from notifications.common.notification import Notification
SEQUENCE_BINDER_TYPES = (appConst.typeFermionic, appConst.typeKerr, appConst.typeAlignment)
BACKGROUND_PATH_BY_TYPE = {CosmeticsType.NONE: '',
 CosmeticsType.CORPORATION_LOGO: 'res:/UI/Texture/classes/Fitting/Cosmetics/corp_logo_128px.png',
 CosmeticsType.ALLIANCE_LOGO: 'res:/UI/Texture/classes/Fitting/Cosmetics/alliance_logo_128px.png',
 CosmeticsType.SKIN: 'res:/UI/Texture/classes/Fitting/Cosmetics/skins_32px.png'}
ICON_PATH_BY_TYPE = {CosmeticsType.NONE: '',
 CosmeticsType.CORPORATION_LOGO: 'res:/UI/Texture/classes/Fitting/Cosmetics/corp_logo_24px.png',
 CosmeticsType.ALLIANCE_LOGO: 'res:/UI/Texture/classes/Fitting/Cosmetics/alliance_logo_24px.png',
 CosmeticsType.SKIN: ''}
HINT_BY_TYPE = {CosmeticsType.NONE: '',
 CosmeticsType.CORPORATION_LOGO: 'UI/ShipCosmetics/CorporationEmblem',
 CosmeticsType.ALLIANCE_LOGO: 'UI/ShipCosmetics/AllianceEmblem',
 CosmeticsType.SKIN: ''}
CATEGORY_NAME_BY_TYPE = {CosmeticsType.NONE: '',
 CosmeticsType.CORPORATION_LOGO: 'UI/ShipCosmetics/CorporationEmblems',
 CosmeticsType.ALLIANCE_LOGO: 'UI/ShipCosmetics/AllianceEmblems',
 CosmeticsType.SKIN: ''}
NOTIFICATION_BY_TYPE = {CosmeticsType.CORPORATION_LOGO: Notification.SHIP_CORP_COSMETIC_LICENSE_ACQUIRED,
 CosmeticsType.ALLIANCE_LOGO: Notification.SHIP_ALLIANCE_COSMETIC_LICENSE_ACQUIRED}
LP_STORE_CORP = corpHeraldry

def IsEmblemProviderCorp(corpID):
    return corpID == LP_STORE_CORP
