#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\static_data\first_party_skins.py
import blue
import localization
import evetypes
import fsdBuiltData.common.graphicMaterialSets as materialSets
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from localization.formatters.timeIntervalFormatters import FormatTimeIntervalShortWritten, TIME_CATEGORY_DAY, TIME_CATEGORY_MINUTE

class FirstPartyStaticLicense(object):

    def __init__(self, static, license):
        self._static = static
        self._license = license

    @property
    def typeID(self):
        return self._license.licenseTypeID

    @property
    def name(self):
        return evetypes.GetName(self._license.licenseTypeID)

    @property
    def duration(self):
        return self._license.duration

    @property
    def durationLabel(self):
        if self.is_single_use and self.duration != -1:
            return localization.GetByLabel('UI/Skins/SkinDurationSingleUseWithDuration', days=self.duration)
        if self.is_single_use:
            return localization.GetByLabel('UI/Skins/SkinDurationSingleUse')
        if self.duration == -1:
            return localization.GetByLabel('UI/Skins/SkinDurationPermanent')
        return localization.GetByLabel('UI/Skins/SkinDurationLimited', days=self.duration)

    @property
    def is_permanent(self):
        return self._license.duration == -1

    @property
    def is_single_use(self):
        return getattr(self._license, 'isSingleUse', False)

    @property
    def iconTexturePath(self):
        return _skin_icon_texture_path(self.skin.materialID)

    @property
    def skin(self):
        if not getattr(self, '_cached_skin', None):
            self._cached_skin = self._static.GetSkinByID(self._license.skinID)
        return FirstPartyStaticSkin(self._static, self._cached_skin)

    @property
    def material(self):
        return self.skin.material


class FirstPartyStaticSkin(object):

    def __init__(self, static, skin):
        self._static = static
        self._skin = skin

    @property
    def skinID(self):
        return self._skin.skinID

    @property
    def materialID(self):
        return self._skin.skinMaterialID

    @property
    def material(self):
        if not getattr(self, '_cached_material', None):
            self._cached_material = self._static.GetMaterialByID(self._skin.skinMaterialID)
        return FirstPartyStaticMaterial(self._static, self._cached_material)

    @property
    def types(self):
        return self._skin.types

    @property
    def licenses(self):
        licenses = self._static.GetLicencesForSkinID(self._skin.skinID)
        return [ FirstPartyStaticLicense(self._static, license) for license in licenses ]

    @property
    def isStructureSkin(self):
        return self._skin.isStructureSkin


class FirstPartyStaticMaterial(object):

    def __init__(self, static, material):
        self._static = static
        self._material = material

    @property
    def iconTexturePath(self):
        return _skin_icon_texture_path(self._material.skinMaterialID)

    @property
    def materialID(self):
        return self._material.skinMaterialID

    @property
    def materialSetID(self):
        return self._material.materialSetID

    @property
    def name(self):
        messageID = int(self._material.displayNameID)
        return localization.GetByMessageID(messageID)

    @property
    def skins(self):
        skins = self._static.GetSkinsForMaterialID(self._material.skinMaterialID)
        return [ FirstPartyStaticSkin(self._static, skin) for skin in skins ]


class FirstPartySkin(object):

    def __init__(self, material, skin = None, licensed = False, expires = None, isSingleUse = False, isStructureSkin = False):
        self._skin = skin
        self._material = material
        self._materialSet = materialSets.GetGraphicMaterialSet(self._material.materialSetID)
        self.licensed = licensed
        self.expires = expires
        self.isSingleUse = isSingleUse
        self.isStructureSkin = isStructureSkin

    @property
    def skinID(self):
        if self._skin:
            return self._skin.skinID
        else:
            return None

    @property
    def expired(self):
        return self.expires is not None and self.expires < blue.os.GetWallclockTime()

    @property
    def permanent(self):
        return self.expires is None

    def GetExpiresLabel(self):
        if not self.licensed:
            return
        if self.isSingleUse and self.expires:
            if self.expired:
                return localization.GetByLabel('UI/Skins/SkinDurationSingleUseLicenseExpired')
            else:
                duration = self.expires - blue.os.GetWallclockTime()
                expires = FormatTimeIntervalShortWritten(duration, showFrom=TIME_CATEGORY_DAY, showTo=TIME_CATEGORY_MINUTE)
                return localization.GetByLabel('UI/Skins/SkinDurationSingleUseLicenseExpiresIn', expires=expires)
        if self.isSingleUse:
            return localization.GetByLabel('UI/Skins/SkinDurationSingleUse')
        if self.expires is None:
            return localization.GetByLabel('UI/Skins/SkinDurationPermanent')
        duration = self.expires - blue.os.GetWallclockTime()
        if duration < 0:
            return localization.GetByLabel('UI/Skins/ExpiredLicense')
        expires = FormatTimeIntervalShortWritten(duration, showFrom=TIME_CATEGORY_DAY, showTo=TIME_CATEGORY_MINUTE)
        return localization.GetByLabel('UI/Skins/LicenseExpiresIn', expires=expires)

    @property
    def materialSetID(self):
        return self._material.materialSetID

    @property
    def materialID(self):
        return self._material.skinMaterialID

    @property
    def name(self):
        messageID = int(self._material.displayNameID)
        return localization.GetByMessageID(messageID)

    @property
    def types(self):
        return self._skin.types

    @property
    def iconTexturePath(self):
        return _skin_icon_texture_path(self._material.skinMaterialID)

    @property
    def colorPrimary(self):
        return materialSets.GetColorPrimary(self._materialSet)

    @property
    def colorSecondary(self):
        return materialSets.GetColorSecondary(self._materialSet)

    @property
    def colorHull(self):
        return materialSets.GetColorHull(self._materialSet)

    @property
    def colorWindows(self):
        return materialSets.GetColorWindows(self._materialSet)

    @property
    def skin_type(self):
        return ShipSkinType.FIRST_PARTY_SKIN

    def __eq__(self, other):
        if other is None:
            return False
        if not hasattr(other, 'skinID'):
            return False
        if not hasattr(other, 'materialID'):
            return False
        if not hasattr(other, 'licensed'):
            return False
        if not hasattr(other, 'expires'):
            return False
        return self.skinID == other.skinID and self.materialID == other.materialID and self.licensed == other.licensed and self.expires == other.expires

    def __repr__(self):
        return "<%s material='%s' skinID=%s licensed=%s expires='%s'>" % (self.__class__.__name__,
         self._material,
         self.skinID,
         self.licensed,
         self.expires)


def _skin_icon_texture_path(materialID):
    return 'res:/UI/Texture/classes/skins/icons/%s.png' % materialID
