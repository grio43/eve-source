#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\inventoryrestrictions\common\tracker.py
from collections import defaultdict
import evetypes
from evetypes.data import TypeListLoader
from typeutils import metas

class BaseInventoryRestrictionsTracker(object):
    __metaclass__ = metas.Singleton

    def __init__(self):
        self._static_restrictions_loaded = set()
        self._static_restrictions_by_type_id = defaultdict(set)
        TypeListLoader.ConnectToOnReload(self._clear_static_restrictions)

    def _load_static_restrictions(self, restriction_id):
        if restriction_id not in self._static_restrictions_loaded:
            for type_id in evetypes.GetTypeIDsByListID(restriction_id):
                self._static_restrictions_by_type_id[type_id].add(restriction_id)

            self._static_restrictions_loaded.add(restriction_id)

    def _clear_static_restrictions(self):
        self._static_restrictions_loaded = set()
        self._static_restrictions_by_type_id = defaultdict(set)

    def _has_static_restriction_on_type(self, type_id, restriction_id):
        self._load_static_restrictions(restriction_id)
        return restriction_id in self._static_restrictions_by_type_id[type_id]

    def has_restriction_on_type(self, type_id, restriction_id):
        return self._has_static_restriction_on_type(type_id, restriction_id)

    def has_no_restriction(self, type_id, restriction_ids):
        for restriction_id in restriction_ids:
            if self.has_restriction_on_type(type_id, restriction_id):
                return False

        return True

    def has_container_restriction(self, type_id, container_id, restriction_ids, allowed_container_ids):
        if self._has_static_restriction_on_type(type_id, restriction_ids):
            allowed_container_list = evetypes.GetTypeIDsByListID(allowed_container_ids)
            if container_id not in allowed_container_list:
                return True
        return False
