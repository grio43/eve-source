#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\hangarBehaviours\modularHangarBehavioursConstants.py
import inventorycommon.const as invC
SHIP_SWAP_DURATION = 4
TRANSITION_PADDING = 3
TRANSITION_MODIFY_BY_HALLWAYTIME = True
TRANSITION_TIME_REMAP = [0.14, 0.8]
FP_SWAP_SPEED = 1.1
FP_SWAP_TIMING = 0.5
FP_SWAP_VALUE = 0.5
PATH_ORIGINAL_POSITION_RELEVANCY = [-0.2, 0.2, 2.0]
PATH_FIRST_EXIT_RELEVANCY = [0.0, 0.45, 1.7]
PATH_FIRST_HALLWAY_POINT_RELEVANCY = [0.1, 0.7, 2.0]
PATH_END_HALLWAY_POINT_RELEVANCY = [0.4, 1.2, 2.2]
PATH_END_EXIT_RELEVANCY = [0.7, 1.1, 9.0]
PATH_END_DOCK_POINT_RELEVANCY = [0.9, 1.1, 2.0]
PATH_BELL_CURVE_CONST = 0.0
CAMERA_FOLLOW_SPEED = 3.0
PHASE_1_TO_2_BLEND_DURATION = 3.333
PHASE_2_DURATION = 4.0
PHASE_2_START_THRESHOLD = 2.0
PHASE_2_LERPING_SPEED = 1.333
PHASE_2_END_ZOOM_LEVEL = 0.5
SMALL_PLATFORM_CAMERA_BOUNDS = 385.0
SMALL_PLATFORM_BOUNDING_PADDING = 0.4
SMALL_PLATFORM_GAP_INNER_EDGE = 40.0
SMALL_PLATFORM_GAP_OUTER_EDGE = 100.0
SMALL_PLATFORM_OUTER_EDGE = 220.0
MEDIUM_PLATFORM_CAMERA_BOUNDS = 1450.0
MEDIUM_PLATFORM_BOUNDING_PADDING = 0.2
SMALL_PLATFORM_SHIP_PLACEMENT_OFFSET = (0.0, 0.5, 0.0, 0.75)
MEDIUM_PLATFORM_SHIP_PLACEMENT_OFFSET = (-100, 0.6, 120, 1.0)
MEDIUM_PLATFORM_GAP_INNER_EDGE = 600.0
MEDIUM_PLATFORM_GAP_OUTER_EDGE = 3000.0
MEDIUM_PLATFORM_OUTER_EDGE = 5000.0
SHIELD_ELLIPSOID_ROUNDING_FACTOR = 0.3
SHIELD_ELLIPSOID_ZOOM_MULTIPLIER = 2.3
SMALL_PLATFORM_INNER_PADDING = 10
SMALL_PLATFORM_INNER_PADDING_BOUNDING_SPHERE_FACTOR = 0.1
SMALL_PLATFORM_OUTER_PADDING = 120
MEDIUM_PLATFORM_INNER_PADDING = 250
MEDIUM_PLATFORM_OUTER_PADDING = 500
CAMERA_POSITIONS_TITAN = [((5444.7427, 1895.704, 12005.2295), (-41299.582, -20467.1523, -35926.1484), 1.0),
 ((4427.26, -2705.96, 10374.68), (-5506.1992, 783.7142, -1980.421), 1.2),
 ((10.0821, -1089.0815, 20721.5137), (-237.8054, -666.7568, -20549.0625), 0.41),
 ((-4443.8242, 315.2098, 11118.0244), (7649.5317, -3684.9685, -4091.6868), 1.0)]
CAMERA_POSITIONS_SUPER = [((4354.69, -1805.85, 7763.24), (-2197.9038, -4998.0479, -2801.7432), 1.0), ((547.0052, -2406.0664, 6446.3447), (9462.0059, -1717.0839, -7038.4194), 1.2), ((4965.1689, -2687.8481, 8404.4502), (-4426.8589, -1868.6879, -6898.1924), 0.5)]
CAMERA_POSITIONS_FAUX = [((4228.06, -2846.66, 7806.1), (-4223.3691, 296.6928, -4222.8926), 0.95),
 ((4050.6973, -2978.6477, 9327.3213), (-2385.6045, 110.5095, -5427.2505), 0.65),
 ((3754.3704, 189.946, 8036.9219), (-3367.6882, -5063.1665, -6578.5303), 0.95),
 ((-29.7784, -2974.7385, 5863.6021), (8872.2881, 1349.8269, -1069.6536), 1.2)]
CAMERA_POSITIONS_CARRIERS = [((4334.27, -2351.75, 6206.56), (-2551.7729, -4076.748, -1332.4971), 1.0), ((4224.8784, -2917.3191, 6919.7632), (-2671.8972, -874.185, -5643.4419), 0.73), ((2216.0313, -2930.8423, 6675.5537), (7861.8989, -1501.5132, -3819.3167), 0.73)]
CAMERA_POSITIONS_DREADNOUGHTS = [((4872.93, -2654.53, 8681.48), (-3319.2869, -857.0933, -4592.0674), 0.82), ((416.9402, -3287.2087, 8312.957), (17782.9414, 4351.7769, -11191.4043), 0.73), ((4610.832, -1437.255, 9349.2461), (-3372.7212, -4670.667, -6637.0093), 0.77)]
CAMERA_POSITIONS_FREIGHTERS = [((4872.93, -2654.53, 8681.48), (-3319.2869, -857.0933, -4592.0674), 0.75), ((5503.5024, -1862.807, 9821.9131), (-3368.6204, -4564.1543, -5448.9756), 0.6), ((2258.3635, -3179.9424, 9105.2832), (7339.9058, -280.3324, -1016.624), 0.6)]
CAPITAL_CAMERA_POSITION_MAP = {invC.groupDreadnought: CAMERA_POSITIONS_DREADNOUGHTS,
 invC.groupLancerDreadnought: CAMERA_POSITIONS_DREADNOUGHTS,
 invC.groupTitan: CAMERA_POSITIONS_TITAN,
 invC.groupForceAux: CAMERA_POSITIONS_FAUX,
 invC.groupSupercarrier: CAMERA_POSITIONS_SUPER,
 invC.groupCarrier: CAMERA_POSITIONS_CARRIERS,
 invC.groupFreighter: CAMERA_POSITIONS_FREIGHTERS,
 invC.groupJumpFreighter: CAMERA_POSITIONS_FREIGHTERS,
 invC.groupCapitalIndustrialShip: CAMERA_POSITIONS_CARRIERS}
CAPITAL_CAMERA_WIGGLE_AMMOUNT = 0.1
CAPITAL_CAMERA_DEFAULT_START_POSITION = (3150.0, 2220.0, 16500.0)
CAPITAL_CAMERA_DEFAULT_FOCUS_POINT = (0.0, -500.0, 7500.0)
DOCKER_CAPITAL_MULTIEFFECT_GRAPHIC_ID = 25244
LOCATORSET_DISPLAY_OFFSET = 'display_offset'
LOCATORSET_SMALL_DOCK_SHIPS = 'small_dock_ships'
LOCATORSET_SMALL_DOCK_EXITS = 'small_dock_exit_points'
LOCATORSET_MEDIUM_DOCK_SHIPS = 'medium_dock_ships'
LOCATORSET_MEDIUM_DOCK_EXITS = 'medium_dock_exit_points'
LOCATORSET_HALLWAY_POINTS = 'hallway_path'
LOCATORSET_ENTRANCE_POINTS = 'entrance_areas'
LOCATORSET_CAPITAL_SHIP = 'capital_ships'
LOCATORSET_SMALL_DOCK_CAMERA_EXITS = 'small_dock_camera_transition_points'
LOCATORSET_MEDIUM_DOCK_CAMERA_EXITS = 'medium_dock_camera_transition_points'
LOCATORSET_MEDIUM_DEATHLESS_DOCK = 'mdepl_m_01a_deathless'
LOCATORSET_SMALL_DEATHLESS_DOCK = 'mdepl_s_01a_deathless'
LOCATORSET_MEDIUM_GURISTAS_DOCK = 'mdepl_m_01a_guristas'
LOCATORSET_SMALL_GURISTAS_DOCK = 'mdepl_s_01a_guristas'
LOCATORSET_MEDIUM_ANGEL_DOCK = 'mdepl_m_01a_angel'
LOCATORSET_SMALL_ANGEL_DOCK = 'mdepl_s_01a_angel'

def _CreateShipSizeClassLookUpTable():
    sizeMapping = [[invC.typeCapsule, invC.typeCapsuleGolden],
     [invC.groupCorvette,
      invC.groupShuttle,
      invC.groupFrigate,
      invC.groupAssaultFrigate,
      invC.groupInterceptor,
      invC.groupCommandDestroyer,
      invC.groupDestroyer,
      invC.groupStealthBomber,
      invC.groupLogisticsFrigate,
      invC.groupElectronicAttackShips,
      invC.groupInterdictor,
      invC.groupCovertOps,
      invC.groupExpeditionFrigate,
      invC.groupPrototypeExplorationShip],
     [invC.groupTacticalDestroyer,
      invC.groupForceReconShip,
      invC.groupCombatReconShip,
      invC.groupCommandShip,
      invC.groupBattlecruiser,
      invC.groupAttackBattlecruiser,
      invC.groupHeavyAssaultCruiser,
      invC.groupHeavyInterdictors,
      invC.groupStrategicCruiser,
      invC.groupBlackOps,
      invC.groupMarauders,
      invC.groupBattleship,
      invC.groupLogistics,
      invC.groupTransportShip,
      invC.groupCruiser,
      invC.groupMiningBarge,
      invC.groupBlockadeRunner,
      invC.groupExhumer,
      invC.groupJumpFreighter,
      invC.groupIndustrial,
      invC.groupFlagCruiser,
      invC.groupIndustrialCommandShip],
     [invC.groupDreadnought,
      invC.groupTitan,
      invC.groupSupercarrier,
      invC.groupForceAux,
      invC.groupCarrier,
      invC.groupJumpFreighter,
      invC.groupCapitalIndustrialShip,
      invC.groupFreighter,
      invC.groupLancerDreadnought]]
    classMapping = []
    for i in range(0, len(sizeMapping)):
        classMapping = classMapping + [i] * len(sizeMapping[i])

    return dict(zip(sum(sizeMapping, []), classMapping))


SHIP_SIZE_CLASS_LOOKUP_DICTIONARY = _CreateShipSizeClassLookUpTable()

def GetShipSizeClass(shipGroup):
    group = SHIP_SIZE_CLASS_LOOKUP_DICTIONARY.get(shipGroup)
    return group or 1.0


def IsInLookUpTable(groupID):
    return SHIP_SIZE_CLASS_LOOKUP_DICTIONARY.get(groupID) is not None
