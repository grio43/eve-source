#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\milestone\milestoneController.py
import uuid
import dogma
from eve.common.lib import appConst
import evetypes
import evetypes.skills as skillsData
import mathext
from characterskills.util import GetProgressRatioForSkillLevels, GetInTrainingRatioForSkillLevels
from eve.client.script.ui.skillPlan import skillPlanUISignals
from skills.skillConst import skill_max_level
from skills.skillplan.milestone.const import MilestoneType
from skills.skillplan.milestone.milestonesUtil import GetMilestoneSubType

def BuildMilestonesFromRawData(milestones):
    output = []
    for milestoneID, milestoneType, milestoneInfo in milestones:
        controller = GetMilestoneController(milestoneID, milestoneType, milestoneInfo)
        output.append(controller)

    return output


def GetMilestoneController(milestoneID, milestoneType, milestoneInfo):
    if milestoneType == MilestoneType.SKILL_REQUIREMENT_MILESTONE:
        return SkillRequirementMilestoneController(milestoneInfo[0], milestoneInfo[1], milestoneID)
    if milestoneType == MilestoneType.TYPE_ID_MILESTONE:
        return TypeIDMilestoneController(milestoneInfo, milestoneID)


class BaseMilestoneController(object):

    def __init__(self, milestoneID = None):
        self.milestoneID = milestoneID
        self._milestoneType = None

    def GetMilestoneType(self):
        return self._milestoneType

    def GetMilestoneSubType(self):
        raise NotImplementedError

    def GetData(self):
        raise NotImplementedError

    def GetProgress(self):
        raise NotImplementedError

    def SetMilestoneID(self, milestoneID):
        self.milestoneID = milestoneID

    def GetID(self):
        return self.milestoneID

    def GetTypeID(self):
        return None

    def GetLevel(self):
        return None

    def __eq__(self, other):
        return self.GetData() == other.GetData()

    def GetRequiredSkills(self):
        raise NotImplementedError

    def GetProgressRatio(self):
        return GetProgressRatioForSkillLevels(self.GetRequiredSkills())

    def GetInTrainingRatio(self):
        return GetInTrainingRatioForSkillLevels(self.GetRequiredSkills())

    def GetCopy(self):
        raise NotImplementedError

    def IsCompleted(self):
        required = self.GetRequiredSkills()
        if not required:
            return False
        for typeID, level in required.iteritems():
            if sm.GetService('skills').MySkillLevel(typeID) < level:
                return False

        return True

    def IsValid(self):
        raise NotImplementedError


class TypeIDMilestoneController(BaseMilestoneController):

    def __init__(self, typeID, milestoneID = None):
        super(TypeIDMilestoneController, self).__init__(milestoneID)
        self._milestoneType = MilestoneType.TYPE_ID_MILESTONE
        self.typeID = typeID

    def GetData(self):
        return self.typeID

    def GetRequiredSkills(self):
        return skillsData.get_dogma_required_skills_recursive(self.typeID)

    def GetTypeID(self):
        return self.typeID

    def GetMilestoneSubType(self):
        return GetMilestoneSubType(self.typeID)

    def GetCopy(self):
        milestoneID = uuid.uuid4()
        return TypeIDMilestoneController(self.typeID, milestoneID)

    def IsValid(self):
        return evetypes.IsPublished(self.typeID)


class SkillRequirementMilestoneController(BaseMilestoneController):

    def __init__(self, typeID, level, milestoneID = None):
        super(SkillRequirementMilestoneController, self).__init__(milestoneID)
        self._milestoneType = MilestoneType.SKILL_REQUIREMENT_MILESTONE
        self.typeID = typeID
        self.level = level

    def GetData(self):
        return (self.typeID, self.level)

    def GetRequiredSkills(self):
        requiredSkills = skillsData.get_dogma_required_skills_recursive(self.typeID)
        requiredSkills[self.typeID] = max(requiredSkills.get(self.typeID, 0), self.level)
        return requiredSkills

    def GetTypeID(self):
        return self.typeID

    def GetMilestoneSubType(self):
        return GetMilestoneSubType(self.typeID)

    def GetLevel(self):
        return self.level

    def SetLevel(self, level):
        self.level = mathext.clamp(level, 1, skill_max_level)
        skillPlanUISignals.on_milestone_updated(self.milestoneID)

    def GetCopy(self):
        milestoneID = uuid.uuid4()
        return SkillRequirementMilestoneController(self.typeID, self.level, milestoneID)

    def IsValid(self):
        return 1 <= self.level <= skill_max_level and evetypes.IsSkill(self.typeID) and evetypes.IsPublished(self.typeID) and not dogma.data.get_type_attribute(self.typeID, appConst.attributeSkillIsObsolete, False)
