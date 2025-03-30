#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\planetConst.py
import evetypes
from carbonui.services.setting import UserSettingBool
from eve.common.lib import appConst
from eve.common.script.util.planetCommon import GetGenericPinName, ItemIDToPinDesignator
from fsdBuiltData.common.planet import *
from fsdBuiltData.common.planet import _get_schematics
SCALE_OTHERLINKS = 1.0049
SCALE_RUBBERLINK = 1.0089
SCALE_EXTRACTORLINKS = 1.001
SCALE_LINKS = 1.008
STATE_NORMAL = 0
STATE_BUILDPIN = 1
STATE_CREATELINKSTART = 2
STATE_CREATELINKEND = 3
STATE_CREATEROUTE = 4
STATE_SURVEY = 5
STATE_DECOMMISSION = 6
SUBSTATE_NORMAL = 0
SUBSTATE_MOVEEXTRACTIONHEAD = 1
TYPEIDS_PROCESSORS_BASIC = (2469, 2471, 2473, 2481, 2483, 2490, 2492, 2493)
TYPEIDS_PROCESSORS_ADVANCED = (2470, 2472, 2474, 2480, 2484, 2485, 2491, 2494)
TYPEIDS_PROCESSORS_HIGHTECH = (2475, 2482)
TYPEIDS_COMMAND_CENTER = (2254, 2524, 2525, 2533, 2534, 2549, 2550, 2551)
TYPEIDS_PROCESSORS = TYPEIDS_PROCESSORS_BASIC + TYPEIDS_PROCESSORS_ADVANCED + TYPEIDS_PROCESSORS_HIGHTECH
LINK_COLOR_BASE = (0.0, 0.0, 0.0, 1.0)
LINK_COLOR_DEFAULT = (0.0, 1.0, 1.0, 1.0)
LINK_COLOR_ROUTED = (1.0, 0.5, 0.0, 1.0)
LINK_COLOR_HOVER = (1.0, 1.0, 1.0, 1.0)
LINK_COLOR_SELECTED = (1.0, 1.0, 0.0, 1.0)
LINK_COLOR_INACTIVE = (0.0, 0.0, 0.0, 0.3)
PLANETTYPE_NAMES = {appConst.typePlanetSandstorm: 'UI/PI/PlanetType/Barren',
 appConst.typePlanetThunderstorm: 'UI/PI/PlanetType/Storm',
 appConst.typePlanetEarthlike: 'UI/PI/PlanetType/Temperate',
 appConst.typePlanetIce: 'UI/PI/PlanetType/Ice',
 appConst.typePlanetGas: 'UI/PI/PlanetType/Gas',
 appConst.typePlanetPlasma: 'UI/PI/PlanetType/Plasma',
 appConst.typePlanetOcean: 'UI/PI/PlanetType/Oceanic',
 appConst.typePlanetLava: 'UI/PI/PlanetType/Lava',
 appConst.typePlanetShattered: 'UI/PI/PlanetType/Shattered',
 appConst.typePlanetScorched: 'UI/PI/PlanetType/Scorched'}
PLANET_TYPES = (appConst.typePlanetEarthlike,
 appConst.typePlanetPlasma,
 appConst.typePlanetGas,
 appConst.typePlanetIce,
 appConst.typePlanetOcean,
 appConst.typePlanetLava,
 appConst.typePlanetSandstorm,
 appConst.typePlanetThunderstorm,
 appConst.typePlanetShattered,
 appConst.typePlanetScorched)
PIN_HIGH = 'HIGH'
PIN_BASIC = 'BASIC'
PIN_ADV = 'ADV'
PLANET_TYPE_TO_PIN = {2016: {PIN_ADV: 2474,
        1027: 2524,
        1029: 2541,
        1030: 2544,
        1063: 2848,
        PIN_HIGH: 2475,
        PIN_BASIC: 2473},
 2017: {PIN_ADV: 2484,
        1027: 2550,
        1029: 2561,
        1030: 2557,
        1063: 3067,
        PIN_BASIC: 2483},
 2063: {PIN_ADV: 2472,
        1027: 2551,
        1029: 2560,
        1030: 2556,
        1063: 3064,
        PIN_BASIC: 2471},
 11: {PIN_ADV: 2480,
      1027: 2254,
      1029: 2562,
      1030: 2256,
      1063: 3068,
      PIN_HIGH: 2482,
      PIN_BASIC: 2481},
 12: {PIN_ADV: 2491,
      1027: 2533,
      1029: 2257,
      1030: 2552,
      1063: 3061,
      PIN_BASIC: 2493},
 13: {PIN_ADV: 2494,
      1027: 2534,
      1029: 2536,
      1030: 2543,
      1063: 3060,
      PIN_BASIC: 2492},
 2014: {PIN_ADV: 2485,
        1027: 2525,
        1029: 2535,
        1030: 2542,
        1063: 3063,
        PIN_BASIC: 2490},
 2015: {PIN_ADV: 2470,
        1027: 2549,
        1029: 2558,
        1030: 2555,
        1063: 3062,
        PIN_BASIC: 2469}}
SettingsHideInappropriateRadius = UserSettingBool(settings_key='HideInappropriateRadiusTemplates', default_value=False)
SettingShowOnlyFav = UserSettingBool(settings_key='ShowOnlyFavTemplates', default_value=False)
All_Schematics = _get_schematics()
SCHEMATIC_DEMAND = {}
SCHEMATIC_PRODUCT = {}
OUTPUT_TO_SCHEMATICID = {}
for schematicID in All_Schematics.keys():
    schematic = get_schematic(schematicID)
    for typeID, commodity in schematic.types.iteritems():
        if commodity.isInput:
            SCHEMATIC_DEMAND[typeID] = commodity.quantity
        else:
            SCHEMATIC_PRODUCT[typeID] = commodity.quantity
            OUTPUT_TO_SCHEMATICID[typeID] = schematicID

shortPinTypeNamePaths = {}
shortPinTypeNamePaths.update({x:'UI/PI/BasicFacility' for x in TYPEIDS_PROCESSORS_BASIC})
shortPinTypeNamePaths.update({x:'UI/PI/AdvancedFacility' for x in TYPEIDS_PROCESSORS_ADVANCED})
shortPinTypeNamePaths.update({x:'UI/PI/HighTechFacility' for x in TYPEIDS_PROCESSORS_HIGHTECH})
shortPinTypeNamePaths.update({x:'UI/PI/StorageFacility' for x in evetypes.GetTypeIDsByGroup(appConst.groupStoragePins)})
shortPinTypeNamePaths.update({x:'UI/PI/Launchpad' for x in evetypes.GetTypeIDsByGroup(appConst.groupSpaceportPins)})
shortPinTypeNamePaths.update({x:'UI/PI/ExtractorControlUnit' for x in evetypes.GetTypeIDsByGroup(appConst.groupExtractionControlUnitPins)})

def GetPinNameShort(typeID, itemID):
    if isinstance(itemID, tuple):
        return GetGenericPinName(typeID, itemID)
    else:
        from localization import GetByLabel
        labelPath = shortPinTypeNamePaths.get(typeID, None)
        typeName = GetByLabel(labelPath) if labelPath else evetypes.GetName(typeID)
        return localization.GetByLabel('UI/PI/Common/PinNameAndID', pinName=typeName, pinID=ItemIDToPinDesignator(itemID))
