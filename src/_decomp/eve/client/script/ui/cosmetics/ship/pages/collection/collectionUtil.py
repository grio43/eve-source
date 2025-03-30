#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\collection\collectionUtil.py
from cosmetics.client.cosmeticsSvc import FirstPartySkin

def create_skin_object(static_skin, licensed_skin = None):
    material = sm.GetService('cosmeticsSvc').static.GetMaterialByID(static_skin.skinMaterialID)
    licensed = licensed_skin is not None
    expires = licensed_skin.expires if licensed_skin else None
    is_single_use = licensed_skin.isSingleUse if licensed_skin else None
    return FirstPartySkin(material, skin=static_skin, licensed=licensed, expires=expires, isSingleUse=is_single_use)


def get_first_party_skins():
    service = sm.GetService('cosmeticsSvc')
    licensed_skins_by_id = {s.skinID:s for s in service.GetLicensedSkins()}
    skins = []
    for static_skin in service.static.GetAllShipSkins():
        licensed_skin = licensed_skins_by_id.get(static_skin.skinID, None)
        skins.append(create_skin_object(static_skin, licensed_skin))

    all_licensed_skins = filter(lambda s: s.licensed, skins)
    return {s.skinID:s for s in all_licensed_skins}
