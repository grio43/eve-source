#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\inventoryrestrictions\common\util.py
import eveprefs

def has_no_restriction(type_id, restriction_ids):
    return _get_tracker().has_no_restriction(type_id, restriction_ids)


def has_container_restriction(type_id, container_id, restriction_ids, allowed_container_ids):
    return _get_tracker().has_container_restriction(type_id, container_id, restriction_ids, allowed_container_ids)


def _get_tracker():
    boot_role = eveprefs.boot.role
    if boot_role == 'client':
        from inventoryrestrictions.client.tracker import InventoryRestrictionsTracker
        return InventoryRestrictionsTracker()
    if boot_role == 'server':
        from inventoryrestrictions.server.tracker import InventoryRestrictionsTracker
        return InventoryRestrictionsTracker()
    from inventoryrestrictions.common.tracker import BaseInventoryRestrictionsTracker
    return BaseInventoryRestrictionsTracker()
