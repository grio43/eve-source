#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanConst.py
from eve.common.lib import appConst
from characterdata import careerpathconst
from skills.skillplan.milestone.const import MilestoneSubType
MILESTONE_TRACKER_HEIGHT = 300
TRAINING_TIME_EMPTY_LABEL = '-'
ICON_BY_FACTION_ID = {appConst.factionAmarrEmpire: 'res:/UI/Texture/Classes/SkillPlan/factionButtons/iconAmarr.png',
 appConst.factionGallenteFederation: 'res:/UI/Texture/Classes/SkillPlan/factionButtons/iconGallente.png',
 appConst.factionMinmatarRepublic: 'res:/UI/Texture/Classes/SkillPlan/factionButtons/iconMinmatar.png',
 appConst.factionCaldariState: 'res:/UI/Texture/Classes/SkillPlan/factionButtons/iconCaldari.png'}
MILESTONE_ICON_BY_SUBTYPE = {MilestoneSubType.SHIP_MILESTONE: 'res:/UI/Texture/Classes/SkillPlan/milestones/milestoneShip.png',
 MilestoneSubType.SKILL_MILESTONE: 'res:/UI/Texture/Classes/SkillPlan/milestones/milestoneSkill.png',
 MilestoneSubType.MODULE_MILESTONE: 'res:/UI/Texture/Classes/SkillPlan/milestones/milestoneModule.png',
 MilestoneSubType.OTHER_MILESTONE: 'res:/UI/Texture/Classes/SkillPlan/milestones/milestoneOther.png'}
HINT_BY_FACTION_ID = {appConst.factionAmarrEmpire: 'UI/SkillPlan/SkillPlanFactionAmarr',
 appConst.factionGallenteFederation: 'UI/SkillPlan/SkillPlanFactionGallente',
 appConst.factionMinmatarRepublic: 'UI/SkillPlan/SkillPlanFactionMinmatar',
 appConst.factionCaldariState: 'UI/SkillPlan/SkillPlanFactionCaldari'}
HINT_BY_CAREER_ID = {careerpathconst.career_path_enforcer: 'UI/SkillPlan/SkillPlanCareerPathEnforcer',
 careerpathconst.career_path_explorer: 'UI/SkillPlan/SkillPlanCareerPathExplorer',
 careerpathconst.career_path_industrialist: 'UI/SkillPlan/SkillPlanCareerPathIndustrial',
 careerpathconst.career_path_soldier_of_fortune: 'UI/SkillPlan/SkillPlanCareerPathSoldier'}
AIR_LOCK_ICON_PATH = 'res:/UI/Texture/Classes/SkillPlan/careerPathButtons/lock.png'
IS_PREREQ = -1
NO_REQ = None
REQUIRED_FOR = 1
BUTTON_GROUP_ID_TOP_LEVEL = 'SkillPlanTopLevelPanel'
BUTTON_GROUP_ID_SKILL_PLANS = 'SkillPlanBrowserToggleBtnID'
PANEL_SKILL_PLANS = 1
PANEL_SKILLS_CATALOGUE = 2
PANEL_EXPERT_SYSTEMS = 3
PANEL_CERTIFIED = 1
PANEL_PERSONAL = 2
PANEL_CORP = 3
