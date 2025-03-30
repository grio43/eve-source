#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\job_board_service.py
from carbonui.uicore import uicore
import carbonui.const as uiconst
from metadata.common import ContentTags
from jobboard.client import job_board_signals
from jobboard.client.feature_flag import is_job_board_available
from jobboard.client.messenger import JobBoardMessenger
from jobboard.client.relevance_profile import PlayerRelevanceProfile
from jobboard.client.storage import JobBoardStorage
from jobboard.client.tag_counter import ContentTagCounter
from jobboard.client.open_on_startup import OpenOpportunitiesOnStartup
from jobboard.client.ui.job_board_window import JobBoardWindow, JobDetailsWindow
import logging
from uthread2 import StartTasklet
logger = logging.getLogger(__name__)

class JobBoardService(object):
    __notifyevents__ = ['ProcessSessionReset', 'OnCharacterSelected']

    def __init__(self):
        self._storage = None
        self._player_relevance_profile = None
        self._content_tag_counter = ContentTagCounter()
        self._messenger = JobBoardMessenger(public_gateway=sm.GetService('publicGatewaySvc'))
        self._open_on_startup = OpenOpportunitiesOnStartup()
        self._register()

    def __del__(self):
        self._unregister()

    def _register(self):
        sm.RegisterNotify(self)
        job_board_signals.on_job_completed.connect(self._on_job_completed)
        job_board_signals.on_job_board_feature_availability_changed.connect(self._on_availability_changed)

    def _unregister(self):
        sm.UnregisterNotify(self)
        job_board_signals.on_job_completed.disconnect(self._on_job_completed)
        job_board_signals.on_job_board_feature_availability_changed.disconnect(self._on_availability_changed)

    def OnCharacterSelected(self, *args, **kwargs):
        if session.charid:
            self._open_on_startup.register()
        else:
            self._open_on_startup.unregister()
        self.flush_cache()

    def ProcessSessionReset(self):
        self.flush_cache()

    def _on_availability_changed(self, *args, **kwargs):
        self.flush_cache()

    @property
    def is_available(self):
        return is_job_board_available()

    @property
    def is_open(self):
        job_board_window = JobBoardWindow.GetIfOpen()
        return bool(job_board_window) and not job_board_window.IsMinimized()

    def is_job_open(self, job_id):
        job_board_window = JobBoardWindow.GetIfOpen()
        if job_board_window and job_board_window.is_job_open(job_id):
            return True
        job_details_window = JobDetailsWindow.GetIfOpen(windowInstanceID=job_id)
        return bool(job_details_window)

    @property
    def storage(self):
        if not self._storage:
            self._storage = JobBoardStorage()
            self._player_relevance_profile = PlayerRelevanceProfile()
        return self._storage

    @property
    def player_relevance_profile(self):
        return self._player_relevance_profile

    def toggle_window(self):
        JobBoardWindow.ToggleOpenClose()

    def open_window(self):
        JobBoardWindow.Open()

    def open_browse_page(self, content_tag_id = None, keyword = None):
        JobBoardWindow.Open(page_id='browse', content_tag_id=content_tag_id, keyword=keyword)

    def open_home_page(self):
        JobBoardWindow.Open(page_id='home')

    def open_active_page(self):
        JobBoardWindow.Open(page_id='active')

    def open_job(self, job_id, instanced = None):
        job = self.get_job(job_id, wait=False)
        if instanced is None:
            instanced = bool(uicore.uilib.Key(uiconst.VK_SHIFT))
        if instanced:
            JobDetailsWindow.Open(windowInstanceID=job_id, job_id=job_id, job=job)
        else:
            JobBoardWindow.Open(job_id=job_id)
        self._notify_of_job_viewed(job)

    def get_jobs(self, filters = None, provider_id = None):
        return self.storage.get_jobs(filters, provider_id)

    def get_available_jobs(self, filters = None, provider_id = None):
        return self.storage.get_available_jobs(filters, provider_id)

    def get_active_jobs(self, filters = None):
        return self.storage.get_active_jobs(filters)

    def get_jobs_with_unclaimed_rewards(self, provider_id = None):
        return self.storage.get_jobs_with_unclaimed_rewards(provider_id)

    def get_tracked_jobs(self):
        return self.storage.get_tracked_jobs()

    def get_related_jobs(self, relevance_profile = None):
        return self.storage.get_related_jobs(relevance_profile or self.player_relevance_profile)

    def get_job(self, job_id, wait = True, show_error = True):
        if show_error and not self.is_available:
            uicore.Message('ServiceUnavailable')
            return None
        job = self.storage.get_job(job_id, wait)
        return job

    def get_provider(self, provider_id):
        return self.storage.get_provider(provider_id)

    def get_provider_for_feature_tag(self, feature_tag_id):
        return self.storage.get_provider_for_feature_tag(feature_tag_id)

    def get_content_tag_count(self, content_tag_id):
        if content_tag_id == ContentTags.feature_epic_arcs:
            return self._content_tag_counter.get_feature_tag_count_by_id(content_tag_id)
        return self._content_tag_counter.get_content_tag_count_by_id(content_tag_id)

    def get_available_content_tags(self):
        content_tag_count = self._content_tag_counter.get_content_tag_count()
        return [ content_tag_id for content_tag_id, count in content_tag_count.iteritems() if count > 0 ]

    def calculate_relevance_score(self, content_tag_ids, solar_system_id):
        return self.player_relevance_profile.calculate_relevance_score(content_tag_ids, solar_system_id)

    def add_relevance_score(self, content_tag_ids):
        self.player_relevance_profile.add_content_tag_scores(content_tag_ids)

    def flush_cache(self):
        if self._storage:
            self._storage.close()
        self._storage = None
        self._player_relevance_profile = None
        self._content_tag_counter.clear()

    def _on_job_completed(self, job):
        self._notify_of_job_completed(job)

    def _notify_of_job_viewed(self, job):
        StartTasklet(self._messenger.on_job_viewed, job)

    def notify_of_job_tracked(self, job):
        StartTasklet(self._messenger.on_job_tracked, job)

    def notify_of_job_untracked(self, job):
        StartTasklet(self._messenger.on_job_untracked, job)

    def _notify_of_job_completed(self, job):
        StartTasklet(self._messenger.on_job_completed, job)
