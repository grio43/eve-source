#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corpPanelConst.py
import eveicon
from eve.client.script.ui.shared.pointerTool import pointerToolConst
from eve.common.lib import appConst
from itertoolsext.Enum import Enum

@Enum

class CorpPanel:
    CORPORATION = 'corporation'
    ALLIANCES = 'alliances'
    ADMINISTRATION = 'administration'
    CORP_GENERAL = 'corp_general'
    CORP_RECRUITMENT = 'corp_recruitment'
    CORP_MEMBERS = 'corp_members'
    CORP_STANDINGS = 'corp_standings'
    CORP_WARS = 'corp_wars'
    CORP_VOTING = 'corp_voting'
    ADMIN_WARS = 'admin_wars'
    ADMIN_RECRUITMENT = 'admin_recruitment'
    ADMIN_MEMBERS = 'admin_members'
    ADMIN_GENERAL = 'admin_general'
    MY_CORPORATION = 'home'
    PROJECTS = 'corpgoals'
    KILLREPORTS = 'killreports'
    CONTACTS = 'corpContacts'
    NPC_STANDINGS = 'corpNPCStandings'
    BULLETINS = 'bulletin'
    RECRUITMENT_SEARCH = 'search'
    RECRUITMENT_APPLICATIONS = 'corpApplications'
    RECRUITMENT_ADS = 'corpRecruitmentAds'
    MY_APPLICATIONS = 'myApplications'
    WARS = 'wars'
    WARS_HOMEPAGE = 'landingPage'
    WARS_OUR = 'our'
    WARS_ALL = 'all'
    WARS_HISTORY = 'warHistory'
    WARS_MUTUAL_INVITES = 'mutualWarInvites'
    WARS_DIRECT_ENLISTMENT = 'directEnlistment'
    ASSETS = 'accounts'
    STRUCTURE_DESIGN = 'structureDesign'
    SANCTIONABLE = 'sanctionable'
    VOTES = 'votes'
    DECORATIONS = 'decorations'
    AUDITING = 'auditing'
    TITLES = 'titles'
    AUTOKICKS = 'autoKicks'
    ROLEMANAGEMENT = 'newRoles'
    FINDMEMBER = 'findmember'
    MEMBERLIST = 'main'
    ALLIANCES_GENERAL = 'alliances_general'
    ALLIANCES_HOME = 'alliances_home'
    ALLIANCES_BULLETINS = 'alliances_bulletins'
    ALLIANCES_MEMBERS = 'alliances_members'
    ALLIANCES_RELATIONSHIPS_GROUP = 'alliances_relationships_group'
    ALLIANCES_CONTACTS = 'alliancecontactsform'
    ALLIANCES_APPLICATIONS = 'alliances_applications'
    ALLIANCES_BROWSE_ALL = 'alliances_rankings'
    ALLIANCES_SOVEREIGNTY_GROUP = 'alliances_sovereignty_group'
    ALLIANCE_SOVEREIGNTY = 'alliance_sovereignty'
    ALLIANCES_SYSTEMS = 'alliances_systems'
    ALLIANCES_SOVHUBS = 'alliances_sov_hubs'


NAME_BY_PANEL_ID = {CorpPanel.MY_CORPORATION: 'UI/Fleet/FleetRegistry/MyCorporation',
 CorpPanel.WARS: 'UI/Corporations/BaseCorporationUI/OngoingWarsTab',
 CorpPanel.ASSETS: 'UI/Corporations/BaseCorporationUI/Assets',
 CorpPanel.ALLIANCES: 'UI/Corporations/BaseCorporationUI/Alliances',
 CorpPanel.STRUCTURE_DESIGN: 'UI/Personalization/PaintTool/TrySKINRTitle',
 CorpPanel.SANCTIONABLE: 'UI/Corporations/BaseCorporationUI/SanctionableActions',
 CorpPanel.VOTES: 'UI/Corporations/BaseCorporationUI/Votes',
 CorpPanel.DECORATIONS: 'UI/Corporations/BaseCorporationUI/Decorations',
 CorpPanel.AUDITING: 'UI/Corporations/BaseCorporationUI/Auditing',
 CorpPanel.TITLES: 'UI/Corporations/BaseCorporationUI/TitleManagement',
 CorpPanel.AUTOKICKS: 'UI/Corporations/BaseCorporationUI/AutoKickManagement',
 CorpPanel.ROLEMANAGEMENT: 'UI/Corporations/BaseCorporationUI/RoleManagement',
 CorpPanel.MEMBERLIST: 'UI/Corporations/BaseCorporationUI/MemberList',
 CorpPanel.FINDMEMBER: 'UI/Corporations/BaseCorporationUI/FindMemberInRole',
 CorpPanel.ALLIANCES_GENERAL: 'UI/Generic/General',
 CorpPanel.ALLIANCES_RELATIONSHIPS_GROUP: 'UI/Corporations/CorporationWindow/Alliances/Relationships',
 CorpPanel.ALLIANCES_SOVEREIGNTY_GROUP: 'UI/Neocom/Sovereignty',
 CorpPanel.ALLIANCES_APPLICATIONS: 'UI/Corporations/CorporationWindow/Alliances/Applications',
 CorpPanel.ALLIANCES_CONTACTS: 'UI/Corporations/CorporationWindow/Alliances/AllianceContacts',
 CorpPanel.ALLIANCES_BROWSE_ALL: 'UI/Corporations/CorporationWindow/Alliances/AllAlliances',
 CorpPanel.ALLIANCES_HOME: 'UI/Corporations/BaseCorporationUI/MyAlliance',
 CorpPanel.ALLIANCES_SYSTEMS: 'UI/Corporations/CorporationWindow/Alliances/Systems',
 CorpPanel.ALLIANCE_SOVEREIGNTY: 'UI/Corporations/CorporationWindow/Alliances/SovereigntyTab',
 CorpPanel.ALLIANCES_SOVHUBS: 'UI/Corporations/CorporationWindow/Alliances/SovHubs',
 CorpPanel.ALLIANCES_MEMBERS: 'UI/Corporations/CorporationWindow/Alliances/Members',
 CorpPanel.ALLIANCES_BULLETINS: 'UI/Corporations/CorporationWindow/Alliances/Bulletins',
 CorpPanel.KILLREPORTS: 'UI/Corporations/Wars/Killmails/KillReports',
 CorpPanel.BULLETINS: 'UI/Corporations/CorpUIHome/Bulletins',
 CorpPanel.PROJECTS: 'UI/Corporations/Goals/Projects',
 CorpPanel.WARS_HOMEPAGE: 'UI/Corporations/Wars/WarInfoTab',
 CorpPanel.WARS_HISTORY: 'UI/Corporations/Wars/WarHistory',
 CorpPanel.WARS_MUTUAL_INVITES: 'UI/Corporations/Wars/MutualWarInvitesTab',
 CorpPanel.WARS_DIRECT_ENLISTMENT: 'UI/Corporations/Wars/DirectEnlistment',
 CorpPanel.CONTACTS: 'UI/Corporations/CorporationWindow/Standings/CorpContacts',
 CorpPanel.NPC_STANDINGS: 'UI/Corporations/CorporationWindow/Standings/NPCStandings',
 CorpPanel.MY_APPLICATIONS: 'UI/Corporations/CorpApplications/MyApplications',
 CorpPanel.RECRUITMENT_ADS: 'UI/Corporations/CorporationWindow/Recruitment/CorporationAds',
 CorpPanel.RECRUITMENT_APPLICATIONS: 'UI/Corporations/CorpApplications/ApplicationsToCorp',
 CorpPanel.RECRUITMENT_SEARCH: 'UI/Corporations/BaseCorporationUI/FindNewCorporation',
 CorpPanel.CORP_GENERAL: 'UI/Generic/General',
 CorpPanel.CORP_MEMBERS: 'UI/Corporations/BaseCorporationUI/Members',
 CorpPanel.CORP_STANDINGS: 'UI/InfoWindow/TabNames/Standings',
 CorpPanel.CORP_WARS: 'UI/Corporations/BaseCorporationUI/Wars',
 CorpPanel.CORP_RECRUITMENT: 'UI/Corporations/BaseCorporationUI/Recruitment',
 CorpPanel.CORP_VOTING: 'UI/Corporations/BaseCorporationUI/Voting',
 CorpPanel.ADMIN_WARS: 'UI/Corporations/BaseCorporationUI/Wars',
 CorpPanel.ADMIN_RECRUITMENT: 'UI/Corporations/BaseCorporationUI/Recruitment',
 CorpPanel.ADMIN_MEMBERS: 'UI/Corporations/BaseCorporationUI/Members',
 CorpPanel.ADMIN_GENERAL: 'UI/Generic/General'}
HINT_BY_PANEL_ID = {CorpPanel.PROJECTS: 'UI/Corporations/Goals/ProjectsTabHint',
 CorpPanel.MY_CORPORATION: 'UI/Corporations/BaseCorporationUI/AboutThisCorp',
 CorpPanel.KILLREPORTS: 'UI/Corporations/Wars/Killmails/KillReportsTabHint',
 CorpPanel.BULLETINS: 'UI/Corporations/CorpUIHome/BulletinsTabHint',
 CorpPanel.RECRUITMENT_SEARCH: 'UI/Corporations/BaseCorporationUI/FindNewCorporationTabHint',
 CorpPanel.MY_APPLICATIONS: 'UI/Corporations/CorpApplications/MyApplicationsTabHint',
 CorpPanel.MEMBERLIST: 'UI/Corporations/BaseCorporationUI/MemberListTabHint',
 CorpPanel.DECORATIONS: 'UI/Corporations/BaseCorporationUI/DecorationsTabHint',
 CorpPanel.CONTACTS: 'UI/Corporations/CorporationWindow/Standings/CorpContactsTabHint',
 CorpPanel.NPC_STANDINGS: 'UI/Corporations/BaseCorporationUI/NPCStandingsTabHint',
 CorpPanel.VOTES: 'UI/Corporations/BaseCorporationUI/CorpVotesHint',
 CorpPanel.SANCTIONABLE: 'UI/Corporations/BaseCorporationUI/CorpSanctionableActionsHint',
 CorpPanel.WARS: 'UI/Corporations/BaseCorporationUI/CorpWarsHint',
 CorpPanel.WARS_HOMEPAGE: 'UI/Corporations/Wars/WarInfoTabHint',
 CorpPanel.WARS_HISTORY: 'UI/Corporations/Wars/WarHistoryTabHint',
 CorpPanel.ALLIANCES_HOME: 'UI/Corporations/BaseCorporationUI/MyAllianceTabHint',
 CorpPanel.ALLIANCES_BULLETINS: 'UI/Corporations/CorporationWindow/Alliances/BulletinsTabHint',
 CorpPanel.ALLIANCES_MEMBERS: 'UI/Corporations/CorporationWindow/Alliances/MembersTabHint',
 CorpPanel.ALLIANCES_CONTACTS: 'UI/Corporations/CorporationWindow/Alliances/AllianceContactsTabHint',
 CorpPanel.ALLIANCES_APPLICATIONS: 'UI/Corporations/CorporationWindow/Alliances/ApplicationsTabHint',
 CorpPanel.ALLIANCES_BROWSE_ALL: 'UI/Corporations/CorporationWindow/Alliances/AllAlliancesTabHint',
 CorpPanel.ALLIANCE_SOVEREIGNTY: 'UI/Corporations/CorporationWindow/Alliances/SovereigntyTabHint',
 CorpPanel.ALLIANCES_SOVHUBS: 'UI/Corporations/CorporationWindow/Alliances/SovHubTabHint',
 CorpPanel.ALLIANCES_SYSTEMS: 'UI/Corporations/CorporationWindow/Alliances/SystemsTabHint',
 CorpPanel.FINDMEMBER: 'UI/Corporations/BaseCorporationUI/FindMemberInRoleTabHint',
 CorpPanel.ROLEMANAGEMENT: 'UI/Corporations/BaseCorporationUI/RoleManagementTabHint',
 CorpPanel.AUTOKICKS: 'UI/Corporations/BaseCorporationUI/AutoKickDescription',
 CorpPanel.TITLES: 'UI/Corporations/BaseCorporationUI/TitleManagementTabHint',
 CorpPanel.AUDITING: 'UI/Corporations/BaseCorporationUI/AuditingTabHint',
 CorpPanel.ASSETS: 'UI/Corporations/BaseCorporationUI/CorpAccountsHint',
 CorpPanel.STRUCTURE_DESIGN: 'UI/Corporations/BaseCorporationUI/StructureDesignHint',
 CorpPanel.RECRUITMENT_ADS: 'UI/Corporations/CorporationWindow/Recruitment/CorporationAdsTabHint',
 CorpPanel.RECRUITMENT_APPLICATIONS: 'UI/Corporations/CorpApplications/ApplicationsToCorpTabHint',
 CorpPanel.WARS_MUTUAL_INVITES: 'UI/Corporations/Wars/MutualWarInvitesTabHint',
 CorpPanel.WARS_DIRECT_ENLISTMENT: 'UI/Corporations/Wars/DirectEnlistmentTabHint'}
ICON_BY_PANEL_ID = {CorpPanel.PROJECTS: eveicon.projects,
 CorpPanel.MY_CORPORATION: eveicon.info,
 CorpPanel.KILLREPORTS: eveicon.destroy_capsuleer,
 CorpPanel.BULLETINS: eveicon.bulletins,
 CorpPanel.RECRUITMENT_SEARCH: eveicon.search,
 CorpPanel.MY_APPLICATIONS: eveicon.application,
 CorpPanel.MEMBERLIST: eveicon.people,
 CorpPanel.DECORATIONS: eveicon.medal,
 CorpPanel.CONTACTS: eveicon.corporation_contact,
 CorpPanel.NPC_STANDINGS: eveicon.lp,
 CorpPanel.VOTES: eveicon.vote,
 CorpPanel.SANCTIONABLE: eveicon.sanctionable_actions,
 CorpPanel.WARS: eveicon.ongoing_conflicts,
 CorpPanel.WARS_HOMEPAGE: eveicon.law_of_war,
 CorpPanel.WARS_HISTORY: eveicon.theaters_of_war,
 CorpPanel.ALLIANCES_HOME: eveicon.info,
 CorpPanel.ALLIANCES_BULLETINS: eveicon.bulletins,
 CorpPanel.ALLIANCES_MEMBERS: eveicon.people,
 CorpPanel.ALLIANCES_CONTACTS: eveicon.corporation_contact,
 CorpPanel.ALLIANCES_APPLICATIONS: eveicon.application,
 CorpPanel.ALLIANCES_BROWSE_ALL: eveicon.list_view,
 CorpPanel.ALLIANCE_SOVEREIGNTY: eveicon.sovereignity,
 CorpPanel.ALLIANCES_SOVHUBS: eveicon.sovereignity,
 CorpPanel.ALLIANCES_SYSTEMS: eveicon.solar_system,
 CorpPanel.FINDMEMBER: eveicon.find_member_in_role,
 CorpPanel.ROLEMANAGEMENT: eveicon.role_management,
 CorpPanel.AUTOKICKS: eveicon.auto_removal,
 CorpPanel.TITLES: eveicon.titles,
 CorpPanel.AUDITING: eveicon.audit,
 CorpPanel.ASSETS: eveicon.inventory,
 CorpPanel.STRUCTURE_DESIGN: eveicon.skinr,
 CorpPanel.RECRUITMENT_ADS: eveicon.star,
 CorpPanel.RECRUITMENT_APPLICATIONS: eveicon.application,
 CorpPanel.WARS_MUTUAL_INVITES: eveicon.sword,
 CorpPanel.WARS_DIRECT_ENLISTMENT: eveicon.factional_warfare}
POINTER_UUID_BY_PANEL_ID = {CorpPanel.MY_CORPORATION: pointerToolConst.UNIQUE_NAME_CORP_HOME_TAB,
 CorpPanel.ASSETS: pointerToolConst.UNIQUE_NAME_CORP_ASSETS_TAB,
 CorpPanel.BULLETINS: pointerToolConst.UNIQUE_NAME_CORP_BULLETIN_TAB,
 CorpPanel.MY_APPLICATIONS: pointerToolConst.UNIQUE_NAME_MY_APPLICATIONS,
 CorpPanel.CORPORATION: pointerToolConst.UNIQUE_NAME_CORP_CORPORATION_TAB,
 CorpPanel.ADMINISTRATION: pointerToolConst.UNIQUE_NAME_CORP_ADMIN_TAB,
 CorpPanel.ALLIANCES: pointerToolConst.UNIQUE_NAME_CORP_ALLIANCES_TAB,
 CorpPanel.PROJECTS: pointerToolConst.UNIQUE_NAME_CORP_PROJECTS,
 CorpPanel.RECRUITMENT_SEARCH: pointerToolConst.UNIQUE_NAME_FIND_NEW_CORP}
ACCESSIBLE_IF_HAS_ROLE = {CorpPanel.ADMIN_MEMBERS: appConst.corpRolePersonnelManager,
 CorpPanel.AUTOKICKS: appConst.corpRoleDirector,
 CorpPanel.TITLES: appConst.corpRoleDirector,
 CorpPanel.AUDITING: appConst.corpRoleAuditor,
 CorpPanel.ASSETS: appConst.corpRoleAccountant,
 CorpPanel.STRUCTURE_DESIGN: appConst.corpRoleBrandManager,
 CorpPanel.RECRUITMENT_ADS: appConst.corpRolePersonnelManager,
 CorpPanel.RECRUITMENT_APPLICATIONS: appConst.corpRolePersonnelManager,
 CorpPanel.WARS_MUTUAL_INVITES: appConst.corpRoleDirector,
 CorpPanel.WARS_DIRECT_ENLISTMENT: appConst.corpRoleDirector}
ACCESSIBLE_IF_HAS_GRANTABLE_ROLES = (CorpPanel.FINDMEMBER,
 CorpPanel.ROLEMANAGEMENT,
 CorpPanel.RECRUITMENT_ADS,
 CorpPanel.RECRUITMENT_APPLICATIONS)
