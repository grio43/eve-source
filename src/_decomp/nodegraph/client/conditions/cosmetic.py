#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\cosmetic.py
from .base import Condition
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType

class IsFirstPartySkinApplied(Condition):
    atom_id = 549

    def __init__(self, ship_id = None, skin_id = None):
        self.skin_id = skin_id
        self.ship_id = ship_id
        super(IsFirstPartySkinApplied, self).__init__()

    def _fetch_applied_skin_id(self):
        character_id = session.charid
        ship_id = self.ship_id or session.shipid
        skin_state = sm.GetService('cosmeticsSvc').GetAppliedSkinState(character_id, ship_id)
        if not skin_state or skin_state.skin_type != ShipSkinType.FIRST_PARTY_SKIN:
            return None
        return skin_state.skin_data.skin_id

    def validate(self, **kwargs):
        skin_id = self._fetch_applied_skin_id()
        return self.skin_id == skin_id


class IsAnyFirstPartySkinApplied(Condition):
    atom_id = 569

    def __init__(self, ship_id = None, skin_id_list = None):
        self.skin_id_list = skin_id_list
        self.ship_id = ship_id
        super(IsAnyFirstPartySkinApplied, self).__init__()

    def validate(self, **kwargs):
        if not self.skin_id_list:
            return False
        for skin_id in self.skin_id_list:
            if IsFirstPartySkinApplied(ship_id=self.ship_id, skin_id=skin_id).validate():
                return True

        return False


class IsSkinLicenseActivated(Condition):
    atom_id = 550

    def __init__(self, skin_id = None):
        self.skin_id = skin_id
        super(IsSkinLicenseActivated, self).__init__()

    def validate(self, **kwargs):
        licenced_skins = sm.GetService('cosmeticsSvc').GetLicensedSkins()
        for skin in licenced_skins:
            if skin.skinID == self.skin_id:
                return True

        return False


class IsAnySkinLicenseActivated(Condition):
    atom_id = 570

    def __init__(self, skin_id_list = None):
        self.skin_id_list = skin_id_list
        super(IsAnySkinLicenseActivated, self).__init__()

    def validate(self, **kwargs):
        if self.skin_id_list is None:
            return False
        for skin_id in self.skin_id_list:
            if IsSkinLicenseActivated(skin_id=skin_id).validate():
                return True

        return False
