#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\common\cosmeticlicenses\storage.py
import evetypes
from fsdBuiltData.common.base import BuiltDataLoader
from shipcosmetics.structs._license._logo import ShipLogoLicense
try:
    import shipCosmeticLicensesLoader
except ImportError:
    shipCosmeticLicensesLoader = None

class ShipCosmeticLicensesBuiltDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/shipCosmeticLicenses.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/shipCosmeticLicenses.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/shipCosmeticLicenses.fsdbinary'
    __loader__ = shipCosmeticLicensesLoader


class ShipCosmeticLicensesStaticData(object):

    def __init__(self):
        self._data = None
        self._id_by_type = None
        self._id_by_ship_and_cosmetic_type = None
        self._ship_groups = None

    @property
    def data(self):
        self._load_data()
        return self._data

    @property
    def id_by_type(self):
        self._load_data()
        return self._id_by_type

    @property
    def id_by_ship_and_cosmetic_type(self):
        self._load_data()
        return self._id_by_ship_and_cosmetic_type

    @property
    def ship_groups(self):
        self._load_data()
        return self._ship_groups

    def _load_data(self):
        if self._data is None:
            self._data = {}
            self._id_by_type = {}
            self._id_by_ship_and_cosmetic_type = {}
            self._ship_groups = set()
            loader = ShipCosmeticLicensesBuiltDataLoader()
            rawData = loader.GetData()
            for k, v in rawData.iteritems():
                logo = ShipLogoLicense(k, v)
                self._data[k] = logo
                self._id_by_type[logo.fsdTypeID] = k
                if logo.shipTypeID not in self._id_by_ship_and_cosmetic_type:
                    self._id_by_ship_and_cosmetic_type[logo.shipTypeID] = {}
                self._id_by_ship_and_cosmetic_type[logo.shipTypeID][logo.cosmeticType] = k
                self._ship_groups.add(evetypes.GetGroupID(logo.shipTypeID))

    def get_licenses_for_ship(self, ship_type):
        self._load_data()
        return {license_id:license for license_id, license in self.data.iteritems() if license.shipTypeID == ship_type}

    def get_license_for_ship_and_type(self, ship_type, cosmetic_type):
        self._load_data()
        for license_id, license in self.data.iteritems():
            if license.shipTypeID == ship_type and license.cosmeticType == cosmetic_type:
                return (license_id, license)

    def get_license(self, license_id):
        self._load_data()
        return self.data.get(license_id, None)

    def get_license_for_license_type_id(self, license_type_id):
        self._load_data()
        for value in self.data.itervalues():
            if value.fsdTypeID == license_type_id:
                return value

    def get_license_id_for_license_type_id(self, license_type_id):
        self._load_data()
        for key, value in self.data.iteritems():
            if value.fsdTypeID == license_type_id:
                return key
