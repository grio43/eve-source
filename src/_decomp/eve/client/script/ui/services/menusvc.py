#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\menusvc.py
import sys
import types
import random
import eveformat
import eveicon
import utillib
from stargate.client.localGates import FindLocalStargate, FindLocalJumpGateForDestinationPath
from eve.common.script.sys.idCheckers import IsSkyhook
from shipcaster.shipcasterConst import SHIPCASTER_PROXIMITY_TO_JUMP
from shipcaster.shipcasterUtil import GetTargetForShipcaster, GetFailureTextAndDisabledOption
from carbon.common.script.net.moniker import Moniker
from carbon.common.script.sys.serviceConst import ROLE_CONTENT, ROLE_GML, ROLE_LEGIONEER, ROLE_PROGRAMMER, ROLE_SPAWN, ROLE_WORLDMOD
from carbon.common.script.sys.sessions import ThrottlePerSecond
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.inflight.overview import overviewMenuUtil
from eve.client.script.ui.services.menuEntries import DroneEngageTargetMenuEntryData, WarpToMenuEntryData, KeepAtRangeMenuEntryData, OrbitMenuEntryData
from eve.client.script.ui.services.menuMerge import MergeMenus
from eve.client.script.ui.shared.fleet.fleetBroadcastConst import iconsByBroadcastType
from evefleet import BROADCAST_TRAVEL_TO, BROADCAST_JUMP_TO, BROADCAST_ALIGN_TO, BROADCAST_WARP_TO, BROADCAST_TARGET, BROADCAST_REP_TARGET
from eveclientqatools.shaderDebugger import ShaderDebugger
from eveclientqatools.textureViewer import TextureWindow
from itemcompression.client.ui.compression_window import DirectlyCompressInSpace, DirectlyCompressInStructure
from itemcompression.client.gasDecompression import decompress_gas
from itemcompression.client.ui.decompression_window import GasDecompressionWindow
from itemcompression.client.itemCompression import CompressItemInSpace, CompressItemInStructure
from eve.client.script.ui.inflight.capitalnavigation import CapitalNav
from eve.client.script.ui.inflight.facilityTaxWindow import FacilityTaxWindow
from eve.client.script.ui.shared.fittingScreen.tryFit import GhostFitShip
from eve.client.script.ui.shared.inventory.invWindow import Inventory
from eve.client.script.ui.shared.neocom.corporation.memberDetails import OpenMemberDetails
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.client.script.util import eveMisc
import evefleet.client
from eve.devtools.script.svc_dgmattr import AttributeInspector
from evefleet.client.util import GetSelectedFormationName
from eveservices.xmppchat import GetChatService
import inventorycommon.const as invconst
from eve.client.script.parklife import states
from evestations.data import get_station_services_for_operation
from menu import CONTAINERGROUPS, MenuLabel, MenuList
from eve.client.script.ui.shared.fitting.fittingUtil import TryFit
from eve.client.script.ui.shared.industry.industryWnd import Industry
from eve.client.script.ui.shared.mapView.mapViewUtil import OpenMap
from eve.client.script.ui.shared.activateMultiTraining import ActivateMultiTraining
from eve.client.script.ui.shared.sov.sovHub.cleanupSovSystemWindow import open_sov_system_cleanup
from eve.common.script.util import industryCommon
from eve.common.script.net import eveMoniker
import carbon.common.script.util.format as fmtutil
import evetypes
from eveuniverse.solar_systems import GetLightYearDistance
from globalConfig.getFunctions import GetMaxShipsToFit, AllowCharacterLogoff
from inventorycommon.const import compareCategories
from inventorycommon.util import IsShipFittable
from moonmining.const import MOON_BEACONID_NAME
from shipfitting.multiBuyUtil import BuyMultipleTypes
from eve.client.script.ui.services.menuSvcExtras import marketMenu
from eve.client.script.ui.structure.structuremenu import GetStructureMenu
from eveclientqatools.stargateDebugger import StargateDebuggerViewController
from eveclientqatools.modelstatedebugger import ModelStateDebuggerController
from eveclientqatools.audio import AudioGmMenu
from eve.client.script.ui.util import uix, utilWindows
import uthread
import log
import blue
from eve.common.script.net import eveMoniker as moniker
import destiny
from eve.client.script.parklife import states as state
import carbonui.const as uiconst
import eve.common.script.mgt.posConst as pos
import localization
from eve.client.script.environment import invControllers as invCtrl
import telemetry
import eve.client.script.ui.util.defaultRangeUtils as defaultRangeUtils
from eve.common.lib import appConst as const, appConst
import evegraphics.settings as gfxsettings
from eveexceptions import UserError
from shipprogression.boarding_moment import can_play_boarding_moment
from sovereignty.mercenaryden.client.checkers import is_mercenary_den_close_enough_to_configure
from spacecomponents.common.helper import HasCargoBayComponent, HasBehaviorComponent, HasDeployComponent, HasMercenaryDenComponent
from spacecomponents.client.components import cargobay, behavior, microJumpDriver, linkWithShip, towGameObjective
from spacecomponents.client.qa.utils import get_qa_menu as get_space_components_menu
from spacecomponents.client.ui.link_with_ship import GetLinkButtonLabelPath
from spacecomponents.common.componentConst import ITEM_TRADER, UNDER_CONSTRUCTION
from eve.client.script.ui.services.menuSvcExtras import menuFunctions, modelDebugFunctions, movementFunctions, invItemFunctions, droneFunctions, devFunctions, openFunctions
from carbon.common.script.sys.service import Service
from carbonui.control.contextMenu.menuConst import DISABLED_ENTRY0
from carbonui.control.contextMenu.menuUtil import CloseContextMenus
import inventorycommon.typeHelpers
from eve.common.script.sys.eveCfg import InShipInSpace, IsControllingStructure
from eve.common.script.sys import eveCfg, idCheckers
import fsdBuiltData.common.graphicIDs as fsdGraphicIDs
from menucheckers import ItemChecker, SessionChecker, MapChecker, BookmarkChecker, CelestialChecker, DroneChecker, CharacterChecker, FleetMemberChecker
from carbonui.uicore import uicore
from eveprefs import prefs, boot
from eveservices.menu import StartMenuService
from itertoolsext import Bundle
import homestation.client
import expertSystems.client
from eve.client.script.ui.control import eveMenu
from journey.journey_messanger import JourneyMessenger
CELESTIAL_MENU_CATEGORIES = (const.categoryCelestial,
 const.categoryStarbase,
 const.categoryStation,
 const.categoryShip,
 const.categoryEntity,
 const.categoryDrone,
 const.categoryAsteroid,
 const.categoryDeployable,
 const.categorySovereigntyStructure,
 const.categoryStructure,
 const.categoryFighter,
 const.categoryOrbital)
DEFAULT_INTERACTION_RANGE = 2500

class MenuSvc(Service):
    __guid__ = 'svc.menu'
    __update_on_reload__ = 0
    __dependencies__ = ['pwn',
     'godma',
     'michelle',
     'invCache',
     'crimewatchSvc',
     'clientPathfinderService',
     'securitySvc',
     'fighters']
    __startupdependencies__ = ['settings']
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self):
        super(MenuSvc, self).__init__()
        self.sessionChecker = None
        self.expandTimer = None
        self.lastAlignTargetID = None
        self.lastAlignedToBookmark = None

    def Run(self, memStream = None):
        uicore.uilib.RegisterForTriuiEvents([uiconst.UI_MOUSEDOWN], self.OnGlobalMouseDown)
        self.sessionChecker = None
        self.expandTimer = None

    @staticmethod
    def OnGlobalMouseDown(obj, *args):
        if not obj.IsUnder(uicore.layer.menu):
            CloseContextMenus()
        return True

    def Stop(self, *args):
        self.expandTimer = None

    def OnSessionChanged(self, isremote, session, change):
        self.expandTimer = None
        self.sessionChecker = None
        CloseContextMenus()

    @staticmethod
    def TryExpandActionMenu(itemID, clickedObject, *args, **kwargs):
        sm.GetService('radialmenu').TryExpandActionMenu(itemID, clickedObject, *args, **kwargs)

    def MapMenu(self, itemID):
        if idCheckers.IsSolarSystem(itemID) or idCheckers.IsStation(itemID) or sm.GetService('structureDirectory').GetStructureInfo(itemID):
            return self._MapMenu(itemID)
        return MenuList()

    def _MapMenu(self, itemID):
        menuEntries = MenuList()
        starmap = sm.GetService('starmap')
        checker = MapChecker(itemID)
        if checker.OfferSetDestination():
            menuEntries.append(MenuEntryData(MenuLabel('UI/Inflight/SetDestination'), lambda : starmap.SetWaypoint(itemID, True)))
        if checker.OfferRemoveWaypoint():
            menuEntries += [[MenuLabel('UI/Inflight/RemoveWaypoint'), starmap.ClearWaypoints, (itemID,)]]
        else:
            menuEntries += [[MenuLabel('UI/Inflight/AddWaypoint'), starmap.SetWaypoint, (itemID,)]]
        _, _, constellationID, _, _ = sm.StartService('map').GetParentLocationID(itemID)
        menuEntries += [[MenuLabel('UI/Inflight/BookmarkLocation'), self.Bookmark, (itemID, const.typeSolarSystem, constellationID)]]
        return menuEntries

    def InvItemMenu(self, invItems, viewOnly = 0, unparsed = 0):
        if type(invItems) == list:
            menus = []
            allInvItems = [ items[0] for items in invItems ]
            for invItem, viewOnly, _ in invItems:
                menus.append(self._InvItemMenu(invItem, viewOnly, unparsed, allInvItems=allInvItems))

            return MergeMenus(menus)
        else:
            return MergeMenus([self._InvItemMenu(invItems, viewOnly, unparsed)])

    def _InvItemMenu(self, invItem, viewOnly, unparsed = 0, allInvItems = None):
        stationOperation = sm.GetService('station').stationItem.operationID if session.stationid else None
        stationServices = get_station_services_for_operation(stationOperation) or []
        checkViewOnly = bool(viewOnly)
        isMultiSelection = allInvItems and len(allInvItems) > 1
        spansMultipleLocations = isMultiSelection and any((allInvItems[0].locationID != item.locationID for item in allInvItems))
        if self.sessionChecker is None:
            self.sessionChecker = SessionChecker(session, sm)
        item = ItemChecker(invItem, self.sessionChecker)
        menuEntries = MenuList()
        if item.OfferSplitStack():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/SplitStack'), self.SplitStack, [invItem]]]
        if item.OfferRedeemCurrency():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/RedeemCurrency'), self.RedeemCurrency, (invItem, invItem.stacksize)]]
        if item.OfferAssembleContainer():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/AssembleContainer'), self.AssembleContainer, [invItem]]]
        if item.OfferLockItem():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/LockItem'), self.ALSCLock, [invItem]]]
        if item.OfferUnlockItem():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/UnlockItem'), self.ALSCUnlock, [invItem]]]
        if item.OfferProposeBlueprintLockdownVote():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/ProposeBlueprintLockdownVote'), self.LockDownBlueprint, (invItem,)]]
        if item.OfferProposeBlueprintUnlockVote():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/ProposeBlueprintUnlockVote'), self.UnlockBlueprint, (invItem,)]]
        if item.OfferRepairItems():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/GetRepairQuote'), openFunctions.RepairItems, [invItem]]]
        if item.OfferViewTypesMarketDetails():
            self._AddMarketDetailsOption(menuEntries, invItem.typeID)
        if item.OfferSellThisItem():
            if item.IsPlexVaultItem():
                menuEntries.append(MenuEntryData(MenuLabel('UI/Inventory/ItemActions/SellThisItem'), self.SellPlex, texturePath=eveicon.isk))
            elif isMultiSelection:
                menuEntries.append(MenuEntryData(MenuLabel('UI/Inventory/ItemActions/MultiSell'), lambda : self.SellItems(allInvItems), texturePath=eveicon.isk, typeID=invItem.typeID, internalName='Sell', quantity=len(allInvItems)))
            else:
                menuEntries.append(MenuEntryData(MenuLabel('UI/Inventory/ItemActions/SellThisItem'), lambda : self.SellItems([invItem]), texturePath=eveicon.isk, typeID=invItem.typeID, internalName='Sell'))
        if item.OfferBuyThisType():
            if isMultiSelection:
                menuEntries.append(MenuEntryData(MenuLabel('UI/Market/MarketQuote/BuyAll'), lambda : BuyMultipleTypes(allInvItems), quantity=len(allInvItems), internalName='BuyAll'))
            else:
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/BuyThisType'), self.QuickBuy, (invItem.typeID,)]]
        if item.OfferViewContents():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/ViewContents'), self.GetContainerContents, [invItem, item.GetLocationIDOfItemInCorpOffice()]]]
        if item.OfferConfigureShipCloneFacility():
            menuEntries += [[MenuLabel('UI/Commands/ConfigureShipCloneFacility'), self.ShipCloneConfig, (invItem.itemID,)]]
        menuEntries.extend(openFunctions.GetOpenShipHoldMenus(item))
        if not spansMultipleLocations:
            if item.OfferCreateContract():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/CreateContract'), self.QuickContract, [invItem]]]
            if item.OfferDeliverTo():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/DeliverTo'), self.DeliverToStructure, [invItem]]]
        if item.OfferRepackage():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/Repackage'), self.RepackageItems, [invItem]]]
        if item.OfferUndock():
            label = 'UI/Commands/UndockFromStation' if self.sessionChecker.IsPilotInStation() else 'UI/Commands/UndockFromStructure'
            menuEntries += [[MenuLabel(label), self.ExitDockableLocation, ()]]
        if item.IsCompressibleType():
            if item.OfferCompressInSpace():
                menuEntries += [[MenuLabel('UI/Commands/Compress'), DirectlyCompressInSpace, [invItem]]]
            elif item.OfferCompressInStructure():
                menuEntries += [[MenuLabel('UI/Commands/Compress'), DirectlyCompressInStructure, [invItem]]]
        if item.OfferDecompressGas():
            menuEntries += [[MenuLabel('UI/Commands/DecompressGas'), GasDecompressionWindow.AddItemOrOpenWindow, (invItem,)]]
        if item.OfferDeliverToCorp():
            divisionNames = sm.GetService('corp').GetDivisionNames()
            divisions = []
            for flagID in const.flagCorpSAGs:
                divisionID = const.corpDivisionsByFlag[flagID]
                divisionName = divisionNames[divisionID + 1]
                divisions.append((flagID, divisionName))

            deliverToCorpHangarMenu = [ (divisionName, self.DeliverToCorpHangarFolder, [[(invItem, flagID)]]) for flagID, divisionName in divisions ]
            deliverToMenu = [[MenuLabel('UI/Corporations/CorpHangarSubmenu'), deliverToCorpHangarMenu],
             [MenuLabel('UI/Corporations/CorporationWindow/Members/CorpMember'), self.DeliverToCorpMember, [invItem]],
             None,
             [MenuLabel('UI/Corporations/CorporationWindow/Members/Myself', {'char': session.charid}), self.DeliverToSelf, [invItem]]]
            if unparsed:
                menuEntries += [None]
            menuEntries += [[MenuLabel('UI/Corporations/DeliverCorpStuffTo'), deliverToMenu]]
        if item.OfferTrashIt():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/TrashIt'), self.TrashInvItems, [invItem]]]
        if item.OfferConfigureOrbitalPoco() or item.OfferConfigureOrbitalSkyhook():
            menuEntries += [[MenuLabel('UI/DustLink/ConfigureOrbital'), self.ConfigureOrbital, (invItem,)]]
        if item.OfferCompareButton():
            menuEntries += [(MenuLabel('UI/Compare/CompareButton'), self.CompareType, (invItem.typeID, invItem.itemID))]
        if item.OfferActivateShipSkinLicense():
            if isMultiSelection:
                menuEntries += [[MenuLabel('UI/Commands/ActivateSkinLicense'), menuFunctions.ActivateShipSkinLicense, [(invItem.itemID, invItem.typeID)]]]
            else:
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/SkinSubmenu'), ('isDynamic', self.GetSkinLicenseMenu, (invItem, item))]]
        if item.OfferConsumeShipSkinDesignComponent():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/ConsumeSkinDesignComponentItem'), menuFunctions.ConsumeSkinDesignComponent, [(invItem.itemID, invItem.typeID, invItem.stacksize)]]]
        if item.IsDecodable():
            menuEntries += [[MenuLabel('UI/Commands/DecodeDataStream'), menuFunctions.DecryptItem, [invItem.itemID, invItem.typeID]]]
        if not checkViewOnly:
            if item.OfferLaunchDrones():
                menuEntries.append(MenuEntryData(MenuLabel('UI/Drones/LaunchDrone', {'numDrones': 1}), lambda : self.LaunchDrones([invItem])))
            elif item.failure_label:
                menuEntries.reasonsWhyNotAvailable['UI/Drones/LaunchDrones'] = self.GetUnavailableText(item)
            if item.OfferTrainNowToLevel1():
                menuEntries += [[MenuLabel('UI/SkillQueue/AddSkillMenu/TrainNowToLevel1'), self.TrainNow, [invItem]]]
            if item.OfferInjectSkill():
                menuEntries.append(MenuEntryData(MenuLabel('UI/SkillQueue/InjectSkill'), lambda : self.InjectSkillIntoBrain([invItem]), texturePath=eveicon.person))
            if item.OfferConsumeBooster():
                menuEntries.append(MenuEntryData(MenuLabel('UI/Inventory/ItemActions/ConsumeBooster'), lambda : self.ConsumeBooster([invItem]), texturePath=eveicon.person))
            if item.OfferPlugInImplant():
                menuEntries.append(MenuEntryData(MenuLabel('UI/Inventory/ItemActions/PlugInImplant'), lambda : self.PlugInImplant([invItem]), texturePath=eveicon.person))
            if item.OfferAssembleShip():
                menuEntries.append(MenuEntryData(MenuLabel('UI/Inventory/ItemActions/AssembleShip'), lambda : self.AssembleShip([invItem]), texturePath=eveicon.assemble_ship))
                if self.sessionChecker.IsPilotDocked():
                    menuEntries += [[MenuLabel('UI/Fitting/FittingWindow/FittingManagement/OpenMultifit'), ('isDynamic', self.GetFitMenu, [invItem, invItem.typeID])]]
            if not isMultiSelection and item.OfferAssembleAndBoardShip():
                menuEntries.append(MenuEntryData(MenuLabel('UI/Inflight/BoardShip'), lambda : self.AssembleAndBoardShip(invItem), texturePath=eveicon.board))
            if item.OfferReprocess(stationServices):
                if item.session.IsPilotDocked():
                    menuEntries += [[MenuLabel('UI/Inventory/ItemActions/Reprocess'), invItemFunctions.Reprocess, [invItem]]]
                else:
                    refineryID = item.GetInSpaceLocationItem().itemID
                    menuEntries += [[MenuLabel('UI/Inventory/ItemActions/Reprocess'), lambda itemIDasList: self.invCache.GetInventoryFromId(refineryID).Reprocess(itemIDasList[0]), [invItem.itemID]]]
            if item.OfferOpenContainer():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/OpenContainer'), openFunctions.OpenCargoContainer, [invItem]]]
            if item.OfferBreakContract():
                menuEntries += [[MenuLabel('UI/Contracts/BreakContract'), self.Break, [invItem]]]
            if item.OfferDeliverCourierPackage():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/ContractsDelieverCourierPackage'), self.DeliverCourierContract, [invItem]]]
            if item.OfferFitToActiveShip():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/FitToActiveShip'), TryFit, [invItem]]]
            if item.OfferMoveToDroneBay():
                menuEntries += [[MenuLabel('UI/Drones/MoveToDroneBay'), self.FitDrone, [invItem]]]
            if item.OfferLaunchForCorp():
                if HasDeployComponent(invItem.typeID):
                    menuEntries.append(MenuEntryData(MenuLabel('UI/Inventory/ItemActions/LaunchForCorp'), lambda : eveMisc.LaunchFromShip([invItem], maxQty=1)))
                else:
                    deployFunction = self.LaunchForCorp
                    if item.IsStructure():
                        deployFunction = self.DeployStructure
                    menuEntries.append([MenuLabel('UI/Inventory/ItemActions/LaunchForCorp'), deployFunction, [invItem]])
            if item.OfferLaunchForSelf():
                if HasDeployComponent(invItem.typeID):
                    menuEntries.append(MenuEntryData(MenuLabel('UI/Inventory/ItemActions/LaunchForSelf'), lambda : eveMisc.LaunchFromShip([invItem], maxQty=1)))
                else:
                    menuEntries.append([MenuLabel('UI/Inventory/ItemActions/LaunchForSelf'), self.LaunchForSelf, [invItem]])
            if item.OfferJettison():
                if item.session.IsPilotControllingUndockableStructure():
                    menuEntries += [[MenuLabel('UI/Inventory/ItemActions/Jettison'), self.JettisonFuel, [invItem]]]
                else:
                    menuEntries += [[MenuLabel('UI/Inventory/ItemActions/Jettison'), self.Jettison, [invItem]]]
            if item.OfferLaunchForSelf_Container():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/LaunchForSelf'), self.Jettison, [invItem]]]
            if item.OfferLeaveShip():
                if self.sessionChecker.IsPilotInStation():
                    if can_play_boarding_moment(invItem.typeID):
                        menuEntries += [[MenuLabel('UI/ShipProgression/TriggerBoardingMoment'), self.DoBoardingMoment]]
                    menuEntries += [[MenuLabel('UI/Inventory/ItemActions/LeaveShip'), self.LeaveShip, (invItem,)]]
                elif self.sessionChecker.IsPilotInStructure():
                    if can_play_boarding_moment(invItem.typeID) and sm.GetService('viewState').IsPrimaryViewActive(ViewState.Hangar):
                        menuEntries += [[MenuLabel('UI/ShipProgression/TriggerBoardingMoment'), self.DoBoardingMoment]]
                    menuEntries += [[MenuLabel('UI/Inventory/ItemActions/LeaveShip'), sm.GetService('structureDocking').LeaveShip, (invItem.itemID,)]]
        if unparsed:
            menuEntries += [None]
        if not isMultiSelection:
            menuEntries += [[MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (invItem.typeID,
               invItem.itemID,
               0,
               invItem,
               None)]]
            if item.OfferReverseRedeem():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/ReverseRedeem'), sm.GetService('redeem').ReverseRedeem, (invItem,)]]
            elif item.OfferActivateCharacterReSculptToken():
                menuEntries += [[MenuLabel('UI/Commands/ActivateCharacterReSculptToken'), self.ActivateCharacterReSculpt, (invItem.itemID,)]]
            elif item.OfferActivateMultiTraining():
                menuEntries += [[MenuLabel('UI/Commands/ActivateMultiTrainingToken'), self.ActivateMultiTraining, (invItem.itemID,)]]
            elif item.OfferActivateSkillExtractor():
                menuEntries += [[MenuLabel('UI/Commands/ActivateSkillExtractor'), self.ActivateSkillExtractor, (invItem,)]]
            elif item.OfferActivateSkillInjector():
                menuEntries += self.GetActivateSkillInjectorMenuEntry(invItem)
            elif item.OfferOpenCrate():
                menuEntries += [[localization.GetByLabel('UI/Crate/MenuCommandOpenCrate', typeID=invItem.typeID), self.OpenCrate, (invItem.typeID, invItem.itemID, invItem.stacksize)]]
            if item.OfferSplitSkillInjector():
                menuEntries += [[MenuLabel('UI/Commands/SplitInjector', {'quantity': invItem.stacksize}), menuFunctions.SplitSkillInjector, (invItem.itemID, invItem.stacksize)]]
            if item.OfferCombineSkillInjector():
                menuEntries += [[MenuLabel('UI/Commands/CombineInjector'), menuFunctions.CombineSkillInjector, (invItem.itemID, invItem.stacksize)]]
            if item.OfferCraftDynamicItem():
                menuEntries += [[MenuLabel('UI/Commands/CraftDynamicItem', {'mutator': invItem.typeID}), self.CraftDynamicItem, (invItem,)]]
            if item.OfferActivateAbyssalKey():
                menuEntries += [[MenuLabel('UI/Commands/ActivateAbyssalKey', {'item': invItem.typeID}), self.ActivateAbyssalKey, (invItem,)]]
            if item.OfferActivateVoidSpaceKey():
                menuEntries += [[MenuLabel('UI/Commands/ActivateAbyssalKey', {'item': invItem.typeID}), self.ActivateVoidSpaceKey, (invItem,)]]
            if item.OfferRandomJumpKey():
                menuEntries += [[MenuLabel('UI/Commands/ActivateRandomJumpKey', {'item': invItem.typeID}), self.ActivateRandomJumpKey, (invItem,)]]
            if item.OfferPVPFilamentKey():
                menuEntries += [[MenuLabel('UI/Commands/ActivatePVPFilamentKey', {'item': invItem.typeID}), self.ActivatePVPfilamentKey, (invItem,)]]
            if item.OfferWarpVector():
                menuEntries += [[MenuLabel('UI/Commands/ActivateWarpVectorItem'), self.ActivateWarpVector, (invItem,)]]
            if item.OfferUseFormula():
                menuEntries += [[MenuLabel('UI/Industry/UseFormula'), self.ShowInIndustryWindow, [invItem]]]
            if item.OfferUseBlueprint():
                menuEntries += [[MenuLabel('UI/Industry/UseBlueprint'), self.ShowInIndustryWindow, [invItem]]]
            if item.OfferTransferAmmoToCargo():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/TransferAmmoToCargo'), self.TransferToCargo, (invItem.itemID,)]]
            if item.OfferInsureItem(stationServices):
                menuEntries += [[MenuLabel('UI/Insurance/InsuranceWindow/Commands/Insure'), sm.GetService('insurance').Insure, (invItem,)]]
            if item.OfferFindInContracts():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/FindInContracts'), sm.GetService('contracts').FindRelated, (invItem.typeID,
                   None,
                   None,
                   None,
                   None,
                   None)]]
            if item.OfferFindInPersonalAssets():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/FindPersonalAssets'), invItemFunctions.FindInPersonalAssets, (invItem.typeID,)]]
            if invItem.typeID in settings.user.ui.Get('marketquickbar', []):
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/RemoveTypeFromMarketQuickbar'), self.RemoveFromQuickBar, (invItem,)]]
            elif item.OfferAddToMarketQuickBar():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/AddTypeToMarketQuickbar'), self.AddToQuickBar, (invItem.typeID,)]]
            if item.OfferLoadCharges():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/LoadCharges'), self.LoadCharges, (invItem,)]]
            if item.OfferSimulateShipFitting():
                menuEntries += [(MenuLabel('UI/Fitting/FittingWindow/SimulateShipFitting'), GhostFitShip, (invItem,))]
            if item.OfferSimulateShip():
                menuEntries += [(MenuLabel('UI/Fitting/FittingWindow/SimulateShip'), openFunctions.SimulateFitting, (utillib.KeyVal(shipTypeID=invItem.typeID, fitData=[]),))]
            if unparsed:
                menuEntries += [None]
        if not isMultiSelection and not checkViewOnly:
            if item.OfferSetNewPasswordForContainer():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/SetNewPasswordForContainer'), self.AskNewContainerPwd, ([invItem], localization.GetByLabel('UI/Inventory/ItemActions/SetNewPasswordForContainer'), const.SCCPasswordTypeGeneral)]]
            if item.OfferSetNewConfigPasswordForContainer():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/SetNewConfigPasswordForContainer'), self.AskNewContainerPwd, ([invItem], localization.GetByLabel('UI/Inventory/ItemActions/SetNewConfigPasswordForContainer'), const.SCCPasswordTypeConfig)]]
            if item.OfferViewLog():
                menuEntries += [MenuEntryData(MenuLabel('UI/Inventory/ItemActions/ViewLog'), lambda : openFunctions.ViewAuditLogForALSC(invItem.itemID), texturePath=eveicon.details_view)]
            if item.OfferConfigureALSC():
                menuEntries += [MenuEntryData(MenuLabel('UI/Inventory/ItemActions/ConfigureALSContainer'), lambda : self.ConfigureALSC(invItem.itemID), texturePath=eveicon.settings)]
            if item.OfferRetrievePasswordALSC():
                menuEntries += [[MenuLabel('UI/Commands/RetrievePassword'), self.RetrievePasswordALSC, (invItem.itemID,)]]
            if item.OfferSetName():
                menuEntries += [[MenuLabel('UI/Commands/SetName'), self.SetName, (invItem,)]]
            if item.OfferMakeShipActive():
                if self.sessionChecker.IsPilotInStation():
                    menuEntries += [[MenuLabel('UI/Inflight/BoardShip'), self.ActivateShip, (invItem,)]]
                elif self.sessionChecker.IsPilotInStructure():
                    menuEntries += [[MenuLabel('UI/Inflight/BoardShip'), sm.GetService('structureDocking').ActivateShip, (invItem.itemID,)]]
            if item.OfferStripFitting():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/StripFitting'), self.StripFitting, [invItem]]]
            if item.OfferFindContract():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/FindContract'), self.FindCourierContract, [invItem]]]
            if item.OfferChangeName():
                menuEntries += [[MenuLabel('UI/Commands/ChangeName'), self.SetName, (invItem,)]]
            if item.OfferLaunchFromContainer():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/LaunchFromContainer'), self.LaunchContainerFromContainer, (invItem,)]]
            if item.OfferLaunchShip():
                if item.IsInShipMA():
                    menuEntries += [[MenuLabel('UI/Inventory/ItemActions/LaunchShip'), self.LaunchSMAContents, [invItem]]]
                elif item.OfferLaunchShipFromSpaceContainer():
                    menuEntries += [[MenuLabel('UI/Inventory/ItemActions/LaunchShip'), self.LaunchShipFromWreck, [invItem]]]
            if item.OfferBoardShip_FromSMA():
                menuEntries += [[MenuLabel('UI/Inflight/BoardShip'), self.BoardSMAShip, (invItem.locationID, invItem.itemID)]]
            if item.OfferLaunchShipFromBay():
                menuEntries += [[MenuLabel('UI/Inventory/ItemActions/LaunchShipFromBay'), self.LaunchSMAContents, [invItem]]]
            if item.OfferBoardShipFromBay():
                menuEntries += [[MenuLabel('UI/Inflight/POS/BoardShipFromBay'), self.BoardSMAShip, (invItem.locationID, invItem.itemID)]]
        if session.role & (ROLE_GML | ROLE_WORLDMOD):
            menuEntries.insert(0, ('GM / WM Extras', ('isDynamic', self.GetGMMenu, (invItem.itemID,
               None,
               None,
               invItem,
               None))))
        return menuEntries

    def DeliverToCorpHangarFolder(self, invItemAndFlagList):
        return invItemFunctions.DeliverToCorpHangarFolder(invItemAndFlagList, self.invCache)

    def DeliverToCorpMember(self, invItems):
        return invItemFunctions.DeliverToCorpMember(invItems, self.invCache)

    def DeliverToSelf(self, invItems):
        return invItemFunctions.DeliverToMyself(invItems, self.invCache)

    def SplitStack(self, invItems):
        return invItemFunctions.SplitStack(invItems, self.invCache)

    def MarketDetailMenu(self, typeID):
        m = MenuList()
        if not evetypes.IsPublished(typeID):
            return m
        if evetypes.GetMarketGroupID(typeID):
            self._AddMarketDetailsOption(m, typeID)
        if evetypes.IsPublished(typeID):
            m += [(MenuLabel('UI/Inventory/ItemActions/FindInContracts'), sm.GetService('contracts').FindRelated, (typeID,
               None,
               None,
               None,
               None,
               None))]
        m += [[MenuLabel('UI/Inventory/ItemActions/FindPersonalAssets'), invItemFunctions.FindInPersonalAssets, (typeID,)]]
        m += [(MenuLabel('UI/Compare/CompareButton'), self.CompareType, (typeID,))]
        return m

    def DroneMenu(self, data, unmerged = 0):
        if isinstance(data, list):
            menus = MenuList([ self._DroneMenu(droneID, typeID, ownerID, locationID) for droneID, typeID, ownerID, locationID in data ])
            if unmerged:
                return menus
            return MergeMenus(menus)
        return self._DroneMenu(*data)

    def _DroneMenu(self, droneID, typeID, ownerID, locationID):
        bp = sm.StartService('michelle').GetBallpark()
        if not bp:
            return MenuList()
        groupID = evetypes.GetGroupID(typeID)
        categoryID = evetypes.GetCategoryID(typeID)
        droneState = sm.GetService('michelle').GetDroneState(droneID)
        drone = DroneChecker(Bundle(itemID=droneID, typeID=typeID, groupID=groupID, categoryID=categoryID, ownerID=ownerID, locationID=locationID, droneState=droneState))
        m = MenuList()
        if drone.OfferEngageTarget():
            targetID = sm.GetService('target').GetActiveTargetID()
            crimewatchSvc = sm.GetService('crimewatchSvc')
            requiredSafetyLevel = crimewatchSvc.GetRequiredSafetyLevelForEngagingDrones([droneID], targetID)
            menuClass = None
            if crimewatchSvc.CheckUnsafe(requiredSafetyLevel):
                menuClass = eveMenu.CriminalMenuEntryView if requiredSafetyLevel == const.shipSafetyLevelNone else eveMenu.SuspectMenuEntryView
            m.append(DroneEngageTargetMenuEntryData(MenuLabel('UI/Drones/EngageTarget'), lambda : self.EngageTarget([droneID]), droneIDs=[droneID], menuEntryViewClass=menuClass))
        elif drone.failure_label:
            m.reasonsWhyNotAvailable['UI/Drones/EngageTarget'] = self.GetUnavailableText(drone)
        if drone.OfferMineWithDrone():
            m += [[MenuLabel('UI/Drones/MineWithDrone'), self.MineRepeatedly, [droneID]]]
        elif drone.OfferSalvage():
            m += [[MenuLabel('UI/Drones/Salvage'), self.Salvage, [[droneID]]]]
        elif drone.failure_label:
            m.reasonsWhyNotAvailable['UI/Drones/MineWithDrone'] = self.GetUnavailableText(drone)
        if drone.OfferDroneAssist():
            m += [[MenuLabel('UI/Drones/DroneAssist'), ('isDynamic', self.GetFleetMemberMenu, (self.Assist,)), [droneID]]]
        if drone.OfferDroneGuard():
            m += [[MenuLabel('UI/Drones/DroneGuard'), ('isDynamic', self.GetFleetMemberMenu, (self.Guard,)), [droneID]]]
        if drone.OfferDroneUnanchorObject():
            m += [[MenuLabel('UI/Inflight/UnanchorObject'), self.DroneUnanchor, [droneID]]]
        elif drone.failure_label:
            m.reasonsWhyNotAvailable['UI/Inflight/UnanchorObject'] = self.GetUnavailableText(drone)
        if drone.OfferReturnAndOrbit():
            m += [[MenuLabel('UI/Drones/ReturnDroneAndOrbit'), self.ReturnAndOrbit, [droneID]]]
        elif drone.failure_label:
            m.reasonsWhyNotAvailable['UI/Drones/ReturnDroneAndOrbit'] = self.GetUnavailableText(drone)
        if drone.OfferReturnToDroneBay():
            m += [[MenuLabel('UI/Drones/ReturnDroneToBay'), self.ReturnToDroneBay, [droneID]]]
        elif drone.failure_label:
            m.reasonsWhyNotAvailable['UI/Drones/ReturnDroneToBay'] = self.GetUnavailableText(drone)
        if drone.OfferScoopDroneToBay():
            m += [MenuEntryData(MenuLabel('UI/Drones/ScoopDroneToBay'), func=lambda : self.ScoopToDroneBay((droneID,)))]
        elif drone.failure_label:
            m.reasonsWhyNotAvailable['UI/Drones/ScoopDroneToBay'] = self.GetUnavailableText(drone)
        if drone.OfferAbandonDrone():
            m += [[MenuLabel('UI/Drones/AbandonDrone'), self.AbandonDrone, [droneID]]]
        return m

    def GetUnavailableText(self, entity):
        if entity.failure_label:
            return localization.GetByLabel(entity.failure_label, **entity.label_args)

    def CharacterMenu(self, charid, **kwargs):
        if type(charid) == list:
            menus = []
            for charID in charid:
                menus.append(self._CharacterMenu(charID, (len(charid) > 1), **kwargs))

            return MergeMenus(menus)
        else:
            return self._CharacterMenu(charid, **kwargs)

    def _CharacterMenu(self, charID, multi = 0, **kwargs):
        if not charID:
            return MenuList()
        addressBookSvc = sm.GetService('addressbook')
        menuEntries = MenuList()
        if not self.sessionChecker:
            self.sessionChecker = SessionChecker(session, sm)
        character = CharacterChecker(charID, bool(multi), self.sessionChecker)
        if character.OfferShowInfo():
            menuEntries += [(MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (cfg.eveowners.Get(charID).typeID, charID))]
        if character.OfferStartConversation():
            menuEntries += [[MenuLabel('UI/Chat/StartConversation'), GetChatService().Invite, (charID, None, kwargs.get('isRecruiting', None))]]
        if character.OfferStartConversationAgent():
            menuEntries += [[MenuLabel('UI/Chat/StartConversationAgent'), sm.StartService('agents').OpenDialogueWindow, (charID,)]]
        if character.OfferAddToAddressBook():
            menuEntries += [[MenuLabel('UI/PeopleAndPlaces/AddToAddressbook'), addressBookSvc.AddToPersonalMulti, [charID]]]
        if character.OfferInviteToChat():
            menuEntries += [[MenuLabel('UI/Chat/InviteToChat'), ('isDynamic', self.__GetInviteMenu, (charID,))]]
        if character.OfferSendPilotEVEMail():
            menuEntries += [[MenuLabel('UI/EVEMail/SendPilotEVEMail'), sm.StartService('mailSvc').SendMsgDlg, ([charID], None, None)]]
        if character.OfferAddContact():
            menuEntries.append(MenuEntryData(MenuLabel('UI/PeopleAndPlaces/AddContact'), lambda : addressBookSvc.AddToPersonalMulti([charID], 'contact'), texturePath=eveicon.add))
        if character.OfferEditContact():
            menuEntries += [[MenuLabel('UI/PeopleAndPlaces/EditContact'), addressBookSvc.AddToPersonalMulti, [charID, 'contact', True]]]
        if character.OfferRemoveContact():
            menuEntries += [[MenuLabel('UI/PeopleAndPlaces/RemoveContact'), addressBookSvc.DeleteEntryMulti, [[charID], 'contact']]]
        if character.OfferRemoveFromAddressbook():
            menuEntries += [[MenuLabel('UI/PeopleAndPlaces/RemoveFromAddressbook'), addressBookSvc.DeleteEntryMulti, [charID]]]
        if character.OfferUnblockContact():
            menuEntries += [[MenuLabel('UI/PeopleAndPlaces/UnblockContact'), addressBookSvc.UnblockOwner, ([charID],)]]
        if character.OfferBlockContact():
            menuEntries += [[MenuLabel('UI/PeopleAndPlaces/BlockContact'), addressBookSvc.BlockOwner, (charID,)]]
        if character.OfferAddCorpContact():
            menuEntries += [[MenuLabel('UI/PeopleAndPlaces/AddCorpContact'), addressBookSvc.AddToPersonalMulti, [charID, 'corpcontact']]]
        if character.OfferRemoveCorpContact():
            menuEntries += [[MenuLabel('UI/PeopleAndPlaces/RemoveCorpContact'), addressBookSvc.DeleteEntryMulti, [[charID], 'corpcontact']]]
        if character.OfferEditCorpContact():
            menuEntries += [[MenuLabel('UI/PeopleAndPlaces/EditCorpContact'), addressBookSvc.AddToPersonalMulti, [charID, 'corpcontact', True]]]
        if character.OfferAddAllianceContact():
            menuEntries += [[MenuLabel('UI/PeopleAndPlaces/AddAllianceContact'), addressBookSvc.AddToPersonalMulti, [charID, 'alliancecontact']]]
        if character.OfferRemoveAllianceContact():
            menuEntries += [[MenuLabel('UI/PeopleAndPlaces/RemoveAllianceContact'), addressBookSvc.DeleteEntryMulti, [[charID], 'alliancecontact']]]
        if character.OfferEditEditAllianceContact():
            menuEntries += [[MenuLabel('UI/PeopleAndPlaces/EditAllianceContact'), addressBookSvc.AddToPersonalMulti, [charID, 'alliancecontact', True]]]
        if character.OfferGiveMoney():
            menuEntries += [[MenuLabel('UI/Commands/GiveMoney'), sm.StartService('wallet').TransferMoney, (session.charid,
               None,
               charID,
               None)]]
        if character.OfferCloneInstallation():
            menuEntries += [[MenuLabel('UI/CloneJump/OfferCloneInstallation'), sm.StartService('clonejump').OfferShipCloneInstallation, (charID,)]]
        if character.OfferMapMenu():
            menuEntries += [None]
            menuEntries += self._MapMenu(character.GetAgentLocation())
            agentInfo = character.GetAgentInfo()
            if session.solarsystemid and agentInfo.solarsystemID == session.solarsystemid and agentInfo.stationID and not session.structureid:
                menuEntries += [[MenuLabel('UI/Inflight/DockInStation'),
                  self.Dock,
                  (agentInfo.stationID,),
                  None,
                  None,
                  'DockInStation']]
        if character.OfferTradeWithCharacter():
            menuEntries += [[MenuLabel('UI/Market/TradeWithCharacter'), sm.GetService('pvptrade').StartTradeSession, (charID,)]]
        if character.OfferPlaceBounty():
            menuEntries += [[MenuLabel('UI/Station/BountyOffice/PlaceBounty'), openFunctions.OpenBountyOffice, (charID,)]]
        if character.OfferCapturePortrait():
            menuEntries += [[MenuLabel('UI/Commands/CapturePortrait'), sm.StartService('photo').SavePortraits, [charID]]]
        if character.OfferInvitePilotToFleet():
            menuEntries += [[MenuLabel('UI/Fleet/InvitePilotToFleet'), self.FleetInviteMenu(charID)]]
        if character.OfferFleetMenu():
            menuEntries += [[MenuLabel('UI/Fleet/Fleet'), ('isDynamic', self.FleetMenu, (charID, False))]]
        if character.OfferFormFleetWith():
            menuEntries += [[MenuLabel('UI/Fleet/FormFleetWith'), self.InviteToFleet, [charID]]]
        if character.OfferDuelMenuEntry():
            menuEntries += [[MenuLabel('UI/Crimewatch/Duel/DuelMenuEntry'), self.crimewatchSvc.StartDuel, (charID,)]]
        menuEntries += [None]
        if character.OfferViewCorpMemberDetails():
            menuEntries += [[MenuLabel('UI/Corporations/Common/ViewCorpMemberDetails'), self.ShowCorpMemberDetails, (charID,)]]
        if character.OfferEditCorpMember():
            menuEntries += [[MenuLabel('UI/Corporations/Common/EditCorpMember'), self.ShowCorpMemberDetails, (charID,)]]
        if character.OfferAllowCorpRoles():
            allowRolesMenu = [[MenuLabel('UI/Corporations/Common/ConfirmAllowCorpRoles'), sm.StartService('corp').UpdateMember, (session.charid,
               None,
               None,
               None,
               None,
               None,
               None,
               None,
               None,
               None,
               None,
               None,
               None,
               None,
               0)]]
            menuEntries += [[MenuLabel('UI/Corporations/Common/AllowCorpRoles'), allowRolesMenu]]
        if character.OfferTransferCorpCash():
            menuEntries += [[MenuLabel('UI/Corporations/Common/TransferCorpCash'), sm.StartService('wallet').TransferMoney, (session.corpid,
               None,
               charID,
               None)]]
        if character.OfferQuitCorp():
            quitCorpMenu = [[MenuLabel('UI/Corporations/Common/RemoveAllCorpRoles'), sm.StartService('corp').RemoveAllRoles, ()], [MenuLabel('UI/Corporations/Common/ConfirmQuitCorp'), sm.StartService('corp').KickOut, (charID,)]]
            menuEntries += [[MenuLabel('UI/Corporations/Common/QuitCorp'), quitCorpMenu]]
        if character.OfferExpelCorpMember():
            if multi:
                expelMenu = [[MenuLabel('UI/Corporations/Common/ConfirmExpelMembers'), sm.StartService('corp').KickOutMultipleMembers, [charID]]]
                menuEntries += [[MenuLabel('UI/Corporations/Common/ExpelCorpMembers'), expelMenu]]
            else:
                expelMenu = [[MenuLabel('UI/Corporations/Common/ConfirmExpelMember'), sm.StartService('corp').KickOut, (charID,)]]
                menuEntries += [[MenuLabel('UI/Corporations/Common/ExpelCorpMember'), expelMenu]]
        if character.OfferResignAsCEO():
            resignMenu = [[MenuLabel('UI/Corporations/Common/ConfirmResignAsCEO'), sm.StartService('corp').ResignFromCEO, ()]]
            menuEntries += [[MenuLabel('UI/Corporations/Common/ResignAsCEO'), resignMenu]]
        if character.OfferAwardCorpMemberDecoration():
            menuEntries += [[MenuLabel('UI/Corporations/Common/AwardCorpMemberDecoration'), self.AwardDecoration, [charID]]]
        if character.OfferSendCorpInvite():
            menuEntries += [[MenuLabel('UI/Corporations/Common/SendCorpInvite'), sm.StartService('corp').InviteToJoinCorp, (charID,)]]
        if boot.region == 'optic':
            if character.OfferReportMenuEntry():
                menuEntries += [[MenuLabel('UI/Kiring/Report/ReportMenuEntry'), sm.GetService('reportClientSvc').Report, (charID,)]]
        if session.role & (ROLE_GML | ROLE_WORLDMOD | ROLE_LEGIONEER):
            menuEntries.insert(0, ('GM / WM Extras', ('isDynamic', self.GetGMMenu, (None,
               None,
               charID,
               None,
               None,
               None,
               kwargs.get('channelID', None)))))
        return menuEntries

    def FleetMenu(self, charID, unparsed = True):
        menuEntries = MenuList()
        if not self.sessionChecker:
            self.sessionChecker = SessionChecker(session, sm)
        member = FleetMemberChecker(charID, self.sessionChecker, cfg)
        if member.OfferShowInfo():
            menuEntries += [[MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (member.typeID,
               charID,
               0,
               None,
               None)]]
        if not member.IsFleetMember():
            return menuEntries
        fleetSvc = sm.GetService('fleet')
        defaultWarpDist = self.GetDefaultActionDistance('WarpTo')
        formationName = {'fleetFormation': GetSelectedFormationName()}
        if unparsed:
            menuEntries += [None]
        if member.OfferKickFleetMember():
            menuEntries += [[MenuLabel('UI/Fleet/KickFleetMember'), self.ConfirmMenu(lambda *x: fleetSvc.KickMember(charID))]]
        if member.OfferMakeFleetLeader():
            menuEntries += [[MenuLabel('UI/Fleet/MakeFleetLeader'), fleetSvc.MakeLeader, (charID,)]]
        if member.OfferAddPilotToWatchlist():
            menuEntries += [[MenuLabel('UI/Fleet/AddPilotToWatchlist'), fleetSvc.AddFavorite, ([charID],)]]
        if member.OfferRemovePilotFromWatchlist():
            menuEntries += [[MenuLabel('UI/Fleet/RemovePilotFromWatchlist'), fleetSvc.RemoveFavorite, (charID,)]]
        if member.OfferBroadcastTravelToMe():
            menuEntries += [MenuEntryData(MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastTravelToMe'), lambda : sm.GetService('fleet').SendBroadcast_TravelTo(session.solarsystemid2), texturePath=iconsByBroadcastType[BROADCAST_TRAVEL_TO])]
        if member.OfferWarpToMember():
            menuEntries += [[MenuLabel('UI/Fleet/WarpToMember'), self.WarpToMember, (charID, float(defaultWarpDist))]]
            menuEntries += [[MenuLabel('UI/Fleet/WarpToMemberSubmenuOption'), self.WarpToMenu(self.WarpToMember, charID)]]
        if member.OfferWarpFleetToMember():
            menuEntries += [[MenuLabel('UI/Fleet/WarpFleetToMember', formationName), self.WarpFleetToMember, (charID, float(defaultWarpDist))]]
            menuEntries += [[MenuLabel('UI/Fleet/FleetSubmenus/WarpFleetToMember', formationName), self.WarpToMenu(self.WarpFleetToMember, charID)]]
        if member.OfferWarpWingToMember():
            menuEntries += [[MenuLabel('UI/Fleet/WarpWingToMember', formationName), self.WarpFleetToMember, (charID, float(defaultWarpDist))]]
            menuEntries += [[MenuLabel('UI/Fleet/FleetSubmenus/WarpWingToMember', formationName), self.WarpToMenu(self.WarpFleetToMember, charID)]]
        if member.OfferWarpSquadToMember():
            menuEntries += [[MenuLabel('UI/Fleet/WarpSquadToMember', formationName), self.WarpFleetToMember, (charID, float(defaultWarpDist))]]
            menuEntries += [[MenuLabel('UI/Fleet/FleetSubmenus/WarpSquadToMember', formationName), self.WarpToMenu(self.WarpFleetToMember, charID)]]
        if member.OfferJumpToFleetMember():
            menuEntries += [[MenuLabel('UI/Inflight/JumpToFleetMember'), self.JumpToMember, (charID,)]]
        if member.OfferBridgeToMember():
            menuEntries += [[MenuLabel('UI/Fleet/BridgeToMember'), self.BridgeToMember, (charID,)]]
        if member.OfferGroupJumpToFleetMember():
            menuEntries += [[MenuLabel('UI/Fleet/ConduitJumpToFleetMember'), self.GroupJumpToMember, (charID,)]]
        if member.IsMe():
            menuEntries += [[MenuLabel('UI/Fleet/LeaveMyFleet'), self.ConfirmMenu(fleetSvc.LeaveFleet)]]
        moveMenu = self.GetFleetMemberMenu2(charID, fleetSvc.MoveMember, True)
        if moveMenu:
            menuEntries.extend([[MenuLabel('UI/Fleet/FleetSubmenus/MoveFleetMember'), moveMenu]])
        return menuEntries

    def FleetInviteMenu(self, charID):
        return self.GetFleetMemberMenu2(charID, lambda *args: self.DoInviteToFleet(*args))

    @staticmethod
    def GetFleetMemberMenu2(charID, callback, isMove = False):
        wings = sm.GetService('fleet').GetWings()
        members = sm.GetService('fleet').GetMembers()
        ret = evefleet.client.MemberMenu(charID, wings, members, callback, sm.GetService('fleet').GetOptions().isFreeMove, isMove, MenuLabel, localization.GetByLabel).Get()
        return ret

    @staticmethod
    def DoInviteToFleet(charID, wingID, squadID, role):
        sm.GetService('fleet').Invite(charID, wingID, squadID, role)

    @staticmethod
    def AwardDecoration(charIDs):
        return menuFunctions.AwardDecoration(charIDs)

    @staticmethod
    def ShowCorpMemberDetails(charID):
        OpenMemberDetails(charID)

    @staticmethod
    def __GetInviteMenu(charID):

        def Invite(characterID, channelID):
            GetChatService().Invite(characterID, channelID)

        channels = GetChatService().GetChannelsAvailableForInvite(charID)
        inviteMenu = []
        for channel in channels:
            inviteMenu += [[GetChatService().GetDisplayName(channel), Invite, (charID, channel)]]

        inviteMenu.sort()
        inviteMenu = [[MenuLabel('UI/Chat/StartConversation'), Invite, (charID, None)]] + inviteMenu
        return MenuList(inviteMenu)

    @staticmethod
    def SlashCmd(cmd):
        return devFunctions.SlashCmd(cmd)

    @staticmethod
    def SlashCmdTr(cmd):
        return devFunctions.SlashCmdTr(cmd)

    def GetGMTypeMenu(self, typeID, itemID = None, divs = False, unload = False):
        if not session.role & (ROLE_GML | ROLE_WORLDMOD):
            return []

        def _wrapMulti(command, what = None, maxValue = 2147483647):
            if uicore.uilib.Key(uiconst.VK_SHIFT):
                if not what:
                    what = command.split(' ', 1)[0]
                result = uix.QtyPopup(maxvalue=maxValue, minvalue=1, caption=what, label=localization.GetByLabel('UI/Common/Quantity'), hint='')
                if result:
                    qty = result['qty']
                else:
                    return
            else:
                qty = 1
            return sm.GetService('slash').SlashCmd(command % qty)

        cat = evetypes.GetCategoryID(typeID)
        if unload:
            if type(itemID) is tuple:
                for row in self.invCache.GetInventoryFromId(itemID[0]).ListHardwareModules():
                    if row.flagID == itemID[1]:
                        itemID = row.itemID
                        break
                else:
                    itemID = None

            else:
                charge = self.godma.GetItem(itemID)
                if charge and charge.categoryID == const.categoryCharge:
                    for row in self.invCache.GetInventoryFromId(charge.locationID).ListHardwareModules():
                        if row.flagID == charge.flagID and row.itemID != itemID:
                            itemID = row.itemID
                            break
                    else:
                        itemID = None

        gm = MenuList()
        if divs:
            gm.append(None)
        if session.role & (ROLE_WORLDMOD | ROLE_SPAWN):
            if not session.stationid:
                if cat in (const.categoryShip, const.categoryStructure):
                    gm.append(('WM: /Spawn this type', lambda *x: _wrapMulti('/spawnN %%d 4000 %d' % typeID, '/Spawn', 50)))
                    if itemID:
                        gm.append(('WM: /Unspawn this item', lambda *x: sm.RemoteSvc('slash').SlashCmd('/unspawn %d' % itemID)))
                if cat == const.categoryEntity:
                    gm.append(('WM: /Entity deploy this type', lambda *x: _wrapMulti('/entity deploy %%d %d' % typeID, '/Entity', 100)))
        gm.append(None)
        gm.append(('typeID: ' + str(typeID) + ' (%s)' % evetypes.GetName(typeID), blue.pyos.SetClipboardData, (str(typeID),)))
        group = evetypes.GetGroupID(typeID)
        gm.append(('groupID: ' + str(group) + ' (%s)' % evetypes.GetGroupName(typeID), blue.pyos.SetClipboardData, (str(group),)))
        category = evetypes.GetCategoryID(typeID)
        categoryName = evetypes.GetCategoryNameByCategory(category)
        gm.append(('categID: ' + str(category) + ' (%s)' % categoryName, blue.pyos.SetClipboardData, (str(category),)))
        graphic = inventorycommon.typeHelpers.GetGraphic(typeID)
        if graphic is not None:
            gm.append(('graphicID: ' + str(evetypes.GetGraphicID(typeID)), blue.pyos.SetClipboardData, (str(evetypes.GetGraphicID(typeID)),)))
            if hasattr(graphic, 'graphicFile'):
                gm.append(('graphicFile: ' + str(graphic.graphicFile), blue.pyos.SetClipboardData, (str(graphic.graphicFile),)))
        gm.append(None)
        if typeID != const.typeSolarSystem and cat not in [const.categoryStation, const.categoryOwner]:
            if session.role & ROLE_WORLDMOD:
                gm.append(('WM: /create this type', lambda *x: _wrapMulti('/create %d %%d' % typeID)))
            gm.append(('GM: /load me this type', lambda *x: _wrapMulti('/load me %d %%d' % typeID)))
            graphicID = evetypes.GetGraphicID(typeID)
            graphic = fsdGraphicIDs.GetGraphic(graphicID)
            graphicFile = fsdGraphicIDs.GetGraphicFile(graphic)
            sofHull = fsdGraphicIDs.GetSofHullName(graphic)
            if session.stationid is not None:
                graphicsItems = [('typeID: ' + str(typeID), blue.pyos.SetClipboardData, (str(typeID),)),
                 ('graphicID: ' + str(graphicID), blue.pyos.SetClipboardData, (str(graphicID),)),
                 ('graphicFile: ' + str(graphicFile), blue.pyos.SetClipboardData, (str(graphicFile),)),
                 ('SOF hull: ' + str(sofHull), blue.pyos.SetClipboardData, (str(sofHull),))]
                if itemID is not None and self.godma.GetItem(itemID) is not None:
                    dirtTimeStamp = eveMoniker.GetShipAccess().GetDirtTimestamp(itemID)
                    dirtTimeStampStr = fmtutil.FmtDateEng(dirtTimeStamp)
                    dirtTimeDiff = blue.os.TimeDiffInMs(dirtTimeStamp, blue.os.GetWallclockTime())
                    killCounter = sm.RemoteSvc('shipKillCounter').GetItemKillCountPlayer(itemID)
                    graphicsItems += [None,
                     ('Last cleaning: ' + str(dirtTimeStampStr), blue.pyos.SetClipboardData, (str(dirtTimeStampStr),)),
                     ('msecs since last cleaning: ' + str(dirtTimeDiff), blue.pyos.SetClipboardData, (str(dirtTimeDiff),)),
                     None,
                     ('kill counter: ' + str(killCounter), blue.pyos.SetClipboardData, (str(killCounter),))]
                gm.append(('graphics', graphicsItems))
        if IsShipFittable(cat):
            gm.append(('GM: /fit me this type', lambda *x: _wrapMulti('/loop %%d /fit me %d' % typeID, '/Fit', 8)))
            if unload:
                if itemID:
                    gm.append(('GM: /unload me this item', lambda *x: sm.RemoteSvc('slash').SlashCmd('/unload me %d' % itemID)))
                gm.append(('GM: /unload me this type', lambda *x: sm.RemoteSvc('slash').SlashCmd('/unload me %d' % typeID)))
                if itemID:
                    module = self.godma.GetItem(itemID)
                    if module and module.damage:
                        gm.append(('GM: Repair this module', lambda *x: sm.RemoteSvc('slash').SlashCmd('/heal %d' % itemID)))
        if itemID:
            gm.append(get_space_components_menu(itemID, typeID))
            gm.append(('GM: Inspect Attributes', self.InspectAttributes, (itemID, typeID)))
        if session.role & ROLE_PROGRAMMER:
            gm.append(('PROG: Modify Attributes', ('isDynamic', self.AttributeMenu, (itemID, typeID))))
        import webbrowser
        gm.append(MenuEntryData('Show in FSD editor', lambda : webbrowser.open_new('http://localhost:8000/specializedtypes/categories/{category_id}/groups/{group_id}/types/{type_id}/'.format(category_id=evetypes.GetCategoryID(typeID), group_id=evetypes.GetGroupID(typeID), type_id=typeID))))
        gm.append(None)
        gm.extend(expertSystems.get_gm_menu_options(typeID))
        if divs:
            gm.append(None)
        return gm

    @staticmethod
    def InspectAttributes(itemID, typeID):
        AttributeInspector.Open(itemID=itemID, typeID=typeID)

    @staticmethod
    def InspectSlimItem(itemID):
        from eve.devtools.script.slimItemInspector import SlimItemInspector
        windowID = 'slimItemInspector_%s' % itemID
        SlimItemInspector.Open(itemID=itemID, windowID=windowID)

    @staticmethod
    def NPCInfoMenu(item):
        return devFunctions.NPCInfoMenu(item)

    @staticmethod
    def AttributeMenu(itemID, typeID):
        return devFunctions.AttributeMenu(itemID, typeID)

    @staticmethod
    def SetDogmaAttribute(itemID, attrName, actualValue):
        return devFunctions.SetDogmaAttribute(itemID, attrName, actualValue)

    @staticmethod
    def GagPopup(charID, channelID, numMinutes):
        return devFunctions.GagPopup(charID, channelID, numMinutes)

    @staticmethod
    def Ungag(charID, channelID):
        return devFunctions.Ungag(charID, channelID)

    @staticmethod
    def ReportISKSpammer(charID, channelID):
        sm.GetService('chat').report_isk_spammer(charID, channelID)

    @staticmethod
    def BanIskSpammer(charID):
        return devFunctions.BanIskSpammer(charID)

    @staticmethod
    def GagIskSpammer(charID):
        return devFunctions.GagIskSpammer(charID)

    @staticmethod
    def GetFromESP(action):
        return devFunctions.GetFromESP(action)

    def GetFitMenu(self, item, typeID):
        from shipfitting.multiFitMenu import GetMultiFitMenu
        return GetMultiFitMenu(item, typeID)

    @staticmethod
    def FitStack(item, fit):
        from eve.client.script.ui.shared.fitting.multiFitWnd import MultiFitWnd
        maxShipsAllowed = GetMaxShipsToFit(sm.GetService('machoNet'))
        wnd = MultiFitWnd.GetIfOpen()
        if wnd:
            wnd.LoadWindow(fit, min(item.stacksize, maxShipsAllowed))
        else:
            MultiFitWnd.Open(fitting=fit, qty=min(item.stacksize, maxShipsAllowed))

    def GetSkinLicenseMenu(self, invItem, itemChecker):
        submenu = MenuList()
        submenu.append([MenuLabel('UI/Commands/ActivateSkinLicense'), menuFunctions.ActivateShipSkinLicense, [[(invItem.itemID, invItem.typeID)]]])
        if itemChecker.IsSkinForCurrentShip():
            submenu.append([MenuLabel('UI/Commands/ActivateAndApplySkinLicense'), menuFunctions.ActivateShipSkinLicenseAndApply, (invItem.itemID, invItem.typeID)])
        else:
            submenu.append([MenuLabel('UI/Commands/ActivateAndApplySkinLicenseDisabled'), DISABLED_ENTRY0])
            submenu.reasonsWhyNotAvailable['UI/Commands/ActivateAndApplySkinLicense'] = localization.GetByLabel('UI/Menusvc/MenuHints/SkinNotForCurrentShip')
        return submenu

    def GetGMMenu(self, itemID = None, slimItem = None, charID = None, invItem = None, mapItem = None, typeID = None, channelID = None):
        if not session.role & (ROLE_GML | ROLE_WORLDMOD):
            if charID and session.role & ROLE_LEGIONEER:
                return [('Gag ISK Spammer', self.GagIskSpammer, (charID,))]
            return MenuList()
        gm = MenuList()
        gm += [(str(itemID or charID), blue.pyos.SetClipboardData, (str(itemID or charID),))]
        if mapItem and not slimItem:
            gm.append(('TR me here!', self.SlashCmdTr, ('/tr me ' + str(mapItem.itemID),)))
            gm.append(None)
        elif charID:
            gm.append(('TR me to %s' % cfg.eveowners.Get(charID).name, self.SlashCmdTr, ('/tr me ' + str(charID),)))
            gm.append(None)
        elif slimItem:
            gm.append(('TR me here!', self.SlashCmdTr, ('/tr me ' + str(itemID),)))
            gm.append(None)
        elif itemID:
            gm.append(('TR me here!', self.SlashCmdTr, ('/tr me ' + str(itemID),)))
            gm.append(None)
        if invItem:
            gm += [('Copy ID/Qty', self.CopyItemIDAndMaybeQuantityToClipboard, (invItem,))]
            typeText = 'copy typeID (%s)' % invItem.typeID
            gm += [(typeText, blue.pyos.SetClipboardData, (str(invItem.typeID),))]
            gm.append(None)
            typeID = invItem.typeID
            if invItem.locationID and not idCheckers.IsSolarSystem(invItem.locationID):
                try:
                    inv = self.invCache.GetInventoryFromId(invItem.locationID)
                    gm.append(('QA LOCK ITEM', inv.QALockItem, (invItem.itemID,)))
                    gm.append(('QA UNLOCK ITEM', inv.QAUnlockItem, (invItem.itemID,)))
                except StandardError:
                    pass

        if charID and not idCheckers.IsNPC(charID):
            action = 'gm/character.py?action=Character&characterID=' + str(charID)
            gm.append(('Show in ESP', self.GetFromESP, (action,)))
            gm.append(None)
            gm.append(('Gag ISK Spammer', self.GagIskSpammer, (charID,)))
            gm.append(('Ban ISK Spammer', self.BanIskSpammer, (charID,)))
            action = 'gm/users.py?action=BanUserByCharacterID&characterID=' + str(charID)
            gm.append(('Ban User (ESP)', self.GetFromESP, (action,)))
            gm += [('Gag User', [('30 minutes', self.GagPopup, (charID, channelID, 30)),
               ('1 hour', self.GagPopup, (charID, channelID, 60)),
               ('6 hours', self.GagPopup, (charID, channelID, 360)),
               ('24 hours', self.GagPopup, (charID, channelID, 1440)),
               None,
               ('Ungag', self.Ungag, (charID, channelID))])]
        gm.append(None)
        item = slimItem or invItem
        if item:
            if item.categoryID == const.categoryShip and (item.singleton or not session.stationid):
                from eve.devtools.script import dna
                if item.ownerID in [session.corpid, session.charid] or session.role & ROLE_WORLDMOD:
                    try:
                        menu = dna.Ship().ImportFromShip(shipID=item.itemID, ownerID=item.ownerID, deferred=True).GetMenuInline(spiffy=False, fit=item.itemID != session.shipid)
                        gm.append(('Copycat', menu))
                    except RuntimeError:
                        pass

                gm += [('/Online modules', lambda shipID = item.itemID: self.SlashCmd('/online %d' % shipID))]
            gm += self.GetGMTypeMenu(item.typeID, itemID=item.itemID)
            if getattr(slimItem, 'categoryID', None) == const.categoryEntity or getattr(slimItem, 'groupID', None) == const.groupWreck:
                gm.append(('NPC Info', ('isDynamic', self.NPCInfoMenu, (item,))))
            gm.append(None)
        elif typeID:
            gm += self.GetGMTypeMenu(typeID)
        if session.role & ROLE_CONTENT:
            if slimItem:
                if getattr(slimItem, 'dunObjectID', None) is not None:
                    if not sm.StartService('scenario').IsSelected(itemID):
                        gm.append(('Add to Selection', sm.StartService('scenario').AddSelected, (itemID,)))
                    else:
                        gm.append(('Remove from Selection', sm.StartService('scenario').RemoveSelected, (itemID,)))
        if slimItem:
            itemID = slimItem.itemID
            graphicID = evetypes.GetGraphicID(item.typeID)
            if slimItem.categoryID == const.categoryStation and slimItem.itemID:
                npcStation = cfg.mapSolarSystemContentCache.npcStations.get(itemID, None)
                if npcStation:
                    graphicID = npcStation.graphicID
            graphic = fsdGraphicIDs.GetGraphic(graphicID)
            graphicFile = fsdGraphicIDs.GetGraphicFile(graphic)
            raceName = fsdGraphicIDs.GetSofRaceName(graphic)
            sofDNA = None
            ball = sm.StartService('michelle').GetBallpark().GetBall(slimItem.itemID)
            subMenu = self.GetGMStructureStateMenu(itemID, slimItem)
            if len(subMenu) > 0:
                gm += [('Change State', subMenu)]
            gm += self.GetGMBallsAndBoxesMenu(itemID, slimItem, charID, invItem, mapItem)
            slimItemAttributes = []
            for k, v in slimItem.__dict__.items():
                if k.startswith('__'):
                    continue
                txt = '%s = %s' % (k, v)
                if len(txt) > 80:
                    label = eveformat.simple_html_escape(txt[:60]) + ' ...'
                else:
                    label = eveformat.simple_html_escape(txt)
                slimItemAttributes.append((label, blue.pyos.SetClipboardData, (txt,)))

            slimItemAttributes.sort()
            if len(slimItemAttributes) > 0:
                gm += [('Slim attributes', slimItemAttributes)]
                gm += [('Slim attributes inspector', self.InspectSlimItem, (itemID,))]
            dirtLastClean = None
            dirtCurrentValue = None
            if ball is not None:
                if hasattr(ball, 'GetDirtTimeStampAsStr'):
                    dirtLastClean = ball.GetDirtTimeStampAsStr()
                if hasattr(ball, 'model'):
                    if ball.model is not None:
                        dirtCurrentValue = getattr(ball.model, 'dirtLevel', None)
            currentKillCount = None
            if ball is not None:
                if hasattr(ball, 'model'):
                    if ball.model is not None:
                        currentKillCount = getattr(ball.model, 'displayKillCounterValue', None)
            currentGeoLODstr = 'INVALID'
            currentGeoLOD = ''
            currentTexLODmenu = []
            impostorMode = None
            if ball is not None:
                if hasattr(ball, 'model'):
                    if ball.model is not None:
                        if hasattr(ball.model, 'mesh'):
                            if ball.model.mesh is not None:
                                currentGeoLODstr = ball.model.mesh.GetGeometryResPath()
                                try:
                                    currentGeoLOD = ball.model.GetLastUsedMeshLod() + 1
                                except AttributeError:
                                    pass

                                paramLst = ball.model.mesh.Find('trinity.TriTextureParameter')
                                currentTexLODstr = {}
                                for param in paramLst:
                                    mip = str(getattr(param.resource, 'gpuMip', ''))
                                    currentTexLODstr[param.resourcePath.lower()] = mip

                                for param, mip in currentTexLODstr.iteritems():
                                    currentTexLODmenu.append(('%s: %s' % (param, mip), blue.pyos.SetClipboardData, (str(param),)))

                        if hasattr(ball.model, 'dna'):
                            sofDNA = ball.model.dna
                        if hasattr(ball.model, 'IsImpostor'):
                            impostorMode = ball.model.IsImpostor()
            gm.append(None)
            gm.append(('charID: ' + self.GetOwnerLabel(slimItem.charID), blue.pyos.SetClipboardData, (str(slimItem.charID),)))
            gm.append(('ownerID: ' + self.GetOwnerLabel(slimItem.ownerID), blue.pyos.SetClipboardData, (str(slimItem.ownerID),)))
            gm.append(('corpID: ' + self.GetOwnerLabel(slimItem.corpID), blue.pyos.SetClipboardData, (str(slimItem.corpID),)))
            gm.append(('allianceID: ' + self.GetOwnerLabel(slimItem.allianceID), blue.pyos.SetClipboardData, (str(slimItem.allianceID),)))
            if hasattr(slimItem, 'districtID'):
                gm.append(('districtID: ' + str(slimItem.districtID), blue.pyos.SetClipboardData, (str(slimItem.districtID),)))
            gm.append(None)
            gm.append(('typeID: ' + str(slimItem.typeID) + ' (%s)' % evetypes.GetName(slimItem.typeID), blue.pyos.SetClipboardData, (str(slimItem.typeID),)))
            gm.append(('groupID: ' + str(slimItem.groupID) + ' (%s)' % evetypes.GetGroupNameByGroup(slimItem.groupID), blue.pyos.SetClipboardData, (str(slimItem.groupID),)))
            gm.append(('categID: ' + str(slimItem.categoryID) + ' (%s)' % evetypes.GetCategoryNameByCategory(slimItem.categoryID), blue.pyos.SetClipboardData, (str(slimItem.categoryID),)))
            graphics_items = [('graphicID: ' + str(graphicID), blue.pyos.SetClipboardData, (str(graphicID),)),
             ('graphicFile: ' + str(graphicFile), blue.pyos.SetClipboardData, (str(graphicFile),)),
             ('SOF DNA: ' + str(sofDNA), blue.pyos.SetClipboardData, (str(sofDNA),)),
             ('materialSetID: ' + str(slimItem.skinMaterialSetID), blue.pyos.SetClipboardData, (str(slimItem.skinMaterialSetID),)),
             ('race: ' + str(raceName), blue.pyos.SetClipboardData, (str(raceName),)),
             None,
             ('current geo LOD: %s %s' % (currentGeoLODstr, currentGeoLOD), blue.pyos.SetClipboardData, (currentGeoLODstr,)),
             ('current tex LODs', currentTexLODmenu),
             ('current impostor mode: ' + str(impostorMode), blue.pyos.SetClipboardData, (str(impostorMode),)),
             None,
             ('Last cleaning: ' + str(dirtLastClean), blue.pyos.SetClipboardData, (str(dirtLastClean),)),
             ('Current dirt value: ' + str(dirtCurrentValue), blue.pyos.SetClipboardData, (str(dirtCurrentValue),)),
             None,
             ('Current kill count: ' + str(currentKillCount), blue.pyos.SetClipboardData, (str(currentKillCount),)),
             ('Randomize kill counter', self.RandomizeKillCounter, (ball,)),
             None]
            if evetypes.GetGroupID(typeID) == const.groupStargate:
                graphics_items.append(('Debug Stargate', lambda *x: StargateDebuggerViewController(itemID).ShowUI()))
            graphics_items.append(('Debug model state', lambda *x: ModelStateDebuggerController(itemID).ShowUI()))
            graphics_items.append(('Trinity Debug Items', modelDebugFunctions.GetTrinityDebugItems(itemID)))
            graphics_items.append(('Textures', self.OpenTextureViewer, (ball,)))
            graphics_items += [None,
             ('Toggle Shield Ellipsoid', modelDebugFunctions.ShowShieldEllipsoid, (itemID,)),
             ('Undocking Locators', modelDebugFunctions.ShowUndockLocations, (itemID,)),
             None,
             ('Save red file', self.SaveRedFile, (ball, graphicFile)),
             ('Toggle display', self.ToggleDisplay, (ball,)),
             ('Open Shader Debugger', self.ToggleShaderDebugger, (ball, graphicID)),
             modelDebugFunctions.GetGMModelInfoMenuItem(itemID)]
            if hasattr(ball, 'ForceAuroraNow'):
                graphics_items += [None, ('Next Aurora in %s' % self._FormatAuroraTime(ball.GetTimeUntilNextAurora()), lambda : None, ()), ('Force Aurora Now', ball.ForceAuroraNow, ())]
            gm.append(('graphics', graphics_items))
            try:
                from carbon.tools.jessica import jessica
                gm.append(('Select in Jessica', lambda *x: jessica.SetCurrentSelection([ball.model])))
            except ImportError:
                pass

            try:
                from platformtools.compatibility.exposure.graphite.graphiteutils import IsGraphiteAttached, setCurrentSelection
                if IsGraphiteAttached():
                    gm.append(('Select in Graphite', lambda *x: setCurrentSelection([ball.model], userDirected=True)))
            except ImportError:
                pass

            if ball is not None:
                if hasattr(ball, 'model'):
                    if ball.model is not None:
                        gm.append(None)
                        gm.append(('audio', [('audio emitters', AudioGmMenu(itemID).GetEmitterMenu())]))
                        gm.append(None)
            gm.append(None)
            gm.append(('Copy Coordinates', self.CopyCoordinates, (itemID,)))
            gm.append(None)
            if HasBehaviorComponent(slimItem.typeID):
                gm.extend(behavior.GetBehaviorGMMenu(slimItem))
            if IsSkyhook(slimItem.typeID):

                def GMSetSkyhookState(skyhookID, skyhookState):
                    sm.RemoteSvc('slash').SlashCmd('/skyhook state %d %d' % (skyhookID, skyhookState))

                import orbitalSkyhook.const as reinforceConst
                states = [ [name, GMSetSkyhookState, [itemID, value]] for value, name in reinforceConst.STATES.iteritems() ]
                gm.append(['GM: Set Skyhook State', states])
        gm.append(None)
        d = {'CHARID': charID,
         'ITEMID': itemID,
         'ID': charID or itemID}
        for i in range(20):
            item = prefs.GetValue('gmmenuslash%d' % i, None)
            if item:
                for k, v in d.iteritems():
                    if ' %s ' % k in item and v:
                        item = item.replace(k, str(v))
                        break
                else:
                    continue

                gm.append((item, sm.RemoteSvc('slash').SlashCmd, (item,)))

        return gm

    @staticmethod
    def _FormatAuroraTime(time):
        time = int(time)
        result = ''
        day = 86400
        if time > day:
            result = '%s days ' % (time / day)
            time = time % day
        hour = 3600
        if time > hour:
            result += '%s hours ' % (time / hour)
            time = time % hour
        minute = 60
        if time > minute:
            result += '%s min ' % (time / minute)
            time = time % minute
        result += '%s sec' % time
        return result

    @staticmethod
    def SaveRedFile(ball, graphicFile):
        return modelDebugFunctions.SaveRedFile(ball, graphicFile)

    @staticmethod
    def RandomizeKillCounter(ball):
        if ball is not None:
            if hasattr(ball, 'model'):
                if ball.model is not None:
                    if hasattr(ball.model, 'displayKillCounterValue'):
                        ball.model.displayKillCounterValue = random.randint(0, 999)

    @staticmethod
    def ToggleDisplay(ball):
        if ball is not None:
            if hasattr(ball, 'model'):
                if ball.model is not None:
                    if hasattr(ball.model, 'display'):
                        ball.model.display = not ball.model.display

    @staticmethod
    def ToggleShaderDebugger(ball, graphicID):
        if ball is not None:
            if hasattr(ball, 'model'):
                if ball.model is not None:
                    ShaderDebugger(object=ball.model, graphicID=graphicID)

    @staticmethod
    def OpenTextureViewer(ball):
        if ball is not None:
            if hasattr(ball, 'model'):
                if ball.model is not None:
                    TextureWindow(object=ball.model)

    @staticmethod
    def GetGMStructureStateMenu(itemID = None, slimItem = None):
        subMenu = MenuList()
        if hasattr(slimItem, 'posState') and slimItem.posState is not None:
            currentState = slimItem.posState
            if currentState not in pos.ONLINE_STABLE_STATES:
                if currentState == pos.STRUCTURE_ANCHORED:
                    subMenu.append(('Online', sm.RemoteSvc('slash').SlashCmd, ('/pos online ' + str(itemID),)))
                    subMenu.append(('Unanchor', sm.RemoteSvc('slash').SlashCmd, ('/pos unanchor ' + str(itemID),)))
                elif currentState == pos.STRUCTURE_UNANCHORED:
                    subMenu.append(('Anchor', sm.RemoteSvc('slash').SlashCmd, ('/pos anchor ' + str(itemID),)))
            else:
                subMenu.append(('Offline', sm.RemoteSvc('slash').SlashCmd, ('/pos offline ' + str(itemID),)))
        return subMenu

    @staticmethod
    def GetGMBallsAndBoxesMenu(itemID = None, slimItem = None, charID = None, invItem = None, mapItem = None):
        return modelDebugFunctions.GetGMBallsAndBoxesMenu(itemID, slimItem, charID, invItem, mapItem)

    @staticmethod
    def GetOwnerLabel(ownerID):
        return menuFunctions.GetOwnerLabel(ownerID)

    @staticmethod
    def ImFleetLeaderOrCommander():
        return sm.GetService('fleet').IsCommanderOrBoss()

    @staticmethod
    def CheckImFleetLeader():
        return session.fleetrole == evefleet.fleetRoleLeader

    @staticmethod
    def CheckImWingCmdr():
        return session.fleetrole == evefleet.fleetRoleWingCmdr

    @staticmethod
    def CheckImSquadCmdr():
        return session.fleetrole == evefleet.fleetRoleSquadCmdr

    def GetWarpOptions(self, FleetWarpToMethod, WarpToMethod, itemID):
        if not InShipInSpace():
            return MenuList()
        warptoLabel = movementFunctions.GetDefaultWarpToLabel()
        defaultWarpDist = self.GetDefaultActionDistance('WarpTo')
        return self._GetWarpOptions(FleetWarpToMethod, WarpToMethod, itemID, warptoLabel, defaultWarpDist)

    def _GetWarpOptions(self, FleetWarpToMethod, WarpToMethod, itemID, warptoLabel, warpDist):
        ret = MenuList([(warptoLabel, WarpToMethod, (itemID, warpDist)), (MenuLabel('UI/Inflight/Submenus/WarpToWithin', {'distance': 0}), self.WarpToMenu(WarpToMethod, itemID))])
        formationName = {'fleetFormation': GetSelectedFormationName()}
        if self.CheckImFleetLeader():
            ret.extend([(MenuLabel('UI/Fleet/WarpFleet', formationName), FleetWarpToMethod, (itemID, float(warpDist))), (MenuLabel('UI/Fleet/FleetSubmenus/WarpFleetToWithin', formationName), self.WarpToMenu(FleetWarpToMethod, itemID))])
        elif self.CheckImWingCmdr():
            ret.extend([(MenuLabel('UI/Fleet/WarpWing', formationName), FleetWarpToMethod, (itemID, float(warpDist))), (MenuLabel('UI/Fleet/FleetSubmenus/WarpWingToWithin', formationName), self.WarpToMenu(FleetWarpToMethod, itemID))])
        elif self.CheckImSquadCmdr():
            ret.extend([(MenuLabel('UI/Fleet/WarpSquad', formationName), FleetWarpToMethod, (itemID, float(warpDist))), (MenuLabel('UI/Fleet/FleetSubmenus/WarpSquadToWithin', formationName), self.WarpToMenu(FleetWarpToMethod, itemID))])
        return ret

    def SolarsystemScanMenu(self, scanResultID):
        WarpToMethod = self.WarpToScanResult
        FleetWarpToMethod = self.WarpFleetToScanResult
        itemID = scanResultID
        return self.GetWarpOptions(FleetWarpToMethod, WarpToMethod, itemID)

    def WarpToScanResult(self, scanResultID, minRange = None):
        self._WarpXToScanResult(scanResultID, minRange)

    def WarpFleetToScanResult(self, scanResultID, minRange = None):
        self._WarpXToScanResult(scanResultID, minRange, fleet=True)

    @staticmethod
    def _WarpXToScanResult(scanResultID, minRange = None, fleet = False):
        michelle = sm.GetService('michelle')
        bp = michelle.GetRemotePark()
        if bp is not None:
            sm.GetService('autoPilot').CancelSystemNavigation()
            itemID, typeID = sm.GetService('sensorSuite').GetPositionalSiteItemIDFromTargetID(scanResultID)
            if itemID is None:
                subject, subjectID = 'scan', scanResultID
            else:
                subject, subjectID = 'item', itemID
            michelle.CmdWarpToStuff(subject, subjectID, minRange=minRange, fleet=fleet)
            sm.StartService('space').WarpDestination(celestialID=scanResultID)

    @staticmethod
    def IsItemDead(ballPark, itemID):
        ball = ballPark.GetBall(itemID)
        return not ball or ball.isMoribund

    def BookmarkMenu(self, bookmark):
        return MergeMenus([self._BookmarkMenu(bookmark)])

    @telemetry.ZONE_METHOD
    def _BookmarkMenu(self, bookmark):
        typeID = bookmark.typeID
        itemID = bookmark.itemID or bookmark.locationID
        menuEntries = MenuList()
        slimItem = None
        bp = sm.StartService('michelle').GetBallpark()
        if bp:
            slimItem = bp.GetInvItem(itemID)
        infoArgs = (slimItem.typeID,
         slimItem.itemID,
         0,
         None,
         None) if slimItem else (typeID,
         itemID,
         0,
         None,
         None)
        menuEntries += [[MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, infoArgs]]
        if not self.sessionChecker:
            self.sessionChecker = SessionChecker(session, sm)
        bm = BookmarkChecker(slimItem or (itemID, typeID), bookmark, cfg, self.sessionChecker)
        mapItemID, mapTypeID = bm.GetMapIDs()
        groupID = bm.item.groupID
        groupName = evetypes.GetGroupNameByGroup(groupID)
        if bm.IsStructure():
            menuEntries.extend(GetStructureMenu(bm))
        if bm.OfferDock():
            menuEntries += [[MenuLabel('UI/Inflight/DockInStation'),
              self.Dock,
              (itemID,),
              None,
              None,
              'DockInStation']]
        if bm.OfferStargateJump():
            jumpInfo = bm.GetJumpInfo()
            cfg.evelocations.Prime([jumpInfo.toCelestialID, jumpInfo.locationID])
            menuEntries.append(MenuEntryData(MenuLabel('UI/Inflight/Jump'), lambda : self.StargateJump(itemID, typeID, jumpInfo.toCelestialID, jumpInfo.locationID)))
            if not bm.isWaypoint():
                menuEntries += [[MenuLabel('UI/Inflight/AddFirstWaypoint'), sm.StartService('starmap').SetWaypoint, (jumpInfo.locationID,)]]
        if bm.OfferJumpThroughStargate():
            localStargate = FindLocalStargate(bm.GetWaypointSolarsystemID())
            if localStargate:
                menuEntries += [[MenuLabel('UI/Inflight/JumpThroughStargate'),
                  self.StargateJump,
                  (localStargate.itemID,
                   localStargate.typeID,
                   localStargate.jumps[0].toCelestialID,
                   localStargate.jumps[0].locationID),
                  eveicon.jump_to]]
        if bm.OfferJumpThroughStructureJumpGate():
            localJumpBridge = FindLocalJumpGateForDestinationPath(bm.GetWaypointSolarsystemID())
            if localJumpBridge:
                menuEntries += [[MenuLabel('UI/Inflight/JumpThroughJumpgate'),
                  self.JumpThroughStructureJumpBridge,
                  (localJumpBridge.itemID,),
                  eveicon.jump_to]]
        if bm.OfferWarpTo():
            defaultWarpDist = self.GetDefaultActionDistance('WarpTo')
            if not bm.IsDeadspaceBookmark():
                menuEntries.append(WarpToMenuEntryData(MenuLabel('UI/Inflight/Submenus/WarpToWithin'), func=lambda : movementFunctions.WarpToBookmark(bookmark, float(defaultWarpDist)), subMenuData=self.WarpToMenu(movementFunctions.WarpToBookmark, bookmark)))
            else:
                menuEntries += [[MenuLabel('UI/Inflight/WarpToBookmark'), movementFunctions.WarpToBookmark, (bookmark, float(defaultWarpDist))]]
            formationName = {'fleetFormation': GetSelectedFormationName()}
            if bm.session.IsPilotFleetLeader():
                label = MenuLabel('UI/Fleet/WarpFleetToLocation', formationName) if bm.IsDeadspaceBookmark() else MenuLabel('UI/Fleet/WarpFleetToLocationWithinDistance', {'warpToDistance': fmtutil.FmtDist(float(defaultWarpDist)),
                 'fleetFormation': GetSelectedFormationName()})
                menuEntries += [[label, movementFunctions.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                menuEntries += [[MenuLabel('UI/Fleet/FleetSubmenus/WarpFleetToWithin', formationName), self.WarpToMenu(movementFunctions.WarpFleetToBookmark, bookmark)]]
            if bm.session.IsPilotWingCommander():
                label = MenuLabel('UI/Fleet/WarpWingToLocation', formationName) if bm.IsDeadspaceBookmark() else MenuLabel('UI/Fleet/WarpWingToLocationWithinDistance', {'warpToDistance': fmtutil.FmtDist(float(defaultWarpDist)),
                 'fleetFormation': GetSelectedFormationName()})
                menuEntries += [[label, movementFunctions.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                menuEntries += [[MenuLabel('UI/Fleet/FleetSubmenus/WarpWingToWithin', formationName), self.WarpToMenu(movementFunctions.WarpFleetToBookmark, bookmark)]]
            if bm.session.IsPilotSquadCommander():
                label = MenuLabel('UI/Fleet/WarpSquadToLocation', formationName) if bm.IsDeadspaceBookmark() else MenuLabel('UI/Fleet/WarpSquadToLocationWithinDistance', {'warpToDistance': fmtutil.FmtDist(float(defaultWarpDist)),
                 'fleetFormation': GetSelectedFormationName()})
                menuEntries += [[label, movementFunctions.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                menuEntries += [[MenuLabel('UI/Fleet/FleetSubmenus/WarpSquadToWithin', formationName), self.WarpToMenu(movementFunctions.WarpFleetToBookmark, bookmark)]]
        if bm.OfferApproachLocation():
            menuEntries += [[MenuLabel('UI/Inflight/ApproachLocationActionGroup'), movementFunctions.ApproachLocation, (bookmark,)]]
        if bm.OfferAlignTo():
            menuEntries += [[MenuLabel('UI/Inflight/AlignTo'), self.AlignToBookmark, (getattr(bookmark, 'bookmarkID', None),)]]
        if bm.OfferSetDestination():
            menuEntries.append(MenuEntryData(MenuLabel('UI/Inflight/SetDestination'), lambda : sm.StartService('starmap').SetWaypoint(mapItemID, True)))
        if bm.OfferAddWaypoint():
            menuEntries += [[MenuLabel('UI/Inflight/AddWaypoint'), sm.StartService('starmap').SetWaypoint, (mapItemID,)]]
        elif bm.isWaypoint():
            menuEntries += [[MenuLabel('UI/Inflight/RemoveWaypoint'), sm.StartService('starmap').ClearWaypoints, (mapItemID,)]]
        if bm.OfferBroadcastTravelTo():
            menuEntries += [None]
            menuEntries += [MenuEntryData(MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastTravelTo'), lambda : sm.GetService('fleet').SendBroadcast_TravelTo(mapItemID), texturePath=iconsByBroadcastType[BROADCAST_TRAVEL_TO])]
        if bm.OfferLookAtObject():
            menuEntries += [[MenuLabel('UI/Inflight/LookAtObject'), self.TryLookAt, (itemID,)]]
            if bool(gfxsettings.Get(gfxsettings.UI_ADVANCED_CAMERA)):
                menuEntries += [[MenuLabel('UI/Inflight/SetAsCameraParent'), self.SetParent, (itemID,)]]
        if bm.OfferResetCamera():
            menuEntries += [[MenuLabel('UI/Inflight/ResetCamera'), sm.GetService('sceneManager').GetActiveSpaceCamera().ResetCamera]]
        if bm.OfferShowLocationOnMap():
            menuEntries += [None]
            menuEntries += [[MenuLabel('UI/Commands/ShowLocationOnMap'), self.ShowInMap, (mapItemID,)]]
            menuEntries += [[MenuLabel('UI/Inflight/ShowInMapBrowser', {'locationType': groupName}), self.ShowInMapBrowser, (mapItemID,)]]
        if bm.OfferAvoidLocation():
            menuEntries += [[MenuLabel('UI/Inflight/AvoidLocation', {'theLocation': mapItemID,
               'locationType': groupName}), self.clientPathfinderService.AddAvoidanceItem, (mapItemID,)]]
        elif bm.OfferStopAvoidingLocation():
            menuEntries += [[MenuLabel('UI/Inflight/StopAvoidingLocation', {'theLocation': mapItemID,
               'locationType': groupName}), self.clientPathfinderService.RemoveAvoidanceItem, (mapItemID,)]]
        if bm.OfferViewPlanetaryProduction():
            menuEntries += [[MenuLabel('UI/PI/Common/ViewInPlanetMode'), self.ViewPlanetaryProduction, (itemID,)]]
        elif bm.OfferExitPlanetaryProduction():
            menuEntries += [[MenuLabel('UI/PI/Common/ExitPlanetMode'), sm.GetService('viewState').CloseSecondaryView, ()]]
        if bm.OfferEditBookmark():
            menuEntries += [[MenuLabel('UI/Inflight/EditBookmark'), sm.GetService('addressbook').EditBookmark, (bookmark,)]]
            menuEntries += [[MenuLabel('UI/Inflight/RemoveBookmark'), sm.GetService('addressbook').DeleteBookmarks, ([getattr(bookmark, 'bookmarkID', None)],)]]
        if bm.OfferSetName():
            menuEntries += [[MenuLabel('UI/Commands/SetName'), self.SetName, (bm.item,)]]
        if bm.OfferScoopToCargoHold():
            menuEntries += [[MenuLabel('UI/Inflight/ScoopToCargoHold'), self.Scoop, (itemID, typeID)]]
        if bm.OfferEditProfileForStructure():
            menuEntries += [[MenuLabel('UI/Commands/EditProfileForStructure'), openFunctions.OpenProfileSettingsForStructure, (itemID,)]]
        if bm.OfferToggleOverviewVisibility():
            menuEntries.append(overviewMenuUtil.GetToggleEntry(groupID))
        if session.role & (ROLE_GML | ROLE_WORLDMOD):
            menuEntries.insert(0, ('GM / WM Extras', ('isDynamic', self.GetGMMenu, (itemID,
               slimItem,
               None,
               None,
               None,
               typeID))))
        del bm
        return menuEntries

    @telemetry.ZONE_METHOD
    def CelestialMenu(self, itemID, mapItem = None, slimItem = None, typeID = None, parentID = None, hint = None):
        if type(itemID) == list:
            menus = []
            for data in itemID:
                m = self._CelestialMenu(data, hint, len(itemID) > 1)
                menus.append(m)

            return MergeMenus(menus)
        else:
            ret = self._CelestialMenu((itemID,
             mapItem,
             slimItem,
             typeID,
             parentID), hint)
            return MergeMenus([ret])

    def UnmergedCelestialMenu(self, slimItem):
        return self._CelestialMenu((slimItem.itemID,
         None,
         slimItem,
         None,
         None))

    @telemetry.ZONE_METHOD
    def _CelestialMenu(self, data, hint = None, multi = 0):
        itemID, mapItem, slimItem, typeID, parentID = data
        categoryID = None
        dist = False
        bp = sm.StartService('michelle').GetBallpark()
        if bp:
            slimItem = slimItem or bp.GetInvItem(itemID)
            otherBall = bp.GetBall(itemID)
            ownBall = bp.GetBall(session.shipid)
            dist = otherBall and ownBall and max(0, otherBall.surfaceDist)
        if slimItem:
            typeID = slimItem.typeID
            parentID = sm.StartService('map').GetParent(itemID) or session.solarsystemid
            categoryID = slimItem.categoryID
        mapItemID = None
        mapFunctionID = itemID
        mapItem = mapItem or sm.StartService('map').GetItem(itemID, categoryID=categoryID)
        if mapItem:
            typeID = mapItem.typeID
            parentID = getattr(mapItem, 'locationID', None) or const.locationUniverse
            if typeID == const.groupSolarSystem:
                mapItemID = mapItem.itemID
        if typeID is None:
            return []
        groupID = evetypes.GetGroupID(typeID)
        if categoryID == const.categoryCharge and groupID != const.groupScannerProbe:
            return []
        if groupID in [const.groupSolarSystem, const.groupConstellation, const.groupRegion] and parentID != session.solarsystemid:
            mapFunctionID = mapItemID or itemID
        if parentID is None and groupID == const.groupStation and itemID:
            tmp = sm.StartService('ui').GetStationStaticInfo(itemID)
            if tmp is not None:
                parentID = tmp.solarSystemID
        niceRange = dist is not False and fmtutil.FmtDist(dist) or localization.GetByLabel('UI/Inflight/NoDistanceAvailable')
        defaultWarpDist = self.GetDefaultActionDistance('WarpTo')
        groupName = evetypes.GetGroupNameByGroup(groupID)
        menuEntries = MenuList()
        if not self.sessionChecker:
            self.sessionChecker = SessionChecker(session, sm)
        celestial = CelestialChecker(slimItem or (itemID, typeID), cfg, self.sessionChecker)
        celestial.isMultiSelection = bool(multi)
        if celestial.OfferDroneMenu():
            for droneEntry in self.DroneMenu([[itemID,
              typeID,
              slimItem.ownerID,
              slimItem.locationID]], 1):
                menuEntries += droneEntry

        if celestial.OfferUseFittingService():
            menuEntries += [[MenuLabel('UI/Fitting/UseFittingService'), uicore.cmd.GetCommandToExecute('OpenFitting'), ()]]
        if celestial.OfferBoardShip():
            boardCmd = self.Board if self.sessionChecker.IsPilotInShipInSpace() else sm.GetService('structureControl').EjectFromStructure
            if self.sessionChecker.IsPilotControllingStructure():
                structureTypeID = sm.GetService('structureDirectory').GetStructureInfo(session.structureid).typeID
                if idCheckers.IsDockableStructure(structureTypeID):
                    boardCmd = None
            if boardCmd:
                menuEntries += [[MenuLabel('UI/Inflight/BoardShip'), boardCmd, (itemID,)]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/BoardShip'] = self.GetUnavailableText(celestial)
        if celestial.OfferOpenCargo():
            menuEntries += [[MenuLabel('UI/Commands/OpenCargo'),
              self.OpenCargo,
              [itemID],
              None,
              None,
              'OpenCargo']]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Commands/OpenCargo'] = self.GetUnavailableText(celestial)
        if celestial.OfferEjectFromShip():
            menuEntries += [[MenuLabel('UI/Inflight/EjectFromShip'), self.Eject]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/EjectFromShip'] = self.GetUnavailableText(celestial)
        if celestial.OfferSetName():
            menuEntries += [[MenuLabel('UI/Commands/SetName'), self.SetName, (celestial.item,)]]
        if celestial.OfferBroadcastEnemySpotted():
            senderID, = sm.GetService('fleet').CurrentFleetBroadcastOnItem(itemID, state.gbEnemySpotted)
            menuEntries += [[MenuLabel('UI/Fleet/FleetSubmenus/BroadCastEnemySpotted', {'character': senderID}), ('isDynamic', self.CharacterMenu, (senderID,))]]
        if celestial.OfferStopMyShip():
            label = 'UI/Inflight/StopMyCapsule' if groupID == const.groupCapsule else 'UI/Inflight/StopMyShip'
            menuEntries += [[MenuLabel(label), movementFunctions.StopMyShip]]
        elif celestial.failure_label:
            label = 'UI/Inflight/StopMyCapsule' if groupID == const.groupCapsule else 'UI/Inflight/StopMyShip'
            fail_text = self.GetUnavailableText(celestial)
            menuEntries.reasonsWhyNotAvailable[label] = fail_text
            menuEntries.reasonsWhyNotAvailable['UI/Commands/OpenMyCargo'] = fail_text
        if celestial.OfferStoreVessel():
            menuEntries += [[MenuLabel('UI/Inflight/POS/StoreVesselInSMA'), self.StoreVessel, (itemID, session.shipid)]]
        menuEntries.extend(openFunctions.GetOpenShipHoldMenus(celestial))
        if celestial.OfferConfigureShipCloneFacility():
            menuEntries += [[MenuLabel('UI/Commands/ConfigureShipCloneFacility'), self.ShipCloneConfig, (itemID,)]]
        if celestial.OfferReconnectToLostDrones():
            menuEntries += [[MenuLabel('UI/Commands/ReconnectToLostDrones'), self.ReconnectToDrones]]
        if celestial.OfferSafeLogoff():
            if AllowCharacterLogoff(sm.GetService('machoNet')):
                menuEntries += [[MenuLabel('UI/Inflight/SafeLogoff'), uicore.cmd.CmdLogOff]]
            else:
                menuEntries += [[MenuLabel('UI/Inflight/SafeLogoff/SafeLogoffQuitGame'), self.SafeLogoff]]
        if celestial.OfferSelfDestructShip():
            menuEntries += [[MenuLabel('UI/Inflight/SelfDestructShipOrPod'), self.SelfDestructShip, (itemID,)]]
        elif celestial.OfferAbortSelfDestructShip():
            menuEntries += [[MenuLabel('UI/Inflight/AbortSelfDestruct'), self.AbortSelfDestructShip, (itemID,)]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/SelfDestructShipOrPod'] = self.GetUnavailableText(celestial)
        if celestial.OfferEnterStarbasePassword():
            menuEntries += [[MenuLabel('UI/Inflight/POS/EnterStarbasePassword'), self.EnterPOSPassword]]
        if celestial.OfferActivateAutopilot():
            menuEntries += [[MenuLabel('UI/Inflight/ActivateAutopilot'), self.ToggleAutopilot, (1,)]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/ActivateAutopilot'] = self.GetUnavailableText(celestial)
        if celestial.OfferDeactivateAutopilot():
            menuEntries += [[MenuLabel('UI/Inflight/DeactivateAutopilot'), self.ToggleAutopilot, (0,)]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/DeactivateAutopilot'] = self.GetUnavailableText(celestial)
        if celestial.IsMyActiveShip():
            if self.sessionChecker.isShipJumpCapable():
                menuEntries += [[MenuLabel('UI/CapitalNavigation/CapitalNavigationWindow/OpenJumpNavigation'), uicore.cmd.GetCommandToExecute('OpenCapitalNavigation'), ()]]
                menuEntries += [[MenuLabel('UI/Inflight/Submenus/JumpTo'), ('isDynamic', self.GetHybridBeaconJumpMenu, [])]]
                if self.sessionChecker.canOpenJumpPortal():
                    menuEntries += [[MenuLabel('UI/Inflight/Submenus/BridgeTo'), ('isDynamic', self.GetHybridBridgeMenu, [])]]
                if self.sessionChecker.canPerformGroupJump():
                    menuEntries += [[MenuLabel('UI/Inflight/Submenus/ConduitJumpTo'), ('isDynamic', self.GetHybridBeaconGroupJumpMenu, [])]]
        if celestial.OfferMoonMiningPointMenu():
            menuEntries.extend(self.GetMoonMiningPointMenu(celestial, slimItem))
        if celestial.OfferWarpTo():
            if celestial.IsShip() and self.sessionChecker.isPilotInSameFleetAs(slimItem.charID):
                warpFn = self.WarpToMember
                warpID = slimItem.charID
            else:
                warpFn = movementFunctions.WarpToItem
                warpID = itemID
            menuEntries.append(WarpToMenuEntryData(MenuLabel('UI/Inflight/Submenus/WarpToWithin'), func=lambda : warpFn(warpID, float(defaultWarpDist)), subMenuData=self.WarpToMenu(warpFn, warpID)))
            if self.sessionChecker.IsPilotFleetMember():
                warpFleetFn = self.WarpFleetToMember if warpFn is self.WarpToMember else self.WarpFleet
                formationName = {'fleetFormation': GetSelectedFormationName()}
                if self.sessionChecker.IsPilotFleetLeader():
                    menuEntries += [[MenuLabel('UI/Fleet/WarpFleet', formationName), warpFleetFn, (warpID, float(defaultWarpDist))]]
                    menuEntries += [[MenuLabel('UI/Fleet/FleetSubmenus/WarpFleetToWithin', formationName), self.WarpToMenu(warpFleetFn, warpID)]]
                if self.sessionChecker.IsPilotWingCommander():
                    menuEntries += [[MenuLabel('UI/Fleet/WarpWing', formationName), warpFleetFn, (warpID, float(defaultWarpDist))]]
                    menuEntries += [[MenuLabel('UI/Fleet/FleetSubmenus/WarpWingToWithin', formationName), self.WarpToMenu(warpFleetFn, warpID)]]
                if self.sessionChecker.IsPilotSquadCommander():
                    menuEntries += [[MenuLabel('UI/Fleet/WarpSquad', formationName), warpFleetFn, (warpID, float(defaultWarpDist))]]
                    menuEntries += [[MenuLabel('UI/Fleet/FleetSubmenus/WarpSquadToWithin', formationName), self.WarpToMenu(warpFleetFn, warpID)]]
        elif celestial.failure_label:
            fail_text = self.GetUnavailableText(celestial)
            menuEntries.reasonsWhyNotAvailable[movementFunctions.GetDefaultWarpToLabel().labelPath] = fail_text
            if 'UI/Inflight/WarpToMoonMiningPoint' not in menuEntries.reasonsWhyNotAvailable:
                menuEntries.reasonsWhyNotAvailable['UI/Inflight/WarpToMoonMiningPoint'] = fail_text
        menuEntries += [None]
        if celestial.OfferApproachObject():
            menuEntries.append(MenuEntryData(MenuLabel('UI/Inflight/ApproachObject'), lambda : movementFunctions.Approach(itemID), internalName='Approach', typeID=typeID))
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/ApproachObject'] = self.GetUnavailableText(celestial)
        if celestial.OfferOrbitObject():
            menuEntries.append(OrbitMenuEntryData(MenuLabel('UI/Inflight/OrbitObject'), func=lambda : movementFunctions.Orbit(itemID), subMenuData=movementFunctions.GetOrbitMenu(itemID, typeID, dist, niceRange), internalName='Orbit', typeID=typeID))
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/OrbitObject'] = self.GetUnavailableText(celestial)
        if celestial.OfferKeepAtRange():
            menuEntries.append(KeepAtRangeMenuEntryData(MenuLabel('UI/Inflight/Submenus/KeepAtRange'), func=lambda : movementFunctions.KeepAtRange(itemID), subMenuData=movementFunctions.GetKeepAtRangeMenu(itemID, typeID, dist, niceRange)))
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/Submenus/KeepAtRange'] = self.GetUnavailableText(celestial)
        if celestial.OfferAlignTo():
            menuEntries.append(MenuEntryData(MenuLabel('UI/Inflight/AlignTo'), lambda : self.AlignTo(itemID)))
        if celestial.OfferStructureMenu():
            menuEntries.extend(GetStructureMenu(celestial))
        if celestial.OfferBroadcastTarget():
            menuEntries += [MenuEntryData(MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastTarget'), lambda : sm.GetService('fleet').SendBroadcast_Target(itemID), texturePath=iconsByBroadcastType[BROADCAST_TARGET])]
        if celestial.OfferBroadcastWarpTo():
            menuEntries += [MenuEntryData(MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastWarpTo'), lambda : sm.GetService('fleet').SendBroadcast_WarpTo(itemID, typeID), texturePath=iconsByBroadcastType[BROADCAST_WARP_TO])]
        if celestial.OfferBroadcastAlignTo():
            menuEntries += [MenuEntryData(MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastAlignTo'), lambda : sm.GetService('fleet').SendBroadcast_AlignTo(itemID, typeID), texturePath=iconsByBroadcastType[BROADCAST_ALIGN_TO])]
        if celestial.OfferBroadcastJumpTo():
            menuEntries += [MenuEntryData(MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastJumpTo'), lambda : sm.GetService('fleet').SendBroadcast_JumpTo(itemID, typeID), texturePath=iconsByBroadcastType[BROADCAST_JUMP_TO])]
        if celestial.OfferJumpFleetThroughToSystem():
            menuEntries += [None]
            menuEntries += [[MenuLabel('UI/Fleet/JumpThroughToSystem', {'solarsystem': celestial.GetActiveFleetBridge()[0]}), self.JumpThroughFleet, (slimItem.charID or slimItem.ownerID, itemID)]]
        if celestial.OfferBroadcastHealTarget():
            menuEntries += [MenuEntryData(MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastHealTarget'), lambda : sm.GetService('fleet').SendBroadcast_Heal_Target(itemID), texturePath=eveicon.heal_first_aid)]
        if celestial.OfferDock():
            menuEntries.append(MenuEntryData(MenuLabel('UI/Inflight/DockInStation'), lambda : self.Dock(itemID), internalName='DockInStation'))
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/DockInStation'] = self.GetUnavailableText(celestial)
        if celestial.IsDockable() and celestial.session.isPilotWarping() and not celestial.OfferDock():
            self.AddDisabledEntryForWarp(menuEntries, 'UI/Inflight/DockInStation')
        if celestial.OfferStargateJump():
            jumpInfo = celestial.GetJumpInfo()
            cfg.evelocations.Prime([jumpInfo.toCelestialID, jumpInfo.locationID])
            menuEntries.append(MenuEntryData(MenuLabel('UI/Inflight/Jump'), lambda : self.StargateJump(celestial.item.itemID, celestial.item.typeID, jumpInfo.toCelestialID, jumpInfo.locationID), internalName='Jump'))
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/Jump'] = self.GetUnavailableText(celestial)
        if celestial.IsStargate() and celestial.session.isPilotWarping() and not celestial.OfferStargateJump():
            self.AddDisabledEntryForWarp(menuEntries, 'UI/Inflight/Jump')
        if celestial.OfferShipcasterJump():
            targetSolarsystemID, _ = GetTargetForShipcaster(itemID)
            text = localization.GetByLabel('UI/Inflight/JumpByShipcasterToSystem', solarsystem=targetSolarsystemID)
            menuEntries.append(MenuEntryData(MenuLabel('UI/Inflight/JumpByShipcaster', {'text': text}), lambda : self.JumpThroughShipcaster(celestial.item.itemID), internalName='JumpThroughShipcaster'))
        elif celestial.failure_label:
            failureText, disabledOption = GetFailureTextAndDisabledOption(itemID, celestial)
            if disabledOption:
                menuEntries.append(disabledOption)
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/JumpByShipcaster'] = failureText
        if celestial.OfferAddFirstWaypoint():
            jumpInfo = celestial.GetJumpInfo()
            cfg.evelocations.Prime([jumpInfo.toCelestialID, jumpInfo.locationID])
            menuEntries += [[MenuLabel('UI/Inflight/AddFirstWaypoint'), sm.StartService('starmap').SetWaypoint, (jumpInfo.locationID, False, True)]]
        if celestial.OfferActivateGate():
            crimewatchSvc = sm.GetService('crimewatchSvc')
            requiredSafetyLevel, _, _ = crimewatchSvc.GetRequiredSafetyLevelForActivatingAccelerationGate(itemID)
            if requiredSafetyLevel == const.shipSafetyLevelNone:
                menuClass = eveMenu.CriminalMenuEntryView
            elif requiredSafetyLevel == const.shipSafetyLevelPartial:
                menuClass = eveMenu.SuspectMenuEntryView
            else:
                menuClass = None
            menuEntries += [[MenuLabel('UI/Inflight/ActivateGate'),
              self.GetAbyssalGateFunction(typeID) or self.ActivateAccelerationGate,
              (itemID,),
              None,
              menuClass]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/ActivateGate'] = self.GetUnavailableText(celestial)
            if celestial.IsWarpGate() and self.sessionChecker.isPilotWarping():
                self.AddDisabledEntryForWarp(menuEntries, 'UI/Inflight/ActivateGate')
        if celestial.OfferActivatRandomTraceGate():
            menuEntries += [[MenuLabel('UI/Inflight/ActivateTraceGate'), self.ActivateRandomJumpTraceGate, (itemID,)]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/ActivateTraceGate'] = self.GetUnavailableText(celestial)
        if celestial.OfferEnterWormhole():
            menuEntries += [[MenuLabel('UI/Inflight/EnterWormhole'), self.EnterWormhole, (itemID,)]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/EnterWormhole'] = self.GetUnavailableText(celestial)
            if celestial.IsWormhole() and self.sessionChecker.isPilotWarping():
                self.AddDisabledEntryForWarp(menuEntries, 'UI/Inflight/EnterWormhole')
        menuEntries += [None]
        if celestial.OfferLookAtObject():
            menuEntries.append(MenuEntryData(MenuLabel('UI/Inflight/LookAtObject'), lambda : self.TryLookAt(itemID)))
            if bool(gfxsettings.Get(gfxsettings.UI_ADVANCED_CAMERA)):
                menuEntries += [[MenuLabel('UI/Inflight/SetAsCameraParent'), self.SetParent, (itemID,)]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/LookAtObject'] = self.GetUnavailableText(celestial)
        if celestial.OfferSetAsCameraInterest():
            menuEntries.append(MenuEntryData(MenuLabel('UI/Inflight/SetAsCameraInterest'), lambda : self.SetInterest(itemID)))
        if celestial.OfferResetCamera():
            menuEntries += [[MenuLabel('UI/Inflight/ResetCamera'), sm.GetService('sceneManager').GetActiveSpaceCamera().ResetCamera]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/ResetCamera'] = self.GetUnavailableText(celestial)
        if celestial.OfferAccessCustomOfficePoco() or celestial.OfferAccessCustomOfficeSkyhook():
            menuEntries += [None]
            menuEntries += [[MenuLabel('UI/PI/Common/AccessCustomOffice'), self.OpenPlanetCustomsOfficeImportWindow, [itemID]]]
        if celestial.OfferAccessOrbitalSkyhookOffice():
            menuEntries += [[MenuLabel('UI/OrbitalSkyhook/SkyhookWnd/AccessOrbitalSkyhookOffice'), self.OpenOrbitalSkyhookWindow, [itemID]]]
        if celestial.OfferAccessMercenaryDen():
            menuEntries.append(MenuEntryData(text=MenuLabel('UI/Sovereignty/MercenaryDen/ConfigurationWindow/ConfigureMercenaryDen'), func=lambda : self.OpenMercenaryDen(itemID), texturePath=eveicon.mercenary_den))
        menuEntries += [None]
        if celestial.OfferAccessMoonMaterialBay():
            menuEntries += [[MenuLabel('UI/Inflight/OpenMoonMaterialBay'), self.OpenMoonMaterialBay, [itemID]]]
        if celestial.OfferOpenUpgradeHold():
            menuEntries += [[MenuLabel('UI/DustLink/OpenUpgradeHold'), self.OpenUpgradeWindow, [itemID]]]
        if celestial.OfferAbandonWreck():
            menuEntries += [[MenuLabel('UI/Inflight/AbandonWreack'), self.AbandonLoot, [itemID]]]
            menuEntries += [[MenuLabel('UI/Inflight/AbandonAllWrecks'), self.AbandonAllLoot, [itemID]]]
        if celestial.OfferAbandonCargo():
            menuEntries += [[MenuLabel('UI/Inflight/AbandonCargo'), self.AbandonLoot, [itemID]]]
            menuEntries += [[MenuLabel('UI/Inflight/AbandonAllCargo'), self.AbandonAllLoot, [itemID]]]
        if celestial.OfferScoopToCargoHold():
            menuEntries += [[MenuLabel('UI/Inflight/ScoopToCargoHold'), self.Scoop, (itemID, typeID)]]
        if celestial.OfferScoopToFleetHangar():
            menuEntries += [[MenuLabel('UI/Inflight/ScoopToFleetHangar'), self.ScoopToFleetHangar, (itemID, typeID)]]
        if celestial.OfferScoopToFighterBay():
            menuEntries += [[MenuLabel('UI/Inflight/ScoopToFighterBay'), self.ScoopToFighterBay, (itemID, typeID)]]
        if celestial.OfferScoopToShipMaintenanceBay():
            menuEntries += [[MenuLabel('UI/Inflight/POS/ScoopToShipMaintenanceBay'), self.ScoopSMA, (itemID,)]]
        if celestial.OfferScoopToInfrastructureHold():
            menuEntries += [[MenuLabel('UI/Inflight/ScoopToInfrastructureHold'), self.ScoopToInfrastructureHold, (itemID, typeID)]]
        if celestial.OfferAnchorPOSObject():
            menuEntries += [[MenuLabel('UI/Inflight/POS/AnchorObject'), self.AnchorObject, (itemID, 1)]]
        if celestial.OfferUnanchorPOSObject():
            menuEntries += [[MenuLabel('UI/Inflight/UnanchorObject'), self.AnchorObject, (itemID, 0)]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/UnanchorObject'] = self.GetUnavailableText(celestial)
        if celestial.IsPOSStructure():
            menuEntries.append(None)
        if celestial.OfferAccessPOSFuelBay():
            menuEntries += [[MenuLabel('UI/Inflight/POS/AccessPOSFuelBay'), self.OpenPOSFuelBay, (itemID,)]]
        if celestial.OfferAccessPOSStrontiumBay():
            menuEntries += [[MenuLabel('UI/Inflight/POS/AccessPOSStrontiumBay'), self.OpenStrontiumBay, (itemID,)]]
        if celestial.OfferAccessPOSAmmo():
            menuEntries += [[MenuLabel('UI/Inflight/POS/AccessPOSAmmo'), self.OpenPOSStructureCharges, (itemID, True)]]
        if celestial.OfferAccessPOSActiveCrystal():
            menuEntries += [[MenuLabel('UI/Inflight/POS/AccessPOSActiveCrystal'), self.OpenPOSStructureChargeCrystal, (itemID,)]]
        if celestial.OfferAccessPOSCrystalStorage():
            menuEntries += [[MenuLabel('UI/Inflight/POS/AccessPOSCrystalStorage'), self.OpenPOSStructureChargesStorage, (itemID,)]]
        if celestial.OfferStoreVesselInSMA():
            menuEntries += [[MenuLabel('UI/Inflight/POS/StoreVesselInSMA'), self.StoreVessel, (itemID, session.shipid)]]
        if celestial.OfferAccessPOSStorage():
            openFunc = self.OpenCorpHangarArray
            if celestial.IsPersonalHangarArray():
                openFunc = self.OpenPersonalHangar
            elif celestial.IsSilo():
                openFunc = self.OpenPOSSilo
            elif celestial.IsReactor():
                openFunc = self.OpenPOSMobileReactor
            menuEntries += [[MenuLabel('UI/Inflight/POS/AccessPOSStorage'), openFunc, (itemID,)]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/POS/AccessPOSStorage'] = self.GetUnavailableText(celestial)
        if celestial.OfferManageControlTower():
            menuEntries += [[MenuLabel('UI/Inflight/POS/ManageControlTower'), self.ManageControlTower, (slimItem,)]]
        if celestial.OfferSetNewPasswordForForceField():
            menuEntries += [[MenuLabel('UI/Inflight/POS/SetNewPasswordForForceField'), self.EnterForceFieldPassword, (itemID,)]]
        if celestial.OfferAccessPOSVessels():
            menuEntries += [[MenuLabel('UI/Inflight/POS/AccessPOSVessels'), self.OpenPOSShipMaintenanceArray, (itemID,)]]
            menuEntries += [None]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/AccessPOSVessels'] = self.GetUnavailableText(celestial)
        if celestial.OfferSetName():
            menuEntries += [[MenuLabel('UI/Commands/SetName'), self.SetName, (slimItem,)]]
        if celestial.OfferAccessPOSRefinery():
            menuEntries += [[MenuLabel('UI/Inflight/POS/AccessPOSRefinery'), self.OpenPOSRefinery, (itemID,)]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/POS/AccessPOSRefinery'] = self.GetUnavailableText(celestial)
        if celestial.OfferAccessPOSCompression():
            menuEntries += [[MenuLabel('UI/Inflight/POS/AccessPOSCompression'), self.OpenPOSCompression, (itemID,)]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/POS/AccessPOSCompression'] = self.GetUnavailableText(celestial)
        if celestial.OfferOpenInfrastructureHubPanel():
            menuEntries += [[MenuLabel('UI/FactionWarfare/IHub/OpenInfrastructureHubPanel'), openFunctions.OpenInfrastructureHubPanel, (itemID,)]]
        if celestial.OfferOpenSovFuelDepositWindow():
            menuEntries += [[MenuLabel('UI/Sovereignty/SovHub/ReagentBay/DepositReagents'), openFunctions.OpenSovFuelDepositWindow, (itemID, slimItem)]]
        if celestial.OfferOpenSovHubConfigWindow():
            menuEntries += [[MenuLabel('UI/Menusvc/OpenSovHubConfigWindow'), openFunctions.OpenSovHubWindow, (itemID,)]]
        if celestial.OfferOpenSovSystemCleanup():
            menuEntries += [MenuEntryData(MenuLabel('UI/Sovereignty/SovHub/SystemCleanup/OfferCleanup'), open_sov_system_cleanup, texturePath=eveicon.hourglass)]
        if celestial.OfferTransferSovStructureOwnership():
            menuEntries += [[MenuLabel('UI/Inflight/POS/TransferSovStructureOwnership'), self.TransferOwnership, (itemID,)]]
        if celestial.OfferSelfDestructShipOrPod():
            menuEntries += [[MenuLabel('UI/Inflight/SelfDestructShipOrPod'), self.SelfDestructStructure, (itemID,)]]
        elif celestial.OfferAbortSelfDestructStructure():
            menuEntries += [[MenuLabel('UI/Inflight/AbortSelfDestruct'), self.AbortSelfDestructStructure, (itemID,)]]
        if celestial.OfferAnchorStructure():
            menuEntries += [[MenuLabel('UI/Inflight/POS/AnchorStructure'), sm.StartService('posAnchor').StartAnchorPosSelect, (itemID,)]]
        if celestial.OfferUnanchorStructure():
            menuEntries += [[MenuLabel('UI/Inflight/POS/UnanchorStructure'), self.UnanchorStructure, (itemID,)]]
        if celestial.OfferPutStructureOnline():
            menuEntries += [[MenuLabel('UI/Inflight/PutStructureOnline'), self.ToggleObjectOnline, (itemID, 1)]]
        if celestial.OfferPutStructureOffline():
            menuEntries += [[MenuLabel('UI/Inflight/PutStructureOffline'), self.ToggleObjectOnline, (itemID, 0)]]
        if celestial.OfferRelinquishPOSControl():
            menuEntries += [[MenuLabel('UI/Inflight/POS/RelinquishPOSControl'), self.pwn.RelinquishStructureControl, (slimItem,)]]
        if celestial.OfferAssumeStructureControl():
            menuEntries += [[MenuLabel('UI/Inflight/POS/AssumeStructureControl'), self.pwn.AssumeStructureControl, (slimItem,)]]
        if celestial.OfferUnlockStructureTarget():
            menuEntries += [[MenuLabel('UI/Inflight/POS/UnlcokSTructureTarget'), self.pwn.UnlockStructureTarget, (itemID,)]]
        if celestial.OfferAnchorOrbital():
            menuEntries += [[MenuLabel('UI/Inflight/POS/AnchorObject'), self.AnchorOrbital, (itemID,)]]
        if celestial.OfferUnanchorOrbital():
            menuEntries += [[MenuLabel('UI/Inflight/UnanchorObject'), self.UnanchorOrbital, (itemID,)]]
        if celestial.OfferConfigureOrbitalPoco() or celestial.OfferConfigureOrbitalSkyhook():
            menuEntries += [[MenuLabel('UI/DustLink/ConfigureOrbital'), self.ConfigureOrbital, (slimItem,)]]
        if celestial.OfferTransferCorporationOwnershipPoco() or celestial.OfferTransferCorporationOwnershipSkyhook():
            menuEntries += [[MenuLabel('UI/Inflight/POS/TransferSovStructureOwnership'), self.TransferCorporationOwnership, (itemID,)]]
        if celestial.OfferMarkWreckNotViewed():
            menuEntries += [[MenuLabel('UI/Inflight/MarkWreckNotViewed'), sm.GetService('wreck').MarkViewed, (itemID, False)]]
        elif celestial.OfferMarkWreckViewed():
            menuEntries += [[MenuLabel('UI/Inflight/MarkWreckViewed'), sm.GetService('wreck').MarkViewed, (itemID, True)]]
        menuEntries += [None]
        if celestial.OfferCancelLockTarget():
            menuEntries += [[MenuLabel('UI/Inflight/CancelLockTarget'), self.CancelLockTarget, (itemID,)]]
        elif celestial.OfferUnlockTarget():
            menuEntries += [[MenuLabel('UI/Inflight/UnlockTarget'), self.UnlockTarget, (itemID,)]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/UnlockTarget'] = self.GetUnavailableText(celestial)
        if celestial.OfferLockTarget():
            menuEntries.append(MenuEntryData(MenuLabel('UI/Inflight/LockTarget'), lambda : self.LockTarget(itemID), internalName='LockTarget', typeID=typeID))
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/LockTarget'] = self.GetUnavailableText(celestial)
        if celestial.OfferFleetTagItem():
            menuEntries += [None]
            tagItemMenu = [(MenuLabel('UI/Fleet/FleetTagNumber'), [ (' ' + str(i), self.TagItem, (itemID, str(i))) for i in xrange(10) ])]
            tagItemMenu += [(MenuLabel('UI/Fleet/FleetTagLetter'), [ (' ' + str(i), self.TagItem, (itemID, str(i))) for i in 'ABCDEFGHIJXYZ' ])]
            menuEntries += [[MenuLabel('UI/Fleet/FleetSubmenus/FleetTagItem'), tagItemMenu]]
            menuEntries += [[MenuLabel('UI/Fleet/FleetSubmenus/UntagItem'), self.TagItem, (itemID, None)]]
        if celestial.OfferStartConversation():
            menuEntries += [[MenuLabel('UI/Chat/StartConversation'), sm.StartService('agents').OpenDialogueWindow, (sm.StartService('godma').GetType(typeID).agentID,)]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Chat/StartConversation'] = self.GetUnavailableText(celestial)
        menuEntries += [None]
        if celestial.OfferSetNewPasswordForContainer():
            desc = localization.GetByLabel('UI/Inventory/ItemActions/SetNewPasswordForContainer')
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/SetNewPasswordForContainer'), self.AskNewContainerPassword, (itemID, desc, const.SCCPasswordTypeGeneral)]]
        if celestial.OfferSetNewConfigPasswordForContainer():
            desc = localization.GetByLabel('UI/Inventory/ItemActions/SetNewConfigPasswordForContainer')
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/SetNewConfigPasswordForContainer'), self.AskNewContainerPassword, (itemID, desc, const.SCCPasswordTypeConfig)]]
        if celestial.OfferViewLog():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/ViewLog'), openFunctions.ViewAuditLogForALSC, (itemID,)]]
        if celestial.OfferConfigureALSC():
            menuEntries += [[MenuLabel('UI/Inventory/ItemActions/ConfigureALSContainer'), self.ConfigureALSC, (itemID,)]]
        if celestial.OfferRetrievePasswordALSC():
            menuEntries += [[MenuLabel('UI/Commands/RetrievePassword'), self.RetrievePasswordALSC, (itemID,)]]
        if celestial.OfferAccessShippingUnit():
            menuEntries += [[MenuLabel('UI/Menusvc/AccessShippingUnit'), self.OpenShippingUnitStorage, (itemID,)]]
        if celestial.OfferOpenCargoBay():
            menuEntries += [[MenuLabel('UI/Commands/OpenCargo'), cargobay.OpenCargoWindow, [itemID, typeID, self]]]
        if celestial.OfferActivateMicroJumpDrive():
            menuEntries += [[MenuLabel('UI/Inflight/SpaceComponents/MicroJumpDriver/ActivateMicroJumpDrive'), microJumpDriver.ActivateMicroJumpDrive, [sm.GetService('michelle'), itemID]]]
        if celestial.OfferItemTraderAccess():
            menuEntries += [[MenuLabel('UI/Inflight/SpaceComponents/ItemTrader/Access'), self.RequestTrade, [itemID]]]
        if celestial.OfferOpenUnderConstruction():
            menuEntries += [[MenuLabel('UI/Inflight/SpaceComponents/UnderConstruction/Access'), self.OpenUnderConstruction, [itemID]]]
        if celestial.OfferLinkWithShip():
            menuEntries += [[MenuLabel(GetLinkButtonLabelPath(typeID)), linkWithShip.InitiateLink, [sm.GetService('michelle'), itemID]]]
            if session.role & (ROLE_GML | ROLE_WORLDMOD):
                menuEntries += [['GM: LINK QUICKLY!', linkWithShip.InitiateLinkQuick, [sm.GetService('michelle'), itemID]]]
        if celestial.OfferTowableMenu():
            menuEntries.extend(towGameObjective.GetMenuEntries(celestial))
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/SpaceComponents/TowGameObjective/startTowing'] = self.GetUnavailableText(celestial)
        if celestial.OfferConfigureFacility():
            menuEntries += [[MenuLabel('UI/Menusvc/ConfigureFacility'), self.ConfigureIndustryTax, (itemID, typeID)]]
        if celestial.OfferJumpThroughStargate():
            localStargate = FindLocalStargate(celestial.GetWaypointSolarsystemID())
            if localStargate:
                menuEntries += [[MenuLabel('UI/Inflight/JumpThroughStargate'),
                  self.StargateJump,
                  (localStargate.itemID,
                   localStargate.typeID,
                   localStargate.jumps[0].toCelestialID,
                   localStargate.jumps[0].locationID),
                  eveicon.jump_to,
                  None,
                  'Jump']]
        if celestial.OfferJumpThroughStructureJumpGate():
            localJumpBridge = FindLocalJumpGateForDestinationPath(celestial.GetWaypointSolarsystemID())
            if localJumpBridge:
                menuEntries += [[MenuLabel('UI/Inflight/JumpThroughJumpgate'),
                  self.JumpThroughStructureJumpBridge,
                  (localJumpBridge.itemID,),
                  eveicon.jump_to]]
        if celestial.OfferSetDestination():
            menuEntries.append(MenuEntryData(MenuLabel('UI/Inflight/SetDestination'), lambda : sm.StartService('starmap').SetWaypoint(itemID, True)))
        if celestial.OfferAddWaypoint():
            menuEntries += [[MenuLabel('UI/Inflight/AddWaypoint'), sm.StartService('starmap').SetWaypoint, (itemID,)]]
        elif celestial.isWaypoint():
            menuEntries += [[MenuLabel('UI/Inflight/RemoveWaypoint'), sm.StartService('starmap').ClearWaypoints, (itemID,)]]
        if celestial.OfferBroadcastTravelTo():
            menuEntries += [None]
            menuEntries += [MenuEntryData(MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastTravelTo'), lambda : sm.GetService('fleet').SendBroadcast_TravelTo(itemID), texturePath=iconsByBroadcastType[BROADCAST_TRAVEL_TO])]
        if celestial.OfferEditProfileForStructure():
            menuEntries += [[MenuLabel('UI/Commands/EditProfileForStructure'), openFunctions.OpenProfileSettingsForStructure, (itemID,)]]
        if celestial.OfferSetHomeStation():
            menuEntries += [[MenuLabel('UI/Menusvc/SetHomeStation'), self.SetHomeStation, (itemID,)]]
        if celestial.OfferToggleOverviewVisibility():
            menuEntries.append(overviewMenuUtil.GetToggleEntry(groupID))
        if celestial.OfferBookmarkLocation():
            if celestial.IsBeacon():
                beacon = sm.GetService('michelle').GetItem(itemID)
                if beacon and hasattr(beacon, 'dunDescriptionID') and beacon.dunDescriptionID:
                    hint = localization.GetByMessageID(beacon.dunDescriptionID)
            if parentID:
                menuEntries += [None]
            menuEntries += [[MenuLabel('UI/Inflight/BookmarkLocation'), self.Bookmark, (itemID,
               typeID,
               parentID,
               hint)]]
        if celestial.OfferShowLocationOnMap():
            menuEntries += [None]
            menuEntries += [[MenuLabel('UI/Commands/ShowLocationOnMap'), self.ShowInMap, (itemID,)]]
            menuEntries += [[MenuLabel('UI/Inflight/ShowInMapBrowser', {'locationType': groupName}), self.ShowInMapBrowser, (itemID,)]]
        if celestial.OfferAvoidLocation():
            menuEntries += [[MenuLabel('UI/Inflight/AvoidLocation', {'theLocation': mapFunctionID,
               'locationType': groupName}), self.clientPathfinderService.AddAvoidanceItem, (itemID,)]]
        elif celestial.OfferStopAvoidingLocation():
            menuEntries += [[MenuLabel('UI/Inflight/StopAvoidingLocation', {'theLocation': mapFunctionID,
               'locationType': groupName}), self.clientPathfinderService.RemoveAvoidanceItem, (itemID,)]]
        if celestial.OfferViewPlanetaryProduction():
            menuEntries += [[MenuLabel('UI/PI/Common/ViewInPlanetMode'), self.ViewPlanetaryProduction, (itemID,)]]
        elif celestial.OfferExitPlanetaryProduction():
            menuEntries += [[MenuLabel('UI/PI/Common/ExitPlanetMode'), sm.GetService('viewState').CloseSecondaryView, ()]]
        if not celestial.isMultiSelection:
            menuEntries += [[MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (typeID,
               itemID,
               0,
               None,
               parentID)]]
        if celestial.OfferMoonMenuOptions():
            menuEntries.append(MenuEntryData(MenuLabel('UI/Menusvc/MoonsMenuOption'), subMenuData=lambda : self.GetMoons(celestial.GetMoonsForPlanet()), texturePath=sm.GetService('bracket').GetBracketIconByGroupID(appConst.groupMoon)))
        if celestial.OfferCustomsOfficeMenu():
            customsOfficeID = celestial.GetPocoOrbitals()[0]
            menuEntries.append(MenuEntryData(MenuLabel('UI/PI/Common/CustomsOffice'), subMenuData=lambda : self.GetCustomsOfficeMenu(customsOfficeID), texturePath=sm.GetService('bracket').GetBracketIconByGroupID(appConst.groupOrbitalInfrastructure), func=lambda : movementFunctions.WarpToItem(customsOfficeID)))
        if celestial.OfferOrbitalSkyhook():
            skyhookIDs = celestial.GetSkyhookOrbitals()
            if skyhookIDs:
                skyhookID = skyhookIDs[0]
                menuEntries.append(MenuEntryData(MenuLabel('UI/OrbitalSkyhook/OrbitalSkyhook'), subMenuData=lambda : self.GetCustomsOfficeMenu(skyhookID), texturePath=sm.GetService('bracket').GetBracketIconByGroupID(appConst.groupSkyhook), func=lambda : movementFunctions.WarpToItem(skyhookID)))
        if celestial.OfferPilotMenu():
            menuEntries += [None]
            menuEntries.append(MenuEntryData(MenuLabel('UI/Common/Pilot', {'character': slimItem.charID}), subMenuData=lambda : self.CharacterMenu(slimItem.charID or slimItem.ownerID), texturePath=eveicon.person))
        if celestial.OfferSimulateShip():
            menuEntries += [(MenuLabel('UI/Fitting/FittingWindow/SimulateShip'), openFunctions.SimulateFitting, (utillib.KeyVal(shipTypeID=typeID, fitData=[]),))]
        if session.role & (ROLE_GML | ROLE_WORLDMOD):
            menuEntries.insert(0, ('GM / WM Extras', ('isDynamic', self.GetGMMenu, (itemID,
               slimItem,
               None,
               None,
               mapItem,
               typeID))))
        return menuEntries

    @staticmethod
    def RequestTrade(itemID):
        return sm.GetService('michelle').GetBallpark().componentRegistry.GetComponentForItem(itemID, ITEM_TRADER).RequestTrade()

    def OpenUnderConstruction(self, itemID):
        comp = sm.GetService('michelle').GetBallpark().componentRegistry.GetComponentForItem(itemID, UNDER_CONSTRUCTION)
        self.GetCloseAndTryCommand(itemID, comp.OpenUnderConstructionWnd, ())

    @staticmethod
    def ViewPlanetaryProduction(planetID, *args):
        return sm.GetService('viewState').ActivateView('planet', planetID=planetID)

    def GetMoonMiningPointMenu(self, celestial, slimItem):
        subMenu = MenuList()
        if not celestial.IsMoon():
            return subMenu
        if slimItem:
            beaconItemID = getattr(slimItem, MOON_BEACONID_NAME, None)
            if beaconItemID:
                subMenu += [[MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (invconst.typeMoonMiningBeacon, beaconItemID, 0)]]
        menuEntries = MenuList()
        if celestial.OfferWarpToMoonMiningPoint():
            defaultWarpDist = self.GetDefaultActionDistance('WarpTo')
            label = MenuLabel('UI/Inflight/WarpToMoonMiningPoint', {'distance': fmtutil.FmtDist(float(defaultWarpDist))})
            subMenu += self._GetWarpOptions(movementFunctions.WarpFleetToMiningPointPoint, movementFunctions.WarpToMiningPointPoint, slimItem.itemID, label, defaultWarpDist)
            menuEntries += [[MenuLabel('UI/Inflight/MoonMiningPoint'), subMenu]]
        elif celestial.failure_label:
            menuEntries.reasonsWhyNotAvailable['UI/Inflight/WarpToMoonMiningPoint'] = self.GetUnavailableText(celestial)
        return menuEntries

    def JumpThroughStructureJumpBridge(self, structureID):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return
        self.LogNotice('Jump through structure jump bridge', structureID)
        self.GetCloseAndTryCommand(structureID, self.ReallyJumpThroughStructureJumpBridge, (structureID,))

    @staticmethod
    def ReallyJumpThroughStructureJumpBridge(structureID):
        didJumpThrough = sm.StartService('sessionMgr').PerformSessionChange('jump', sm.RemoteSvc('structureJumpBridgeMgr').CmdJumpThroughStructureStargate, structureID)
        if didJumpThrough:
            sm.GetService('starmap').RemoveWaypointIfFirst(structureID)
        return didJumpThrough

    @staticmethod
    def OpenCapitalNavigation(*args):
        if eveCfg.GetActiveShip():
            CapitalNav.Open()

    def GetHybridBeaconJumpMenu(self):
        moduleBeaconCallback = self.JumpToFleetModuleBeacon
        deployableBeaconCallback = self.JumpToFleetDeployableBeacon
        structureBeaconCallback = self.JumpToStructureBeacon
        return self._GetCynoTargetSubMenus(moduleBeaconCallback, deployableBeaconCallback, structureBeaconCallback)

    def GetHybridBridgeMenu(self):
        moduleBeaconCallback = self.BridgeToFleetModuleBeacon
        deployableBeaconCallback = self.BridgeToFleetDeployableBeacon
        structureBeaconCallback = self.BridgeToBeaconStructure
        return self._GetCynoTargetSubMenus(moduleBeaconCallback, deployableBeaconCallback, structureBeaconCallback)

    def GetHybridBeaconGroupJumpMenu(self):
        moduleBeaconCallback = self.GroupJumpToFleetModuleBeacon
        deployableBeaconCallback = self.GroupJumpToFleetDeployableBeacon
        structureBeaconCallback = self.GroupJumpToStructureBeacon
        return self._GetCynoTargetSubMenus(moduleBeaconCallback, deployableBeaconCallback, structureBeaconCallback)

    def _GetCynoTargetSubMenus(self, moduleBeaconCallback, deployableBeaconCallback, structureBeaconCallback):
        fullMenu = MenuList()
        menuSize = 20
        if session.fleetid:
            fleetSvc = sm.GetService('fleet')
            fleetModuleTargets = []
            for charID, (solarsystemID, beaconID, typeID) in fleetSvc.GetActiveBeacons().iteritems():
                if solarsystemID == session.solarsystemid:
                    continue
                character = cfg.eveowners.Get(charID)
                cynoTypeText = fleetSvc.GetCynoTypeText(typeID)
                menuLabel = MenuLabel('UI/Fleet/FleetSubmenus/ModuleCynoBeaconLabel', {'fleetMemberName': character.name,
                 'system': solarsystemID,
                 'cynoType': cynoTypeText})
                menuArgs = (charID,
                 solarsystemID,
                 beaconID,
                 typeID)
                sortKey = character.name
                fleetModuleTargets.append((sortKey, (menuLabel, menuArgs)))

            fleetModuleTargets = SortListOfTuples(fleetModuleTargets)
            for menuLabel, menuArgs in fleetModuleTargets:
                fullMenu.append([menuLabel, moduleBeaconCallback, menuArgs])

            fleetDeployableTargets = []
            for deployableID, (solarSystemID, beaconID, ownerID) in fleetSvc.activeDeployableBeacons.iteritems():
                if solarSystemID == session.solarsystemid:
                    continue
                ownerName = cfg.eveowners.Get(ownerID)
                menuLabel = MenuLabel('UI/Fleet/FleetSubmenus/DeployableCynoBeaconLabel', {'fleetMemberName': ownerName.name,
                 'system': solarSystemID})
                menuArgs = (deployableID, solarSystemID, beaconID)
                sortKey = ownerName.name
                fleetDeployableTargets.append((sortKey, (menuLabel, menuArgs)))

            fleetDeployableTargets = SortListOfTuples(fleetDeployableTargets)
            for menuLabel, menuArgs in fleetDeployableTargets:
                fullMenu.append([menuLabel, deployableBeaconCallback, menuArgs])

        structureTargets = []
        structureBeacons = sm.GetService('structureDirectory').GetAccessibleOnlineCynoBeaconStructures()
        cfg.evelocations.Prime([ beacon[3] for beacon in structureBeacons ])
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        jumpDriveRange = dogmaLocation.GetAttributeValue(eveCfg.GetActiveShip(), const.attributeJumpDriveRange)
        for structureID, typeID, ownerID, solarSystemID, structureState, name in structureBeacons:
            if solarSystemID == session.solarsystemid:
                continue
            distance = GetLightYearDistance(session.solarsystemid2, solarSystemID)
            if distance > jumpDriveRange:
                continue
            solarsystem = cfg.evelocations.Get(solarSystemID)
            menuLabel = MenuLabel('UI/Fleet/FleetSubmenus/StructureCynoBeaconLabel', {'structureName': name})
            menuArgs = (solarSystemID, structureID)
            extraArgForLongMenuMerging = solarsystem.name
            structureTargets.append((solarsystem.name, (menuLabel, menuArgs, extraArgForLongMenuMerging)))

        structureTargets = SortListOfTuples(structureTargets)
        if len(structureTargets):
            if len(fullMenu) > 0:
                fullMenu.append(None)
            structureMenu = []
            for menuLabel, menuArgs, extraArgForLongMenuMerging in structureTargets:
                structureMenu.append([menuLabel,
                 structureBeaconCallback,
                 menuArgs,
                 extraArgForLongMenuMerging])

            fullMenu.extend(self.CreateSubMenusForLongMenus(structureMenu, menuSize, subMenuFunc=self.GetJumpSubMenu))
        if len(fullMenu) > 0:
            return fullMenu
        else:
            return ([MenuLabel('UI/Inflight/NoDestination'), self.DoNothing],)

    @staticmethod
    def CreateSubMenusForLongMenus(menuList, menuSize, subMenuFunc, *args):
        allMenuItems = []
        menuListLeft = menuList[:]
        while len(menuListLeft) > menuSize:
            allMenuItems.append(menuListLeft[:menuSize])
            menuListLeft = menuListLeft[menuSize:]

        if menuListLeft:
            allMenuItems.append(menuListLeft)
        if len(allMenuItems) == 1:
            m = subMenuFunc(allMenuItems[0])
        else:
            m = MenuList()
            for sub in allMenuItems:
                firstItem = sub[0]
                lastItem = sub[-1]
                if firstItem:
                    firstLetter = firstItem[3][0]
                else:
                    firstLetter = '0'
                if lastItem:
                    lastLetter = lastItem[3][0]
                else:
                    lastLetter = '-1'
                m.append(('%s ... %s' % (firstLetter, lastLetter), ('isDynamic', subMenuFunc, [sub])))

        return m

    @staticmethod
    def GetJumpSubMenu(subMenuItems, *args):
        m = MenuList()
        for menuItem in subMenuItems:
            if menuItem is None:
                m.append(None)
                continue
            name, eachFunc, eachArgs, systemName = menuItem
            m.append([name, eachFunc, eachArgs])

        return m

    @staticmethod
    def ConfirmMenu(func):
        m = [(MenuLabel('UI/Menusvc/ConfirmMenuOption'), func)]
        return m

    @staticmethod
    def WarpToMenu(func, ID):
        ranges = movementFunctions.GetWarpToRanges()
        defMenuWarpOptions = [ (fmtutil.FmtDist(rnge), defaultRangeUtils.SetDefaultWarpToDist, (rnge,)) for rnge in ranges ]
        warpDistMenu = [(MenuLabel('UI/Inflight/WarpToWithin', {'distance': fmtutil.FmtDist(ranges[0])}), func, (ID, float(ranges[0]))),
         (MenuLabel('UI/Inflight/WarpToWithin', {'distance': fmtutil.FmtDist(ranges[1])}), func, (ID, float(ranges[1]))),
         (MenuLabel('UI/Inflight/WarpToWithin', {'distance': fmtutil.FmtDist(ranges[2])}), func, (ID, float(ranges[2]))),
         (MenuLabel('UI/Inflight/WarpToWithin', {'distance': fmtutil.FmtDist(ranges[3])}), func, (ID, float(ranges[3]))),
         (MenuLabel('UI/Inflight/WarpToWithin', {'distance': fmtutil.FmtDist(ranges[4])}), func, (ID, float(ranges[4]))),
         (MenuLabel('UI/Inflight/WarpToWithin', {'distance': fmtutil.FmtDist(ranges[5])}), func, (ID, float(ranges[5]))),
         (MenuLabel('UI/Inflight/WarpToWithin', {'distance': fmtutil.FmtDist(ranges[6])}), func, (ID, float(ranges[6]))),
         None,
         (MenuLabel('UI/Inflight/Submenus/SetDefaultWarpRange'), defMenuWarpOptions)]
        return warpDistMenu

    def GetMenuForOwner(self, ownerID):
        owner = cfg.eveowners.Get(ownerID)
        return self.GetMenuFromItemIDTypeID(ownerID, owner.typeID)

    def GetMenuFromItemIDTypeID(self, itemID, typeID, invItem = None, includeMarketDetails = False, abstractInfo = None, **kwargs):
        if typeID is None:
            return MenuList()
        if invItem:
            return self.InvItemMenu(invItem)
        groupID = evetypes.GetGroupID(typeID)
        categoryID = evetypes.GetCategoryID(typeID)
        if groupID == const.groupCharacter:
            return self.CharacterMenu(itemID, **kwargs)
        if categoryID in CELESTIAL_MENU_CATEGORIES:
            menu = self.CelestialMenu(itemID, typeID=typeID)
            if includeMarketDetails:
                menu.extend(self.MarketDetailMenu(typeID))
            return menu
        m = MenuList()
        m += [(MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (typeID,
           itemID,
           0,
           None,
           None,
           abstractInfo))]
        if groupID == const.groupCorporation and idCheckers.IsCorporation(itemID) and not idCheckers.IsNPC(itemID):
            m += [(MenuLabel('UI/Commands/GiveMoney'), sm.StartService('wallet').TransferMoney, (session.charid,
               None,
               itemID,
               None))]
        if industryCommon.IsBlueprintCategory(categoryID):
            from eve.client.script.ui.shared.industry.industryWnd import Industry
            bpData = abstractInfo.get('bpData', None) if abstractInfo else None
            m += ((localization.GetByLabel('UI/Industry/ViewInIndustry'), Industry.OpenOrShowBlueprint, (itemID, typeID, bpData)),)
        if groupID in [const.groupCorporation, const.groupAlliance, const.groupFaction]:
            addressBookSvc = sm.GetService('addressbook')
            inAddressbook = addressBookSvc.IsInAddressBook(itemID, 'contact')
            isBlocked = addressBookSvc.IsBlocked(itemID)
            isNPC = idCheckers.IsNPC(itemID)
            if inAddressbook:
                m += ((MenuLabel('UI/PeopleAndPlaces/EditContact'), addressBookSvc.AddToPersonalMulti, [itemID, 'contact', True]),)
                m += ((MenuLabel('UI/PeopleAndPlaces/RemoveContact'), addressBookSvc.DeleteEntryMulti, [[itemID], 'contact']),)
            else:
                m.append(MenuEntryData(MenuLabel('UI/PeopleAndPlaces/AddContact'), lambda : addressBookSvc.AddToPersonalMulti([itemID], 'contact')))
            if not isNPC:
                if isBlocked:
                    m += ((MenuLabel('UI/PeopleAndPlaces/UnblockContact'), addressBookSvc.UnblockOwner, [[itemID]]),)
                else:
                    m += ((MenuLabel('UI/PeopleAndPlaces/BlockContact'), addressBookSvc.BlockOwner, [itemID]),)
            iAmDiplomat = (const.corpRoleDirector | const.corpRoleDiplomat) & session.corprole != 0
            if iAmDiplomat:
                inCorpAddressbook = addressBookSvc.IsInAddressBook(itemID, 'corpcontact')
                if inCorpAddressbook:
                    m += ((MenuLabel('UI/PeopleAndPlaces/EditCorpContact'), addressBookSvc.AddToPersonalMulti, [itemID, 'corpcontact', True]),)
                    m += ((MenuLabel('UI/PeopleAndPlaces/RemoveCorpContact'), addressBookSvc.DeleteEntryMulti, [[itemID], 'corpcontact']),)
                else:
                    m += ((MenuLabel('UI/PeopleAndPlaces/AddCorpContact'), addressBookSvc.AddToPersonalMulti, [itemID, 'corpcontact']),)
                if session.allianceid:
                    execCorp = sm.GetService('alliance').GetAlliance(session.allianceid).executorCorpID == session.corpid
                    if execCorp:
                        inAllianceAddressbook = addressBookSvc.IsInAddressBook(itemID, 'alliancecontact')
                        if inAllianceAddressbook:
                            m += ((MenuLabel('UI/PeopleAndPlaces/EditAllianceContact'), addressBookSvc.AddToPersonalMulti, [itemID, 'alliancecontact', True]),)
                            m += ((MenuLabel('UI/PeopleAndPlaces/RemoveAllianceContact'), addressBookSvc.DeleteEntryMulti, [[itemID], 'alliancecontact']),)
                        else:
                            m += ((MenuLabel('UI/PeopleAndPlaces/AddAllianceContact'), addressBookSvc.AddToPersonalMulti, [itemID, 'alliancecontact']),)
            if session.corprole & const.corpRoleDirector == const.corpRoleDirector and groupID in (const.groupCorporation, const.groupAlliance):
                if itemID not in (session.corpid, session.allianceid) and not idCheckers.IsNPC(itemID):
                    if sm.GetService('warPermit').CanDeclareWarAgainst(itemID):
                        m += ((MenuLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/DeclareWar'), self.DeclareWarAgainst, [itemID]),)
        if includeMarketDetails:
            if session.charid:
                if evetypes.GetMarketGroupID(typeID) is not None:
                    self._AddMarketDetailsOption(m, typeID)
                if evetypes.IsPublished(typeID):
                    m += [(MenuLabel('UI/Inventory/ItemActions/FindInContracts'), sm.GetService('contracts').FindRelated, (typeID,
                       None,
                       None,
                       None,
                       None,
                       None))]
                    m += [[MenuLabel('UI/Inventory/ItemActions/FindPersonalAssets'), invItemFunctions.FindInPersonalAssets, (typeID,)]]
        if categoryID in compareCategories:
            m += [(MenuLabel('UI/Compare/CompareButton'), self.CompareType, (typeID,))]
        if session.role & (ROLE_GML | ROLE_WORLDMOD | ROLE_LEGIONEER):
            charID = itemID if idCheckers.IsOwner(itemID) else None
            m.insert(0, ('GM / WM Extras', ('isDynamic', self.GetGMMenu, (None,
               None,
               charID,
               None,
               None,
               typeID))))
        return m

    @staticmethod
    def CompareType(typeID, itemID = 0, *args):
        from eve.client.script.ui.shared.neocom.compare import TypeCompare
        typeWnd = TypeCompare.Open()
        typeWnd.AddTypeID(typeID, itemID)

    def GetMenuForSkill(self, typeID):
        m = MenuList()
        if session.role & ROLE_GML == ROLE_GML:
            m.extend(sm.GetService('info').GetGMGiveSkillMenu(typeID))
        skillInfo = sm.GetService('skills').GetSkillIncludingLapsed(typeID)
        if skillInfo is not None:
            m += sm.GetService('skillqueue').GetAddMenuForSkillEntries(typeID, skillInfo)
        else:
            m.append((MenuLabel('UI/Inventory/ItemActions/BuyThisType'), self.QuickBuy, (typeID,)))
        m += self.GetMenuFromItemIDTypeID(None, typeID, includeMarketDetails=True)
        return m

    def GetMoons(self, moons):
        if not moons:
            return [(MenuLabel('UI/Menusvc/PlanetHasNoMoons'), self.DoNothing)]
        moons = SortListOfTuples([ (moon.orbitIndex, moon) for moon in moons ])
        moonmenu = []
        for moon in moons:
            label = MenuLabel('UI/Inflight/Submenus/MoonX', {'moonNumber': moon.orbitIndex})
            moonmenu.append(MenuEntryData(label, subMenuData=lambda itemID = moon.itemID: self.ExpandMoon(itemID, moon), func=lambda itemID = moon.itemID: movementFunctions.WarpToItem(itemID)))

        return moonmenu

    def GetCustomsOfficeMenu(self, customsOfficeID, *args):
        return self.CelestialMenu(customsOfficeID)

    @staticmethod
    def TransferToCargo(itemKey):
        sm.GetService('clientDogmaIM').GetDogmaLocation().UnloadAmmoToContainer(session.shipid, itemKey, session.shipid)

    @staticmethod
    def LoadCharges(item):
        sm.GetService('clientDogmaIM').GetDogmaLocation().LoadChargeToAllModules(item)

    def DoNothing(self, *args):
        pass

    @staticmethod
    def ExpandMoon(itemID, moon):
        return StartMenuService().CelestialMenu(itemID, moon)

    def Activate(self, slimItem):
        if IsControllingStructure():
            return
        itemID, groupID, categoryID = slimItem.itemID, slimItem.groupID, slimItem.categoryID
        if itemID == session.shipid:
            myship = sm.StartService('godma').GetItem(session.shipid)
            if myship.groupID == const.groupCapsule:
                bp = sm.StartService('michelle').GetRemotePark()
                if bp is not None:
                    bp.CmdStop()
            else:
                uicore.cmd.GetCommandAndExecute('OpenCargoHoldOfActiveShip')
            return
        bp = sm.StartService('michelle').GetBallpark()
        if bp:
            ownBall = bp.GetBall(session.shipid)
            otherBall = bp.GetBall(itemID)
            dist = None
            if ownBall and otherBall:
                dist = bp.GetSurfaceDist(ownBall.id, otherBall.id)
            if dist < const.minWarpDistance:
                if groupID == const.groupStation and dist < const.maxDockingDistance:
                    self.Dock(itemID)
                elif groupID == const.groupControlBunker:
                    openFunctions.OpenInfrastructureHubPanel(otherBall.id)
                elif groupID != const.groupMissionContainer and groupID in CONTAINERGROUPS:
                    self.OpenCargo(itemID, 'SomeCargo')
                else:
                    movementFunctions.ShipApproach(itemID)
            else:
                self.AlignTo(itemID)

    def AnchorObject(self, itemID, anchorFlag):
        dogmaLM = self.godma.GetDogmaLM()
        if dogmaLM:
            typeID = sm.StartService('michelle').GetItem(itemID).typeID
            anchoringDelay = self.godma.GetType(typeID).anchoringDelay
            if anchorFlag:
                dogmaLM.Activate(itemID, const.effectAnchorDrop)
                eve.Message('AnchoringObject', {'delay': anchoringDelay / 1000.0})
            else:
                dogmaLM.Activate(itemID, const.effectAnchorLift)
                eve.Message('UnanchoringObject', {'delay': anchoringDelay / 1000.0})

    def UnanchorStructure(self, itemID):
        item = sm.GetService('michelle').GetItem(itemID)
        orphaned = self.pwn.StructureIsOrphan(itemID)
        if orphaned:
            msgName = 'ConfirmOrphanStructureUnanchor'
        elif item.groupID == const.groupInfrastructureHub:
            msgName = 'ConfirmInfrastructureHubUnanchor'
        elif item.groupID == const.groupAssemblyArray:
            msgName = 'ConfirmAssemblyArrayUnanchor'
        elif item.groupID == const.groupPersonalHangar:
            msgName = 'ConfirmUnanchoringPersonalHangar'
        else:
            msgName = 'ConfirmStructureUnanchor'
        if eve.Message(msgName, {'item': item.typeID}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        unanchoringDelay = self.godma.GetType(item.typeID).unanchoringDelay
        dogmaLM = sm.GetService('godma').GetDogmaLM()
        dogmaLM.Activate(itemID, const.effectAnchorLiftForStructures)
        eve.Message('UnanchoringObject', {'delay': unanchoringDelay / 1000.0})

    def ToggleObjectOnline(self, itemID, onlineFlag):
        dogmaLM = self.godma.GetDogmaLM()
        if dogmaLM:
            item = sm.StartService('michelle').GetItem(itemID)
            if onlineFlag:
                if item.groupID in (const.groupSovereigntyClaimMarkers,):
                    if eve.Message('ConfirmSovStructureOnline', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                        return
                dogmaLM.Activate(itemID, const.effectOnlineForStructures)
            else:
                if item.groupID == const.groupControlTower:
                    msgName = 'ConfirmTowerOffline'
                elif item.groupID == const.groupSovereigntyClaimMarkers:
                    msgName = 'ConfirmSovereigntyClaimMarkerOffline'
                else:
                    msgName = 'ConfirmStructureOffline'
                if eve.Message(msgName, {'item': (const.UE_TYPEID, item.typeID)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                    return
                dogmaLM.Deactivate(itemID, const.effectOnlineForStructures)

    @staticmethod
    def DeclareWar():
        return menuFunctions.DeclareWar()

    @staticmethod
    def DeclareWarAgainst(againstID):
        return menuFunctions.DeclareWarAgainst(againstID)

    @staticmethod
    def TransferOwnership(itemID):
        return menuFunctions.TransferOwnership(itemID)

    @staticmethod
    def AbortSelfDestructStructure(itemID):
        return menuFunctions.AbortSelfDestructStructure(itemID)

    @staticmethod
    def SelfDestructStructure(itemID):
        return menuFunctions.SelfDestructStructure(itemID)

    @staticmethod
    def TransferCorporationOwnership(itemID):
        return menuFunctions.TransferCorporationOwnership(itemID)

    def AskNewContainerPassword(self, id_, desc, which = 1, setnew = '', setold = ''):
        return menuFunctions.AskNewContainerPassword(self.invCache, id_, desc, which, setnew, setold)

    @staticmethod
    def LockDownBlueprint(invItem):
        return invItemFunctions.LockDownBlueprint(invItem)

    @staticmethod
    def UnlockBlueprint(invItem):
        return invItemFunctions.UnlockBlueprint(invItem)

    def ALSCLock(self, invItems):
        return invItemFunctions.ALSCLock(invItems, self.invCache)

    def ALSCUnlock(self, invItems):
        return invItemFunctions.ALSCUnlock(invItems, self.invCache)

    def ConfigureALSC(self, itemID):
        return menuFunctions.ConfigureALSC(itemID, self.invCache)

    def RetrievePasswordALSC(self, itemID):
        return menuFunctions.RetrievePasswordALSC(itemID, self.invCache)

    def OpenShippingUnitStorage(self, itemID):
        self.GetCloseAndTryCommand(itemID, self.ReallyOpenShippingUnitStorage, (itemID,))

    @staticmethod
    def ReallyOpenShippingUnitStorage(itemID):
        entity = moniker.GetEntityAccess()
        if entity:
            entity.OpenShippingUnitStorage(itemID)

    def GetFleetMemberMenu(self, func, args):
        menuSize = 20
        watchlistCharIDs = {member.charID for member in sm.GetService('fleet').GetFavorites()}
        charIDsInBallpark = set()
        bp = sm.GetService('michelle').GetBallpark()
        if bp:
            charIDsInBallpark = set(filter(None, {getattr(x, 'charID', None) for x in bp.slimItems.itervalues()}))
        fleet = []
        watchlistMembers = []
        for member in sm.GetService('fleet').GetMembers().itervalues():
            if member.charID == session.charid or member.charID not in charIDsInBallpark:
                continue
            data = cfg.eveowners.Get(member.charID)
            memberInfo = (data.name.lower(), (member.charID, data.name))
            fleet.append(memberInfo)
            if member.charID in watchlistCharIDs:
                watchlistMembers.append(memberInfo)

        fleet = SortListOfTuples(fleet)
        if watchlistMembers:
            watchlistMembers = SortListOfTuples(watchlistMembers)
            watchlistEntry = [(localization.GetByLabel('UI/Fleet/WatchList'), ('isDynamic', self.GetSubFleetMemberMenu, (watchlistMembers, func, args))), None]
        else:
            watchlistEntry = []
        alles = []
        while len(fleet) > menuSize:
            alles.append(fleet[:menuSize])
            fleet = fleet[menuSize:]

        if fleet:
            alles.append(fleet)
        if not alles:
            return [(MenuLabel('UI/Fleet/NoValidOptions'), None)]
        elif len(alles) == 1:
            return watchlistEntry + self.GetSubFleetMemberMenu(alles[0], func, args)
        else:
            return watchlistEntry + [ ('%c ... %c' % (sub[0][1][0], sub[-1][1][0]), ('isDynamic', self.GetSubFleetMemberMenu, (sub, func, args))) for sub in alles ]

    @staticmethod
    def GetSubFleetMemberMenu(memberIDs, func, args):
        return [ [name, func, (charID, args)] for charID, name in memberIDs ]

    def BridgeToMember(self, charID):
        beaconStuff = sm.GetService('fleet').GetActiveBeaconForChar(charID)
        if beaconStuff is None:
            return
        solarsystemID, beaconID, typeID = beaconStuff
        self.BridgeToFleetModuleBeacon(charID, solarsystemID, beaconID, typeID)

    @staticmethod
    def BridgeToBeaconStructure(solarSystemID, structureID):
        sm.GetService('cynoTravel').BridgeToBeaconStructure(solarSystemID, structureID)

    @staticmethod
    def BridgeToFleetModuleBeacon(charID, solarsystemID, beaconID, typeID):
        sm.GetService('cynoTravel').BridgeToFleetModuleBeacon(charID, solarsystemID, beaconID)

    @staticmethod
    def BridgeToFleetDeployableBeacon(deployableID, solarsystemID, beaconID):
        sm.GetService('cynoTravel').BridgeToFleetDeployableBeacon(deployableID, solarsystemID, beaconID)

    @staticmethod
    def JumpThroughFleet(otherCharID, otherShipID):
        sm.GetService('cynoTravel').JumpThroughFleet(otherCharID, otherShipID)

    def JumpToMember(self, charid):
        beaconStuff = sm.GetService('fleet').GetActiveBeaconForChar(charid)
        if beaconStuff is None:
            return
        solarsystemID, beaconID, typeID = beaconStuff
        self.JumpToFleetModuleBeacon(charid, solarsystemID, beaconID, typeID)

    @staticmethod
    def JumpToFleetModuleBeacon(charid, solarsystemID, beaconID, typeID):
        sm.GetService('cynoTravel').JumpToFleetModuleBeacon(charid, solarsystemID, beaconID)

    @staticmethod
    def JumpToFleetDeployableBeacon(deployableID, solarsystemID, beaconID):
        sm.GetService('cynoTravel').JumpToFleetDeployableBeacon(deployableID, solarsystemID, beaconID)

    @staticmethod
    def JumpToStructureBeacon(solarSystemID, structureID):
        sm.GetService('cynoTravel').JumpToStructureBeacon(solarSystemID, structureID)

    def GroupJumpToMember(self, charid):
        beaconStuff = sm.GetService('fleet').GetActiveBeaconForChar(charid)
        if beaconStuff is None:
            return
        solarsystemID, beaconID, typeID = beaconStuff
        self.GroupJumpToFleetModuleBeacon(charid, solarsystemID, beaconID, typeID)

    @staticmethod
    def GroupJumpToFleetModuleBeacon(charid, solarsystemID, beaconID, typeID):
        sm.GetService('cynoTravel').GroupJumpToFleetModuleBeacon(charid, solarsystemID, beaconID)

    @staticmethod
    def GroupJumpToFleetDeployableBeacon(deployableID, solarsystemID, beaconID):
        sm.GetService('cynoTravel').GroupJumpToFleetDeployableBeacon(deployableID, solarsystemID, beaconID)

    @staticmethod
    def GroupJumpToStructureBeacon(solarSystemID, structureID):
        sm.GetService('cynoTravel').GroupJumpToStructureBeacon(solarSystemID, structureID)

    @staticmethod
    def LeaveFleet():
        sm.GetService('fleet').LeaveFleet()

    @staticmethod
    def MakeLeader(charid):
        sm.GetService('fleet').MakeLeader(charid)

    @staticmethod
    def KickMember(charid):
        sm.GetService('fleet').KickMember(charid)

    @staticmethod
    def InviteToFleet(charIDs, ignoreWars = 0):
        if type(charIDs) != list:
            charIDs = [charIDs]
        charErrors = {}
        for charID in charIDs:
            try:
                sm.GetService('fleet').Invite(charID, None, None, None)
            except UserError as ue:
                charErrors[charID] = ue
                sys.exc_clear()

        if len(charErrors) == 1:
            raise charErrors.values()[0]
        elif len(charErrors) > 1:
            charNames = None
            for charID in charErrors.iterkeys():
                if charNames is not None:
                    charNames += ', %s' % cfg.eveowners.Get(charID).name
                else:
                    charNames = cfg.eveowners.Get(charID).name

            raise UserError('FleetInviteMultipleErrors', {'namelist': charNames})

    @staticmethod
    def WarpFleet(targetID, warpRange = None):
        michelle = sm.GetService('michelle')
        bp = michelle.GetRemotePark()
        if bp is not None:
            sm.GetService('autoPilot').CancelSystemNavigation()
            michelle.CmdWarpToStuff('item', targetID, minRange=warpRange, fleet=True)
            sm.StartService('space').WarpDestination(celestialID=targetID)

    @staticmethod
    def WarpToMember(charID, warpRange = None):
        michelle = sm.GetService('michelle')
        bp = michelle.GetRemotePark()
        if bp is not None:
            sm.GetService('autoPilot').CancelSystemNavigation()
            michelle.CmdWarpToStuff('char', charID, minRange=warpRange)
            sm.StartService('space').WarpDestination(fleetMemberID=charID)

    @staticmethod
    def WarpFleetToMember(charID, warpRange = None):
        michelle = sm.GetService('michelle')
        bp = michelle.GetRemotePark()
        if bp is not None:
            sm.GetService('autoPilot').CancelSystemNavigation()
            michelle.CmdWarpToStuff('char', charID, minRange=warpRange, fleet=True)
            sm.StartService('space').WarpDestination(fleetMemberID=charID)

    @staticmethod
    def TacticalItemClicked(itemID):
        isTargeted = sm.GetService('target').IsTarget(itemID)
        if isTargeted:
            sm.GetService('stateSvc').SetState(itemID, state.activeTarget, 1)
        uicore.cmd.ExecuteCombatCommand(itemID, uiconst.UI_CLICK)

    def AlignTo(self, alignID):
        if alignID == session.shipid:
            return
        if self._CheckAlignToSiteBracket(alignID):
            return
        self._AlignTo(alignID, isBookmark=False)

    def _AlignTo(self, alignID, isBookmark = False):
        bp = sm.GetService('michelle').GetRemotePark()
        if bp is None:
            return
        sm.GetService('tacticalNavigation').NotifyOfAlignCommand(alignID)
        if isBookmark:
            targetID, bookmarkID = None, alignID
        else:
            targetID, bookmarkID = alignID, None
        self.StoreAlignTarget(alignTargetID=targetID, aligningToBookmark=isBookmark)
        sm.GetService('space').SetIndicationTextForcefully(ballMode=destiny.DSTBALL_GOTO, followId=targetID, followRange=None)
        bp.CmdAlignTo(dstID=targetID, bookmarkID=bookmarkID)
        sm.GetService('autoPilot').CancelSystemNavigation()
        if not isBookmark:
            sm.GetService('flightPredictionSvc').OptionActivated('AlignTo', alignID)

    @staticmethod
    def _CheckAlignToSiteBracket(itemID):
        bracket = sm.GetService('sensorSuite').siteController.spaceLocations.GetBracketByBallID(itemID)
        if bracket:
            bracket.AlignTo()
            return True
        return False

    def AlignToBookmark(self, alignID):
        self._AlignTo(alignID, isBookmark=True)

    def StoreAlignTarget(self, alignTargetID = None, aligningToBookmark = False, *args):
        self.lastAlignTargetID = alignTargetID
        self.lastAlignedToBookmark = aligningToBookmark

    def GetLastAlignTarget(self, *args):
        return (getattr(self, 'lastAlignTargetID', None), getattr(self, 'lastAlignedToBookmark', False))

    def ClearAlignTargets(self, *args):
        self.lastAlignTargetID = None
        self.lastAlignedToBookmark = None

    @staticmethod
    def TagItem(itemID, tag):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp:
            bp.CmdFleetTagTarget(itemID, tag)

    @staticmethod
    def LockTarget(targetID):
        sm.StartService('target').TryLockTarget(targetID)

    @staticmethod
    def UnlockTarget(targetID):
        sm.StartService('target').UnlockTarget(targetID)

    @staticmethod
    def CancelLockTarget(targetID):
        sm.StartService('target').CancelAddTarget(targetID)

    @staticmethod
    def ShowInfo(typeID, itemID = None, new = 0, rec = None, parentID = None, abstractInfo = None, *args):
        sm.GetService('info').ShowInfo(typeID, itemID, new, rec, parentID, abstractinfo=abstractInfo)

    @staticmethod
    def ShowInfoForItem(itemID):
        if sm.GetService('sensorSuite').IsSiteBall(itemID):
            return
        bp = sm.StartService('michelle').GetBallpark()
        if bp:
            itemTypeID = bp.GetInvItem(itemID).typeID
            sm.GetService('info').ShowInfo(itemTypeID, itemID)

    @staticmethod
    def PreviewType(typeID):
        sm.GetService('preview').PreviewType(typeID)

    def StoreVessel(self, destID, shipID):
        if shipID != session.shipid:
            return
        shipItem = self.godma.GetStateManager().GetItem(shipID)
        if shipItem.groupID == const.groupCapsule:
            return
        destItem = uix.GetBallparkRecord(destID)
        if destItem.categoryID == const.categoryShip:
            msgName = 'ConfirmStoreVesselInShip'
        else:
            msgName = 'ConfirmStoreVesselInStructure'
        if eve.Message(msgName, {'dest': destItem.typeID}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        if shipID != session.shipid:
            return
        shipItem = self.godma.GetStateManager().GetItem(shipID)
        if shipItem.groupID == const.groupCapsule:
            return
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            sm.ScatterEvent('OnBeforeActiveShipChanged', shipID, eveCfg.GetActiveShip())
            sm.StartService('sessionMgr').PerformSessionChange('storeVessel', ship.StoreVessel, destID)

    @staticmethod
    def OpenCorpHangarArray(itemID):
        Inventory.OpenOrShow(invID=('POSCorpHangars', itemID))

    @staticmethod
    def OpenPersonalHangar(itemID):
        Inventory.OpenOrShow(invID=('POSPersonalHangar', itemID))

    @staticmethod
    def OpenPOSSilo(itemID):
        Inventory.OpenOrShow(invID=('POSSilo', itemID))

    @staticmethod
    def OpenPOSMobileReactor(itemID):
        Inventory.OpenOrShow(invID=('POSMobileReactor', itemID))

    @staticmethod
    def OpenPOSShipMaintenanceArray(itemID):
        Inventory.OpenOrShow(invID=('POSShipMaintenanceArray', itemID))

    @staticmethod
    def OpenPOSStructureChargesStorage(itemID):
        Inventory.OpenOrShow(invID=('POSStructureChargesStorage', itemID))

    @staticmethod
    def OpenPOSStructureChargeCrystal(itemID):
        Inventory.OpenOrShow(invID=('POSStructureChargeCrystal', itemID))

    @staticmethod
    def OpenPOSFuelBay(itemID):
        Inventory.OpenOrShow(invID=('POSFuelBay', itemID))

    @staticmethod
    def OpenPOSRefinery(itemID):
        Inventory.OpenOrShow(invID=('POSRefinery', itemID))

    @staticmethod
    def OpenPOSCompression(itemID):
        Inventory.OpenOrShow(invID=('POSCompression', itemID))

    @staticmethod
    def OpenPOSStructureCharges(itemID, showCapacity = 0):
        Inventory.OpenOrShow(invID=('POSStructureCharges', itemID))

    @staticmethod
    def OpenStrontiumBay(itemID):
        Inventory.OpenOrShow(invID=('POSStrontiumBay', itemID))

    @staticmethod
    def OpenMoonMaterialBay(itemID):
        Inventory.OpenOrShow(invID=('StructureMoonMaterialBay', itemID))

    def ManageControlTower(self, itemID):
        uthread.new(self._ManageControlTower, itemID)

    @staticmethod
    def _ManageControlTower(itemID):
        uicore.cmd.GetCommandAndExecute('OpenMoonMining', itemID)

    @staticmethod
    def OpenSpaceComponentInventory(itemID):
        Inventory.OpenOrShow(invID=('SpaceComponentInventory', itemID))

    @staticmethod
    def Bookmark(itemID, typeID, parentID, note = None):
        sm.StartService('addressbook').BookmarkLocationPopup(itemID, typeID, parentID, note)

    @staticmethod
    def ShowInMapBrowser(itemID, *args):
        uicore.cmd.GetCommandAndExecute('OpenMapBrowser', itemID)

    @staticmethod
    def ShowInMap(itemID, *args):
        OpenMap(interestID=itemID)

    def Dock(self, itemID):
        item = sm.GetService('michelle').GetItem(itemID)
        message_bus = JourneyMessenger(sm.GetService('publicGatewaySvc'))
        uthread.new(message_bus.linked, 'Dock')
        if item and item.categoryID == const.categoryStation:
            self.DockStation(itemID)
        elif item and item.categoryID == const.categoryStructure:
            sm.GetService('structureDocking').Dock(itemID)

    def DockStation(self, itemID):
        sm.ScatterEvent('OnClientEvent_DockCmdExecuted', itemID)
        bp = sm.StartService('michelle').GetBallpark()
        if not bp:
            return
        self.GetCloseAndTryCommand(itemID, movementFunctions.RealDock, (itemID,))

    def GetIllegality(self, itemID, typeID = None, solarSystemID = None):
        if solarSystemID is None:
            solarSystemID = session.solarsystemid
        toFactionID = sm.StartService('faction').GetFactionOfSolarSystem(solarSystemID)
        if typeID is not None and evetypes.GetGroupID(typeID) not in (const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer):
            illegality = inventorycommon.typeHelpers.GetIllegalityInFaction(typeID, toFactionID)
            if illegality:
                return evetypes.GetName(typeID)
            return ''
        stuff = ''
        invItem = self.invCache.GetInventoryFromId(itemID)
        for item in invItem.List():
            try:
                illegality = inventorycommon.typeHelpers.GetIllegalityInFaction(item.typeID, toFactionID)
                if illegality:
                    stuff += evetypes.GetName(item.typeID) + ', '
                if evetypes.GetGroupID(item.typeID) in (const.groupCargoContainer,
                 const.groupSecureCargoContainer,
                 const.groupAuditLogSecureContainer,
                 const.groupFreightContainer):
                    sublegality = self.GetIllegality(item.itemID, solarSystemID=solarSystemID)
                    if sublegality:
                        stuff += sublegality + ', '
            except StandardError:
                log.LogTraceback('bork in illegality check 2')
                sys.exc_clear()

        return stuff[:-2]

    def StargateJump(self, stargateID, typeID, beaconID = None, solarSystemID = None):
        if beaconID:
            gateJumpSvc = sm.GetService('gatejump')
            if gateJumpSvc.IsNextSystemInRoute(solarSystemID):
                sm.ScatterEvent('OnClientEvent_JumpToNextSystemInRouteCmdExecuted')
            self.GetCloseAndTryCommand(stargateID, gateJumpSvc.JumpThroughGate, (stargateID,
             typeID,
             beaconID,
             solarSystemID), interactionRange=const.maxStargateJumpingDistance)

    def ActivateAccelerationGate(self, gateID):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(gateID)
        if slimItem:
            interactionRange = getattr(slimItem, 'gateActivationRange', const.maxStargateJumpingDistance) or const.maxStargateJumpingDistance
        else:
            interactionRange = const.maxStargateJumpingDistance
        self.GetCloseAndTryCommand(gateID, movementFunctions.RealActivateAccelerationGate, (gateID,), interactionRange=interactionRange)

    def ActivateAbyssalAccelerationGate(self, gateID):
        self.GetCloseAndTryCommand(gateID, movementFunctions.RealActivateAbyssalGate, (gateID,), interactionRange=const.maxStargateJumpingDistance)

    def ActivateAbyssalEndGate(self, gateID):
        self.GetCloseAndTryCommand(gateID, movementFunctions.RealActivateAbyssalEndGate, (gateID,), interactionRange=const.maxStargateJumpingDistance)

    def ActivatePVPAbyssalEndGate(self, gateID):
        self.GetCloseAndTryCommand(gateID, movementFunctions.RealActivatePVPAbyssalEndGate, (gateID,), interactionRange=const.maxStargateJumpingDistance)

    def ActivateVoidSpaceExitGate(self, gateID):
        self.GetCloseAndTryCommand(gateID, movementFunctions.RealActivateVoidSpaceExitGate, (gateID,), interactionRange=const.maxStargateJumpingDistance)

    def ActivateAbyssalEntranceAccelerationGate(self, id):
        self.GetCloseAndTryCommand(id, movementFunctions.RealActivateEntranceToAbyssalGate, (id,), interactionRange=const.maxStargateJumpingDistance)

    def ActivateRandomJumpTraceGate(self, id):
        self.GetCloseAndTryCommand(id, movementFunctions.RealActivateRandomFilamentGate, (id,), interactionRange=const.maxStargateJumpingDistance)

    def EnterWormhole(self, itemID):
        self.GetCloseAndTryCommand(itemID, movementFunctions.RealEnterWormhole, (itemID,), interactionRange=const.maxWormholeEnterDistance)

    def JumpThroughShipcaster(self, itemID):
        targetSolarsystemID, targetLandingPadID = GetTargetForShipcaster(itemID)
        self.GetCloseAndTryCommand(itemID, movementFunctions.RealJumpThroughShipcaster, (itemID, targetSolarsystemID, targetLandingPadID), interactionRange=SHIPCASTER_PROXIMITY_TO_JUMP)

    @staticmethod
    def CopyItemIDToClipboard(itemID):
        blue.pyos.SetClipboardData(str(itemID))

    def OpenCargo(self, itemID, *args):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(itemID)
        if slimItem:
            sm.ScatterEvent('OnOpenCargoExecuted', slimItem)
        self.GetCloseAndTryCommand(itemID, self.RealOpenCargo, (itemID,))
        if self.IsTooFarToExecuteCommand(itemID):
            eve.Message('OpenCargoTooFar')

    def RealOpenCargo(self, itemID, *args):
        if getattr(self, '_openingCargo', 0):
            return
        setattr(self, '_openingCargo', 1)
        uthread.new(self._OpenCargo, itemID)

    def _OpenCargo(self, _id):
        if type(_id) != types.ListType:
            _id = [_id]
        for itemID in _id:
            try:
                if itemID == eveCfg.GetActiveShip():
                    uicore.cmd.GetCommandAndExecute('OpenCargoHoldOfActiveShip')
                else:
                    slim = sm.GetService('michelle').GetItem(itemID)
                    if slim and slim.groupID == const.groupWreck:
                        invID = ('ItemWreck', itemID)
                    else:
                        invID = ('ItemFloatingCargo', itemID)
                    invCtrl.GetInvCtrlFromInvID(invID).GetItems()
                    if not (slim and HasCargoBayComponent(slim.typeID)):
                        sm.GetService('inv').AddTemporaryInvLocation(invID)
                    Inventory.OpenOrShow(invID=invID)
            finally:
                self._openingCargo = 0

    def OpenMercenaryDen(self, itemID):
        self.GetCloseAndTryCommand(itemID, self.RealOpenMercenaryDen, (itemID,))
        if not is_mercenary_den_close_enough_to_configure(itemID):
            eve.Message('ConfigureMercenaryDenTooFar')

    def RealOpenMercenaryDen(self, itemID):
        slim = sm.GetService('michelle').GetItem(itemID)
        if slim and HasMercenaryDenComponent(slim.typeID):
            openFunctions.OpenMercenaryDenWindow(slim.itemID, slim.typeID)

    @staticmethod
    def OpenPlanetCustomsOfficeImportWindow(customsOfficeID):
        sm.GetService('planetUI').OpenPlanetCustomsOfficeImportWindow(customsOfficeID)

    @staticmethod
    def OpenOrbitalSkyhookWindow(itemID):
        from eve.client.script.ui.shared.skyhook.skyhookWnd import OpenSkyhookWindow
        OpenSkyhookWindow(itemID)

    @staticmethod
    def OpenUpgradeWindow(orbitalID):
        sm.GetService('planetUI').OpenUpgradeWindow(orbitalID)

    @staticmethod
    def AbandonLoot(wreckID, *args):
        return menuFunctions.AbandonLoot(wreckID)

    @staticmethod
    def AbandonAllLoot(wreckID, *args):
        return menuFunctions.AbandonAllLoot(wreckID)

    def ShipCloneConfig(self, shipID = None):
        if shipID == eveCfg.GetActiveShip():
            uthread.new(self._ShipCloneConfig)

    @staticmethod
    def _ShipCloneConfig():
        uicore.cmd.GetCommandAndExecute('OpenShipConfig')

    @staticmethod
    def EnterPOSPassword():
        sm.StartService('pwn').EnterShipPassword()

    @staticmethod
    def EnterForceFieldPassword(towerID):
        sm.StartService('pwn').EnterTowerPassword(towerID)

    @staticmethod
    def Eject():
        return menuFunctions.Eject()

    @staticmethod
    def Board(shipID):
        return menuFunctions.Board(shipID)

    @staticmethod
    def BoardSMAShip(structureID, shipID):
        return menuFunctions.BoardSMAShip(structureID, shipID)

    @staticmethod
    def ToggleAutopilot(on):
        if on:
            sm.StartService('autoPilot').SetOn()
        else:
            sm.StartService('autoPilot').SetOff('toggled through menu')

    @staticmethod
    def AbortSelfDestructShip(pickid):
        return menuFunctions.AbortSelfDestructShip(pickid)

    @staticmethod
    def SelfDestructShip(pickid):
        return menuFunctions.SelfDestructShip(pickid)

    @staticmethod
    def SafeLogoff():
        return menuFunctions.SafeLogoff()

    @staticmethod
    def SetParent(pickid):
        sm.GetService('sceneManager').GetActiveSpaceCamera().LookAt(pickid, smooth=False)

    @staticmethod
    def SetInterest(pickid):
        sm.GetService('sceneManager').GetActiveSpaceCamera().Track(pickid)

    @staticmethod
    def TryLookAt(itemID):
        return menuFunctions.TryLookAt(itemID)

    @staticmethod
    def ToggleLookAt(itemID, **kwargs):
        return menuFunctions.ToggleLookAt(itemID, **kwargs)

    @staticmethod
    def SelectTarget(itemID):
        sm.GetService('stateSvc').SetState(itemID, states.multiSelected, True)
        if itemID in sm.GetService('fighters').shipFighterState.GetAllFighterIDsInSpace() or itemID == session.shipid:
            movementFunctions.SelectForNavigation(itemID)

    def Scoop(self, objectID, typeID, password = None):
        self.GetCloseAndTryCommand(objectID, self.RealScoop, (objectID, typeID, password))

    def RealScoop(self, objectID, typeID, password = None):
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            if not self.CheckIllegalOkay(objectID, typeID):
                return
            if not self.crimewatchSvc.IsOkToScoopItem(objectID):
                self.crimewatchSvc.SafetyActivated(const.shipSafetyLevelPartial)
                return
            try:
                if evetypes.GetCategoryID(typeID) == const.categoryFighter:
                    self.ScoopAbandonedFighterFromSpace(objectID, const.flagCargo)
                elif password is None:
                    ship.Scoop(objectID)
                else:
                    ship.Scoop(objectID, password)
            except UserError as e:
                if e.msg == 'ShpScoopSecureCC':
                    if password:
                        caption = localization.GetByLabel('UI/Menusvc/IncorrectPassword')
                        label = localization.GetByLabel('UI/Menusvc/PleaseTryEnteringPasswordAgain')
                    else:
                        caption = localization.GetByLabel('UI/Menusvc/PasswordRequired')
                        label = localization.GetByLabel('UI/Menusvc/PleaseEnterPassword')
                    passw = utilWindows.NamePopup(caption=caption, label=label, setvalue='', maxLength=50, passwordChar='*')
                    if passw:
                        self.Scoop(objectID, typeID, password=passw)
                else:
                    raise
                sys.exc_clear()

    def ScoopToFleetHangar(self, objectID, typeID):
        self.GetCloseAndTryCommand(objectID, self.RealScoopToFleetHangar, (objectID, typeID))

    def RealScoopToFleetHangar(self, objectID, typeID):
        ship = sm.GetService('gameui').GetShipAccess()
        if ship:
            if not self.CheckIllegalOkay(objectID, typeID):
                return
            if not self.crimewatchSvc.IsOkToScoopItem(objectID):
                self.crimewatchSvc.SafetyActivated(const.shipSafetyLevelPartial)
                return
            if evetypes.GetCategoryID(typeID) == const.categoryFighter:
                self.ScoopAbandonedFighterFromSpace(objectID, const.flagFleetHangar)
            else:
                ship.ScoopToFleetHangar(objectID)

    def ScoopToFighterBay(self, objectID, typeID):
        self.GetCloseAndTryCommand(objectID, self.RealScoopToFighterBay, (objectID, typeID))

    def RealScoopToFighterBay(self, objectID, typeID):
        ship = sm.GetService('gameui').GetShipAccess()
        if ship:
            if not self.CheckIllegalOkay(objectID, typeID):
                return
            self.ScoopAbandonedFighterFromSpace(objectID, const.flagFighterBay)

    def ScoopToInfrastructureHold(self, objectID, typeID):
        ship = sm.GetService('gameui').GetShipAccess()
        if ship:
            ship.ScoopToInfrastructureHold(objectID)

    def CheckIllegalOkay(self, objectID, typeID):
        toFactionID = sm.StartService('faction').GetFactionOfSolarSystem(session.solarsystemid)
        stuff = self.GetIllegality(objectID, typeID)
        if stuff and toFactionID and eve.Message('ConfirmScoopWithIllicitGoods', {'faction': cfg.eveowners.Get(toFactionID).name}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return False
        return True

    def ScoopSMA(self, objectID):
        self.GetCloseAndTryCommand(objectID, self.RealScoopSMA, (objectID,))

    @staticmethod
    def RealScoopSMA(objectID):
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            ship.ScoopToSMA(objectID)

    def ScoopAbandonedFighterFromSpace(self, fighterID, toFlagID):
        self.fighters.ScoopAbandonedFighterFromSpace(fighterID, toFlagID)

    @staticmethod
    def QuickBuy(typeID, quantity = 1):
        sm.StartService('marketutils').Buy(typeID, quantity=quantity)

    @staticmethod
    def SellItems(invItems):
        return marketMenu.SellItems(invItems)

    @staticmethod
    def SellPlex():
        from eve.client.script.ui.shared.inventory.plexVault import PlexVaultController
        controller = PlexVaultController()
        controller.SellPlex()

    @staticmethod
    def QuickContract(invItems, *args):
        sm.GetService('contracts').OpenCreateContract(items=invItems)

    @staticmethod
    def ShowMarketDetails(invItem = None, typeID = None):
        uthread.new(sm.StartService('marketutils').ShowMarketDetails, typeID or invItem.typeID, None)

    def _AddMarketDetailsOption(self, menuEntries, typeID):
        menuEntries.append(MenuEntryData(MenuLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), lambda : self.ShowMarketDetails(typeID=typeID), internalName='ViewMarketDetails', typeID=typeID))

    def GetContainerContents(self, invItem, dockableID):
        return invItemFunctions.GetContainerContents(invItem, self.invCache, dockableID)

    @staticmethod
    def AddToQuickBar(typeID, parent = 0):
        return menuFunctions.AddToQuickBar(typeID, parent)

    @staticmethod
    def RemoveFromQuickBar(node):
        return menuFunctions.RemoveFromQuickBar(node)

    @staticmethod
    def ActivateShip(invItem):
        if invItem.singleton and not uicore.uilib.Key(uiconst.VK_CONTROL):
            sm.StartService('station').TryActivateShip(invItem)

    @staticmethod
    def LeaveShip(invItem):
        if invItem.singleton and not uicore.uilib.Key(uiconst.VK_CONTROL):
            sm.StartService('station').TryLeaveShip(invItem)

    def StripFitting(self, invItem):
        if eve.Message('AskStripShip', None, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            shipID = invItem.itemID
            self.invCache.StripFitting(shipID)

    @staticmethod
    def ExitDockableLocation(*args, **kwargs):
        uicore.cmd.GetCommandAndExecute('CmdExitStation')

    def CompressItemInSpace(self, compressibleItem, compressionFacilityBallID):
        return CompressItemInSpace(compressibleItem, compressionFacilityBallID)

    def CompressItemInStructure(self, compressibleItem):
        return CompressItemInStructure(compressibleItem)

    def DecompressGasInStructure(self, compressedGasItem):
        return decompress_gas(compressedGasItem.itemID)

    @staticmethod
    def RepackageItems(invItems):
        invItemFunctions.RepackageItems(invItems)

    def Break(self, invItems):
        return invItemFunctions.Break(invItems, self.invCache)

    @staticmethod
    def DeliverCourierContract(invItem):
        sm.GetService('contracts').DeliverCourierContractFromItemID(invItem.itemID)

    @staticmethod
    def FindCourierContract(invItem):
        sm.GetService('contracts').FindCourierContractFromItemID(invItem.itemID)

    @staticmethod
    def LaunchDrones(invItems, *args):
        sm.GetService('godma').GetStateManager().SendDroneSettings()
        eveMisc.LaunchFromShip(invItems)

    @staticmethod
    def DeployStructure(invItems):
        sm.GetService('structureDeployment').Deploy(invItems[0])

    @staticmethod
    def LaunchForSelf(invItems):
        eveMisc.LaunchFromShip(invItems, session.charid, maxQty=1)

    @staticmethod
    def LaunchForCorp(invItems, ignoreWarning = False):
        makesCorpWarDeccable = False
        for eachItem in invItems:
            if eachItem.categoryID in (const.categoryOrbital, const.categoryStructure) or eachItem.groupID == const.groupControlTower:
                makesCorpWarDeccable = True
                break

        if makesCorpWarDeccable and sm.GetService('warPermit').DoesMyCorpHaveNegativeWarPermit():
            if eve.Message('ConfirmDeployFirstStructureMakeWarDeccable', {}, uiconst.YESNO) != uiconst.ID_YES:
                return
        eveMisc.LaunchFromShip(invItems, session.corpid, ignoreWarning, maxQty=1)

    @staticmethod
    def LaunchSMAContents(invItems):
        return invItemFunctions.LaunchSMAContents(invItems[0])

    @staticmethod
    def LaunchShipFromWreck(invItems):
        return invItemFunctions.LaunchShipOrContainerFromWreckOrContainer(invItems[0])

    @staticmethod
    def LaunchContainerFromContainer(invItem):
        return invItemFunctions.LaunchShipOrContainerFromWreckOrContainer(invItem)

    @staticmethod
    def Jettison(invItems):
        return invItemFunctions.Jettison(invItems)

    @staticmethod
    def JettisonFuel(invItems):
        return invItemFunctions.JettisonStructureFuel(invItems)

    def TrashInvItems(self, invItems):
        return invItemFunctions.TrashInvItems(invItems, self.invCache)

    @staticmethod
    def TrainNow(invItems):
        return invItemFunctions.TrainNow(invItems)

    @staticmethod
    def InjectSkillIntoBrain(invItems):
        return invItemFunctions.InjectSkillIntoBrain(invItems)

    @staticmethod
    def PlugInImplant(invItems):
        return invItemFunctions.PlugInImplant(invItems)

    @staticmethod
    def RedeemCurrency(item, qty):
        return menuFunctions.RedeemCurrency(item, qty)

    @staticmethod
    def ActivateCharacterReSculpt(itemID):
        return menuFunctions.ActivateCharacterReSculpt(itemID)

    @staticmethod
    def ActivateMultiTraining(itemID):
        return ActivateMultiTraining(itemID=itemID)

    @staticmethod
    def ActivateSkillExtractor(item):
        return menuFunctions.ActivateSkillExtractor(item)

    @staticmethod
    def ActivateSkillInjector(item, quantity):
        return menuFunctions.ActivateSkillInjector(item, quantity)

    def GetActivateSkillInjectorMenuEntry(self, invItem):
        if invItem.typeID == invconst.typeAlphaTrainingInjector:
            quantity = 1
        else:
            quantity = invItem.stacksize
        menuLabel = MenuLabel('UI/Commands/ActivateSkillInjector', {'injector': invItem.typeID,
         'quantity': quantity})
        return [[menuLabel, self.ActivateSkillInjector, (invItem, quantity)]]

    @staticmethod
    def OpenCrate(typeID, itemID, stacksize):
        return menuFunctions.OpenCrate(typeID, itemID, stacksize)

    @staticmethod
    def CraftDynamicItem(item):
        return menuFunctions.CraftDynamicItem(item)

    @staticmethod
    def ActivateAbyssalKey(item):
        return menuFunctions.ActivateAbyssalKey(item)

    @staticmethod
    def ActivateWarpVector(item):
        return menuFunctions.ActivateWarpVector(item)

    @staticmethod
    def ActivateVoidSpaceKey(item):
        return menuFunctions.ActivateVoidSpaceKey(item)

    @staticmethod
    def ActivateRandomJumpKey(item):
        return menuFunctions.ActivateRandomJumpKey(item)

    @staticmethod
    def ActivatePVPfilamentKey(item):
        return menuFunctions.ActivatePVPfilamentKey(item)

    @staticmethod
    def ConsumeBooster(invItems):
        return invItemFunctions.ConsumeBooster(invItems)

    def DeliverToStructure(self, invItems):
        return invItemFunctions.DeliverToStructure(invItems, self.invCache)

    def AssembleContainer(self, invItems):
        invMgr = self.invCache.GetInventoryMgr()
        for invItem in invItems:
            invMgr.AssembleCargoContainer(invItem.itemID, None, 0.0)

    @staticmethod
    def ShowInIndustryWindow(invItem):
        Industry.OpenOrShowBlueprint(blueprintID=invItem.itemID)

    @staticmethod
    def SetHomeStation(stationID):
        homestation.set_home_station(stationID)

    @staticmethod
    @ThrottlePerSecond()
    def AssembleShip(invItems):
        return invItemFunctions.AssembleShip(invItems)

    @staticmethod
    @ThrottlePerSecond()
    def AssembleAndBoardShip(invItem):
        invItemFunctions.AssembleAndBoardShip(invItem)

    @staticmethod
    def HandleMultipleCallError(droneID, ret, messageName):
        return droneFunctions.HandleMultipleCallError(droneID, ret, messageName)

    @staticmethod
    def EngageTarget(droneIDs):
        return droneFunctions.EngageTarget(droneIDs)

    @staticmethod
    def Assist(charID, droneIDs):
        return droneFunctions.Assist(charID, droneIDs)

    @staticmethod
    def Guard(charID, droneIDs):
        return droneFunctions.Guard(charID, droneIDs)

    @staticmethod
    def MineRepeatedly(droneIDs):
        return droneFunctions.MineRepeatedly(droneIDs)

    @staticmethod
    def Salvage(droneIDs):
        return droneFunctions.Salvage(droneIDs)

    @staticmethod
    def DroneUnanchor(droneIDs):
        return droneFunctions.DroneUnanchor(droneIDs)

    @staticmethod
    def ReturnAndOrbit(droneIDs):
        return droneFunctions.ReturnAndOrbit(droneIDs)

    @staticmethod
    def ReturnToDroneBay(droneIDs):
        return droneFunctions.ReturnToDroneBay(droneIDs)

    def ScoopToDroneBay(self, objectIDs):
        if len(objectIDs) == 1:
            self.GetCloseAndTryCommand(objectIDs[0], self.RealScoopToDroneBay, (objectIDs,))
        else:
            self.RealScoopToDroneBay(objectIDs)

    @staticmethod
    def RealScoopToDroneBay(objectIDs):
        return droneFunctions.RealScoopToDroneBay(objectIDs)

    def FitDrone(self, invItems):
        return droneFunctions.FitDrone(invItems, self.invCache)

    @staticmethod
    def AbandonDrone(droneIDs):
        return droneFunctions.AbandonDrone(droneIDs)

    @staticmethod
    def CopyItemIDAndMaybeQuantityToClipboard(invItem):
        return menuFunctions.CopyItemIDAndMaybeQuantityToClipboard(invItem)

    def SetName(self, invOrSlimItem):
        return menuFunctions.SetName(invOrSlimItem, self.invCache)

    def AskNewContainerPwd(self, invItems, desc, which = 1):
        for invItem in invItems:
            self.AskNewContainerPassword(invItem.itemID, desc, which)

    @staticmethod
    def GetDefaultActionDistance(key):
        return defaultRangeUtils.FetchRangeSetting(key)

    def CopyCoordinates(self, itemID):
        ball = self.michelle.GetBall(itemID)
        if ball:
            blue.pyos.SetClipboardData(str((ball.x, ball.y, ball.z)))

    @staticmethod
    def AnchorOrbital(itemID):
        posMgr = Moniker('posMgr', session.solarsystemid)
        posMgr.AnchorOrbital(itemID)

    @staticmethod
    def UnanchorOrbital(itemID):
        posMgr = Moniker('posMgr', session.solarsystemid)
        posMgr.UnanchorOrbital(itemID)

    @staticmethod
    def ConfigureOrbital(item):
        sm.GetService('planetUI').OpenConfigureWindow(item)

    @staticmethod
    def ConfigureIndustryTax(itemID, typeID):
        facilityName = cfg.evelocations.Get(itemID).name
        if not facilityName:
            facilityName = evetypes.GetName(typeID)
        FacilityTaxWindow.Open(facilityID=itemID, facilityName=facilityName)

    @staticmethod
    def IsTooFarToExecuteCommand(itemID, interactionRange = DEFAULT_INTERACTION_RANGE):
        if not sm.GetService('autoPilot').IsSystemNavigationComplete(itemID, interactionRange):
            return True

    @staticmethod
    def GetCloseAndTryCommand(itemID, cmdMethod, args, interactionRange = DEFAULT_INTERACTION_RANGE):
        sm.GetService('autoPilot').NavigateSystemTo(itemID, interactionRange, cmdMethod, *args)

    @staticmethod
    def ReconnectToDrones():
        return droneFunctions.ReconnectToDrones()

    @staticmethod
    def SetDefaultDist(key):
        return movementFunctions.SetDefaultDist(key)

    @staticmethod
    def AddDisabledEntryForWarp(menuEntries, textPath):
        menuEntries.append(MenuEntryData(MenuLabel(textPath), isEnabled=False, hint=localization.GetByLabel('UI/Menusvc/MenuHints/YouAreInWarp')))
        menuEntries.reasonsWhyNotAvailable[textPath] = localization.GetByLabel('UI/Menusvc/MenuHints/YouAreInWarp')

    @staticmethod
    def DoBoardingMoment():
        currentView = sm.GetService('viewState').GetCurrentView()
        if currentView is None or currentView.name != 'hangar':
            return
        currentView.play_boarding_moment()

    def GetAbyssalGateFunction(self, typeID):
        if typeID == const.typeAbyssEncounterGate:
            return self.ActivateAbyssalAccelerationGate
        if typeID == const.typeAbyssEntranceGate:
            return self.ActivateAbyssalEntranceAccelerationGate
        if typeID == const.typeAbyssExitGate:
            return self.ActivateAbyssalEndGate
        if typeID == const.typeAbyssPvPGate:
            return self.ActivatePVPAbyssalEndGate
        if typeID == const.typeVoidSpaceExitGate:
            return self.ActivateVoidSpaceExitGate
