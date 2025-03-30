#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\structs\_modules\_logo.py
__all__ = ['ShipCosmeticLogo']
from shipcosmetics.structs import AbstractShipCosmeticLicense
from shipcosmetics.structs._modules._abstract import AbstractShipCosmeticModule
import logging
log = logging.getLogger(__name__)

class ShipCosmeticLogo(AbstractShipCosmeticModule):

    def __init__(self, license, *args, **kwargs):
        super(ShipCosmeticLogo, self).__init__(license, *args, **kwargs)
