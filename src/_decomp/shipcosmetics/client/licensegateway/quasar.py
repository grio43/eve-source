#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\client\licensegateway\quasar.py
__all__ = ['ClientShipCosmeticLicenseGateway', 'on_ship_license_changed_internal']
from eve.common.script.sys.eveCfg import IsDocked, IsControllingStructure
from shipcosmetics.common.const import CosmeticsType
from shipcosmetics.client.apis.licensegateway import *
from cosmetics.client.messengers.entitlements.character.ship.noticeMessenger import NoticeMessenger
from cosmetics.client.messengers.entitlements.character.ship.requestMessenger import PublicEntitlementsRequestsMessenger
from cosmetics.client.messengers.entitlements.character.ship.admin.requestMessenger import PublicEntitlementsAdministrativeRequestsMessenger
from shipcosmetics.utils.converter import get_entitlement_cosmetic_type, get_entitlement_ship_type_id
from signals import Signal
import logging
log = logging.getLogger(__name__)
on_ship_license_changed_internal = Signal(signalName='on_ship_license_changed_internal')

class ClientShipCosmeticLicenseGateway(IClientShipCosmeticLicenseGateway):

    def __init__(self, publicGatewaySvc, licensesStorage):
        self._licensesStorage = licensesStorage
        self._entitlementNoticeMessenger = NoticeMessenger(publicGatewaySvc.publicGateway)
        self._entitlementNoticeMessenger.on_corp_logo_granted.connect(self._OnLogoGranted)
        self._entitlementNoticeMessenger.on_alliance_logo_granted.connect(self._OnLogoGranted)
        self._entitlementNoticeMessenger.on_corp_logo_revoked.connect(self._OnLogoRevoked)
        self._entitlementNoticeMessenger.on_alliance_logo_revoked.connect(self._OnLogoRevoked)
        self._entitlementRequestMessenger = PublicEntitlementsRequestsMessenger(publicGatewaySvc.publicGateway)
        self._adminEntitlementRequestMessenger = PublicEntitlementsAdministrativeRequestsMessenger(publicGatewaySvc.publicGateway)

    def __del__(self):
        if self._entitlementNoticeMessenger:
            self._entitlementNoticeMessenger.on_corp_logo_granted.disconnect(self._OnLogoGranted)
            self._entitlementNoticeMessenger.on_alliance_logo_granted.disconnect(self._OnLogoGranted)
            self._entitlementNoticeMessenger.on_corp_logo_revoked.disconnect(self._OnLogoRevoked)
            self._entitlementNoticeMessenger.on_alliance_logo_revoked.disconnect(self._OnLogoRevoked)

    def listOwnedLicenses(self, character_id):
        try:
            entitlements = self._entitlementRequestMessenger.get_owned_ship_logos()
        except Exception as ex:
            error_msg = 'Could not fetch owned ship cosmetic licenses: %s' % ex
            log.exception(error_msg)
            raise RuntimeError(error_msg)

        licenses = []
        for entitlement in entitlements:
            license = self.getByShipAndCosmeticType(get_entitlement_ship_type_id(entitlement), get_entitlement_cosmetic_type(entitlement))
            if license:
                licenses.append(license)

        return licenses

    def listAll(self):
        return self._licensesStorage.data.itervalues()

    def listAllShipGroups(self):
        return self._licensesStorage.ship_groups

    def listByShipTypeId(self, ship_type_id):
        return (self.getByLicenseId(lid) for lid in self._licensesStorage.id_by_ship_and_cosmetic_type.get(ship_type_id, {}).itervalues())

    def listByCosmeticType(self, cosmetic_type):
        return (logo for logo in self._licensesStorage.data.itervalues() if logo.cosmeticType == cosmetic_type)

    def getByLicenseId(self, license_id):
        return self._licensesStorage.data.get(license_id, None)

    def getByShipCosmeticLicenseTypeID(self, ship_cosmetic_license_type_id):
        return self.getByLicenseId(self._licensesStorage.id_by_type.get(ship_cosmetic_license_type_id, None))

    def getByShipAndCosmeticType(self, ship_type_id, cosmetic_type):
        return self.getByLicenseId(self._licensesStorage.id_by_ship_and_cosmetic_type.get(ship_type_id, {}).get(cosmetic_type, None))

    def getByShipItemIDAndCosmeticType(self, ship_item_id, cosmetic_type):
        typeID = None
        if not IsDocked() and not IsControllingStructure() or ship_item_id == session.shipid:
            item = sm.GetService('godma').GetItem(ship_item_id)
            if item is not None:
                typeID = item.typeID
            else:
                log.exception('Could not find ship godma item when looking up cosmetic license')
        else:
            ship = sm.GetService('invCache').GetInventoryFromId(ship_item_id)
            if ship is not None:
                typeID = ship.typeID
            else:
                log.exception('Could not find ship inventory item when looking up cosmetic license')
        if typeID:
            return self.getByShipAndCosmeticType(typeID, cosmetic_type)
        else:
            return

    def grantLicense_admin(self, character_id, license_id):
        licenseData = self.getByLicenseId(license_id)
        if licenseData.cosmeticType == CosmeticsType.CORPORATION_LOGO:
            return self._adminEntitlementRequestMessenger.grant_corp_logo(character_id, licenseData.shipTypeID)
        if licenseData.cosmeticType == CosmeticsType.ALLIANCE_LOGO:
            return self._adminEntitlementRequestMessenger.grant_alliance_logo(character_id, licenseData.shipTypeID)

    def revokeLicense_admin(self, character_id, license_id):
        licenseData = self.getByLicenseId(license_id)
        if licenseData.cosmeticType == CosmeticsType.CORPORATION_LOGO:
            return self._adminEntitlementRequestMessenger.revoke_corp_logo(character_id, licenseData.shipTypeID)
        if licenseData.cosmeticType == CosmeticsType.ALLIANCE_LOGO:
            return self._adminEntitlementRequestMessenger.revoke_alliance_logo(character_id, licenseData.shipTypeID)

    def _OnLogoGranted(self, entitlement):
        licenseID = self.getByShipAndCosmeticType(get_entitlement_ship_type_id(entitlement), get_entitlement_cosmetic_type(entitlement))
        on_ship_license_changed_internal(licenseID, True)

    def _OnLogoRevoked(self, entitlement):
        licenseID = self.getByShipAndCosmeticType(get_entitlement_ship_type_id(entitlement), get_entitlement_cosmetic_type(entitlement))
        on_ship_license_changed_internal(licenseID, False)
