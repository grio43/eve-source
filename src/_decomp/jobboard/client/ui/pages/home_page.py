#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\pages\home_page.py
import carbonui
import eveicon
import eveui
import evetypes
import localization
import uthread2
from carbonui import Align
from carbonui.uicore import uicore
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
from eve.client.script.ui.shared.cloneGrade import ORIGIN_OPPORTUNITIES
from eve.client.script.ui.shared.neocom.corporation.corpPanelConst import CorpPanel
from eve.common.script.sys.idCheckers import IsPlayerCorporation
from inventorycommon.const import typeMercenaryDenManagementSkill
from jobboard.client import get_job_board_service, job_board_signals
from jobboard.client.provider_type import ProviderType
from jobboard.client.ui.analytics import ANALYTICS_OPEN_CORPORATION_PROJECT_HISTORY, ANALYTICS_OPEN_CORPORATION_FINDER, ANALYTICS_OPEN_AGENCY_HOMEFRONT, ANALYTICS_OPEN_AGENCY_MISSIONS, ANALYTICS_OPEN_FACTIONAL_WARFARE_ENLISTMENT, ANALYTICS_OPEN_MTO, ANALYTICS_OPEN_AGENCY_MTO
from jobboard.client.ui.card_section import FeatureCardSection
from jobboard.client.ui.career_path_section import CareerPathSection
from jobboard.client.ui.pages.base_page import BasePage
from jobboard.client.features.daily_goals.home_page_section import DailyGoalsHomePageSection
from jobboard.client.features.seasons.home_page_section import SeasonHomePageSection
from metadata.common.content_tags import get_content_tags_as_objects, get_content_tag_as_object, ContentTags
from sovereignty.mercenaryden.client.mercenary_den_signals import on_activity_started_notice, on_activity_removed_notice, on_activity_completed_notice, on_activity_expiry_changed_notice
from sovereignty.mercenaryden.client.repository import get_mercenary_den_repository
from sovereignty.mercenaryden.common.errors import GenericError, ServiceUnavailable

class HomePage(BasePage):
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self, window_controller, **kwargs):
        self._window_controller = window_controller
        super(HomePage, self).__init__(**kwargs)
        self._update_search_section()

    def _register(self):
        sm.RegisterNotify(self)
        super(HomePage, self)._register()
        job_board_signals.on_content_tag_count_updated.connect(self._on_content_tag_count_updated)
        job_board_signals.on_job_provider_state_changed.connect(self._on_job_provider_state_changed)

    def _unregister(self):
        sm.UnregisterNotify(self)
        super(HomePage, self)._unregister()
        job_board_signals.on_content_tag_count_updated.disconnect(self._on_content_tag_count_updated)
        job_board_signals.on_job_provider_state_changed.disconnect(self._on_job_provider_state_changed)

    def _on_job_provider_state_changed(self, provider):
        if provider.PROVIDER_ID == ProviderType.DAILY_GOALS:
            self._header_container.Flush()
            self._construct_header()

    @uthread2.debounce(0.2)
    def _on_content_tag_count_updated(self):
        self._update_search_section()

    def _update_search_section(self):
        jobs = self._service.get_available_jobs()
        self._search_section.update(len(jobs), get_content_tags_as_objects(self._service.get_available_content_tags()))

    def _construct_header(self):
        provider = get_job_board_service().get_provider(ProviderType.DAILY_GOALS)
        if not provider.is_hidden:
            DailyGoalsHomePageSection(parent=self._header_container, align=Align.TOTOP, padBottom=16)

    def _construct_filters(self):
        self._search_section = TopSearchBar(parent=self._filters_container, controller=self._window_controller.page_controller, padBottom=16)

    def _construct_content(self):
        SeasonHomePageSection(parent=self._content_container, padBottom=24)
        self._construct_category(provider_id=ProviderType.STORYLINES)
        self._construct_category(provider_id=ProviderType.ESCALATION_SITES)
        self._construct_category(provider_id=ProviderType.CORPORATION_GOALS)
        self._construct_category(provider_id=ProviderType.EPIC_ARCS)
        self._construct_category(provider_id=ProviderType.AGENT_MISSIONS)
        CareerPathSection(parent=self._content_container, padBottom=24)
        self._construct_category(provider_id=ProviderType.FACTIONAL_WARFARE)
        self._construct_category(provider_id=ProviderType.PIRATE_INSURGENCIES)
        self._construct_category(provider_id=ProviderType.HOMEFRONT_OPERATIONS)
        self._construct_category(provider_id=ProviderType.COMBAT_ANOMALIES)
        self._construct_category(provider_id=ProviderType.ORE_ANOMALIES)
        self._construct_category(provider_id=ProviderType.ICE_BELTS)
        self._construct_category(provider_id=ProviderType.MERCENARY_TACTICAL_OPS)
        self._construct_advert(provider_id=ProviderType.CORPORATION_GOALS, section_class=CorpProjectsAdvert)
        self._construct_advert(provider_id=ProviderType.AGENT_MISSIONS, info={'text': localization.GetByLabel('UI/Opportunities/AgentMissionsEmpty'),
         'button_label': localization.GetByLabel('UI/Opportunities/OpenAgency'),
         'button_action': lambda *args, **kwargs: self._open_agency(contentGroupConst.contentGroupMissions),
         'button_analyticID': ANALYTICS_OPEN_AGENCY_MISSIONS})
        self._construct_advert(provider_id=ProviderType.FACTIONAL_WARFARE_ENLISTMENT, section_class=FactionalWarfareEnlistmentAdvert)
        self._construct_advert(provider_id=ProviderType.HOMEFRONT_OPERATIONS, info={'text': localization.GetByLabel('UI/Opportunities/DungeonsEmpty'),
         'button_label': localization.GetByLabel('UI/Opportunities/OpenAgency'),
         'button_action': lambda *args, **kwargs: self._open_agency(contentGroupConst.contentGroupHomefrontSites),
         'button_analyticID': ANALYTICS_OPEN_AGENCY_HOMEFRONT})
        self._construct_advert(ProviderType.MERCENARY_TACTICAL_OPS, section_class=MercenaryTacticalOperationsAdvert)

    def _construct_category(self, provider_id, section_class = FeatureCardSection):
        provider = get_job_board_service().get_provider(provider_id)
        primary_content_tag = provider.feature_tag
        primary_content_tag_id = primary_content_tag.id
        section_class(parent=self._content_container, padBottom=24, title=primary_content_tag.title, icon=primary_content_tag.icon, view_all_callback=lambda : self._view_all_category(primary_content_tag_id), hide_empty=True, content_tag_id=primary_content_tag_id, provider=provider)

    def _construct_advert(self, provider_id, info = None, section_class = None):
        provider = get_job_board_service().get_provider(provider_id)
        primary_content_tag = provider.feature_tag
        primary_content_tag_id = primary_content_tag.id
        section_class = section_class or FeatureAdvert
        section_class(parent=self._content_container, padBottom=24, title=primary_content_tag.title, icon=primary_content_tag.icon, view_all_callback=lambda : self._view_all_category(primary_content_tag_id), hide_empty=True, content_tag_id=primary_content_tag_id, provider=provider, info=info)

    def _view_all_category(self, content_tag_id):
        self._service.open_browse_page(content_tag_id=content_tag_id)

    def _open_agency(self, content_group_id):
        AgencyWndNew.OpenAndShowContentGroup(contentGroupID=content_group_id)


class TopSearchBar(eveui.Container):
    default_align = Align.TOTOP
    default_height = 24

    def __init__(self, controller, *args, **kwargs):
        super(TopSearchBar, self).__init__(*args, **kwargs)
        self._controller = controller
        self._available_content_tags = {}
        self._layout()

    def update(self, job_count, content_tags):
        self._label.text = localization.GetByLabel('UI/Opportunities/OpportunitiesAmount', amount=job_count)
        available_content_tags = {tag_id:tag for tag_id, tag in content_tags.iteritems()}
        self._available_content_tags = available_content_tags

    def _layout(self):
        self._search_field = eveui.SingleLineEditText(parent=self, align=eveui.Align.to_right, width=150, hintText=localization.GetByLabel('UI/Common/Search'), OnReturn=self._search_submitted, texturePath=eveicon.search)
        self._search_field.GetSuggestions = self._get_search_suggestions
        self._search_field.OnHistoryClick = self._search_submitted
        label_container = eveui.Container(parent=self, align=eveui.Align.to_all)
        self._label = carbonui.TextHeader(parent=label_container, align=eveui.Align.center_left, maxLines=1, autoFadeSides=16)

    def _search_submitted(self, *args, **kwargs):
        available_tags = {tag.title:tag.id for tag in self._available_content_tags.values()}
        if self._search_field.text in available_tags:
            self._controller.add_content_tag(available_tags[self._search_field.text])
        else:
            self._controller.add_keyword(self._search_field.text)
        self._search_field.Clear()

    def _get_search_suggestions(self):
        return [ tag.title for tag in self._available_content_tags.values() ]


class FeatureAdvert(FeatureCardSection):
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top
    default_state = eveui.State.normal
    default_clipChildren = True

    def __init__(self, title, icon = None, provider = None, info = None, *args, **kwargs):
        self._info = info
        self._fallback_frame = None
        super(FeatureAdvert, self).__init__(title=title, icon=icon, provider=provider, *args, **kwargs)

    def _construct_cards(self):
        if bool(self._jobs_by_id) or not self._info:
            self.display = False
            return
        self.display = True
        self._fallback_frame = eveui.Frame(bgParent=self._cards_container, texturePath='res:/UI/Texture/classes/Opportunities/card_mask.png', cornerSize=16, color=eveThemeColor.THEME_FOCUSDARK, opacity=0.1)
        top = eveui.Container(parent=self._cards_container, align=eveui.Align.to_top_prop, height=0.5, padding=8)
        bottom = eveui.Container(parent=self._cards_container, align=eveui.Align.to_all, padding=8)
        carbonui.TextBody(parent=top, align=eveui.Align.to_bottom, textAlign=carbonui.TextAlign.CENTER, text=self._info['text'])
        button = eveui.Button(parent=bottom, align=eveui.Align.center_top, label=self._info.get('button_label', ''), func=self._info.get('button_action'), texturePath=self._info.get('button_icon'), analyticID=self._info.get('button_analyticID'), style=self._info.get('button_style', carbonui.ButtonStyle.NORMAL))
        if not self._info.get('show_button', True):
            button.display = False

    def OnColorThemeChanged(self):
        super(FeatureAdvert, self).OnColorThemeChanged()
        if self._fallback_frame:
            self._fallback_frame.rgb = eveThemeColor.THEME_FOCUSDARK[:3]


class CorpProjectsAdvert(FeatureAdvert):

    def __init__(self, *args, **kwargs):
        kwargs['title'] = self._get_title()
        kwargs['info'] = self._get_info()
        super(CorpProjectsAdvert, self).__init__(*args, **kwargs)

    def _on_job_provider_state_changed(self, provider):
        if self._provider_id == provider.PROVIDER_ID:
            self._info = self._get_info()
            self._title = self._get_title()
            self._title_label.text = self._title
            self._refresh()

    def _get_info(self):
        if session.corpid and IsPlayerCorporation(session.corpid):
            return {'text': localization.GetByLabel('UI/Opportunities/CorpProjectsEmpty'),
             'button_label': localization.GetByLabel('UI/Opportunities/OpenCorporationProjects'),
             'button_action': self._open_corporation_project_history,
             'button_analyticID': ANALYTICS_OPEN_CORPORATION_PROJECT_HISTORY}
        else:
            return {'text': localization.GetByLabel('UI/Opportunities/CorpProjectsEmptyNoCorp'),
             'button_label': localization.GetByLabel('UI/Opportunities/OpenCorporationRecruitment'),
             'button_action': self._open_corporation_finder,
             'button_analyticID': ANALYTICS_OPEN_CORPORATION_FINDER}

    def _get_title(self):
        corporation_projects_title = None
        if session.corpid and IsPlayerCorporation(session.corpid):
            corp_info = cfg.eveowners.Get(session.corpid)
            if corp_info:
                corporation_projects_title = localization.GetByLabel('UI/Opportunities/BrowseCorporationProjectsWithName', corporation_name=corp_info.ownerName)
        return corporation_projects_title or localization.GetByLabel('UI/Opportunities/BrowseCorporationProjects')

    def _open_corporation_project_history(self, *args, **kwargs):
        sm.GetService('corpui').Show(CorpPanel.PROJECTS)

    def _open_corporation_finder(self, *args, **kwargs):
        sm.GetService('corpui').Show(CorpPanel.RECRUITMENT_SEARCH)


class FactionalWarfareEnlistmentAdvert(FeatureAdvert):

    def __init__(self, *args, **kwargs):
        content_tag = get_content_tag_as_object(ContentTags.feature_factional_warfare)
        kwargs['title'] = content_tag.title
        kwargs['icon'] = content_tag.icon
        super(FactionalWarfareEnlistmentAdvert, self).__init__(*args, **kwargs)
        self._info = self._get_info()

    def _on_job_provider_state_changed(self, provider):
        if self._provider_id == provider.PROVIDER_ID:
            self._info = self._get_info()
            self._refresh()

    def _get_info(self):
        if self._provider.is_hidden:
            return None
        else:
            is_enlisted = bool(sm.GetService('fwEnlistmentSvc').GetMyFaction())
            if is_enlisted:
                return None
            return {'text': localization.GetByLabel('UI/Opportunities/FactionalWarfareEmpty'),
             'button_label': localization.GetByLabel('UI/PirateInsurgencies/openFactionSelection'),
             'button_action': lambda *args, **kwargs: sm.GetService('cmd').OpenFwEnlistment(),
             'button_icon': 'res:/UI/Texture/WindowIcons/factionalwarfare.png',
             'button_analyticID': ANALYTICS_OPEN_FACTIONAL_WARFARE_ENLISTMENT}


class MercenaryTacticalOperationsAdvert(FeatureAdvert):

    def __init__(self, *args, **kwargs):
        import logging
        self.logger = logging.getLogger(__name__)
        self.logger.info('MercenaryTacticalOperationsAdvert')
        content_tag = get_content_tag_as_object(ContentTags.feature_mercenary_tactical_ops)
        kwargs['title'] = content_tag.title
        kwargs['icon'] = content_tag.icon
        super(MercenaryTacticalOperationsAdvert, self).__init__(*args, **kwargs)
        self._info = self._get_info()
        self._refresh()

    def _on_job_provider_state_changed(self, provider):
        if self._provider_id == provider.PROVIDER_ID:
            self._info = self._get_info()
            self._refresh()

    def _get_info(self):
        if self._provider.is_hidden:
            return
        is_omega = sm.GetService('cloneGradeSvc').IsOmega()
        skill_level = sm.GetService('skills').GetMyLevel(typeMercenaryDenManagementSkill)
        has_mercenary_den_skills = skill_level is not None and skill_level > 0
        den_ids_list = []
        try:
            den_ids_list = get_mercenary_den_repository().get_my_mercenary_dens_ids()
        except ServiceUnavailable as e:
            self.logger.warning('Could not get the list of mercenary den ids, service not available: %s', e)
        except GenericError as e:
            self.logger.error('Could not get the list of mercenary den ids, error: %s', e)

        has_mercenary_dens = len(den_ids_list) > 0
        can_run_mtos = has_mercenary_dens
        if can_run_mtos:
            return
        omega_and_skill_text = localization.GetByLabel('UI/Opportunities/MTOAdvertSkillsAndOmega', skill_name=evetypes.GetName(typeMercenaryDenManagementSkill))
        if not is_omega:
            return {'text': omega_and_skill_text,
             'button_label': localization.GetByLabel('Tooltips/SkillPlanner/UpgradeToOmega'),
             'button_action': self.open_buy_omega,
             'button_icon': eveicon.omega,
             'button_analyticID': ANALYTICS_OPEN_MTO,
             'button_style': carbonui.ButtonStyle.MONETIZATION}
        elif not has_mercenary_den_skills:
            return {'text': omega_and_skill_text,
             'button_label': localization.GetByLabel('UI/Agency/MercDen/OpenSkillTraining'),
             'button_action': self.open_skill_training,
             'button_icon': eveicon.skill_book,
             'button_analyticID': ANALYTICS_OPEN_MTO}
        else:
            return {'text': localization.GetByLabel('UI/Opportunities/MTOAdvertDeployMercenaryDens'),
             'button_label': localization.GetByLabel('UI/Opportunities/OpenAgency'),
             'button_action': self.open_agency_to_mercenary_den,
             'button_analyticID': ANALYTICS_OPEN_AGENCY_MTO}

    def open_skill_training(self, *args):
        uicore.cmd.OpenSkillsWindow()

    def open_buy_omega(self, *args):
        uicore.cmd.OpenCloneUpgradeWindow(origin=ORIGIN_OPPORTUNITIES)

    def open_agency_to_mercenary_den(self, *args):
        AgencyWndNew.OpenAndShowContentGroup(contentGroupID=contentGroupConst.contentGroupMercDens)
