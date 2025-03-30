#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\fleetwindow.py
import carbonui.const as uiconst
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import evefleet
import localization
import uthread
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.services.setting import SessionSettingBool
from carbonui.window.widget import WidgetWindow
from carbonui.primitives.container import Container
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from eve.client.script.ui.shared.fleet import fleetbroadcastexports, fleetBroadcastConst
from eve.client.script.ui.shared.fleet.fleet import MyFleetPanel
from eve.client.script.ui.shared.fleet.fleetBroadcastConst import broadcastButtonIDs
from eve.client.script.ui.shared.fleet.fleetBroadcastCont import FleetBroadcastCont
from eve.client.script.ui.shared.fleet.fleetConst import FLEET_VIEW_FLAT_LIST_SETTING
from eve.client.script.ui.shared.fleet.fleetFormations import FleetFormationsPanel, FleetFormationWnd
from eve.client.script.ui.shared.fleet.fleetRespawnPoints import RespawnPanel
from eve.client.script.ui.shared.fleet.fleetUtil import ExportLootHistory, OnDropInMyFleet
from eve.client.script.ui.shared.fleet.fleetbroadcast import BroadcastHistoryPanel
from eve.client.script.ui.shared.fleet.fleetbroadcast import BroadcastSettings
from eve.client.script.ui.shared.fleet.fleetfinder import PanelFleetFinder, PanelAdvert, PanelFleetFinderAndAdvert
from eve.client.script.ui.shared.fleet.panelFormFleet import PanelFormFleet
from eve.client.script.ui.shared.fleet.storeFleetSetupWnd import StoredFleetSetupListWnd
from eve.common.script.util.esiUtils import CopyESIFleetUrlToClipboard
from eveexceptions import ExceptionEater
from evefleet.client.util import GetFleetSetupOptionHint
from menu import MenuLabel
from signals.signalUtil import ConnectSignals, DisconnectSignals
import evefleet.fleetSetupConst as fsConst
PANEL_BROADCASTS = 'broadcasts'
PANEL_FLEETFINDER = 'fleetfinder'
PANEL_MYADVERT = 'myadvert'
PANEL_MYFLEET = 'myfleet'
PANEL_RESPAWN = 'respawnPoints'
PANEL_FORMATIONS = 'warpFormations'
PANEL_FORMFLEET = 'formFleet'

class FleetWindow(WidgetWindow):
    __notifyevents__ = ['OnFleetFormationWndChanged']
    default_width = 500
    default_height = 400
    default_minSize = (256, 120)
    default_windowID = 'fleetwindow'
    default_captionLabelPath = 'Tooltips/Neocom/Fleet'
    default_descriptionLabelPath = 'Tooltips/Neocom/Fleet_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/fleet.png'
    default_isCompactable = True

    def ApplyAttributes(self, attributes):
        super(FleetWindow, self).ApplyAttributes(attributes)
        self.formationsPanel = None
        self.myFleetPanel = None
        self.respawnPanel = None
        self.fleetSvc = sm.GetService('fleet')
        self.TryOpenStandaloneFormationWnd()
        self.InitBroadcastBottom()
        self.ConstructTabGroup()
        self.panelsCont = Container(name='panelsCont', parent=self.sr.main, clipChildren=True)
        self.ReconstructTabs()
        self.tabGroup.AutoSelect()
        self.on_content_padding_changed.connect(self.ApplyContentPadding)

    def get_wnd_menu_unique_name(self):
        return pConst.UNIQUE_NAME_FLEET_SETTINGS

    def TryOpenStandaloneFormationWnd(self):
        if session.fleetid and settings.char.ui.Get('fleetFormationStandalone', False):
            FleetFormationWnd.Open()

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader()

    def ReconstructTabs(self):
        self.panelsCont.Flush()
        self.tabGroup.Flush()
        if session.fleetid is not None:
            self.myFleetPanel = MyFleetPanel(parent=self.panelsCont)
            self.historyPanel = BroadcastHistoryPanel(parent=self.panelsCont)
            self.respawnPanel = RespawnPanel(parent=self.panelsCont)
            self.tabGroup.AddTab(localization.GetByLabel('UI/Fleet/Fleet'), self.myFleetPanel, tabID=PANEL_MYFLEET, uniqueName=pConst.UNIQUE_NAME_FLEET_MY_FLEET_TAB)
            self.tabGroup.AddTab(localization.GetByLabel('UI/Fleet/FleetWindow/Broadcasts'), self.historyPanel, tabID=PANEL_BROADCASTS, uniqueName=pConst.UNIQUE_NAME_FLEET_HISTORY_TAB)
            self.tabGroup.AddTab(localization.GetByLabel('UI/Fleet/Respawn/Respawn'), self.respawnPanel, tabID=PANEL_RESPAWN, uniqueName=pConst.UNIQUE_NAME_FLEET_ACTIVE_RECLONERS_TAB)
            if self.IsFormationsTabVisible():
                self.formationsPanel = FleetFormationsPanel(parent=self.panelsCont)
                self.tabGroup.AddTab(localization.GetByLabel('UI/Fleet/FleetFormations/Formations'), self.formationsPanel, tabID=PANEL_FORMATIONS)
            self.tabGroup.AddTab(localization.GetByLabel('UI/Fleet/FleetRegistry/Advert'), PanelAdvert(parent=self.panelsCont), tabID=PANEL_MYADVERT)
            p = PanelFleetFinderAndAdvert(parent=self.panelsCont)
            self.tabGroup.AddTab(localization.GetByLabel('UI/Fleet/FleetRegistry/FindFleets'), p, tabID=PANEL_FLEETFINDER, uniqueName=pConst.UNIQUE_NAME_FLEET_FINDER_TAB)
        else:
            self.tabGroup.AddTab(localization.GetByLabel('Tooltips/Neocom/Fleet'), PanelFormFleet(parent=self.panelsCont), tabID=PANEL_FORMFLEET)
            self.tabGroup.AddTab(localization.GetByLabel('UI/Fleet/FleetWindow/FleetFinder'), PanelFleetFinder(parent=self.panelsCont), tabID=PANEL_FLEETFINDER, uniqueName=pConst.UNIQUE_NAME_FLEET_FINDER_TAB)
        if session.fleetid is not None:
            myFleetTab = self.tabGroup.GetTabs()[0]
            myFleetTab.OnTabDropData = OnDropInMyFleet

    def IsFormationsTabVisible(self):
        return not settings.char.ui.Get('fleetFormationStandalone', False) or not FleetFormationWnd.GetIfOpen()

    def ConstructTabGroup(self):
        self.tabGroup = self.header.tab_group
        self.tabGroup.callback = self.OnTabGroup

    def SelectFirstTab(self):
        panelID = PANEL_MYFLEET if session.fleetid else PANEL_FORMFLEET
        uthread.new(self.tabGroup.ShowPanelByID, panelID)

    def OnFleetFormationWndChanged(self, *args):
        self.ReconstructTabs()
        if not self.IsFormationsTabVisible():
            self.SelectFirstTab()
        else:
            self.tabGroup.AutoSelect()

    def InitBroadcastBottom(self):
        self.content_padding
        self.broadcastCont = FleetBroadcastCont(name='broadcastCont', align=uiconst.TOBOTTOM, parent=self.sr.main, clipChildren=True, innerPadding=self.content_padding)
        self.ApplyContentPadding()

    def ApplyContentPadding(self, *args):
        padLeft, _, padRight, padBottom = self.content_padding
        self.broadcastCont.padding = (-padLeft,
         0,
         -padRight,
         -padBottom)
        self.broadcastCont.SetInnerPadding(self.content_padding)

    def UpdateBottomContVisibility(self):
        panelID = self.tabGroup.GetSelectedID()
        if not session.fleetid or panelID in (PANEL_FLEETFINDER, PANEL_MYADVERT):
            self.broadcastCont.Hide()
        else:
            self.broadcastCont.Show()

    def OnTabGroup(self, tabID, oldTabID):
        self.UpdateBottomContVisibility()

    def GotoTab(self, idx):
        self.tabGroup.SelectByIdx(idx)

    def StartFleetFromSetup(self):
        m = MenuData()
        fleetSetupsByName = self.fleetSvc.GetFleetSetups()
        listOfSetups = sorted(fleetSetupsByName.values(), key=lambda x: x[fsConst.FS_NAME].lower())
        for eachSetup in listOfSetups:
            setupName = eachSetup[fsConst.FS_NAME]
            hint = GetFleetSetupOptionHint(eachSetup)
            m.AddEntry(setupName, func=lambda sn = setupName: self.fleetSvc.StartNewFleet(sn), hint=hint)

        return m

    def GetMenuMoreOptions(self):
        menuData = super(FleetWindow, self).GetMenuMoreOptions()
        menuData += self.GetFleetMenuTop()
        return menuData

    def GetFleetMenuTop(self):
        fleetSvc = self.fleetSvc
        menuData = MenuData()
        if session.fleetid is None:
            menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/FormFleet'), fleetSvc.StartNewFleet)
            if fleetSvc.GetSetups():
                startFleetFromSetupOptions = self.StartFleetFromSetup()
                menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/FormFleetWithSetup'), subMenuData=startFleetFromSetupOptions)
            menuData.AddSeparator()
        else:
            menuData.AddEntry(MenuLabel('UI/Fleet/LeaveMyFleet'), fleetSvc.LeaveFleet)
            if session.fleetrole in [evefleet.fleetRoleLeader, evefleet.fleetRoleWingCmdr, evefleet.fleetRoleSquadCmdr]:
                menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/Regroup'), lambda : fleetSvc.Regroup())
            if fleetSvc.HasActiveBeacon(session.charid):
                menuData.AddEntry(MenuLabel('UI/Fleet/BroadcastJumpBeacon'), lambda : fleetSvc.SendBroadcast_JumpBeacon())
            menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/Broadcasts'), subMenuData=self._GetBroadcastMenu())
            menuData.AddSeparator()
            menuData.AddEntry(MenuLabel('UI/Fleet/FleetBroadcast/BroadcastSettings'), lambda : BroadcastSettings.Open())
            if FLEET_VIEW_FLAT_LIST_SETTING.is_enabled():
                hierarchyText = MenuLabel('UI/Fleet/FleetWindow/ViewAsHierarchy')
            else:
                hierarchyText = MenuLabel('UI/Fleet/FleetWindow/ViewAsFlatList')
            menuData.AddEntry(hierarchyText, FLEET_VIEW_FLAT_LIST_SETTING.toggle)
            menuData.AddSeparator()
            menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/StoreFleetSetup'), fleetSvc.StoreSetup)
            if fleetSvc.IsCommanderOrBoss():
                if fleetSvc.GetSetups():
                    fleetSetupOptions = self.GetFleetSetups()
                    menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/FleetSetups'), subMenuData=fleetSetupOptions)
            menuData.AddSeparator()
            takesFleetWarp = fleetSvc.TakesFleetWarp()
            acceptsFleetWarpSetting = SessionSettingBool(takesFleetWarp)
            acceptsFleetWarpSetting.on_change.connect(self.ChangeAcceptsFleetWarp)
            menuData.AddCheckbox(MenuLabel('UI/Fleet/FleetWindow/AcceptFleetWarp'), acceptsFleetWarpSetting)
            acceptsConduitJumps = fleetSvc.AcceptsConduitJumps()
            acceptsConduitJumpsSetting = SessionSettingBool(acceptsConduitJumps)
            acceptsConduitJumpsSetting.on_change.connect(self.ChangeAcceptsConduitJumps)
            menuData.AddCheckbox(MenuLabel('UI/Fleet/FleetWindow/AcceptConduitJumps'), acceptsConduitJumpsSetting)
            acceptsRegroups = fleetSvc.AcceptsFleetRegroups()
            acceptsRegroupSetting = SessionSettingBool(acceptsRegroups)
            acceptsRegroupSetting.on_change.connect(self.ChangeAcceptsRegroups)
            menuData.AddCheckbox(MenuLabel('UI/Fleet/FleetWindow/AcceptRegroup'), acceptsRegroupSetting)
            menuData.AddSeparator()
            if fleetSvc.IsBoss():
                menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/SetFleetMaxSize'), fleetSvc.SetFleetMaxSize)
                options = fleetSvc.GetOptions()
                freemoveSetting = SessionSettingBool(options.isFreeMove)
                freemoveSetting.on_change.connect(self._ChangeFreeMove)
                menuData.AddCheckbox(MenuLabel('UI/Fleet/FleetWindow/SetFreeMove'), freemoveSetting)
            menuData.AddSeparator()
            if fleetSvc.IsCommanderOrBoss():
                menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/ShowFleetComposition'), fleetSvc.OpenFleetCompositionWindow)
            if fleetSvc.IsBoss():
                if fleetSvc.options.isRegistered:
                    menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/EditAdvert'), fleetSvc.OpenRegisterFleetWindow)
                    menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/RemoveAdvert'), fleetSvc.UnregisterFleet)
                else:
                    menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/CreateAdvert'), fleetSvc.OpenRegisterFleetWindow)
                menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/OpenJoinRequest'), fleetSvc.OpenJoinRequestWindow)
                menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/GetFleetID'), self._CopyESIFleetUrlToClipboard)
            menuData.AddEntry(MenuLabel('UI/Fleet/FleetWindow/ExportLootHistory'), ExportLootHistory)
            if fleetSvc.IsBoss():
                menuData.AddEntry(MenuLabel('UI/Fleet/DisbandFleet'), self.DisbandFleet)
        return menuData

    def _ChangeFreeMove(self, value, *args):
        self.fleetSvc.SetOptions(isFreeMove=value)

    def ChangeAcceptsFleetWarp(self, value, *args):
        self.fleetSvc.SetAcceptsFleetWarpValue(value)

    def ChangeAcceptsConduitJumps(self, value, *args):
        self.fleetSvc.SetAcceptConduitJumpsValue(value)

    def ChangeAcceptsRegroups(self, value, *args):
        self.fleetSvc.SetAcceptRegroupValue(value)

    def DisbandFleet(self):
        if eve.Message('DisbandFleet', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        return self.fleetSvc.DisbandFleet()

    def _GetBroadcastMenu(self):
        m = []
        for broadcastID in broadcastButtonIDs:
            hint = fleetbroadcastexports.GetBroadcastName(broadcastID)
            m.append(MenuEntryData(hint, lambda _broadcastID = broadcastID: self.fleetSvc.SendBroadcast(_broadcastID), texturePath=fleetBroadcastConst.iconsByBroadcastType[broadcastID]))

        if session.fleetrole in evefleet.fleetCmdrRoles:
            m.append(MenuEntryData(localization.GetByLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastTravelToMe'), lambda : self.fleetSvc.SendBroadcast_TravelTo(session.solarsystemid2), texturePath=fleetBroadcastConst.iconsByBroadcastType[fleetBroadcastConst.BROADCAST_TRAVEL_TO]))
        return m

    def GetFleetSetups(self):
        fleetSetupsByName = self.fleetSvc.GetFleetSetups()
        m = self.fleetSvc.GetSetups()
        if fleetSetupsByName:
            m.AddSeparator()
            m.AddEntry(MenuLabel('UI/Fleet/FleetWindow/SetupsOverview'), self.OpenStoredFleetSetupListWnd)
        return m

    def OpenStoredFleetSetupListWnd(self):
        StoredFleetSetupListWnd.Open(fleetSvc=self.fleetSvc)

    def UpdateHeader(self):
        nMembers = len(self.myFleetPanel.members)
        info = self.fleetSvc.GetMemberInfo(session.charid)
        if info is None:
            return
        if info.role == evefleet.fleetRoleLeader:
            caption = localization.GetByLabel('UI/Fleet/FleetWindow/FleetHeaderBoss', numMembers=nMembers)
        elif info.role == evefleet.fleetRoleWingCmdr:
            caption = localization.GetByLabel('UI/Fleet/FleetWindow/FleetHeaderWingCmdr', numMembers=nMembers, wingName=info.wingName)
        else:
            caption = localization.GetByLabel('UI/Fleet/FleetWindow/FleetHeaderSquadMember', numMembers=nMembers, wingName=info.wingName, squadName=info.squadName)
        self.SetCaption(caption)

    def _CopyESIFleetUrlToClipboard(self):
        CopyESIFleetUrlToClipboard(session.fleetid)
