#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\hangarRegistry.py
import evetypes
import const
import inventorycommon.const as invC
from hangarBehaviours import capitalHangarBehaviours, defaultHangarBehaviours, modularHangarBehaviours, modularHangarCapitalBehaviours
from hangarBehaviours.modularHangarBehavioursConstants import GetShipSizeClass
from eve.common.script.sys.idCheckers import IsHighSecSystem
HANGAR_TYPE_OVERRIDE = None
HANGAR_VFX_TRIGGERS_MULTIEFFECT = 'res:\\dx9\\model\\hangar\\shared\\FX\\ME_generic_hangar_vfx_01a.red'
ALL_DEFAULT_BEHAVIOURS = {'ship': defaultHangarBehaviours.DefaultHangarShipBehaviour,
 'drone': defaultHangarBehaviours.DefaultHangarDroneBehaviour}
ALL_CAPITAL_BEHAVIOURS = {'ship': capitalHangarBehaviours.CapitalHangarShipBehaviour,
 'drone': capitalHangarBehaviours.CapitalHangarDroneBehaviour}
ALL_MODULAR_BEHAVIOURS = {'ship': modularHangarBehaviours.ModularHangarShipBehaviour,
 'drone': modularHangarBehaviours.ModularHangarDroneBehaviour}
ALL_MODULAR_CAPITAL_BEHAVIOURS = {'ship': modularHangarCapitalBehaviours.ModularCapitalHangarShipBehaviour,
 'drone': modularHangarCapitalBehaviours.ModularCapitalHangarDroneBehaviour}
OLD_HANGAR_CAMERA_SETTINGS = [[1,
  5.5,
  3.534,
  1.375,
  1.634,
  1.2,
  2.0,
  0.7]]
DEFAULT_HANGAR_DICTIONARY = {'name': 'unassigned',
 'isModular': False,
 'isCapital': False,
 'isEnlistmentDockingEnabled': False,
 'dockCameraSettings': OLD_HANGAR_CAMERA_SETTINGS,
 'activityLevelThresholds': {'MID_THRESHOLD': 40,
                             'HIGH_THRESHOLD': 100},
 'sceneGraphicID': 0,
 'hangarModelGraphicID': 0,
 'factionOverrideMap': None,
 'hangarType': 0}
AMARR_NORMAL_HANGAR_SIZE = dict(DEFAULT_HANGAR_DICTIONARY, name='AMARR', sceneGraphicID=20273, hangarModelGraphicID=24407, hangarType=1)
CALDARI_NORMAL_HANGAR_SIZE = dict(DEFAULT_HANGAR_DICTIONARY, name='CALDARI', sceneGraphicID=20271, hangarModelGraphicID=24408, hangarType=2)
GALLENTE_NORMAL_HANGAR_SIZE = dict(DEFAULT_HANGAR_DICTIONARY, name='GALLENTE', sceneGraphicID=20274, hangarModelGraphicID=24409, hangarType=3)
MINMATAR_NORMAL_HANGAR_SIZE = dict(DEFAULT_HANGAR_DICTIONARY, name='MINMTAR', sceneGraphicID=20272, hangarModelGraphicID=24410, factionOverrideMap={invC.typeDamagedMinmatarStation: 'minmatarbase_damaged'}, hangarType=4)
CITADEL_NORMAL_HANGAR_SIZE = dict(DEFAULT_HANGAR_DICTIONARY, name='CITADEL_NORMAL', sceneGraphicID=21259, hangarModelGraphicID=24411)
CITADEL_CAPITAL_HANGAR_SIZE = dict(DEFAULT_HANGAR_DICTIONARY, name='CITADEL_LARGE', isCapital=True, sceneGraphicID=25577, hangarModelGraphicID=24412)
JITA_4_4_NORMAL_HANGAR_SIZE = dict(DEFAULT_HANGAR_DICTIONARY, name='JITA_4_4', dockCameraSettings=[[4,
  -0.1,
  -1.23,
  1.466,
  1.55,
  1.2,
  4.0,
  0.7],
 [4,
  0.05,
  -2.5,
  1.496,
  1.57,
  1.2,
  3.0,
  0.7],
 [4,
  -6.2,
  -3.6,
  1.5,
  1.24,
  1.2,
  2.0,
  0.7],
 [4,
  0.05,
  1.17,
  1.55,
  1.4,
  1.2,
  2.0,
  0.7],
 [4,
  1.0,
  0.16,
  1.52,
  1.6,
  1.2,
  3.0,
  0.8],
 [3,
  2.55,
  3.542,
  1.5,
  1.0,
  1.2,
  3.0,
  0.7],
 [3,
  4.0,
  3.142,
  1.4,
  0.1,
  3.0,
  15.0,
  0.6],
 [1,
  1.0,
  0.0,
  1.2,
  1.633,
  3.0,
  15.0,
  0.7]], activityLevelThresholds={'MID_THRESHOLD': 1000,
 'HIGH_THRESHOLD': 1500}, sceneGraphicID=24526, hangarModelGraphicID=24525)
AIR_NORMAL_HANGAR_SIZE = dict(DEFAULT_HANGAR_DICTIONARY, name='AIR', dockCameraSettings=[[1,
  2.6,
  1.5708,
  1.0,
  0.0,
  3.5,
  0.5,
  0.8], [9,
  -3.2,
  -0.34,
  1.0,
  1.3,
  1.5,
  100.0,
  0.9]], activityLevelThresholds={'MID_THRESHOLD': 25,
 'HIGH_THRESHOLD': 50}, sceneGraphicID=25045, hangarModelGraphicID=25044, hangarType=7)
UPWELL_MODULAR_HANGAR = dict(DEFAULT_HANGAR_DICTIONARY, isModular=True, name='UPWELL_MODULAR', sceneGraphicID=25263, hangarModelGraphicID=25235, dockingEffectGraphicID=25244, factionOverrideMap={invC.typeRefineryAthanor: 'upwell_interior-refinery',
 invC.typeRefineryTatara: 'upwell_interior-refinery',
 invC.typeEngineeringComplexRaitaru: 'upwell_interior-indy',
 invC.typeEngineeringComplexAzbel: 'upwell_interior-indy',
 invC.typeEngineeringComplexSotiyo: 'upwell_interior-indy'}, sceneGIDOverrideMap={invC.typeRefineryAthanor: 25661,
 invC.typeRefineryTatara: 25661,
 invC.typeEngineeringComplexRaitaru: 25659,
 invC.typeEngineeringComplexAzbel: 25659,
 invC.typeEngineeringComplexSotiyo: 25659}, hangarType=5)
UPWELL_MODULAR_HANGAR_LOWSEC = dict(UPWELL_MODULAR_HANGAR, name='UPWELL_MODULAR_LOWSEC', hangarModelGraphicID=25605, dockingEffectGraphicID=25244)
UPWELL_MODULAR_HANGAR_CAPITAL = dict(DEFAULT_HANGAR_DICTIONARY, isModular=True, isCapital=True, name='UPWELL_MODULAR_CAPITAL', sceneGraphicID=25577, hangarModelGraphicID=25568, dockingEffectGraphicID=25244, factionOverrideMap={invC.typeRefineryAthanor: 'upwell_interior-refinery',
 invC.typeRefineryTatara: 'upwell_interior-refinery',
 invC.typeEngineeringComplexRaitaru: 'upwell_interior-indy',
 invC.typeEngineeringComplexAzbel: 'upwell_interior-indy',
 invC.typeEngineeringComplexSotiyo: 'upwell_interior-indy'}, sceneGIDOverrideMap={invC.typeRefineryAthanor: 25662,
 invC.typeRefineryTatara: 25662,
 invC.typeEngineeringComplexRaitaru: 25660,
 invC.typeEngineeringComplexAzbel: 25660,
 invC.typeEngineeringComplexSotiyo: 25660}, hangarType=6)
DEATHLESS_MODULAR_HANGAR = dict(DEFAULT_HANGAR_DICTIONARY, isModular=True, isEnlistmentDockingEnabled=True, isCapital=False, name='DEATHLESS_MODULAR_HANGAR', sceneGraphicID=26369, hangarModelGraphicID=26303, dockingEffectGraphicID=26436, factionOverrideMap={invC.typeDeathlessStation: 'deathless'}, hangarType=8)
DEATHLESS_FOB_HANGAR_ANGELS = dict(DEFAULT_HANGAR_DICTIONARY, isModular=True, isCapital=False, name='DEATHLESS_FOB_HANGAR_ANGELS', sceneGraphicID=26441, hangarModelGraphicID=26374, dockingEffectGraphicID=26437, hangarType=9)
DEATHLESS_FOB_HANGAR_GUERISTAS = dict(DEATHLESS_FOB_HANGAR_ANGELS, name='DEATHLESS_FOB_HANGAR_GUERISTAS', hangarModelGraphicID=26447)
HANGARS = {AMARR_NORMAL_HANGAR_SIZE['name']: AMARR_NORMAL_HANGAR_SIZE,
 CALDARI_NORMAL_HANGAR_SIZE['name']: CALDARI_NORMAL_HANGAR_SIZE,
 GALLENTE_NORMAL_HANGAR_SIZE['name']: GALLENTE_NORMAL_HANGAR_SIZE,
 MINMATAR_NORMAL_HANGAR_SIZE['name']: MINMATAR_NORMAL_HANGAR_SIZE,
 CITADEL_NORMAL_HANGAR_SIZE['name']: CITADEL_NORMAL_HANGAR_SIZE,
 CITADEL_CAPITAL_HANGAR_SIZE['name']: CITADEL_CAPITAL_HANGAR_SIZE,
 JITA_4_4_NORMAL_HANGAR_SIZE['name']: JITA_4_4_NORMAL_HANGAR_SIZE,
 AIR_NORMAL_HANGAR_SIZE['name']: AIR_NORMAL_HANGAR_SIZE,
 UPWELL_MODULAR_HANGAR['name']: UPWELL_MODULAR_HANGAR,
 UPWELL_MODULAR_HANGAR_LOWSEC['name']: UPWELL_MODULAR_HANGAR_LOWSEC,
 UPWELL_MODULAR_HANGAR_CAPITAL['name']: UPWELL_MODULAR_HANGAR_CAPITAL,
 DEATHLESS_MODULAR_HANGAR['name']: DEATHLESS_MODULAR_HANGAR,
 DEATHLESS_FOB_HANGAR_ANGELS['name']: DEATHLESS_FOB_HANGAR_ANGELS,
 DEATHLESS_FOB_HANGAR_GUERISTAS['name']: DEATHLESS_FOB_HANGAR_GUERISTAS}

def ShipNeedsACapitalHangar(shipTypeID):
    typeGroup = evetypes.GetGroupID(shipTypeID)
    return GetShipSizeClass(typeGroup) == 3


def GetHangarType(stationTypeID, shipTypeID, stationItemID = None):
    if HANGAR_TYPE_OVERRIDE is not None:
        return HANGAR_TYPE_OVERRIDE
    if stationTypeID == invC.typeAirOutpost:
        return AIR_NORMAL_HANGAR_SIZE['name']
    if stationItemID == invC.stationJitaIV4:
        return JITA_4_4_NORMAL_HANGAR_SIZE['name']
    if shipTypeID and ShipNeedsACapitalHangar(shipTypeID):
        return UPWELL_MODULAR_HANGAR_CAPITAL['name']
    if stationTypeID == invC.typeDeathlessStation:
        if shipTypeID and ShipNeedsACapitalHangar(shipTypeID):
            return UPWELL_MODULAR_HANGAR_CAPITAL['name']
        else:
            return DEATHLESS_MODULAR_HANGAR['name']
    else:
        if stationTypeID == invC.typeDeathlessFOBStationAngels:
            return DEATHLESS_FOB_HANGAR_ANGELS['name']
        if stationTypeID == invC.typeDeathlessFOBStationGuristas:
            return DEATHLESS_FOB_HANGAR_GUERISTAS['name']
        if evetypes.GetCategoryID(stationTypeID) == const.categoryStructure:
            if not IsHighSecSystem(session.solarsystemid2) and isHangarTypeCapitalDockable(stationTypeID):
                hangarType = UPWELL_MODULAR_HANGAR_LOWSEC['name']
            else:
                hangarType = UPWELL_MODULAR_HANGAR['name']
        else:
            raceID = evetypes.GetRaceID(stationTypeID)
            if raceID == const.raceAmarr:
                hangarType = AMARR_NORMAL_HANGAR_SIZE['name']
            elif raceID == const.raceCaldari:
                hangarType = CALDARI_NORMAL_HANGAR_SIZE['name']
            elif raceID == const.raceGallente:
                hangarType = GALLENTE_NORMAL_HANGAR_SIZE['name']
            elif raceID == const.raceMinmatar:
                hangarType = MINMATAR_NORMAL_HANGAR_SIZE['name']
            else:
                hangarType = MINMATAR_NORMAL_HANGAR_SIZE['name']
    return hangarType


def GetHangarTypeOverrideKeys():
    overrideKeys = {}
    for each in HANGARS:
        overrideKeys[each] = HANGARS[each].get('hangarModelGraphicID')

    return overrideKeys


def isHangarTypeCapitalDockable(stationTypeID):
    return stationTypeID in (invC.typeEngineeringComplexSotiyo, invC.typeCitadelKeepstar, invC.typeCitadelFortizar)


def isHangarModular(stationTypeID, shipTypeID, stationItemID = None):
    return HANGARS.get(GetHangarType(stationTypeID, shipTypeID, stationItemID)).get('isModular')


def isEnlistmentDockingEnabled(stationTypeID, shipTypeID, stationItemID = None):
    return HANGARS.get(GetHangarType(stationTypeID, shipTypeID, stationItemID)).get('isEnlistmentDockingEnabled')


def GetDockingEffectGraphicID(stationTypeID, shipTypeID, stationItemID = None):
    return HANGARS.get(GetHangarType(stationTypeID, shipTypeID, stationItemID)).get('dockingEffectGraphicID')


def isHangarCapital(stationTypeID, shipTypeID, stationItemID = None):
    return HANGARS.get(GetHangarType(stationTypeID, shipTypeID, stationItemID)).get('isCapital')


def GetHangarBehaviours(stationTypeID, shipTypeID, stationItemID = None):
    if isHangarModular(stationTypeID, shipTypeID, stationItemID):
        if isHangarCapital(stationTypeID, shipTypeID, stationItemID):
            return ALL_MODULAR_CAPITAL_BEHAVIOURS
        else:
            return ALL_MODULAR_BEHAVIOURS
    else:
        if isHangarCapital(stationTypeID, shipTypeID, stationItemID):
            return ALL_CAPITAL_BEHAVIOURS
        return ALL_DEFAULT_BEHAVIOURS


def GetHangarName(stationTypeID, shipTypeID, stationItemID = None):
    return HANGARS.get(GetHangarType(stationTypeID, shipTypeID, stationItemID)).get('name')


def GetHangarSceneGraphicID(stationTypeID, shipTypeID, stationItemID = None):
    hangar = HANGARS.get(GetHangarType(stationTypeID, shipTypeID, stationItemID))
    sceneGIDMap = hangar.get('sceneGIDOverrideMap')
    if sceneGIDMap is not None:
        gID = sceneGIDMap.get(stationTypeID)
        if gID is not None:
            return gID
    return hangar.get('sceneGraphicID')


def GetHangarModelGraphicID(stationTypeID, shipTypeID, stationItemID = None):
    return HANGARS.get(GetHangarType(stationTypeID, shipTypeID, stationItemID)).get('hangarModelGraphicID')


def GetHangarDockCameraMapping(stationTypeID, shipTypeID, stationItemID = None):
    return HANGARS.get(GetHangarType(stationTypeID, shipTypeID, stationItemID)).get('dockCameraSettings')


def GetHangarFactionDataOverwrite(stationTypeID, shipTypeID, stationItemID = None):
    FOMap = HANGARS.get(GetHangarType(stationTypeID, shipTypeID, stationItemID)).get('factionOverrideMap')
    if FOMap is not None and stationTypeID in FOMap:
        return FOMap[stationTypeID]
    else:
        return


def GetHangarMidAndHighActivityThresholds(stationTypeID, shipTypeID, stationItemID = None):
    settings = HANGARS.get(GetHangarType(stationTypeID, shipTypeID, stationItemID)).get('activityLevelThresholds')
    return (settings.get('MID_THRESHOLD'), settings.get('HIGH_THRESHOLD'))


def GetHangarIdentifier(stationTypeID, shipTypeID, stationItemID = None):
    return HANGARS.get(GetHangarType(stationTypeID, shipTypeID, stationItemID)).get('hangarType')
