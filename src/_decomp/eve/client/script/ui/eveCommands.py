#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\eveCommands.py
import sys
import urllib
import urlparse
import blue
import bluepy
import carbon.client.script.sys.appUtils as appUtils
import carbonui.const as uiconst
import carbonui.services.command as command
import destiny
import eve.client.script.parklife.fxSequencer as FxSequencer
import eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst as agencyContentGroupConst
import eve.common.lib.appConst as appConst
import eve.common.script.sys.eveCfg as eveCfg
import evecamera
import evegraphics.settings as gfxsettings
import evespacemouse
import inventorycommon.const as invConst
import localization
import shipmode.data
import structures
import trinity
import uthread
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_CONTENT, ROLE_GML, ROLE_PROGRAMMER, ROLEMASK_ELEVATEDPLAYER
from UITree import UITree
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.sessions import ThrottlePerMinute
from carbonui.control.contextMenu.menuUtil import ClearMenuLayer
from carbonui.control.window import Window
from carbonui.services.command import CommandService
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from charactercreator.client.characterCreationMetrics import check_for_character_creation_exit
from eve.client.script.parklife import bracketSettings
from eve.client.script.parklife.dungeonHelper import IsJessicaOpen
from eve.client.script.ui.camera.cameraUtil import IsAutoTrackingEnabled
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.shipSKINRWindow import ShipSKINRWindow
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.eveCommandsDescFunctions import GetCmdLogoffHint
from eve.client.script.ui.inflight.capitalnavigation import CapitalNav
from eve.client.script.ui.inflight.drones.droneGroupsController import GetDroneGroupsController
from eve.client.script.ui.inflight.drones.droneSettings import drones_aggressive_setting, drones_focus_fire_setting
from eve.client.script.ui.inflight.drones.dronesUtil import GetDronesInBay
from eve.client.script.ui.inflight.dungeoneditor import DungeonEditor, DungeonObjectProperties
from eve.client.script.ui.inflight.moonmining import MoonMining
from eve.client.script.ui.inflight.overview import overviewWindowUtil
from eve.client.script.ui.inflight.overviewSettings.overviewSettingsWnd import OverviewSettingsWnd
from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow
from eve.client.script.ui.inflight.scannerFiles.directionalScannerWindow import DirectionalScanner
from eve.client.script.ui.inflight.scannerFiles.moonScanner import MoonScanner
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import IsProbeScanEmbeddedPanelOpen
from eve.client.script.ui.inflight.shipstance import set_stance
from eve.client.script.ui.mapCmdWindow import MapCmdWindow
from eve.client.script.ui.services.bugReporting import BugReportingWindow
from eve.client.script.ui.services.menuSvcExtras import movementFunctions, droneFunctions
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import DockOrJumpOrActivateGate, KeepAtRange, Orbit
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem, GetSelectedShipAndFighters
from eve.client.script.ui.shared.addressBookWindow import AddressBookWindow
from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
from eve.client.script.ui.shared.assetsWindow import AssetsWindow
from eve.client.script.ui.shared.autopilotSettings import AutopilotSettings
from eve.client.script.ui.shared.bookmarks.standaloneBookmarkWnd import StandaloneBookmarkWnd
from eve.client.script.ui.shared.bountyWindow import BountyWindow
from eve.client.script.ui.shared.careerPortal.careerPortalWnd import CareerPortalDockablePanel
from eve.client.script.ui.shared.cloneGrade import open_omega_upgrade_window
from eve.client.script.ui.shared.ctrltab import CtrlTabWindow
from eve.client.script.ui.shared.eveCalendar import CalendarWnd
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.fwEnlistmentWnd import FwEnlistmentWnd
from eve.client.script.ui.shared.fittingMgmtWindow import FittingMgmt
from eve.client.script.ui.shared.fittingScreen.fittingWnd import FittingWindow
from eve.client.script.ui.shared.fleet.fleet import WatchListPanel
from eve.client.script.ui.shared.fleet.fleetwindow import FleetWindow
from eve.client.script.ui.shared.industry.industryWnd import Industry
from eve.client.script.ui.shared.inventory import invWindow
from eve.client.script.ui.shared.inventory.invWindow import Inventory
from eve.client.script.ui.shared.ledger.ledgerWnd import LedgerWindow
from eve.client.script.ui.shared.mapView.dockPanelUtil import GetDockPanelManager
from eve.client.script.ui.shared.mapView.mapViewUtil import IsDirectionalScannerOpen
from eve.client.script.ui.shared.mapView.settings import classic_map_enabled_setting
from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
from eve.client.script.ui.shared.maps.browserwindow import MapBrowserWnd
from eve.client.script.ui.shared.market.marketOrdersWnd import MarketOrdersWnd
from eve.client.script.ui.shared.market.marketbase import RegionalMarket
from eve.client.script.ui.shared.neocom.calculator import Calculator
from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
from eve.client.script.ui.shared.neocom.charsheet import PANEL_JUMPCLONES
from eve.client.script.ui.shared.neocom.compare import TypeCompare
from eve.client.script.ui.shared.neocom.contracts.contractsWnd import ContractsWindow
from eve.client.script.ui.shared.neocom.corporation.corpPanelConst import CorpPanel
from eve.client.script.ui.shared.neocom.corporation.corporationWindow import CorporationWindow
from eve.client.script.ui.shared.neocom.evemail import MailWindow
from eve.client.script.ui.shared.neocom.help import HelpWindow
from eve.client.script.ui.shared.neocom.journal import JournalWindow
from eve.client.script.ui.shared.neocom.locations.window import LocationsWindow
from eve.client.script.ui.shared.neocom.neocom.neocomUtil import ResetNeocomButtons
from eve.client.script.ui.shared.neocom.notepad import NotepadWindow
from eve.client.script.ui.shared.neocom.wallet.walletWnd import WalletWindow
from eve.client.script.ui.cosmetics.structure.paintToolWnd import PaintToolWnd
from eve.client.script.ui.shared.planet.mecDen.mercDenWnd import MyMercDensWnd
from eve.client.script.ui.shared.planet.planetWindow import PlanetWindow
from eve.client.script.ui.shared.pointerTool.pointerWnd import PointerToolWnd
from eve.client.script.ui.shared.preview import PreviewCharacterWnd
from eve.client.script.ui.shared.shipTree.shipTreeDockablePanel import ShipTreeDockablePanel
from eve.client.script.ui.shared.shipconfig import ShipConfig
from eve.client.script.ui.shared.uilog import LoggerWindow
from eve.client.script.ui.shared.videowindow import VideoPlayerWindow
from eve.client.script.ui.skillPlan.skillPlanDockablePanel import SkillPlanDockablePanel
from eve.client.script.ui.skillTree.skillTreeDockablePanel import SkillTreeDockablePanel
from eve.client.script.ui.station.insurance.base_insurance import InsuranceWindow
from eve.client.script.ui.station.loyaltyPointStore.lpStoreWindow import LPStoreWindow
from eve.client.script.ui.station.repairshop.base_repairshop import RepairShopWindow
from eve.client.script.ui.station.securityOfficeWindow import SecurityOfficeWindow
from eve.client.script.ui.structure.accessGroups.accesGroupsWnd import AccessGroupsWnd
from eve.client.script.ui.structure.structureBrowser.structureBrowserWnd import StructureBrowserWnd
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.script.net import eveMoniker
from eve.common.script.sys import idCheckers
from eve.common.script.util.facwarCommon import IsPirateFWFaction
from eve.common.script.util.urlUtil import IsClientLaunchedThroughSteam, AppendSteamOriginIfApplies
from eve.devtools.script.enginetools import EngineToolsLauncher
from eveNewCommands.client.escapeCommand import EscapeCommand
from eveNewCommands.client.escapeCommandAdapter import EscapeCommandAdapter
from evecamera.locationalcamera import get_orbit_camera_by_solar_system
from eveexceptions import UserError
from eveservices.menu import GetMenuService
from eveuniverse.solar_systems import is_tactical_camera_suppressed, is_map_browser_suppressed, is_directional_scanner_suppressed, is_scanning_suppressed, is_solarsystem_map_suppressed
from fsdBuiltData.client.effects import GetEffectGuids
from fwwarzone.client.dashboard.fwWarzoneDashboard import FwWarzoneDashboard
from globalConfig.getFunctions import IsContentComplianceControlSystemActive
from globalConfig.getFunctions import IsPlayerBountyHidden, ArePointerLinksActive, AllowCharacterLogoff
from inventorycommon.util import IsModularShip
from jobboard.client import get_job_board_service
from jobboard.client.feature_flag import is_job_board_available, are_missions_in_job_board_available
from launchdarkly.client.featureflag import create_string_flag_check
from localization import GetByLabel
from localization.util import AmOnChineseServer
from logmodule import LogException
from loyaltypoints.lpUtil import get_normal_lp_stores_in_station
from menucheckers import SessionChecker
from pirateinsurgency.client.dashboard.dashboard import InsurgentsDashboard
from projectdiscovery.client.windowclass import get_project_discovery_window_class
from reprocessing.ui.reprocessingWnd import ReprocessingWnd
from seasons.client.util import OpenSeasonsWindow
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty
from uthread2.callthrottlers import CallCombiner
from xmppchatclient.xmppchatchannels import XmppChatChannels
contextFiS = 1
contextIncarna = 2
labelsByFuncName = {'CmdAccelerate': 'UI/Commands/CmdAccelerate',
 'CmdActivateHighPowerSlot1': 'UI/Commands/CmdActivateHighPowerSlot1',
 'CmdActivateHighPowerSlot2': 'UI/Commands/CmdActivateHighPowerSlot2',
 'CmdActivateHighPowerSlot3': 'UI/Commands/CmdActivateHighPowerSlot3',
 'CmdActivateHighPowerSlot4': 'UI/Commands/CmdActivateHighPowerSlot4',
 'CmdActivateHighPowerSlot5': 'UI/Commands/CmdActivateHighPowerSlot5',
 'CmdActivateHighPowerSlot6': 'UI/Commands/CmdActivateHighPowerSlot6',
 'CmdActivateHighPowerSlot7': 'UI/Commands/CmdActivateHighPowerSlot7',
 'CmdActivateHighPowerSlot8': 'UI/Commands/CmdActivateHighPowerSlot8',
 'CmdActivateLowPowerSlot1': 'UI/Commands/CmdActivateLowPowerSlot1',
 'CmdActivateLowPowerSlot2': 'UI/Commands/CmdActivateLowPowerSlot2',
 'CmdActivateLowPowerSlot3': 'UI/Commands/CmdActivateLowPowerSlot3',
 'CmdActivateLowPowerSlot4': 'UI/Commands/CmdActivateLowPowerSlot4',
 'CmdActivateLowPowerSlot5': 'UI/Commands/CmdActivateLowPowerSlot5',
 'CmdActivateLowPowerSlot6': 'UI/Commands/CmdActivateLowPowerSlot6',
 'CmdActivateLowPowerSlot7': 'UI/Commands/CmdActivateLowPowerSlot7',
 'CmdActivateLowPowerSlot8': 'UI/Commands/CmdActivateLowPowerSlot8',
 'CmdActivateMediumPowerSlot1': 'UI/Commands/CmdActivateMediumPowerSlot1',
 'CmdActivateMediumPowerSlot2': 'UI/Commands/CmdActivateMediumPowerSlot2',
 'CmdActivateMediumPowerSlot3': 'UI/Commands/CmdActivateMediumPowerSlot3',
 'CmdActivateMediumPowerSlot4': 'UI/Commands/CmdActivateMediumPowerSlot4',
 'CmdActivateMediumPowerSlot5': 'UI/Commands/CmdActivateMediumPowerSlot5',
 'CmdActivateMediumPowerSlot6': 'UI/Commands/CmdActivateMediumPowerSlot6',
 'CmdActivateMediumPowerSlot7': 'UI/Commands/CmdActivateMediumPowerSlot7',
 'CmdActivateMediumPowerSlot8': 'UI/Commands/CmdActivateMediumPowerSlot8',
 'CmdAlignToItem': 'UI/Commands/CmdAlignToItem',
 'CmdApproachItem': 'UI/Commands/CmdApproachItem',
 'CmdCycleFleetBroadcastScope': 'UI/Commands/CmdCycleFleetBroadcastScope',
 'CmdDecelerate': 'UI/Commands/CmdDecelerate',
 'CmdDockOrJumpOrActivateGate': 'UI/Commands/CmdDockOrJumpOrActivateGate',
 'CmdDronesEngage': 'UI/Commands/CmdDronesEngage',
 'CmdDronesReturnAndOrbit': 'UI/Commands/CmdDronesReturnAndOrbit',
 'CmdDronesReturnToBay': 'UI/Commands/CmdDronesReturnToBay',
 'CmdLaunchFavoriteDrones': 'UI/Drones/LaunchDrones',
 'CmdExitStation': 'UI/Commands/CmdExitStation',
 'CmdEnterHangar': 'UI/Commands/EnterHangar',
 'CmdEnterStructure': 'UI/Commands/EnterStructure',
 'CmdFleetBroadcast_EnemySpotted': 'UI/Fleet/FleetBroadcast/Commands/EnemySpotted',
 'CmdFleetBroadcast_HealArmor': 'UI/Fleet/FleetBroadcast/Commands/HealArmor',
 'CmdFleetBroadcast_HealCapacitor': 'UI/Fleet/FleetBroadcast/Commands/HealCapacitor',
 'CmdFleetBroadcast_HealShield': 'UI/Fleet/FleetBroadcast/Commands/HealShield',
 'CmdFleetBroadcast_HoldPosition': 'UI/Fleet/FleetBroadcast/Commands/HoldPosition',
 'CmdFleetBroadcast_InPosition': 'UI/Fleet/FleetBroadcast/Commands/InPosition',
 'CmdFleetBroadcast_JumpBeacon': 'UI/Fleet/FleetBroadcast/Commands/JumpBeacon',
 'CmdFleetBroadcast_Location': 'UI/Fleet/FleetBroadcast/Commands/Location',
 'CmdFleetBroadcast_NeedBackup': 'UI/Fleet/FleetBroadcast/Commands/NeedBackup',
 'CmdForceFadeFromBlack': 'UI/Commands/CmdForceFadeFromBlack',
 'CmdHideCursor': 'UI/Commands/CmdHideCursor',
 'CmdHideUI': 'UI/Commands/CmdHideUI',
 'CmdKeepItemAtRange': 'UI/Commands/CmdKeepItemAtRange',
 'CmdLockTargetItem': 'UI/Commands/CmdLockTargetItem',
 'CmdSelectTargetItem': 'UI/Commands/CmdSelectTargetItem',
 'CmdLogOff': 'UI/Commands/CmdLogOff',
 'CmdMoveBackward': 'UI/Commands/CmdMoveBackward',
 'CmdMoveForward': 'UI/Commands/CmdMoveForward',
 'CmdMoveLeft': 'UI/Commands/CmdMoveLeft',
 'CmdMoveRight': 'UI/Commands/CmdMoveRight',
 'CmdNextStackedWindow': 'UI/Commands/CmdNextStackedWindow',
 'CmdNextTab': 'UI/Commands/CmdNextTab',
 'CmdOpenNewMessage': 'UI/Commands/CmdOpenNewMessage',
 'CmdOrbitItem': 'UI/Commands/CmdOrbitItem',
 'CmdOverloadHighPowerRack': 'UI/Commands/CmdOverloadHighPowerRack',
 'CmdOverloadHighPowerSlot1': 'UI/Commands/CmdOverloadHighPowerSlot1',
 'CmdOverloadHighPowerSlot2': 'UI/Commands/CmdOverloadHighPowerSlot2',
 'CmdOverloadHighPowerSlot3': 'UI/Commands/CmdOverloadHighPowerSlot3',
 'CmdOverloadHighPowerSlot4': 'UI/Commands/CmdOverloadHighPowerSlot4',
 'CmdOverloadHighPowerSlot5': 'UI/Commands/CmdOverloadHighPowerSlot5',
 'CmdOverloadHighPowerSlot6': 'UI/Commands/CmdOverloadHighPowerSlot6',
 'CmdOverloadHighPowerSlot7': 'UI/Commands/CmdOverloadHighPowerSlot7',
 'CmdOverloadHighPowerSlot8': 'UI/Commands/CmdOverloadHighPowerSlot8',
 'CmdOverloadLowPowerRack': 'UI/Commands/CmdOverloadLowPowerRack',
 'CmdOverloadLowPowerSlot1': 'UI/Commands/CmdOverloadLowPowerSlot1',
 'CmdOverloadLowPowerSlot2': 'UI/Commands/CmdOverloadLowPowerSlot2',
 'CmdOverloadLowPowerSlot3': 'UI/Commands/CmdOverloadLowPowerSlot3',
 'CmdOverloadLowPowerSlot4': 'UI/Commands/CmdOverloadLowPowerSlot4',
 'CmdOverloadLowPowerSlot5': 'UI/Commands/CmdOverloadLowPowerSlot5',
 'CmdOverloadLowPowerSlot6': 'UI/Commands/CmdOverloadLowPowerSlot6',
 'CmdOverloadLowPowerSlot7': 'UI/Commands/CmdOverloadLowPowerSlot7',
 'CmdOverloadLowPowerSlot8': 'UI/Commands/CmdOverloadLowPowerSlot8',
 'CmdOverloadMediumPowerRack': 'UI/Commands/CmdOverloadMediumPowerRack',
 'CmdOverloadMediumPowerSlot1': 'UI/Commands/CmdOverloadMediumPowerSlot1',
 'CmdOverloadMediumPowerSlot2': 'UI/Commands/CmdOverloadMediumPowerSlot2',
 'CmdOverloadMediumPowerSlot3': 'UI/Commands/CmdOverloadMediumPowerSlot3',
 'CmdOverloadMediumPowerSlot4': 'UI/Commands/CmdOverloadMediumPowerSlot4',
 'CmdOverloadMediumPowerSlot5': 'UI/Commands/CmdOverloadMediumPowerSlot5',
 'CmdOverloadMediumPowerSlot6': 'UI/Commands/CmdOverloadMediumPowerSlot6',
 'CmdOverloadMediumPowerSlot7': 'UI/Commands/CmdOverloadMediumPowerSlot7',
 'CmdOverloadMediumPowerSlot8': 'UI/Commands/CmdOverloadMediumPowerSlot8',
 'CmdPickPortrait0': 'UI/Commands/PickPortrait0',
 'CmdPickPortrait1': 'UI/Commands/PickPortrait1',
 'CmdPickPortrait2': 'UI/Commands/PickPortrait2',
 'CmdPickPortrait3': 'UI/Commands/PickPortrait3',
 'CmdPrevStackedWindow': 'UI/Commands/CmdPrevStackedWindow',
 'CmdPrevTab': 'UI/Commands/CmdPrevTab',
 'CmdQuitGame': 'UI/Commands/CmdQuitGame',
 'CmdReconnectToDrones': 'UI/Commands/ReconnectToLostDrones',
 'CmdReloadAmmo': 'UI/Commands/CmdReloadAmmo',
 'CmdResetMonitor': 'UI/Commands/CmdResetMonitor',
 'CmdSelectNextTarget': 'UI/Commands/CmdSelectNextTarget',
 'CmdSelectPrevTarget': 'UI/Commands/CmdSelectPrevTarget',
 'CmdSendBroadcast_Target': 'UI/Commands/CmdSendBroadcast_Target',
 'CmdSendBroadcast_HealTarget': 'UI/Commands/CmdSendBroadcast_HealTarget',
 'CmdSendBroadcast_WarpToItemID': 'UI/Fleet/FleetBroadcast/Commands/BroadcastWarpTo',
 'CmdSendBroadcast_AlignToItemID': 'UI/Fleet/FleetBroadcast/Commands/BroadcastAlignTo',
 'CmdSendBroadcast_JumpToItemID': 'UI/Fleet/FleetBroadcast/Commands/BroadcastJumpTo',
 'CmdSetChatChannelFocus': 'UI/Commands/CmdSetChatChannelFocus',
 'CmdSetSearchBarFocus': 'UI/Commands/CmdSetSearchBarFocus',
 'CmdSetOverviewFocus': 'UI/Commands/CmdSetOverviewFocus',
 'CmdSetShipFullSpeed': 'UI/Commands/CmdSetShipFullSpeed',
 'CmdShowItemInfo': 'UI/Commands/CmdShowItemInfo',
 'CmdStopShip': 'UI/Commands/CmdStopShip',
 'CmdToggleAggressivePassive': 'UI/Commands/CmdToggleAggressivePassive',
 'CmdToggleAutopilot': 'UI/Commands/CmdToggleAutopilot',
 'CmdToggleCombatView': 'UI/Commands/CmdToggleCombatView',
 'CmdToggleDroneFocusFire': 'UI/Commands/CmdToggleDroneFocusFire',
 'CmdToggleEffects': 'UI/Commands/CmdToggleEffects',
 'CmdToggleEffectTurrets': 'UI/Commands/CmdToggleEffectTurrets',
 'CmdToggleLookAtItem': 'UI/Commands/CmdToggleLookAtItem',
 'CmdToggleCameraTracking': 'UI/Commands/CmdToggleCameraTracking',
 'CmdToggleShowAllBrackets': 'UI/Commands/CmdToggleShowAllBrackets',
 'CmdToggleShowNoBrackets': 'UI/Commands/CmdToggleShowNoBrackets',
 'CmdToggleShowSpecialBrackets': 'UI/Commands/CmdToggleShowSpecialBrackets',
 'CmdToggleTacticalOverlay': 'UI/Commands/CmdToggleTacticalOverlay',
 'CmdToggleTargetItem': 'UI/Commands/CmdToggleTargetItem',
 'CmdUnlockTargetItem': 'UI/Commands/CmdUnlockTargetItem',
 'CmdUnlockTargetItems': 'UI/Commands/CmdUnlockTargetItems',
 'CmdWarpToItem': 'UI/Commands/CmdWarpToItem',
 'CmdOpenRadialMenu': 'UI/Commands/CmdOpenRadialMenu',
 'CmdOpenBroadcastRadialMenu': 'UI/Commands/CmdOpenBroadcastRadialMenu',
 'CmdRefreshDirectionalScan': 'UI/Commands/CmdRefreshDirectionalScan',
 'CmdToggleAutoTracking': 'UI/Commands/CmdToggleAutoTracking',
 'WinCmdToggleWindowed': 'UI/Commands/WinCmdToggleWindowed',
 'CmdSetCameraPOV': 'UI/Commands/CmdSetCameraPOV',
 'CmdSetCameraOrbit': 'UI/Commands/CmdSetCameraOrbit',
 'CmdSetCameraTactical': 'UI/Commands/CmdSetCameraTactical',
 'CmdTagItem_1': 'UI/Commands/CmdTagItem_1',
 'CmdTagItem_2': 'UI/Commands/CmdTagItem_2',
 'CmdTagItem_3': 'UI/Commands/CmdTagItem_3',
 'CmdTagItem_A': 'UI/Commands/CmdTagItem_A',
 'CmdTagItem_B': 'UI/Commands/CmdTagItem_B',
 'CmdTagItem_C': 'UI/Commands/CmdTagItem_C',
 'CmdTagItem_X': 'UI/Commands/CmdTagItem_X',
 'CmdTagItem_Y': 'UI/Commands/CmdTagItem_Y',
 'CmdTagItem_Z': 'UI/Commands/CmdTagItem_Z',
 'CmdTagItem_None': 'UI/Commands/CmdTagItem_None',
 'CmdTagItem_123': 'UI/Commands/CmdTagItem_123',
 'CmdTagItem_ABC': 'UI/Commands/CmdTagItem_ABC',
 'CmdTagItem_XYZ': 'UI/Commands/CmdTagItem_XYZ',
 'CmdTagItem_123456789': 'UI/Commands/CmdTagItem_123456789',
 'CmdTagItem_ABCDEFGHI': 'UI/Commands/CmdTagItem_ABCDEFGHI',
 'CmdToggleSensorOverlay': 'UI/Commands/CmdToggleSensorOverlay',
 'CmdCreateBookmark': 'UI/Inflight/BookmarkLocation',
 'ToggleAurumStore': 'UI/Commands/OpenStore',
 'ToggleRedeemItems': 'UI/Commands/RedeemItems',
 'ToggleActivities': 'UI/Commands/Activities',
 'CmdFlightControlsUp': 'UI/Commands/CmdFlightControlsUp',
 'CmdFlightControlsDown': 'UI/Commands/CmdFlightControlsDown',
 'CmdFlightControlsLeft': 'UI/Commands/CmdFlightControlsLeft',
 'CmdFlightControlsRight': 'UI/Commands/CmdFlightControlsRight',
 'CmdToggleSystemMenu': 'UI/Commands/CmdToggleSystemMenu',
 'CmdSetDefenceStance': 'UI/Commands/CmdSetDefenceStance',
 'CmdSetSniperStance': 'UI/Commands/CmdSetSniperStance',
 'CmdSetSpeedStance': 'UI/Commands/CmdSetSpeedStance',
 'CmdToggleProjectDiscovery': 'UI/Commands/CmdToggleProjectDiscovery',
 'CmdRefreshProbeScan': 'UI/Commands/CmdRefreshProbeScan',
 'CmdLaunchAllFighters': 'UI/Fighters/ShortcutLaunchAllFighters',
 'CmdRecallAllFightersToTubes': 'UI/Fighters/ShortcutRecallAllFighter',
 'CmdLaunchSelectedFighters': 'UI/Fighters/ShortcutLaunchSelectedFighter',
 'CmdRecallSelectedFightersToTubes': 'UI/Fighters/ShortcutRecallSelectedFighters',
 'CmdSelectAllFighters': 'UI/Fighters/ShortcutSelectAllFighter',
 'CmdDeselectAllFighters': 'UI/Fighters/ShortcutDeselectAllFighter',
 'CmdToggleShipSelection': 'UI/Fighters/ShortcutToggleShipSelection',
 'CmdToggleTubeSelection_0': 'UI/Fighters/ShortcutToggleTube1Selection',
 'CmdToggleTubeSelection_1': 'UI/Fighters/ShortcutToggleTube2Selection',
 'CmdToggleTubeSelection_2': 'UI/Fighters/ShortcutToggleTube3Selection',
 'CmdToggleTubeSelection_3': 'UI/Fighters/ShortcutToggleTube4Selection',
 'CmdToggleTubeSelection_4': 'UI/Fighters/ShortcutToggleTube5Selection',
 'CmdToggle3DView': 'UI/Commands/CmdToggle3DView'}
CATEGORIES = {'window': 'UI/SystemMenu/Shortcuts/WindowTab',
 'combat': 'UI/SystemMenu/Shortcuts/CombatTab',
 'general': 'UI/SystemMenu/Shortcuts/GeneralTab',
 'navigation': 'UI/SystemMenu/Shortcuts/NavigationTab',
 'modules': 'UI/SystemMenu/Shortcuts/ModulesTab',
 'drones': 'UI/SystemMenu/Shortcuts/DronesTab',
 'fighters': 'UI/Common/Fighters',
 'charactercreator': 'UI/CharacterCreation',
 'movement': 'UI/SystemMenu/Shortcuts/CharacterMovementTab'}
RULE_NOT_ALLOWED_WITH_MODIFIERS = 'notAllowedWithModifiers'

class EveCommandService(CommandService):
    __guid__ = 'svc.eveCmd'
    __displayname__ = 'Command service'
    __replaceservice__ = 'cmd'
    __notifyevents__ = ['OnSessionChanged', 'OnGlobalConfigChanged', 'OnApplicationFocusChanged']
    __categoryToContext__ = {'general': (contextFiS, contextIncarna),
     'window': (contextFiS, contextIncarna),
     'combat': (contextFiS,),
     'drones': (contextFiS,),
     'fighters': (contextFiS,),
     'modules': (contextFiS,),
     'navigation': (contextFiS,),
     'movement': (contextIncarna,),
     'charactercreator': (contextIncarna,)}
    __dependencies__ = CommandService.__dependencies__ + ['menu', 'machoNet']
    __startupdependencies__ = CommandService.__startupdependencies__ + ['command_blocker']
    extraShortcutRules = {'CmdOpenBroadcastRadialMenu': {RULE_NOT_ALLOWED_WITH_MODIFIERS: (uiconst.VK_MBUTTON, uiconst.VK_XBUTTON1, uiconst.VK_XBUTTON2)}}

    def Run(self, memStream = None):
        CommandService.Run(self, memStream)
        self.combatFunctionLoaded = None
        self.combatCmdLoaded = None
        self.combatCmdCurrentHasExecuted = False
        self.combatCmdUnloadFunc = None
        self.contextToCommand = {}
        self.disabledCommands = set()
        self.labelsByFuncName.update(labelsByFuncName)
        self._telemetrySessionActive = False
        self.isCmdQuitPending = False
        self.commandMemory = {}
        self.openingWndsAutomatically = False
        self.SetSpeedFractionThrottled = CallCombiner(self.SetSpeedFraction, 0.3)
        self.check_store_url_flag = create_string_flag_check(appConst.STORE_URL_FLAG, appConst.STORE_URL_FALLBACK)
        self.check_secure_url_flag = create_string_flag_check(appConst.SECURE_URL_FLAG, appConst.SECURE_URL_FALLBACK)

    def Reload(self, forceGenericOnly = False):
        CommandService.Reload(self, forceGenericOnly)
        self.contextToCommand = {}
        self.LoadAllAccelerators()
        self.commandMemory = {}

    def OnSessionChanged(self, isRemote, sess, change):
        CommandService.OnSessionChanged(self, isRemote, sess, change)
        if 'locationid' in change:
            self.LoadAllAccelerators()

    def OnGlobalConfigChanged(self, config):
        self.Reload()

    def LoadAllAccelerators(self):
        self.commandMap.UnloadAllAccelerators()
        self.commandMap.LoadAcceleratorsByCategory('general')
        self.commandMap.LoadAcceleratorsByCategory('window')
        if getattr(session, 'locationid', None):
            if idCheckers.IsStation(session.locationid):
                self.commandMap.LoadAcceleratorsByCategory('movement')
            else:
                self.commandMap.LoadAcceleratorsByCategory('combat')
                self.commandMap.LoadAcceleratorsByCategory('drones')
                self.commandMap.LoadAcceleratorsByCategory('fighters')
                self.commandMap.LoadAcceleratorsByCategory('modules')
                self.commandMap.LoadAcceleratorsByCategory('navigation')

    def OnApplicationFocusChanged(self, hasFocus):
        if hasFocus:
            uthread.new(self._CheckLoadCombatCommand)

    def _CheckLoadCombatCommand(self):
        if getattr(session, 'locationid', None) and idCheckers.IsSolarSystem(session.locationid):
            cmds = self.commandMap.GetAllCommands()
            combatCmds = [ cmd for cmd in cmds if cmd.category == 'combat' ]
            for cmd in combatCmds:
                allPressed = True
                if not cmd.shortcut:
                    continue
                for key in cmd.shortcut:
                    if not uicore.uilib.Key(key):
                        allPressed = False

                if allPressed:
                    cmd.callback()
                    return

    def GetExtraShortcutRulesForCmd(self, cmdName):
        return self.extraShortcutRules.get(cmdName, None)

    def GetCategoryContext(self, category):
        return self.__categoryToContext__[category]

    def CheckContextIntersection(self, context1, context2):
        for context in context1:
            if context in context2:
                return True

        return False

    def CheckDuplicateShortcuts(self):
        for cmd in self.defaultShortcutMapping:
            for cmdCheck in self.defaultShortcutMapping:
                if cmdCheck.shortcut:
                    sameName = cmdCheck.name == cmd.name
                    sameShortcut = cmdCheck.shortcut == cmd.shortcut
                    cmdCheckContext = self.__categoryToContext__[cmdCheck.category]
                    cmdContext = self.__categoryToContext__[cmd.category]
                    sameContext = self.CheckContextIntersection(cmdCheckContext, cmdContext)
                    if sameShortcut and sameContext and not sameName:
                        self.LogError('Same default shortcut used for multiple commands:', cmd)

    def SetDefaultShortcutMappingGAME(self):
        ret = []
        c = command.CommandMapping
        CTRL = uiconst.VK_CONTROL
        ALT = uiconst.VK_MENU
        SHIFT = uiconst.VK_SHIFT
        COMMAND = uiconst.VK_LWIN

        def k(win, mac):
            if sys.platform.startswith('darwin'):
                return mac
            return win

        m = [c(self.CmdOverloadLowPowerRack, (CTRL, uiconst.VK_1)),
         c(self.CmdOverloadMediumPowerRack, (CTRL, uiconst.VK_2)),
         c(self.CmdOverloadHighPowerRack, (CTRL, uiconst.VK_3)),
         c(self.CmdReloadAmmo, (CTRL, uiconst.VK_R))]
        for i in xrange(1, 9):
            key = getattr(uiconst, 'VK_F%s' % i)
            m.extend([c(getattr(self, 'CmdActivateHighPowerSlot%s' % i), key),
             c(getattr(self, 'CmdActivateMediumPowerSlot%s' % i), (ALT, key)),
             c(getattr(self, 'CmdActivateLowPowerSlot%s' % i), (k(win=CTRL, mac=COMMAND), key)),
             c(getattr(self, 'CmdOverloadHighPowerSlot%s' % i), (SHIFT, key)),
             c(getattr(self, 'CmdOverloadMediumPowerSlot%s' % i), (ALT, SHIFT, key)),
             c(getattr(self, 'CmdOverloadLowPowerSlot%s' % i), (k(win=CTRL, mac=COMMAND), SHIFT, key))])

        for cm in m:
            cm.category = 'modules'
            ret.append(cm)

        m = [c(self.CmdSelectPrevTarget, k(win=(ALT, uiconst.VK_LEFT), mac=(CTRL, uiconst.VK_OEM_PERIOD))),
         c(self.CmdSelectNextTarget, k(win=(ALT, uiconst.VK_RIGHT), mac=(CTRL, uiconst.VK_OEM_COMMA))),
         c(self.CmdToggleAutopilot, (CTRL, uiconst.VK_S)),
         c(self.CmdToggleTacticalOverlay, (CTRL, uiconst.VK_D)),
         c(self.CmdDecelerate, uiconst.VK_SUBTRACT, repeatable=True),
         c(self.CmdAccelerate, uiconst.VK_ADD, repeatable=True),
         c(self.CmdStopShip, (k(win=CTRL, mac=SHIFT), uiconst.VK_SPACE)),
         c(self.CmdSetShipFullSpeed, (ALT, CTRL, uiconst.VK_SPACE)),
         c(self.CmdFlightControlsUp, uiconst.VK_UP),
         c(self.CmdFlightControlsDown, uiconst.VK_DOWN),
         c(self.CmdFlightControlsLeft, uiconst.VK_LEFT),
         c(self.CmdFlightControlsRight, uiconst.VK_RIGHT),
         c(self.CmdToggleShowAllBrackets, (ALT, uiconst.VK_Z)),
         c(self.CmdToggleShowNoBrackets, (ALT, SHIFT, uiconst.VK_Z)),
         c(self.CmdToggleShowSpecialBrackets, (ALT, SHIFT, uiconst.VK_X)),
         c(self.CmdFleetBroadcast_EnemySpotted, uiconst.VK_Z),
         c(self.CmdFleetBroadcast_NeedBackup, None),
         c(self.CmdFleetBroadcast_HealArmor, None),
         c(self.CmdFleetBroadcast_HealShield, None),
         c(self.CmdFleetBroadcast_HealCapacitor, None),
         c(self.CmdFleetBroadcast_InPosition, None),
         c(self.CmdFleetBroadcast_HoldPosition, None),
         c(self.CmdFleetBroadcast_JumpBeacon, None),
         c(self.CmdFleetBroadcast_Location, None),
         c(self.CmdSendBroadcast_Target, uiconst.VK_X),
         c(self.CmdSendBroadcast_HealTarget, None),
         c(self.CmdSendBroadcast_WarpToItemID, None),
         c(self.CmdSendBroadcast_AlignToItemID, None),
         c(self.CmdSendBroadcast_JumpToItemID, None),
         c(self.CmdCycleFleetBroadcastScope, None),
         c(self.CmdSetCameraTactical, (ALT, uiconst.VK_1)),
         c(self.CmdSetCameraOrbit, (ALT, uiconst.VK_2)),
         c(self.CmdSetCameraPOV, (ALT, uiconst.VK_3)),
         c(self.CmdToggleSensorOverlay, (CTRL, uiconst.VK_O)),
         c(self.CmdCreateBookmark, (CTRL, uiconst.VK_B)),
         c(self.CmdFleetGroup, None),
         c(self.CmdClearFleetBroadcastIcons, None)]
        if evespacemouse.IsEnabled():
            m += [c(self.CmdIncreaseSpaceMouseSpeed, None, repeatable=True),
             c(self.CmdDecreaseSpaceMouseSpeed, None, repeatable=True),
             c(self.CmdIncreaseSpaceMouseAcceleration, None, repeatable=True),
             c(self.CmdDecreaseSpaceMouseAcceleration, None, repeatable=True)]
        for cm in m:
            cm.category = 'navigation'
            ret.append(cm)

        m = [c(self.CmdDronesEngage, (uiconst.VK_F,)),
         c(self.CmdDronesReturnAndOrbit, (SHIFT, ALT, uiconst.VK_R)),
         c(self.CmdDronesReturnToBay, (SHIFT, uiconst.VK_R)),
         c(self.CmdReconnectToDrones, None),
         c(self.CmdToggleAggressivePassive, None),
         c(self.CmdToggleDroneFocusFire, None),
         c(self.CmdLaunchFavoriteDrones, (SHIFT, uiconst.VK_F))]
        for cm in m:
            cm.category = 'drones'
            ret.append(cm)

        m = [c(self.CmdLaunchAllFighters, None),
         c(self.CmdRecallAllFightersToTubes, None),
         c(self.CmdLaunchSelectedFighters, None),
         c(self.CmdRecallSelectedFightersToTubes, None),
         c(self.CmdSelectAllFighters, None),
         c(self.CmdDeselectAllFighters, None),
         c(self.CmdToggleShipSelection, None),
         c(self.CmdToggleTubeSelection_0, None),
         c(self.CmdToggleTubeSelection_1, None),
         c(self.CmdToggleTubeSelection_2, None),
         c(self.CmdToggleTubeSelection_3, None),
         c(self.CmdToggleTubeSelection_4, None)]
        for cm in m:
            cm.category = 'fighters'
            ret.append(cm)

        m = [c(self.CmdPrevStackedWindow, (CTRL, SHIFT, uiconst.VK_PRIOR)),
         c(self.CmdNextStackedWindow, (CTRL, SHIFT, uiconst.VK_NEXT)),
         c(self.CmdPrevTab, (CTRL, uiconst.VK_PRIOR)),
         c(self.CmdNextTab, (CTRL, uiconst.VK_NEXT)),
         c(self.CmdExitStation, None),
         c(self.CmdEnterHangar, None),
         c(self.CmdEnterStructure, None),
         c(self.CmdHideUI, (CTRL, uiconst.VK_F9)),
         c(self.CmdHideCursor, (ALT, uiconst.VK_F9)),
         c(self.CmdToggle3DView, (CTRL, SHIFT, uiconst.VK_F9)),
         c(self.CmdToggleEffects, (CTRL,
          ALT,
          SHIFT,
          uiconst.VK_E)),
         c(self.CmdToggleEffectTurrets, (CTRL,
          ALT,
          SHIFT,
          uiconst.VK_T)),
         c(self.CmdOpenRadialMenu, None, hintPath='UI/SystemMenu/Shortcuts/RadialMenuHint'),
         c(self.CmdOpenBroadcastRadialMenu, None, hintPath='UI/SystemMenu/Shortcuts/BroadcastRadialMenuHint'),
         c(self.CmdZoomIn, (CTRL, SHIFT, uiconst.VK_A), repeatable=True),
         c(self.CmdZoomOut, (CTRL, SHIFT, uiconst.VK_Z), repeatable=True),
         c(self.CmdToggleSystemMenu, None, enabled=False),
         c(self.CmdSetSearchBarFocus, (SHIFT, uiconst.VK_S))]
        ret.extend(m)
        if bool(session.role & ROLE_CONTENT):
            ret.append(c(self.OpenDungeonEditor, (CTRL, SHIFT, uiconst.VK_D)))
        if bool(session.role & ROLEMASK_ELEVATEDPLAYER):
            ret.append(c(self.CmdToggleCombatView, (CTRL, ALT, uiconst.VK_T)))
        m = [c(self.CmdToggleTargetItem, None),
         c(self.CmdLockTargetItem, CTRL),
         c(self.CmdSelectTargetItem, SHIFT),
         c(self.CmdUnlockTargetItem, (CTRL, SHIFT)),
         c(self.CmdUnlockTargetItems, None),
         c(self.CmdToggleLookAtItem, ALT),
         c(self.CmdToggleCameraTracking, uiconst.VK_C),
         c(self.CmdApproachItem, uiconst.VK_Q),
         c(self.CmdAlignToItem, uiconst.VK_A),
         c(self.CmdOrbitItem, uiconst.VK_W),
         c(self.CmdKeepItemAtRange, uiconst.VK_E),
         c(self.CmdShowItemInfo, uiconst.VK_T),
         c(self.CmdDockOrJumpOrActivateGate, uiconst.VK_D),
         c(self.CmdWarpToItem, uiconst.VK_S),
         c(self.MakeCmdTagItem('1'), uiconst.VK_1),
         c(self.MakeCmdTagItem('2'), uiconst.VK_2),
         c(self.MakeCmdTagItem('3'), uiconst.VK_3),
         c(self.MakeCmdTagItem('A'), uiconst.VK_4),
         c(self.MakeCmdTagItem('B'), uiconst.VK_5),
         c(self.MakeCmdTagItem('C'), uiconst.VK_6),
         c(self.MakeCmdTagItem('X'), None),
         c(self.MakeCmdTagItem('Y'), None),
         c(self.MakeCmdTagItem('Z'), None),
         c(self.MakeCmdTagItem(None), None),
         c(self.MakeCmdTagItemFromSequence(['1', '2', '3']), uiconst.VK_7),
         c(self.MakeCmdTagItemFromSequence(['A', 'B', 'C']), uiconst.VK_8),
         c(self.MakeCmdTagItemFromSequence(['X', 'Y', 'Z']), uiconst.VK_9),
         c(self.MakeCmdTagItemFromSequence(['1',
          '2',
          '3',
          '4',
          '5',
          '6',
          '7',
          '8',
          '9']), None),
         c(self.MakeCmdTagItemFromSequence(['A',
          'B',
          'C',
          'D',
          'E',
          'F',
          'G',
          'H',
          'I']), None),
         c(self.CmdSetDefenceStance, (SHIFT, uiconst.VK_1)),
         c(self.CmdSetSniperStance, (SHIFT, uiconst.VK_2)),
         c(self.CmdSetSpeedStance, (SHIFT, uiconst.VK_3)),
         c(self.CmdIncreaseProbeScanRange, None),
         c(self.CmdDecreaseProbeScanRange, None),
         c(self.CmdRefreshProbeScan, uiconst.VK_B),
         c(self.CmdRefreshDirectionalScan, uiconst.VK_V),
         c(self.CmdToggleAutoTracking, (SHIFT, uiconst.VK_C)),
         c(self.CmdGetLocationMenuForNavigation, None)]
        for cm in m:
            cm.category = 'combat'
            ret.append(cm)

        m = [c(self.CmdOpenNewMessage, None),
         c(self.CmdSetChatChannelFocus, uiconst.VK_SPACE),
         c(self.CmdSetOverviewFocus, (ALT, uiconst.VK_SPACE)),
         c(self.CmdToggleMap, uiconst.VK_F10),
         c(self.CmdToggleSolarSystemMap, uiconst.VK_F9),
         c(self.CmdToggleShipTree, None),
         c(self.OpenAssets, (ALT, uiconst.VK_T)),
         c(self.OpenCalculator, None),
         c(self.OpenCalendar, None),
         c(self.OpenCapitalNavigation, None),
         c(self.OpenCargoHoldOfActiveShip, None),
         c(self.OpenGeneralMiningHoldOfActiveShip, None),
         c(self.OpenMineralHoldOfActiveShip, None),
         c(self.OpenPlanetaryCommoditiesHoldOfActiveShip, None),
         c(self.OpenFuelBayOfActiveShip, None),
         c(self.OpenFwEnlistment, None),
         c(self.OpenInsurgencyDashboard, None),
         c(self.OpenRelevantFWWindow, None),
         c(self.OpenAmmoHoldOfActiveShip, None),
         c(self.OpenFleetHangarOfActiveShip, None),
         c(self.OpenShipMaintenanceOfBayActiveShip, None),
         c(self.OpenChannels, None),
         c(self.OpenCharactersheet, (ALT, uiconst.VK_A)),
         c(self.OpenConfigMenu, None),
         c(self.OpenContracts, None),
         c(self.OpenCorpDeliveries, None),
         c(self.OpenCorpHangar, None),
         c(self.OpenCorporationPanel, None),
         c(self.OpenDroneBayOfActiveShip, None),
         c(self.OpenFighterBayOfActiveShip, None),
         c(self.OpenIndustry, (ALT, uiconst.VK_S)),
         c(self.OpenFitting, (ALT, uiconst.VK_F)),
         c(self.OpenFleet, None),
         c(self.OpenFpsMonitor, (CTRL, uiconst.VK_F)),
         c(self.OpenHangarFloor, (ALT, uiconst.VK_G)),
         c(self.OpenPlexVault, None),
         c(self.OpenHelp, uiconst.VK_F12),
         c(self.OpenInsurance, None),
         c(self.OpenAgencyNew, (ALT, uiconst.VK_M)),
         c(self.OpenLoginRewardWindow, None),
         c(self.OpenLog, None),
         c(self.OpenLpstore, None),
         c(self.OpenMail, (ALT, uiconst.VK_I)),
         c(self.OpenMapBrowser, k(win=uiconst.VK_F11, mac=(ALT, uiconst.VK_B))),
         c(self.OpenMarket, (ALT, uiconst.VK_R)),
         c(self.OpenMarketOrders, None),
         c(self.OpenMultibuy, None),
         c(self.OpenMedical, None),
         c(self.OpenMilitia, None),
         c(self.OpenMoonMining, None),
         c(self.OpenNotepad, None),
         c(self.OpenOverviewSettings, None),
         c(self.OpenPeopleAndPlaces, (ALT, uiconst.VK_E)),
         c(self.OpenCharacterCustomization, None),
         c(self.OpenRepairshop, None),
         c(self.OpenReprocessingPlant, None),
         c(self.ToggleProbeScanner, (ALT, uiconst.VK_P)),
         c(self.OpenDirectionalScanner, (ALT, uiconst.VK_D)),
         c(self.OpenMoonScan, None),
         c(self.OpenSecurityOffice, None),
         c(self.OpenShipConfig, None),
         c(self.OpenShipHangar, (ALT, uiconst.VK_N)),
         c(self.OpenInventory, (ALT, uiconst.VK_C)),
         c(self.OpenSkillsWindow, (ALT, uiconst.VK_X)),
         c(self.OpenWallet, (ALT, uiconst.VK_W)),
         c(self.CmdForceFadeFromBlack, (SHIFT, uiconst.VK_BACK)),
         c(self.OpenCompare, None),
         c(self.OpenEveMenu, uiconst.VK_OEM_5),
         c(self.OpenFittingMgmt, None),
         c(self.ToggleAurumStore, (ALT, uiconst.VK_4)),
         c(self.ToggleRedeemItems, (ALT, uiconst.VK_Y)),
         c(self.OpenPlanets, None),
         c(self.OpenMyMercenaryDens, None),
         c(self.OpenStructureBrowser, None),
         c(self.OpenAccessGroupsWindow, None),
         c(self.OpenLedger, None),
         c(self.OpenSeason, None),
         c(self.OpenContextualOffersWindow, None),
         c(self.OpenPVPFilamentEventWindow, None),
         c(self.CmdGetUiPointer, None),
         c(self.OpenCombatAnomaliesInAgency, None),
         c(self.OpenEncounterSurveillanceSystemInAgency, None),
         c(self.CmdToggleAirCareerProgram, None),
         c(self.OpenFrigateEscapeBay, None),
         c(self.OpenManageRoute, None),
         c(self.OpenFleetWatchlist, None),
         c(self.OpenPaintToolWindow, None),
         c(self.OpenShipSKINRWindow, None)]
        m.append(c(self.OpenLocations, uiconst.VK_L))
        m.append(c(self.ToggleCurrentSystemLocationWnd, None))
        if sm.GetService('raffleSvc').is_available:
            m.append(c(self.OpenRaffleWindow, None))
        if is_job_board_available():
            m.append(c(self.OpenJobBoardWindow, (ALT, uiconst.VK_J)))
            if not are_missions_in_job_board_available():
                m.append(c(self.OpenJournal, (ALT, None)))
        else:
            m.append(c(self.OpenJournal, (ALT, uiconst.VK_J)))
        if ArePointerLinksActive(sm.GetService('machoNet')):
            m += [c(self.OpenPointerWnd, None)]
        if not IsPlayerBountyHidden(sm.GetService('machoNet')):
            m.append(c(self.OpenBountyOffice, None))
        if not AmOnChineseServer():
            m.append(c(self.ToggleProjectDiscovery, None))
        if bool(session.role & ROLE_PROGRAMMER):
            m.append(c(self.OpenUIDebugger, None))
            m.append(c(self.ToggleTelemetryRecord, None))
            m.append(c(self.ToggleUILinearColor, None))
            m.append(c(self.ToggleGammaCorrectText, None))
            m.append(c(self.OpenSkillTreeWindow, None))
        if localization.util.AmOnChineseServer():
            m.append(c(self.ToggleActivities, None))
        for cm in m:
            cm.category = 'window'
            ret.append(cm)

        m = [c(self.CmdPickPortrait0, uiconst.VK_F1),
         c(self.CmdPickPortrait1, uiconst.VK_F2),
         c(self.CmdPickPortrait2, uiconst.VK_F3),
         c(self.CmdPickPortrait3, uiconst.VK_F4)]
        for cm in m:
            cm.category = 'charactercreator'
            ret.append(cm)

        return ret

    def CmdActivateHighPowerSlot1(self, *args):
        self._cmdshipui(0, 0)

    def CmdActivateHighPowerSlot2(self, *args):
        self._cmdshipui(1, 0)

    def CmdActivateHighPowerSlot3(self, *args):
        self._cmdshipui(2, 0)

    def CmdActivateHighPowerSlot4(self, *args):
        self._cmdshipui(3, 0)

    def CmdActivateHighPowerSlot5(self, *args):
        self._cmdshipui(4, 0)

    def CmdActivateHighPowerSlot6(self, *args):
        self._cmdshipui(5, 0)

    def CmdActivateHighPowerSlot7(self, *args):
        self._cmdshipui(6, 0)

    def CmdActivateHighPowerSlot8(self, *args):
        self._cmdshipui(7, 0)

    def CmdActivateMediumPowerSlot1(self, *args):
        self._cmdshipui(0, 1)

    def CmdActivateMediumPowerSlot2(self, *args):
        self._cmdshipui(1, 1)

    def CmdActivateMediumPowerSlot3(self, *args):
        self._cmdshipui(2, 1)

    def CmdActivateMediumPowerSlot4(self, *args):
        self._cmdshipui(3, 1)

    def CmdActivateMediumPowerSlot5(self, *args):
        self._cmdshipui(4, 1)

    def CmdActivateMediumPowerSlot6(self, *args):
        self._cmdshipui(5, 1)

    def CmdActivateMediumPowerSlot7(self, *args):
        self._cmdshipui(6, 1)

    def CmdActivateMediumPowerSlot8(self, *args):
        self._cmdshipui(7, 1)

    def CmdActivateLowPowerSlot1(self, *args):
        self._cmdshipui(0, 2)

    def CmdActivateLowPowerSlot2(self, *args):
        self._cmdshipui(1, 2)

    def CmdActivateLowPowerSlot3(self, *args):
        self._cmdshipui(2, 2)

    def CmdActivateLowPowerSlot4(self, *args):
        self._cmdshipui(3, 2)

    def CmdActivateLowPowerSlot5(self, *args):
        self._cmdshipui(4, 2)

    def CmdActivateLowPowerSlot6(self, *args):
        self._cmdshipui(5, 2)

    def CmdActivateLowPowerSlot7(self, *args):
        self._cmdshipui(6, 2)

    def CmdActivateLowPowerSlot8(self, *args):
        self._cmdshipui(7, 2)

    def CmdOverloadHighPowerSlot1(self, *args):
        self._cmdoverload(0, 0)

    def CmdOverloadHighPowerSlot2(self, *args):
        self._cmdoverload(1, 0)

    def CmdOverloadHighPowerSlot3(self, *args):
        self._cmdoverload(2, 0)

    def CmdOverloadHighPowerSlot4(self, *args):
        self._cmdoverload(3, 0)

    def CmdOverloadHighPowerSlot5(self, *args):
        self._cmdoverload(4, 0)

    def CmdOverloadHighPowerSlot6(self, *args):
        self._cmdoverload(5, 0)

    def CmdOverloadHighPowerSlot7(self, *args):
        self._cmdoverload(6, 0)

    def CmdOverloadHighPowerSlot8(self, *args):
        self._cmdoverload(7, 0)

    def CmdOverloadMediumPowerSlot1(self, *args):
        self._cmdoverload(0, 1)

    def CmdOverloadMediumPowerSlot2(self, *args):
        self._cmdoverload(1, 1)

    def CmdOverloadMediumPowerSlot3(self, *args):
        self._cmdoverload(2, 1)

    def CmdOverloadMediumPowerSlot4(self, *args):
        self._cmdoverload(3, 1)

    def CmdOverloadMediumPowerSlot5(self, *args):
        self._cmdoverload(4, 1)

    def CmdOverloadMediumPowerSlot6(self, *args):
        self._cmdoverload(5, 1)

    def CmdOverloadMediumPowerSlot7(self, *args):
        self._cmdoverload(6, 1)

    def CmdOverloadMediumPowerSlot8(self, *args):
        self._cmdoverload(7, 1)

    def CmdOverloadLowPowerSlot1(self, *args):
        self._cmdoverload(0, 2)

    def CmdOverloadLowPowerSlot2(self, *args):
        self._cmdoverload(1, 2)

    def CmdOverloadLowPowerSlot3(self, *args):
        self._cmdoverload(2, 2)

    def CmdOverloadLowPowerSlot4(self, *args):
        self._cmdoverload(3, 2)

    def CmdOverloadLowPowerSlot5(self, *args):
        self._cmdoverload(4, 2)

    def CmdOverloadLowPowerSlot6(self, *args):
        self._cmdoverload(5, 2)

    def CmdOverloadLowPowerSlot7(self, *args):
        self._cmdoverload(6, 2)

    def CmdOverloadLowPowerSlot8(self, *args):
        self._cmdoverload(7, 2)

    def CmdOverloadHighPowerRack(self, *args):
        self._cmdoverloadrack('Hi')

    def CmdOverloadMediumPowerRack(self, *args):
        self._cmdoverloadrack('Med')

    def CmdOverloadLowPowerRack(self, *args):
        self._cmdoverloadrack('Lo')

    def CmdSelectPrevTarget(self, *args):
        sm.GetService('target').SelectPrevTarget()
        self.CmdSetOverviewFocus()

    def CmdSelectNextTarget(self, *args):
        sm.GetService('target').SelectNextTarget()
        self.CmdSetOverviewFocus()

    def CmdZoomIn(self, *args):
        self._Zoom(direction=-1)

    CmdZoomIn.nameLabelPath = 'UI/Inflight/ZoomIn'

    def CmdZoomOut(self, *args):
        self._Zoom(direction=1)

    CmdZoomOut.nameLabelPath = 'UI/Inflight/ZoomOut'

    def _Zoom(self, direction):
        viewSvc = sm.GetService('viewState')
        simulatedMouseScroll = direction * 120
        activeWindow = uicore.registry.GetActiveStackOrWindow()
        if activeWindow and hasattr(activeWindow, 'CmdZoomInOut'):
            activeWindow.CmdZoomInOut(simulatedMouseScroll)
        elif viewSvc.IsViewActive('planet', 'starmap', 'systemmap', 'shiptree', 'inflight', 'station', 'hangar'):
            view = viewSvc.GetCurrentView()
            view.ZoomBy(simulatedMouseScroll)
        if eveCfg.InSpace():
            if simulatedMouseScroll < 0:
                sm.ScatterEvent('OnClientMouseZoomInSpace', simulatedMouseScroll)
            else:
                sm.ScatterEvent('OnClientMouseZoomOutSpace', simulatedMouseScroll)

    def CmdToggleAutopilot(self, *args):
        if eveCfg.InSpace():
            if sm.GetService('autoPilot').GetState():
                sm.GetService('autoPilot').SetOff()
            else:
                sm.GetService('autoPilot').SetOn()

    CmdToggleAutopilot.nameLabelPath = 'Tooltips/Hud/Autopilot'
    CmdToggleAutopilot.descriptionLabelPath = 'Tooltips/Hud/Autopilot_description'

    def CmdToggleTacticalOverlay(self, *args):
        if eveCfg.InSpace():
            sm.GetService('tactical').ToggleOnOff()

    CmdToggleTacticalOverlay.nameLabelPath = 'Tooltips/Hud/Tactical'
    CmdToggleTacticalOverlay.descriptionLabelPath = 'Tooltips/Hud/Tactical_description'

    def SetSpeedFraction(self, speed):
        remote = sm.GetService('michelle').GetRemotePark()
        if remote:
            remote.CmdSetSpeedFraction(speed)

    def CmdDecelerate(self, *args):
        if eveCfg.InShipInSpace():
            bp = sm.GetService('michelle').GetBallpark()
            ownBall = bp.GetBall(session.shipid)
            if ownBall is not None:
                self.SetSpeedFractionThrottled(min(1.0, ownBall.speedFraction - 0.1))

    def CmdAccelerate(self, *args):
        if eveCfg.InShipInSpace():
            rp = sm.GetService('michelle').GetRemotePark()
            bp = sm.GetService('michelle').GetBallpark()
            ownBall = bp.GetBall(session.shipid)
            if rp is not None and ownBall is not None:
                if ownBall.mode == destiny.DSTBALL_STOP and not sm.GetService('autoPilot').GetState():
                    direction = trinity.TriVector(0.0, 0.0, 1.0)
                    currentDirection = ownBall.GetQuaternionAt(blue.os.GetSimTime())
                    direction.TransformQuaternion(currentDirection)
                    rp.CmdGotoDirection(direction.x, direction.y, direction.z)
                    GetMenuService().ClearAlignTargets()
                self.SetSpeedFractionThrottled(min(1.0, ownBall.speedFraction + 0.1))

    def CmdStopShip(self, *args):
        if eveCfg.InShipInSpace():
            autoPilot = sm.GetService('autoPilot')
            autoPilot.CancelSystemNavigation()
            if session.IsItSafe():
                bp = sm.GetService('michelle').GetRemotePark()
                if bp and session.IsItSafe():
                    bp.CmdStop()
            sm.GetService('logger').AddText(localization.GetByLabel('UI/Commands/ShipStopping'), 'notify')
            sm.GetService('space').DoSetIndicationTextForcefully(localization.GetByLabel('UI/Inflight/Messages/ShipStoppingHeader'), '')
            if autoPilot.GetState():
                autoPilot.SetOff()
            sm.ScatterEvent('OnClientEvent_StopShip')

    def CmdSetShipFullSpeed(self, *args):
        bp = sm.GetService('michelle').GetBallpark()
        rbp = sm.GetService('michelle').GetRemotePark()
        if bp is None or rbp is None:
            return
        if eveCfg.IsControllingStructure():
            return
        ownBall = bp.GetBall(session.shipid)
        if ownBall and rbp is not None and ownBall.mode == destiny.DSTBALL_STOP:
            if not sm.GetService('autoPilot').GetState():
                direction = trinity.TriVector(0.0, 0.0, 1.0)
                currentDirection = ownBall.GetQuaternionAt(blue.os.GetSimTime())
                direction.TransformQuaternion(currentDirection)
                rbp.CmdGotoDirection(direction.x, direction.y, direction.z)
                GetMenuService().ClearAlignTargets()
        if rbp is not None:
            rbp.CmdSetSpeedFraction(1.0)
            speedText = self._FormatSpeed(ownBall.maxVelocity)
            sm.GetService('logger').AddText(speedText, 'notify')
            ShowQuickMessage(speedText)

    def _FormatSpeed(self, speed):
        if speed >= 100:
            speed = long(speed)
        return localization.GetByLabel('UI/Commands/SpeedChangedTo', speed=speed)

    def CmdToggleShowAllBrackets(self, *args):
        if eveCfg.InSpace():
            bracketSettings.toggle_show_all_brackets()

    def CmdToggleShowNoBrackets(self, *args):
        if eveCfg.InSpace():
            bracketSettings.toggle_show_no_brackets()

    def CmdToggleShowSpecialBrackets(self, *args):
        if eveCfg.InSpace():
            bracketSettings.bracket_showing_specials_setting.toggle()

    def CmdReloadAmmo(self, *args):
        if uicore.layer.shipui.isopen:
            uicore.layer.shipui.OnReloadAmmo()

    def _cmdshipui(self, sidx, gidx):
        if uicore.layer.shipui.isopen:
            uicore.layer.shipui.OnF(sidx, gidx)

    def _cmdoverload(self, sidx, gidx):
        if uicore.layer.shipui.isopen:
            uicore.layer.shipui.OnFKeyOverload(sidx, gidx)

    def _cmdoverloadrack(self, what):
        if uicore.layer.shipui.isopen:
            uicore.layer.shipui.ToggleRackOverload(what)

    def CmdQuitGame(self, *args):
        if self.isCmdQuitPending:
            return
        self.isCmdQuitPending = True
        try:
            if sm.GetService('gameui').HasDisconnectionNotice() or uicore.Message('AskQuitGame', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                self.DoQuitGame()
        finally:
            self.isCmdQuitPending = False

    CmdQuitGame.nameLabelPath = 'UI/Commands/CmdQuitGame'

    def DoQuitGame(self):
        try:
            check_for_character_creation_exit()
            if session.charid:
                sm.GetService('skillqueue').OnCloseApp()
            self.settings.SaveSettings()
            sm.GetService('clientStatsSvc').OnProcessExit()
        except:
            self.LogException()
        finally:
            bluepy.Terminate(0, 'User requesting close')

    def _CheckLogoffApplicable(self):
        viewStateSvc = sm.GetService('viewState')
        if eveCfg.IsControllingStructure():
            raise UserError('CannotWhileControllingStructure')
        if viewStateSvc.IsViewActive('planet'):
            currentPlanet = sm.GetService('planetUI').GetCurrentPlanet()
            if currentPlanet and currentPlanet.IsInEditMode():
                raise UserError('CannotWhileEditingPlanetaryProduction')
        return True

    def CmdLogOff(self, *args):
        check_for_character_creation_exit()
        if AllowCharacterLogoff(sm.GetService('machoNet')):
            viewStateSvc = sm.GetService('viewState')
            if viewStateSvc.HasActiveTransition():
                self.LogWarn("Denying logoff attempt as we're currently transitioning between viewStates.")
                return False
            if session.charid:
                if not self._CheckLogoffApplicable():
                    return
                if viewStateSvc.GetCurrentViewInfo().IsSecondary():
                    viewStateSvc.CloseSecondaryView()
                if SessionChecker(session, sm).IsPilotInShipInSpace():
                    ShipTreeDockablePanel.CloseIfOpen()
                    self.LogNotice('Initiating safe logoff for character %s' % cfg.eveowners.Get(session.charid).name)
                    GetMenuService().SafeLogoff()
                else:
                    if not (viewStateSvc.IsViewActive('hangar') or viewStateSvc.IsViewActive('structure')):
                        self.LogWarn('Cannot logoff with view %s active' % viewStateSvc.GetCurrentView())
                        return False
                    if uicore.Message('AskLogoffToCharacterSelection', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                        sm.GetService('gameui').LogOffCharacter()
        else:
            modalWnd = uicore.registry.GetModalWindow()
            if modalWnd and modalWnd.__guid__ == 'form.MessageBox':
                return
            if uicore.Message('AskLogoffGame', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                check_for_character_creation_exit()
                self.settings.SaveSettings()
                appUtils.Reboot('Generic Logoff')

    CmdLogOff.nameLabelPath = 'UI/Commands/CmdLogOff'
    CmdLogOff.descriptionFunc = GetCmdLogoffHint

    def CmdDronesEngage(self, *args):
        drones = sm.GetService('michelle').GetDrones()
        if drones is None:
            return
        entity = eveMoniker.GetEntityAccess()
        if not entity:
            return
        droneItemIDsAndTypeIDs = [ (droneID, drone.typeID) for droneID, drone in drones.iteritems() ]
        droneFunctions.PerformPrimaryAction(droneItemIDsAndTypeIDs)

    CmdDronesEngage.nameLabelPath = 'UI/Commands/CmdDronesEngage'

    def CmdDronesReturnAndOrbit(self, *args):
        drones = sm.GetService('michelle').GetDrones()
        if drones:
            droneIDs = drones.keys()
            targetID = sm.GetService('target').GetActiveTargetID()
            entity = eveMoniker.GetEntityAccess()
            if entity:
                ret = entity.CmdReturnHome(droneIDs)
                GetMenuService().HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')
                if droneIDs and targetID:
                    eve.Message('Command', {'command': localization.GetByLabel('UI/Commands/DronesReturningAndOrbiting')})
        sm.GetService('fighters').RecallAllFightersAndOrbit()

    CmdDronesReturnAndOrbit.nameLabelPath = 'UI/Commands/CmdDronesReturnAndOrbit'

    def CmdDronesReturnToBay(self, *args):
        drones = sm.GetService('michelle').GetDrones()
        if drones:
            droneIDs = drones.keys()
            targetID = sm.GetService('target').GetActiveTargetID()
            entity = eveMoniker.GetEntityAccess()
            if entity:
                ret = entity.CmdReturnBay(droneIDs)
                GetMenuService().HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')
                if droneIDs and targetID:
                    eve.Message('Command', {'command': localization.GetByLabel('UI/Commands/DronesReturningToDroneBay')})
        self.CmdRecallAllFightersToTubes()

    CmdDronesReturnToBay.nameLabelPath = 'UI/Commands/CmdDronesReturnToBay'

    def _GetDronesToLaunch(self):
        favoriteDroneIDsPresent = GetDroneGroupsController().GetFavoriteGroupDroneIDsInBayOrSpace()
        if favoriteDroneIDsPresent:
            return [ x for x in GetDronesInBay() if x.itemID in favoriteDroneIDsPresent ]
        return GetDronesInBay()

    def CmdLaunchFavoriteDrones(self, *args):
        if not session.shipid or sm.GetService('michelle').GetBallpark() is None:
            return
        dronesToLaunch = self._GetDronesToLaunch()
        if dronesToLaunch:
            GetMenuService().LaunchDrones(dronesToLaunch)

    CmdLaunchFavoriteDrones.nameLabelPath = 'UI/Drones/LaunchDrones'
    CmdLaunchFavoriteDrones.descriptionLabelPath = 'UI/Drones/HintOnFavoriteIcon'

    def CmdReconnectToDrones(self, *args):
        GetMenuService().ReconnectToDrones()

    def CmdLaunchAllFighters(self, *args):
        sm.GetService('fighters').LaunchAllFighters()

    def CmdRecallAllFightersToTubes(self):
        sm.GetService('fighters').RecallAllFightersToTubes()

    def CmdToggleTubeSelection_0(self, *args):
        self._DoToggleTubeSelection(appConst.flagFighterTube0)

    def CmdToggleTubeSelection_1(self, *args):
        self._DoToggleTubeSelection(appConst.flagFighterTube1)

    def CmdToggleTubeSelection_2(self, *args):
        self._DoToggleTubeSelection(appConst.flagFighterTube2)

    def CmdToggleTubeSelection_3(self, *args):
        self._DoToggleTubeSelection(appConst.flagFighterTube3)

    def CmdToggleTubeSelection_4(self, *args):
        self._DoToggleTubeSelection(appConst.flagFighterTube4)

    def _DoToggleTubeSelection(self, tubeFlagID):
        sm.GetService('fighters').ToggleSelectionForFightersForTube(tubeFlagID)

    def CmdLaunchSelectedFighters(self):
        sm.GetService('fighters').LaunchSelectedFighters()

    def CmdRecallSelectedFightersToTubes(self):
        sm.GetService('fighters').RecallSelectedFightersToTubes()

    def CmdSelectAllFighters(self):
        sm.GetService('fighters').SelectAllFighters()

    def CmdDeselectAllFighters(self):
        sm.GetService('fighters').DeselectAllFighters()

    def CmdToggleShipSelection(self):
        if session.shipid:
            movementFunctions.ToggleSelectForNavigation(session.shipid)

    def CmdToggleAggressivePassive(self, *args):
        drones_aggressive_setting.toggle()

    def CmdToggleDroneFocusFire(self, *args):
        drones_focus_fire_setting.toggle()

    def WinCmdToggleWindowed(self, *args):
        lastTimeToggled = settings.user.ui.Get('LastTimeToggleWindowed', 0)
        if blue.os.GetWallclockTime() - lastTimeToggled > 2 * appConst.SEC:
            settings.user.ui.Set('LastTimeToggleWindowed', blue.os.GetWallclockTime())
            sm.GetService('device').ToggleWindowed()

    def CmdResetMonitor(self, *args):
        sm.GetService('device').ResetMonitor()

    def CmdToggleSolarSystemMap(self, **kwargs):
        if session.charid:
            from eve.client.script.ui.shared.mapView.mapViewUtil import ToggleSolarSystemMap
            if is_solarsystem_map_suppressed(session.solarsystemid2):
                raise UserError('CannotProbeScanInSystem')
            ToggleSolarSystemMap(**kwargs)

    CmdToggleSolarSystemMap.nameLabelPath = 'UI/Map/MapPallet/btnSolarsystemMap'
    CmdToggleSolarSystemMap.descriptionLabelPath = ''

    def CmdToggleMap(self, *args):
        if session.charid is not None and not getattr(self, 'loadingCharacterCustomization', False):
            if not classic_map_enabled_setting.is_enabled():
                self._CmdToggleMapBeta()
            else:
                uthread.new(sm.GetService('map').Toggle).context = 'svc.map.Toggle'
                sm.ScatterEvent('OnClientEvent_OpenMap')

    CmdToggleMap.nameLabelPath = 'UI/Neocom/MapBtn'
    CmdToggleMap.descriptionLabelPath = 'Tooltips/Neocom/Map_description'

    def _CmdToggleMapBeta(self, *args):
        from eve.client.script.ui.shared.mapView.mapViewPanel import MapViewPanel
        wnd = MapViewPanel.GetIfOpen()
        if not wnd:
            MapViewPanel.Open(parent=uicore.layer.main)
        elif wnd.IsMinimized():
            wnd.Maximize()
        else:
            MapViewPanel.CloseIfOpen()

    def CmdToggleShipTree(self):
        wnd = ShipTreeDockablePanel.GetIfOpen()
        if not wnd:
            if not sm.GetService('viewState').SafeLogoffInProgress():
                ShipTreeDockablePanel.Open(parent=uicore.layer.main)
        elif wnd.IsMinimized():
            wnd.Maximize()
        else:
            ShipTreeDockablePanel.CloseIfOpen()

    CmdToggleShipTree.nameLabelPath = 'UI/Neocom/ShipTreeBtn'
    CmdToggleShipTree.descriptionLabelPath = 'Tooltips/Neocom/ISIS_description'

    def CmdToggleAirCareerProgram(self, **kwargs):
        wnd = CareerPortalDockablePanel.GetIfOpen()
        if not wnd:
            CareerPortalDockablePanel.Open(parent=uicore.layer.main)
        elif wnd.IsMinimized():
            wnd.Maximize()
        else:
            CareerPortalDockablePanel.ToggleMinimize(wnd)

    CmdToggleAirCareerProgram.nameLabelPath = 'UI/CareerPortal/CareerPortalWnd'
    CmdToggleAirCareerProgram.descriptionLabelPath = 'UI/CareerPortal/CareerPortalWndDescription'

    def CmdPrevStackedWindow(self, *args):
        wnd = uicore.registry.GetActive()
        if wnd is None or not wnd.stacked:
            return
        tabGroup = wnd.stack.GetTabGroup()
        tabGroup.SelectPrev()

    def CmdNextStackedWindow(self, *args):
        wnd = uicore.registry.GetActive()
        if wnd is None or not isinstance(wnd, Window) or not wnd.stacked:
            return
        tabGroup = wnd.stack.GetTabGroup()
        tabGroup.SelectNext()

    def CmdPrevTab(self, *args):
        tabGroup = self._GetTabgroup()
        if tabGroup:
            tabGroup.SelectPrev()

    def CmdNextTab(self, *args):
        tabGroup = self._GetTabgroup()
        if tabGroup:
            tabGroup.SelectNext()

    def _GetTabgroup(self):
        wnd = uicore.registry.GetActive()
        if not wnd:
            return
        MAXRECURS = 10
        tabGroup = self._FindTabGroup(wnd.sr.maincontainer, MAXRECURS)
        if not tabGroup and wnd.stacked:
            tabGroup = wnd.stack.GetTabGroup()
        return tabGroup

    def _FindTabGroup(self, parent, maxLevel):
        if isinstance(parent, TabGroup) and not parent.destroyed:
            return parent
        if not hasattr(parent, 'children') or not parent.children or maxLevel == 0:
            return
        blue.pyos.BeNice()
        for c in parent.children:
            tabGroup = self._FindTabGroup(c, maxLevel - 1)
            if tabGroup:
                return tabGroup

    def CmdExitStation(self, *args):
        if uicore.registry.GetModalWindow():
            return
        ccLayer = uicore.layer.Get('charactercreation')
        if ccLayer and ccLayer.isopen:
            return
        if sm.GetService('viewState').HasActiveTransition():
            return
        if eveCfg.IsControllingStructure():
            return
        if session.stationid or session.structureid:
            sm.GetService('undocking').ExitDockableLocation()

    def CmdEnterHangar(self, *args):
        if session.stationid and not sm.GetService('viewState').IsViewActive('hangar'):
            change = {'stationid': (session.stationid, session.stationid)}
            uthread.pool('eveCommands::CmdEnterHangar', sm.GetService('viewState').ChangePrimaryView, 'hangar', change=change)
        elif eveCfg.IsDockedInStructure() and not sm.GetService('viewState').IsViewActive('hangar'):
            uthread.pool('eveCommands::CmdEnterHangar', sm.GetService('viewState').ChangePrimaryView, 'hangar')

    def CmdEnterStructure(self, *args):
        if eveCfg.IsDockedInStructure() and not sm.GetService('viewState').IsViewActive('structure', 'charactercreation'):
            uthread.pool('eveCommands::CmdEnterStructure', sm.GetService('viewState').ChangePrimaryView, 'structure')

    def CmdSetChatChannelFocus(self, *args):
        sm.GetService('focus').SetChannelFocus()

    def CmdSetSearchBarFocus(self, *args):
        sm.ScatterEvent('OnSetSearchBarFocus')

    def CmdSetOverviewFocus(self, *args):
        wnd = overviewWindowUtil.GetOverviewWndIfOpen()
        if wnd:
            uicore.registry.SetFocus(wnd)

    def GetWndMenu(self, *args):
        if uicore.registry.GetModalWindow() or not session.charid:
            return
        if not getattr(eve, 'chooseWndMenu', None) or eve.chooseWndMenu.destroyed or eve.chooseWndMenu.state == uiconst.UI_HIDDEN:
            ClearMenuLayer()
            CtrlTabWindow.CloseIfOpen()
            mv = CtrlTabWindow.Open()
            mv.left = (uicore.desktop.width - mv.width) / 2
            mv.top = (uicore.desktop.height - mv.height) / 2
            eve.chooseWndMenu = mv
        return eve.chooseWndMenu

    def CmdFleetBroadcast_EnemySpotted(self):
        sm.GetService('fleet').SendBroadcast_EnemySpotted()

    def CmdFleetBroadcast_NeedBackup(self):
        sm.GetService('fleet').SendBroadcast_NeedBackup()

    def CmdFleetBroadcast_HealArmor(self):
        sm.GetService('fleet').SendBroadcast_HealArmor()

    def CmdFleetBroadcast_HealShield(self):
        sm.GetService('fleet').SendBroadcast_HealShield()

    def CmdFleetBroadcast_HealCapacitor(self):
        sm.GetService('fleet').SendBroadcast_HealCapacitor()

    def CmdFleetBroadcast_InPosition(self):
        sm.GetService('fleet').SendBroadcast_InPosition()

    def CmdFleetBroadcast_HoldPosition(self):
        sm.GetService('fleet').SendBroadcast_HoldPosition()

    def CmdFleetBroadcast_JumpBeacon(self):
        sm.GetService('fleet').SendBroadcast_JumpBeacon()

    def CmdFleetBroadcast_Location(self):
        sm.GetService('fleet').SendBroadcast_Location()

    def CmdSetCameraPOV(self):
        if not self._IsSpaceCameraSwitchAllowed():
            return
        sm.GetService('sceneManager').SetPrimaryCamera(evecamera.CAM_SHIPPOV)

    CmdSetCameraPOV.nameLabelPath = 'Tooltips/Hud/POVCamera'
    CmdSetCameraPOV.descriptionLabelPath = 'Tooltips/Hud/POVCamera_description'

    def CmdSetCameraOrbit(self):
        if not self._IsSpaceCameraSwitchAllowed():
            return
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if cam.cameraID in (evecamera.CAM_SHIPORBIT, evecamera.CAM_SHIPORBIT_ABYSSAL_SPACE, evecamera.CAM_SHIPORBIT_HAZARD):
            if cam.GetItemID() != session.shipid:
                cam.LookAt(session.shipid)
            elif cam.isManualFovEnabled:
                cam.DisableManualFov()
            else:
                cam.Track(session.shipid)
        else:
            sm.GetService('sceneManager').SetPrimaryCamera(get_orbit_camera_by_solar_system(session.solarsystemid2))

    CmdSetCameraOrbit.nameLabelPath = 'Tooltips/Hud/OrbitCamera'
    CmdSetCameraOrbit.descriptionLabelPath = 'Tooltips/Hud/OrbitCamera_description'

    def CmdSetCameraTactical(self):
        if is_tactical_camera_suppressed(session.solarsystemid):
            return
        if not self._IsSpaceCameraSwitchAllowed():
            return
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if cam.cameraID == evecamera.CAM_TACTICAL:
            cam.LookAt(session.shipid, allowSwitchCamera=False)
        else:
            sm.GetService('sceneManager').SetPrimaryCamera(evecamera.CAM_TACTICAL)

    CmdSetCameraTactical.nameLabelPath = 'Tooltips/Hud/TacticalCamera'
    CmdSetCameraTactical.descriptionLabelPath = 'Tooltips/Hud/TacticalCamera_description'

    def CmdIncreaseSpaceMouseSpeed(self):
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if cam.cameraID in (evecamera.CAM_TACTICAL, evecamera.CAM_DEBUG):
            speed = min(1.0, gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT) + 0.01)
            gfxsettings.Set(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT, speed, pending=False)
            acceleration = gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT)
            sm.ScatterEvent('OnSpaceMouseSpeedCoefficientChanged')
            sm.GetService('space').SetShortcutText(GetByLabel('Tooltips/Hud/SpaceMouseCaption'), GetByLabel('Tooltips/Hud/SpaceMouseInfo', speed=speed * 100, acceleration=acceleration * 100), hideDelayMs=750)

    CmdIncreaseSpaceMouseSpeed.nameLabelPath = 'Tooltips/Hud/SpaceMouseSpeedIncrease'
    CmdIncreaseSpaceMouseSpeed.descriptionLabelPath = 'Tooltips/Hud/SpaceMouseSpeedIncrease_description'

    def CmdDecreaseSpaceMouseSpeed(self):
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if cam.cameraID in (evecamera.CAM_TACTICAL, evecamera.CAM_DEBUG):
            speed = max(0.01, gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT) - 0.01)
            gfxsettings.Set(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT, speed, pending=False)
            acceleration = gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT)
            sm.ScatterEvent('OnSpaceMouseSpeedCoefficientChanged')
            sm.GetService('space').SetShortcutText(GetByLabel('Tooltips/Hud/SpaceMouseCaption'), GetByLabel('Tooltips/Hud/SpaceMouseInfo', speed=speed * 100, acceleration=acceleration * 100), hideDelayMs=750)

    CmdDecreaseSpaceMouseSpeed.nameLabelPath = 'Tooltips/Hud/SpaceMouseSpeedDecrease'
    CmdDecreaseSpaceMouseSpeed.descriptionLabelPath = 'Tooltips/Hud/SpaceMouseSpeedDecrease_description'

    def CmdIncreaseSpaceMouseAcceleration(self):
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if cam.cameraID in (evecamera.CAM_TACTICAL, evecamera.CAM_DEBUG):
            acceleration = min(1.0, gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT) + 0.01)
            gfxsettings.Set(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT, acceleration, pending=False)
            speed = gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT)
            sm.ScatterEvent('OnSpaceMouseAccelerationCoefficientChanged')
            sm.GetService('space').SetShortcutText(GetByLabel('Tooltips/Hud/SpaceMouseCaption'), GetByLabel('Tooltips/Hud/SpaceMouseInfo', speed=speed * 100, acceleration=acceleration * 100), hideDelayMs=750)

    CmdIncreaseSpaceMouseAcceleration.nameLabelPath = 'Tooltips/Hud/SpaceMouseAccelerationIncrease'
    CmdIncreaseSpaceMouseAcceleration.descriptionLabelPath = 'Tooltips/Hud/SpaceMouseAccelerationIncrease_description'

    def CmdDecreaseSpaceMouseAcceleration(self):
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if cam.cameraID in (evecamera.CAM_TACTICAL, evecamera.CAM_DEBUG):
            acceleration = max(0.01, gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT) - 0.01)
            gfxsettings.Set(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT, acceleration, pending=False)
            speed = gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT)
            sm.ScatterEvent('OnSpaceMouseAccelerationCoefficientChanged')
            sm.GetService('space').SetShortcutText(GetByLabel('Tooltips/Hud/SpaceMouseCaption'), GetByLabel('Tooltips/Hud/SpaceMouseInfo', speed=speed * 100, acceleration=acceleration * 100), hideDelayMs=750)

    CmdDecreaseSpaceMouseAcceleration.nameLabelPath = 'Tooltips/Hud/SpaceMouseAccelerationDecrease'
    CmdDecreaseSpaceMouseAcceleration.descriptionLabelPath = 'Tooltips/Hud/SpaceMouseAccelerationDecrease_description'

    def _IsSpaceCameraSwitchAllowed(self):
        if not sm.GetService('viewState').IsViewActive(ViewState.Space):
            return
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if not cam or cam.IsLocked():
            return False
        return True

    def OpenCapitalNavigation(self, *args):
        if eveCfg.GetActiveShip():
            CapitalNav.ToggleOpenClose()

    OpenCapitalNavigation.nameLabelPath = CapitalNav.default_captionLabelPath

    def OpenMonitor(self, *args):
        EngineToolsLauncher.Open()

    OpenMonitor.nameLabelPath = 'UI/Commands/OpenMonitor'

    def OpenFpsMonitor(self, *args):
        from carbonui.modules.fpsmonitor import FpsMonitor
        FpsMonitor.ToggleOpenClose(parent=uicore.layer.alwaysvisible)

    OpenFpsMonitor.nameLabelPath = 'UI/Commands/OpenFpsMonitor'

    def OpenConfigMenu(self, *args):
        sysMenu = uicore.layer.systemmenu
        if sysMenu.isopen:
            uthread.new(sysMenu.CloseMenu)
        else:
            sysMenu.OpenView()

    OpenConfigMenu.nameLabelPath = 'UI/Commands/OpenConfigMenu'

    def OpenMail(self, *args):
        if session.charid:
            return MailWindow.ToggleOpenClose()

    OpenMail.nameLabelPath = MailWindow.default_captionLabelPath
    OpenMail.descriptionLabelPath = MailWindow.default_descriptionLabelPath

    def CmdOpenNewMessage(self, *args):
        if session.charid:
            sm.GetService('mailSvc').SendMsgDlg()

    def OpenWallet(self, *args):
        if session.solarsystemid2:
            WalletWindow.ToggleOpenClose()

    OpenWallet.nameLabelPath = WalletWindow.default_captionLabelPath

    def OpenCorporationPanel(self, *args):
        if session.solarsystemid2:
            wnd = CorporationWindow.GetIfOpen()
            if wnd:
                CorporationWindow.ToggleOpenClose()
            elif idCheckers.IsNPC(session.corpid):
                panel_id = CorpPanel.MY_APPLICATIONS if sm.GetService('corp').GetMyOpenInvitations() else None
                sm.GetService('corpui').Show(panel_id=panel_id)
            else:
                sm.GetService('corpui').Show()

    OpenCorporationPanel.nameLabelPath = CorporationWindow.default_captionLabelPath
    OpenCorporationPanel.descriptionLabelPath = CorporationWindow.default_descriptionLabelPath

    def OpenAssets(self, *args):
        if session.solarsystemid2:
            AssetsWindow.ToggleOpenClose()

    OpenAssets.nameLabelPath = AssetsWindow.default_captionLabelPath
    OpenAssets.descriptionLabelPath = AssetsWindow.default_descriptionLabelPath

    def OpenChannels(self, *args):
        if session.solarsystemid2:
            XmppChatChannels.Open()

    OpenChannels.nameLabelPath = XmppChatChannels.default_captionLabelPath
    OpenChannels.descriptionLabelPath = XmppChatChannels.default_descriptionLabelPath

    def OpenJournal(self, *args):
        if session.solarsystemid2:
            JournalWindow.ToggleOpenClose()

    OpenJournal.nameLabelPath = JournalWindow.default_captionLabelPath
    OpenJournal.descriptionLabelPath = JournalWindow.default_descriptionLabelPath

    def OpenAgencyNew(self, *args):
        if not session.solarsystemid2:
            return
        AgencyWndNew.ToggleOpenClose()

    OpenAgencyNew.nameLabelPath = 'UI/Agency/Caption'
    OpenAgencyNew.descriptionLabelPath = 'UI/Agency/Description'

    def OpenCombatAnomaliesInAgency(self, *args):
        if not session.solarsystemid2:
            return
        AgencyWndNew.OpenAndShowContentGroup(contentGroupID=agencyContentGroupConst.contentGroupCombatAnomalies)

    OpenCombatAnomaliesInAgency.nameLabelPath = 'UI/Agency/CaptionCombatAnomalies'
    OpenCombatAnomaliesInAgency.descriptionLabelPath = 'UI/Agency/Description'

    def OpenFactionWarfareInAgency(self, *args):
        if not session.solarsystemid2:
            return
        AgencyWndNew.OpenAndShowContentGroup(contentGroupID=agencyContentGroupConst.contentGroupFactionalWarfareSystems)

    OpenCombatAnomaliesInAgency.nameLabelPath = 'UI/Agency/Caption'
    OpenCombatAnomaliesInAgency.descriptionLabelPath = 'UI/Agency/Description'

    def OpenSeason(self, *args):
        OpenSeasonsWindow()

    OpenSeason.nameLabelPath = 'UI/Seasons/Title'
    OpenSeason.descriptionLabelPath = 'UI/Seasons/Subcaption'

    def OpenEncounterSurveillanceSystemInAgency(self):
        if not session.solarsystemid2:
            return
        AgencyWndNew.OpenAndShowContentGroup(contentGroupID=agencyContentGroupConst.contentGroupESSSystems)

    OpenEncounterSurveillanceSystemInAgency.nameLabelPath = 'UI/Agency/CaptionEncounterSurveillanceSystem'
    OpenEncounterSurveillanceSystemInAgency.descriptionLabelPath = 'UI/Agency/Description'

    def OpenLoginRewardWindow(self, *args):
        if not session.solarsystemid2:
            return
        inDailyCampaign = sm.GetService('loginCampaignService').is_user_enrolled_in_campaign()
        seasonActive = sm.GetService('seasonalLoginCampaignService').is_login_campaign_active()
        if inDailyCampaign or seasonActive:
            from eve.client.script.ui.shared.loginRewards.loginRewardsWnd import DailyLoginRewardsWnd
            DailyLoginRewardsWnd.ToggleOpenClose()

    OpenLoginRewardWindow.nameLabelPath = 'UI/LoginRewards/WindowCaption'
    OpenLoginRewardWindow.descriptionLabelPath = 'UI/LoginRewards/WindowDescription'

    def OpenSkillsWindow(self, forceClose = False, *args, **kwds):
        if session.charid:
            if forceClose:
                if SkillPlanDockablePanel.CloseIfOpen():
                    uthread2.sleep(0.1)
                SkillPlanDockablePanel.Open(*args, **kwds)
            else:
                SkillPlanDockablePanel.ToggleOpenClose(*args, **kwds)

    OpenSkillsWindow.nameLabelPath = 'UI/SkillPlan/Skills'
    OpenSkillsWindow.descriptionLabelPath = 'Tooltips/Neocom/SkillPlans_description'

    def OpenEveMenu(self, *args):
        sm.GetService('neocom').ToggleEveMenu()

    OpenEveMenu.nameLabelPath = 'Tooltips/Neocom/NeocomMenu'
    OpenEveMenu.descriptionLabelPath = 'Tooltips/Neocom/NeocomMenu_description'

    def ToggleAurumStore(self, *args):
        sm.GetService('vgsService').ToggleStore()

    ToggleAurumStore.nameLabelPath = 'UI/VirtualGoodsStore/VgsName'
    ToggleAurumStore.descriptionLabelPath = 'Tooltips/Neocom/Vgs_description'

    def ToggleProjectDiscovery(self, *args):
        get_project_discovery_window_class().ToggleOpenClose()

    ToggleProjectDiscovery.nameLabelPath = 'UI/ProjectDiscovery/ProjectName'
    ToggleProjectDiscovery.descriptionLabelPath = 'Tooltips/Neocom/ProjectDiscoveryDescription'

    def OpenProjectDiscovery(self):
        get_project_discovery_window_class().Open()

    @ThrottlePerMinute(5)
    def CmdBuyPlex(self, logContext):
        sm.GetService('fastCheckoutClientService').buy_plex(log_context=logContext)

    def ToggleRedeemItems(self, *args):
        if session.charid is not None:
            sm.StartService('redeem').ToggleRedeemWindow()

    ToggleRedeemItems.nameLabelPath = 'UI/Commands/RedeemItems'
    ToggleRedeemItems.descriptionLabelPath = 'Tooltips/Neocom/RedeemItems_description'

    def ToggleActivities(self, *args):
        if session.charid is not None:
            sm.StartService('activities').ToggleActivities()

    ToggleActivities.nameLabelPath = 'UI/Commands/Activities'
    ToggleActivities.descriptionLabelPath = 'Tooltips/Neocom/Activities_description'

    def OpenLog(self, *args):
        uthread.new(self.__OpenLog_thread).context = 'cmd.OpenLog'

    OpenLog.nameLabelPath = LoggerWindow.default_captionLabelPath
    OpenLog.descriptionLabelPath = LoggerWindow.default_descriptionLabelPath

    def OpenStructureBrowser(self, *args):
        StructureBrowserWnd.ToggleOpenClose()

    OpenStructureBrowser.nameLabelPath = StructureBrowserWnd.default_captionLabelPath
    OpenStructureBrowser.descriptionLabelPath = 'Tooltips/Neocom/StructureBrowserDescription'

    def OpenAccessGroupsWindow(self, *args):
        AccessGroupsWnd.ToggleOpenClose()

    OpenAccessGroupsWindow.nameLabelPath = AccessGroupsWnd.default_captionLabelPath
    OpenAccessGroupsWindow.descriptionLabelPath = 'Tooltips/Neocom/AccessListsDescription'

    def __OpenLog_thread(self, *args):
        LoggerWindow.ToggleOpenClose()

    def OpenDroneBayOfActiveShip(self, *args):
        if eveCfg.GetActiveShip() is not None:
            uthread.new(self.__OpenDroneBayOfActiveShip_thread).context = 'cmd.OpenDroneBayOfActiveShip'

    OpenDroneBayOfActiveShip.nameLabelPath = 'UI/Commands/OpenDroneBayOfActiveShip'

    def __OpenDroneBayOfActiveShip_thread(self, *args):
        shipID = eveCfg.GetActiveShip()
        if shipID is None:
            return
        shipItem = sm.GetService('clientDogmaIM').GetDogmaLocation().GetDogmaItemWithWait(shipID)
        godmaType = sm.GetService('godma').GetType(shipItem.typeID)
        if godmaType.droneCapacity or IsModularShip(shipItem.typeID):
            invID = ('ShipDroneBay', shipID)
            Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True)
        else:
            raise UserError('ShipHasNoDroneBay')

    def OpenFighterBayOfActiveShip(self, *args):
        if eveCfg.GetActiveShip() is not None:
            uthread.new(self.__OpenFighterBayOfActiveShip_thread).context = 'cmd.OpenFighterBayOfActiveShip'

    OpenFighterBayOfActiveShip.nameLabelPath = 'UI/Commands/OpenFighterBayOfActiveShip'

    def __OpenFighterBayOfActiveShip_thread(self, *args):
        shipID = session.shipid
        if shipID is None:
            return
        shipItem = sm.GetService('clientDogmaIM').GetDogmaLocation().GetDogmaItemWithWait(shipID)
        godmaType = sm.GetService('godma').GetType(shipItem.typeID)
        if godmaType.fighterCapacity:
            if session.shipid == session.structureid:
                invID = ('StructureFighterBay', shipID)
            else:
                invID = ('ShipFighterBay', shipID)
            Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True)
        else:
            raise UserError('ShipHasNoFighterBay')

    def OpenCargoHoldOfActiveShip(self, *args):
        if eveCfg.GetActiveShip() is not None:
            uthread.new(self.__OpenCargoHoldOfActiveShip_thread).context = 'cmd.OpenCargoHoldOfActiveShip'

    OpenCargoHoldOfActiveShip.nameLabelPath = 'Tooltips/Hud/CargoHold'
    OpenCargoHoldOfActiveShip.descriptionLabelPath = 'Tooltips/Hud/CargoHold_description'

    def __OpenCargoHoldOfActiveShip_thread(self, *args):
        shipID = eveCfg.GetActiveShip()
        if eveCfg.IsControllingStructure():
            return self.OpenStructureCargo()
        if shipID is None:
            return
        shipItem = sm.GetService('clientDogmaIM').GetDogmaLocation().GetDogmaItemWithWait(shipID)
        if shipItem is None:
            return
        invID = (invConst.INVENTORY_ID_SHIP_CARGO, shipID)
        Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True)

    def OpenStructureCargo(self):
        invID = ('Structure', session.structureid)
        Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True)

    def OpenPlexVault(self):
        invID = (invConst.INVENTORY_ID_PLEX_VAULT, None)
        Inventory.OpenOrShow(invID=invID, usePrimary=True, toggle=True)

    OpenPlexVault.nameLabelPath = 'UI/Neocom/PlexVault'
    OpenPlexVault.descriptionLabelPath = 'Tooltips/Neocom/PlexVaultDescription'
    OpenStructureCargo.nameLabelPath = 'Tooltips/Hud/CargoHold'
    OpenStructureCargo.descriptionLabelPath = 'Tooltips/Hud/CargoHoldStructure_description'

    def OpenRaffleWindow(self):
        sm.GetService('raffleSvc').toggle_window()

    OpenRaffleWindow.nameLabelPath = 'UI/HyperNet/WindowTitle'
    OpenRaffleWindow.descriptionLabelPath = 'UI/HyperNet/WindowDescription'

    def OpenJobBoardWindow(self):
        get_job_board_service().toggle_window()

    OpenJobBoardWindow.nameLabelPath = 'UI/Opportunities/WindowTitle'
    OpenJobBoardWindow.descriptionLabelPath = 'UI/Opportunities/WindowDescription'

    def OpenPVPFilamentEventWindow(self):
        sm.GetService('pvpFilamentSvc').OpenPVPFilamentEventWindow()

    OpenPVPFilamentEventWindow.nameLabelPath = 'UI/PVPFilament/EventWindow/WindowTitle'
    OpenPVPFilamentEventWindow.descriptionLabelPath = 'UI/PVPFilament/EventWindow/WindowDescription'

    def OpenFuelBayOfActiveShip(self):
        self._OpenSpecialHoldOfActiveship(appConst.attributeSpecialFuelBayCapacity, 'ShipFuelBay')

    OpenFuelBayOfActiveShip.nameLabelPath = 'UI/Commands/OpenFuelBayOfActiveShip'

    def OpenGeneralMiningHoldOfActiveShip(self):
        self._OpenSpecialHoldOfActiveship(appConst.attributeGeneralMiningHoldCapacity, 'ShipGeneralMiningHold')

    OpenGeneralMiningHoldOfActiveShip.nameLabelPath = 'UI/Commands/OpenGeneralMiningHoldOfActiveShip'

    def OpenMineralHoldOfActiveShip(self):
        self._OpenSpecialHoldOfActiveship(appConst.attributeSpecialMineralHoldCapacity, 'ShipMineralHold')

    OpenMineralHoldOfActiveShip.nameLabelPath = 'UI/Commands/OpenMineralHoldOfActiveShip'

    def OpenPlanetaryCommoditiesHoldOfActiveShip(self):
        self._OpenSpecialHoldOfActiveship(appConst.attributeSpecialPlanetaryCommoditiesHoldCapacity, 'ShipPlanetaryCommoditiesHold')

    OpenPlanetaryCommoditiesHoldOfActiveShip.nameLabelPath = 'UI/Commands/OpenPlanetaryCommoditiesHoldOfActiveShip'

    def OpenAmmoHoldOfActiveShip(self):
        self._OpenSpecialHoldOfActiveship(appConst.attributeSpecialAmmoHoldCapacity, 'ShipAmmoHold')

    OpenAmmoHoldOfActiveShip.nameLabelPath = 'UI/Commands/OpenAmmoHold'

    def OpenFleetHangarOfActiveShip(self):
        self._OpenSpecialHoldOfActiveship(appConst.attributeFleetHangarCapacity, 'ShipFleetHangar')

    OpenFleetHangarOfActiveShip.nameLabelPath = 'UI/Commands/OpenFleetHangar'

    def OpenShipMaintenanceOfBayActiveShip(self):
        self._OpenSpecialHoldOfActiveship(appConst.attributeShipMaintenanceBayCapacity, 'ShipMaintenanceBay')

    OpenShipMaintenanceOfBayActiveShip.nameLabelPath = 'UI/Commands/OpenShipMaintenanceBay'

    def OpenFrigateEscapeBay(self):
        self._OpenSpecialHoldOfActiveship(appConst.attributeFrigateEscapeBayCapacity, 'ShipFrigateEscapeBay')

    OpenFrigateEscapeBay.nameLabelPath = 'UI/Commands/OpenFrigateEscapeBay'

    def _OpenSpecialHoldOfActiveship(self, attr, invCtrlName):
        itemID = eveCfg.GetActiveShip()
        if itemID is None:
            return
        ship = sm.GetService('clientDogmaIM').GetDogmaLocation().GetDogmaItemWithWait(itemID)
        if bool(sm.GetService('godma').GetTypeAttribute(ship.typeID, attr)):
            invID = (invCtrlName, itemID)
            Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True)

    def OpenCharactersheet(self, *args):
        if session.solarsystemid2:
            CharacterSheetWindow.ToggleOpenClose()

    OpenCharactersheet.nameLabelPath = CharacterSheetWindow.default_captionLabelPath
    OpenCharactersheet.descriptionLabelPath = CharacterSheetWindow.default_descriptionLabelPath

    def OpenFleet(self, *args):
        FleetWindow.ToggleOpenClose()

    OpenFleet.nameLabelPath = FleetWindow.default_captionLabelPath
    OpenFleet.descriptionLabelPath = FleetWindow.default_descriptionLabelPath

    def OpenFleetWatchlist(self):
        if not session.fleetid:
            return
        WatchListPanel.Open(showActions=False, panelName=localization.GetByLabel('UI/Fleet/WatchList'))

    OpenFleetWatchlist.nameLabelPath = 'UI/Fleet/Watchlist/WatchListWindow'

    def OpenPeopleAndPlaces(self, *args):
        if session.solarsystemid2:
            AddressBookWindow.ToggleOpenClose()

    OpenPeopleAndPlaces.nameLabelPath = AddressBookWindow.default_captionLabelPath
    OpenPeopleAndPlaces.descriptionLabelPath = AddressBookWindow.default_descriptionLabelPath

    def OpenLocations(self, *args):
        if session.solarsystemid2:
            LocationsWindow.ToggleOpenClose()

    OpenLocations.nameLabelPath = LocationsWindow.default_captionLabelPath
    OpenLocations.descriptionLabelPath = LocationsWindow.default_descriptionLabelPath

    def OpenHelp(self, *args):
        if not session.charid:
            return
        HelpWindow.ToggleOpenClose()

    OpenHelp.nameLabelPath = HelpWindow.default_captionLabelPath
    OpenHelp.descriptionLabelPath = HelpWindow.default_descriptionLabelPath

    def OpenReportBug(self, *args):
        BugReportingWindow.ToggleOpenClose()

    def OpenManageRoute(self, *args):
        if not session.charid:
            return
        AutopilotSettings.ToggleOpenClose()

    OpenManageRoute.nameLabelPath = AutopilotSettings.default_captionLabelPath

    def OpenProbeScanner(self, *args):
        if eveCfg.InSpace():
            if is_scanning_suppressed(session.solarsystemid2):
                raise UserError('CannotProbeScanInSystem')
            from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow
            ProbeScannerWindow.OpenProbeScanner(*args)
        else:
            ShowQuickMessage(GetByLabel('UI/ErrorDialog/mustUndockToTakeAction'))

    OpenProbeScanner.nameLabelPath = ProbeScannerWindow.default_captionLabelPath
    OpenProbeScanner.descriptionLabelPath = ProbeScannerWindow.default_descriptionLabelPath

    def ToggleProbeScanner(self, *args):
        if eveCfg.InSpace():
            if is_scanning_suppressed(session.solarsystemid2):
                raise UserError('CannotProbeScanInSystem')
            from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow
            ProbeScannerWindow.ToggleOpenCloseProbeScanner()
        else:
            ShowQuickMessage(GetByLabel('UI/ErrorDialog/mustUndockToTakeAction'))

    ToggleProbeScanner.nameLabelPath = ProbeScannerWindow.default_captionLabelPath
    ToggleProbeScanner.descriptionLabelPath = ProbeScannerWindow.default_descriptionLabelPath

    def OpenDirectionalScanner(self, toggle = True, *args):
        if eveCfg.InSpace():
            if is_directional_scanner_suppressed(session.solarsystemid2):
                ShowQuickMessage(GetByLabel('UI/InfoWindow/DscanDisabled'))
                return
            if toggle:
                DirectionalScanner.ToggleOpenCloseDirectionalScanner()
            else:
                DirectionalScanner.OpenDirectionalScanner()

    OpenDirectionalScanner.nameLabelPath = DirectionalScanner.default_captionLabelPath
    OpenDirectionalScanner.descriptionLabelPath = DirectionalScanner.default_descriptionLabelPath

    def OpenMoonScan(self, *args):
        if eveCfg.InShipInSpace():
            MoonScanner.ToggleOpenClose()

    OpenMoonScan.nameLabelPath = MoonScanner.default_captionLabelPath

    def OpenMapBrowser(self, locationID = None):
        if session.solarsystemid2:
            if is_map_browser_suppressed(session.solarsystemid2):
                wnd = MapBrowserWnd.GetIfOpen()
                if wnd and not wnd.destroyed:
                    wnd.Close()
                raise UserError('CannotOpenMapBrowserInAbyssSpace')
            wnd = MapBrowserWnd.GetIfOpen()
            if wnd and not wnd.destroyed:
                if locationID is None:
                    wnd.ToggleOpenClose()
                else:
                    if wnd.state == uiconst.UI_HIDDEN:
                        wnd.Show()
                    wnd.DoLoad(locationID)
                return
            MapBrowserWnd.Open(locationID=locationID)

    OpenMapBrowser.nameLabelPath = MapBrowserWnd.default_captionLabelPath
    OpenMapBrowser.descriptionLabelPath = MapBrowserWnd.default_descriptionLabelPath

    def OpenHangarFloor(self, *args):
        if session.stationid:
            invWindow.StationItems.ToggleOpenClose(windowInstanceID=session.stationid)
        if session.structureid:
            invWindow.StructureItems.ToggleOpenClose(windowInstanceID=session.structureid)

    OpenHangarFloor.nameLabelPath = 'UI/Commands/OpenHangarFloor'

    def OpenShipHangar(self, *args, **kwds):
        if session.stationid:
            invWindow.StationShips.ToggleOpenClose(windowInstanceID=session.stationid)
        if session.structureid:
            invWindow.StructureShips.ToggleOpenClose(windowInstanceID=session.structureid)

    OpenShipHangar.nameLabelPath = 'UI/Commands/OpenShipHangar'

    def OpenInventory(self, *args):
        if not session.charid:
            return
        invWindow.InventoryPrimary.ToggleOpenClose()

    OpenInventory.nameLabelPath = 'UI/Neocom/InventoryBtn'
    OpenInventory.descriptionLabelPath = 'Tooltips/Neocom/Inventory_description'

    def OpenCalculator(self, *args):
        Calculator.ToggleOpenClose()

    OpenCalculator.nameLabelPath = Calculator.default_captionLabelPath
    OpenCalculator.descriptionLabelPath = Calculator.default_descriptionLabelPath

    def OpenOverviewSettings(self, *args):
        OverviewSettingsWnd.Open()

    OpenOverviewSettings.nameLabelPath = OverviewSettingsWnd.default_captionLabelPath
    OpenOverviewSettings.descriptionLabelPath = OverviewSettingsWnd.default_descriptionLabelPath

    def OpenCorpHangar(self, *args):
        office = sm.GetService('officeManager').GetCorpOfficeAtLocation()
        if office:
            invClass = 'StationCorpHangars' if session.stationid else 'StructureCorpHangars'
            invID = (invClass, office.officeID)
            Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True)

    OpenCorpHangar.nameLabelPath = 'UI/Commands/OpenCorpHangar'

    def OpenCorpDeliveries(self, *args):
        if session.stationid or session.structureid:
            uthread.new(self.__OpenCorpDeliveries_thread)

    OpenCorpDeliveries.nameLabelPath = 'UI/Commands/OpenCorpDeliveries'

    def __OpenCorpDeliveries_thread(self, *args):
        locationID = session.stationid or session.structureid
        if not locationID:
            return
        invWindow.StationCorpDeliveries.ToggleOpenClose(windowInstanceID=locationID)

    def OpenVideoPlayerWindow(self, videoPath):
        VideoPlayerWindow.Open().SetVideoPath(videoPath)

    def OpenPaintToolWindow(self, *args):
        PaintToolWnd.ToggleOpenClose()

    OpenPaintToolWindow.nameLabelPath = PaintToolWnd.default_captionLabelPath
    OpenPaintToolWindow.descriptionLabelPath = PaintToolWnd.default_descriptionLabelPath

    def OpenShipSKINRWindow(self, *args):
        ShipSKINRWindow.ToggleOpenClose()

    OpenShipSKINRWindow.nameLabelPath = ShipSKINRWindow.default_captionLabelPath
    OpenShipSKINRWindow.descriptionLabelPath = ShipSKINRWindow.default_descriptionLabelPath

    def GetSecureServerUrl(self):
        secure_server_url = self.check_secure_url_flag()
        return secure_server_url

    def GetStoreServerUrl(self):
        store_server_url = self.check_store_url_flag()
        return store_server_url

    def BuyMultipleCharacterTrainingOnline(self, origin = None, reason = None):
        try:
            base_url = self.GetStoreServerUrl()
            plex_url = self.GetURLWithParameters(url=base_url, path='mct', origin=origin, reason=reason, utm_medium='app', utm_source='eveonline', utm_campaign='newedenstore', utm_content='cta_buymct')
            if 'secure' in base_url.lower():
                plex_url = self.GetURLWithParameters(url=urlparse.urljoin(base_url, 'multiple-character-training'), origin=origin, reason=reason, utm_medium='app', utm_source='eveonline', utm_campaign='newedenstore', utm_content='cta_buymct')
            blue.os.ShellExecute(plex_url)
        except Exception:
            LogException('Failed to open URL to buy MCT online')
            raise UserError('FailedToOpenBuyPlexUrl')

    def BuyContextualOfferOnline(self, url, offerID):
        try:
            baseurl = urllib.splitquery(url)[0]
            kwargs = self.UrlParamsToKwargDict(url) if '?' in url else {}
            contextualOfferUrl = self.GetURLWithParameters(url=baseurl, origin='contextualofferwindow', utm_medium='app', utm_source='eveonline', utm_campaign='contextualoffers', utm_content=str(offerID), **kwargs)
            blue.os.ShellExecute(contextualOfferUrl)
        except Exception:
            LogException('Failed to open URL for the offer (offerID: %s, URL: %s)' % (offerID, url))
            raise

    def ViewSpecialOffersOnline(self, origin = None, reason = None):
        try:
            specialOffersUrl = self.GetURLWithParameters(url=self.GetStoreServerURL(), origin=origin, reason=reason)
            blue.os.ShellExecute(specialOffersUrl)
        except Exception:
            LogException('Failed to open Special Offers URL')
            raise

    def UrlParamsToKwargDict(self, url):
        kwargs = {}
        queryResults = urllib.splitquery(url)
        if len(queryResults) > 1:
            query = queryResults[1]
            splitquery = query.split('&')
            for keyvalueset in splitquery:
                key, value = urllib.splitvalue(keyvalueset)
                kwargs[key] = value

        return kwargs

    def OpenAccountManagement(self, origin = None, reason = None):
        try:
            accountUrl = self.GetURLWithParameters(self.GetSecureServerUrl(), origin=origin, reason=reason)
            blue.os.ShellExecute(accountUrl)
        except Exception:
            LogException('Failed to open URL to access account management online')
            raise UserError('FailedToOpenAccountManagementUrl')

    def GetURLWithParameters(self, url, origin, **kwargs):
        try:
            token = sm.RemoteSvc('userSvc').GetUserToken()
            kwargs['token'] = token
        except Exception:
            LogException('No token generated')
            raise

        if IsClientLaunchedThroughSteam():
            origin = AppendSteamOriginIfApplies(origin)
        kwargs['origin'] = origin
        url = urlparse.urlsplit(url)
        existing_qs = dict(urlparse.parse_qsl(url.query))
        overlapped = set(existing_qs.keys()).intersection(set(kwargs.keys()))
        if overlapped:
            self.LogWarn('GetURLWithParameters: overriding pre-existing query parameters:', list(overlapped))
        existing_qs.update(kwargs)
        updated_qs = urllib.urlencode(existing_qs.items())
        augmented_url = urlparse.SplitResult(url.scheme, url.netloc, url.path, updated_qs, url.fragment)
        url_with_parameters = urlparse.urlunsplit(augmented_url)
        self.LogNotice('GetURLWithParameters - URL: %s' % url_with_parameters)
        return url_with_parameters

    def OpenBrowser(self, url = None, windowName = 'virtualbrowser', args = {}, data = None, newTab = False):
        parsedUrl = urlparse.urlparse(url or '')
        if not session.charid:
            if url is not None and url != 'home' and parsedUrl.scheme in ('http', 'https'):
                blue.os.ShellExecute(url)
            return
        if parsedUrl.hostname and (parsedUrl.hostname.count('secure.eveonline.com') > 0 or parsedUrl.hostname.count('store.eveonline.com') > 0):
            if parsedUrl.path.lower().count('plex') > 0:
                sm.GetService('fastCheckoutClientService').buy_plex_online()
            else:
                self.OpenAccountManagement()
            return

    OpenBrowser.nameLabelPath = 'UI/Neocom/BrowserBtn'

    def OpenNotepad(self, *args):
        NotepadWindow.ToggleOpenClose()

    OpenNotepad.nameLabelPath = NotepadWindow.default_captionLabelPath
    OpenNotepad.descriptionLabelPath = NotepadWindow.default_descriptionLabelPath

    def OpenMoonMining(self, id = None):
        bp = sm.GetService('michelle').GetBallpark()
        if not id:
            for itemID in bp.slimItems:
                if bp.slimItems[itemID].groupID == appConst.groupControlTower:
                    id = bp.slimItems[itemID]
                    break

        if not id:
            return
        MoonMining.ToggleOpenClose(slimItem=id)

    OpenMoonMining.nameLabelPath = MoonMining.default_captionLabelPath
    OpenMoonMining.descriptionLabelPath = MoonMining.default_descriptionLabelPath

    def OpenLedger(self, *args):
        LedgerWindow.ToggleOpenClose()

    OpenLedger.nameLabelPath = LedgerWindow.default_captionLabelPath
    OpenLedger.descriptionLabelPath = LedgerWindow.default_descriptionLabelPath

    def OpenCloneUpgradeWindow(self, origin = None, reason = None):
        open_omega_upgrade_window(origin=origin, reason=reason)

    def OpenShipConfig(self, id = None):
        activeShipID = eveCfg.GetActiveShip()
        if activeShipID is not None:
            ship = sm.GetService('clientDogmaIM').GetDogmaLocation().GetShip()
            typeObj = sm.GetService('godma').GetType(ship.typeID)
            if bool(typeObj.canReceiveCloneJumps):
                ShipConfig.ToggleOpenClose()

    OpenShipConfig.nameLabelPath = ShipConfig.default_captionLabelPath
    OpenShipConfig.descriptionLabelPath = ShipConfig.default_descriptionLabelPath

    def HasServiceAccess(self, serviceName, onlyCheckFacWarSystems = False):
        if onlyCheckFacWarSystems and not sm.GetService('fwWarzoneSvc').IsWarzoneSolarSystem(session.solarsystemid2):
            return True
        from eve.client.script.ui.shared.dockedUI.lobbyWnd import LobbyWnd
        lobby = LobbyWnd.GetIfOpen()
        if lobby is None:
            return False
        lobby.CheckCanAccessService(serviceName)
        return True

    def _IsRepairServiceAvailable(self):
        if session.stationid and sm.GetService('station').IsStationServiceAvailable(appConst.stationServiceRepairFacilities):
            if self.HasServiceAccess('repairshop'):
                return True
        if session.structureid:
            if sm.GetService('structureServices').IsServiceAvailableForCharacter(structures.SERVICE_REPAIR):
                return True
        return False

    def _IsInsuranceServiceAvailable(self):
        if session.stationid and sm.GetService('station').IsStationServiceAvailable(appConst.stationServiceInsurance):
            if self.HasServiceAccess('insurance'):
                return True
        if session.structureid:
            if sm.GetService('structureServices').IsServiceAvailableForCharacter(structures.SERVICE_INSURANCE):
                return True
        return False

    def _IsReprocessingServiceAvailable(self):
        if session.stationid and sm.GetService('station').IsStationServiceAvailable(appConst.stationServiceReprocessingPlant):
            if self.HasServiceAccess('reprocessingPlant'):
                return True
        if session.structureid:
            if sm.GetService('structureSettings').CharacterHasService(session.structureid, structures.SERVICE_REPROCESSING):
                return True
        return False

    def OpenMarket(self, *args):
        if session.stationid is None or self.HasServiceAccess('market', True):
            RegionalMarket.ToggleOpenClose()

    OpenMarket.nameLabelPath = RegionalMarket.default_captionLabelPath
    OpenMarket.descriptionLabelPath = RegionalMarket.default_descriptionLabelPath

    def OpenMarketOrders(self, *args):
        MarketOrdersWnd.ToggleOpenClose()

    OpenMarketOrders.nameLabelPath = MarketOrdersWnd.default_captionLabelPath
    OpenMarketOrders.descriptionLabelPath = MarketOrdersWnd.default_descriptionLabelPath

    def OpenContracts(self, *args):
        wnd = ContractsWindow.ToggleOpenClose()

    OpenContracts.nameLabelPath = ContractsWindow.default_captionLabelPath
    OpenContracts.descriptionLabelPath = ContractsWindow.default_descriptionLabelPath

    def OpenIndustry(self, *args):
        if session.solarsystemid2:
            Industry.ToggleOpenClose()

    OpenIndustry.nameLabelPath = Industry.default_captionLabelPath
    OpenIndustry.descriptionLabelPath = Industry.default_descriptionLabelPath

    def OpenMultibuy(self, *args):
        BuyMultipleTypesWithQty({})

    OpenMultibuy.nameLabelPath = 'UI/Market/Multibuy'
    OpenMultibuy.descriptionLabelPath = 'UI/Market/Multibuy_description'

    def OpenPlanets(self, *args):
        if session.solarsystemid2:
            PlanetWindow.ToggleOpenClose()

    OpenPlanets.nameLabelPath = PlanetWindow.default_captionLabelPath
    OpenPlanets.descriptionLabelPath = PlanetWindow.default_descriptionLabelPath

    def OpenMyMercenaryDens(self, *args):
        if session.solarsystemid2:
            MyMercDensWnd.ToggleOpenClose()

    OpenMyMercenaryDens.nameLabelPath = MyMercDensWnd.default_captionLabelPath
    OpenMyMercenaryDens.descriptionLabelPath = MyMercDensWnd.default_descriptionLabelPath

    def OpenFitting(self, *args):
        return self._OpenNewFittingWnd()

    OpenFitting.nameLabelPath = FittingWindow.default_captionLabelPath
    OpenFitting.descriptionLabelPath = FittingWindow.default_descriptionLabelPath

    def _OpenNewFittingWnd(self):
        fittingSvc = sm.GetService('fittingSvc')
        shipID = fittingSvc.GetShipIDForFittingWindow()
        if shipID is None:
            if fittingSvc.IsShipSimulated():
                fittingSvc.SetSimulationState(False)
            else:
                uicore.Message('CannotPerformActionWithoutShip')
                return
        if session.stationid is None or self.HasServiceAccess('fitting'):
            FittingWindow.ToggleOpenClose(shipID=shipID)

    def OpenMedical(self, *args):
        CharacterSheetWindow.ToggleOpenWithPanel(PANEL_JUMPCLONES)

    OpenMedical.nameLabelPath = 'Tooltips/StationServices/CloneBay'
    OpenMedical.descriptionLabelPath = 'Tooltips/StationServices/CloneBay_description'

    def OpenRepairshop(self, *args):
        if self._IsRepairServiceAvailable():
            RepairShopWindow.ToggleOpenClose()

    OpenRepairshop.nameLabelPath = RepairShopWindow.default_captionLabelPath
    OpenRepairshop.descriptionLabelPath = RepairShopWindow.default_descriptionLabelPath

    def OpenInsurance(self, *args):
        if self._IsInsuranceServiceAvailable():
            InsuranceWindow.ToggleOpenClose()

    OpenInsurance.nameLabelPath = InsuranceWindow.default_captionLabelPath
    OpenInsurance.descriptionLabelPath = InsuranceWindow.default_descriptionLabelPath

    def OpenBountyOffice(self, *args):
        if not IsPlayerBountyHidden(sm.GetService('machoNet')):
            BountyWindow.ToggleOpenClose()

    OpenBountyOffice.nameLabelPath = BountyWindow.default_captionLabelPath
    OpenBountyOffice.descriptionLabelPath = BountyWindow.default_descriptionLabelPath

    def OpenSecurityOffice(self, *args):
        if session.stationid:
            if sm.GetService('securityOfficeSvc').CanAccessServiceInStation(session.stationid):
                SecurityOfficeWindow.ToggleOpenClose()

    OpenSecurityOffice.nameLabelPath = SecurityOfficeWindow.default_captionLabelPath
    OpenSecurityOffice.descriptionLabelPath = SecurityOfficeWindow.default_descriptionLabelPath

    def OpenFwEnlistment(self, *args, **kwargs):
        FwEnlistmentWnd.ToggleOpenClose(**kwargs)

    OpenFwEnlistment.nameLabelPath = FwEnlistmentWnd.default_captionLabelPath

    def OpenInsurgencyDashboard(self, *args, **kwargs):
        InsurgentsDashboard.ToggleOpenClose(**kwargs)

    OpenInsurgencyDashboard.nameLabelPath = InsurgentsDashboard.default_captionLabelPath
    OpenInsurgencyDashboard.descriptionLabelPath = InsurgentsDashboard.default_descriptionLabelPath

    def OpenMilitia(self, *args, **kwargs):
        FwWarzoneDashboard.ToggleOpenClose(**kwargs)

    OpenMilitia.nameLabelPath = FwWarzoneDashboard.default_captionLabelPath
    OpenMilitia.descriptionLabelPath = FwWarzoneDashboard.default_descriptionLabelPath

    def OpenRelevantFWWindow(self, *args, **kwargs):
        if session.warfactionid is None:
            self.OpenFwEnlistment(*args, **kwargs)
        elif IsPirateFWFaction(session.warfactionid):
            self.OpenInsurgencyDashboard(*args, **kwargs)
        else:
            self.OpenMilitia(*args, **kwargs)

    OpenRelevantFWWindow.nameLabelPath = FwWarzoneDashboard.default_captionLabelPath
    OpenRelevantFWWindow.descriptionLabelPath = FwWarzoneDashboard.default_descriptionLabelPath

    def OpenFWInfoTab(self, *args, **kwargs):
        wnd = FwWarzoneDashboard.GetIfOpen()
        if wnd is None:
            wnd = FwWarzoneDashboard.Open()
        wnd.SelectTab('Objectives')

    def OpenReprocessingPlant(self, items = None):
        if self._IsReprocessingServiceAvailable():
            if ReprocessingWnd.IsOpen() and items:
                wnd = ReprocessingWnd.GetIfOpen()
                wnd.AddPreselectedItems(items)
                if wnd.IsMinimized():
                    wnd.Maximize()
            else:
                ReprocessingWnd.ToggleOpenClose(selectedItems=items)

    OpenReprocessingPlant.nameLabelPath = ReprocessingWnd.default_captionLabelPath
    OpenReprocessingPlant.descriptionLabelPath = ReprocessingWnd.default_descriptionLabelPath

    def OpenLpstore(self, *args):
        lpstore = sm.GetService('lpstore')
        if session.stationid:
            stationOwnerCorpID = sm.GetService('station').stationItem.ownerID
            if idCheckers.IsNPC(stationOwnerCorpID) and self.HasServiceAccess('lpstore'):
                stores_to_open = []
                normalStoresInStation = get_normal_lp_stores_in_station(session.stationid, stationOwnerCorpID)
                for corpID in normalStoresInStation:
                    stores_to_open.append(corpID)

                factionID = sm.GetService('map').GetItem(session.solarsystemid2).factionID
                rwCorpID = sm.GetService('rwService').get_rw_corp_for_faction_and_system(factionID)
                if rwCorpID is not None:
                    stores_to_open.append(rwCorpID)
                lpstore.OpenLPStore(stores_to_open)
        elif session.structureid:
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(session.structureid)
            stationOwnerCorpID = structureInfo.ownerID
            if idCheckers.IsNPC(stationOwnerCorpID) and self.HasServiceAccess('lpstore'):
                stores_to_open = [stationOwnerCorpID]
                lpstore.OpenLPStore(stores_to_open)

    OpenLpstore.nameLabelPath = LPStoreWindow.default_captionLabelPath
    OpenLpstore.descriptionLabelPath = LPStoreWindow.default_descriptionLabelPath

    def OpenCharacterCustomization(self, *args):
        if IsContentComplianceControlSystemActive(sm.GetService('machoNet')):
            return
        if getattr(sm.GetService('map'), 'busy', False):
            return
        if sm.GetService('cc').NoExistingCustomization():
            raise UserError('CantRecustomizeCharacterWithoutDoll')
        if session.stationid or session.structureid:
            try:
                self.loadingCharacterCustomization = True
                CharacterSheetWindow.CloseIfOpen()
                wnd = PreviewCharacterWnd.GetIfOpen()
                if wnd is not None:
                    wnd.Close()
                if self.HasServiceAccess('charcustomization'):
                    uicore.cmd.commandMap.UnloadAccelerator(uicore.cmd.commandMap.commandsByName['OpenCharactersheet'])
                    sm.GetService('gameui').GoCharacterCreationCurrentCharacter()
            finally:
                self.loadingCharacterCustomization = False

    OpenCharacterCustomization.nameLabelPath = 'Tooltips/StationServices/CharacterCustomization'
    OpenCharacterCustomization.descriptionLabelPath = 'Tooltips/StationServices/CharacterCustomization_description'

    def OpenCalendar(self, *args):
        sm.GetService('neocom').BlinkOff('clock')
        if session.charid:
            CalendarWnd.ToggleOpenClose()

    OpenCalendar.nameLabelPath = CalendarWnd.default_captionLabelPath
    OpenCalendar.descriptionLabelPath = CalendarWnd.default_descriptionLabelPath

    def OpenAuraInteraction(self, *args):
        agentService = sm.GetService('agents')
        auraID = agentService.GetAuraAgentID()
        agentService.OpenDialogueWindow(auraID)

    def CmdHideUI(self, force = 0):
        sys = uicore.layer.systemmenu
        if sys.isopen and not force:
            return
        sm.GetService('ui').ToggleUiVisible()

    def CmdHideCursor(self, *args):
        uicore.uilib.SetCursor(uiconst.UICURSOR_NONE)

    def CmdToggle3DView(self, *args):
        sm.GetService('sceneManager').ToggleEnable3DView()

    def OpenDungeonEditor(self, *args):
        if eveCfg.InSpace() and session.role & ROLE_CONTENT:
            DungeonEditor.Open()
            if IsJessicaOpen():
                DungeonObjectProperties.Open()
                import panel
                panel.LoadDungeonListViewer()

    OpenDungeonEditor.nameLabelPath = 'UI/Commands/OpenDungeonEditor'

    def OpenFittingMgmt(self):
        FittingMgmt.Open()

    OpenFittingMgmt.nameLabelPath = FittingMgmt.default_captionLabelPath
    OpenFittingMgmt.descriptionLabelPath = 'Tooltips/Neocom/FittingManagementDescription'

    def OpenCompare(self, *args):
        TypeCompare.ToggleOpenClose()

    OpenCompare.nameLabelPath = TypeCompare.default_captionLabelPath
    OpenCompare.descriptionLabelPath = TypeCompare.default_descriptionLabelPath

    def OpenUIDebugger(self, *args):
        if session.role & ROLE_GML:
            UITree.ToggleOpenClose()

    OpenUIDebugger.nameLabelPath = 'UI/Commands/OpenUIDebugger'

    def OpenSkillTreeWindow(self):
        return SkillTreeDockablePanel.ToggleOpenClose()

    def ToggleTelemetryRecord(self):
        if self._telemetrySessionActive:
            blue.statistics.StopTelemetry()
            self._telemetrySessionActive = False
            print '*** Telemetry session stopped ***'
        else:
            blue.statistics.StartTelemetry('localhost')
            self._telemetrySessionActive = True
            print '*** Telemetry session started ***'

    def ToggleUILinearColor(self):
        uicore.desktop.renderObject.useLinearColorSpace = not uicore.desktop.renderObject.useLinearColorSpace

    def ToggleGammaCorrectText(self):
        uicore.desktop.renderObject.gammaCorrectText = not uicore.desktop.renderObject.gammaCorrectText

    def CmdToggleEffects(self, *args):
        candidateEffects = []
        for guid in GetEffectGuids():
            if guid not in FxSequencer.fxTurretGuids and guid not in FxSequencer.fxProtectedGuids:
                candidateEffects.append(guid)

        disabledGuids = sm.GetService('FxSequencer').GetDisabledGuids()
        if len(candidateEffects) > 0:
            if candidateEffects[0] in disabledGuids:
                gfxsettings.Set(gfxsettings.UI_EFFECTS_ENABLED, 1, pending=False)
                sm.GetService('FxSequencer').EnableGuids(candidateEffects)
                uicore.Message('CustomNotify', {'notify': 'All effects - On'})
            else:
                gfxsettings.Set(gfxsettings.UI_EFFECTS_ENABLED, 0, pending=False)
                sm.GetService('FxSequencer').DisableGuids(candidateEffects)
                uicore.Message('CustomNotify', {'notify': 'All effects - Off'})

    def CmdToggleEffectTurrets(self, *args):
        disabledGuids = sm.GetService('FxSequencer').GetDisabledGuids()
        if FxSequencer.fxTurretGuids[0] in disabledGuids:
            gfxsettings.Set(gfxsettings.UI_TURRETS_ENABLED, 1, pending=False)
            sm.GetService('FxSequencer').EnableGuids(FxSequencer.fxTurretGuids)
            uicore.Message('CustomNotify', {'notify': 'All Turret effects - On'})
        else:
            gfxsettings.Set(gfxsettings.UI_TURRETS_ENABLED, 0, pending=False)
            sm.GetService('FxSequencer').DisableGuids(FxSequencer.fxTurretGuids)
            uicore.Message('CustomNotify', {'notify': 'All Turret effects - Off'})

    def CmdToggleCombatView(self, *args):
        if session.solarsystemid and session.role & ROLEMASK_ELEVATEDPLAYER:
            sm.GetService('target').ToggleViewMode()

    def CmdCycleFleetBroadcastScope(self, *args):
        sm.GetService('fleet').CycleBroadcastScope()

    def CmdToggleTargetItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdToggleTargetItem')
        self.LoadCombatCommand(sm.GetService('target').ToggleLockTarget, cmd)

    def CmdLockTargetItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdLockTargetItem')
        self.LoadCombatCommand(sm.GetService('target').TryLockTarget, cmd)

    def CmdSelectTargetItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdSelectTargetItem')
        self.LoadCombatCommand(GetMenuService().SelectTarget, cmd)

    def CmdUnlockTargetItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdUnlockTargetItem')
        self.LoadCombatCommand(sm.GetService('target').UnlockTarget, cmd)

    def CmdUnlockTargetItems(self):
        sm.GetService('target').UnlockTargets()

    def CmdToggleLookAtItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdToggleLookAtItem')
        self.LoadCombatCommand(GetMenuService().ToggleLookAt, cmd)

    def CmdToggleCameraTracking(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdToggleCameraTracking')
        self.LoadCombatCommand(GetMenuService().SetInterest, cmd)

    def CmdApproachItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdApproachItem')
        if not self._IsCombatCmdAvailableToHull():
            return
        uicore.layer.inflight.positionalControl.StartMoveCommand()
        self.LoadCombatCommand(movementFunctions.Approach, cmd)
        self.combatCmdUnloadFunc = self._CmdApproacItemUnloadCallback

    def CmdGetLocationMenuForNavigation(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdGetLocationMenuForNavigation')
        self.LoadLightCombatCommand(cmd)

    CmdGetLocationMenuForNavigation.nameLabelPath = 'UI/Commands/CmdGetLocationMenuForNavigation'
    CmdGetLocationMenuForNavigation.descriptionLabelPath = 'UI/Commands/CmdGetLocationMenuForNavigationDesc'

    def CmdGetUiPointer(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdGetUiPointer')
        pointerHelper = sm.GetService('helpPointer').GetPointerOverlay(create=True)
        self.combatCmdUnloadFunc = self._CmdGetUiPointerUnloadCallback
        self.LogInfo('cmd:UI Pointer overlay: activate pointer')
        uthread.new(pointerHelper.ShowOverlay)
        self.LoadLightCombatCommand(cmd)

    CmdGetUiPointer.nameLabelPath = 'UI/Commands/CmdGetUiPointer'
    CmdGetUiPointer.descriptionLabelPath = 'UI/Commands/CmdGetUiPointerDesc'

    def _CmdGetUiPointerUnloadCallback(self, *args):
        sm.GetService('helpPointer').HidePointerOverlay()

    def _IsCombatCmdAvailableToHull(self):
        if eveCfg.IsControllingStructure():
            shipIsSelected, selectedFighterIDs = GetSelectedShipAndFighters()
            if not selectedFighterIDs:
                return False
        return True

    def _CmdApproacItemUnloadCallback(self, *args):
        posCtrl = uicore.layer.inflight.positionalControl
        if not posCtrl.IsFirstPointSet():
            posCtrl.AbortCommand()

    def CmdAlignToItem(self):
        if not self._IsCombatCmdAvailableToHull():
            return
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdAlignToItem')
        self.LoadCombatCommand(GetMenuService().AlignTo, cmd)

    def CmdOrbitItem(self):
        if not self._IsCombatCmdAvailableToHull():
            return
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdOrbitItem')
        self.LoadCombatCommand(Orbit, cmd)

    def CmdKeepItemAtRange(self):
        if not self._IsCombatCmdAvailableToHull():
            return
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdKeepItemAtRange')
        self.LoadCombatCommand(KeepAtRange, cmd)

    def CmdShowItemInfo(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdShowItemInfo')
        self.LoadCombatCommand(GetMenuService().ShowInfoForItem, cmd)

    def CmdDockOrJumpOrActivateGate(self):
        if eveCfg.IsControllingStructure():
            return
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdDockOrJumpOrActivateGate')
        self.LoadCombatCommand(DockOrJumpOrActivateGate, cmd)

    def CmdWarpToItem(self):
        if not self._IsCombatCmdAvailableToHull():
            return
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdWarpToItem')
        self.LoadCombatCommand(WarpToItem, cmd)

    def CmdOpenRadialMenu(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdOpenRadialMenu')
        self.LoadCombatCommand(None, cmd)

    def CmdOpenBroadcastRadialMenu(self):
        if not session.fleetid:
            return
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdOpenBroadcastRadialMenu')
        self.LoadCombatCommand(None, cmd)

    def CmdSendBroadcast_Target(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdSendBroadcast_Target')
        self.LoadCombatCommand(sm.GetService('fleet').SendBroadcast_Target, cmd)

    def CmdSendBroadcast_HealTarget(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdSendBroadcast_HealTarget')
        self.LoadCombatCommand(sm.GetService('fleet').SendBroadcast_Heal_Target, cmd)

    def CmdSendBroadcast_WarpToItemID(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdSendBroadcast_WarpToItemID')
        self.LoadCombatCommand(sm.GetService('fleet').SendBroadcast_WarpToItemID, cmd)

    def CmdSendBroadcast_AlignToItemID(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdSendBroadcast_AlignToItemID')
        self.LoadCombatCommand(sm.GetService('fleet').SendBroadcast_AlignToItemID, cmd)

    def CmdSendBroadcast_JumpToItemID(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdSendBroadcast_JumpToItemID')
        self.LoadCombatCommand(sm.GetService('fleet').SendBroadcast_JumpToItemID, cmd)

    def MakeCmdTagItem(self, tag):
        functionName = 'CmdTagItem_%s' % tag

        def CmdTagItem():
            if session.fleetid is None:
                return
            cmd = uicore.cmd.commandMap.GetCommandByName(functionName)

            def DoTagItem(itemID):
                if session.fleetid is None:
                    return
                self.menu.TagItem(itemID, tag)

            self.LoadCombatCommand(DoTagItem, cmd)

        CmdTagItem.__name__ = functionName
        return CmdTagItem

    def MakeCmdTagItemFromSequence(self, tagSequence):
        functionName = 'CmdTagItem_%s' % ''.join(tagSequence)

        def CmdTagItem():
            if session.fleetid is None:
                return
            cmd = uicore.cmd.commandMap.GetCommandByName(functionName)

            def DoTagItemFromSequence(itemID):
                if session.fleetid is None:
                    return
                index = self.commandMemory.get(functionName, 0)
                tag = tagSequence[index]
                index = (index + 1) % len(tagSequence)
                self.commandMemory[functionName] = index
                self.menu.TagItem(itemID, tag)

            self.LoadCombatCommand(DoTagItemFromSequence, cmd)

        CmdTagItem.__name__ = functionName
        return CmdTagItem

    def CmdToggleSensorOverlay(self):
        if eveCfg.InSpace():
            sm.GetService('sensorSuite').ToggleOverlay()

    CmdToggleSensorOverlay.nameLabelPath = 'UI/Inflight/Scanner/SensorOverlay'

    def CmdCreateBookmark(self):
        if eveCfg.InSpace():
            sm.GetService('addressbook').BookmarkCurrentLocation()

    def CmdFleetGroup(self):
        if not session.fleetid:
            return
        if session.fleetrole in appConst.fleetCmdrRoles:
            sm.GetService('fleet').Regroup()

    CmdFleetGroup.nameLabelPath = 'UI/Fleet/FleetRegroup'

    def CmdClearFleetBroadcastIcons(self):
        if not session.fleetid:
            return
        sm.GetService('fleet').ClearWatchlistBroadcastHistory()

    CmdClearFleetBroadcastIcons.nameLabelPath = 'UI/Fleet/ClearBroadcastIcons'

    def CmdFlightControlsUp(self):
        pass

    CmdFlightControlsUp.nameLabelPath = 'UI/Commands/CmdFlightControlsUp'

    def CmdFlightControlsDown(self):
        pass

    CmdFlightControlsDown.nameLabelPath = 'UI/Commands/CmdFlightControlsDown'

    def CmdFlightControlsLeft(self):
        pass

    CmdFlightControlsLeft.nameLabelPath = 'UI/Commands/CmdFlightControlsLeft'

    def CmdFlightControlsRight(self):
        pass

    CmdFlightControlsRight.nameLabelPath = 'UI/Commands/CmdFlightControlsRight'

    def CmdAimFighterAbility(self, fighterID, abiltySlotID):
        self.CmdAimMultiSquadronFighterAbilities([fighterID], abiltySlotID)

    def CmdAimMultiSquadronFighterAbilities(self, fighterIDs, abiltySlotID):
        uicore.layer.inflight.positionalControl.StartFighterAbilityTargeting(fighterIDs, abiltySlotID)

    def CmdAimWeapon(self, moduleID, effect, targetPointCount):
        uicore.layer.inflight.positionalControl.StartEffectTargeting(session.shipid, moduleID, effect, targetPointCount)

    def LoadCombatCommand(self, function, cmd):
        if not session.solarsystemid:
            return
        sm.ScatterEvent('OnFreezeOverviewWindows')
        self.combatFunctionLoaded = function
        self.combatCmdLoaded = cmd
        uicore.event.RegisterForTriuiEvents((uiconst.UI_KEYUP,
         uiconst.UI_KEYDOWN,
         uiconst.UI_ACTIVE,
         uiconst.UI_MOUSEUP), self.CombatKeyUnloadListener)
        delayMs = 300
        for key in cmd.shortcut:
            if key not in uiconst.MODKEYS:
                delayMs = 0
                break

        sm.GetService('space').SetShortcutText(cmd.GetDescription(), localization.GetByLabel('UI/Commands/ClickTarget'), delayMs)
        sm.GetService('flightPredictionSvc').CommandKeyDown(cmd.name)

    def LoadLightCombatCommand(self, cmd):
        if not session.charid:
            return
        self.combatFunctionLoaded = None
        self.combatCmdLoaded = cmd
        uicore.event.RegisterForTriuiEvents((uiconst.UI_KEYUP,
         uiconst.UI_KEYDOWN,
         uiconst.UI_ACTIVE,
         uiconst.UI_MOUSEUP), self.CombatKeyUnloadListener)
        delayMs = 300
        for key in cmd.shortcut:
            if key not in uiconst.MODKEYS:
                delayMs = 0
                break

        desc = cmd.GetDetailedDescription()
        if desc:
            desc = '<center>%s</center>' % desc
        sm.GetService('space').SetShortcutText(cmd.GetDescription(), desc, delayMs)

    def UnloadCombatCommand(self):
        uthread.new(self._UnloadCombatCommand)

    def _UnloadCombatCommand(self):
        sm.GetService('flightPredictionSvc').CommandKeyUp()
        sm.GetService('space').ClearShortcutText()
        sm.ScatterEvent('OnUnfreezeOverviewWindows')
        self.combatFunctionLoaded = None
        self.combatCmdLoaded = None
        if self.combatCmdUnloadFunc:
            self.combatCmdUnloadFunc(self.combatCmdCurrentHasExecuted)
            self.combatCmdUnloadFunc = None
        self.combatCmdCurrentHasExecuted = False

    def CombatKeyUnloadListener(self, wnd, eventID, keyChange):
        vk = keyChange[0] if keyChange else None
        if eventID == uiconst.UI_MOUSEUP and vk in (uiconst.MOUSELEFT, uiconst.MOUSERIGHT):
            return True
        if eventID == uiconst.UI_ACTIVE:
            self.UnloadCombatCommand()
            return
        if self.combatCmdLoaded is None:
            return True
        if vk not in self.combatCmdLoaded.shortcut:
            self.UnloadCombatCommand()
            return
        for key in self.combatCmdLoaded.shortcut:
            if not uicore.uilib.Key(key):
                self.UnloadCombatCommand()
                return

        return True

    def ExecuteCombatCommand(self, itemID, eventID, **kwargs):
        if itemID is None or self.combatFunctionLoaded is None:
            return False
        if eventID == uiconst.UI_KEYUP and self.combatCmdCurrentHasExecuted:
            self.UnloadCombatCommand()
            return True
        self.combatCmdCurrentHasExecuted = True
        self.ExecuteActiveCombatCommand(itemID, **kwargs)
        return True

    def ExecuteActiveCombatCommand(self, itemID, **kwargs):
        uthread.new(self.combatFunctionLoaded, itemID, **kwargs)

    def IsSomeCombatCommandLoaded(self):
        return self.combatFunctionLoaded is not None

    def IsCombatCommandLoaded(self, cmdName):
        return self.combatCmdLoaded == self.commandMap.GetCommandByName(cmdName)

    def GetCombatCmdLoadedName(self):
        return self.combatCmdLoaded

    def CmdForceFadeFromBlack(self, *args):
        loadSvc = sm.GetService('loading')
        if loadSvc.IsLoading():
            loadSvc.FadeOut(100)

    def Reset(self, resetKey):
        if resetKey == 'windows':
            GetDockPanelManager().ResetAllPanelSettings()
            sm.GetService('window').ResetWindowSettings()
        elif resetKey == 'window color':
            sm.GetService('uiColor').ResetUIColors()
        elif resetKey == 'clear cache':
            sm.GetService('gameui').ClearCacheFiles()
        elif resetKey == 'clear iskspammers':
            sm.GetService('chat').clear_reported_spammers()
        elif resetKey == 'clear settings':
            sm.GetService('gameui').ClearSettings()
        elif resetKey == 'clear mail':
            sm.GetService('mailSvc').ClearMailCache()
        elif resetKey == 'reset neocom':
            ResetNeocomButtons()

    def CmdToggleSystemMenu(self):
        systemMenu = uicore.layer.systemmenu
        if systemMenu.isopen:
            sm.GetService('uipointerSvc').RevealPointers()
            uthread.new(systemMenu.CloseMenu)
        else:
            sm.GetService('uipointerSvc').SuppressPointers()
            uthread.new(systemMenu.OpenView)

    CmdToggleSystemMenu.nameLabelPath = 'UI/Login/Settings'

    def OnEsc(self, *args):
        escapeAdaptor = EscapeCommandAdapter()
        escCommand = EscapeCommand(viewStateSrvc=sm.GetService('viewState'), adaptor=escapeAdaptor, dockPanelManager=GetDockPanelManager())
        escCommand.Execute()

    def OnTab(self):
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            uicore.registry.FindFocus(-1)
        else:
            uicore.registry.FindFocus(1)

    def MapCmd(self, cmdname, context):
        self.commandMap.UnloadAllAccelerators()
        wnd = MapCmdWindow.Open(cmdname=cmdname)
        modalResult = wnd.ShowModal()
        self.LoadAllAccelerators()
        if modalResult == 1:
            retval = wnd.result
            shortcut = retval['shortcut']
        else:
            return
        errorMsg, canOverride = self.MapCmdErrorCheck(cmdname, shortcut, context)
        doOverride = False
        if errorMsg:
            if canOverride:
                questionText = localization.GetByLabel('UI/Commands/ShortcutAlreadyUsedReassign', usedText=errorMsg, cmd=self.GetStringFromShortcutKeys(shortcut), newFunc=uicore.cmd.FuncToDesc(cmdname))
                questionHeader = localization.GetByLabel('UI/Commands/ShortcutAlreadyUsedReassignHeader')
                reassingID = -1
                buttons = [Bunch(id=reassingID, label=localization.GetByLabel('UI/Commands/ReassingCmd')), Bunch(id=uiconst.ID_CANCEL, label=localization.GetByLabel('UI/Common/Buttons/Cancel'))]
                ret = eve.Message('CustomQuestion', {'question': questionText,
                 'header': questionHeader}, buttons=buttons)
                if ret == reassingID:
                    doOverride = True
                else:
                    return self.MapCmd(cmdname, context)
            else:
                eve.Message('CustomInfo', {'info': errorMsg})
                return self.MapCmd(cmdname, context)
        alreadyUsing = self.commandMap.GetCommandByShortcut(shortcut)
        if alreadyUsing is not None:
            alreadyUsingContext = self.__categoryToContext__[alreadyUsing.category]
            if alreadyUsingContext not in self.contextToCommand:
                self.contextToCommand[alreadyUsingContext] = {}
            self.contextToCommand[alreadyUsingContext][shortcut] = alreadyUsing
        if alreadyUsing and doOverride:
            self.ClearMappedCmd(alreadyUsing.name)
        self.commandMap.RemapCommand(cmdname, shortcut)
        if context not in self.contextToCommand:
            self.contextToCommand[context] = {}
        self.ClearContextToCommandMapping(context, cmdname)
        self.contextToCommand[context][shortcut] = self.commandMap.GetCommandByName(cmdname)
        sm.ScatterEvent('OnMapShortcut', cmdname, shortcut)

    def ClearContextToCommandMapping(self, context, cmdname):
        toDeleteShortcut = None
        for shortcutKey, command in self.contextToCommand[context].iteritems():
            if command.name == cmdname:
                toDeleteShortcut = shortcutKey

        if toDeleteShortcut is not None:
            del self.contextToCommand[context][toDeleteShortcut]

    def MapCmdErrorCheck(self, cmdname, shortcut, context):
        if not shortcut:
            return (localization.GetByLabel('UI/Commands/ChooseAKeyPrompt'), False)
        for key in shortcut:
            keyName = self.GetKeyNameFromVK(key)
            if not getattr(uiconst, 'VK_%s' % keyName.upper(), None):
                eve.Message('UnknownKey', {'key': keyName})
                return ('', False)

        extraShortcutRulesForCmd = self.GetExtraShortcutRulesForCmd(cmdname)
        if extraShortcutRulesForCmd:
            notAllowedWithModifiers = extraShortcutRulesForCmd.get(RULE_NOT_ALLOWED_WITH_MODIFIERS, None)
            if notAllowedWithModifiers and len(shortcut) > 1 and set.intersection(set(shortcut), set(notAllowedWithModifiers)):
                cmd = labelsByFuncName.get(cmdname, None)
                cmdText = localization.GetByLabel(cmd) if cmd else cmdname
                listOfKeys = '<br>'.join([ command.GetKeyName(x) for x in notAllowedWithModifiers ])
                return (localization.GetByLabel('UI/Commands/ShortcutKeyNotAllowedWithModifiers', cmd=cmdText, listOfKeys=listOfKeys), False)
        alreadyUsing = self.commandMap.GetCommandByShortcut(shortcut)
        if alreadyUsing:
            cmdEdit = self.commandMap.GetCommandByName(cmdname)
            alreadyUsingContext = self.__categoryToContext__[alreadyUsing.category]
            cmdEditContext = self.__categoryToContext__[cmdEdit.category]
            sameContext = self.CheckContextIntersection(alreadyUsingContext, cmdEditContext)
            if sameContext and alreadyUsing.name != cmdname:
                canOverride = not alreadyUsing.isLocked
                errorText = localization.GetByLabel('UI/Commands/ShortcutAlreadyUsedByCmd', cmd=alreadyUsing.GetShortcutAsString(), category=localization.GetByLabel(CATEGORIES[alreadyUsing.category]), func=alreadyUsing.GetDescription())
                return (errorText, canOverride)
        if context in self.contextToCommand and shortcut in self.contextToCommand[context]:
            alreadyUsing = self.contextToCommand[context][shortcut]
            canOverride = not alreadyUsing.isLocked
            errorText = localization.GetByLabel('UI/Commands/ShortcutAlreadyUsedByCmd', cmd=alreadyUsing.GetShortcutAsString(), category=localization.GetByLabel(CATEGORIES[alreadyUsing.category]), func=alreadyUsing.GetDescription())
            return (errorText, canOverride)
        return ('', False)

    def ClearMappedCmd(self, cmdname, showMsg = 1):
        command = self.commandMap.GetCommandByName(cmdname)
        context = self.__categoryToContext__[command.category]
        if context in self.contextToCommand:
            self.ClearContextToCommandMapping(context, cmdname)
        CommandService.ClearMappedCmd(self, cmdname, showMsg)

    def CmdPickPortrait0(self, *args):
        self.PickPortrait(0)

    def CmdPickPortrait1(self, *args):
        self.PickPortrait(1)

    def CmdPickPortrait2(self, *args):
        self.PickPortrait(2)

    def CmdPickPortrait3(self, *args):
        self.PickPortrait(3)

    def PickPortrait(self, portraitID):
        uicore.layer.charactercreation.controller.PickPortrait(portraitID)

    def GetCommandToExecute(self, cmdName, *args, **kwargs):
        cmd = self.commandMap.GetCommandByName(cmdName)
        if cmd:
            return lambda : self.ExecuteCommand(cmd, *args, **kwargs)

    def GetCommandAndExecute(self, cmdName, *args, **kwargs):
        cmd = self.commandMap.GetCommandByName(cmdName)
        self.ExecuteCommand(cmd, *args, **kwargs)

    def ExecuteCommand(self, cmd, *args, **kwargs):
        if not self.IsCommandEnabled(cmd):
            return
        if cmd.category in ('window', 'modules', 'drones'):
            PlaySound(uiconst.SOUND_BUTTON_CLICK)
        return cmd.callback(*args, **kwargs)

    def IsCommandEnabled(self, command):
        references = ['cmd', 'cmd.name.{}'.format(command.name), 'cmd.category.{}'.format(command.category)]
        if self.command_blocker.is_blocked(references):
            return False
        return command.name not in self.disabledCommands

    def EnableCommand(self, commandName):
        self.disabledCommands.discard(commandName)

    def DisableCommand(self, commandName):
        self.disabledCommands.add(commandName)

    def EnableAllCommands(self):
        self.disabledCommands.clear()

    def DisableAllCommands(self):
        for command in self.commandMap.GetAllCommands():
            self.disabledCommands.add(command.name)

    def CmdSetDefenceStance(self, *args):
        self._SetStance(shipmode.data.shipStanceDefense)

    def CmdSetSniperStance(self, *args):
        self._SetStance(shipmode.data.shipStanceSniper)

    def CmdSetSpeedStance(self, *args):
        self._SetStance(shipmode.data.shipStanceSpeed)

    def _SetStance(self, stanceID):
        if eveCfg.InShip():
            clientDL = sm.GetService('clientDogmaIM').GetDogmaLocation()
            ship = clientDL.SafeGetDogmaItem(clientDL.GetActiveShipID(session.charid))
            set_stance(stanceID, ship.itemID, ship.typeID)

    def CmdIncreaseProbeScanRange(self, *args):
        if eveCfg.InSpace():
            if ProbeScannerWindow.GetIfOpen():
                sm.GetService('scanSvc').ScaleFormation(2.0)
            elif IsProbeScanEmbeddedPanelOpen():
                sm.GetService('scanSvc').ScaleFormation(2.0)
            return True

    CmdIncreaseProbeScanRange.nameLabelPath = 'UI/Commands/CmdIncreaseProbeScanRange'

    def CmdDecreaseProbeScanRange(self, *args):
        if eveCfg.InSpace():
            if ProbeScannerWindow.GetIfOpen():
                sm.GetService('scanSvc').ScaleFormation(0.5)
            elif IsProbeScanEmbeddedPanelOpen():
                sm.GetService('scanSvc').ScaleFormation(0.5)
            return True

    CmdDecreaseProbeScanRange.nameLabelPath = 'UI/Commands/CmdDecreaseProbeScanRange'

    def CmdRefreshProbeScan(self, *args):
        if eveCfg.InSpace():
            from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow
            probeScanWindow = ProbeScannerWindow.GetIfOpen()
            if probeScanWindow:
                probeScanWindow.Confirm()
            else:
                scanWindow = SolarSystemViewPanel.GetIfOpen()
                if scanWindow and IsProbeScanEmbeddedPanelOpen():
                    scanWindow.mapView.probeScannerPalette.Confirm()
            return True

    CmdRefreshProbeScan.nameLabelPath = 'UI/Commands/CmdRefreshProbeScan'

    def CmdRefreshDirectionalScan(self, *args):
        if not eveCfg.InSpace():
            return
        if not IsDirectionalScannerOpen():
            self.OpenDirectionalScanner()
        else:
            cmd = uicore.cmd.commandMap.GetCommandByName('CmdRefreshDirectionalScan')
            scanSvc = sm.GetService('directionalScanSvc')
            self.LoadCombatCommand(scanSvc.ScanTowardsItem, cmd)
            self.combatCmdUnloadFunc = scanSvc.OnCmdDirectionalScanUnload
            scanSvc.OnCmdDirectionalScanLoad()

    CmdRefreshDirectionalScan.nameLabelPath = 'UI/Commands/CmdRefreshDirectionalScan'

    def CmdToggleAutoTracking(self, *args):
        if not session.solarsystemid:
            return
        settings.char.ui.Set('orbitCameraAutoTracking', not IsAutoTrackingEnabled())

    CmdToggleAutoTracking.nameLabelPath = 'UI/Commands/CmdToggleAutoTracking'

    def OpenPointerWnd(self):
        if not ArePointerLinksActive(sm.GetService('machoNet')):
            return
        PointerToolWnd.Open()

    OpenPointerWnd.nameLabelPath = PointerToolWnd.default_captionLabelPath
    OpenPointerWnd.descriptionLabelPath = PointerToolWnd.default_descriptionLabelPath

    def OpenContextualOffersWindow(self):
        sm.GetService('contextualOfferSvc').OpenContextualOffersWindow()

    OpenContextualOffersWindow.nameLabelPath = 'UI/ContextualOffers/OfferTitle'
    OpenContextualOffersWindow.descriptionLabelPath = 'UI/ContextualOffers/OfferSubcaption'

    def ToggleCurrentSystemLocationWnd(self):
        if not session.solarsystemid2:
            return
        StandaloneBookmarkWnd.ToggleOpenClose()

    ToggleCurrentSystemLocationWnd.nameLabelPath = 'UI/AclBookmarks/OpenBookmarkStandaloneWindow'

    def IsCommandAllowed(self, cmdName):
        return True

    def _IsZhGiftCodeAvailable(self):
        return AmOnChineseServer()

    def GetCSMVotingURL(self):
        return self.machoNet.GetGlobalConfig().get('CSMVotingURL', 'https://community.eveonline.com/community/csm/vote/')

    def OpenCSMVoting(self):
        try:
            CSMVoteURL = self.GetCSMVotingURL()
            blue.os.ShellExecute(CSMVoteURL)
        except Exception:
            LogException('Failed to open URL to access CSM voting')
            raise UserError('FailedToOpenCSMVotingURL')

    def GetEVEPortalLandingURL(self):
        return self.machoNet.GetGlobalConfig().get('CSMVotingURL', 'https://www.eveonline.com/eve-portal')

    def OpenEVEPortalLandingPage(self):
        try:
            EVEPortalLandingURL = self.GetEVEPortalLandingURL()
            blue.os.ShellExecute(EVEPortalLandingURL)
        except Exception:
            LogException('Failed to open URL to access EVE Portal landing page')
            raise UserError('FailedToOpenEVEPortalLandingURL')

    def GetEVEAcademyLandingPageURL(self):
        return self.machoNet.GetGlobalConfig().get('AcademyLandingPageURL', 'https://www.eveonline.com/now/eve-academy')

    def OpenEVEAcademyLandingPage(self):
        try:
            EVEAcademyLandingURL = self.GetEVEAcademyLandingPageURL()
            blue.os.ShellExecute(EVEAcademyLandingURL)
        except Exception:
            LogException('Failed to open URL to access EVE Academy landing page')
            raise UserError('FailedToOpenEVEAcademyLandingURL')

    def GetCSMCandidateInfoURL(self):
        return self.machoNet.GetGlobalConfig().get('CSMCandidateInfoURL', 'https://www.eveonline.com/news/view/csm-17-meet-your-candidates')

    def OpenCSMCandidateInfo(self):
        try:
            CSMCandidateInfoURL = self.GetCSMCandidateInfoURL()
            blue.os.ShellExecute(CSMCandidateInfoURL)
        except Exception:
            LogException('Failed to open URL to access CSM Candidate Info')
            raise UserError('FailedToOpenCSMVotingURL')

    def GetUprisingPatchNotesURL(self):
        return self.machoNet.GetGlobalConfig().get('UprisingPatchNotesURL', 'https://www.eveonline.com/news/view/patch-notes-version-20-10')

    def OpenUprisingPatchNotes(self):
        try:
            UprisingPatchNotesURL = self.GetUprisingPatchNotesURL()
            blue.os.ShellExecute(UprisingPatchNotesURL)
        except Exception:
            LogException('Failed to open URL to access Uprising Patch Notes')
            raise UserError('FailedToOpenUprisingPatchNotesURL')
