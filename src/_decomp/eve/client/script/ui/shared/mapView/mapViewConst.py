#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\mapViewConst.py
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_FACTIONEMPIRE
UNIVERSE_SCALE = 1.5e-13
SOLARSYSTEM_SCALE = 1e-10
STAR_SIZE_UNIMPORTANT = 8.0
STAR_SIZE_STANDARD = 30.0
STAR_SIZE_AFFECTED = 60.0
SCALING_SOLARSYSTEMINWORLDMAP = 0.05
MAX_MARKER_DISTANCE = 220000.0
OPACITY_MARKER_ACTIVE = 1.0
OPACITY_MARKER_SELECTED = 1.3
MIN_CAMERA_DISTANCE = 1.0
MAX_CAMERA_DISTANCE = 160000.0
MIN_CAMERA_DISTANCE_SOLARSYSTEMVIEW = 0.5
MAX_CAMERA_DISTANCE_SOLARSYSTEMVIEW = 9000.0
JUMPLINE_BASE_WIDTH = 2.5
AUTOPILOT_LINE_TICKSIZE = const.AU * 10000 * UNIVERSE_SCALE
AUTOPILOT_LINE_ANIM_SPEED = 1.0
AUTOPILOT_LINE_WIDTH = JUMPLINE_BASE_WIDTH * 2
CONSTELLATION_LINE_TICKSIZE = const.AU * 4000 * UNIVERSE_SCALE
REGION_LINE_TICKSIZE = const.AU * 20000 * UNIVERSE_SCALE
AUDIO_SOLARSYSTEM_DISTANCE = 10.0
AUDIO_CONSTELLATION_DISTANCE = 50.0
SETTING_PREFIX = 'mapview2'
VIEWMODE_LAYOUT_SETTINGS = SETTING_PREFIX + '_majorlayout'
VIEWMODE_LAYOUT_SOLARSYSTEM = 0
VIEWMODE_LAYOUT_CONSTELLATIONS = 1
VIEWMODE_LAYOUT_REGIONS = 2
VIEWMODE_LAYOUT_DEFAULT = VIEWMODE_LAYOUT_SOLARSYSTEM
VIEWMODE_LINES_SETTINGS = SETTING_PREFIX + '_lines'
VIEWMODE_LINES_NONE = 3
VIEWMODE_LINES_ALL = 4
VIEWMODE_LINES_SELECTION = 5
VIEWMODE_LINES_SELECTION_REGION = 6
VIEWMODE_LINES_SELECTION_REGION_NEIGHBOURS = 7
VIEWMODE_LINES_DEFAULT = VIEWMODE_LINES_ALL
VIEWMODE_LINES_SHOW_ALLIANCE_SETTINGS = SETTING_PREFIX + '_show_alliance_lines'
VIEWMODE_LINES_SHOW_ALLIANCE_DEFAULT = True
VIEWMODE_LINES_SHOW_JUMP_BRIDGES_MY = 0
VIEWMODE_LINES_SHOW_JUMP_BRIDGES_ALL = 1
VIEWMODE_LINES_SHOW_JUMP_BRIDGES_SETTINGS = SETTING_PREFIX + '_showJumpBridges'
VIEWMODE_LINES_SHOW_JUMP_BRIDGES_DEFAULT = VIEWMODE_LINES_SHOW_JUMP_BRIDGES_MY
VIEWMODE_LAYOUT_SHOW_ABSTRACT_SETTINGS = SETTING_PREFIX + '_layout'
VIEWMODE_LAYOUT_SHOW_ABSTRACT_DEFAULT = True
VIEWMODE_COLOR_SETTINGS = SETTING_PREFIX + '_colormode'
VIEWMODE_COLOR_DEFAULT = STARMODE_FACTIONEMPIRE
VIEWMODE_COLOR_RECENT = SETTING_PREFIX + '_recent_colormode'
VIEWMODE_COLOR_RECENT_DEFAULT = [VIEWMODE_COLOR_DEFAULT]
VIEWMODE_COLOR_RECENT_MAX = 5
VIEWMODE_MARKERS_SETTINGS = SETTING_PREFIX + '_systemmap_markers'
MARKERS_OPTION_PERSONAL_LOCATION = 'personal_location'
MARKERS_OPTION_SHARED_LOCATION = 'shared_location'
MARKERS_OPTION_SOV_HUBS = 'sov_hubs'
MARKERS_OPTION_VULNERABLE_SKYHOOK = 'vulnerable_skyhook'
VIEWMODE_MARKERS_OPTIONS_CUSTOM = [MARKERS_OPTION_PERSONAL_LOCATION, MARKERS_OPTION_SHARED_LOCATION, MARKERS_OPTION_VULNERABLE_SKYHOOK]
VIEWMODE_MARKERS_OPTIONS_CUSTOM_DEFAULT = VIEWMODE_MARKERS_OPTIONS_CUSTOM[:]
VIEWMODE_MARKERS_CUSTOM_LABELS = {MARKERS_OPTION_PERSONAL_LOCATION: 'UI/PeopleAndPlaces/PersonalLocations',
 MARKERS_OPTION_SHARED_LOCATION: 'UI/PeopleAndPlaces/SharedLocations',
 MARKERS_OPTION_SOV_HUBS: 'UI/Sovereignty/HubPage/SovereigntyHubs',
 MARKERS_OPTION_VULNERABLE_SKYHOOK: 'UI/OrbitalSkyhook/SkyhookMap/VulnerableSkyhooks'}
VIEWMODE_MARKERS_OPTIONS = [const.groupScannerProbe,
 const.groupPlanet,
 const.groupMoon,
 const.groupStation,
 const.groupAsteroidBelt,
 const.groupBeacon,
 const.groupCynosuralBeacon,
 const.groupStargate,
 const.groupSovereigntyClaimMarkers,
 const.groupSun,
 const.groupStructureCitadel,
 const.groupStructureIndustrialArray,
 const.groupStructureDrillingPlatform]
VIEWMODE_MARKERS_OPTIONS_DEFAULT = [const.groupPlanet,
 const.groupMoon,
 const.groupStation,
 const.groupAsteroidBelt,
 const.groupBeacon,
 const.groupCynosuralBeacon,
 const.groupStargate,
 const.groupSovereigntyClaimMarkers,
 const.groupSun,
 const.groupStructureCitadel,
 const.groupStructureIndustrialArray,
 const.groupStructureDrillingPlatform]
VIEWMODE_MARKERS_DEFAULT = VIEWMODE_MARKERS_OPTIONS_DEFAULT + VIEWMODE_MARKERS_OPTIONS_CUSTOM_DEFAULT
VIEWMODE_MARKERS_OVERLAP_SORT_ORDER = [const.groupStargate,
 const.groupAsteroidBelt,
 const.groupStation,
 const.groupScannerProbe,
 const.groupPlanet,
 const.groupMoon,
 const.groupBeacon,
 const.groupCynosuralBeacon,
 const.groupSovereigntyClaimMarkers,
 const.groupSun]
DEFAULT_MAPVIEW_SETTINGS = {VIEWMODE_LAYOUT_SETTINGS: VIEWMODE_LAYOUT_DEFAULT,
 VIEWMODE_COLOR_SETTINGS: VIEWMODE_COLOR_DEFAULT,
 VIEWMODE_COLOR_RECENT: VIEWMODE_COLOR_RECENT_DEFAULT,
 VIEWMODE_LAYOUT_SHOW_ABSTRACT_SETTINGS: VIEWMODE_LAYOUT_SHOW_ABSTRACT_DEFAULT,
 VIEWMODE_LINES_SETTINGS: VIEWMODE_LINES_DEFAULT,
 VIEWMODE_LINES_SHOW_ALLIANCE_SETTINGS: VIEWMODE_LINES_SHOW_ALLIANCE_DEFAULT,
 VIEWMODE_MARKERS_SETTINGS: VIEWMODE_MARKERS_DEFAULT,
 VIEWMODE_LINES_SHOW_JUMP_BRIDGES_SETTINGS: VIEWMODE_LINES_SHOW_JUMP_BRIDGES_DEFAULT}
VIEWMODE_FOCUS_SELF = 'focus_self'
MARKERID_MYPOS = 1
MARKERID_MYHOME = 2
MARKERID_BOOKMARK = 3
MARKERID_ROUTE = 4
MARKERID_SCANRESULT = 5
MARKERID_SOLARSYSTEM_CELESTIAL = 6
MARKERID_PROBE = 7
MARKERID_CSBLOB = 8
MARKERID_SOVHUBS = 9
MARKERID_EMANATION_LOCK_GATE = 10
MARKERID_VULNERABLE_SKYHOOK = 11
MARKERID_VULNERABLE_SKYHOOK_SOLARSYSTEM = 12
MARKERID_SCANRESULT_OVERLAP_SORT_ORDER = 0
MARKERID_MYPOS_OVERLAP_SORT_ORDER = 1
MARKERID_MYHOME_OVERLAP_SORT_ORDER = 2
MARKER_TYPES = (MARKERID_MYPOS,
 MARKERID_BOOKMARK,
 MARKERID_ROUTE,
 MARKERID_SOLARSYSTEM_CELESTIAL,
 MARKERID_MYHOME,
 MARKERID_PROBE,
 MARKERID_SCANRESULT,
 MARKERID_CSBLOB)
MARKER_POINT_LEFT = 0
MARKER_POINT_TOP = 1
MARKER_POINT_RIGHT = 2
MARKER_POINT_BOTTOM = 3
JUMPBRIDGE_COLOR = (0.0, 1.0, 0.0, 1.0)
JUMPBRIDGE_COLOR_NO_ACCESS = (1.0, 0.0, 0.0, 1.0)
JUMPBRIDGE_CURVE_SCALE = 0.5
JUMPBRIDGE_TYPE = 4
WORKFORCE_TRANSPORT_CONFIG_TYPE = 5
WORKFORCE_TRANSPORT_STATE_TYPE = 6
MAPVIEW_CAMERA_SETTINGS = SETTING_PREFIX + '_camera'
MAPVIEW_PRIMARY_ID = 'primary'
MAPVIEW_PRIMARY_OVERLAY_ID = 'primary_overlay'
MAPVIEW_SOLARSYSTEM_ID = 'solarsystem'
MODIFY_POSITION = 1
MODIFY_RANGE = 2
MODIFY_SPREAD = 3
MARKER_INACTIVE = 0
MARKER_ACTIVE = 1
MARKER_SELECTED = 2
TRIGLAVIAN_SUN_FLARE_COLOR = (1.0, 0.25098039215686274, 0.1607843137254902, 1.0)
