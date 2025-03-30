#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\activity_cache.py
from locks import RWLock
from six import iteritems
from sovereignty.mercenaryden.client.data.activity import MercenaryDenActivity
from uuid import UUID
if False:
    from typing import Dict, List, Set

class ActivityCache(object):

    def __init__(self):
        self._lock = RWLock('MercenaryCache Lock')
        self._activity_id_to_solar_system_id = {}
        self._solar_system_id_to_activity_dict = {}

    def read_lock(self):
        return self._lock.acquired_read()

    def write_lock(self):
        return self._lock

    def add_activities(self, activities):
        with self.write_lock():
            for activity in activities:
                self.add_activity_for_solar_system(activity.solar_system_id, activity)

    def add_activity(self, activity):
        self.add_activity_for_solar_system(activity.solar_system_id, activity)

    def add_activity_for_solar_system(self, solar_system_id, activity):
        with self.write_lock():
            self._activity_id_to_solar_system_id[activity.id] = solar_system_id
            activity_dict = self._solar_system_id_to_activity_dict.get(solar_system_id, {})
            activity_dict[activity.id] = activity
            self._solar_system_id_to_activity_dict[solar_system_id] = activity_dict

    def remove_activity_by_id(self, activity_id):
        with self.write_lock():
            solar_system_id = self._activity_id_to_solar_system_id.pop(activity_id, None)
            if solar_system_id:
                activity_dict = self._solar_system_id_to_activity_dict.get(solar_system_id, None)
                if activity_dict:
                    activity_dict.pop(activity_id, None)

    def remove_all_activities(self):
        with self.write_lock():
            self._activity_id_to_solar_system_id.clear()
            self._solar_system_id_to_activity_dict.clear()

    def get_activity_by_id(self, activity_id):
        with self.read_lock():
            solar_system_id = self._activity_id_to_solar_system_id.get(activity_id, None)
            activity_dict = self._solar_system_id_to_activity_dict.get(solar_system_id, {})
            return activity_dict.get(activity_id, None)

    def get_activities(self):
        activities = []
        with self.read_lock():
            for solar_system_id, activity_dict in iteritems(self._solar_system_id_to_activity_dict):
                activities += activity_dict.values()

        return activities

    def get_activities_in_solar_system(self, solar_system_id):
        with self.read_lock():
            activity_dict = self._solar_system_id_to_activity_dict.get(solar_system_id, {})
            return activity_dict.values()
