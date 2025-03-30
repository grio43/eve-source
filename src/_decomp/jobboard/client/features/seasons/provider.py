#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\seasons\provider.py
from metadata.common.content_tags import ContentTags
from jobboard.client import job_board_signals
from jobboard.client.job_provider import JobProvider
from jobboard.client.provider_type import ProviderType
from jobboard.client.job_board_settings import get_display_feature_setting
from .feature_page import SeasonsFeaturePage

class SeasonsProvider(JobProvider):
    PROVIDER_ID = ProviderType.SEASONS
    PROVIDER_CONTENT_TAGS = []
    FEATURE_PAGE_CLASS = SeasonsFeaturePage
    __notifyevents__ = ['OnSeasonSelectionUpdated']

    def __init__(self, job_storage):
        self._service = sm.GetService('seasonService')
        super(SeasonsProvider, self).__init__(job_storage)

    @property
    def service(self):
        return self._service

    @property
    def current_season(self):
        return self.service.current_season

    def _should_enable(self):
        current_season = self.current_season
        return bool(current_season) and current_season.feature_tag_id

    def OnSeasonSelectionUpdated(self):
        should_enable = self._should_enable()
        if should_enable and self.is_enabled:
            self._invalidate_cache()
            job_board_signals.on_job_provider_state_changed(self)
        else:
            self._update_provider_state(should_enable)

    def _register_slots(self):
        super(SeasonsProvider, self)._register_slots()
        self._update_display_setting()

    def _unregister_slots(self):
        super(SeasonsProvider, self)._unregister_slots()
        self._update_display_setting()

    def _update_display_setting(self):
        if self._display_feature_setting:
            self._display_feature_setting.on_change.disconnect(self._display_feature_setting_changed)
            self._display_feature_setting = None
        if self.is_enabled:
            self._display_feature_setting = get_display_feature_setting(self.feature_tag_id)
            self._display_feature_setting.on_change.connect(self._display_feature_setting_changed)

    @property
    def feature_tag_id(self):
        current_season = self.current_season
        if current_season:
            return current_season.feature_tag_id
        return ContentTags.feature_seasons

    def _should_refresh_on_init(self):
        return True

    def _should_refresh_on_window_initializing(self):
        return self.is_dirty

    def _get_instance_id(self, challenge):
        return challenge.challenge_id

    def _get_all_content(self):
        return []

    def _construct_job(self, job_id, content):
        return None
