#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\controllers\corpSkillPlanController.py
from eve.common.lib import appConst
from localization import GetByLabel
from skills.skillplan import skillPlanConst
from skills.skillplan.controllers.editableSkillPlanController import EditableSkillPlanController
from skills.skillplan.grpc import corpSkillPlanRequest

class CorpSkillPlanController(EditableSkillPlanController):

    def __init__(self, skillPlanID, name = '', description = '', skillRequirements = None, ownerID = None, milestoneSvc = None, categoryID = None):
        super(CorpSkillPlanController, self).__init__(skillPlanID, name, description, skillRequirements, ownerID, milestoneSvc, categoryID)
        self._skillRequirements = None

    @property
    def skillRequirements(self):
        if self._skillRequirements is None:
            if self.GetID() == skillPlanConst.PLAN_ID_NEW_UNSAVED:
                self._skillRequirements = []
            else:
                skillPlan = corpSkillPlanRequest.Get(self.GetID())
                self._skillRequirements = [ (int(req.skill_type.sequential), req.level) for req in skillPlan.skill_requirements ]
                wasInvalid = self._ValidateSkillRequirements()
                if wasInvalid:
                    corpSkillPlanRequest.SetRequiredSkills(self.skillPlanID, self._skillRequirements)
        return self._skillRequirements

    @skillRequirements.setter
    def skillRequirements(self, value):
        self._skillRequirements = value

    def IsEditable(self):
        return session.corpid == self.ownerID and session.corprole & appConst.corpRoleSkillPlanManager

    def HasEditableCategoryID(self):
        return True

    def IsTrackable(self):
        return False

    def GetTypeName(self):
        return GetByLabel('UI/SkillPlan/CorpSkillPlan')

    def GetCareerPathID(self):
        return self.GetCategoryID()
