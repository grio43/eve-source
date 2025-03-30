#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\btnData\btnDataRaw.py
import eveicon
import neocom2.btnIDs as btnIDs
from eve.client.script.ui.cosmetics.ship.shipSKINRWindow import ShipSKINRWindow
from eve.client.script.ui.shared.addressBookWindow import AddressBookWindow
from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
from eve.client.script.ui.shared.assetsWindow import AssetsWindow
from eve.client.script.ui.shared.bountyWindow import BountyWindow
from eve.client.script.ui.shared.careerPortal.careerPortalWnd import CareerPortalDockablePanel
from eve.client.script.ui.shared.eveCalendar import CalendarWnd
from eve.client.script.ui.shared.fittingMgmtWindow import FittingMgmt
from eve.client.script.ui.shared.fittingScreen.fittingWnd import FittingWindow
from eve.client.script.ui.shared.fleet.fleetwindow import FleetWindow
from eve.client.script.ui.shared.industry.industryWnd import Industry
from eve.client.script.ui.shared.inventory.invWindow import InventoryPrimary, PlexVaultWindow, StationCorpHangars, StationCorpDeliveries
from eve.client.script.ui.shared.ledger.ledgerWnd import LedgerWindow
from eve.client.script.ui.shared.loginRewards.loginRewardsWnd import DailyLoginRewardsWnd
from eve.client.script.ui.shared.mapView.mapViewPanel import MapViewPanel
from eve.client.script.ui.shared.market.buyMultiFromBase import MultiBuy
from eve.client.script.ui.shared.market.marketOrdersWnd import MarketOrdersWnd
from eve.client.script.ui.shared.market.marketbase import RegionalMarket
from eve.client.script.ui.shared.neocom.calculator import Calculator
from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
from eve.client.script.ui.shared.neocom.compare import TypeCompare
from eve.client.script.ui.shared.neocom.contracts.contractsWnd import ContractsWindow
from eve.client.script.ui.shared.neocom.corporation.corporationWindow import CorporationWindow
from eve.client.script.ui.shared.neocom.evemail import MailWindow
from eve.client.script.ui.shared.neocom.help import HelpWindow
from eve.client.script.ui.shared.neocom.journal import JournalWindow
from eve.client.script.ui.shared.neocom.locations.window import LocationsWindow
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.notepad import NotepadWindow
from eve.client.script.ui.shared.neocom.wallet.walletWnd import WalletWindow
from eve.client.script.ui.shared.planet.mecDen.mercDenWnd import MyMercDensWnd
from eve.client.script.ui.shared.planet.planetWindow import PlanetWindow
from eve.client.script.ui.shared.pointerTool.pointerWnd import PointerToolWnd
from eve.client.script.ui.shared.shipTree.shipTreeDockablePanel import ShipTreeDockablePanel
from eve.client.script.ui.shared.uilog import LoggerWindow
from eve.client.script.ui.skillPlan.skillPlanDockablePanel import SkillPlanDockablePanel
from eve.client.script.ui.station.securityOfficeWindow import SecurityOfficeWindow
from eve.client.script.ui.structure.accessGroups.accesGroupsWnd import AccessGroupsWnd
from eve.client.script.ui.structure.structureBrowser.structureBrowserWnd import StructureBrowserWnd
from eve.client.script.ui.view.aurumstore.AurumStoreNeocomClass import AurumStoreNeocomClass
from eve.client.script.ui.view.settingsNeocomClass import SettingsNeocomClass
from fwwarzone.client.dashboard.fwWarzoneDashboard import FwWarzoneDashboard
from jobboard.client.ui.job_board_window import JobBoardWindow
from pirateinsurgency.client.dashboard.dashboard import InsurgentsDashboard
from projectdiscovery.client.windowclass import get_project_discovery_window_class
from pvpFilaments.client import PVPFilamentEventWindow
from raffles.client import RaffleWindow
from xmppchatclient.xmppchatchannels import XmppChatChannels
from chat.client.window import BaseChatWindow

class BtnDataRaw:

    def __init__(self, label = None, cmdName = None, iconPath = None, wndCls = None):
        self.label = label
        self.cmdName = cmdName
        self.iconPath = iconPath
        self.wndCls = wndCls


BTNDATARAW_BY_ID = {btnIDs.ADDRESSBOOK_ID: BtnDataRaw(cmdName='OpenPeopleAndPlaces', wndCls=AddressBookWindow),
 btnIDs.AIR_CAREER_PROGRAM_ID: BtnDataRaw(label='CareerPortalWnd', cmdName='CmdToggleAirCareerProgram', iconPath='res:/ui/texture/windowIcons/airCareerProgram.png', wndCls=CareerPortalDockablePanel),
 btnIDs.ASSETS_ID: BtnDataRaw(cmdName='OpenAssets', wndCls=AssetsWindow),
 btnIDs.BOUNTY_OFFICE_ID: BtnDataRaw(cmdName='OpenBountyOffice', wndCls=BountyWindow),
 btnIDs.CALCULATOR_ID: BtnDataRaw(cmdName='OpenCalculator', wndCls=Calculator),
 btnIDs.CALENDAR_ID: BtnDataRaw(cmdName='OpenCalendar', wndCls=CalendarWnd),
 btnIDs.CHARACTER_SHEET_ID: BtnDataRaw(cmdName='OpenCharactersheet', wndCls=CharacterSheetWindow),
 btnIDs.CHAT_ID: BtnDataRaw(wndCls=BaseChatWindow, label='UI/Chat/ChannelWindow/Channels'),
 btnIDs.CHAT_CHANNELS_ID: BtnDataRaw(cmdName='OpenChannels', wndCls=XmppChatChannels),
 btnIDs.CONTRACTS_ID: BtnDataRaw(cmdName='OpenContracts', wndCls=ContractsWindow),
 btnIDs.CORP_ID: BtnDataRaw(cmdName='OpenCorporationPanel', wndCls=CorporationWindow),
 btnIDs.FITTING_ID: BtnDataRaw(cmdName='OpenFitting', wndCls=FittingWindow),
 btnIDs.FITTING_MGMT_ID: BtnDataRaw(cmdName='OpenFittingMgmt', wndCls=FittingMgmt),
 btnIDs.FLEET_ID: BtnDataRaw(cmdName='OpenFleet', wndCls=FleetWindow),
 btnIDs.GROUP_BTN_ID: BtnDataRaw(label='UI/Neocom/ButtonGroup', iconPath=neocomConst.ICONPATH_GROUP),
 btnIDs.GROUP_ACTIVITIES_ID: BtnDataRaw(label='UI/Neocom/GroupActivities', iconPath='res:/UI/Texture/WindowIcons/directoryActivities.png'),
 btnIDs.GROUP_INDUSTRY_ID: BtnDataRaw(label='UI/Neocom/GroupIndustry', iconPath='res:/UI/Texture/WindowIcons/directoryIndustry.png'),
 btnIDs.GROUP_INVENTORY_ID: BtnDataRaw(label='UI/Neocom/GroupInventory', iconPath='res:/UI/Texture/WindowIcons/directoryInventory.png'),
 btnIDs.GROUP_FINANCE_ID: BtnDataRaw(label='UI/Neocom/GroupFinance', iconPath='res:/UI/Texture/WindowIcons/directoryMarket.png'),
 btnIDs.GROUP_PERSONAL_ID: BtnDataRaw(label='UI/Neocom/GroupPersonal', iconPath='res:/UI/Texture/WindowIcons/directoryPersonal.png'),
 btnIDs.GROUP_SHIP_ID: BtnDataRaw(label='UI/Neocom/GroupShip', iconPath='res:/UI/Texture/WindowIcons/directoryShip.png'),
 btnIDs.GROUP_SOCIAL_ID: BtnDataRaw(label='UI/Neocom/GroupSocial', iconPath='res:/UI/Texture/WindowIcons/directorySocial.png'),
 btnIDs.GROUP_UTILITIES_ID: BtnDataRaw(label='UI/Neocom/GroupUtilities', iconPath='res:/UI/Texture/WindowIcons/directoryUtilities.png'),
 btnIDs.GROUP_PARAGON_SERVICES_ID: BtnDataRaw(label='UI/Neocom/GroupParagonServices', iconPath=eveicon.paragon_folder),
 btnIDs.HELP_ID: BtnDataRaw(cmdName='OpenHelp', wndCls=HelpWindow),
 btnIDs.INVENTORY_ID: BtnDataRaw(cmdName='OpenInventory', wndCls=InventoryPrimary),
 btnIDs.PLEX_VAULT_ID: BtnDataRaw(cmdName='OpenPlexVault', wndCls=PlexVaultWindow),
 btnIDs.CORP_HANGAR_ID: BtnDataRaw(cmdName='OpenCorpHangar', wndCls=StationCorpHangars),
 btnIDs.CORP_DELIVERIES_ID: BtnDataRaw(cmdName='OpenCorpDeliveries', wndCls=StationCorpDeliveries),
 btnIDs.JOURNAL_ID: BtnDataRaw(label=JournalWindow.default_captionLabelPath, cmdName='OpenJournal', wndCls=JournalWindow),
 btnIDs.LOCATIONS_ID: BtnDataRaw(cmdName='OpenLocations', wndCls=LocationsWindow),
 btnIDs.LOG_ID: BtnDataRaw(cmdName='OpenLog', wndCls=LoggerWindow),
 btnIDs.MAIL_ID: BtnDataRaw(cmdName='OpenMail', wndCls=MailWindow),
 btnIDs.MAP_BETA_ID: BtnDataRaw(cmdName='CmdToggleMap', iconPath='res:/UI/Texture/windowIcons/map.png', wndCls=MapViewPanel),
 btnIDs.SHIP_TREE_ID: BtnDataRaw(cmdName='CmdToggleShipTree', iconPath='res:/ui/texture/windowIcons/ISIS.png', wndCls=ShipTreeDockablePanel),
 btnIDs.MARKET_ID: BtnDataRaw(cmdName='OpenMarket', wndCls=RegionalMarket),
 btnIDs.MARKET_ORDERS_ID: BtnDataRaw(cmdName='OpenMarketOrders', wndCls=MarketOrdersWnd),
 btnIDs.MULTI_BUY_ID: BtnDataRaw(cmdName='OpenMultibuy', wndCls=MultiBuy),
 btnIDs.MILITIA_ID: BtnDataRaw(cmdName='OpenMilitia', wndCls=FwWarzoneDashboard),
 btnIDs.NOTEPAD_ID: BtnDataRaw(cmdName='OpenNotepad', wndCls=NotepadWindow),
 btnIDs.INDUSTRY_ID: BtnDataRaw(label='UI/Neocom/IndustryBtn', cmdName='OpenIndustry', wndCls=Industry),
 btnIDs.PLANETS_ID: BtnDataRaw(label='UI/ScienceAndIndustry/PlanetaryColonies', cmdName='OpenPlanets', wndCls=PlanetWindow),
 btnIDs.MERCENARY_DEN: BtnDataRaw(label='UI/ScienceAndIndustry/PlanetaryColonies', cmdName='OpenMyMercenaryDens', wndCls=MyMercDensWnd),
 btnIDs.WALLET_ID: BtnDataRaw(cmdName='OpenWallet', wndCls=WalletWindow),
 btnIDs.SETTINGS_ID: BtnDataRaw(cmdName='CmdToggleSystemMenu', iconPath='res:/ui/texture/WindowIcons/settings.png', wndCls=SettingsNeocomClass),
 btnIDs.SECURITY_OFFICE_ID: BtnDataRaw(cmdName='OpenSecurityOffice', wndCls=SecurityOfficeWindow),
 btnIDs.COMPARE_ID: BtnDataRaw(cmdName='OpenCompare', wndCls=TypeCompare),
 btnIDs.AURUM_STORE_ID: BtnDataRaw(cmdName='ToggleAurumStore', iconPath='res:/ui/texture/WindowIcons/NES.png', wndCls=AurumStoreNeocomClass),
 btnIDs.STRUCTURE_BROWSER_ID: BtnDataRaw(cmdName='OpenStructureBrowser', wndCls=StructureBrowserWnd),
 btnIDs.ACCESS_GROUP_ID: BtnDataRaw(cmdName='OpenAccessGroupsWindow', wndCls=AccessGroupsWnd),
 btnIDs.LEDGER_ID: BtnDataRaw(cmdName='OpenLedger', wndCls=LedgerWindow),
 btnIDs.POINTER_WND_ID: BtnDataRaw(cmdName='OpenPointerWnd', wndCls=PointerToolWnd),
 btnIDs.AGENCY_ID: BtnDataRaw(label='AgencyWindow', cmdName='OpenAgencyNew', wndCls=AgencyWndNew, iconPath='res:/UI/Texture/WindowIcons/theAgency.png'),
 btnIDs.PROJECT_DISCOVERY_ID: BtnDataRaw(label=btnIDs.PROJECT_DISCOVERY_ID, cmdName='ToggleProjectDiscovery', iconPath='res:/ui/texture/WindowIcons/projectdiscovery.png', wndCls=get_project_discovery_window_class()),
 btnIDs.LOGIN_REWARDS_ID: BtnDataRaw(label='LoginCampaignWindow', cmdName='OpenLoginRewardWindow', iconPath='res:/UI/Texture/WindowIcons/gift.png', wndCls=DailyLoginRewardsWnd),
 btnIDs.RAFFLE_WINDOW_ID: BtnDataRaw(label='UI/HyperNet/WindowTitle', cmdName='OpenRaffleWindow', wndCls=RaffleWindow),
 btnIDs.QUIT_GAME_ID: BtnDataRaw(cmdName='CmdQuitGame', iconPath='res:/ui/texture/WindowIcons/quitGame.png'),
 btnIDs.LOG_OFF_ID: BtnDataRaw(cmdName='CmdLogOff', iconPath='res:/ui/texture/WindowIcons/logOut.png'),
 btnIDs.PVP_FILAMENTS_ID: BtnDataRaw(cmdName='OpenPVPFilamentEventWindow', wndCls=PVPFilamentEventWindow),
 btnIDs.SKILLS_ID: BtnDataRaw(cmdName='OpenSkillsWindow', wndCls=SkillPlanDockablePanel),
 btnIDs.JOB_BOARD_ID: BtnDataRaw(label=JobBoardWindow.default_captionLabelPath, cmdName='OpenJobBoardWindow', wndCls=JobBoardWindow),
 btnIDs.INSURGENCY_DASHBOARD: BtnDataRaw(cmdName='OpenInsurgencyDashboard', wndCls=InsurgentsDashboard),
 btnIDs.SHIP_SKINR: BtnDataRaw(cmdName='OpenShipSKINRWindow', wndCls=ShipSKINRWindow)}

def GetCmdNameForWindowFromRawData(wnd):
    for k, rButtonData in BTNDATARAW_BY_ID.iteritems():
        if rButtonData.wndCls == wnd.__class__:
            return getattr(rButtonData, 'cmdName', None)
