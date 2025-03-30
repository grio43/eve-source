#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\inventoryrestrictions\common\errors.py
from eveexceptions import UserError
from eveexceptions.const import UE_TYPEIDL
CANNOT_TRASH_ERROR = 'CannotTrashItem'
CANNOT_TRADE_ERROR = 'CannotTradeNonTradable'
CANNOT_ADD_TO_CONTAINER_ERROR = 'CannotAddItemListToThatLocation'
CANNOT_UNFIT_ERROR = 'CannotUnfitItem'

class ItemCannotBeTraded(UserError):

    def __init__(self, type_ids):
        super(ItemCannotBeTraded, self).__init__(CANNOT_TRADE_ERROR, {'itemList': (UE_TYPEIDL, type_ids)})


class ItemCannotBeTrashed(UserError):

    def __init__(self):
        super(ItemCannotBeTrashed, self).__init__(CANNOT_TRASH_ERROR)


class ItemCannotBeAddedToContainer(UserError):

    def __init__(self, type_ids):
        super(ItemCannotBeAddedToContainer, self).__init__(CANNOT_ADD_TO_CONTAINER_ERROR, {'itemList': (UE_TYPEIDL, type_ids)})


class ItemCannotBeUnfitted(UserError):

    def __init__(self, type_ids):
        super(ItemCannotBeUnfitted, self).__init__(CANNOT_UNFIT_ERROR, {'itemList': (UE_TYPEIDL, type_ids)})
