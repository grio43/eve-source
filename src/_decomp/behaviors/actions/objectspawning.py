#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\objectspawning.py
import random
import logging
import evetypes
from behaviors.tasks import Task
from behaviors.utility.ballparks import get_my_position
from behaviors.utility.inventory import get_inventory2
from behaviors.utility.owner import get_owner_id
from inventorycommon.const import flagNone
from utillib import KeyVal
logger = logging.getLogger(__name__)

class SpawnSpaceObjectsFromDungeon(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        inventory_2 = get_inventory2(self)
        owner_id = get_owner_id(self)
        replaced_object = self._generate_replaced_objects()
        assets = self._get_assets_from_dungeon()
        for object_for_spawning in assets:
            object_name_id = object_for_spawning.objectNameID
            object_custom_info = self._get_object_custom_info(object_for_spawning, object_name_id)
            type_id = self._get_type_id_for_object_spawning(object_for_spawning.typeID, replaced_object)
            if type_id is None:
                continue
            inventory_2.AddFakeLocation(type_id, owner_id, self.context.ballpark.solarsystemID, flagNone, 1, '', self.context.myBall.x + object_for_spawning.x, self.context.myBall.y + object_for_spawning.y, self.context.myBall.z + object_for_spawning.z, object_name_id, object_custom_info)

    def _generate_replaced_objects(self):
        return {self.attributes.object1TypeIdForReplacing: {'count': 0,
                                                     'max_count': random.randint(self.attributes.object1MinCount, self.attributes.object1MaxCount),
                                                     'type_list_id': self.attributes.eveTypeList1},
         self.attributes.object2TypeIdForReplacing: {'count': 0,
                                                     'max_count': random.randint(self.attributes.object2MinCount, self.attributes.object2MaxCount),
                                                     'type_list_id': self.attributes.eveTypeList2},
         self.attributes.object3TypeIdForReplacing: {'count': 0,
                                                     'max_count': random.randint(self.attributes.object3MinCount, self.attributes.object3MaxCount),
                                                     'type_list_id': self.attributes.eveTypeList3}}

    def _get_assets_from_dungeon(self):
        dungeon_id = self._get_dungeon_id()
        keeper = sm.GetService('keeper')
        dungeon_data = keeper.GetDungeonData(dungeon_id)
        return dungeon_data.roomObjects[next(iter(dungeon_data.roomObjects))]

    def _get_dungeon_id(self):
        return self.attributes.dungeonId

    def _get_object_custom_info(self, object_for_spawning, object_name_id):
        custom_info = KeyVal()
        if None not in (object_for_spawning.yaw, object_for_spawning.pitch, object_for_spawning.roll) and (object_for_spawning.yaw or object_for_spawning.pitch or object_for_spawning.roll):
            custom_info.dunRotation = (object_for_spawning.yaw, object_for_spawning.pitch, object_for_spawning.roll)
        if object_for_spawning.objectID is not None:
            custom_info.dunObjectID = object_for_spawning.objectID
            custom_info.dunObjectNameID = object_name_id
        return custom_info

    def _get_type_id_for_object_spawning(self, object_type_id, replaced_object):
        if object_type_id not in replaced_object:
            return object_type_id
        if replaced_object[object_type_id]['count'] == replaced_object[object_type_id]['max_count']:
            return None
        type_list_id = evetypes.GetTypeIDsByListID(replaced_object[object_type_id]['type_list_id'])
        picked_type_id = random.choice(tuple(type_list_id))
        replaced_object[object_type_id]['count'] += 1
        return picked_type_id


def _get_spawn_coordinates(task):
    if task.HasAttribute('coordinateAddress'):
        return task.GetLastBlackboardValue(task.attributes.coordinateAddress)
    return get_my_position(task)


class SpawnSpaceObject(Task):

    def OnEnter(self):
        inventory_2 = get_inventory2(self)
        owner_id = get_owner_id(self)
        coordinates = _get_spawn_coordinates(self)
        if coordinates is None:
            self.SetStatusToFailed()
            return
        x, y, z = coordinates
        inventory_2.AddFakeLocation(self.attributes.typeId, owner_id, self.context.ballpark.solarsystemID, flagNone, 1, '', x, y, z)
        self.SetStatusToSuccess()


class SpawnPersistentSpaceObject(Task):

    def OnEnter(self):
        inventory_2 = get_inventory2(self)
        owner_id = get_owner_id(self)
        coordinates = _get_spawn_coordinates(self)
        if coordinates is None:
            self.SetStatusToFailed()
            return
        x, y, z = coordinates
        item = inventory_2.EveInsertLocation(self.attributes.typeId, owner_id, self.context.ballpark.solarsystemID, flagNone, '', x, y, z)
        self.SetStatusToSuccess()
        logger.info('Behavior %s spawned PersistentSpaceObject of type : %s and itemID: %s', self.behaviorTree.GetBehaviorId(), self.attributes.typeId, item.itemID)
