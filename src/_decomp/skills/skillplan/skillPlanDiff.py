#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\skillPlanDiff.py
from skills.skillplan import skillPlanConst
from skills.skillplan.skillPlanService import GetSkillPlanSvc

def IsEditedPlanDifferentFromOriginal(newSkillPlan):
    if newSkillPlan.GetID() == skillPlanConst.PLAN_ID_NEW_UNSAVED:
        if newSkillPlan.GetName() or newSkillPlan.GetDescription() or newSkillPlan.GetSkillRequirements():
            return True
        if newSkillPlan.GetMilestonesToAdd():
            return True
        return False
    savedSkillPlan = GetSkillPlanSvc().Get(newSkillPlan.GetID())
    if not savedSkillPlan:
        return True
    if savedSkillPlan.GetName() != newSkillPlan.GetName():
        return True
    if savedSkillPlan.GetDescription() != newSkillPlan.GetDescription():
        return True
    if savedSkillPlan.GetSkillRequirements() != newSkillPlan.GetSkillRequirements():
        return True
    if _HaveMilestonesChanged(newSkillPlan, savedSkillPlan):
        return True
    return False


def _HaveMilestonesChanged(newSkillPlan, savedSkillPlan):
    newMilestonesData = sorted([ m.GetData() for m in newSkillPlan.GetMilestones().values() ])
    savedMilestonesData = sorted([ m.GetData() for m in savedSkillPlan.GetMilestones().values() ])
    haveMilestonesChanged = newMilestonesData != savedMilestonesData
    return haveMilestonesChanged
