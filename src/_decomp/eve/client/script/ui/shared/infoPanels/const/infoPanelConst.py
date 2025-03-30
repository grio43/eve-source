#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\const\infoPanelConst.py
from eve.client.script.ui.view.viewStateConst import ViewState
PANEL_LOCATION_INFO = 1
PANEL_ROUTE = 2
PANEL_MISSIONS = 3
PANEL_INCURSIONS = 4
PANEL_FACTIONAL_WARFARE = 5
PANEL_PLANETARY_INTERACTION = 6
PANEL_SHIP_TREE = 7
PANEL_SEASONS = 10
PANEL_OPERATIONS = 11
PANEL_RESOURCE_WARS = 12
PANEL_SEARCH = 14
PANEL_DUNGEON_PROGRESSION = 16
PANEL_ESS = 20
PANEL_RECOMMENDATIONS = 21
PANEL_AIR_NPE = 22
PANEL_CAREER_PROGRAM = 23
PANEL_JOB_BOARD = 24
PANEL_INSURGENCY = 25
PANEL_WAREHOUSE_RAID = 26
PANEL_SKYHOOK_THEFT = 27
PANEL_WORLD_EVENTS = 28
PANEL_ABYSS = 29
PANELTYPES = (PANEL_SEARCH,
 PANEL_LOCATION_INFO,
 PANEL_ROUTE,
 PANEL_MISSIONS,
 PANEL_INCURSIONS,
 PANEL_FACTIONAL_WARFARE,
 PANEL_ESS,
 PANEL_PLANETARY_INTERACTION,
 PANEL_SHIP_TREE,
 PANEL_SEASONS,
 PANEL_OPERATIONS,
 PANEL_RECOMMENDATIONS,
 PANEL_RESOURCE_WARS,
 PANEL_DUNGEON_PROGRESSION,
 PANEL_AIR_NPE,
 PANEL_CAREER_PROGRAM,
 PANEL_JOB_BOARD,
 PANEL_INSURGENCY,
 PANEL_SKYHOOK_THEFT,
 PANEL_WORLD_EVENTS)
MODE_NORMAL = 1
MODE_COMPACT = 2
MODE_HIDDEN = 3
SETTINGS_ID_SHIP_TREE_DOCKPANEL = 'ShipTree_dockablePanel'
PANELS_BY_SETTINGSID = {ViewState.Hangar: [PANEL_SEARCH,
                    PANEL_LOCATION_INFO,
                    PANEL_ROUTE,
                    PANEL_INCURSIONS,
                    PANEL_MISSIONS,
                    PANEL_FACTIONAL_WARFARE,
                    PANEL_SEASONS,
                    PANEL_OPERATIONS,
                    PANEL_RECOMMENDATIONS,
                    PANEL_AIR_NPE,
                    PANEL_CAREER_PROGRAM,
                    PANEL_JOB_BOARD,
                    PANEL_INSURGENCY,
                    PANEL_WORLD_EVENTS],
 ViewState.Planet: [PANEL_SEARCH,
                    PANEL_LOCATION_INFO,
                    PANEL_ROUTE,
                    PANEL_PLANETARY_INTERACTION],
 ViewState.ShipTree: [PANEL_SEARCH,
                      PANEL_LOCATION_INFO,
                      PANEL_ROUTE,
                      PANEL_SHIP_TREE],
 ViewState.Space: [PANEL_SEARCH,
                   PANEL_LOCATION_INFO,
                   PANEL_ROUTE,
                   PANEL_INCURSIONS,
                   PANEL_MISSIONS,
                   PANEL_FACTIONAL_WARFARE,
                   PANEL_SEASONS,
                   PANEL_OPERATIONS,
                   PANEL_RECOMMENDATIONS,
                   PANEL_RESOURCE_WARS,
                   PANEL_DUNGEON_PROGRESSION,
                   PANEL_ESS,
                   PANEL_AIR_NPE,
                   PANEL_CAREER_PROGRAM,
                   PANEL_JOB_BOARD,
                   PANEL_INSURGENCY,
                   PANEL_SKYHOOK_THEFT,
                   PANEL_WORLD_EVENTS,
                   PANEL_ABYSS],
 ViewState.StarMap: [PANEL_SEARCH, PANEL_LOCATION_INFO, PANEL_ROUTE],
 ViewState.StarMapNew: [PANEL_SEARCH, PANEL_LOCATION_INFO, PANEL_ROUTE],
 ViewState.Structure: [PANEL_SEARCH,
                       PANEL_LOCATION_INFO,
                       PANEL_ROUTE,
                       PANEL_INCURSIONS,
                       PANEL_MISSIONS,
                       PANEL_FACTIONAL_WARFARE,
                       PANEL_SEASONS,
                       PANEL_OPERATIONS,
                       PANEL_RECOMMENDATIONS,
                       PANEL_AIR_NPE,
                       PANEL_CAREER_PROGRAM,
                       PANEL_JOB_BOARD,
                       PANEL_INSURGENCY,
                       PANEL_WORLD_EVENTS],
 ViewState.SystemMap: [PANEL_SEARCH, PANEL_LOCATION_INFO, PANEL_ROUTE],
 ViewState.SystemMapNew: [PANEL_SEARCH, PANEL_LOCATION_INFO, PANEL_ROUTE],
 ViewState.SkillPlan: [PANEL_SEARCH],
 SETTINGS_ID_SHIP_TREE_DOCKPANEL: [PANEL_SHIP_TREE]}
PANEL_DEFAULT_MODE_BY_SETTINGSID = {ViewState.ShipTree: {PANEL_LOCATION_INFO: MODE_COMPACT,
                      PANEL_ROUTE: MODE_HIDDEN},
 ViewState.Planet: {PANEL_LOCATION_INFO: MODE_COMPACT,
                    PANEL_ROUTE: MODE_HIDDEN},
 ViewState.SystemMapNew: {PANEL_LOCATION_INFO: MODE_COMPACT,
                          PANEL_ROUTE: MODE_HIDDEN},
 ViewState.SkillPlan: {PANEL_SEARCH: MODE_HIDDEN,
                       PANEL_LOCATION_INFO: MODE_HIDDEN,
                       PANEL_ROUTE: MODE_HIDDEN},
 ViewState.PaintTool: {PANEL_SEARCH: MODE_HIDDEN,
                       PANEL_LOCATION_INFO: MODE_HIDDEN,
                       PANEL_ROUTE: MODE_HIDDEN},
 ViewState.ShipSKINR: {PANEL_SEARCH: MODE_HIDDEN,
                       PANEL_LOCATION_INFO: MODE_HIDDEN,
                       PANEL_ROUTE: MODE_HIDDEN}}
