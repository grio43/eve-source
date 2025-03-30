#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\assetholding\client\assetholdingController.py
import logging
from assetholding.client.messengers.assetholdingMessenger import AssetHoldingMessenger
import assetholding.client.messengers.assetholdingMessengerSignal as messenger_signals
from assetholding.client import assetholdingSignals
logger = logging.getLogger('asset_holding')

class AssetHoldingController(object):
    _instance = None

    def __init__(self):
        self._messenger = AssetHoldingMessenger.get_instance(sm.GetService('publicGatewaySvc'))
        self._connect_to_messenger_signals()

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = AssetHoldingController()
        return cls._instance

    def __del__(self):
        self._disconnect_from_messenger_signals()

    def _connect_to_messenger_signals(self):
        messenger_signals.on_entitlement_redeemed_internal.connect(self._on_entitlement_redeemed)

    def _disconnect_from_messenger_signals(self):
        messenger_signals.on_entitlement_redeemed_internal.disconnect(self._on_entitlement_redeemed)

    @staticmethod
    def _on_entitlement_redeemed(external_id, change_quantity):
        assetholdingSignals.on_entitlement_redeemed(external_id, change_quantity)
