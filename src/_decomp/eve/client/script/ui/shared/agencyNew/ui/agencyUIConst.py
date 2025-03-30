#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\agencyUIConst.py
from carbonui import TextColor
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
COLOR_AVAILABLE = Color.HextoRGBA('#134d66')
COLOR_AVAILABLE_HILIGHT = eveColor.SUCCESS_GREEN
COLOR_UNAVAILABLE = Color.HextoRGBA('#991f24')
COLOR_UNAVAILABLE_HILIGHT = eveColor.DANGER_RED
CONTENTCARD_HEIGHT = 86
CONTENTCARD_WIDTH = 300
LAYOUT_CONTAINER_WIDTH = 660
LAYOUT_CONTAINER_HEIGHT = 470
CONTENT_PAGE_WIDTH = 871
CONTENT_PAGE_HEIGHT = 465
CONTENT_PAGE_WIDTH_HALF = 436
OPACITY_DESCRIPTION_LABEL = 0.8
OPACITY_DESCRIPTION_LABEL_HOVER = 1.0
COLOR_BY_CONTENTTYPE = {agencyConst.CONTENTTYPE_MINING: (1.0, 1.0, 1.0, 1.0),
 agencyConst.CONTENTTYPE_COMBAT: (1.0, 1.0, 1.0, 1.0),
 agencyConst.CONTENTTYPE_SUGGESTED: (1.0, 1.0, 1.0, 1.0),
 agencyConst.CONTENTTYPE_AGENTS: (0.2, 0.8, 1.0, 1.0),
 agencyConst.CONTENTTYPE_CAREERAGENTS: (0.2, 0.8, 1.0, 1.0),
 agencyConst.CONTENTTYPE_HERALDRYAGENTS: (0.2, 0.8, 1.0, 1.0),
 agencyConst.CONTENTTYPE_SITES: (0.2, 0.8, 0.6, 1.0),
 agencyConst.CONTENTTYPE_SIGNATURES: (0.0, 1.0, 0.4, 1.0),
 agencyConst.CONTENTTYPE_INCURSIONS: (0.82, 0.247, 0.6, 1.0),
 agencyConst.CONTENTTYPE_AGENCY: (0.38, 0.46, 0.92, 1.0),
 agencyConst.CONTENTTYPE_EPICARCS: (0.4, 1.0, 1.0, 1.0),
 agencyConst.CONTENTTYPE_ASTEROIDBELTS: (0.2, 0.8, 0.2, 1.0),
 agencyConst.CONTENTTYPE_ICEBELTS: (0.05, 0.78, 0.95, 1.0),
 agencyConst.CONTENTTYPE_ESCALATION: (1.0, 0.8, 0.2, 1.0),
 agencyConst.CONTENTTYPE_INCURSIONSITE: (0.2, 0.8, 0.6, 1.0),
 agencyConst.CONTENTTYPE_PIRATE_STRONGHOLD: (0.7, 0.1, 0.1, 1.0),
 agencyConst.CONTENTTYPE_FACTIONALWARFARE: (0.325, 0.557, 0.651, 1.0)}
BG_COLOR_BY_CONTENTTYPE = {}
for contentType, col in COLOR_BY_CONTENTTYPE.iteritems():
    BG_COLOR_BY_CONTENTTYPE[contentType] = Color(*col).SetAlpha(0.075).GetRGBA()

OPACITY_SLANTS = 0.1
COLOR_BG = (0, 0, 0, 0.25)
COLOR_BG_DARK = (0, 0, 0, 0.45)
CONTENT_GROUP_CARD_DISABLED_COLOR = eveColor.WARNING_ORANGE
CONTENT_GROUP_CARD_DISABLED_LABEL_COLOR = TextColor.WARNING
CONTENT_GROUP_CARD_TITLE_DISABLED_COLOR = TextColor.DISABLED
ACTION_UNDOCK = 1
ACTION_DOCK = 2
ACTION_WARPTO = 3
ACTION_SETDESTINATION = 4
ACTION_STARTCONVERSATION = 5
ACTION_OPENPROBESCANNER = 6
ACTION_NONE = 7
ACTION_DESTINATIONSET = 8
NUM_ROWS = 16
NUM_COLUMNS = 2
PAD_CARDS = 16
FILTER_CONTAINER_WIDTH = 300
ACTIVITY_BADGES_BY_CONTENT_GROUP = {contentGroupConst.contentGroupMissionAgentsDistribution: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsDistribution.png',
 contentGroupConst.contentGroupMissionAgentsLocator: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsLocator.png',
 contentGroupConst.contentGroupMissionAgentsMining: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsMining.png',
 contentGroupConst.contentGroupMissionAgentsResearch: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsResearch.png',
 contentGroupConst.contentGroupMissionAgentsSecurity: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsSecurity.png',
 contentGroupConst.contentGroupCombatAnomalies: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_anomalies.png',
 contentGroupConst.contentGroupAsteroidBelts: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_asteroidBelts.png',
 contentGroupConst.contentGroupCareerAgents: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_careerAgents.png',
 contentGroupConst.contentGroupEpicArcs: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_epicArcs.png',
 contentGroupConst.contentGroupEscalations: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_escalations.png',
 contentGroupConst.contentGroupFactionalWarfare: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_factionWarfare.png',
 contentGroupConst.contentGroupIceBelts: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_iceBelts.png',
 contentGroupConst.contentGroupIncursions: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_incursions.png',
 contentGroupConst.contentGroupOreAnomalies: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_oreSites.png',
 contentGroupConst.contentGroupPirateStrongholds: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_pirateStrongholds.png',
 contentGroupConst.contentGroupPlanetaryProduction: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_planetaryProduction.png',
 contentGroupConst.contentGroupSignatures: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_signatures.png',
 contentGroupConst.contentGroupStorylineAgents: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_storylineMissions.png',
 contentGroupConst.contentGroupMissionAgentsHeraldry: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsHeraldry.png',
 contentGroupConst.contentGroupHomefrontSites: 'res:/UI/Texture/classes/agency/ActivityBadges/badge_anomalies.png'}
ICONSIZE_CONTENTCARD = 76
ICON_SIZE_RESOURCE = 20
SUN_BG_BY_TYPEID = {6: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_yellow_01a.png',
 7: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_orange_01a.png',
 8: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_red_01a.png',
 9: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_blue_01a.png',
 10: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_white_01a.png',
 34331: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_purple_sun_01a.png',
 78350: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_purple_sun_01a.png',
 3796: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_blue_sun_01a.png',
 3797: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_pink_hazy_01a.png',
 3798: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_orange_sun_01a.png',
 3799: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_pink_sun_small_01a.png',
 3800: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_orange_radiating_01a.png',
 3801: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_blue_small_01a.png',
 3802: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_yellow_small_01a.png',
 3803: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_white_tiny_01a.png',
 45030: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_yellow_01b.png',
 45031: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_orange_01b.png',
 45032: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_orange_01c.png',
 45033: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_red_01b.png',
 45034: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_blue_01b.png',
 45035: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_white_01b.png',
 45036: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_pink_hazy_01b.png',
 45037: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_orange_sun_01b.png',
 45038: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_pink_sun_small_01b.png',
 45039: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_orange_radiating_01b.png',
 45040: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_orange_radiating_01c.png',
 45041: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_yellow_small_01b.png',
 45042: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_white_tiny_01b.png',
 45046: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_blue_01c.png',
 45047: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_yellow_01c.png',
 73909: 'res:/UI/Texture/classes/agency/SunBackgrounds/sun_blue_small_01a.png'}
