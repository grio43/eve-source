#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\cosmeticsSvc.py
from carbon.common.script.sys.service import Service
from cosmetics.client.shipSkinStateController import ShipSkinStateController
from cosmetics.client.structureCosmeticStatesController import StructureCosmeticStatesController
from cosmetics.client.ships.skins.static_data.first_party_skins import FirstPartyStaticLicense, FirstPartyStaticSkin, FirstPartyStaticMaterial, FirstPartySkin
from eve.common.script.sys.idCheckers import IsShip
from eveprefs import boot
import shipskins
import evetypes
from localization import GetByMessageID
from shipLogoController import ShipLogoController
from eve.common.script.sys.idCheckers import IsCharacter, IsPlayerItem

class CosmeticsService(Service):
    __guid__ = 'svc.cosmeticsSvc'
    __startupdependencies__ = ['publicGatewaySvc']
    __notifyevents__ = ['OnSkinLicenseActivated',
     'OnSkinLicenseRemoved',
     'OnSessionReset',
     'OnSessionChanged']

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        sm.FavourMe(self.OnSkinLicenseActivated)
        sm.FavourMe(self.OnSkinLicenseRemoved)
        self._ship_logo_controller = ShipLogoController()
        self._structure_cosmetic_states_controller = StructureCosmeticStatesController(self._get_public_gateway())
        self._skin_state_controller = ShipSkinStateController(self.publicGatewaySvc)
        self.static = shipskins.SkinStaticData(region=boot.region)
        self.lastSkinChange = None
        self.ResetCache()

    def Stop(self, memStream = None):
        self._structure_cosmetic_states_controller.shutdown()
        self._skin_state_controller.shutdown()
        super(CosmeticsService, self).Stop(memStream)

    def _get_public_gateway(self):
        return sm.GetService('publicGatewaySvc')

    def OnSessionChanged(self, _is_remote, _session, change):
        if 'charid' in change:
            self._ship_logo_controller.flush_cache()
            self._skin_state_controller.on_character_changed()
        if 'solarsystemid' in change:
            self._start_structure_cosmetic_state_update(session.solarsystemid2)

    def OnSessionReset(self):
        self.ResetCache()

    def ResetCache(self):
        self.ResetPersonalCache()

    def ResetPersonalCache(self):
        self._licensedSkins = None
        self._licensedSkinsByType = {}

    def GetAppliedSkinStateForCurrentSession(self, itemID):
        return self.GetAppliedSkinState(session.charid, itemID)

    def GetAppliedSkinState(self, licenseeID, itemID):
        if not IsCharacter(licenseeID) or not IsPlayerItem(itemID):
            return None
        try:
            return self._skin_state_controller.get_skin_state(itemID, licenseeID)
        except Exception as exc:
            self.LogInfo('Failed to retrieve current SKIN for ship {ship_id}, returning default. {exc}'.format(ship_id=itemID, exc=exc))

    def GetCachedAppliedSkinState(self, licenseeID, itemID):
        if not IsPlayerItem(itemID):
            return None
        return self._skin_state_controller.get_cached_skin_state(itemID, licenseeID)

    def ActivateShipSkinLicense(self, itemIDs):
        sm.RemoteSvc('shipCosmeticsMgr').ActivateSkinLicense(itemIDs)

    def GetSkins(self, hullTypeID):
        if not self.IsShip(hullTypeID):
            return []
        skinsByMaterial = {}
        licensedSkins = self.GetLicensedSkinsForType(hullTypeID)
        if licensedSkins:
            for licensedSkin in licensedSkins:
                skin = self._CreateFirstPartySkinDataFromID(skinID=licensedSkin.skinID, licensed=True, expires=licensedSkin.expires, isSingleUse=licensedSkin.isSingleUse)
                skinsByMaterial[skin.materialID] = skin

        staticSkins = self.static.GetSkinsForTypeID(hullTypeID)
        if staticSkins:
            for skin in staticSkins:
                material = self.static.materials[skin.skinMaterialID]
                if material.skinMaterialID not in skinsByMaterial:
                    skinsByMaterial[material.skinMaterialID] = FirstPartySkin(material)

        return skinsByMaterial.values()

    def GetLicensedSkins(self):
        if self._licensedSkins is None:
            shipCosmeticsMgr = sm.RemoteSvc('shipCosmeticsMgr')
            self._licensedSkins = shipCosmeticsMgr.GetLicencedSkins()
        return self._licensedSkins

    def GetLicensedSkinsForType(self, typeID):
        if self.IsShip(typeID):
            return self._GetLicensedPersonalSkinsForType(typeID)

    def _GetLicensedPersonalSkinsForType(self, typeID):
        if typeID not in self._licensedSkinsByType:
            shipCosmeticsMgr = sm.RemoteSvc('shipCosmeticsMgr')
            licensedSkins = shipCosmeticsMgr.GetLicencedSkinsForShipType(session.charid, typeID)
            self._licensedSkinsByType[typeID] = licensedSkins
        return self._licensedSkinsByType[typeID]

    def GetFirstPartySkinObjectForCurrentSession(self, skinID):
        return self.GetFirstPartySkinObject(session.charid, skinID)

    def GetFirstPartySkinObject(self, licenseeID, skinID):
        skin_data = sm.RemoteSvc('shipCosmeticsMgr').GetFirstPartySkinData(licenseeID, skinID)
        if skin_data is None:
            return
        return self._CreateFirstPartySkinDataFromID(skinID, licensed=True, expires=skin_data.expires, isSingleUse=skin_data.isSingleUse)

    def GetFirstPartySkinMaterialID(self, skinID):
        return self.static.skins[skinID].skinMaterialID

    def GetFirstPartySkinMaterialSetID(self, skinID):
        skin = self.static.skins[skinID]
        material = self.static.materials[skin.skinMaterialID]
        return material.materialSetID

    def GetFirstPartySkinMaterialDisplayName(self, skinID):
        skin = self.static.skins[skinID]
        material = self.static.materials[skin.skinMaterialID]
        messageID = int(material.displayNameID)
        return GetByMessageID(messageID)

    def GetSkinByLicenseType(self, typeID):
        license = self.static.licenses[typeID]
        return self._CreateFirstPartySkinDataFromID(license.skinID)

    def InternalApplySkin(self, itemID, hullTypeID, skin):
        skinID = skin.skinID if skin is not None else None
        if self.IsShip(hullTypeID):
            sm.RemoteSvc('shipCosmeticsMgr').ApplySkinToShip(itemID, skinID)

    def _CreateFirstPartySkinDataFromID(self, skinID, licensed = False, expires = None, isSingleUse = False):
        skin = self.static.skins[skinID]
        material = self.static.materials[skin.skinMaterialID]
        return FirstPartySkin(material, skin=skin, licensed=licensed, expires=expires, isSingleUse=isSingleUse, isStructureSkin=skin.isStructureSkin)

    def CreateSkinObjectFromLicensedSkin(self, staticSkin, licensedSkin = None):
        licensed = licensedSkin is not None
        expires = licensedSkin.expires if licensedSkin else None
        isSingleUse = licensedSkin.isSingleUse if licensedSkin else None
        return self._CreateFirstPartySkinDataFromID(staticSkin.skinID, licensed=licensed, expires=expires, isSingleUse=isSingleUse)

    def GetStaticLicenseByID(self, typeID):
        return FirstPartyStaticLicense(self.static, self.static.GetLicenseByID(typeID))

    def GetStaticSkinByID(self, skinID):
        return FirstPartyStaticSkin(self.static, self.static.GetSkinByID(skinID))

    def GetStaticMaterialByID(self, materialID):
        return FirstPartyStaticMaterial(self.static, self.static.GetMaterialByID(materialID))

    def FindOffersForTypes(self, typeIDs):
        try:
            store = sm.GetService('vgsService').GetStore()
            offers = store.SearchOffersByTypeIDs(typeIDs)
            return offers
        except Exception as e:
            if len(e.args) >= 1 and e.args[0] == 'tokenMissing':
                self.LogWarn('Failed to search the NES for offers due to missing token')
            else:
                self.LogException('Failed to search the NES for offers')
            return []

    def FindOffersForTypeWithMaterial(self, typeID, materialID):
        licenseTypes = self.GetLicencesForTypeWithMaterial(typeID, materialID)
        return self.FindOffersForTypes(licenseTypes)

    def GetLicencesForTypeWithMaterial(self, typeID, materialID):
        licenses = self.static.GetLicensesForTypeWithMaterial(typeID, materialID)
        return [ l.licenseTypeID for l in licenses ]

    def OpenMarketForTypeWithMaterial(self, typeID, materialID):
        licenses = self.GetLicencesForTypeWithMaterial(typeID, materialID)
        if licenses:
            sm.GetService('marketutils').ShowMarketDetails(licenses[0])

    def OnSkinLicenseActivated(self, _skinID, licenseeID):
        if licenseeID == session.charid:
            self.ResetPersonalCache()

    def OnSkinLicenseRemoved(self, _skinID, itemID, typeID):
        self.ResetCache()

    def enable_ship_cosmetic_license(self, license, slotIndex, groupIndex, enable):
        return self._ship_logo_controller.enable_ship_cosmetic_license(license, slotIndex, groupIndex, enable)

    def get_enabled_ship_cosmetics(self, shipID, forceRefresh = False, raises = False):
        try:
            return self._ship_logo_controller.get_enabled_ship_cosmetics(shipID, forceRefresh)
        except RuntimeError:
            if raises:
                raise
            else:
                return []

    def are_ship_emblems_disabled(self):
        return self._ship_logo_controller.are_ship_emblems_disabled()

    def get_cached_structure_cosmetic_state(self, structure_id):
        return self._structure_cosmetic_states_controller.get_cached_cosmetic_state(structure_id)

    def get_structure_cosmetic_state(self, structure_id, solar_system_id, force_refresh = False):
        return self._structure_cosmetic_states_controller.get_cosmetic_state(structure_id, solar_system_id, force_refresh)

    def get_structure_cosmetic_license_id_from_state(self, structure_id, solar_system_id, force_refresh = False):
        return self._structure_cosmetic_states_controller.get_cosmetic_license_id(structure_id, solar_system_id, force_refresh)

    def _start_structure_cosmetic_state_update(self, solar_system_id):
        self._structure_cosmetic_states_controller.start_update(solar_system_id)

    def IsShip(self, typeID):
        return IsShip(evetypes.GetCategoryID(typeID))
