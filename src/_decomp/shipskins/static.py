#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipskins\static.py
import fsdlite
import immutable
from itertools import chain
from shipskins.util import Base

class License(Base):
    __metaclass__ = immutable.Immutable
    MAPPING = []
    INDEXES = ['skinID.(?P<skinID>[0-9]+)$']

    def __new__(cls, *args, **kwargs):
        obj = Base.__new__(cls)
        obj.licenseTypeID = None
        obj.skinID = None
        obj.duration = None
        obj.isSingleUse = False
        return obj


License.MAPPING.append(('$', License))

def LicenseStorage():
    return fsdlite.EveStorage(data='skins/licenses', cache='skinLicenses.static', mapping=License.MAPPING, indexes=License.INDEXES)


class Skin(Base):
    __metaclass__ = immutable.Immutable
    MAPPING = []
    INDEXES = ['skinMaterialID.(?P<skinMaterialID>[0-9]+)',
     'types.(?P<typeID>[0-9]+)$',
     'allowCCPDevs.(?P<CCP>True|False)$',
     'visibleSerenity.(?P<SERENITY>True|False)$',
     'visibleTranquility.(?P<TRANQUILITY>True|False)$',
     'isStructureSkin.(?P<isStructureSkin>True|False)$']

    def __new__(cls, *args, **kwargs):
        obj = Base.__new__(cls)
        obj.skinID = None
        obj.skinMaterialID = None
        obj.types = []
        obj.internalName = None
        obj.visibleTranquility = False
        obj.visibleSerenity = False
        obj.allowCCPDevs = False
        obj.isStructureSkin = False
        return obj


Skin.MAPPING.append(('$', Skin))

def SkinStorage():
    return fsdlite.EveStorage(data='skins/skins', cache='skins.static', mapping=Skin.MAPPING, indexes=Skin.INDEXES)


class SkinMaterial(Base):
    __metaclass__ = immutable.Immutable
    MAPPING = []
    INDEXES = ['skinMaterialID.(?P<skinMaterialID>[0-9]+)']

    def __new__(cls, *args, **kwargs):
        obj = Base.__new__(cls)
        obj.skinMaterialID = None
        obj.materialSetID = None
        obj.displayNameID = None
        return obj


SkinMaterial.MAPPING.append(('$', SkinMaterial))

def SkinMaterialStorage():
    return fsdlite.EveStorage(data='skins/materials', cache='skinMaterials.static', mapping=SkinMaterial.MAPPING, indexes=SkinMaterial.INDEXES)


class SkinStaticData(object):

    def __init__(self, region):
        self.licenses = LicenseStorage()
        self.skins = SkinStorage()
        self.materials = SkinMaterialStorage()
        self._region = region

    def GetSkinByID(self, skinID):
        return self.skins.Get(skinID)

    def GetMaterialByID(self, materialID):
        return self.materials.Get(materialID)

    def GetMaterialBySkinId(self, skinID):
        skin = self.skins.Get(skinID)
        return self.materials.Get(skin.skinMaterialID)

    def GetLicenseByID(self, licenseID):
        return self.licenses.Get(licenseID)

    def GetSkinsForTypeID(self, typeID):
        skins_by_type = self.skins.filter('typeID', typeID)
        return self._FilterSkinsByRegion(skins_by_type)

    def GetLicensesForTypeID(self, typeID):
        skins = self.GetSkinsForTypeID(typeID)
        skinIDs = (skin.skinID for skin in skins)
        return list(chain.from_iterable(map(self.GetLicencesForSkinID, skinIDs)))

    def GetLicenseIDsForTypeID(self, typeID):
        licenses = self.GetLicensesForTypeID(typeID)
        return [ l.licenseTypeID for l in licenses ]

    def GetSkinsForTypeWithMaterial(self, typeID, materialID):
        skins = self.GetSkinsForMaterialID(materialID)
        skins = self._FilterSkinsByRegion(skins)
        return filter(lambda s: typeID in s.types, skins)

    def GetLicensesForTypeWithMaterial(self, typeID, materialID):
        skins = self.GetSkinsForTypeWithMaterial(typeID, materialID)
        skinIDs = (s.skinID for s in skins)
        return list(chain.from_iterable(map(self.GetLicencesForSkinID, skinIDs)))

    def AreAllLicensesSingleUse(self, typeID, materialID):
        licenses = self.GetLicensesForTypeWithMaterial(typeID, materialID)
        for license in licenses:
            if not license.isSingleUse:
                return False

        return True

    def GetSkinsForMaterialID(self, materialID):
        skins = self.skins.filter('skinMaterialID', materialID)
        return self._FilterSkinsByRegion(skins)

    def GetLicencesForSkinID(self, skinID):
        return self.licenses.filter('skinID', skinID)

    def GetSkinsForCcp(self):
        skins = self.skins.filter('CCP', True)
        return self._FilterSkinsByRegion(skins)

    def GetAllShipSkins(self):
        skinForRegion = self._FilterSkinsByRegion(self.skins.values())
        return self._FilterShipSkins(skinForRegion)

    def GetAllStructureSkins(self):
        skinForRegion = self._FilterSkinsByRegion(self.skins.values())
        return self._FilterStructureSkins(skinForRegion)

    def GetAllShipLicenses(self):
        skinIDs = (s.skinID for s in self.GetAllShipSkins())
        return list(chain.from_iterable(map(self.GetLicencesForSkinID, skinIDs)))

    def IsLicenseUsable(self, licenseID):
        license = self.GetLicenseByID(licenseID)
        skin = self.GetSkinByID(license.skinID)
        if self._region == 'optic':
            return skin.visibleSerenity
        else:
            return skin.visibleTranquility

    def _FilterSkinsByRegion(self, skins):
        if self._region == 'optic':
            return self._FilterSerenitySkins(skins)
        else:
            return self._FilterTranquilitySkins(skins)

    def _FilterSerenitySkins(self, skins):
        return filter(lambda s: s.visibleSerenity, skins)

    def _FilterTranquilitySkins(self, skins):
        return filter(lambda s: s.visibleTranquility, skins)

    def _FilterShipSkins(self, skins):
        return filter(lambda s: not s.isStructureSkin, skins)

    def _FilterStructureSkins(self, skins):
        return filter(lambda s: s.isStructureSkin, skins)
