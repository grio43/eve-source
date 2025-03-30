#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\common\errors.py
from eveexceptions import UserError

class RafflesError(UserError):

    def __init__(self, msg = None):
        super(RafflesError, self).__init__(msg or 'UndhandledRaffleError')

    def __repr__(self):
        return str(self.__class__)

    def __str__(self):
        return str(self.__class__)


class RaffleNotFoundError(RafflesError):
    pass


class PurchaseError(RafflesError):
    pass


class TicketUnavailableError(PurchaseError):
    pass


class NotEnoughISKError(PurchaseError):
    pass


class FailureToDeliverItemError(RafflesError):
    pass


class FetchError(RafflesError):
    pass


class InventoryError(RafflesError):
    pass


class CreateError(RafflesError):

    def __init__(self, reason):
        super(CreateError, self).__init__(msg=reason)


class CreateErrorReason(object):
    token_payment = 'TokenPaymentError'
    item_escrow = 'ItemEscrowError'
    type_mismatch = 'TypeMismatchError'
    ticket_count = 'TicketCountError'
    ticket_price = 'TicketPriceError'
    item_type = 'ItemTypeError'
    item_location = 'ItemLocationError'
    item_inventory = 'ItemInventoryError'
    item_singleton = 'ItemSingletonError'
    item_owner = 'ItemOwnerError'
    item_triglavian_system = 'ItemTriglavianSystemError'
    token_type = 'TokenTypeError'
    token_location = 'TokenLocationError'
    token_inventory = 'TokenInventoryError'
    token_owner = 'TokenOwnerError'
    token_amount = 'TokenAmountError'
    unknown = 'UnknownError'
