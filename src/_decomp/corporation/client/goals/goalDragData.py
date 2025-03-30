#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\client\goals\goalDragData.py
import eveicon
from carbonui.control.dragdrop.dragdata import BaseDragData
from corporation.common.goals.link import get_goal_link

class GoalDragData(BaseDragData):

    def __init__(self, goal):
        super(GoalDragData, self).__init__()
        self.goal = goal

    def GetIconTexturePath(self):
        return eveicon.corporation_folder.resolve(16)

    def get_link(self):
        return get_goal_link(goal_id=self.goal.get_id().int, goal_name=self.goal.get_name())
