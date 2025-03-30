#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\common\instance_identifier.py
from uuid import UUID
from eveProto.generated.eve.sovereignty.mercenaryden.activity.activity_pb2 import Identifier as ActivityID

class DungeonInstanceIdentifier(object):
    _MODE_UNKNOWN = '_MODE_UNKNOWN'
    _MODE_PERMANENT = '_MODE_PERMANENT'
    _MODE_ADMIN = '_MODE_ADMIN'
    _MODE_EPHEMERAL = '_MODE_EPHEMERAL'
    _MODE_EXTERNAL_ACTIVITY = '_MODE_EXTERNAL_ACTIVITY'
    _MODES = [_MODE_UNKNOWN,
     _MODE_PERMANENT,
     _MODE_EPHEMERAL,
     _MODE_ADMIN,
     _MODE_EXTERNAL_ACTIVITY]
    _MODES_FOR_EXTERNAL_DUNGEONS = [_MODE_EXTERNAL_ACTIVITY]

    def __init__(self, mode, value):
        if mode not in self._MODES:
            raise ValueError("DungeonInstanceIdentifier mode '%s' not recognized" % mode)
        self._mode = mode
        self._value = value

    def __repr__(self):
        if self.is_permanent:
            int_id = self._value
            return '<DungeonInstanceIdentifier (PERMANENT=%d)>' % int_id
        elif self.is_ephemeral:
            int_id = self._value
            return '<DungeonInstanceIdentifier (EPHEMERAL=%d)>' % int_id
        elif self.is_admin:
            return '<DungeonInstanceIdentifier (ADMIN)>'
        elif self.is_external_activity:
            uuid = self._value
            return '<DungeonInstanceIdentifier (EXTERNAL_ACTIVITY=%r)>' % uuid
        else:
            return '<DungeonInstanceIdentifier (UNKNOWN)>'

    def __str__(self):
        if self.is_permanent:
            int_id = self._value
            return 'DungeonInstanceID (PERMANENT=%d)' % int_id
        elif self.is_ephemeral:
            int_id = self._value
            return 'DungeonInstanceID (EPHEMERAL=%d)' % int_id
        elif self.is_admin:
            return 'DungeonInstanceID (ADMIN)'
        elif self.is_external_activity:
            uuid = self._value
            return 'DungeonInstanceID (EXTERNAL_ACTIVITY=%s)' % uuid
        else:
            return 'DungeonInstanceID (UNKNOWN)'

    def __eq__(self, other):
        if not isinstance(other, DungeonInstanceIdentifier):
            return NotImplemented
        return self._mode == other._mode and self._value == other._value

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self._mode, self._value))

    @property
    def is_permanent(self):
        return self._mode == DungeonInstanceIdentifier._MODE_PERMANENT

    @property
    def is_ephemeral(self):
        return self._mode == DungeonInstanceIdentifier._MODE_EPHEMERAL

    @property
    def is_admin(self):
        return self._mode == DungeonInstanceIdentifier._MODE_ADMIN

    @property
    def is_external(self):
        return self._mode in DungeonInstanceIdentifier._MODES_FOR_EXTERNAL_DUNGEONS

    @property
    def is_external_activity(self):
        return self._mode == DungeonInstanceIdentifier._MODE_EXTERNAL_ACTIVITY

    @property
    def permanent_id(self):
        if self.is_permanent:
            return self._value

    @property
    def ephemeral_id(self):
        if self.is_ephemeral:
            return self._value

    @property
    def external_activity_id(self):
        if self.is_external_activity:
            return self._value

    @staticmethod
    def create_unknown_instance_id(value):
        return DungeonInstanceIdentifier(DungeonInstanceIdentifier._MODE_UNKNOWN, value)

    @staticmethod
    def create_permanent_instance_id(int_id):
        if not isinstance(int_id, int) or int_id < 0:
            raise ValueError("DungeonInstanceIdentifier requires positive integer ID for PERMANENT mode - got '%s'" % int_id)
        return DungeonInstanceIdentifier(DungeonInstanceIdentifier._MODE_PERMANENT, int_id)

    @staticmethod
    def create_ephemeral_instance_id(int_id):
        if not isinstance(int_id, int) or int_id > 0:
            raise ValueError("DungeonInstanceIdentifier requires negative integer ID for EPHEMERAL mode - got '%s'" % int_id)
        return DungeonInstanceIdentifier(DungeonInstanceIdentifier._MODE_EPHEMERAL, int_id)

    @staticmethod
    def create_admin_instance_id(int_id):
        if not isinstance(int_id, int):
            raise ValueError("DungeonInstanceIdentifier requires integer ID for ADMIN mode - got '%s'" % int_id)
        return DungeonInstanceIdentifier(DungeonInstanceIdentifier._MODE_ADMIN, int_id)

    @staticmethod
    def create_external_activity_instance_id(uuid):
        if not isinstance(uuid, UUID):
            raise ValueError("DungeonInstanceIdentifier requires UUID for EXTERNAL_ACTIVITY mode - got '%s'" % uuid)
        return DungeonInstanceIdentifier(DungeonInstanceIdentifier._MODE_EXTERNAL_ACTIVITY, uuid)

    def format_proto_identifier(self, instance_proto):
        if self.is_permanent:
            int_id = self._value
            instance_proto.permanent = int_id
        elif self.is_ephemeral:
            int_id = self._value
            instance_proto.ephemeral = int_id
        elif self.is_admin:
            instance_proto.admin = True
        elif self.is_external_activity:
            uuid = self._value
            instance_proto.activity.CopyFrom(ActivityID(uuid=uuid.bytes))
        else:
            instance_proto.unknown = True
