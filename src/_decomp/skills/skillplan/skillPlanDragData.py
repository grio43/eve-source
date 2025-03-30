#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\skillPlanDragData.py
from carbonui.control.dragdrop.dragdata.basedragdata import BaseDragData
from eve.client.script.ui.skillPlan.link import skillplan_link

class SkillPlanDragData(BaseDragData):

    def __init__(self, skillPlanID, name, ownerID = None):
        super(SkillPlanDragData, self).__init__()
        self.skillPlanID = skillPlanID
        self.name = name
        self.ownerID = ownerID

    def GetIconTexturePath(self):
        return 'res:/ui/texture/classes/SkillPlan/skillplanIcon64.png'

    def get_link(self):
        return skillplan_link(self.skillPlanID, self.name, self.ownerID)
