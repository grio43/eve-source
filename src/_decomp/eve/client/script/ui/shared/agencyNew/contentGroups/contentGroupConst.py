#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\contentGroupConst.py
import eve.client.script.ui.shared.comtool.constants as chatConst
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.pointerTool.pointerToolConst import GetUniqueAgencyContentPageName
import re
contentGroupHome = 1
contentGroupEvents = 2
contentGroupActivities = 3
contentGroupFleetFinder = 4
contentGroupMissions = 11
contentGroupEncounters = 12
contentGroupExploration = 13
contentGroupResourceHarvesting = 14
contentGroupCareerAgents = 21
contentGroupMissionAgents = 22
contentGroupMissionAgentsSecurity = 23
contentGroupMissionAgentsMining = 24
contentGroupMissionAgentsDistribution = 25
contentGroupMissionAgentsResearch = 26
contentGroupMissionAgentsLocator = 27
contentGroupAgentFinder = 28
contentGroupEpicArcs = 33
contentGroupSeasons = 34
contentGroupFactionalWarfare = 35
contentGroupAbyssalDeadspace = 37
contentGroupCombatAnomalies = 38
contentGroupSignatures = 39
contentGroupAsteroidBelts = 40
contentGroupIceBelts = 41
contentGroupPlanetaryProduction = 42
contentGroupAbyssalFilaments = 44
contentGroupEscalations = 45
contentGroupFactionalWarfareSystems = 46
contentGroupFactionalWarfareAgents = 47
contentGroupOreAnomalies = 48
contentGroupIncursion = 50
contentGroupStorylineAgents = 51
contentGroupProjectDiscovery = 52
contentGroupCorp = 62
contentGroupTriglavianSpace = 63
contentGroupTriglavianFilaments = 64
contentGroupESSSystems = 65
contentGroupFleetUp = 67
contentGroupFleetUpRegister = 68
contentGroupHelp = 69
contentGroupMissionAgentsHeraldry = 71
contentGroupIncursions = 72
contentGroupPirateStrongholds = 73
contentGroupHomefrontSites = 78
contentGroupPirateIncursions = 79
contentGroupPirateIncursion = 80
contentGroupPirateIncursionsHome = 81
contentGroupPirateIncursionsGuide = 82
contentGroupZarzakh = 83
contentGroupColonyResourcesAgency = 84
contentGroupMercDens = 85
contentGroupPlanetHarvesting = 86
NEW_FEATURE_CONTENT_GROUP_OFFSET = 10000
contentGroupBookmarkableBlacklist = (contentGroupHome, contentGroupIncursion, contentGroupSeasons)
contentGroupNameByID = {contentGroupHome: 'UI/Agency/ContentGroups/ContentGroupHome',
 contentGroupEvents: 'UI/Agency/ContentGroups/ContentGroupEvents',
 contentGroupActivities: 'UI/Agency/ContentGroups/ContentGroupActivities',
 contentGroupFleetFinder: 'UI/Agency/ContentGroups/ContentGroupFleetFinder',
 contentGroupMissions: 'UI/Agency/ContentGroups/ContentGroupMissions',
 contentGroupEncounters: 'UI/Agency/ContentGroups/ContentGroupEncounters',
 contentGroupExploration: 'UI/Agency/ContentGroups/ContentGroupExploration',
 contentGroupResourceHarvesting: 'UI/Agency/ContentGroups/ContentGroupResourceHarvesting',
 contentGroupCareerAgents: 'UI/Agency/ContentGroups/ContentGroupCareerAgents',
 contentGroupMissionAgents: 'UI/Agency/ContentGroups/ContentGroupMissionAgents',
 contentGroupMissionAgentsSecurity: 'UI/Agency/ContentGroups/ContentGroupMissionAgentsSecurity',
 contentGroupMissionAgentsMining: 'UI/Agency/ContentGroups/ContentGroupMissionAgentsMining',
 contentGroupMissionAgentsDistribution: 'UI/Agency/ContentGroups/ContentGroupMissionAgentsDistribution',
 contentGroupMissionAgentsResearch: 'UI/Agency/ContentGroups/ContentGroupMissionAgentsResearch',
 contentGroupMissionAgentsLocator: 'UI/Agency/ContentGroups/ContentGroupMissionAgentsLocator',
 contentGroupAgentFinder: 'UI/Agency/ContentGroups/ContentGroupAgentFinder',
 contentGroupEpicArcs: 'UI/Agency/ContentGroups/ContentGroupEpicArcs',
 contentGroupIncursions: 'UI/Agency/ContentGroups/ContentGroupIncursions',
 contentGroupFactionalWarfare: 'UI/Agency/ContentGroups/ContentGroupFactionalWarfare',
 contentGroupPirateStrongholds: 'UI/Agency/ContentGroups/ContentGroupPirateStrongholds',
 contentGroupAbyssalDeadspace: 'UI/Agency/ContentGroups/ContentGroupAbyssalDeadspace',
 contentGroupCombatAnomalies: 'UI/Agency/ContentGroups/ContentGroupCombatAnomalies',
 contentGroupOreAnomalies: 'UI/Agency/ContentGroups/ContentGroupOreAnomalies',
 contentGroupSignatures: 'UI/Agency/ContentGroups/ContentGroupSignatures',
 contentGroupEscalations: 'UI/Agency/ContentGroups/ContentGroupEscalations',
 contentGroupAsteroidBelts: 'UI/Agency/ContentGroups/ContentGroupAsteroidBelts',
 contentGroupIceBelts: 'UI/Agency/ContentGroups/ContentGroupIceBelts',
 contentGroupPlanetaryProduction: 'UI/Agency/ContentGroups/ContentGroupPlanetaryProduction',
 contentGroupAbyssalFilaments: 'UI/Agency/ContentGroups/ContentGroupAbyssalFilaments',
 contentGroupFactionalWarfareAgents: 'UI/Agency/ContentGroups/ContentGroupFactionalWarfareAgents',
 contentGroupFactionalWarfareSystems: 'UI/Agency/ContentGroups/ContentGroupFactionalWarfareSystems',
 contentGroupStorylineAgents: 'UI/Agency/ContentGroups/ContentGroupStorylineAgents',
 contentGroupProjectDiscovery: 'UI/Agency/ContentGroups/ContentGroupProjectDiscovery',
 contentGroupCorp: 'UI/Agency/ContentGroups/ContentGroupCorp',
 (contentGroupCorp, 1): 'UI/Agency/ContentGroups/ContentGroupCorp2',
 contentGroupTriglavianSpace: 'UI/Agency/ContentGroups/ContentGroupTriglavianSpace',
 contentGroupTriglavianFilaments: 'UI/Agency/ContentGroups/ContentGroupTriglavianFilaments',
 contentGroupESSSystems: 'UI/Agency/ContentGroups/ContentGroupESS',
 contentGroupFleetUp: 'UI/Agency/ContentGroups/ContentGroupFleetUp',
 contentGroupFleetUpRegister: 'UI/Agency/ContentGroups/ContentGroupFleetUpRegistration',
 contentGroupHelp: 'UI/Agency/ContentGroups/ContentGroupHelp',
 contentGroupMissionAgentsHeraldry: 'UI/Agency/ContentGroups/ContentGroupMissionAgentsHeraldry',
 contentGroupHomefrontSites: 'UI/Agency/ContentGroups/ContentGroupHomefrontSites',
 contentGroupPirateIncursions: 'UI/Agency/ContentGroups/ContentGroupPirateIncursions',
 contentGroupPirateIncursionsHome: 'UI/Agency/ContentGroups/contentGroupPirateIncursionsHome',
 contentGroupPirateIncursionsGuide: 'UI/Agency/ContentGroups/ContentGroupPirateIncursionsGuide',
 contentGroupZarzakh: 'UI/Agency/ContentGroups/ContentGroupZarzakh',
 contentGroupColonyResourcesAgency: 'UI/Agency/ContentGroups/ContentGroupColonyResourcesAgency',
 contentGroupMercDens: 'UI/Agency/ContentGroups/ContentGroupMercDens',
 contentGroupPlanetHarvesting: 'UI/Agency/ContentGroups/PlanetHarvesting'}

def get_content_group_name(content_group_id):
    extended_content_group_name = contentGroupNameByID.get(content_group_id, '')
    if extended_content_group_name:
        match = re.search('UI/Agency/ContentGroups/ContentGroup(.*)', extended_content_group_name)
        if match:
            group_name = match.group(1)
            if group_name:
                return GetUniqueAgencyContentPageName(group_name)
    return ''


contentGroupDescriptionByID = {contentGroupEvents: 'UI/Agency/ContentGroups/Descriptions/Events',
 contentGroupActivities: 'UI/Agency/ContentGroups/Descriptions/Activities',
 contentGroupFleetFinder: 'UI/Agency/ContentGroups/Descriptions/FleetFinder',
 contentGroupMissions: 'UI/Agency/ContentGroups/Descriptions/Missions',
 contentGroupEncounters: 'UI/Agency/ContentGroups/Descriptions/Encounters',
 contentGroupExploration: 'UI/Agency/ContentGroups/Descriptions/Exploration',
 contentGroupResourceHarvesting: 'UI/Agency/ContentGroups/Descriptions/ResourceHarvesting',
 contentGroupCareerAgents: 'UI/Agency/ContentGroups/Descriptions/CareerAgents',
 contentGroupMissionAgents: 'UI/Agency/ContentGroups/Descriptions/MissionAgents',
 contentGroupMissionAgentsSecurity: 'UI/Agency/ContentGroups/Descriptions/MissionAgentsSecurity',
 contentGroupMissionAgentsMining: 'UI/Agency/ContentGroups/Descriptions/MissionAgentsMining',
 contentGroupMissionAgentsDistribution: 'UI/Agency/ContentGroups/Descriptions/MissionAgentsDistribution',
 contentGroupMissionAgentsResearch: 'UI/Agency/ContentGroups/Descriptions/MissionAgentsResearch',
 contentGroupMissionAgentsLocator: 'UI/Agency/ContentGroups/Descriptions/MissionAgentsLocator',
 contentGroupAgentFinder: 'UI/Agency/ContentGroups/Descriptions/AgentFinder',
 contentGroupEpicArcs: 'UI/Agency/ContentGroups/Descriptions/EpicArcs',
 contentGroupIncursions: 'UI/Agency/ContentGroups/Descriptions/Incursions',
 contentGroupFactionalWarfare: 'UI/Agency/ContentGroups/Descriptions/FactionalWarfare',
 contentGroupPirateStrongholds: 'UI/Agency/ContentGroups/Descriptions/PirateStrongholds',
 contentGroupAbyssalDeadspace: 'UI/Agency/ContentGroups/Descriptions/AbyssalDeadspace',
 contentGroupCombatAnomalies: 'UI/Agency/ContentGroups/Descriptions/CombatAnomalies',
 contentGroupOreAnomalies: 'UI/Agency/ContentGroups/Descriptions/OreAnomalies',
 contentGroupSignatures: 'UI/Agency/ContentGroups/Descriptions/Signatures',
 contentGroupEscalations: 'UI/Agency/ContentGroups/Descriptions/Escalations',
 contentGroupAsteroidBelts: 'UI/Agency/ContentGroups/Descriptions/AsteroidBelts',
 contentGroupIceBelts: 'UI/Agency/ContentGroups/Descriptions/IceBelts',
 contentGroupPlanetaryProduction: 'UI/Agency/ContentGroups/Descriptions/PlanetaryProduction',
 contentGroupAbyssalFilaments: 'UI/Agency/ContentGroups/Descriptions/AbyssalFilaments',
 contentGroupFactionalWarfareAgents: 'UI/Agency/ContentGroups/Descriptions/FactionalWarfareAgents',
 contentGroupFactionalWarfareSystems: 'UI/Agency/ContentGroups/Descriptions/FactionalWarfareSystems',
 contentGroupStorylineAgents: 'UI/Agency/ContentGroups/Descriptions/StorylineAgents',
 contentGroupProjectDiscovery: 'UI/Agency/ContentGroups/Descriptions/ProjectDiscovery',
 contentGroupSeasons: 'UI/Agency/ContentGroups/Descriptions/Seasons',
 contentGroupCorp: 'UI/Agency/ContentGroups/Descriptions/Corp',
 (contentGroupCorp, 1): 'UI/Agency/ContentGroups/Descriptions/Corp2',
 contentGroupTriglavianSpace: 'UI/Agency/ContentGroups/Descriptions/TriglavianSpace',
 contentGroupFleetUp: 'UI/Agency/ContentGroups/Descriptions/FleetUp',
 contentGroupESSSystems: 'UI/Agency/ContentGroups/Descriptions/ESS',
 contentGroupHelp: 'UI/Agency/ContentGroups/Descriptions/Help',
 contentGroupMissionAgentsHeraldry: 'UI/Agency/ContentGroups/Descriptions/MissionAgentsHeraldry',
 contentGroupHomefrontSites: 'UI/Agency/ContentGroups/Descriptions/HomefrontSites',
 contentGroupPirateIncursions: 'UI/Agency/ContentGroups/Descriptions/PirateIncursions',
 contentGroupPirateIncursionsHome: 'UI/Agency/ContentGroups/Descriptions/PirateIncursionsHome',
 contentGroupPirateIncursionsGuide: 'UI/Agency/ContentGroups/Descriptions/PirateIncursionsGuide',
 contentGroupZarzakh: 'UI/Agency/ContentGroups/Descriptions/Zarzakh',
 contentGroupColonyResourcesAgency: 'UI/Agency/ContentGroups/Descriptions/ColonyResourcesAgency',
 contentGroupMercDens: 'UI/Agency/ContentGroups/Descriptions/MercDens',
 contentGroupPlanetHarvesting: 'UI/Agency/ContentGroups/Descriptions/PlanetHarvesting'}
contentGroupHintByContentGroup = {contentGroupMissions: 'UI/Agency/Tooltips/NavigationCards/Agents&Missions',
 contentGroupEncounters: 'UI/Agency/Tooltips/NavigationCards/Encounters',
 contentGroupExploration: 'UI/Agency/Tooltips/NavigationCards/Exploration',
 contentGroupResourceHarvesting: 'UI/Agency/Tooltips/NavigationCards/ResourceHarvesting',
 contentGroupCareerAgents: 'UI/Agency/Tooltips/NavigationCards/CareerAgents',
 contentGroupMissionAgents: 'UI/Agency/Tooltips/NavigationCards/MissionAgents',
 contentGroupEpicArcs: 'UI/Agency/Tooltips/NavigationCards/EpicArcs',
 contentGroupAgentFinder: 'UI/Agency/Tooltips/NavigationCards/AgentFinder',
 contentGroupStorylineAgents: 'UI/Agency/Tooltips/NavigationCards/StorylineMissions',
 contentGroupMissionAgentsSecurity: 'UI/Agency/Tooltips/NavigationCards/SecurityAgents',
 contentGroupMissionAgentsMining: 'UI/Agency/Tooltips/NavigationCards/MiningAgents',
 contentGroupMissionAgentsDistribution: 'UI/Agency/Tooltips/NavigationCards/DistributionAgents',
 contentGroupMissionAgentsResearch: 'UI/Agency/Tooltips/NavigationCards/R&DAgents',
 contentGroupMissionAgentsLocator: 'UI/Agency/Tooltips/NavigationCards/LocatorAgents',
 contentGroupAsteroidBelts: 'UI/Agency/Tooltips/NavigationCards/AsteroidBelts',
 contentGroupIceBelts: 'UI/Agency/Tooltips/NavigationCards/IceBelts',
 contentGroupOreAnomalies: 'UI/Agency/Tooltips/NavigationCards/OreSites',
 contentGroupPlanetaryProduction: 'UI/Agency/Tooltips/NavigationCards/PlanetaryProduction',
 contentGroupIncursions: 'UI/Agency/Tooltips/NavigationCards/Incursions',
 contentGroupFactionalWarfare: 'UI/Agency/Tooltips/NavigationCards/FactionalWarfare',
 contentGroupPirateStrongholds: 'UI/Agency/Tooltips/NavigationCards/PirateStronghold',
 contentGroupAbyssalDeadspace: 'UI/Agency/Tooltips/NavigationCards/AbyssalDeadspace',
 contentGroupCombatAnomalies: 'UI/Agency/Tooltips/NavigationCards/CombatAnomalies',
 contentGroupSignatures: 'UI/Agency/Tooltips/NavigationCards/CosmicSignatures',
 contentGroupProjectDiscovery: 'UI/Agency/Tooltips/NavigationCards/ProjectDiscovery',
 contentGroupEscalations: 'UI/Agency/Tooltips/NavigationCards/Escalations',
 contentGroupSeasons: 'UI/Agency/Tooltips/NavigationCards/Seasons',
 contentGroupTriglavianSpace: 'UI/Agency/TriglavianSpace/OverviewDescription',
 contentGroupFleetUp: 'UI/Agency/Tooltips/NavigationCards/FleetUp',
 contentGroupESSSystems: 'UI/Agency/Tooltips/NavigationCards/ESS',
 contentGroupHelp: 'UI/Agency/Tooltips/NavigationCards/Help',
 contentGroupMissionAgentsHeraldry: 'UI/Agency/Tooltips/NavigationCards/HeraldryAgents',
 contentGroupHomefrontSites: 'UI/Agency/Tooltips/NavigationCards/HomefrontSites',
 contentGroupPirateIncursions: 'UI/Agency/ContentGroups/ContentGroupPirateIncursions',
 contentGroupPirateIncursionsHome: 'UI/Agency/Tooltips/NavigationCards/PirateIncursionsHome',
 contentGroupPirateIncursionsGuide: 'UI/Agency/ContentGroups/ContentGroupPirateIncursionsGuide',
 contentGroupZarzakh: 'UI/Agency/Tooltips/NavigationCards/Zarzakh',
 contentGroupColonyResourcesAgency: 'UI/Agency/Tooltips/NavigationCards/ColonyResourcesAgency',
 contentGroupMercDens: 'UI/Agency/Tooltips/NavigationCards/MercDens',
 contentGroupPlanetHarvesting: 'UI/Agency/Tooltips/NavigationCards/PlanetHarvesting'}
groupActivityContentGroups = [contentGroupIncursions,
 contentGroupPirateStrongholds,
 contentGroupFactionalWarfare,
 contentGroupHomefrontSites,
 contentGroupPirateIncursionsHome]
cardBackgroundByContentGroup = {contentGroupMissions: 'res:/UI/Texture/Classes/Agency/navigationCards/card_AgentsMissions.png',
 contentGroupEncounters: 'res:/UI/Texture/Classes/Agency/navigationCards/card_Encounters.png',
 contentGroupExploration: 'res:/UI/Texture/Classes/Agency/navigationCards/card_Exploration.png',
 contentGroupResourceHarvesting: 'res:/UI/Texture/Classes/Agency/navigationCards/card_ResourceHarvesting.png',
 contentGroupCareerAgents: 'res:/UI/Texture/Classes/Agency/navigationCards/card_CareerAgents.png',
 contentGroupMissionAgents: 'res:/UI/Texture/Classes/Agency/navigationCards/card_MissionAgents.png',
 contentGroupMissionAgentsSecurity: 'res:/UI/Texture/Classes/Agency/navigationCards/card_AgentsSecurity.png',
 contentGroupMissionAgentsMining: 'res:/UI/Texture/Classes/Agency/navigationCards/card_AgentsMining.png',
 contentGroupMissionAgentsDistribution: 'res:/UI/Texture/Classes/Agency/navigationCards/card_AgentsDistribution.png',
 contentGroupMissionAgentsResearch: 'res:/UI/Texture/Classes/Agency/navigationCards/card_AgentsR&D.png',
 contentGroupMissionAgentsLocator: 'res:/UI/Texture/Classes/Agency/navigationCards/card_AgentsLocator.png',
 contentGroupAgentFinder: 'res:/UI/Texture/Classes/Agency/navigationCards/card_AgentFinder.png',
 contentGroupEpicArcs: 'res:/UI/Texture/Classes/Agency/navigationCards/card_EpicArcs.png',
 contentGroupFactionalWarfare: 'res:/UI/Texture/Classes/Agency/navigationCards/card_FactionalWarfare.png',
 contentGroupPirateStrongholds: 'res:/UI/Texture/Classes/Agency/navigationCards/card_PirateStrongholds.png',
 contentGroupAbyssalDeadspace: 'res:/UI/Texture/Classes/Agency/navigationCards/card_AbyssalDeadspace.png',
 contentGroupCombatAnomalies: 'res:/UI/Texture/Classes/Agency/navigationCards/card_CombatSites.png',
 contentGroupSignatures: 'res:/UI/Texture/Classes/Agency/navigationCards/card_CosmicSignatures.png',
 contentGroupAsteroidBelts: 'res:/UI/Texture/Classes/Agency/navigationCards/card_AsteroidBelts.png',
 contentGroupIceBelts: 'res:/UI/Texture/Classes/Agency/navigationCards/card_IceBelts.png',
 contentGroupPlanetaryProduction: 'res:/UI/Texture/Classes/Agency/navigationCards/card_PlanetaryProduction.png',
 contentGroupAbyssalFilaments: 'res:/UI/Texture/Classes/Agency/navigationCards/card_AbyssalWeather.png',
 contentGroupEscalations: 'res:/UI/Texture/Classes/Agency/navigationCards/card_Escalations.png',
 contentGroupFactionalWarfareSystems: 'res:/UI/Texture/Classes/Agency/navigationCards/card_FWSystems.png',
 contentGroupFactionalWarfareAgents: 'res:/UI/Texture/Classes/Agency/navigationCards/card_FWAgents.png',
 contentGroupOreAnomalies: 'res:/UI/Texture/Classes/Agency/navigationCards/card_OreSites.png',
 contentGroupIncursions: 'res:/UI/Texture/Classes/Agency/navigationCards/card_Incursions.png',
 contentGroupIncursion: 'res:/UI/Texture/Classes/Agency/navigationCards/card_Incursions.png',
 contentGroupStorylineAgents: 'res:/UI/Texture/Classes/Agency/navigationCards/card_StorylineMissions.png',
 contentGroupProjectDiscovery: 'res:/UI/Texture/Classes/Agency/navigationCards/card_ProjectDiscovery.png',
 contentGroupCorp: 'res:/UI/Texture/Classes/Agency/navigationCards/card_CorpSmall.png',
 contentGroupTriglavianSpace: 'res:/UI/Texture/Classes/Agency/navigationCards/TriglavianSpace.png',
 contentGroupTriglavianFilaments: 'res:/UI/Texture/Classes/Agency/navigationCards/TriglavianFilaments.png',
 contentGroupFleetUp: 'res:/UI/Texture/Classes/Agency/navigationCards/EveEvolvedSmall.png',
 contentGroupESSSystems: 'res:/UI/Texture/Classes/Agency/navigationCards/card_EncounterSurveillanceSystem.png',
 contentGroupHelp: 'res:/UI/Texture/Classes/Agency/navigationCards/card_HelpVideos.png',
 contentGroupMissionAgentsHeraldry: 'res:/UI/Texture/Classes/Agency/navigationCards/card_AgentsHeraldry.png',
 contentGroupHomefrontSites: 'res:/UI/Texture/Classes/Agency/navigationCards/card_HomefrontSites.png',
 contentGroupPirateIncursions: 'res:/UI/Texture/Classes/Agency/navigationCards/PirateInsurgencySystems.png',
 contentGroupPirateIncursionsHome: 'res:/UI/Texture/Classes/Agency/navigationCards/card_PirateInsurgencies.png',
 contentGroupPirateIncursionsGuide: 'res:/UI/Texture/Classes/Agency/navigationCards/PirateInsurgencyGuide.png',
 contentGroupZarzakh: 'res:/UI/Texture/Classes/Agency/navigationCards/card_Zarzakh.png',
 contentGroupColonyResourcesAgency: 'res:/UI/Texture/Classes/Agency/navigationCards/card_ColonyResourcesAgency.png',
 contentGroupMercDens: 'res:/UI/Texture/Classes/Agency/navigationCards/card_MercDen.png',
 contentGroupPlanetHarvesting: 'res:/UI/Texture/Classes/Agency/navigationCards/card_PlanetHarvesting.png'}
contentTypeByContentGroup = {contentGroupEvents: agencyConst.CONTENTTYPE_AGENCY,
 contentGroupCareerAgents: agencyConst.CONTENTTYPE_CAREERAGENTS,
 contentGroupEpicArcs: agencyConst.CONTENTTYPE_EPICARCS,
 contentGroupIncursions: agencyConst.CONTENTTYPE_INCURSIONS,
 contentGroupIncursion: agencyConst.CONTENTTYPE_INCURSIONS,
 contentGroupPirateStrongholds: agencyConst.CONTENTTYPE_PIRATE_STRONGHOLD,
 contentGroupCombatAnomalies: agencyConst.CONTENTTYPE_SITES,
 contentGroupSignatures: agencyConst.CONTENTTYPE_SIGNATURES,
 contentGroupEscalations: agencyConst.CONTENTTYPE_ESCALATION,
 contentGroupAsteroidBelts: agencyConst.CONTENTTYPE_ASTEROIDBELTS,
 contentGroupIceBelts: agencyConst.CONTENTTYPE_ICEBELTS,
 contentGroupMissionAgentsSecurity: agencyConst.CONTENTTYPE_SECURITYAGENTS,
 contentGroupMissionAgentsMining: agencyConst.CONTENTTYPE_MININGAGENTS,
 contentGroupMissionAgentsDistribution: agencyConst.CONTENTTYPE_DISTRIBUTIONAGENTS,
 contentGroupMissionAgentsResearch: agencyConst.CONTENTTYPE_RESEARCHAGENTS,
 contentGroupMissionAgentsLocator: agencyConst.CONTENTTYPE_LOCATORAGENTS,
 contentGroupAbyssalFilaments: agencyConst.CONTENTTYPE_ABYSSALDEADSPACE,
 contentGroupAgentFinder: agencyConst.CONTENTTYPE_AGENTS,
 contentGroupFactionalWarfareAgents: agencyConst.CONTENTTYPE_FACTIONALWARFAREAGENTS,
 contentGroupFactionalWarfareSystems: agencyConst.CONTENTTYPE_FACTIONALWARFARESYSTEM,
 contentGroupPlanetaryProduction: agencyConst.CONTENTTYPE_PLANETARYPRODUCTION,
 contentGroupStorylineAgents: agencyConst.CONTENTTYPE_STORYLINEAGENTS,
 contentGroupProjectDiscovery: agencyConst.CONTENTTYPE_PROJECTDISCOVERY,
 contentGroupOreAnomalies: agencyConst.CONTENTTYPE_OREANOMALY,
 contentGroupSeasons: agencyConst.CONTENTTYPE_SEASONS,
 contentGroupTriglavianFilaments: agencyConst.CONTENTTYPE_AGENCY,
 contentGroupESSSystems: agencyConst.CONTENTTYPE_ESS,
 contentGroupFleetUp: agencyConst.CONTENTTYPE_FLEETUP,
 contentGroupFleetUpRegister: agencyConst.CONTENTTYPE_FLEETUP_REGISTRATION,
 contentGroupHelp: agencyConst.CONTENTTYPE_HELP,
 contentGroupMissionAgentsHeraldry: agencyConst.CONTENTTYPE_HERALDRYAGENTS,
 contentGroupHomefrontSites: agencyConst.CONTENTTYPE_HOMEFRONT_SITES,
 contentGroupPirateIncursions: agencyConst.CONTENTTYPE_PIRATEINSURGENCESYSTEM,
 contentGroupColonyResourcesAgency: agencyConst.CONTENTTYPE_COLONYRESOURCESAGENCY}
chatChannelIDsByContentGroups = {contentGroupIncursions: chatConst.CHANNEL_INCURSIONS,
 contentGroupAsteroidBelts: chatConst.CHANNEL_MINING,
 contentGroupSignatures: chatConst.CHANNEL_SCANNING,
 contentGroupMissionAgents: chatConst.CHANNEL_MISSIONS,
 contentGroupEvents: chatConst.CHANNEL_EVENTS}
contentGroupsEnabledInWormholes = {contentGroupEscalations,
 contentGroupAbyssalDeadspace,
 contentGroupAbyssalFilaments,
 contentGroupCombatAnomalies,
 contentGroupSignatures,
 contentGroupProjectDiscovery,
 contentGroupOreAnomalies,
 contentGroupPlanetaryProduction,
 contentGroupEncounters,
 contentGroupExploration,
 contentGroupResourceHarvesting,
 contentGroupIceBelts,
 contentGroupTriglavianSpace,
 contentGroupTriglavianFilaments,
 contentGroupHelp,
 contentGroupCorp,
 contentGroupFleetUp,
 contentGroupFleetUpRegister,
 contentGroupFleetFinder,
 contentGroupSeasons,
 contentGroupMissionAgentsHeraldry,
 contentGroupMissions,
 contentGroupPirateIncursions,
 contentGroupPlanetHarvesting}
