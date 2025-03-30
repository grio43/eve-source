#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\cosmetic.py
from .base import Event

class CurrentShipSkinChange(Event):
    atom_id = 547
    __notifyevents__ = ['OnCurrentShipSkinChange']

    def OnCurrentShipSkinChange(self, ship_id, skin_id):
        self.invoke(ship_id=ship_id, skin_id=skin_id)


class SkinLicenseChanged(Event):
    atom_id = 548
    __notifyevents__ = ['OnSkinLicenseActivated']

    def OnSkinLicenseActivated(self, skin_id, character_id):
        self.invoke(character_id=character_id, skin_id=skin_id)
