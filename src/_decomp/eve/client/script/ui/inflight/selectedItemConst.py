#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\selectedItemConst.py
import eveicon
from eve.common.lib import appConst as const
from structures import FLEX_STRUCTURE_TYPES
ACTIONS_ALWAYS_VISIBLE = ['UI/Inflight/OrbitObject',
 'UI/Inflight/Submenus/KeepAtRange',
 'UI/Inflight/LockTarget',
 'UI/Inflight/LookAtObject',
 'UI/Inflight/SetAsCameraInterest',
 'UI/Commands/ShowInfo']
TOGGLE_ACTIONS = {'UI/Inflight/LockTarget': 'UI/Inflight/UnlockTarget',
 'UI/Inflight/LookAtObject': 'UI/Inflight/ResetCamera',
 'UI/Inflight/SpaceComponents/TowGameObjective/startTowing': 'UI/Inflight/SpaceComponents/TowGameObjective/stopTowing'}
ACTIONS_BY_TYPEID = {const.typeUpwellSmallStargate: ['UI/Inflight/JumpUsingBridge'],
 const.typeUpwellAutoMoonMiner: ['UI/Inflight/OpenMoonMaterialBay'],
 const.typeNeedlejackTrace: ['UI/Inflight/ActivateTraceGate'],
 const.typeYoiulTrace: ['UI/Inflight/ActivateTraceGate'],
 const.typeTriglavianSpaceTrace: ['UI/Inflight/ActivateTraceGate']}
for typeID in FLEX_STRUCTURE_TYPES:
    if typeID not in ACTIONS_BY_TYPEID:
        ACTIONS_BY_TYPEID[typeID] = []
    ACTIONS_BY_TYPEID[typeID].extend(['UI/Inflight/AccessHangarTransfer', 'UI/Inflight/BoardStructure'])

ACTIONS_BY_GROUPID = {const.groupStation: ['UI/Inflight/DockInStation'],
 const.groupWreck: ['UI/Commands/OpenCargo'],
 const.groupCargoContainer: ['UI/Commands/OpenCargo'],
 const.groupMissionContainer: ['UI/Commands/OpenCargo'],
 const.groupSecureCargoContainer: ['UI/Commands/OpenCargo'],
 const.groupAuditLogSecureContainer: ['UI/Commands/OpenCargo'],
 const.groupFreightContainer: ['UI/Commands/OpenCargo'],
 const.groupSpawnContainer: ['UI/Commands/OpenCargo'],
 const.groupSpewContainer: ['UI/Commands/OpenCargo'],
 const.groupDeadspaceOverseersBelongings: ['UI/Commands/OpenCargo'],
 const.groupPlanetaryCustomsOffices: ['UI/PI/Common/AccessCustomOffice'],
 const.groupOrbitalConstructionPlatforms: ['UI/DustLink/OpenUpgradeHold'],
 const.groupMoon: ['UI/Inflight/WarpToMoonMiningPoint'],
 const.groupReprocessingArray: ['UI/Inflight/POS/AccessPOSRefinery'],
 const.groupCompressionArray: ['UI/Inflight/POS/AccessPOSCompression'],
 const.groupMobileReactor: ['UI/Inflight/POS/AccessPOSStorage'],
 const.groupControlTower: ['UI/Inflight/POS/AccessPOSFuelBay', 'UI/Inflight/POS/AccessPOSStrontiumBay'],
 const.groupSilo: ['UI/Inflight/POS/AccessPOSStorage'],
 const.groupAssemblyArray: ['UI/Inflight/POS/AccessPOSStorage'],
 const.groupMobileLaboratory: ['UI/Inflight/POS/AccessPOSStorage'],
 const.groupCorporateHangarArray: ['UI/Inflight/POS/AccessPOSStorage'],
 const.groupPersonalHangar: ['UI/Inflight/POS/AccessPOSStorage'],
 const.groupMobileMissileSentry: ['UI/Inflight/POS/AccessPOSAmmo'],
 const.groupMobileHybridSentry: ['UI/Inflight/POS/AccessPOSAmmo'],
 const.groupMobileProjectileSentry: ['UI/Inflight/POS/AccessPOSAmmo'],
 const.groupMobileLaserSentry: ['UI/Inflight/POS/AccessPOSCrystalStorage'],
 const.groupShipMaintenanceArray: ['UI/Inflight/POS/AccessPOSVessels'],
 const.groupStargate: ['UI/Inflight/Jump'],
 const.groupWormhole: ['UI/Inflight/EnterWormhole'],
 const.groupWarpGate: ['UI/Inflight/ActivateGate'],
 const.groupAbyssalTraces: ['UI/Inflight/ActivateGate'],
 const.groupBillboard: ['UI/Commands/ReadNews'],
 const.groupAgentsinSpace: ['UI/Chat/StartConversation'],
 const.groupDestructibleAgentsInSpace: ['UI/Chat/StartConversation'],
 const.groupMiningDrone: ['UI/Drones/ScoopDroneToBay'],
 const.groupSalvageDrone: ['UI/Drones/ScoopDroneToBay'],
 const.groupPlanet: ['UI/PI/Common/ViewInPlanetMode'],
 const.groupInterstellarShipcaster: ['UI/Inflight/JumpByShipcaster'],
 const.groupTowableEntities: ['UI/Inflight/SpaceComponents/TowGameObjective/startTowing']}
ACTIONS_BY_CATEGORYID = {const.categoryShip: ['UI/Inflight/BoardShip'],
 const.categoryStructure: ['UI/Inflight/DockInStation', 'UI/Inflight/AccessHangarTransfer'],
 const.categoryDrone: ['UI/Drones/ScoopDroneToBay']}

class ActiveItemOptionObject(object):

    def __init__(self, iconPath, uniqueUiName, cmdName = None):
        self.iconPath = iconPath
        self.uniqueUiName = uniqueUiName
        self.cmdName = cmdName


ICON_APPROACH = 'res:/UI/Texture/icons/44_32_23.png'
ICON_ALIGN_TO = 'res:/UI/Texture/icons/44_32_59.png'
ICON_WARP_TO = 'res:/UI/Texture/Icons/44_32_18.png'
ICON_ORBIT = 'res:/UI/Texture/icons/44_32_21.png'
ICON_KEEP_AT_RANGE = 'res:/UI/Texture/icons/44_32_22.png'
ICON_JUMP_OR_ACTIVATE = 'res:/UI/Texture/icons/44_32_39.png'
ICON_LOCK_TARGET = 'res:/UI/Texture/icons/44_32_17.png'
ICON_DOCK_IN_STATION = 'res:/UI/Texture/icons/44_32_9.png'
ICON_BOARD = 'res:/UI/Texture/icons/44_32_40.png'
ICON_CARGO = 'res:/UI/Texture/icons/44_32_35.png'
ICON_START_TOW = eveicon.tow
ICON_STOP_TOW = eveicon.tow
ICON_CAMERA_LOOK_AT = 'res:/UI/Texture/icons/44_32_20.png'
ICON_CAMERA_TRACK = 'res:/UI/Texture/icons/44_32_65.png'
ICON_PLANET_VIEW = 'res:/UI/Texture/icons/77_32_34.png'
ICON_EXIT_PLANET_VIEW = 'res:/UI/Texture/icons/77_32_35.png'
ICON_SHOW_INFO = 'res:/UI/Texture/icons/44_32_24.png'
ICON_START_CONVERSATION = 'res:/UI/Texture/icons/44_32_33.png'
ICON_SALVAGE = 'res:/UI/Texture/icons/44_32_5.png'
ICON_VIEW_BILLBOARD = 'res:/UI/Texture/icons/44_32_47.png'
ICON_WARP_TO_MOON_MINING_POINT = 'res:/UI/Texture/Classes/Moonmining/warpToMiningPoint.png'
ICON_DRONE_ENGAGE = 'res:/UI/Texture/icons/44_32_4.png'
ICON_DRONE_RETURN = 'res:/UI/Texture/icons/44_32_1.png'
ICON_DRONE_RETURN_AND_ORBIT = 'res:/UI/Texture/icons/44_32_3.png'
ICON_DRONE_LAUNCH = 'res:/UI/Texture/icons/44_32_2.png'
ICON_ID_AND_CMD_BY_ACTIONID = {'UI/Commands/ShowInfo': ActiveItemOptionObject(ICON_SHOW_INFO, 'selectedItemShowInfo', 'CmdShowItemInfo'),
 'UI/Inflight/ApproachObject': ActiveItemOptionObject(ICON_APPROACH, 'selectedItemApproach', 'CmdApproachItem'),
 'UI/Inflight/AlignTo': ActiveItemOptionObject(ICON_ALIGN_TO, 'selectedItemAlignTo', 'CmdAlignToItem'),
 'UI/Inflight/OrbitObject': ActiveItemOptionObject(ICON_ORBIT, 'selectedItemOrbit', 'CmdOrbitItem'),
 'UI/Inflight/Submenus/KeepAtRange': ActiveItemOptionObject(ICON_KEEP_AT_RANGE, 'selectedItemKeepAtRange', 'CmdKeepItemAtRange'),
 'UI/Inflight/LockTarget': ActiveItemOptionObject(ICON_LOCK_TARGET, 'selectedItemLockTarget', 'CmdLockTargetItem'),
 'UI/Inflight/UnlockTarget': ActiveItemOptionObject(ICON_LOCK_TARGET, 'selectedItemUnLockTarget', 'CmdUnlockTargetItem'),
 'UI/Inflight/LookAtObject': ActiveItemOptionObject(ICON_CAMERA_LOOK_AT, 'selectedItemLookAt', 'CmdToggleLookAtItem'),
 'UI/Inflight/ResetCamera': ActiveItemOptionObject(ICON_CAMERA_LOOK_AT, 'selectedItemResetCamera'),
 'UI/Inflight/SetAsCameraInterest': ActiveItemOptionObject(ICON_CAMERA_TRACK, 'selectedItemSetInterest', 'CmdToggleCameraTracking'),
 'UI/Chat/StartConversation': ActiveItemOptionObject(ICON_START_CONVERSATION, 'selectedItemStartConversation'),
 'UI/Commands/OpenCargo': ActiveItemOptionObject(ICON_CARGO, 'selectedItemOpenCargo'),
 'UI/PI/Common/AccessCustomOffice': ActiveItemOptionObject(ICON_CARGO, 'selectedItemAccessCustomOffice'),
 'UI/DustLink/OpenUpgradeHold': ActiveItemOptionObject(ICON_CARGO, 'selectedItemOpenUpgradeHold'),
 'UI/Inflight/SpaceComponents/ItemTrader/Access': ActiveItemOptionObject(ICON_CARGO, 'selectedItemOpenCargo'),
 'UI/Inflight/SpaceComponents/UnderConstruction/Access': ActiveItemOptionObject(ICON_CARGO, 'selectedItemOpenCargo'),
 'UI/PI/Common/ExitPlanetMode': ActiveItemOptionObject(ICON_EXIT_PLANET_VIEW, 'selectedItemExitPlanetMode'),
 'UI/Inflight/POS/AccessPOSRefinery': ActiveItemOptionObject(ICON_CARGO, 'selectedItemAccessRefinery'),
 'UI/Inflight/POS/AccessPOSCompression': ActiveItemOptionObject(ICON_CARGO, 'selectedItemAccessCompression'),
 'UI/Inflight/POS/AccessPOSStrontiumBay': ActiveItemOptionObject(ICON_CARGO, 'selectedItemAccessTrontiumStorage'),
 'UI/Inflight/POS/AccessPOSFuelBay': ActiveItemOptionObject(ICON_CARGO, 'selectedItemAccessFuelStorage'),
 'UI/Inflight/POS/AccessPOSAmmo': ActiveItemOptionObject(ICON_CARGO, 'selectedItemAccessAmmunition'),
 'UI/Inflight/POS/AccessPOSCrystalStorage': ActiveItemOptionObject(ICON_CARGO, 'selectedItemAccessCrystalStorage'),
 'UI/Inflight/POS/AccessPOSStorage': ActiveItemOptionObject(ICON_CARGO, 'selectedItemAccessStorage'),
 'UI/Inflight/AccessHangarTransfer': ActiveItemOptionObject(ICON_CARGO, 'selectedItemAccessDropbox'),
 'UI/Inflight/POS/AccessPOSVessels': ActiveItemOptionObject(ICON_CARGO, 'selectedItemAccessVessels'),
 'UI/Commands/AccessBountyEscrow': ActiveItemOptionObject(ICON_CARGO, 'selectedItemAccessBountyEscrow'),
 'UI/Drones/EngageTarget': ActiveItemOptionObject(ICON_DRONE_ENGAGE, 'selectedItemEngageTarget'),
 'UI/Drones/MineWithDrone': ActiveItemOptionObject(ICON_DRONE_ENGAGE, 'selectedItemMine'),
 'UI/Drones/Salvage': ActiveItemOptionObject(ICON_SALVAGE, 'selectedItemSalvage'),
 'UI/Inflight/POS/AnchorObject': ActiveItemOptionObject(ICON_DRONE_ENGAGE, 'selectedItemUnanchor'),
 'UI/Drones/ReturnDroneAndOrbit': ActiveItemOptionObject(ICON_DRONE_RETURN_AND_ORBIT, 'selectedItemReturnAndOrbit'),
 'UI/Drones/ReturnDroneToBay': ActiveItemOptionObject(ICON_DRONE_RETURN, 'selectedItemReturnToDroneBay'),
 'UI/Drones/ScoopDroneToBay': ActiveItemOptionObject(ICON_DRONE_RETURN, 'selectedItemScoopToDroneBay'),
 'UI/Drones/LaunchDrones': ActiveItemOptionObject(ICON_DRONE_LAUNCH, 'selectedItemLaunchDrones'),
 'UI/Inflight/BoardShip': ActiveItemOptionObject(ICON_BOARD, 'selectedItemBoardShip'),
 'UI/Inflight/BoardStructure': ActiveItemOptionObject(ICON_BOARD, 'selectedItemBoardStructure'),
 'UI/Inflight/DockInStation': ActiveItemOptionObject(ICON_DOCK_IN_STATION, 'selectedItemDock', 'CmdDockOrJumpOrActivateGate'),
 'UI/Inflight/Jump': ActiveItemOptionObject(ICON_JUMP_OR_ACTIVATE, 'selectedItemJump', 'CmdDockOrJumpOrActivateGate'),
 'UI/Inflight/JumpUsingBridge': ActiveItemOptionObject(ICON_JUMP_OR_ACTIVATE, 'selectedItemJump', 'CmdDockOrJumpOrActivateGate'),
 'UI/Inflight/EnterWormhole': ActiveItemOptionObject(ICON_JUMP_OR_ACTIVATE, 'selectedItemEnterWormhole', 'CmdDockOrJumpOrActivateGate'),
 'UI/Inflight/ActivateGate': ActiveItemOptionObject(ICON_JUMP_OR_ACTIVATE, 'selectedItemActivateGate', 'CmdDockOrJumpOrActivateGate'),
 'UI/Inflight/ActivateTraceGate': ActiveItemOptionObject(ICON_JUMP_OR_ACTIVATE, 'selectedItemActivateTraceGate', 'CmdDockOrJumpOrActivateGate'),
 'UI/Commands/ReadNews': ActiveItemOptionObject(ICON_VIEW_BILLBOARD, 'selectedItemReadNews'),
 'UI/Fleet/JumpThroughToSystem': ActiveItemOptionObject(ICON_JUMP_OR_ACTIVATE, 'selectedItemJumpThroughToSystem', 'CmdDockOrJumpOrActivateGate'),
 'UI/Fleet/JumpThrough': ActiveItemOptionObject(ICON_JUMP_OR_ACTIVATE, 'selectedItemJumpThroughToSystem', 'CmdDockOrJumpOrActivateGate'),
 'UI/PI/Common/ViewInPlanetMode': ActiveItemOptionObject(ICON_PLANET_VIEW, 'selectedItemViewInPlanetMode'),
 'UI/Inflight/WarpToMoonMiningPoint': ActiveItemOptionObject(ICON_WARP_TO_MOON_MINING_POINT, 'selectedItemMoonminingPoint'),
 'UI/Inflight/WarpToWithinDistance': ActiveItemOptionObject(ICON_WARP_TO, 'selectedItemWarpTo', 'CmdWarpToItem'),
 'UI/Inflight/Submenus/WarpToWithin': ActiveItemOptionObject(ICON_WARP_TO, 'selectedItemWarpTo', 'CmdWarpToItem'),
 'UI/Inflight/JumpByShipcaster': ActiveItemOptionObject(ICON_JUMP_OR_ACTIVATE, 'selectedItemShipcasterJump', 'CmdDockOrJumpOrActivateGate'),
 'UI/Inflight/SpaceComponents/TowGameObjective/startTowing': ActiveItemOptionObject(ICON_START_TOW, 'selectedItemTowableStartTow'),
 'UI/Inflight/SpaceComponents/TowGameObjective/stopTowing': ActiveItemOptionObject(ICON_STOP_TOW, 'selectedItemTowableStopTow'),
 'UI/Inflight/OpenMoonMaterialBay': ActiveItemOptionObject(eveicon.retrieve, 'selectedItemOpenMoonMaterialBay')}
RESET_ACTIONS = ('UI/Inflight/UnlockTarget', 'UI/Inflight/ResetCamera', 'UI/Inflight/SpaceComponents/TowGameObjective/stopTowing')
CLOSE_MENU_ACTIONS = ('UI/Inflight/OrbitObject', 'UI/Inflight/Submenus/KeepAtRange', 'UI/Inflight/WarpToWithinDistance')
POINTER_ACTIONS = ('UI/DustLink/OpenUpgradeHold', 'UI/Inflight/POS/AccessPOSRefinery', 'UI/Inflight/POS/AccessPOSCompression', 'UI/Inflight/POS/AccessPOSStrontiumBay', 'UI/Inflight/POS/AccessPOSFuelBay', 'UI/Inflight/POS/AccessPOSAmmo', 'UI/Inflight/POS/AccessPOSCrystalStorage', 'UI/Inflight/POS/AccessPOSStorage', 'UI/Inflight/POS/AccessPOSVessels', 'UI/Commands/AccessBountyEscrow', 'UI/Inflight/POS/AnchorObject')
SUB_MENU_ACTIONS = ['UI/Inflight/MoonMiningPoint']
