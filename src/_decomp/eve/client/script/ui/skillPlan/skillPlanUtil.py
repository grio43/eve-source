#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanUtil.py
import evetypes
from carbonui.control.dragdrop import dragDropUtil, dragdata
from eve.client.script.ui.skillPlan import skillPlanConst
import inventorycommon.const as invConst
from eve.client.script.ui.skillPlan.skillPlanConst import IS_PREREQ, NO_REQ, REQUIRED_FOR
from skills.skillplan.milestone.milestonesUtil import GetMilestoneSubType

def IsValidContentsDragData(dragData):
    typeID = dragDropUtil.GetTypeID(dragData)
    if typeID is None:
        return False
    return IsTypeValidMilestone(typeID)


def IsTypeValidMilestone(typeID):
    if typeID is None:
        return False
    typeCategoryID = evetypes.GetCategoryID(typeID)
    if typeCategoryID == invConst.categorySkill:
        return True
    if typeCategoryID == invConst.categoryAsteroid:
        return False
    if sm.GetService('skills').GetRequiredSkills(typeID):
        return True
    return False


def GetDragDataTypeIDAndLevel(dragData):
    if isinstance(dragData, dragdata.SkillLevelDragData):
        typeID = dragData.typeID
        level = dragData.level
    else:
        typeID = dragDropUtil.GetTypeID(dragData)
        level = None
    if typeID and evetypes.IsSkill(typeID):
        level = level or 1
    return (typeID, level)


def GetMilestoneTexturePath(typeID):
    subType = GetMilestoneSubType(typeID)
    return skillPlanConst.MILESTONE_ICON_BY_SUBTYPE.get(subType, None)


def GetPreReqsAndRequiredForSkillLevel(typeID, level):
    prereqs = evetypes.skills.get_dogma_required_skills(typeID)
    reqForTypeIDs = GetSkillsRequiring(typeID, level)
    return (prereqs, reqForTypeIDs)


def GetSkillsRequiring(typeID, level):
    typeIndex = evetypes.skills.get_required_skills_index().get(typeID, {})
    reqForTypeIDs = set()
    typesByMetaGroupID = typeIndex.get(level, {}).get(const.marketCategorySkills, {})
    for typeList in typesByMetaGroupID.itervalues():
        reqForTypeIDs.update(typeList)

    return reqForTypeIDs


def GetRequirementStateForEntry(typeID, level, entry, prereqs, reqForTypeIDs):
    if typeID is None or level is None:
        return NO_REQ
    if entry.typeID in reqForTypeIDs and entry.level == 1:
        return REQUIRED_FOR
    if entry.typeID == typeID:
        if entry.level < level:
            return IS_PREREQ
        if entry.level > level:
            return REQUIRED_FOR
        return NO_REQ
    reqLevel = prereqs.get(entry.typeID, None)
    if reqLevel is not None and entry.level == reqLevel:
        return IS_PREREQ
    return NO_REQ


DEFAULT_PANELID_BY_BUTTONGROUP_ID = {skillPlanConst.BUTTON_GROUP_ID_TOP_LEVEL: skillPlanConst.PANEL_SKILL_PLANS,
 skillPlanConst.BUTTON_GROUP_ID_SKILL_PLANS: skillPlanConst.PANEL_CERTIFIED}

def GetPersistedPanelID(buttonGroupID):
    return settings.char.ui.Get(buttonGroupID, DEFAULT_PANELID_BY_BUTTONGROUP_ID.get(buttonGroupID, None))


def SetPersistedPanelID(buttonGroupID, panelID):
    return settings.char.ui.Set(buttonGroupID, panelID)


def IsExternalServicePanelSelected():
    return GetPersistedPanelID(skillPlanConst.BUTTON_GROUP_ID_TOP_LEVEL) == skillPlanConst.PANEL_SKILL_PLANS and GetPersistedPanelID(skillPlanConst.BUTTON_GROUP_ID_SKILL_PLANS) == skillPlanConst.PANEL_PERSONAL


def LoadGenericTooltip(tooltipPanel, headerText, text):
    tooltipPanel.LoadStandardSpacing()
    tooltipPanel.columns = 1
    tooltipPanel.AddMediumHeader(text=headerText)
    tooltipPanel.AddLabelMedium(text=text, wrapWidth=300)


def _GetCertifiedSkillPlansPanel():
    from eve.client.script.ui.skillPlan.skillPlanDockablePanel import SkillPlanDockablePanel
    skill_plans_window = SkillPlanDockablePanel.GetIfOpen()
    if skill_plans_window:
        skill_plan_panel = getattr(skill_plans_window, 'skillPlanPanel', None)
        if skill_plan_panel:
            skill_plan_browser = getattr(skill_plan_panel, 'skillPlanBrowser', None)
            if skill_plan_browser:
                return getattr(skill_plan_browser, 'certifiedSkillPlans', None)


def GetVisibleCareerPathTabGroup():
    certified_skill_plans = _GetCertifiedSkillPlansPanel()
    if certified_skill_plans:
        return certified_skill_plans.GetVisibleCareerPathTabGroup()


def GetVisibleFactionTabGroup():
    certified_skill_plans = _GetCertifiedSkillPlansPanel()
    if certified_skill_plans:
        return certified_skill_plans.GetVisibleFactionTabGroup()


def HasFactionTabGroup():
    certified_skill_plans = _GetCertifiedSkillPlansPanel()
    if certified_skill_plans:
        return certified_skill_plans.HasFactionTabGroup()
