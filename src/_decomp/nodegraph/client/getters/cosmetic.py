#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\cosmetic.py
from .base import GetterAtom

class GetSkinIdFromLicence(GetterAtom):
    atom_id = 554

    def __init__(self, type_id = None):
        self.type_id = type_id

    def get_values(self):
        if self.type_id is None:
            return
        skin = sm.GetService('cosmeticsSvc').GetSkinByLicenseType(self.type_id)
        if skin is None:
            return
        return {'skin_id': skin.skinID}
