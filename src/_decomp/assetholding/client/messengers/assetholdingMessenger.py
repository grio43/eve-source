#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\assetholding\client\messengers\assetholdingMessenger.py
import uuid
import logging
import assetholding.client.messengers.assetholdingMessengerSignal as messenger_signals
from eveProto.generated.eve_public.assetholding.entitlement.api.notices_pb2 import RedeemedNotice
logger = logging.getLogger('asset_holding')

class AssetHoldingMessenger(object):
    _instance = None
    public_gateway = None

    @classmethod
    def get_instance(cls, public_gateway):
        if not cls._instance:
            cls._instance = AssetHoldingMessenger(public_gateway)
        return cls._instance

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self._subscribe_to_notices()

    def _subscribe_to_notices(self):
        self.public_gateway.subscribe_to_notice(RedeemedNotice, lambda payload, _: self._on_entitlement_redeemed(entitlement_id=payload.entitlement, change_quantity=payload.quantity))

    def _on_entitlement_redeemed(self, entitlement_id, change_quantity):
        logger.info('Entitlement Redeemed Notice: {} with quantity {}'.format(entitlement_id, change_quantity))
        external_id = uuid.UUID(bytes=entitlement_id.group_by.uuid)
        messenger_signals.on_entitlement_redeemed_internal(external_id, change_quantity)
