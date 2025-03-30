#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\inventoryrestrictions\client\tracker.py
from collections import defaultdict
from inventoryrestrictions.common.tracker import BaseInventoryRestrictionsTracker

class InventoryRestrictionsTracker(BaseInventoryRestrictionsTracker):

    def __init__(self):
        super(InventoryRestrictionsTracker, self).__init__()
        self._client_restrictions_by_type_id = defaultdict(set)

    def has_restriction_on_type(self, type_id, restriction_id):
        return any([self._has_client_restriction_on_type(type_id, restriction_id), self._has_static_restriction_on_type(type_id, restriction_id)])

    def _has_client_restriction_on_type(self, type_id, restriction_id):
        return restriction_id in self._client_restrictions_by_type_id[type_id]

    def add_client_restriction_on_type(self, type_id, restriction_id):
        self._client_restrictions_by_type_id[type_id].add(restriction_id)

    def remove_client_restriction_on_type(self, type_id, restriction_id):
        if self._has_client_restriction_on_type(type_id, restriction_id):
            self._client_restrictions_by_type_id[type_id].remove(restriction_id)

    def remove_all_client_restrictions(self):
        self._client_restrictions_by_type_id.clear()
