#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\common\dungeon_proto_util.py
from evedungeons.common.instance_identifier import DungeonInstanceIdentifier

def format_dungeon_instance_id(instance_proto, instance_id):
    if isinstance(instance_id, DungeonInstanceIdentifier):
        instance_id.format_proto_identifier(instance_proto)
    elif instance_id is None:
        instance_proto.admin = True
    elif not isinstance(instance_id, int):
        instance_proto.unknown = True
    elif instance_id >= 0:
        instance_proto.permanent = instance_id
    else:
        instance_proto.ephemeral = instance_id
