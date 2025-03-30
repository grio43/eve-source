#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\careerConst.py
import characterdata.careerpathconst as cpConst
import eveicon
from carbonui.services.setting import CharSettingEnum, CharSettingUUID
import careergoals.client.const as careerGoalsConst
from characterdata import careerpath
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupAbyssalDeadspace, contentGroupAsteroidBelts, contentGroupCareerAgents, contentGroupCombatAnomalies, contentGroupCorp, contentGroupSignatures, contentGroupMissionAgentsDistribution, contentGroupEpicArcs, contentGroupFactionalWarfareAgents, contentGroupFactionalWarfare, contentGroupFactionalWarfareSystems, contentGroupFleetUp, contentGroupHome, contentGroupMissionAgentsMining, contentGroupMissionAgentsSecurity, contentGroupMissionAgentsHeraldry
from itertoolsext.Enum import Enum
from localization import GetByMessageID, GetByLabel
LEVEL_ANIMATION_DURATION = 0.6
HOVER_ANIMATION_DURATION = 0.2
AURA_BADGE_WIDTH = 68
AURA_BADGE_HEIGHT = 75
AGENCY_PAGE_NAME_ABYSSAL_DEADSPACE = 'ABYSSAL_DEADSPACE'
AGENCY_PAGE_NAME_ASTEROID_BELTS = 'ASTEROID_BELTS'
AGENCY_PAGE_NAME_CAREER_AGENTS = 'CAREER_AGENTS'
AGENCY_PAGE_NAME_COMBAT_ANOMOLIES = 'COMBAT_ANOMOLIES'
AGENCY_PAGE_NAME_CORP_RECRUITMENT = 'CORP_RECRUITMENT'
AGENCY_PAGE_NAME_COSMIC_SIGNATURES = 'COSMIC_SIGNATURES'
AGENCY_PAGE_NAME_DISTRIBUTION_AGENTS = 'DISTRIBUTION_AGENTS'
AGENCY_PAGE_NAME_EPIC_ARCS = 'EPIC_ARCS'
AGENCY_PAGE_NAME_FACTION_WARFARE_AGENTS = 'FACTION_WARFARE_AGENTS'
AGENCY_PAGE_NAME_FACTION_WARFARE_INFO = 'FACTION_WARFARE_INFO'
AGENCY_PAGE_NAME_FACTION_WARFARE_LEARN = 'FACTION_WARFARE_LEARN'
AGENCY_PAGE_NAME_FACTION_WARFARE_SYSTEMS = 'FACTION_WARFARE_SYSTEMS'
AGENCY_PAGE_NAME_FLEET_FINDER = 'FLEET_FINDER'
AGENCY_PAGE_NAME_HOMEPAGE = 'HOMEPAGE'
AGENCY_PAGE_NAME_MINING_AGENTS = 'MINING_AGENTS'
AGENCY_PAGE_NAME_SECURITY_AGENTS = 'SECURITY_AGENTS'
AGENCY_PAGE_NAME_HERALDRY_AGENTS = 'HERALDRY_AGENTS'
AGENCY_SECTION_NAMES_TO_IDS = {AGENCY_PAGE_NAME_ABYSSAL_DEADSPACE: contentGroupAbyssalDeadspace,
 AGENCY_PAGE_NAME_ASTEROID_BELTS: contentGroupAsteroidBelts,
 AGENCY_PAGE_NAME_CAREER_AGENTS: contentGroupCareerAgents,
 AGENCY_PAGE_NAME_COMBAT_ANOMOLIES: contentGroupCombatAnomalies,
 AGENCY_PAGE_NAME_CORP_RECRUITMENT: contentGroupCorp,
 AGENCY_PAGE_NAME_COSMIC_SIGNATURES: contentGroupSignatures,
 AGENCY_PAGE_NAME_DISTRIBUTION_AGENTS: contentGroupMissionAgentsDistribution,
 AGENCY_PAGE_NAME_EPIC_ARCS: contentGroupEpicArcs,
 AGENCY_PAGE_NAME_FACTION_WARFARE_AGENTS: contentGroupFactionalWarfareAgents,
 AGENCY_PAGE_NAME_FACTION_WARFARE_INFO: contentGroupFactionalWarfare,
 AGENCY_PAGE_NAME_FACTION_WARFARE_LEARN: contentGroupFactionalWarfare,
 AGENCY_PAGE_NAME_FACTION_WARFARE_SYSTEMS: contentGroupFactionalWarfareSystems,
 AGENCY_PAGE_NAME_FLEET_FINDER: contentGroupFleetUp,
 AGENCY_PAGE_NAME_HOMEPAGE: contentGroupHome,
 AGENCY_PAGE_NAME_MINING_AGENTS: contentGroupMissionAgentsMining,
 AGENCY_PAGE_NAME_SECURITY_AGENTS: contentGroupMissionAgentsSecurity,
 AGENCY_PAGE_NAME_HERALDRY_AGENTS: contentGroupMissionAgentsHeraldry}

def GetCareerPathGroupName(careerPathID, groupID):
    if careerPathID not in careerGoalsConst.CAREER_PATH_GROUPS:
        return None
    careerPathNames = {cpConst.career_path_enforcer: 'Enforcer',
     cpConst.career_path_explorer: 'Explorer',
     cpConst.career_path_industrialist: 'Industrialist',
     cpConst.career_path_soldier_of_fortune: 'SoldierOfFortune'}
    for key, val in careerGoalsConst.CAREER_PATH_GROUPS[careerPathID].iteritems():
        if val == groupID:
            return GetByLabel('Character/CareerGoals/%s/GroupNames/%s' % (careerPathNames[careerPathID], key))


def GetCareerPathName(careerPathID):
    careerInfo = careerpath.get_career_path(careerPathID)
    if careerInfo:
        return GetByMessageID(careerInfo.nameID)


def GetSortedCareerPaths():
    return [cpConst.career_path_explorer,
     cpConst.career_path_soldier_of_fortune,
     cpConst.career_path_industrialist,
     cpConst.career_path_enforcer]


def GetAllActivities():
    result = []
    for values in careerGoalsConst.CAREER_PATH_GROUPS.itervalues():
        result.extend([ a for a in values.itervalues() ])

    return result


HIGHLIGHTED_ACTIVITIES = {cpConst.career_path_enforcer: [careerGoalsConst.ENFORCER_ENFORCERCAREERAGENTMISSIONS],
 cpConst.career_path_soldier_of_fortune: [careerGoalsConst.SOLDIEROFFORTUNE_CAREERAGENTMISSIONS],
 cpConst.career_path_explorer: [careerGoalsConst.EXPLORER_CAREERAGENTMISSIONS],
 cpConst.career_path_industrialist: [careerGoalsConst.INDUSTRIALIST_CAREERAGENTMISSIONS]}
SELECTED_CAREER_PATH_SETTING = CharSettingEnum('careerPortal_selectedCareerPath', None, [cpConst.career_path_none,
 cpConst.career_path_enforcer,
 cpConst.career_path_explorer,
 cpConst.career_path_industrialist,
 cpConst.career_path_soldier_of_fortune])
SELECTED_ACTIVITY_SETTING = CharSettingEnum('careerPortal_selectedActivity', None, GetAllActivities())
SELECTED_GOAL_SETTING = CharSettingUUID('careerPortal_selectedGoal', None)

@Enum

class CareerWindowState(object):
    CAREERS_VIEW = 'CAREERS_VIEW'
    ACTIVITIES_VIEW = 'ACTIVITIES_VIEW'
    GOALS_VIEW = 'GOALS_VIEW'


CAREER_WINDOW_STATE_SETTING = CharSettingEnum('careerPortal_careerWindowState', CareerWindowState.CAREERS_VIEW, [ x for x in CareerWindowState.iterkeys() ])

@Enum

class CareersViewState(object):
    IN_FOCUS = 'IN_FOCUS'
    ONE_DOWN = 'ONE_DOWN'


@Enum

class ActivitiesViewState(object):
    IN_FOCUS = 'IN_FOCUS'
    ONE_DOWN = 'ONE_DOWN'
    HIDDEN = 'HIDDEN'


@Enum

class GoalsViewState(object):
    IN_FOCUS = 'IN_FOCUS'
    HIDDEN = 'HIDDEN'


ICON_BY_CAREER_ID = {cpConst.career_path_enforcer: eveicon.enforcer.resolve(128),
 cpConst.career_path_soldier_of_fortune: eveicon.soldier_of_fortune.resolve(128),
 cpConst.career_path_explorer: eveicon.explorer.resolve(128),
 cpConst.career_path_industrialist: eveicon.industrialist.resolve(128)}
COLOR_BY_CAREER_ID = {cpConst.career_path_enforcer: eveColor.CRYO_BLUE,
 cpConst.career_path_explorer: eveColor.LEAFY_GREEN,
 cpConst.career_path_industrialist: eveColor.SAND_YELLOW,
 cpConst.career_path_soldier_of_fortune: eveColor.DANGER_RED}
BG_IMAGE_BY_CAREER_ID = {cpConst.career_path_enforcer: 'res:/UI/Texture/classes/careerPortal/backgrounds/bg_Enforcer.png',
 cpConst.career_path_explorer: 'res:/UI/Texture/classes/careerPortal/backgrounds/bg_Explorer.png',
 cpConst.career_path_industrialist: 'res:/UI/Texture/classes/careerPortal/backgrounds/bg_Industrialist.png',
 cpConst.career_path_soldier_of_fortune: 'res:/UI/Texture/classes/careerPortal/backgrounds/bg_SoldierOfFortune.png'}
BG_DETAIL_BY_CAREER_ID = {cpConst.career_path_enforcer: 'res:/UI/Texture/classes/careerPortal/backgrounds/bg_detail_topLeft.png',
 cpConst.career_path_explorer: 'res:/UI/Texture/classes/careerPortal/backgrounds/bg_detail_topRight.png',
 cpConst.career_path_industrialist: 'res:/UI/Texture/classes/careerPortal/backgrounds/bg_detail_bottomLeft.png',
 cpConst.career_path_soldier_of_fortune: 'res:/UI/Texture/classes/careerPortal/backgrounds/bg_detail_bottomRight.png'}
ICON_BY_ACTIVITY_ID = {careerGoalsConst.EXPLORER_CAREERAGENTMISSIONS: 'res:/UI/Texture/classes/careerPortal/activities/explorer_agent_32.png',
 careerGoalsConst.EXPLORER_SCANNING: 'res:/UI/Texture/classes/careerPortal/activities/scanning_32.png',
 careerGoalsConst.EXPLORER_HACKING: 'res:/UI/Texture/classes/careerPortal/activities/hacking_32.png',
 careerGoalsConst.EXPLORER_HACKING2: 'res:/UI/Texture/classes/careerPortal/activities/advanced_hacking_32.png',
 careerGoalsConst.EXPLORER_WORMHOLES: 'res:/UI/Texture/classes/careerPortal/activities/wormholes_32.png',
 careerGoalsConst.EXPLORER_GASSITES: 'res:/UI/Texture/classes/careerPortal/activities/gas_sites_32.png',
 careerGoalsConst.EXPLORER_COMBATSITES: 'res:/UI/Texture/classes/careerPortal/activities/combat_sites_32.png',
 careerGoalsConst.EXPLORER_NAVIGATION: 'res:/UI/Texture/classes/careerPortal/activities/navigation_32.png',
 careerGoalsConst.EXPLORER_NAVIGATION2: 'res:/UI/Texture/classes/careerPortal/activities/advanced_navigation_32.png',
 careerGoalsConst.EXPLORER_PROJECTDISCOVERY: 'res:/UI/Texture/classes/careerPortal/activities/project_discovery_32.png',
 careerGoalsConst.INDUSTRIALIST_CAREERAGENTMISSIONS: 'res:/UI/Texture/classes/careerPortal/activities/industrialist_agent_32.png',
 careerGoalsConst.INDUSTRIALIST_MARKET: 'res:/UI/Texture/classes/careerPortal/activities/market_32.png',
 careerGoalsConst.INDUSTRIALIST_SALVAGE: 'res:/UI/Texture/classes/careerPortal/activities/salvaging_32.png',
 careerGoalsConst.INDUSTRIALIST_RESOURCEHARVESTING: 'res:/UI/Texture/classes/careerPortal/activities/explorer_agent_32.png',
 careerGoalsConst.INDUSTRIALIST_REFINING: 'res:/UI/Texture/classes/careerPortal/activities/refining_32.png',
 careerGoalsConst.INDUSTRIALIST_MANUFACTURING: 'res:/UI/Texture/classes/careerPortal/activities/industry_32.png',
 careerGoalsConst.INDUSTRIALIST_DISTRIBUTIONAGENT: 'res:/UI/Texture/classes/careerPortal/activities/industrialist_agent_32.png',
 careerGoalsConst.INDUSTRIALIST_MININGAGENT: 'res:/UI/Texture/classes/careerPortal/activities/mining_agent_32.png',
 careerGoalsConst.INDUSTRIALIST_RESEARCH: 'res:/UI/Texture/classes/careerPortal/activities/research_32.png',
 careerGoalsConst.ENFORCER_ENFORCERCAREERAGENTMISSIONS: 'res:/UI/Texture/classes/careerPortal/activities/enforcer_agent_32.png',
 careerGoalsConst.ENFORCER_SECURITYAGENT: 'res:/UI/Texture/classes/careerPortal/activities/enforcer_agent_32.png',
 careerGoalsConst.ENFORCER_ABYSSALDEADSPACE: 'res:/UI/Texture/classes/careerPortal/activities/abyssal_filament_32.png',
 careerGoalsConst.ENFORCER_COMBAT: 'res:/UI/Texture/classes/careerPortal/activities/combat_32.png',
 careerGoalsConst.ENFORCER_BOUNTIES: 'res:/UI/Texture/classes/careerPortal/activities/bounties_32.png',
 careerGoalsConst.ENFORCER_COMBATSITES: 'res:/UI/Texture/classes/careerPortal/activities/combat_sites_32.png',
 careerGoalsConst.ENFORCER_EPICARC: 'res:/UI/Texture/classes/careerPortal/activities/epic_arc_32.png',
 careerGoalsConst.ENFORCER_MARKET: 'res:/UI/Texture/classes/careerPortal/activities/market_32.png',
 careerGoalsConst.ENFORCER_STANDINGS: 'res:/UI/Texture/classes/careerPortal/activities/standings_32.png',
 careerGoalsConst.ENFORCER_LOYALTYPOINTS: 'res:/UI/Texture/classes/careerPortal/activities/loyalty_points_32.png',
 careerGoalsConst.SOLDIEROFFORTUNE_CAREERAGENTMISSIONS: 'res:/UI/Texture/classes/careerPortal/activities/sof_agent_32.png',
 careerGoalsConst.SOLDIEROFFORTUNE_SOCIAL: 'res:/UI/Texture/classes/careerPortal/activities/social_32.png',
 careerGoalsConst.SOLDIEROFFORTUNE_ELECTRONICWARFARE: 'res:/UI/Texture/classes/careerPortal/activities/electronicwarfare_32.png',
 careerGoalsConst.SOLDIEROFFORTUNE_COMBAT1: 'res:/UI/Texture/classes/careerPortal/activities/combat_32.png',
 careerGoalsConst.SOLDIEROFFORTUNE_PVP: 'res:/UI/Texture/classes/careerPortal/activities/duel_pvp_32.png',
 careerGoalsConst.SOLDIEROFFORTUNE_CAPACITORWARFARE: 'res:/UI/Texture/classes/careerPortal/activities/cap_warfare_32.png',
 careerGoalsConst.SOLDIEROFFORTUNE_FACTIONWARFARE: 'res:/UI/Texture/classes/careerPortal/activities/faction_warfare_32.png',
 careerGoalsConst.SOLDIEROFFORTUNE_SUPPORT: 'res:/UI/Texture/classes/careerPortal/activities/fleet_support_32.png',
 careerGoalsConst.SOLDIEROFFORTUNE_DESTRUCTION: 'res:/UI/Texture/classes/careerPortal/activities/destroy_32.png',
 careerGoalsConst.SOLDIEROFFORTUNE_DUELS: 'res:/UI/Texture/classes/careerPortal/activities/duel_pvp_32.png'}
THREAT_NAMES = {careerGoalsConst.GoalThreat.THREAT_NONE: 'UI/CareerPortal/Threat0',
 careerGoalsConst.GoalThreat.THREAT_LOW: 'UI/CareerPortal/Threat1',
 careerGoalsConst.GoalThreat.THREAT_MEDIUM: 'UI/CareerPortal/Threat2',
 careerGoalsConst.GoalThreat.THREAT_HIGH: 'UI/CareerPortal/Threat3'}

def get_threat_name(threat_level):
    labelPath = THREAT_NAMES.get(threat_level, None)
    if labelPath:
        return GetByLabel(labelPath)
    return ''


CRATE_128_SIZES = {cpConst.career_path_enforcer: 'res:/UI/Texture/classes/careerPortal/crates/enforcerCrate_128.png',
 cpConst.career_path_soldier_of_fortune: 'res:/UI/Texture/classes/careerPortal/crates/sofCrate_128.png',
 cpConst.career_path_explorer: 'res:/UI/Texture/classes/careerPortal/crates/explorerCrate_128.png',
 cpConst.career_path_industrialist: 'res:/UI/Texture/classes/careerPortal/crates/industrialistCrate_128.png'}
CRATE_64_SIZES = {cpConst.career_path_enforcer: 'res:/UI/Texture/classes/careerPortal/crates/enforcerCrate_64.png',
 cpConst.career_path_soldier_of_fortune: 'res:/UI/Texture/classes/careerPortal/crates/sofCrate_64.png',
 cpConst.career_path_explorer: 'res:/UI/Texture/classes/careerPortal/crates/explorerCrate_64.png',
 cpConst.career_path_industrialist: 'res:/UI/Texture/classes/careerPortal/crates/industrialistCrate_64.png'}
CAREERS_32_SIZES = {cpConst.career_path_enforcer: eveicon.enforcer.resolve(32),
 cpConst.career_path_soldier_of_fortune: eveicon.soldier_of_fortune.resolve(32),
 cpConst.career_path_explorer: eveicon.explorer.resolve(32),
 cpConst.career_path_industrialist: eveicon.industrialist.resolve(32),
 cpConst.career_path_none: eveicon.unclassified.resolve(32)}
CAREERS_16_SIZES = {cpConst.career_path_enforcer: eveicon.enforcer.resolve(16),
 cpConst.career_path_soldier_of_fortune: eveicon.soldier_of_fortune.resolve(16),
 cpConst.career_path_explorer: eveicon.explorer.resolve(16),
 cpConst.career_path_industrialist: eveicon.industrialist.resolve(16),
 cpConst.career_path_none: eveicon.unclassified.resolve(16)}
CAREERS_BG_FLAIR = {cpConst.career_path_enforcer: 'res:/UI/Texture/Shared/CareerPaths/enforcer_flair.png',
 cpConst.career_path_soldier_of_fortune: 'res:/UI/Texture/Shared/CareerPaths/sof_flair.png',
 cpConst.career_path_explorer: 'res:/UI/Texture/Shared/CareerPaths/explorer_flair.png',
 cpConst.career_path_industrialist: 'res:/UI/Texture/Shared/CareerPaths/industrialist_flair.png',
 cpConst.career_path_none: 'res:/UI/Texture/Shared/CareerPaths/unclassified_flair.png'}
CAREER_VIDEOS = {cpConst.career_path_enforcer: 'res:/video/AIRCareerProgram/CareerIntros/Enforcer_Intro.webm',
 cpConst.career_path_soldier_of_fortune: 'res:/video/AIRCareerProgram/CareerIntros/SOF_Intro.webm',
 cpConst.career_path_explorer: 'res:/video/AIRCareerProgram/CareerIntros/Exploration_Intro.webm',
 cpConst.career_path_industrialist: 'res:/video/AIRCareerProgram/CareerIntros/Industry_Intro.webm'}
CIRCLE_ROTATION_BY_CAREER = {cpConst.career_path_none: 0,
 cpConst.career_path_enforcer: -45,
 cpConst.career_path_soldier_of_fortune: -45,
 cpConst.career_path_explorer: 45,
 cpConst.career_path_industrialist: 45}
CAREER_DESCRIPTIONS = {cpConst.career_path_enforcer: 'UI/CareerPortal/EnforcerDescriptionShort',
 cpConst.career_path_explorer: 'UI/CareerPortal/ExplorerDescriptionShort',
 cpConst.career_path_industrialist: 'UI/CareerPortal/IndustrialistDescriptionShort',
 cpConst.career_path_soldier_of_fortune: 'UI/CareerPortal/SoldierDescriptionShort'}
