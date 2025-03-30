#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\skillPlanTemplate.py
import evetypes
from inventorycommon import const
from localization import GetByLabel
from skills.skillplan.controllers.editableSkillPlanController import EditableSkillPlanController

class SkillPlanTemplate(object):

    def Apply(self, editableSkillPlanController):
        pass


class RequirementListSkillPlanTemplate(SkillPlanTemplate):

    def __init__(self, requirements, name = None):
        self.requirements = requirements
        self.name = name

    def Apply(self, editableSkillPlanController):
        editableSkillPlanController.AppendSkillRequirements(self.requirements)
        if self.name:
            editableSkillPlanController.SetName(self.name)


class TypeRequirementSkillPlanTemplate(SkillPlanTemplate):

    def __init__(self, typeID):
        self.typeID = typeID

    def Apply(self, editableSkillPlanController):
        if editableSkillPlanController.HasEmptyMilestoneSlots():
            if evetypes.GetCategoryID(self.typeID) == const.categorySkill:
                editableSkillPlanController.AddAllSkillsRequiredFor(self.typeID, 1)
                editableSkillPlanController.AddSkillRequirementMilestone(self.typeID, 1)
            else:
                editableSkillPlanController.AddTypeIDMilestone(self.typeID)
        else:
            editableSkillPlanController.AddAllSkillsRequiredFor(self.typeID)
        if editableSkillPlanController.GetName() == '':
            typeName = evetypes.GetName(self.typeID)
            editableSkillPlanController.SetName(GetByLabel('Tooltips/SkillPlanner/SkillPlanNameStringWithType', typeName=typeName))
