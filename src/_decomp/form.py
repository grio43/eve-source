#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\modules\nice\client\_nastyspace\form.py
from eve.devtools.script.uiAnimationTest import TestAnimationsWnd as UIAnimationTest
from eve.client.script.ui.shared.neocom.addressBook.manageLabels import ManageLabels
from eve.devtools.script.uiDebugger import UIDebugger
from eve.devtools.script.uiEventListener import UIEventListener
from eve.client.script.ui.control.listgroup import VirtualGroupWindow
from eve.client.script.ui.control.listwindow import ListWindow
from eve.client.script.ui.control.scenecontainer import SceneContainer
from eve.client.script.ui.control.scenecontainer import SceneContainerBaseNavigation
from eve.client.script.ui.control.scenecontainer import SceneContainerBrackets
from eve.client.script.ui.control.scenecontainer import SceneWindowTest
from eve.client.script.ui.extras.tourneyBanUI import TourneyBanUI
from eve.client.script.ui.hacking.hackingWindow import HackingWindow
from eve.client.script.ui.inflight.capitalnavigation import CapitalNav
from eve.client.script.ui.inflight.dungeoneditor import DungeonEditor
from eve.client.script.ui.inflight.dungeoneditor import DungeonObjectProperties
from eve.client.script.ui.inflight.facilityTaxWindow import FacilityTaxWindow
from eve.client.script.ui.inflight.moonmining import MoonMining
from eve.client.script.ui.inflight.moonmining import SelectSiloType
from eve.client.script.ui.inflight.orbitalConfiguration import OrbitalConfigurationWindow
from eve.client.script.ui.inflight.scannerfiltereditor import ScannerFilterEditor
from eve.client.script.ui.inflight.shipscan import CargoScan
from eve.client.script.ui.inflight.shipscan import ShipScan
from eve.client.script.ui.inflight.surveyscan import SurveyScanView
from eve.client.script.ui.login.loginII import Login as LoginII
from eve.client.script.ui.mapCmdWindow import MapCmdWindow
from eve.client.script.ui.services.bugReporting import BugReportingWindow
from eve.client.script.ui.services.bugReporting import ScreenshotEditingWnd
from eve.client.script.ui.services.flightPredictionSvc import FlightPredictionTestWindow
from eve.client.script.ui.shared.info.infoWindow import EntityWindow
from eve.client.script.ui.shared.portraitWindow.portraitWindow import PortraitWindow
from eve.client.script.ui.shared.info.infosvc import InfoWindow as infowindow
from eve.client.script.ui.shared.redeem.window import GetRedeemWindow
from eve.client.script.ui.shared.abyss.keyActivationWindow import KeyActivationWindow as keyActivationWindow
from eve.client.script.ui.shared.abyss.AbyssJumpWindow import AbyssActivationWindow as abyssActivationWindow
from eve.client.script.ui.shared.AuditLogSecureContainerLogViewer import AuditLogSecureContainerLogViewer
from eve.client.script.ui.shared.activateMultiTraining import ActivateMultiTrainingWindow
from eve.client.script.ui.shared.assetsWindow import AssetsWindow
from eve.client.script.ui.shared.autopilotSettings import AutopilotSettings
from eve.client.script.ui.shared.bountyWindow import BountyPicker
from eve.client.script.ui.shared.bountyWindow import BountyWindow
from eve.client.script.ui.shared.ctrltab import CtrlTabWindow
from eve.client.script.ui.shared.dynamicItem.craftingWindow import CraftingWindow
from eve.client.script.ui.shared.eveCalendar import CalendarNewEventWnd
from eve.client.script.ui.shared.eveCalendar import CalendarSingleDayWnd
from eve.client.script.ui.shared.eveCalendar import Calendar as eveCalendar
from eve.client.script.ui.shared.eveCalendar import CalendarWnd as eveCalendarWnd
from eve.client.script.ui.shared.export import ExportBaseWindow
from eve.client.script.ui.shared.export import ExportFittingsWindow
from eve.client.script.ui.shared.export import ExportOverviewWindow
from eve.client.script.ui.shared.export import ImportBaseWindow
from eve.client.script.ui.shared.export import ImportFittingsWindow
from eve.client.script.ui.shared.export import ImportLegacyFittingsWindow
from eve.client.script.ui.shared.export import ImportOverviewWindow
from eve.client.script.ui.shared.factionalWarfare.infrastructureHub import FWInfrastructureHub
from eve.client.script.ui.shared.fittingMgmtWindow import FittingMgmt
from eve.client.script.ui.shared.fleet.fleet import WatchListPanel
from eve.client.script.ui.shared.fleet.fleetbroadcast import BroadcastSettings
from eve.client.script.ui.shared.fleet.fleetregister import RegisterFleetWindow
from eve.client.script.ui.shared.fleet.fleetJoinRequestWnd import FleetJoinRequestWindow
from eve.client.script.ui.shared.inventory.filterSvc import FilterCreationWindow
from eve.client.script.ui.shared.inventory.invWindow import ActiveShipCargo
from eve.client.script.ui.shared.inventory.invWindow import Inventory
from eve.client.script.ui.shared.inventory.invWindow import InventoryPrimary
from eve.client.script.ui.shared.inventory.invWindow import StationCorpDeliveries
from eve.client.script.ui.shared.inventory.invWindow import StationCorpHangars
from eve.client.script.ui.shared.inventory.invWindow import StationItems
from eve.client.script.ui.shared.inventory.invWindow import StationShips
from eve.client.script.ui.shared.killReport import KillReportWnd
from eve.client.script.ui.shared.killRights import SellKillRightWnd
from eve.client.script.ui.shared.maps.browserwindow import MapBrowserWnd
from eve.client.script.ui.shared.maps.palette import MapPalette as MapsPalette
from eve.client.script.ui.shared.market.marketbase import MarketBase as Market
from eve.client.script.ui.shared.market.marketbase import MarketData
from eve.client.script.ui.shared.market.marketbase import RegionalMarket
from eve.client.script.ui.shared.market.sellMulti import SellItems
from eve.client.script.ui.shared.medalribbonranks import MedalRibbonPickerWindow
from eve.client.script.ui.shared.messagebox import MessageBox
from eve.client.script.ui.shared.neocom.Alliances.all_ui_alliances import FormAlliances as Alliances
from eve.client.script.ui.shared.neocom.Alliances.all_ui_applications import FormAlliancesApplications as AlliancesApplications
from eve.client.script.ui.shared.neocom.Alliances.all_ui_applications import ApplyToAllianceWnd
from eve.client.script.ui.shared.neocom.Alliances.all_ui_applications import MyAllianceApplicationWnd
from eve.client.script.ui.shared.neocom.Alliances.all_ui_home import FormAlliancesBulletins as AlliancesBulletins
from eve.client.script.ui.shared.neocom.Alliances.all_ui_home import CreateAllianceWnd
from eve.client.script.ui.shared.neocom.Alliances.all_ui_home import EditAllianceWnd
from eve.client.script.ui.shared.neocom.Alliances.all_ui_home import SetShortNameWnd
from eve.client.script.ui.shared.neocom.Alliances.all_ui_members import FormAlliancesMembers as AlliancesMembers
from eve.client.script.ui.shared.neocom.Alliances.all_ui_rankings import FormAlliancesRankings as AlliancesRankings
from eve.client.script.ui.shared.neocom.addressBook.contactManagementMultiEditWindow import ContactManagementMultiEditWnd
from eve.client.script.ui.shared.neocom.addressBook.contactManagementWindow import ContactManagementWnd
from eve.client.script.ui.shared.neocom.addressBook.corpAllianceContactManagementWindow import CorpAllianceContactManagementWnd
from eve.client.script.ui.shared.neocom.attributes import AttributeRespecWindow as attributeRespecWindow
from eve.client.script.ui.shared.neocom.calculator import Calculator
from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow as CharacterSheet
from eve.client.script.ui.shared.neocom.contracts.contractsDetailsWnd import ContractDetailsWindow
from eve.client.script.ui.shared.neocom.contracts.contractsWnd import ContractsWindow
from eve.client.script.ui.shared.neocom.contracts.createContractWnd import CreateContractWnd
from eve.client.script.ui.shared.neocom.contracts.ignoreListWnd import IgnoreListWindow
from eve.client.script.ui.shared.neocom.corporation.corp_dlg_edit_member import EditMemberDialog
from eve.client.script.ui.shared.neocom.corporation.corp_ui_applications import ApplyToCorpWnd
from eve.client.script.ui.shared.neocom.corporation.corp_ui_applications import MyCorpApplicationWnd
from eve.client.script.ui.shared.neocom.corporation.corp_ui_applications import InviteToCorpWnd
from eve.client.script.ui.shared.neocom.corporation.corp_ui_applications import RejectCorpApplicationWnd
from eve.client.script.ui.shared.neocom.corporation.corp_ui_applications import ViewCorpApplicationWnd
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_decorations import CorpDecorations
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_find import CorpFindMembersInRole
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_newroles import CorpRolesNew
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_titles import CorpTitles
from eve.client.script.ui.shared.neocom.corporation.corp_ui_sanctionableactions import CorpSanctionableActions
from eve.client.script.ui.shared.neocom.corporation.war.corporationOrAlliancePickerDailog import CorporationOrAlliancePickerDailog
from eve.client.script.ui.shared.neocom.corporation.corp_ui_votes import CorpVotes
from eve.client.script.ui.shared.neocom.corporation.corp_ui_votes import VoteWizardDialog
from eve.client.script.ui.shared.neocom.corporation.corp_ui_votes import WizardDialogBase
from eve.client.script.ui.shared.neocom.corporation.corp_ui_wars import CorpWars
from eve.client.script.ui.shared.neocom.corporation.war.warReport import WarReportWnd
from eve.client.script.ui.shared.neocom.corporation.war.allyWnd import AllyWnd
from eve.client.script.ui.shared.neocom.corporation.war.warWindows import WarAssistanceOfferWnd
from eve.client.script.ui.shared.neocom.corporation.war.warWindows import WarSurrenderWnd
from eve.client.script.ui.shared.neocom.evemail import MailSearchWindow
from eve.client.script.ui.shared.neocom.evemail import MailForm
from eve.client.script.ui.shared.neocom.evemail import MailReadingWnd
from eve.client.script.ui.shared.neocom.evemail import MailSettings
from eve.client.script.ui.shared.neocom.evemail import MailWindow
from eve.client.script.ui.shared.neocom.evemail import MailinglistWnd
from eve.client.script.ui.shared.neocom.evemail import ManageLabelsBase
from eve.client.script.ui.shared.neocom.evemail import ManageLabelsExistingMails
from eve.client.script.ui.shared.neocom.evemail import ManageLabelsNewMails
from eve.client.script.ui.shared.neocom.evemail import NewNewMessage
from eve.client.script.ui.shared.neocom.evemailingListConfig import MaillistSetupWindow
from eve.client.script.ui.shared.neocom.journal import JournalWindow as Journal
from eve.client.script.ui.shared.neocom.notepad import NotepadWindow as Notepad
from eve.client.script.ui.shared.neocom.notifications import NotificationForm
from eve.client.script.ui.shared.neocom.ownerSearch import OwnerSearchWindow
from eve.client.script.ui.shared.planet.depletionPinManager import DepletionManager
from eve.client.script.ui.shared.planet.expeditedTransferUI import ExpeditedTransferManagementWindow
from eve.client.script.ui.shared.planet.importExportUI import PlanetaryImportExportUI
from eve.client.script.ui.shared.planet.orbitalMaterialUI import OrbitalMaterialUI
from eve.client.script.ui.shared.planet.planetWindow import PlanetWindow
from eve.client.script.ui.shared.planet.surveyUI import SurveyWindow as PlanetSurvey
from eve.client.script.ui.shared.preview import PreviewWnd
from eve.client.script.ui.shared.preview import PreviewCharacterWnd
from eve.client.script.ui.shared.shipconfig import ShipConfig
from eve.client.script.ui.shared.systemMenu.systemmenu import SystemMenu
from eve.client.script.ui.shared.uilog import LoggerWindow as Logger
from eve.client.script.ui.skilltrading.skillExtractorWindow import SkillExtractorWindow
from eve.client.script.ui.station.agents.agentDialogueWindow import AgentDialogueWindow
from eve.client.script.ui.station.assembleModularShip import AssembleShip
from eve.client.script.ui.station.base import StationLayer
from eve.client.script.ui.station.insurance.base_insurance import InsuranceWindow
from eve.client.script.ui.station.pvptrade.pvptradewnd import PVPTrade
from eve.client.script.ui.station.repairshop.base_repairshop import RepairShopWindow
from eve.client.script.ui.util.gradientEdit import GradientEditor
from eve.client.script.ui.util.namedPopup import NamePopupWnd
from eve.devtools.script.colors import ColorPicker as UIColorPicker
from eve.devtools.script.connectiontest import ConnectionLoopTest as ConnLoop
from eve.devtools.script.form_sounds import InsiderSoundPlayer
from eve.devtools.script.form_tournament import TournamentWindow as tournament
from eve.devtools.script.form_viewer import BinkVideoViewer as InsiderBinkVideoViewer
from eve.devtools.script.svc_ballparkExporter import BallparkExporter
from eve.devtools.script.svc_dgmattr import AttributeInspector
from eve.devtools.script.svc_invtools import InvToolsWnd as invTools
from eve.devtools.script.svc_poser import AssembleWindow
from eve.devtools.script.svc_poser import FuelWindow
from eve.devtools.script.svc_settingsMgr import SettingsMgr
from eve.devtools.script.tournamentRefereeTools import RefWindowSpawningWindow
from eve.devtools.script.tournamentRefereeTools import TournamentRefereeTool
from eve.devtools.script.uiScaling import UIScaling
from eve.devtools.script.uiSpriteTest import UISpriteTest
from eve.devtools.script.windowManager import WindowManager
from reprocessing.ui.reprocessingWnd import ReprocessingWnd
