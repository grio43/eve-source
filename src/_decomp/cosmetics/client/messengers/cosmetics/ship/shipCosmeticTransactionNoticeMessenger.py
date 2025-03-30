#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipCosmeticTransactionNoticeMessenger.py
import logging
import uuid
from cosmetics.client.ships.ship_skin_svc_signals import *
from eveProto.generated.eve_public.cosmetic.market.transaction.api.notices_pb2 import TransactionSucceededNotice, TransactionFailedNotice
logger = logging.getLogger(__name__)

class PublicShipCosmeticTransactionNoticeMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(TransactionSucceededNotice, self._on_transaction_succeeded_notice)
        self.public_gateway.subscribe_to_notice(TransactionFailedNotice, self._on_transaction_failed_notice)

    def _on_transaction_succeeded_notice(self, notice_payload, _notice_primitive):
        transaction_id = uuid.UUID(bytes=notice_payload.transaction.uuid)
        on_transaction_succeeded_internal(transaction_id)

    def _on_transaction_failed_notice(self, notice_payload, _notice_primitive):
        transaction_id = uuid.UUID(bytes=notice_payload.transaction.uuid)
        on_transaction_failed_internal(transaction_id)
