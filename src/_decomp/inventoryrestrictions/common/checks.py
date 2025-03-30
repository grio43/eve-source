#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\inventoryrestrictions\common\checks.py
from evetypes import GetMarketGroupID
from evetypes.const import TYPE_LIST_NON_CONTRACTABLE_ITEMS, TYPE_LIST_NON_TRADABLE_ITEMS, TYPE_LIST_NON_TRASHABLE_ITEMS, TYPE_LIST_CANNOT_BE_ADDED_TO_CONTAINER, TYPE_LIST_ALLOWED_IN_SMA_CARGO_HOLDS, TYPE_LIST_CANNOT_BE_DROPPED_AS_LOOT, TYPE_LIST_SOULBOUND_ITEMS, TYPE_LIST_CANNOT_BE_UNFITTED, TYPE_LIST_NO_ESCAPE_RESTRICTED_TYPES, TYPE_LIST_NO_ESCAPE_MISSION_CONTAINERS
from inventoryrestrictions.common.util import has_no_restriction, has_container_restriction

def is_soulbound(type_id):
    return not has_no_restriction(type_id, [TYPE_LIST_SOULBOUND_ITEMS])


def is_tradable(type_id):
    return has_no_restriction(type_id, [TYPE_LIST_NON_TRADABLE_ITEMS, TYPE_LIST_SOULBOUND_ITEMS])


def is_contractable(type_id):
    return has_no_restriction(type_id, [TYPE_LIST_NON_CONTRACTABLE_ITEMS, TYPE_LIST_SOULBOUND_ITEMS])


def can_be_added_to_container(type_id, target_container):
    is_restricted_container = has_container_restriction(type_id=type_id, container_id=target_container, restriction_ids=TYPE_LIST_NO_ESCAPE_RESTRICTED_TYPES, allowed_container_ids=TYPE_LIST_NO_ESCAPE_MISSION_CONTAINERS)
    if is_restricted_container:
        return False
    return has_no_restriction(type_id, [TYPE_LIST_NON_TRADABLE_ITEMS, TYPE_LIST_CANNOT_BE_ADDED_TO_CONTAINER, TYPE_LIST_SOULBOUND_ITEMS])


def can_be_dropped_as_loot(type_id):
    return has_no_restriction(type_id, [TYPE_LIST_CANNOT_BE_DROPPED_AS_LOOT, TYPE_LIST_SOULBOUND_ITEMS])


def is_trashable(type_id):
    return has_no_restriction(type_id, [TYPE_LIST_NON_TRASHABLE_ITEMS])


def can_view_market_details(type_id):
    return GetMarketGroupID(type_id) and is_tradable(type_id)


def is_allowed_in_sma_cargoholds(type_id):
    return not has_no_restriction(type_id, [TYPE_LIST_ALLOWED_IN_SMA_CARGO_HOLDS])


def can_be_unfitted(type_id):
    return has_no_restriction(type_id, [TYPE_LIST_CANNOT_BE_UNFITTED])
