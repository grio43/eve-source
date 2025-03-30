#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\client\apis\licensegateway.py
__all__ = ['IClientShipCosmeticLicenseGateway']
import abc
from shipcosmetics.structs import *

class IClientShipCosmeticLicenseGateway(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def listOwnedLicenses(self, character_id):
        pass

    @abc.abstractmethod
    def listAll(self):
        pass

    @abc.abstractmethod
    def listAllShipGroups(self):
        pass

    @abc.abstractmethod
    def listByShipTypeId(self, ship_type_id):
        pass

    @abc.abstractmethod
    def listByCosmeticType(self, cosmetic_type):
        pass

    @abc.abstractmethod
    def getByLicenseId(self, license_id):
        pass

    @abc.abstractmethod
    def getByShipCosmeticLicenseTypeID(self, ship_cosmetic_license_type_id):
        pass

    @abc.abstractmethod
    def getByShipAndCosmeticType(self, ship_type_id, cosmetic_type):
        pass

    @abc.abstractmethod
    def getByShipItemIDAndCosmeticType(self, ship_item_id, cosmetic_type):
        pass

    @abc.abstractmethod
    def grantLicense_admin(self, character_id, license_id):
        pass

    @abc.abstractmethod
    def revokeLicense_admin(self, character_id, license_id):
        pass
