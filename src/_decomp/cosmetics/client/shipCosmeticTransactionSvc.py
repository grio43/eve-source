#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\shipCosmeticTransactionSvc.py
import uthread2
import uuid
import logging
from cosmetics.client.messengers.cosmetics.ship.shipCosmeticTransactionNoticeMessenger import PublicShipCosmeticTransactionNoticeMessenger
from cosmetics.client.ships import ship_skin_svc_signals
from stackless_response_router.exceptions import TimeoutException
logger = logging.getLogger(__name__)
_instance = None

def get_ship_cosmetic_transaction_svc():
    global _instance
    if _instance is None:
        _instance = _ShipCosmeticTransactionSvc()
    return _instance


TRANSACTION_TIMEOUT_IN_SECONDS = 10
TRANSACTION_INCREMENT_IN_SECONDS = 0.1

class _ShipCosmeticTransactionSvc(object):
    __startupdependencies__ = ['publicGatewaySvc']
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self):
        self._pending_transactions = {}
        public_gateway = sm.GetService('publicGatewaySvc')
        self._notice_messenger = PublicShipCosmeticTransactionNoticeMessenger(public_gateway)
        ship_skin_svc_signals.on_transaction_succeeded_internal.connect(self._on_transaction_succeeded)
        ship_skin_svc_signals.on_transaction_failed_internal.connect(self._on_transaction_failed)
        sm.RegisterNotify(self)

    def __del__(self):
        ship_skin_svc_signals.on_transaction_succeeded_internal.disconnect(self._on_transaction_succeeded)
        ship_skin_svc_signals.on_transaction_failed_internal.disconnect(self._on_transaction_failed)

    def OnSessionChanged(self, _isRemote, _sess, change):
        if 'charid' in change:
            self._clear_cache()

    def _clear_cache(self):
        self._pending_transactions = {}

    def process_transaction(self, transaction_id):
        if transaction_id in self._pending_transactions:
            logger.warning('COSMETIC TRANSACTIONS: transaction %s already logged' % transaction_id)
            return False
        self._pending_transactions[transaction_id] = None
        try:
            timeout = 0
            while transaction_id in self._pending_transactions and self._pending_transactions[transaction_id] is None:
                if timeout >= TRANSACTION_TIMEOUT_IN_SECONDS:
                    logger.warning('COSMETIC TRANSACTIONS: transaction %s timed out' % transaction_id)
                    raise TimeoutException
                timeout += TRANSACTION_INCREMENT_IN_SECONDS
                uthread2.Sleep(TRANSACTION_INCREMENT_IN_SECONDS)

            return self._pending_transactions[transaction_id]
        except Exception as e:
            raise e
        finally:
            logger.info('COSMETIC TRANSACTIONS: transaction %s concluded' % transaction_id)
            self._pending_transactions.pop(transaction_id)

    def _on_transaction_succeeded(self, transaction_id):
        if transaction_id in self._pending_transactions:
            logger.info('COSMETIC TRANSACTIONS: transaction %s succeeded' % transaction_id)
            self._pending_transactions[transaction_id] = True

    def _on_transaction_failed(self, transaction_id):
        if transaction_id in self._pending_transactions:
            logger.info('COSMETIC TRANSACTIONS: transaction %s failed' % transaction_id)
            self._pending_transactions[transaction_id] = False
