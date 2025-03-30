#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\structures\license.py
from datetime import datetime

class StructurePaintworkLicense(object):

    def __init__(self, license_id, corp_id, char_id, structure_id, activation_timestamp, duration):
        self._id = license_id
        self._corp_id = corp_id
        self._char_id = char_id
        self._structure_id = structure_id
        self._activation_timestamp = activation_timestamp
        self._duration = duration

    @property
    def id(self):
        return self._id

    @property
    def corp_id(self):
        return self._corp_id

    @property
    def char_id(self):
        return self._char_id

    @property
    def structure_id(self):
        return self._structure_id

    @property
    def activation_timestamp(self):
        return self._activation_timestamp

    @property
    def duration(self):
        return self._duration

    def get_remaining_time(self):
        now = datetime.now()
        elapsed = now - self._activation_timestamp
        remaining = self._duration - elapsed.total_seconds()
        return remaining

    def __eq__(self, other):
        return self.id == other.id and self.corp_id == other.corp_id and self.char_id == other.char_id and self.structure_id == other.structure_id and self.activation_timestamp == other.activation_timestamp and self.duration == other.duration
