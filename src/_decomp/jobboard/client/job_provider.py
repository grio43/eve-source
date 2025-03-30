#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\job_provider.py
import abc
import uthread2
import logging
import gametime
from metadata.common.content_tags import get_content_tag_as_object
from jobboard.client import get_job_board_service, job_board_signals
from jobboard.client.provider_type import get_job_id
from jobboard.client.job_board_settings import get_display_feature_setting
logger = logging.getLogger('job_board')

class JobProvider(object):
    __metaclass__ = abc.ABCMeta
    PROVIDER_ID = 'job'
    PROVIDER_CONTENT_TAGS = []
    FEATURE_PAGE_CLASS = None
    __notifyevents__ = []

    @classmethod
    def get_job_id(cls, instance_id):
        return get_job_id(cls.PROVIDER_ID, instance_id)

    def __init__(self, job_storage):
        self._job_storage = job_storage
        self._jobs = {}
        self._is_dirty = True
        self._is_registered = False
        self._fetching = False
        self._enabled = self._should_enable()
        self._register_availability()
        if self.PROVIDER_CONTENT_TAGS:
            self._display_feature_setting = get_display_feature_setting(self.PROVIDER_CONTENT_TAGS[0])
            self._display_feature_setting.on_change.connect(self._display_feature_setting_changed)
        else:
            self._display_feature_setting = None
        if self._enabled:
            self._register_events()
        self._refresh_on_init()

    @property
    def is_enabled(self):
        return self._enabled

    @property
    def is_dirty(self):
        return self._is_dirty

    @property
    def service(self):
        return get_job_board_service()

    @property
    def feature_tag(self):
        feature_tag_id = self.feature_tag_id
        if feature_tag_id:
            return get_content_tag_as_object(feature_tag_id)

    @property
    def feature_tag_id(self):
        if self.PROVIDER_CONTENT_TAGS:
            return self.PROVIDER_CONTENT_TAGS[0]

    @property
    def is_hidden(self):
        if not self.is_enabled:
            return True
        if self._display_feature_setting:
            return not self._display_feature_setting.get()
        return False

    @abc.abstractmethod
    def _get_instance_id(self, content):
        pass

    @abc.abstractmethod
    def _get_all_content(self):
        pass

    @abc.abstractmethod
    def _construct_job(self, job_id, content):
        pass

    def close(self):
        self._unregister_availability()
        self._unregister_events()
        if self._display_feature_setting:
            self._display_feature_setting.on_change.disconnect(self._display_feature_setting_changed)
        for job in self._jobs.values():
            job.clear()

        self._jobs.clear()
        self._is_dirty = True
        self._fetching = False

    def get_jobs(self):
        self.wait_for_provider()
        return self._jobs

    def get_tracked_jobs(self):
        result = []
        tracked_job_ids = self.get_tracked_job_ids()
        jobs = self.get_jobs()
        for tracked_job_id in tracked_job_ids:
            job = jobs.get(tracked_job_id, None)
            if job:
                result.append(job)

        return result

    def wait_for_provider_by_tags(self, content_tag_ids):
        if any((content_tag_id in self.PROVIDER_CONTENT_TAGS for content_tag_id in content_tag_ids)):
            self.wait_for_provider()

    def wait_for_provider(self, refresh_jobs = True):
        if not self._enabled:
            return
        if self._is_dirty and refresh_jobs:
            self.refresh_jobs()
        while self._fetching:
            uthread2.Yield()

    def try_fetch_job(self, job_id):
        self.wait_for_provider()
        return self.get_job(job_id)

    def get_job(self, job_id):
        return self._jobs.get(job_id, None)

    def set_dirty(self):
        self._is_dirty = True

    def get_tracked_job_ids(self):
        tracked_jobs = settings.char.ui.Get(self._tracked_setting_id, {})
        if isinstance(tracked_jobs, list):
            return {job_id:None for job_id in tracked_jobs}
        return tracked_jobs

    def toggle_tracked_job_by_player(self, job):
        if job.job_id not in self.get_tracked_job_ids():
            self.add_tracked_job(job, set_expanded=True)
            self.service.notify_of_job_tracked(job)
        else:
            self.remove_tracked_job(job)
            self.service.notify_of_job_untracked(job)

    def add_tracked_job(self, job, set_expanded = True):
        job_id = job.job_id
        if set_expanded:
            sm.GetService('infoPanel').SetExpandedMission('opportunities', job_id)
        tracked_job_ids = self.get_tracked_job_ids()
        tracked_job_ids[job_id] = gametime.GetWallclockTime()
        self._set_tracked_job_ids(tracked_job_ids)
        job.on_tracked()

    def remove_tracked_job(self, job):
        expanded_mission = sm.GetService('infoPanel').GetExpandedMission()
        if expanded_mission and expanded_mission['missionID'] == job.job_id:
            sm.GetService('infoPanel').SetExpandedMission('opportunities', -1)
        tracked_job_ids = self.get_tracked_job_ids()
        tracked_job_ids.pop(job.job_id, None)
        self._set_tracked_job_ids(tracked_job_ids)
        job.on_untracked()

    def get_tracked_job_timestamp(self, job_id):
        tracked_job_ids = self.get_tracked_job_ids()
        return tracked_job_ids.get(job_id, None)

    def set_tracked_job_timestamp(self, job_id, timestamp):
        tracked_job_ids = self.get_tracked_job_ids()
        tracked_job_ids[job_id] = timestamp
        settings.char.ui.Set(self._tracked_setting_id, tracked_job_ids)

    def _has_tracked_jobs(self):
        return bool(self.get_tracked_job_ids())

    def _update_provider_state(self, enabled):
        if self._enabled == enabled:
            return
        self._enabled = enabled
        if enabled:
            self._register_events()
            self._invalidate_cache()
        else:
            self._unregister_events()
            self._remove_all_jobs()
        job_board_signals.on_job_provider_state_changed(self)

    @uthread2.debounce(0.2)
    def _update_jobs(self, jobs = None, update_state = False, **kwargs):
        for job in jobs or self._jobs.values():
            job.update(**kwargs)
            if update_state:
                job_board_signals.on_job_state_changed(job)

    def refresh_jobs(self):
        if not self._enabled or self._fetching:
            return
        if not session.charid:
            logger.warning('No character logged in when refreshing provider %s', self.PROVIDER_ID)
            return
        self._fetching = True
        uthread2.start_tasklet(self.__refresh_jobs)

    def __refresh_jobs(self):
        logger.info('Refreshing provider %s', self.PROVIDER_ID)
        self._fetching = True
        valid_job_ids = set()
        try:
            all_content = self._get_all_content()
        except Exception as e:
            logger.exception('Failed to fetch jobs for provider %s - e=%s', self.PROVIDER_ID, e)
            self._fetching = False
            return

        for content in all_content or []:
            job = self._create_job(content)
            if job:
                valid_job_ids.add(job.job_id)

        for job_id in self._jobs.keys():
            if job_id not in valid_job_ids:
                self._remove_job(job_id)

        self._is_dirty = False
        self._fetching = False
        self._on_jobs_refreshed()

    def _on_jobs_refreshed(self):
        self._cleanup_tracked_jobs()

    def _create_job(self, content):
        if not self._enabled or not content:
            return
        job_id = self.get_job_id(self._get_instance_id(content))
        if job_id in self._jobs:
            job = self._jobs[job_id]
            job.update(content)
        else:
            try:
                job = self._construct_job(job_id, content)
            except Exception as e:
                logger.exception('Failed to construct job e=%s', e)
                job = None

            if job:
                self._add_job(job)
        return job

    def _add_job(self, job):
        self._jobs[job.job_id] = job
        self._job_storage.add_job(job)

    def _remove_job(self, job_id):
        job = self._jobs.pop(job_id, None)
        if job:
            job.on_remove()
            if job_id in self.get_tracked_job_ids():
                self.remove_tracked_job(job)
        self._job_storage.remove_job(job_id)

    def _remove_all_jobs(self):
        for job_id in self._jobs.keys():
            self._remove_job(job_id)

    def _register_events(self):
        if self._is_registered:
            return
        self._register_slots()
        self._is_registered = True

    def _unregister_events(self):
        if not self._is_registered:
            return
        self._unregister_slots()
        self._is_registered = False

    def _register_availability(self):
        pass

    def _unregister_availability(self):
        pass

    def _register_slots(self):
        job_board_signals.on_job_viewed.connect(self._on_job_viewed)
        job_board_signals.on_job_window_initializing.connect(self._on_window_initializing)
        job_board_signals.on_job_window_maximized.connect(self._on_window_maximized)
        sm.RegisterNotify(self)

    def _unregister_slots(self):
        job_board_signals.on_job_viewed.disconnect(self._on_job_viewed)
        job_board_signals.on_job_window_initializing.disconnect(self._on_window_initializing)
        job_board_signals.on_job_window_maximized.disconnect(self._on_window_maximized)
        sm.UnregisterNotify(self)

    def _should_enable(self):
        return True

    def _display_feature_setting_changed(self, *args, **kwargs):
        job_board_signals.on_job_provider_state_changed(self)
        self._update_jobs(update_state=True)
        if self.is_dirty:
            self._invalidate_cache()

    def _on_job_viewed(self, job_id):
        if self._is_dirty and job_id in self._jobs:
            self.refresh_jobs()

    def _invalidate_cache(self):
        if self._should_refresh_on_invalidate():
            self.refresh_jobs()
        else:
            self.set_dirty()

    def _should_refresh_on_invalidate(self):
        if self._has_tracked_jobs():
            return True
        if self.is_hidden:
            return False
        return self.service.is_open

    def _refresh_on_init(self):
        if self._should_refresh_on_init():
            self.refresh_jobs()
            return True
        return False

    def _should_refresh_on_init(self):
        return self._has_tracked_jobs()

    def _on_window_initializing(self):
        if self._should_refresh_on_window_initializing():
            self.refresh_jobs()

    def _should_refresh_on_window_initializing(self):
        return self.is_dirty and not self.is_hidden

    def _on_window_maximized(self):
        if self._should_refresh_on_window_maximized():
            self.refresh_jobs()

    def _should_refresh_on_window_maximized(self):
        return self.is_dirty and not self.is_hidden

    def _cleanup_tracked_jobs(self):
        tracked_job_ids = self.get_tracked_job_ids()
        if not tracked_job_ids:
            return
        requires_update = False
        for job_id in tracked_job_ids.keys():
            if job_id in self._jobs and self._jobs[job_id].is_trackable:
                continue
            if not job_id.startswith(self.PROVIDER_ID):
                continue
            tracked_job_ids.pop(job_id)
            requires_update = True

        if requires_update:
            self._set_tracked_job_ids(tracked_job_ids)
        else:
            sm.GetService('infoPanel').UpdateJobBoardPanel()

    def _set_tracked_job_ids(self, tracked_job_ids):
        settings.char.ui.Set(self._tracked_setting_id, tracked_job_ids)
        job_board_signals.on_tracked_jobs_changed()

    @property
    def _tracked_setting_id(self):
        return 'tracked_opportunities_{}'.format(self.PROVIDER_ID)
