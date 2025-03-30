#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\job.py
import gametime
import caching
from carbonui.control.contextMenu.menuData import MenuData
import eveicon
from eve.client.script.ui import eveColor
import localization
from jobboard.client.ui.reward_list_entry import JobRewardListEntry
from metadata.common.content_tags import get_content_tags_as_objects, ContentTagTypes
import signals
from jobboard.client import get_job_board_service, job_board_signals
from jobboard.client.drag_data import JobDragData
from jobboard.client.ui.card import JobCard
from jobboard.client.ui.pages.details_page import JobPage
from jobboard.client.ui.info_panel_entry import JobInfoPanelEntry
from jobboard.client.ui.list_entry import JobListEntry
from jobboard.client.util import check_content_tags, add_location_menu_option, add_track_job_menu_option, add_open_job_menu_option
from jobboard.client.relevance_profile import JobRelevanceProfile
from metadata.common.content_tags.const import CONTENT_TAG_TO_CAREER_PATH

class BaseJob(object):
    PAGE_CLASS = JobPage
    CARD_CLASS = JobCard
    LIST_ENTRY_CLASS = JobListEntry
    REWARD_LIST_ENTRY_CLASS = JobRewardListEntry
    INFO_PANEL_ENTRY_CLASS = JobInfoPanelEntry

    def __init__(self, job_id, content_id, provider):
        self._job_id = job_id
        self._content_id = content_id
        self._provider = provider
        self._content_tags = None
        self._last_opened_timestamp = None
        self.is_removed = False
        self.on_job_updated = signals.Signal('on_job_updated')
        self._register()

    def update(self, *args, **kwargs):
        self.on_job_updated()

    def opened(self):
        self._last_opened_timestamp = gametime.GetWallclockTime()
        job_board_signals.on_job_viewed(self.job_id)

    def on_remove(self):
        self.clear()
        if self.is_removed:
            return
        self.is_removed = True
        self.update()
        job_board_signals.on_job_state_changed(self)

    def clear(self):
        self._unregister()

    @property
    def job_id(self):
        return self._job_id

    @property
    def provider_id(self):
        return self._provider.PROVIDER_ID

    @property
    def provider(self):
        return self._provider

    @property
    def content_id(self):
        return self._content_id

    @property
    def content_tag_ids(self):
        return self.content_tags.keys()

    @property
    def content_tags(self):
        if self._content_tags is None:
            self._initialize_content_tags()
        return self._content_tags

    @property
    def title(self):
        return ''

    @property
    def subtitle(self):
        return ''

    @property
    def description(self):
        return ''

    @caching.lazy_property
    def feature_tag(self):
        for content_tag in self.content_tags.itervalues():
            if content_tag.tag_type == ContentTagTypes.feature:
                return content_tag

    @property
    def feature_title(self):
        if self.feature_tag:
            return self.feature_tag.title
        return ''

    @property
    def feature_icon(self):
        if self.feature_tag:
            return self.feature_tag.icon

    @property
    def feature_id(self):
        feature_tag = self.feature_tag
        if feature_tag:
            return feature_tag.id

    @caching.lazy_property
    def career_tag(self):
        for content_tag in self.content_tags.itervalues():
            if content_tag.tag_type == ContentTagTypes.career_path:
                return content_tag

    @property
    def career_id(self):
        career_tag = self.career_tag
        if career_tag:
            return career_tag.id

    @property
    def career_path(self):
        return CONTENT_TAG_TO_CAREER_PATH.get(self.career_id, None)

    @property
    def career_title(self):
        if self.career_tag:
            return self.career_tag.title
        return localization.GetByLabel('UI/Generic/Unclassified')

    @property
    def career_icon(self):
        if self.career_tag:
            return self.career_tag.icon
        return eveicon.unclassified

    @property
    def is_trackable(self):
        return False

    @property
    def is_tracked(self):
        return self.job_id in self.provider.get_tracked_job_ids()

    @property
    def is_available_in_active(self):
        return False

    @property
    def is_available_in_browse(self):
        return not self.provider.is_hidden

    @property
    def is_completed(self):
        return False

    @property
    def is_expired(self):
        return False

    @property
    def expiration_time(self):
        return None

    @property
    def location_id(self):
        return None

    @property
    def solar_system_id(self):
        return None

    @property
    def solar_system_name(self):
        if not self.solar_system_id:
            return ''
        else:
            solar_system = cfg.evelocations.Get(self.solar_system_id)
            if solar_system:
                return solar_system.locationName
            return ''

    @property
    def jumps(self):
        return self.get_jumps_away(session.solarsystemid2)

    @property
    def in_same_system(self):
        return self.solar_system_id == session.solarsystemid2

    @property
    def last_opened_timestamp(self):
        return self._last_opened_timestamp

    @property
    def is_open(self):
        return self.service.is_job_open(self.job_id)

    @property
    def is_linkable(self):
        return True

    @property
    def link_title(self):
        return self.title

    @property
    def has_claimable_rewards(self):
        return False

    @property
    def claimable_rewards(self):
        return []

    @property
    def has_claimable_item_reward(self):
        return False

    def claim_rewards(self):
        pass

    @property
    def objective_chain(self):
        return None

    def toggle_tracked_by_player(self):
        self.provider.toggle_tracked_job_by_player(self)

    def add_tracked(self, set_expanded = True):
        self.provider.add_tracked_job(self, set_expanded=set_expanded)

    def remove_tracked(self):
        self.provider.remove_tracked_job(self)

    def get_tracked_timestamp(self):
        return self.provider.get_tracked_job_timestamp(self.job_id)

    def set_tracked_timestamp(self, timestamp):
        return self.provider.set_tracked_job_timestamp(self.job_id, timestamp)

    def on_click(self, *args, **kwargs):
        self.service.open_job(self.job_id)

    def on_tracked(self):
        pass

    def on_untracked(self):
        pass

    def get_cta_buttons(self):
        return []

    def get_buttons(self):
        return []

    def get_drag_data(self):
        if not self.is_linkable:
            return []
        return [JobDragData(self)]

    def get_menu(self):
        data = MenuData()
        solar_system_id = self.solar_system_id
        if solar_system_id:
            add_location_menu_option(data, solar_system_id)
        data.AddSeparator()
        cta_buttons = self.get_cta_buttons()
        for button_info in cta_buttons:
            if not isinstance(button_info, dict):
                continue
            data.AddEntry(text=button_info.get('label', ''), texturePath=button_info.get('icon', None), hint=button_info.get('hint', ''), func=button_info['on_click'], internalName=button_info.get('name', ''))

        add_open_job_menu_option(data, self.job_id)
        data.AddSeparator()
        add_track_job_menu_option(data, self)
        return data

    @property
    def has_menu(self):
        return True

    def construct_entry(self, list_view, *args, **kwargs):
        if list_view:
            return self.construct_list_entry(*args, **kwargs)
        else:
            return self.construct_card(*args, **kwargs)

    def construct_card(self, *args, **kwargs):
        return self.CARD_CLASS(controller=self, *args, **kwargs)

    def construct_list_entry(self, *args, **kwargs):
        return self.LIST_ENTRY_CLASS(controller=self, *args, **kwargs)

    def construct_reward_entry(self, *args, **kwargs):
        return self.REWARD_LIST_ENTRY_CLASS(controller=self, *args, **kwargs)

    def construct_page(self, *args, **kwargs):
        return self.PAGE_CLASS(job=self, *args, **kwargs)

    def get_state_info(self):
        if self.is_completed:
            return {'text': localization.GetByLabel('UI/Generic/Completed'),
             'color': eveColor.SUCCESS_GREEN,
             'icon': eveicon.checkmark}
        if self.is_expired:
            return {'text': localization.GetByLabel('UI/Generic/Expired'),
             'color': eveColor.DANGER_RED,
             'icon': eveicon.hourglass}
        if self.is_removed:
            return {'text': localization.GetByLabel('UI/Opportunities/RemovedState'),
             'color': eveColor.WARNING_ORANGE,
             'icon': eveicon.close}

    def get_relevance_profile(self):
        return JobRelevanceProfile(job=self, override_weights=self._get_relevance_override_weights())

    def get_player_relevance_score(self):
        return self.service.calculate_relevance_score(self.content_tag_ids, self.solar_system_id)

    def check_filters(self, content_tag_ids = None, keywords = None, **kwargs):
        if not check_content_tags(content_tag_ids, self.content_tag_ids):
            return False
        if not self._check_keywords(keywords):
            return False
        return True

    def get_jumps_away(self, solar_system_id):
        if not self.solar_system_id:
            return 0.5
        return sm.GetService('clientPathfinderService').GetAutopilotJumpCount(solar_system_id, self.solar_system_id)

    def _check_keywords(self, keywords):
        if not keywords:
            return True
        title = self.title.lower()
        system_name = self.solar_system_name.lower()
        for keyword in keywords:
            if keyword in title:
                continue
            if system_name and keyword in system_name:
                continue
            return False

        return True

    def _get_content_tag_ids(self):
        return []

    def _initialize_content_tags(self):
        content_tag_ids = self._get_content_tag_ids()
        self._content_tags = get_content_tags_as_objects(content_tag_ids)

    def _get_relevance_override_weights(self):
        return None

    def _register(self):
        pass

    def _unregister(self):
        pass

    @property
    def service(self):
        return get_job_board_service()
