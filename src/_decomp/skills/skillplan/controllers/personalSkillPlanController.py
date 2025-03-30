#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\controllers\personalSkillPlanController.py
from localization import GetByLabel
from skills.skillplan.controllers.editableSkillPlanController import EditableSkillPlanController

class PersonalSkillPlanController(EditableSkillPlanController):

    def IsTrackable(self):
        return self.ownerID == session.charid

    def IsEditable(self):
        return self.ownerID == session.charid

    def GetTypeName(self):
        return GetByLabel('UI/SkillPlan/PersonalSkillPlan')
