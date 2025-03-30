#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\shipEmblemLicensesController.py
import blue
import evetypes
from carbon.common.script.sys.serviceConst import ROLE_GML
from cosmetics.common.cosmeticsConst import NOTIFICATION_BY_TYPE
from shipcosmetics.client.factory import ShipCosmeticGatewayFactory
from shipcosmetics.client.licensegateway.licenseSignals import on_ship_cosmetics_license_change
from shipcosmetics.client.licensegateway.quasar import on_ship_license_changed_internal
from notifications.common.notification import Notification
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException

class ShipEmblemLicensesController(object):

    def __init__(self):
        self._cache = None
        self._ship_license_gateway = ShipCosmeticGatewayFactory().license_gateway
        on_ship_license_changed_internal.connect(self._on_ship_license_changed)

    def _refresh_cache(self):
        self._cache = self._ship_license_gateway.listOwnedLicenses(session.charid)

    def flush_cache(self):
        self._cache = None

    def is_ship_license_owned(self, license_id):
        return any((license.licenseID == license_id for license in self.get_owned_ship_licenses()))

    def get_all_ship_licenses(self):
        return self._ship_license_gateway.listAll()

    def get_all_licensed_ship_groups(self):
        return self._ship_license_gateway.listAllShipGroups()

    def get_owned_ship_licenses(self, force_refresh = False):
        if force_refresh or self._cache is None:
            self._refresh_cache()
        return self._cache

    def get_unowned_ship_licenses(self, force_refresh = False):
        owned_licenses = set(self.get_owned_ship_licenses(force_refresh))
        all_licenses = set(self.get_all_ship_licenses())
        return all_licenses.difference(owned_licenses)

    def get_owned_ship_licenses_for_ship(self, ship_id, force_refresh = False):
        licenses = self.get_owned_ship_licenses(force_refresh)
        ship_item = sm.GetService('godma').GetItem(ship_id)
        if ship_item is not None:
            return [ license for license in licenses if license.shipTypeID == ship_item.typeID ]
        else:
            return []

    def get_ship_licenses_for_ship_type(self, ship_type_id):
        return self._ship_license_gateway.listByShipTypeId(ship_type_id)

    def get_by_ship_license_type_id(self, license_id):
        return self._ship_license_gateway.getByShipCosmeticLicenseTypeID(license_id)

    def _on_ship_license_changed(self, license, granted):
        self.flush_cache()
        on_ship_cosmetics_license_change(license.licenseID, granted)
        if granted:
            self._trigger_ship_license_granted_notification(license)

    def _trigger_ship_license_granted_notification(self, license):
        license = self._ship_license_gateway.getByLicenseId(license.licenseID)
        if license:
            notification_type = NOTIFICATION_BY_TYPE.get(license.cosmeticType, None)
            if notification_type is not None:
                notification = Notification.MakeShipCosmeticLicenseAcquiredNotification(notificationType=notification_type, header=GetByLabel('UI/ShipCosmetics/ShipCosmeticsLicenseGrantedNotification', licenseName=evetypes.GetName(license.fsdTypeID)), body=GetByLabel('UI/ShipCosmetics/ShipCosmeticsLicenseGrantedNotificationBody', shipName=evetypes.GetName(license.shipTypeID)), createdTime=blue.os.GetWallclockTime(), callback=None)
                sm.ScatterEvent('OnNewNotificationReceived', notification)

    def debug_grant_ship_cosmetics_license(self, license_id):
        if session.role & ROLE_GML:
            channel = self._ship_license_gateway.grantLicense_admin(session.charid, license_id)
            try:
                channel.receive()
            except GenericException:
                pass
            finally:
                on_ship_cosmetics_license_change(license_id, True)

    def debug_revoke_ship_cosmetics_license(self, license_id):
        if session.role & ROLE_GML:
            channel = self._ship_license_gateway.revokeLicense_admin(session.charid, license_id)
            try:
                channel.receive()
            except GenericException:
                pass
            finally:
                on_ship_cosmetics_license_change(license_id, False)
