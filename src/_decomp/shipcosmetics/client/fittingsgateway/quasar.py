#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\client\fittingsgateway\quasar.py
__all__ = ['QuasarClientShipCosmeticFittingGateway']
from shipcosmetics.client.apis.fittingsgateway import *
from shipcosmetics.structs import *
from shipcosmetics.utils.indexcast import *
from shipcosmetics.utils import checker
from cosmetics.client.messengers.cosmetics.ship import shipEmblemsRequestMessenger as requestMessenger
from signals import Signal
import uthread
import uthread2
import logging
log = logging.getLogger(__name__)
on_ship_cosmetics_changed_internal = Signal(signalName='on_ship_cosmetics_changed_internal')
SET_COSMETIC_TIMEOUT_SEC = 5

class QuasarClientShipCosmeticFittingGateway(IClientShipCosmeticFittingGateway):
    __notifyevents__ = ['OnShipCosmeticsChanged', 'OnShipCosmeticChanged']

    def __init__(self, publicGatewaySvc, license_gateway):
        self._quasar_gw = requestMessenger.PublicShipEmblemsRequestsMessenger(publicGatewaySvc.publicGateway)
        self._license_gw = license_gateway
        self.pending_changes_channels = {}
        sm.RegisterNotify(self)

    def _get_character_id(self):
        return session.charid

    def getShipCosmeticFitting(self, ship_item_id):
        try:
            enabledCosmetics = sm.RemoteSvc('shipCosmeticsMgr').GetEnabledCosmetics(ship_item_id)
        except Exception as ex:
            error_msg = 'Could not fetch enabled ship cosmetics: %s' % ex
            log.exception(error_msg)
            raise RuntimeError(error_msg)

        fitting = ShipCosmeticFitting(ship_item_id, self._get_character_id())
        if enabledCosmetics is not None:
            for backend_slot_index, cosmetic_type in enabledCosmetics.iteritems():
                group_index, slot_index = backend_to_group_and_slot_index(backend_slot_index)
                license = self._license_gw.getByShipItemIDAndCosmeticType(ship_item_id, cosmetic_type)
                if license:
                    fitting.set_slot(group_index, slot_index, ShipCosmeticLogo(license))

        return fitting

    def setShipCosmeticFittingModule(self, ship_cosmetic_module, slot_index, group_index, ship_item_id):
        backend_slot = group_and_slot_index_to_backend(group_index, slot_index)
        channel = uthread.Channel(('shiplogocontroller::_EnableCosmeticLicense', '%s::%s' % (ship_item_id, backend_slot)))
        self.pending_changes_channels[ship_item_id, backend_slot] = channel
        uthread2.start_tasklet(self._SetShipCosmeticFittingModuleTimeout, channel, SET_COSMETIC_TIMEOUT_SEC)
        try:
            if not ship_cosmetic_module:
                self._quasar_gw.clear_logo(ship_item_id, backend_slot)
            elif checker.is_corp_logo(ship_cosmetic_module):
                self._quasar_gw.display_corporation_logo(ship_item_id, backend_slot)
            elif checker.is_alliance_logo(ship_cosmetic_module):
                self._quasar_gw.display_alliance_logo(ship_item_id, backend_slot)
            else:
                error_msg = 'Tried to use an unsupported cosmetic type logo: %s' % ship_cosmetic_module.getCosmeticType()
                log.error(error_msg)
                raise ValueError(error_msg)
        except Exception as ex:
            error_msg = 'Could not set ship cosmetic module: %s' % ex
            log.exception(error_msg)
            raise RuntimeError(error_msg)

        ok = channel.receive()
        self.pending_changes_channels.pop((ship_item_id, backend_slot))
        if not ok:
            error_msg = 'Timeout when setting ship cosmetic module'
            log.error(error_msg)
            raise RuntimeError(error_msg)
        return ok

    def OnShipCosmeticsChanged(self, ship_id, cosmetics):
        on_ship_cosmetics_changed_internal(ship_id, cosmetics.values())

    def OnShipCosmeticChanged(self, ship_id, slot_index, cosmetic):
        if (ship_id, slot_index) in self.pending_changes_channels:
            self.pending_changes_channels[ship_id, slot_index].send(True)

    @staticmethod
    def _SetShipCosmeticFittingModuleTimeout(channel, seconds):
        uthread2.sleep(seconds)
        channel.send(False)
