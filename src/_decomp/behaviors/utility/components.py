#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\components.py
from brennivin.itertoolsext import Bundle
from spacecomponents.common.componentConst import PROXIMITY_SENSOR_CLASS

def get_proximity_sensor(task, proximity_sensor_id):
    return task.context.ballpark.componentRegistry.GetComponentForItem(proximity_sensor_id, PROXIMITY_SENSOR_CLASS)


def get_proximity_sensors(task, *tags):
    sensors = task.context.ballpark.componentRegistry.GetInstancesWithComponentClass(PROXIMITY_SENSOR_CLASS)
    return [ sensor for sensor in sensors if sensor.HasTags(*tags) ]


def get_proximity_sensors_for_group_members(task):
    member_ids = task.GetMemberIdList()
    sensors = get_proximity_sensors(task)
    return [ sensor for sensor in sensors if sensor.itemID in member_ids ]


def create_proximity_sensor(task, item_id, aggression_range):
    guardObjectTypeId = task.context.ballpark.inventory2.GetItem(item_id).typeID
    proximitySensor = task.context.ballpark.componentRegistry.AddComponentInstanceToItem(PROXIMITY_SENSOR_CLASS, item_id, guardObjectTypeId, Bundle(detectionRange=aggression_range, tags=None))
    return proximitySensor
