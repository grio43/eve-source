#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\drones.py
from behaviors.tasks import Task
from behaviors.utility.dogmatic import get_my_attribute_value
from ccpProfile import TimedFunction
from dogma.const import attributeNpcDroneBandwidth

class CanControlDrones(Task):

    @TimedFunction('behaviors::conditions::drones::CanControlDrones::OnEnter')
    def OnEnter(self):
        drone_bandwidth = get_my_attribute_value(self, attributeNpcDroneBandwidth)
        self.SetStatusToSuccessIfTrueElseToFailed(drone_bandwidth > 0)


class HasDroneBandwidth(Task):

    @TimedFunction('behaviors::conditions::drones::HasDroneBandwidth::OnEnter')
    def OnEnter(self):
        drone_group_id = self.GetLastBlackboardValue(self.attributes.droneGroupIdAddress)
        group_manager = self.context.entityLocation.GetGroupManager()
        drone_group = group_manager.GetGroup(drone_group_id)
        if drone_group_id is None or drone_group is None:
            self.SetStatusToSuccess()
            return
        drone_count = drone_group.Count()
        max_group_size = self.GetLastBlackboardValue(self.attributes.maxDroneActiveCountAddress)
        self.SetStatusToSuccessIfTrueElseToFailed(max_group_size > drone_count)
