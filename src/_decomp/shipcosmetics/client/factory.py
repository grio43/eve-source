#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\client\factory.py
__all__ = ['ShipCosmeticGatewayFactory']
from typeutils import metas
from shipcosmetics.client.apis import *
from shipcosmetics.common.cosmeticlicenses.storage import ShipCosmeticLicensesStaticData
from shipcosmetics.client.licensegateway.quasar import ClientShipCosmeticLicenseGateway
from shipcosmetics.client.fittingsgateway.quasar import QuasarClientShipCosmeticFittingGateway as ClientShipCosmeticFittingGateway

class ShipCosmeticGatewayFactory:
    __metaclass__ = metas.Singleton

    def __init__(self):
        self._license_storage = ShipCosmeticLicensesStaticData()
        self._license_gw = ClientShipCosmeticLicenseGateway(self._get_public_gateway(), self.license_storage)
        self._fitting_gw = ClientShipCosmeticFittingGateway(self._get_public_gateway(), self._license_gw)

    def _get_public_gateway(self):
        return sm.GetService('publicGatewaySvc')

    @property
    def license_gateway(self):
        return self._license_gw

    @property
    def fittings_gateway(self):
        return self._fitting_gw

    @property
    def license_storage(self):
        return self._license_storage
