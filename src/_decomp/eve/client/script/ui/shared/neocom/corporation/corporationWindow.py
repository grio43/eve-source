#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corporationWindow.py
import logging
import blue
import eveicon
import uthread
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_QA
from carbonui import const as uiconst
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.sideNavigation import SideNavigationSplitView, SideNavigation, SideNavigationEntry
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from corporation.client.goals import goalSignals
from corporation.client.goals import goalsSettings
from corporation.client.goals.goalsController import CorpGoalsController
from eve.client.script.ui.control.treeData import TreeData
from eve.client.script.ui.cosmetics.ship.pages.store import storeSignals
from eve.client.script.ui.services.corporation.corp_util import HasRole, HasAnyRole
from eve.client.script.ui.shared.neocom.Alliances.all_ui_applications import FormAlliancesApplications
from eve.client.script.ui.shared.neocom.Alliances.all_ui_home import FormAlliancesHome, FormAlliancesBulletins
from eve.client.script.ui.shared.neocom.Alliances.all_ui_members import FormAlliancesMembers
from eve.client.script.ui.shared.neocom.Alliances.all_ui_rankings import FormAlliancesRankings
from eve.client.script.ui.shared.neocom.Alliances.all_ui_sovereignty import FormAlliancesSovereignty
from eve.client.script.ui.shared.neocom.Alliances.all_ui_systems import FormAlliancesSystems
from eve.client.script.ui.shared.neocom.Alliances.sovHubs.sovHubPage import SovHubPage
from eve.client.script.ui.shared.neocom.addressBook.contactsConst import TAB_ALLIANCECONTACTS, TAB_CORPCONTACTS
from eve.client.script.ui.shared.neocom.addressBook.contactsForm import ContactsForm
from eve.client.script.ui.shared.neocom.charsheet.standingsPanel.standingsPanel import StandingsPanel
from eve.client.script.ui.shared.neocom.corporation import corpUISettings, corpPanelConst
from eve.client.script.ui.shared.neocom.corporation.corpPanelConst import NAME_BY_PANEL_ID, CorpPanel, HINT_BY_PANEL_ID, POINTER_UUID_BY_PANEL_ID
from eve.client.script.ui.shared.neocom.corporation.corp_ui_accounts import CorpAccounts
from eve.client.script.ui.shared.neocom.corporation.corp_ui_applications import ApplicationsWindow
from eve.client.script.ui.shared.neocom.corporation.corp_ui_bulletins import CorpUIBulletins
from eve.client.script.ui.shared.neocom.corporation.corp_ui_direct_enlistment_mgt import CorpDirectEnlistmentMgt
from eve.client.script.ui.shared.neocom.corporation.corp_ui_home import CorpUIHome
from eve.client.script.ui.shared.neocom.corporation.corp_ui_killreports import CorpKillReports
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_auditing import CorpAuditing
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_autokicks import CorpAutoKicks
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_decorations import CorpDecorations
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_find import CorpFindMembersInRole
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_newroles import CorpRolesNew
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_titles import CorpTitles
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_tracking import CorpMemberTracking
from eve.client.script.ui.shared.neocom.corporation.corp_ui_projects import CorpUIProjects
from eve.client.script.ui.shared.neocom.corporation.corp_ui_recruitment import CorpRecruitment
from eve.client.script.ui.shared.neocom.corporation.corp_ui_sanctionableactions import CorpSanctionableActions
from eve.client.script.ui.shared.neocom.corporation.corp_ui_structure_design import CorpStructureDesignPanel
from eve.client.script.ui.shared.neocom.corporation.corp_ui_votes import CorpVotes
from eve.client.script.ui.shared.neocom.corporation.corp_ui_wars import CorpWars
from eve.client.script.ui.shared.neocom.corporation.recruitment.corpRecruitmentContainer import CorpRecruitmentContainerSearch
from eve.client.script.ui.shared.neocom.corporation.war.warHistoryCont import WarHistoryCont
from eve.client.script.ui.shared.neocom.corporation.war.warLandingPage import WarLandingPage
from eve.client.script.ui.shared.neocom.corporation.war.warMutalWarInvite import MutualWarInvites
from eve.client.script.ui.shared.neocom.wallet import walletUtil
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from evecorporation.roles import get_role_name
from localization import GetByLabel
logger = logging.getLogger(__name__)
admin_panel_role_mask = const.corpRolePersonnelManager | const.corpRoleDirector | const.corpRoleAuditor | const.corpRoleAccountant | const.corpRoleStationManager | const.corpRoleBrandManager

def OnCorpGoalViewDetails(job_id):
    wnd = CorporationWindow.GetIfOpen()
    if wnd:
        wnd.Maximize()
        wnd.SelectPanel(CorpPanel.PROJECTS, content_id=job_id)
    else:
        CorporationWindow.Open(panel_id=CorpPanel.PROJECTS, content_id=job_id)


goalSignals.on_view_details.connect(OnCorpGoalViewDetails)

def OnSKINRJoinPlayerCorpBanner():
    wnd = CorporationWindow.GetIfOpen()
    if wnd:
        wnd.Maximize()
        wnd.SelectPanel(CorpPanel.RECRUITMENT_SEARCH)
    else:
        CorporationWindow.Open(panel_id=CorpPanel.RECRUITMENT_SEARCH)


storeSignals.on_join_player_corp_banner.connect(OnSKINRJoinPlayerCorpBanner)

class CorporationWindow(Window):
    default_width = 800
    default_height = 756
    default_minSize = (550, default_height)
    default_windowID = 'corporation'
    default_apply_content_padding = False
    default_captionLabelPath = 'UI/Corporations/BaseCorporationUI/Corporation'
    default_descriptionLabelPath = 'Tooltips/Neocom/Corporations_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/corporation.png'
    __notifyevents__ = ['OnCorpAllowedEnlistmentFactionsSet']

    def ApplyAttributes(self, attributes):
        super(CorporationWindow, self).ApplyAttributes(attributes)
        panel_id = attributes.panel_id
        self.content_id = attributes.content_id
        self.corpSvc = sm.GetService('corp')
        self.panels = {}
        self.panelsCont = None
        while session.mutating:
            blue.pyos.BeNice()

        self.split_view = SideNavigationSplitView(parent=self.content, is_always_expanded_setting=corpUISettings.corp_side_navigation_always_expanded_setting, expanded_panel_width=240)
        self.split_view.content.padTop = self.content_padding[1]
        self.split_view.content.padRight = self.content_padding[2]
        self.split_view.content.padBottom = self.content_padding[3]
        self.side_navigation = SideNavigation(name='navigation_scroll', parent=self.split_view.panel, is_always_expanded_setting=corpUISettings.corp_side_navigation_always_expanded_setting, is_expanded_func=self.split_view.is_expanded, expand_func=self.split_view.expand_panel)
        self.split_view.on_expanded_changed.connect(self.side_navigation.on_expanded_changed)
        self.reconstruct_panels()
        self.reconstruct_main_tabs()
        self.SelectPanel(panel_id, reconstruct_side_nav=True)
        uthread.new(walletUtil.CheckSetDefaultWalletDivision)

    def reconstruct_main_tabs(self):
        self.header.tab_group.Flush()
        self.header.tab_group.AddTab(GetByLabel('UI/Corporations/BaseCorporationUI/Corporation'), tabID=CorpPanel.CORPORATION, uniqueName=POINTER_UUID_BY_PANEL_ID.get(CorpPanel.CORPORATION, None))
        self.header.tab_group.AddTab(GetByLabel('UI/Corporations/CorporationWindow/Alliances/Alliances'), tabID=CorpPanel.ALLIANCES, uniqueName=POINTER_UUID_BY_PANEL_ID.get(CorpPanel.ALLIANCES, None))
        if self.can_see_admin_panels():
            self.header.tab_group.AddTab(GetByLabel('UI/Corporations/CorporationWindow/Administration'), tabID=CorpPanel.ADMINISTRATION, uniqueName=POINTER_UUID_BY_PANEL_ID.get(CorpPanel.ADMINISTRATION, None))

    def _select_header_tab(self, panel_id):
        path = self.navigation_tree_data.GetPathToDescendant(panel_id)
        if path:
            self.header.tab_group.SelectByID(path[1].GetID(), useCallback=False)

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader()
        self.header.on_tab_selected.connect(self.on_header_tabgroup)

    def on_header_tabgroup(self, tab_id, old_panel_id):
        setting = self.get_tab_selected_setting(tab_id)
        panel_id = setting.get()
        if not panel_id:
            panel_id = self.get_first_panel_id(tab_id)
        self.SelectPanel(panel_id, reconstruct_side_nav=True)

    def get_first_panel_id(self, tab_id):
        node = self.navigation_tree_data.GetChildByID(tab_id)
        for decendant in node.GetDescendants().values():
            if decendant.GetID() in self.panels:
                return decendant.GetID()

    def get_tab_selected_setting(self, tab_id):
        if tab_id == CorpPanel.CORPORATION:
            return corpUISettings.corp_window_corp_tab_selected_panel_setting
        if tab_id == CorpPanel.ALLIANCES:
            return corpUISettings.corp_window_alliance_tab_selected_panel_setting
        if tab_id == CorpPanel.ADMINISTRATION:
            return corpUISettings.corp_window_admin_tab_selected_panel_setting

    def add_navigation_node(self, parent_id, panel_id):
        parent = self.navigation_tree_data.GetChildByID(parent_id)
        return parent.AddNode(GetByLabel(NAME_BY_PANEL_ID.get(panel_id, '')), nodeID=panel_id, icon=corpPanelConst.ICON_BY_PANEL_ID.get(panel_id, eveicon.corporation_management))

    def reconstruct_side_navigation(self):
        self.side_navigation.Flush()
        header_tab_id = self.header.tab_group.GetSelectedArgs() or CorpPanel.CORPORATION
        root_node = self.navigation_tree_data.GetChildByID(header_tab_id)
        for node in root_node.children:
            if node.HasChildren():
                self.side_navigation.add_header(node.GetLabel())
                for child_node in node.children:
                    self._add_navigation_entry(child_node)

            else:
                self._add_navigation_entry(node)

    def _add_navigation_entry(self, child_node):
        panel_id = child_node.GetID()
        self.side_navigation.add_entry(entry_id=panel_id, text=child_node.GetLabel(), entry_cls=CorpWindowSideNavigationEntry, on_click=self.on_side_navigation_entry_clicked, icon=child_node.GetIcon(), hint=GetByLabel(HINT_BY_PANEL_ID[panel_id]) if panel_id in HINT_BY_PANEL_ID else None, uniqueUiName=POINTER_UUID_BY_PANEL_ID.get(panel_id, None))

    def on_side_navigation_entry_clicked(self, entry):
        self.SelectPanel(entry.entry_id)

    def SelectPanel(self, panel_id = None, content_id = None, reconstruct_side_nav = False):
        if panel_id is None:
            panel_id = corpUISettings.corp_window_selected_panel_setting.get()
        if content_id:
            self.content_id = content_id
        self._select_header_tab(panel_id)
        if reconstruct_side_nav:
            self.reconstruct_side_navigation()
        node = self.navigation_tree_data.GetChildByID(panel_id)
        if node:
            self._select_node(node)
        else:
            tab_id = self.header.tab_group.GetSelectedArgs() or CorpPanel.CORPORATION
            panel_id = self.get_first_panel_id(tab_id)
            node = self.navigation_tree_data.GetChildByID(panel_id)
            if node:
                self._select_node(node)

    def _select_node(self, node):
        node.GetRootNode().DeselectAll()
        node.SetSelected(animate=False)

    def on_tree_node_selected(self, node, animate = True):
        panel_id = node.GetID()
        self.side_navigation.set_entry_selected(panel_id)
        for _panel_id, panel in self.panels.items():
            panel.display = panel_id == _panel_id

        panel = self.panels[panel_id]
        uthread2.start_tasklet(panel.Load, panel_id, self.content_id)
        self.content_id = None
        self.update_selected_panel_settings(panel_id)

    def reconstruct_panels(self):
        if self.panelsCont and not self.panelsCont.destroyed:
            self.panelsCont.Close()
        self.panelsCont = Container(name='panelsCont', parent=self.split_view.content, padLeft=16)
        self.navigation_tree_data = TreeData()
        self.navigation_tree_data.on_selected.connect(self.on_tree_node_selected)
        self._construct_panels()

    def _construct_panels(self):
        self.navigation_tree_data.AddNode(GetByLabel(NAME_BY_PANEL_ID.get(CorpPanel.CORPORATION, '')), nodeID=CorpPanel.CORPORATION)
        self.navigation_tree_data.AddNode(GetByLabel(NAME_BY_PANEL_ID.get(CorpPanel.ALLIANCES, '')), nodeID=CorpPanel.ALLIANCES)
        self.construct_corporation_panels()
        if self.can_see_admin_panels():
            self.construct_administration_panels()
        self.construct_alliance_panels()

    def construct_corporation_panels(self):
        self.construct_corporation_general_panels()
        self.construct_corporation_recruitment_panels()
        if not idCheckers.IsNPC(session.corpid):
            self.construct_corporation_members_panels()
            self.construct_corporation_standings_panels()
        if sm.GetService('corpvotes').CanViewVotes(session.corpid):
            self.construct_corporation_voting_panels()
        self.construct_corporation_wars_panels()

    def construct_corporation_wars_panels(self):
        self.add_navigation_node(CorpPanel.CORPORATION, CorpPanel.CORP_WARS)
        self.panels[CorpPanel.WARS] = CorpWars(name='warspar', parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.CORP_WARS, CorpPanel.WARS)
        self.panels[CorpPanel.WARS_HOMEPAGE] = WarLandingPage(parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.CORP_WARS, CorpPanel.WARS_HOMEPAGE)
        if not idCheckers.IsNPC(session.corpid):
            self.panels[CorpPanel.WARS_HISTORY] = WarHistoryCont(parent=self.panelsCont)
            self.add_navigation_node(CorpPanel.CORP_WARS, CorpPanel.WARS_HISTORY)

    def construct_corporation_voting_panels(self):
        self.add_navigation_node(CorpPanel.CORPORATION, CorpPanel.CORP_VOTING)
        self.panels[CorpPanel.VOTES] = CorpVotes(name='votespar', parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.CORP_VOTING, CorpPanel.VOTES)
        self.panels[CorpPanel.SANCTIONABLE] = CorpSanctionableActions(name='sanctionablepar', parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.CORP_VOTING, CorpPanel.SANCTIONABLE)

    def construct_corporation_standings_panels(self):
        self.add_navigation_node(CorpPanel.CORPORATION, CorpPanel.CORP_STANDINGS)
        self.panels[CorpPanel.CONTACTS] = ContactsForm(name='corpcontactsform', parent=self.panelsCont, contactType=TAB_CORPCONTACTS)
        self.add_navigation_node(CorpPanel.CORP_STANDINGS, CorpPanel.CONTACTS)
        self.panels[CorpPanel.NPC_STANDINGS] = StandingsPanel(parent=self.panelsCont, toID=session.corpid, corpMode=True)
        self.add_navigation_node(CorpPanel.CORP_STANDINGS, CorpPanel.NPC_STANDINGS)

    def construct_corporation_members_panels(self):
        self.add_navigation_node(CorpPanel.CORPORATION, CorpPanel.CORP_MEMBERS)
        self.panels[CorpPanel.MEMBERLIST] = CorpMemberTracking(name='membertrackingpar', parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.CORP_MEMBERS, CorpPanel.MEMBERLIST)
        self.panels[CorpPanel.DECORATIONS] = CorpDecorations(name='decorations', parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.CORP_MEMBERS, CorpPanel.DECORATIONS)

    def construct_corporation_recruitment_panels(self):
        self.add_navigation_node(CorpPanel.CORPORATION, CorpPanel.CORP_RECRUITMENT)
        self.panels[CorpPanel.RECRUITMENT_SEARCH] = CorpRecruitmentContainerSearch(parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.CORP_RECRUITMENT, CorpPanel.RECRUITMENT_SEARCH)
        self.panels[CorpPanel.MY_APPLICATIONS] = ApplicationsWindow(parent=self.panelsCont, ownerID=session.charid)
        self.add_navigation_node(CorpPanel.CORP_RECRUITMENT, CorpPanel.MY_APPLICATIONS)

    def construct_corporation_general_panels(self):
        self.add_navigation_node(CorpPanel.CORPORATION, CorpPanel.CORP_GENERAL)
        if not idCheckers.IsNPC(session.corpid):
            self.panels[CorpPanel.PROJECTS] = CorpUIProjects(parent=self.panelsCont)
            self.add_navigation_node(CorpPanel.CORP_GENERAL, CorpPanel.PROJECTS)
        self.panels[CorpPanel.MY_CORPORATION] = CorpUIHome(name='corp_home', parent=self.panelsCont, state=uiconst.UI_PICKCHILDREN)
        self.add_navigation_node(CorpPanel.CORP_GENERAL, CorpPanel.MY_CORPORATION)
        self.panels[CorpPanel.KILLREPORTS] = CorpKillReports(parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.CORP_GENERAL, CorpPanel.KILLREPORTS)
        if not idCheckers.IsNPC(session.corpid):
            self.panels[CorpPanel.BULLETINS] = CorpUIBulletins(parent=self.panelsCont)
            self.add_navigation_node(CorpPanel.CORP_GENERAL, CorpPanel.BULLETINS)

    def construct_alliance_panels(self):
        self.construct_alliance_general()
        self.construct_alliance_relationships()
        self.construct_alliance_sovereignty()

    def construct_alliance_general(self):
        self.add_navigation_node(CorpPanel.ALLIANCES, CorpPanel.ALLIANCES_GENERAL)
        self.panels[CorpPanel.ALLIANCES_HOME] = FormAlliancesHome(parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.ALLIANCES_GENERAL, CorpPanel.ALLIANCES_HOME)
        if session.allianceid is not None:
            self.panels[CorpPanel.ALLIANCES_BULLETINS] = FormAlliancesBulletins(parent=self.panelsCont)
            self.add_navigation_node(CorpPanel.ALLIANCES_GENERAL, CorpPanel.ALLIANCES_BULLETINS)
            self.panels[CorpPanel.ALLIANCES_MEMBERS] = FormAlliancesMembers(parent=self.panelsCont)
            self.add_navigation_node(CorpPanel.ALLIANCES_GENERAL, CorpPanel.ALLIANCES_MEMBERS)

    def construct_alliance_relationships(self):
        self.add_navigation_node(CorpPanel.ALLIANCES, CorpPanel.ALLIANCES_RELATIONSHIPS_GROUP)
        if session.allianceid is not None:
            self.panels[CorpPanel.ALLIANCES_CONTACTS] = ContactsForm(name=CorpPanel.ALLIANCES_CONTACTS, parent=self.panelsCont, contactType=TAB_ALLIANCECONTACTS)
            self.add_navigation_node(CorpPanel.ALLIANCES_RELATIONSHIPS_GROUP, CorpPanel.ALLIANCES_CONTACTS)
        if not idCheckers.IsNPC(session.corpid):
            self.panels[CorpPanel.ALLIANCES_APPLICATIONS] = FormAlliancesApplications(parent=self.panelsCont)
            self.add_navigation_node(CorpPanel.ALLIANCES_RELATIONSHIPS_GROUP, CorpPanel.ALLIANCES_APPLICATIONS)
        self.panels[CorpPanel.ALLIANCES_BROWSE_ALL] = FormAlliancesRankings(parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.ALLIANCES_RELATIONSHIPS_GROUP, CorpPanel.ALLIANCES_BROWSE_ALL)

    def construct_alliance_sovereignty(self):
        if session.allianceid is None:
            return
        self.add_navigation_node(CorpPanel.ALLIANCES, CorpPanel.ALLIANCES_SOVEREIGNTY_GROUP)
        self.panels[CorpPanel.ALLIANCE_SOVEREIGNTY] = FormAlliancesSovereignty(parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.ALLIANCES_SOVEREIGNTY_GROUP, CorpPanel.ALLIANCE_SOVEREIGNTY)
        self.panels[CorpPanel.ALLIANCES_SYSTEMS] = FormAlliancesSystems(parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.ALLIANCES_SOVEREIGNTY_GROUP, CorpPanel.ALLIANCES_SYSTEMS)
        if HasRole(appConst.corpRoleStationManager):
            self.panels[CorpPanel.ALLIANCES_SOVHUBS] = SovHubPage(parent=self.panelsCont)
            self.add_navigation_node(CorpPanel.ALLIANCES_SOVEREIGNTY_GROUP, CorpPanel.ALLIANCES_SOVHUBS)

    def construct_administration_panels(self):
        self.navigation_tree_data.AddNode(GetByLabel(NAME_BY_PANEL_ID.get(CorpPanel.ADMINISTRATION, '')), nodeID=CorpPanel.ADMINISTRATION)
        self.construct_admin_members_panels()
        if HasAnyRole((appConst.corpRoleAuditor,
         appConst.corpRoleAccountant,
         appConst.corpRoleStationManager,
         appConst.corpRoleBrandManager)):
            self.construct_admin_general_panels()
        if HasRole(appConst.corpRolePersonnelManager) or self.has_grantable_roles():
            self.construct_admin_recruitment_panels()
        if HasRole(appConst.corpRoleDirector):
            self.construct_admin_wars_panels()

    def construct_admin_general_panels(self):
        self.add_navigation_node(CorpPanel.ADMINISTRATION, CorpPanel.ADMIN_GENERAL)
        if HasRole(appConst.corpRoleAuditor):
            self.panels[CorpPanel.AUDITING] = CorpAuditing(parent=self.panelsCont)
            self.add_navigation_node(CorpPanel.ADMIN_GENERAL, CorpPanel.AUDITING)
        if HasRole(appConst.corpRoleAccountant):
            self.panels[CorpPanel.ASSETS] = CorpAccounts(parent=self.panelsCont)
            self.add_navigation_node(CorpPanel.ADMIN_GENERAL, CorpPanel.ASSETS)
        if HasRole(appConst.corpRoleBrandManager):
            self.panels[CorpPanel.STRUCTURE_DESIGN] = CorpStructureDesignPanel(parent=self.panelsCont)
            self.add_navigation_node(CorpPanel.ADMIN_GENERAL, CorpPanel.STRUCTURE_DESIGN)

    def construct_admin_members_panels(self):
        self.add_navigation_node(CorpPanel.ADMINISTRATION, CorpPanel.ADMIN_MEMBERS)
        if HasRole(appConst.corpRolePersonnelManager) or self.has_grantable_roles():
            self.panels[CorpPanel.FINDMEMBER] = CorpFindMembersInRole(parent=self.panelsCont)
            self.add_navigation_node(CorpPanel.ADMIN_MEMBERS, CorpPanel.FINDMEMBER)
            self.panels[CorpPanel.ROLEMANAGEMENT] = CorpRolesNew(parent=self.panelsCont, corp=sm.GetService('corp').GetCorporation())
            self.add_navigation_node(CorpPanel.ADMIN_MEMBERS, CorpPanel.ROLEMANAGEMENT)
        if HasRole(appConst.corpRoleDirector):
            self.panels[CorpPanel.AUTOKICKS] = CorpAutoKicks(parent=self.panelsCont)
            self.add_navigation_node(CorpPanel.ADMIN_MEMBERS, CorpPanel.AUTOKICKS)
            self.panels[CorpPanel.TITLES] = CorpTitles(parent=self.panelsCont)
            self.add_navigation_node(CorpPanel.ADMIN_MEMBERS, CorpPanel.TITLES)

    def construct_admin_recruitment_panels(self):
        self.add_navigation_node(CorpPanel.ADMINISTRATION, CorpPanel.ADMIN_RECRUITMENT)
        self.panels[CorpPanel.RECRUITMENT_ADS] = CorpRecruitment(name='recruitmentpar', parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.ADMIN_RECRUITMENT, CorpPanel.RECRUITMENT_ADS)
        self.panels[CorpPanel.RECRUITMENT_APPLICATIONS] = ApplicationsWindow(parent=self.panelsCont, ownerID=session.corpid)
        self.add_navigation_node(CorpPanel.ADMIN_RECRUITMENT, CorpPanel.RECRUITMENT_APPLICATIONS)

    def construct_admin_wars_panels(self):
        self.add_navigation_node(CorpPanel.ADMINISTRATION, CorpPanel.ADMIN_WARS)
        self.panels[CorpPanel.WARS_MUTUAL_INVITES] = MutualWarInvites(parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.ADMIN_WARS, CorpPanel.WARS_MUTUAL_INVITES)
        self.panels[CorpPanel.WARS_DIRECT_ENLISTMENT] = CorpDirectEnlistmentMgt(parent=self.panelsCont)
        self.add_navigation_node(CorpPanel.ADMIN_WARS, CorpPanel.WARS_DIRECT_ENLISTMENT)

    def can_see_admin_panels(self):
        return session.corprole & admin_panel_role_mask or self.has_grantable_roles()

    def has_grantable_roles(self):
        grantableRoles, grantableRolesAtHQ, grantableRolesAtBase, grantableRolesAtOther = self.corpSvc.GetMyGrantableRoles()
        hasGrantableRoles = grantableRoles | grantableRolesAtHQ | grantableRolesAtBase | grantableRolesAtOther
        return hasGrantableRoles

    def update_selected_panel_settings(self, panel_id):
        corpUISettings.corp_window_selected_panel_setting.set(panel_id)
        tree_data = self.navigation_tree_data.GetChildByID(panel_id)
        header_tree_data = tree_data.GetAncestors()[1]
        header_tab_id = header_tree_data.GetID()
        setting = self.get_tab_selected_setting(header_tab_id)
        setting.set(panel_id)

    def OnUIRefresh(self):
        pass

    def RefreshSize(self, *args):
        for panel in self.panels.values():
            if panel.state != uiconst.UI_HIDDEN and hasattr(panel, 'OnContentResize'):
                panel.OnContentResize(1)
                continue

    def OnWndScale(self, *args):
        for panel in self.panels.values():
            if panel.state != uiconst.UI_HIDDEN and hasattr(panel, 'OnContentResize'):
                panel.OnContentResize(0)
                continue

    def OnCloseWnd(self, *args):
        for panel in self.panels.values():
            if hasattr(panel, '_OnClose'):
                panel._OnClose(args)

    def OnCorpAllowedEnlistmentFactionsSet(self):
        panel = self.panels.get(CorpPanel.MY_CORPORATION, None)
        if panel:
            panel.LoadScroll()

    def GetMenuMoreOptions(self):
        menuData = super(CorporationWindow, self).GetMenuMoreOptions()
        if session.role & ROLE_QA:
            menuData.AddEntry('QA Options:', subMenuData=self._GetQAMenuOptions)
        return menuData

    def _GetQAMenuOptions(self):
        menuData = MenuData()
        menuData.AddEntry('Flush Corp Projects Cache', CorpGoalsController.get_instance().flush_cache)
        menuData.AddEntry('Delete all projects (without progress)', CorpGoalsController.get_instance().qa_delete_all_goals)
        menuData.AddEntry('Create multiple Projects at once', subMenuData=self._GetCreateMultipleMenuOptions)
        menuData.AddCheckbox('Allow short Projects', setting=goalsSettings.qa_allow_short_corp_projects)
        return menuData

    def _GetCreateMultipleMenuOptions(self):
        menuData = MenuData()
        menuData.AddRadioButton('OFF', None, setting=goalsSettings.gm_create_multiple_goals_setting)
        menuData.AddRadioButton('5', 5, setting=goalsSettings.gm_create_multiple_goals_setting)
        menuData.AddRadioButton('10', 10, setting=goalsSettings.gm_create_multiple_goals_setting)
        menuData.AddRadioButton('25', 25, setting=goalsSettings.gm_create_multiple_goals_setting)
        return menuData

    def Prepare_LoadingIndicator_(self):
        super(CorporationWindow, self).Prepare_LoadingIndicator_()
        self.sr.loadingParent.padLeft = 58


class CorpWindowSideNavigationEntry(SideNavigationEntry):

    def GetHint(self):
        hints = []
        if self.hint:
            hints.append(self.hint)
        if self.entry_id in corpPanelConst.ACCESSIBLE_IF_HAS_ROLE:
            role_id = corpPanelConst.ACCESSIBLE_IF_HAS_ROLE[self.entry_id]
            hints.append(GetByLabel('UI/Corporations/CorporationWindow/AccessibleWithRole', role_name=get_role_name(role_id)))
        if self.entry_id in corpPanelConst.ACCESSIBLE_IF_HAS_GRANTABLE_ROLES:
            hints.append(GetByLabel('UI/Corporations/CorporationWindow/AccessibleIfHasGrantableRoles'))
        return u'\n\n'.join(hints)
