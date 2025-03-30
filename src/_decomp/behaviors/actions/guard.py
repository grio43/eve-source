#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\guard.py
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task
from behaviors.utility.components import get_proximity_sensor, create_proximity_sensor
from npcs.server.tags import entity_group_tag, try_add_behavior_context_tags

class PlaceProximitySensor(Task):

    def OnEnter(self):
        item_id = self.GetLastBlackboardValue(self.attributes.itemIdAddress)
        self._UpdateSensor(item_id)
        self.SetStatusToSuccess()

    def _UpdateSensor(self, item_id):
        try:
            self._ReplaceSensor(item_id)
        except KeyError:
            self._InstallSensor(item_id)

    def _InstallSensor(self, item_id):
        aggression_range = self.GetLastBlackboardValue(self.attributes.rangeAddress)
        proximitySensor = create_proximity_sensor(self, item_id, aggression_range)
        self.SetTags(proximitySensor)
        sensor_ball_id = proximitySensor.RegisterSensor(self.context.ballpark)
        return sensor_ball_id

    def SetTags(self, proximitySensor):
        try_add_behavior_context_tags(proximitySensor, self.context)
        tags = getattr(self.attributes, 'tags', None)
        if tags:
            for tag in tags:
                proximitySensor.AddTag(tag)

    def _ReplaceSensor(self, item_id):
        proximitySensor = get_proximity_sensor(self, item_id)
        if proximitySensor.GetDistanceTo(item_id) > self.attributes.sensorReplacementRange:
            proximitySensor.ReplaceSensor()


class PlaceProximitySensorForGroup(PlaceProximitySensor, GroupTaskMixin):

    def OnEnter(self):
        item_ids = self.GetMemberIdList()
        for item_id in item_ids:
            self._UpdateSensor(item_id)

        self.SetStatusToSuccess()
