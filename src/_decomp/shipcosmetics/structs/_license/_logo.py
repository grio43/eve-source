#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\structs\_license\_logo.py
__all__ = ['ShipLogoLicense']
from shipcosmetics.structs._license._abstract import AbstractShipCosmeticLicense
import evetypes
import localization
import logging
log = logging.getLogger(__name__)

class ShipLogoLicense(AbstractShipCosmeticLicense):

    def __init__(self, license_id, fsd_data_dict, *args, **kwargs):
        self._license_id = license_id
        self._fsd_data_dict = fsd_data_dict
        self._fsd_type = evetypes.GetType(self.fsdTypeID)
        self._ship_type = None

    @property
    def cosmeticType(self):
        return self._fsd_data_dict.cosmeticType

    @property
    def licenseID(self):
        return self._license_id

    @property
    def slotGroup(self):
        return self._fsd_data_dict.slotGroup

    @property
    def fsdTypeID(self):
        return self._fsd_data_dict.shipCosmeticLicenseTypeID

    @property
    def shipTypeID(self):
        return self._fsd_data_dict.shipTypeID

    @property
    def fsdType(self):
        return self._fsd_type

    @property
    def shipType(self):
        if self._ship_type is None:
            self._ship_type = evetypes.GetType(self.shipTypeID)
        return self._ship_type

    @property
    def iconID(self):
        return self.fsdType.iconID

    @property
    def name(self):
        return localization.Get(self.fsdType.typeNameID)

    @property
    def description(self):
        return localization.Get(self.fsdType.descriptionID)
