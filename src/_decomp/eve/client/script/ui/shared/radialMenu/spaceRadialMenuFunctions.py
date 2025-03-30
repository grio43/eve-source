#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\radialMenu\spaceRadialMenuFunctions.py
import types
import logging
import eveicon
from carbonui.control.contextMenu.menuEntryData import BaseMenuEntryData
from collections import OrderedDict
from menu import MenuLabel, CaptionIsInMultiFunctions
from eve.client.script.ui.shared.radialMenu import NORMAL_RADIAL_MENU, BROADCAST_RADIAL_MENU
from eve.client.script.ui.shared.radialMenu.broadcastRadialMenuFunctions import GetBroadcastForShieldMenuAction, GetBroadcastForArmorMenuAction, GetBroadcastForCapacitorMenuAction, GetBroadcastTargetMenuAction, GetBroadcastAlignToMenuAction, GetBroadcastWarpToMenuAction
from eve.client.script.ui.util.uix import GetBallparkRecord
from eve.common.script.sys.eveCfg import GetActiveShip
from eve.common.script.sys.idCheckers import IsCharacter
import inventorycommon.const as invConst
import carbonui.const as uiconst
import evetypes
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import KeepAtRange as movementFunctions__KeepAtRange
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import Orbit as movementFunctions__Orbit
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import GetWarpToRanges as movementFunctions__GetWarpToRanges
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToBookmark as movementFunctions__WarpToBookmark
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem as movementFunctions__WarpToItem
import eve.client.script.ui.util.defaultRangeUtils as defaultRangeUtils
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import RadialMenuOptionsInfo
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import RangeRadialMenuAction
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import SecondLevelRadialMenuAction
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import SimpleRadialMenuAction
from carbonui.uiconst import MOUSEBUTTONS
from eve.client.script.ui.inflight.dungeoneditor import DungeonEditor
from spacecomponents.common.componentConst import FITTING_CLASS, SCOOP_CLASS, CARGO_BAY
from spacecomponents.common.data import get_space_component_names_for_type
from spacecomponents.common.helper import HasMicroJumpDriverComponent, HasItemTrader, HasShipcasterComponent, HasUnderConstructionComponent, HasTowGameObjectiveComponent
from structures import FLEX_STRUCTURE_TYPES
from utillib import KeyVal
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
logger = logging.getLogger(__name__)
primaryCategoryActions = {invConst.categoryDrone: [SimpleRadialMenuAction(option1='UI/Drones/EngageTarget', option2='UI/Drones/LaunchDrone')],
 invConst.categoryShip: [SimpleRadialMenuAction(option1='UI/Inflight/BoardShip')],
 invConst.categoryStation: [SimpleRadialMenuAction(option1='UI/Inflight/DockInStation', option2='UI/Inflight/JumpThroughStargate', option3Path='UI/Inflight/JumpThroughJumpgate', option4Path='UI/Inflight/SetDestination')],
 invConst.categoryStructure: [SimpleRadialMenuAction(option1='UI/Inflight/DockInStation', option2='UI/Inflight/JumpThroughStargate', option3Path='UI/Inflight/JumpThroughJumpgate', option4Path='UI/Inflight/SetDestination')],
 invConst.categoryAsteroid: [SimpleRadialMenuAction(option1='UI/Inflight/SetDestination')]}
primaryGroupActions = {invConst.groupAgentsinSpace: [SimpleRadialMenuAction(option1='UI/Chat/StartConversation')],
 invConst.groupDestructibleAgentsInSpace: [SimpleRadialMenuAction(option1='UI/Chat/StartConversation')],
 invConst.groupAuditLogSecureContainer: [SimpleRadialMenuAction(option1='UI/Commands/OpenCargo')],
 invConst.groupBillboard: [SimpleRadialMenuAction(option1='UI/Commands/ReadNews')],
 invConst.groupBiomass: [SimpleRadialMenuAction(option1='UI/Inflight/ScoopToCargoHold')],
 invConst.groupCargoContainer: [SimpleRadialMenuAction(option1='UI/Commands/OpenCargo')],
 invConst.groupSecureCargoContainer: [SimpleRadialMenuAction(option1='UI/Commands/OpenCargo')],
 invConst.groupMissionContainer: [SimpleRadialMenuAction(option1='UI/Commands/OpenCargo')],
 invConst.groupFreightContainer: [SimpleRadialMenuAction(option1='UI/Commands/OpenCargo')],
 invConst.groupMiningDrone: [SimpleRadialMenuAction(option1='UI/Drones/MineWithDrone', option2='UI/Drones/LaunchDrone')],
 invConst.groupPlanet: [SimpleRadialMenuAction(option1='UI/PI/Common/ViewInPlanetMode', option2='UI/Inflight/SetDestination')],
 invConst.groupSalvageDrone: [SimpleRadialMenuAction(option1='UI/Drones/Salvage', option2='UI/Drones/LaunchDrone')],
 invConst.groupStargate: [SimpleRadialMenuAction(option1='UI/Inflight/Jump', option2='UI/Inflight/SetDestination')],
 invConst.groupWormhole: [SimpleRadialMenuAction(option1='UI/Inflight/EnterWormhole')],
 invConst.groupWreck: [SimpleRadialMenuAction(option1='UI/Commands/OpenCargo')],
 invConst.groupWarpGate: [SimpleRadialMenuAction(option1='UI/Inflight/ActivateGate')],
 invConst.groupAbyssalTraces: [SimpleRadialMenuAction(option1='UI/Inflight/ActivateGate')],
 invConst.groupSpawnContainer: [SimpleRadialMenuAction(option1='UI/Commands/OpenCargo')],
 invConst.groupSpewContainer: [SimpleRadialMenuAction(option1='UI/Commands/OpenCargo')],
 invConst.groupTitan: [SimpleRadialMenuAction(option1='UI/Inflight/BoardShip', option2='UI/Fleet/JumpThroughToSystem')],
 invConst.groupBlackOps: [SimpleRadialMenuAction(option1='UI/Inflight/BoardShip', option2='UI/Fleet/JumpThroughToSystem')],
 invConst.groupCapitalIndustrialShip: [SimpleRadialMenuAction(option1='UI/Inflight/BoardShip', option2='UI/Fleet/JumpThroughToSystem')],
 invConst.groupOrbitalInfrastructure: [SimpleRadialMenuAction(option1='UI/PI/Common/AccessCustomOffice')],
 invConst.groupSkyhook: [SimpleRadialMenuAction(option1='UI/PI/Common/AccessCustomOffice')],
 invConst.groupSolarSystem: [SimpleRadialMenuAction(option1='UI/Inflight/JumpThroughStargate', option2='UI/Inflight/JumpThroughJumpgate', option3Path='UI/Inflight/SetDestination')],
 invConst.groupMoon: [SimpleRadialMenuAction(option1='UI/Inflight/SetDestination')],
 invConst.groupSun: [SimpleRadialMenuAction(option1='UI/Inflight/SetDestination')],
 invConst.groupIndustrialCommandShip: [SimpleRadialMenuAction(option1='UI/Inflight/BoardShip', option2='UI/Commands/OpenFleetHangar')],
 invConst.groupAssemblyArray: [SimpleRadialMenuAction(option1='UI/Inflight/POS/AccessPOSStorage')],
 invConst.groupControlTower: [SimpleRadialMenuAction(option1='UI/Inflight/POS/ManageControlTower')],
 invConst.groupCorporateHangarArray: [SimpleRadialMenuAction(option1='UI/Inflight/POS/AccessPOSStorage')],
 invConst.groupMobileLaboratory: [SimpleRadialMenuAction(option1='UI/Inflight/POS/AccessPOSStorage')],
 invConst.groupMobileLaserSentry: [SimpleRadialMenuAction(option1='UI/Inflight/POS/AccessPOSCrystalStorage')],
 invConst.groupMobileMissileSentry: [SimpleRadialMenuAction(option1='UI/Inflight/POS/AccessPOSAmmo')],
 invConst.groupMobileHybridSentry: [SimpleRadialMenuAction(option1='UI/Inflight/POS/AccessPOSAmmo')],
 invConst.groupMobileProjectileSentry: [SimpleRadialMenuAction(option1='UI/Inflight/POS/AccessPOSAmmo')],
 invConst.groupMobileReactor: [SimpleRadialMenuAction(option1='UI/Inflight/POS/AccessPOSStorage')],
 invConst.groupPersonalHangar: [SimpleRadialMenuAction(option1='UI/Inflight/POS/AccessPOSStorage')],
 invConst.groupReprocessingArray: [SimpleRadialMenuAction(option1='UI/Inflight/POS/AccessPOSRefinery')],
 invConst.groupCompressionArray: [SimpleRadialMenuAction(option1='UI/Inflight/POS/AccessPOSCompression')],
 invConst.groupShipMaintenanceArray: [SimpleRadialMenuAction(option1='UI/Inflight/POS/AccessPOSVessels')],
 invConst.groupSilo: [SimpleRadialMenuAction(option1='UI/Inflight/POS/AccessPOSStorage')],
 invConst.groupInfrastructureHub: [SimpleRadialMenuAction(option1='UI/Menusvc/OpenHubManager')],
 invConst.groupControlBunker: [SimpleRadialMenuAction(option1='UI/FactionWarfare/IHub/OpenInfrastructureHubPanel')],
 invConst.groupDeadspaceOverseersBelongings: [SimpleRadialMenuAction(option1='UI/Commands/OpenCargo')]}
primaryTypeActions = {invConst.typeUpwellSmallStargate: [SimpleRadialMenuAction(option1='UI/Inflight/JumpUsingBridge')],
 invConst.typeNeedlejackTrace: [SimpleRadialMenuAction(option1='UI/Inflight/ActivateTraceGate')],
 invConst.typeYoiulTrace: [SimpleRadialMenuAction(option1='UI/Inflight/ActivateTraceGate')],
 invConst.typeTriglavianSpaceTrace: [SimpleRadialMenuAction(option1='UI/Inflight/ActivateTraceGate')]}
bookMarkOption = SimpleRadialMenuAction(option1='UI/Inflight/BookmarkLocation', option2='UI/Inflight/EditBookmark')
lookAtOption = SimpleRadialMenuAction(option1='UI/Inflight/LookAtObject', option2='UI/Inflight/ResetCamera')
setInterestOption = SimpleRadialMenuAction(option1='UI/Inflight/SetAsCameraInterest')
bookMarkAndLookatOptions = [lookAtOption, bookMarkOption, setInterestOption]
secondaryCategoryActions = {invConst.categoryAsteroid: bookMarkAndLookatOptions,
 invConst.categoryEntity: [lookAtOption, setInterestOption],
 invConst.categoryShip: [lookAtOption, setInterestOption],
 invConst.categoryStation: bookMarkAndLookatOptions,
 invConst.categoryStructure: bookMarkAndLookatOptions + [SimpleRadialMenuAction(option1='UI/Inflight/AccessHangarTransfer')],
 invConst.categoryStarbase: bookMarkAndLookatOptions,
 invConst.categorySovereigntyStructure: bookMarkAndLookatOptions,
 invConst.categoryCelestial: bookMarkAndLookatOptions,
 invConst.categoryOrbital: bookMarkAndLookatOptions,
 invConst.categoryDeployable: bookMarkAndLookatOptions,
 invConst.categoryFighter: [lookAtOption, setInterestOption],
 invConst.categoryDrone: [lookAtOption, setInterestOption] + [SimpleRadialMenuAction(option1='UI/Drones/ReturnDroneAndOrbit'),
                          SimpleRadialMenuAction(option1='UI/Inflight/ScoopToCargoHold'),
                          SimpleRadialMenuAction(option1='UI/Drones/ReturnDroneToBay'),
                          SimpleRadialMenuAction(),
                          SimpleRadialMenuAction(option1='UI/Drones/ScoopDroneToBay')]}
secondaryGroupActions = {invConst.groupAuditLogSecureContainer: [SimpleRadialMenuAction(option1='UI/Inflight/ScoopToCargoHold')],
 invConst.groupBillboard: [bookMarkOption],
 invConst.groupMoon: [SimpleRadialMenuAction(), SimpleRadialMenuAction(), SimpleRadialMenuAction(option1='UI/Inflight/WarpToMoonMiningPoint')],
 invConst.groupSkyhook: [SimpleRadialMenuAction(option1='UI/OrbitalSkyhook/SkyhookWnd/AccessOrbitalSkyhookOffice')],
 invConst.groupMercenaryDen: [SimpleRadialMenuAction(option1='UI/Sovereignty/MercenaryDen/ConfigurationWindow/ConfigureMercenaryDen')]}
secondaryTypeActions = {}
for typeID in FLEX_STRUCTURE_TYPES:
    secondaryTypeActions[typeID] = [SimpleRadialMenuAction(option1='UI/Inflight/BoardStructure')]

secondaryTypeActions[invConst.typeUpwellAutoMoonMiner] += [SimpleRadialMenuAction(option1='UI/Inflight/OpenMoonMaterialBay')]
subMenusToExpand = ['UI/Inflight/MoonMiningPoint']
placeholderIconPath = 'res:/UI/Texture/Icons/9_64_13.png'
iconDict = {'UI/Commands/ShowInfo': 'res:/UI/Texture/Icons/44_32_24.png',
 'UI/Inflight/ApproachObject': 'res:/UI/Texture/Icons/44_32_23.png',
 'UI/Inflight/ApproachLocationActionGroup': 'res:/UI/Texture/Icons/44_32_23.png',
 'UI/Inflight/AlignTo': 'res:/UI/Texture/Icons/44_32_59.png',
 'UI/Inflight/OrbitObject': 'res:/UI/Texture/Icons/44_32_21.png',
 'UI/Inflight/Submenus/KeepAtRange': 'res:/UI/Texture/Icons/44_32_22.png',
 'UI/Inflight/LockTarget': 'res:/UI/Texture/Icons/44_32_17.png',
 'UI/Inflight/UnlockTarget': 'res:/UI/Texture/classes/RadialMenuActions/untarget.png',
 'UI/Inflight/CancelLockTarget': 'res:/UI/Texture/classes/RadialMenuActions/untarget.png',
 'UI/Inflight/LookAtObject': 'res:/UI/Texture/Icons/44_32_20.png',
 'UI/Inflight/ResetCamera': 'res:/UI/Texture/classes/RadialMenuActions/resetCamera.png',
 'UI/Inflight/SetAsCameraInterest': 'res:/UI/Texture/Icons/44_32_65.png',
 'UI/Inflight/BoardShip': 'res:/UI/Texture/Icons/44_32_40.png',
 'UI/Inflight/BoardStructure': 'res:/UI/Texture/Icons/44_32_40.png',
 'UI/Inflight/DockInStation': 'res:/UI/Texture/Icons/44_32_9.png',
 'UI/Inflight/Jump': 'res:/UI/Texture/Icons/44_32_39.png',
 'UI/Inflight/JumpByShipcaster': 'res:/UI/Texture/Icons/44_32_39.png',
 'UI/Inflight/JumpUsingBridge': 'res:/UI/Texture/Icons/44_32_39.png',
 'UI/Inflight/JumpThroughStargate': 'res:/UI/Texture/Icons/44_32_39.png',
 'UI/Inflight/JumpThroughJumpgate': 'res:/UI/Texture/Icons/44_32_39.png',
 'UI/Fleet/JumpThroughToSystem': 'res:/UI/Texture/Icons/44_32_39.png',
 'UI/Commands/OpenCargo': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/Commands/OpenCargoHold': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/Commands/OpenFleetHangar': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/PI/Common/AccessCustomOffice': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/OrbitalSkyhook/SkyhookWnd/AccessOrbitalSkyhookOffice': eveicon.skyhook,
 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/ConfigureMercenaryDen': eveicon.mercenary_den,
 'UI/Inflight/AccessHangarTransfer': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/Inflight/OpenMoonMaterialBay': eveicon.retrieve,
 'UI/Inflight/ScoopToCargoHold': 'res:/UI/Texture/Icons/scoopcargo.png',
 'UI/Drones/ScoopDroneToBay': 'res:/UI/Texture/classes/RadialMenuActions/scoopDrone.png',
 'UI/Drones/LaunchDrone': 'res:/UI/Texture/Icons/44_32_2.png',
 'UI/Drones/ReturnDroneToBay': 'res:/UI/Texture/Icons/44_32_1.png',
 'UI/Chat/StartConversation': 'res:/UI/Texture/Icons/44_32_33.png',
 'UI/Inflight/EnterWormhole': 'res:/UI/Texture/Icons/44_32_39.png',
 'UI/Drones/EngageTarget': 'res:/UI/Texture/Icons/44_32_11.png',
 'UI/Drones/MineWithDrone': 'res:/UI/Texture/Icons/44_32_5.png',
 'UI/Drones/Salvage': 'res:/UI/Texture/Icons/44_32_4.png',
 'UI/Drones/ReturnDroneAndOrbit': 'res:/UI/Texture/Icons/44_32_3.png',
 'UI/Commands/ReadNews': 'res:/UI/Texture/Icons/44_32_47.png',
 'UI/Inflight/Submenus/WarpToWithin': 'res:/UI/Texture/Icons/44_32_18.png',
 'UI/Fleet/WarpToMemberSubmenuOption': 'res:/UI/Texture/Icons/44_32_18.png',
 'UI/Inflight/WarpToBookmark': 'res:/UI/Texture/Icons/44_32_18.png',
 'UI/Inflight/BookmarkLocation': 'res:/UI/Texture/Icons/bookmark.png',
 'UI/Inflight/EditBookmark': 'res:/UI/Texture/classes/RadialMenuActions/edit_bookmark.png',
 'UI/PI/Common/ViewInPlanetMode': 'res:/UI/Texture/Icons/77_32_34.png',
 'UI/Inflight/ActivateGate': 'res:/UI/Texture/Icons/44_32_39.png',
 'UI/Inflight/ActivateTraceGate': 'res:/UI/Texture/Icons/44_32_39.png',
 'UI/Common/Open': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/Inflight/StopMyShip': 'res:/UI/Texture/Icons/44_32_38.png',
 'UI/Inflight/StopMyCapsule': 'res:/UI/Texture/Icons/44_32_38.png',
 'UI/Inflight/HUDOptions/ReleaseControl': 'res:/UI/Texture/classes/RadialMenuActions/releaseStructureControl.png',
 'UI/Inflight/HUDOptions/BoardPreviousShipFromFlex': 'res:/UI/Texture/classes/RadialMenuActions/releaseStructureControl.png',
 'UI/Inflight/SetDestination': 'res:/UI/Texture/classes/RadialMenuActions/setDestination.png',
 'UI/Fitting/UseFittingService': 'res:/UI/Texture/classes/RadialMenuActions/useFittingService.png',
 'UI/Inflight/SetDefaultWarpWithinDistanceShort': 'res:/UI/Texture/classes/RadialMenuActions/setWarpDefault.png',
 'UI/Inflight/SetDefaultKeepAtRangeDistanceShort': 'res:/UI/Texture/classes/RadialMenuActions/setKeepRangeDefault.png',
 'UI/Inflight/SetDefaultOrbitDistanceShort': 'res:/UI/Texture/classes/RadialMenuActions/setOrbitDefault.png',
 'UI/Inflight/POS/ManageControlTower': 'res:/UI/Texture/classes/RadialMenuActions/manageStarbase.png',
 'UI/Menusvc/OpenHubManager': 'res:/UI/Texture/classes/RadialMenuActions/manageStarbase.png',
 'UI/FactionWarfare/IHub/OpenInfrastructureHubPanel': 'res:/UI/Texture/classes/RadialMenuActions/manageStarbase.png',
 'UI/Inflight/POS/AccessPOSStorage': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/Inflight/POS/AccessPOSCrystalStorage': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/Inflight/POS/AccessPOSAmmo': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/Inflight/POS/AccessPOSRefinery': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/Inflight/POS/AccessPOSCompression': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/Inflight/POS/AccessPOSVessels': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/Inflight/SpaceComponents/MicroJumpDriver/ActivateMicroJumpDrive': 'res:/UI/Texture/Icons/44_32_39.png',
 'UI/Inflight/Scanner/IngoreResult': 'res:/UI/Texture/classes/RadialMenuActions/ignore_results.png',
 'UI/Inflight/Scanner/IgnoreOtherResults': 'res:/UI/Texture/classes/RadialMenuActions/ignore_others_results.png',
 'UI/Inflight/Scanner/ProbeScanner': 'res:/UI/Texture/Icons/probe_scan.png',
 'UI/Inflight/SpaceComponents/ItemTrader/Access': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/Inflight/SpaceComponents/UnderConstruction/Access': 'res:/UI/Texture/Icons/44_32_35.png',
 'UI/Inflight/Scanner/DirectionalScan': 'res:/UI/Texture/Icons/d-scan.png',
 'UI/Fleet/FleetBroadcast/Commands/HealShield': 'res:/UI/Texture/Icons/44_32_52.png',
 'UI/Fleet/FleetBroadcast/Commands/HealArmor': 'res:/UI/Texture/Icons/44_32_53.png',
 'UI/Fleet/FleetBroadcast/Commands/HealCapacitor': 'res:/UI/Texture/Icons/44_32_54.png',
 'UI/Fleet/FleetBroadcast/Commands/BroadcastWarpTo': 'res:/UI/Texture/Icons/44_32_55.png',
 'UI/Fleet/FleetBroadcast/Commands/BroadcastAlignTo': 'res:/UI/Texture/Icons/44_32_57.png',
 'UI/Fleet/FleetBroadcast/Commands/BroadcastTarget': 'res:/UI/Texture/Icons/44_32_17.png',
 'UI/Inflight/WarpToMoonMiningPoint': 'res:/UI/Texture/Classes/Moonmining//warpToMiningPoint.png',
 'UI/Inflight/SpaceComponents/TowGameObjective/startTowing': 'res:/UI/Texture/icons/tow_icon.png',
 'UI/Inflight/SpaceComponents/TowGameObjective/stopTowing': 'res:/UI/Texture/icons/tow_icon_reset.png'}

def GetSpaceComponentPrimaryActionsForTypeID(typeID):
    componentNames = get_space_component_names_for_type(typeID)
    if CARGO_BAY in componentNames and not HasItemTrader(typeID) and not HasUnderConstructionComponent(typeID):
        return [SimpleRadialMenuAction(option1='UI/Commands/OpenCargo')]
    if HasMicroJumpDriverComponent(typeID):
        return [SimpleRadialMenuAction(option1='UI/Inflight/SpaceComponents/MicroJumpDriver/ActivateMicroJumpDrive')]
    if HasItemTrader(typeID):
        return [SimpleRadialMenuAction(option1='UI/Inflight/SpaceComponents/ItemTrader/Access')]
    if HasUnderConstructionComponent(typeID):
        return [SimpleRadialMenuAction(option1='UI/Inflight/SpaceComponents/UnderConstruction/Access')]
    if HasShipcasterComponent(typeID):
        return [SimpleRadialMenuAction(option1='UI/Inflight/JumpByShipcaster')]
    if HasTowGameObjectiveComponent(typeID):
        return [SimpleRadialMenuAction(option1='UI/Inflight/SpaceComponents/TowGameObjective/startTowing', option2='UI/Inflight/SpaceComponents/TowGameObjective/stopTowing')]


def GetSpaceComponentSecondaryActions(typeID):
    componentNames = get_space_component_names_for_type(typeID)
    actions = []
    if SCOOP_CLASS in componentNames:
        actions.append(SimpleRadialMenuAction(option1='UI/Inflight/ScoopToCargoHold'))
    if FITTING_CLASS in componentNames:
        actions.append(SimpleRadialMenuAction(option1='UI/Fitting/UseFittingService'))
    return actions


def GetObjectsActions(categoryID, groupID, typeID = None, itemID = None, bookmarkInfo = None, siteData = None, menuType = NORMAL_RADIAL_MENU, *args):
    secondaryActions = GetObjectsSecondaryActions(categoryID, groupID, typeID=typeID, itemID=itemID, bookmarkInfo=bookmarkInfo, siteData=siteData)
    generalActions = GetGeneralActions(hasExtraOptions=bool(secondaryActions), itemID=itemID, bookmarkInfo=bookmarkInfo, siteData=siteData, menuType=menuType)
    myActions = generalActions[:]
    if menuType == BROADCAST_RADIAL_MENU:
        return [SimpleRadialMenuAction()] + myActions
    if itemID == GetActiveShip():
        return myActions
    primaryComponentActions = GetSpaceComponentPrimaryActionsForTypeID(typeID)
    typeActions = primaryTypeActions.get(typeID, None)
    groupActions = primaryGroupActions.get(groupID, None)
    categoryActions = primaryCategoryActions.get(categoryID, None)
    siteActions = siteData.GetSiteActions() if siteData else None
    if primaryComponentActions:
        primaryActions = primaryComponentActions
    elif siteActions:
        primaryActions = siteActions
    else:
        primaryActions = typeActions or groupActions or categoryActions or [SimpleRadialMenuAction()]
    return primaryActions + myActions


def GetObjectsSecondaryActions(categoryID, groupID, typeID = None, itemID = None, bookmarkInfo = None, siteData = None, menuType = NORMAL_RADIAL_MENU):
    if menuType == BROADCAST_RADIAL_MENU:
        return []
    myActions = []
    categoryActions = secondaryCategoryActions.get(categoryID, None)
    if categoryActions:
        myActions += categoryActions
    groupActions = secondaryGroupActions.get(groupID, None)
    if groupActions:
        myActions += groupActions
    typeActions = secondaryTypeActions.get(typeID, None)
    if typeActions:
        myActions += typeActions
    if itemID == GetActiveShip() and session.solarsystemid:
        myActions += GetMyShipSpecialCaseSecondLevel(typeID=typeID, itemID=itemID)
    secondaryComponentActions = GetSpaceComponentSecondaryActions(typeID)
    if secondaryComponentActions:
        myActions += secondaryComponentActions
    if siteData:
        myActions.extend(siteData.GetSecondaryActions())
    if myActions:
        myActions = [SecondLevelRadialMenuAction(hasExtraOptions=False)] + myActions
    return myActions


def GetGeneralActions(hasExtraOptions = True, itemID = None, bookmarkInfo = None, siteData = None, menuType = NORMAL_RADIAL_MENU):
    if itemID == GetActiveShip() and menuType != BROADCAST_RADIAL_MENU:
        if itemID == session.structureid:
            topOption = SimpleRadialMenuAction(option1='UI/Inflight/HUDOptions/ReleaseControl', option2='UI/Inflight/HUDOptions/BoardPreviousShipFromFlex')
        else:
            topOption = SimpleRadialMenuAction(option1='UI/Inflight/StopMyShip', option2='UI/Inflight/StopMyCapsule')
        generalActions = [topOption,
         GetOrbitOption(itemID, isMyShip=True),
         SecondLevelRadialMenuAction(hasExtraOptions=hasExtraOptions),
         GetKeepAtRangeOption(itemID, isMyShip=True),
         SimpleRadialMenuAction(option1='UI/Commands/OpenCargoHold'),
         SimpleRadialMenuAction(),
         SimpleRadialMenuAction(option1='UI/Commands/ShowInfo'),
         GetWarpToOption(itemID, bookmarkInfo=None, isMyShip=True)]
    else:
        if siteData is not None:
            itemID = siteData.siteID
        if menuType == BROADCAST_RADIAL_MENU:
            generalActions = GetBroadcastMenuGeneralActions(itemID)
        else:
            generalActions = [GetOrbitOption(itemID),
             SecondLevelRadialMenuAction(hasExtraOptions=hasExtraOptions),
             GetKeepAtRangeOption(itemID),
             SimpleRadialMenuAction(option1='UI/Inflight/LockTarget', option2='UI/Inflight/UnlockTarget', option3Path='UI/Inflight/CancelLockTarget'),
             GetApproachOption(bookmarkInfo, siteData),
             SimpleRadialMenuAction(option1='UI/Commands/ShowInfo'),
             GetWarpToOption(itemID, bookmarkInfo, siteData=siteData)]
    return generalActions


def GetBroadcastMenuGeneralActions(itemID):
    generalActions = [GetBroadcastForShieldMenuAction(itemID),
     GetBroadcastForArmorMenuAction(itemID),
     GetBroadcastForCapacitorMenuAction(itemID),
     GetBroadcastTargetMenuAction(),
     GetBroadcastAlignToMenuAction(),
     SimpleRadialMenuAction(),
     GetBroadcastWarpToMenuAction()]
    return generalActions


def GetOrbitOption(itemID, isMyShip = False, *args):
    if isMyShip:
        return RangeRadialMenuAction(optionPath='UI/Inflight/SetDefaultOrbitDistanceShort', rangeList=GetOrbitRangesForDefault(), defaultRange=GetOrbitDefault(), callback=SetDefaultOrbit, funcArgs=itemID, alwaysAvailable=True)
    return RangeRadialMenuAction(optionPath='UI/Inflight/OrbitObject', rangeList=GetOrbitRanges(), defaultRange=GetOrbitDefault(), callback=Orbit, funcArgs=itemID)


def GetKeepAtRangeOption(itemID, isMyShip = False, *args):
    if isMyShip:
        return RangeRadialMenuAction(optionPath='UI/Inflight/SetDefaultKeepAtRangeDistanceShort', rangeList=GetKeepAtRangeRangesForDefault(), defaultRange=GetKeepAtRangeDefault(), callback=SetDefaultKeepAtRange, funcArgs=itemID, alwaysAvailable=True)
    return RangeRadialMenuAction(optionPath='UI/Inflight/Submenus/KeepAtRange', rangeList=GetKeepAtRangeRanges(), defaultRange=GetKeepAtRangeDefault(), callback=KeepAtRange, funcArgs=itemID)


def GetWarpToOption(itemID, bookmarkInfo, isMyShip = False, siteData = None, *args):
    if isMyShip:
        return RangeRadialMenuAction(optionPath='UI/Inflight/SetDefaultWarpWithinDistanceShort', rangeList=GetWarpToRanges(), defaultRange=GetWarpToDefault(), callback=SetDefaultWarpTo, funcArgs=itemID, alwaysAvailable=True)
    if bookmarkInfo:
        callback = WarpToBookmark
        funcArgs = bookmarkInfo
        optionPath2 = 'UI/Inflight/WarpToBookmark'
    elif siteData:
        callback = siteData.WarpToAction
        funcArgs = None
        optionPath2 = 'UI/Inflight/WarpToBookmark'
    else:
        optionPath2 = 'UI/Fleet/WarpToMemberSubmenuOption'
        callback = WarpTo
        funcArgs = itemID
    return RangeRadialMenuAction(optionPath='UI/Inflight/Submenus/WarpToWithin', option2Path=optionPath2, rangeList=GetWarpToRanges(), defaultRange=GetWarpToDefault(), callback=callback, funcArgs=funcArgs)


def GetApproachOption(bookmarkInfo, siteData, *args):
    if bookmarkInfo or siteData:
        option1 = 'UI/Inflight/AlignTo'
        option2 = 'UI/Inflight/ApproachLocationActionGroup'
    else:
        option1 = 'UI/Inflight/AlignTo'
        option2 = 'UI/Inflight/ApproachObject'
    return SimpleRadialMenuAction(option1=option1, option2=option2)


def GetMyShipSpecialCaseSecondLevel(typeID = None, itemID = None, *args):
    secondLevelOptions = []
    if session.solarsystemid and not session.structureid:
        func = GetMenuService().Bookmark
        funcArgs = (itemID, typeID, session.solarsystemid)
        secondLevelOptions += [SimpleRadialMenuAction(option1='UI/Inflight/BookmarkLocation', alwaysAvailable=True, func=func, funcArgs=funcArgs)]
    return secondLevelOptions


def FindRadialMenuOptions(slimItem = None, itemID = None, typeID = None, primaryActions = True, bookmarkInfo = None, manyItemsData = None, siteData = None, menuType = 1):
    filterList = []
    if not bookmarkInfo and not manyItemsData and not slimItem and itemID:
        slimItem = GetBallparkRecord(itemID)
    menuSvc = GetMenuService()
    if manyItemsData:
        allMenuOptions = manyItemsData.menuFunction(manyItemsData.itemData)
    elif bookmarkInfo is not None:
        allMenuOptions = menuSvc.BookmarkMenu(bookmarkInfo)
        typeID = bookmarkInfo.typeID
    elif slimItem:
        allMenuOptions = menuSvc.UnmergedCelestialMenu(slimItem)
        typeID = slimItem.typeID
        filterList.append('UI/Inflight/SetDestination')
    elif siteData is not None:
        allMenuOptions = siteData.GetMenu()
        if typeID is None:
            typeID = getattr(siteData, 'typeID', None)
    elif itemID and IsCharacter(itemID):
        allMenuOptions = menuSvc.CharacterMenu(itemID) + menuSvc.FleetMenu(itemID)
    elif typeID is not None:
        allMenuOptions = menuSvc.GetMenuFromItemIDTypeID(itemID, typeID)
    else:
        allMenuOptions = []
    if typeID is not None:
        categoryID = evetypes.GetCategoryID(typeID)
        groupID = evetypes.GetGroupID(typeID)
    else:
        categoryID = None
        groupID = None
    if primaryActions:
        allWantedMenuOptions = GetObjectsActions(categoryID, groupID, typeID, itemID, bookmarkInfo=bookmarkInfo, siteData=siteData, menuType=menuType)
    else:
        allWantedMenuOptions = GetObjectsSecondaryActions(categoryID, groupID, typeID, itemID, bookmarkInfo, siteData=siteData, menuType=menuType)
    return PrepareRadialMenuOptions(allMenuOptions, allWantedMenuOptions, filterList)


def AddOption(optionLabel, menuOption, oneClickMenuOptions, activeSingleOptions):
    menuOption.activeOption = optionLabel
    menuOption.labelArgs = oneClickMenuOptions[optionLabel].labelArgs
    callbackInfo = oneClickMenuOptions[optionLabel].callbackInfo
    menuOption.func = callbackInfo[0]
    if len(callbackInfo) > 1:
        if CaptionIsInMultiFunctions(optionLabel):
            menuOption.funcArgs = (callbackInfo[1],)
        else:
            menuOption.funcArgs = callbackInfo[1]
    else:
        menuOption.funcArgs = None
    activeSingleOptions[optionLabel] = menuOption


def PrepareRadialMenuOptions(allMenuOptions, allWantedMenuOptions, filterList, *args):
    oneClickMenuOptions = {}
    otherMenuOptions = set()
    allMenuOptionsExpanded = _GetAllMenuOptionsWithExpanded(allMenuOptions, filterList)
    for eachMenuEntry in allMenuOptionsExpanded:
        actionName, labelArgs = GetActionNameAndArgs(eachMenuEntry)
        if isinstance(eachMenuEntry, BaseMenuEntryData):
            if eachMenuEntry.HasSubMenuData() or not eachMenuEntry.IsEnabled():
                otherMenuOptions.add(actionName)
            elif hasattr(eachMenuEntry, 'func'):
                oneClickMenuOptions[actionName] = KeyVal(callbackInfo=(eachMenuEntry.func,), labelArgs=labelArgs)
        elif isinstance(eachMenuEntry[1], (types.MethodType, types.LambdaType)):
            oneClickMenuOptions[actionName] = KeyVal(callbackInfo=eachMenuEntry[1:], labelArgs=labelArgs)
        else:
            otherMenuOptions.add(actionName)

    activeSingleOptions = {}
    inactiveSingleOptions = set()
    activeRangeOptions = {}
    inactiveRangeOptions = set()
    for menuOption in allWantedMenuOptions[:]:
        option1 = menuOption.option1Path
        option2 = menuOption.Get('option2Path', None)
        option3 = menuOption.Get('option3Path', None)
        option4 = menuOption.Get('option4Path', None)
        if isinstance(menuOption, SimpleRadialMenuAction):
            if menuOption.get('forcedInactive', False):
                inactiveSingleOptions.add(option1)
            elif option1 in oneClickMenuOptions:
                AddOption(option1, menuOption, oneClickMenuOptions, activeSingleOptions)
            elif _IsOptionAvailable(oneClickMenuOptions, option2):
                AddOption(option2, menuOption, oneClickMenuOptions, activeSingleOptions)
            elif _IsOptionAvailable(oneClickMenuOptions, option3):
                AddOption(option3, menuOption, oneClickMenuOptions, activeSingleOptions)
            elif _IsOptionAvailable(oneClickMenuOptions, option4):
                AddOption(option4, menuOption, oneClickMenuOptions, activeSingleOptions)
            elif menuOption.get('alwaysAvailable', False):
                menuOption.activeOption = option1
                activeSingleOptions[option1] = menuOption
            else:
                inactiveSingleOptions.add(option1)
        elif isinstance(menuOption, RangeRadialMenuAction):
            if option1 in otherMenuOptions or menuOption.get('alwaysAvailable', False):
                activeRangeOptions[option1] = menuOption
            elif option2 in otherMenuOptions:
                menuOption.activeOption = option2
                activeRangeOptions[option2] = menuOption
            elif option2 in oneClickMenuOptions:
                newMenuOption = SimpleRadialMenuAction(option1=option1, option2=option2)
                AddOption(option2, newMenuOption, oneClickMenuOptions, activeSingleOptions)
                idx = allWantedMenuOptions.index(menuOption)
                allWantedMenuOptions[idx] = newMenuOption
            else:
                inactiveRangeOptions.add(option1)

    optionsInfo = RadialMenuOptionsInfo(allWantedMenuOptions=allWantedMenuOptions, activeSingleOptions=activeSingleOptions, inactiveSingleOptions=inactiveSingleOptions, activeRangeOptions=activeRangeOptions, inactiveRangeOptions=inactiveRangeOptions)
    return optionsInfo


def _IsOptionAvailable(oneClickMenuOptions, option):
    if option is None:
        return False
    return option in oneClickMenuOptions


def _GetAllMenuOptionsWithExpanded(allMenuOptions, filterList):
    allMenuOptionsExpanded = OrderedDict()
    subMenuOptions = []
    for eachMenuEntry in allMenuOptions:
        if eachMenuEntry is None:
            continue
        actionName, labelArgs = GetActionNameAndArgs(eachMenuEntry)
        if actionName in filterList:
            continue
        allMenuOptionsExpanded[actionName] = eachMenuEntry
        if actionName in subMenusToExpand:
            for eachSubOption in eachMenuEntry[1]:
                subMenuOptions.append(eachSubOption)

    for eachSubOption in subMenuOptions:
        actionName, labelArgs = GetActionNameAndArgs(eachSubOption)
        if actionName not in allMenuOptionsExpanded and actionName not in filterList:
            allMenuOptionsExpanded[actionName] = eachSubOption

    return allMenuOptionsExpanded.values()


def GetActionNameAndArgs(eachMenuEntry):
    if isinstance(eachMenuEntry, BaseMenuEntryData):
        menuLabel = eachMenuEntry.GetMenuLabel()
    else:
        menuLabel = eachMenuEntry[0]
    if isinstance(menuLabel, (MenuLabel, list)):
        actionName = menuLabel[0]
        labelArgs = menuLabel[1]
    else:
        actionName = menuLabel
        labelArgs = {}
    return (actionName, labelArgs)


def GetIconPath(labelPath):
    return iconDict.get(labelPath, None)


def KeepAtRange(itemID, distance, percOfAllRange):
    movementFunctions__KeepAtRange(itemID, distance)


def GetKeepAtRangeRanges():
    return GetRanges(minValue=500, maxValue=30000)


def GetKeepAtRangeRangesForDefault():
    return GetRanges(minValue=50, maxValue=100000)


def GetKeepAtRangeDefault():
    return GetMenuService().GetDefaultActionDistance('KeepAtRange')


def Orbit(itemID, distance, percOfAllRange):
    movementFunctions__Orbit(itemID, distance)


def GetOrbitRanges():
    return GetRanges(minValue=500, maxValue=30000)


def GetOrbitRangesForDefault():
    return GetRanges(minValue=500, maxValue=100000)


def GetOrbitDefault():
    return GetMenuService().GetDefaultActionDistance('Orbit')


def WarpTo(itemID, distance, percOfAllRange):
    if IsCharacter(itemID):
        GetMenuService().WarpToMember(charID=itemID, warpRange=distance)
    else:
        movementFunctions__WarpToItem(itemID=itemID, warpRange=distance)


def WarpToBookmark(bookmarkInfo, distance, percOfAllRange):
    movementFunctions__WarpToBookmark(bookmark=bookmarkInfo, warpRange=distance)


def GetWarpToRanges():
    return movementFunctions__GetWarpToRanges()


def GetWarpToDefault():
    return GetMenuService().GetDefaultActionDistance('WarpTo')


def GetRanges(minValue = 250, maxValue = 30000):
    newValue = minValue
    rangeList = []
    while newValue <= maxValue:
        rangeList.append(newValue)
        if newValue < 500:
            interval = 150
        elif newValue < 5000:
            interval = 250
        elif newValue < 8000:
            interval = 500
        elif newValue < 30000:
            interval = 1000
        else:
            interval = 5000
        newValue += interval

    return rangeList


def SetDefaultKeepAtRange(itemID, distance, percOfAllRange):
    defaultRangeUtils.SetDefaultKeepAtRangeDist(distance)


def SetDefaultOrbit(itemID, distance, percOfAllRange):
    defaultRangeUtils.SetDefaultOrbitDist(distance)


def SetDefaultWarpTo(itemID, distance, percOfAllRange):
    defaultRangeUtils.SetDefaultWarpToDist(distance)


def IsRadialMenuButtonActive():
    actionmenuBtn = settings.user.ui.Get('actionmenuBtn', uiconst.MOUSELEFT)
    if not isinstance(actionmenuBtn, int):
        actionmenuBtn = uiconst.MOUSELEFT
    myBtn = actionmenuBtn
    menuType = NORMAL_RADIAL_MENU
    actionmenuBtnState = uicore.uilib.GetMouseButtonState(actionmenuBtn)
    if not actionmenuBtnState:
        myBtn = GetSingleMouseBtnBroadcastRadialMenu()
        menuType = BROADCAST_RADIAL_MENU
        if not myBtn or not uicore.uilib.GetMouseButtonState(myBtn):
            return None
    if AreOtherMouseBtnsDown(myBtn):
        return None
    if DungeonEditor.IsOpen():
        return None
    return menuType


def AreOtherMouseBtnsDown(myBtn):
    for eachBtn in MOUSEBUTTONS:
        if eachBtn == myBtn:
            continue
        btnDown = uicore.uilib.GetMouseButtonState(eachBtn)
        if btnDown:
            return True

    return False


def GetSingleMouseBtnBroadcastRadialMenu():
    if settings.user.cmd.customCmds:
        broadcastRm = settings.user.cmd.customCmds.get('CmdOpenBroadcastRadialMenu', None)
    else:
        broadcastRm = None
    if broadcastRm and len(broadcastRm) == 1:
        mBtn = mouseBtnMap.get(broadcastRm[0], None)
        if mBtn in MOUSEBUTTONS:
            return mBtn


mouseBtnMap = {uiconst.VK_MBUTTON: uiconst.MOUSEMIDDLE,
 uiconst.VK_XBUTTON1: uiconst.MOUSEXBUTTON1,
 uiconst.VK_XBUTTON2: uiconst.MOUSEXBUTTON2}
