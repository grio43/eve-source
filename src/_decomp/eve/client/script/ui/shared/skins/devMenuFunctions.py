#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\skins\devMenuFunctions.py
from eve.client.script.ui.util.uix import ListWnd, QtyPopup
from eve.devtools.script.slashError import Error

def GiveSkin(materialID, typeID):
    skin = _PickSkinForMaterialAndType(materialID, typeID)
    duration = _SelectSkinDuration()
    if duration is None:
        return
    sm.RemoteSvc('shipCosmeticsMgr').GiveSkin(skin.skinID, duration=duration)


def GivePermanentSkin(materialID, typeID):
    skin = _PickSkinForMaterialAndType(materialID, typeID)
    sm.RemoteSvc('shipCosmeticsMgr').GiveSkin(skin.skinID)


def GiveLimitedSkin(materialID, typeID):
    skin = _PickSkinForMaterialAndType(materialID, typeID)
    sm.RemoteSvc('shipCosmeticsMgr').GiveSkin(skin.skinID, isSingleUse=True)


def GetSkinUsedWithTypeAndMaterial(materialID, typeID):
    return _PickSkinForMaterialAndType(materialID, typeID)


def GiveExpiredSkin(skinID):
    sm.RemoteSvc('shipCosmeticsMgr').GMExpireSkinLicense(skinID)


def _PickSkinForMaterialAndType(materialID, typeID):
    skins = _GetSkinsForTypeWithMaterial(materialID, typeID)
    if len(skins) == 0:
        message = 'No skins found for type {} that use material {}'.format(typeID, materialID)
        raise Error(message)
    else:
        if len(skins) == 1:
            return skins[0]
        return _SelectSkinFromList(skins)


def _GetSkinsForTypeWithMaterial(materialID, typeID):
    static = sm.GetService('cosmeticsSvc').static
    return static.GetSkinsForTypeWithMaterial(typeID, materialID)


def _SelectSkinFromList(skins):
    entry_list = [ (skin.internalName, skin) for skin in skins ]
    caption = 'AutoComplete: %d types found' % len(entry_list)
    selection = ListWnd(entry_list, listtype='generic', caption=caption)
    if len(selection) != 1:
        return None
    skin = selection[1]
    return skin


def _SelectSkinDuration():
    result = QtyPopup(minvalue=1, setvalue=1, caption='SKIN Duration', label='Set SKIN duration in days')
    if result is None:
        return
    return int(result['qty'])


def RemoveSkin(skinID):
    skin = sm.GetService('cosmeticsSvc').GetStaticSkinByID(skinID)
    if skin.isStructureSkin:
        licenseeID = session.corpid
    else:
        licenseeID = session.charid
    sm.RemoteSvc('shipCosmeticsMgr').RemoveSkin(skinID, licenseeID)
