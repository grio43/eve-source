#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\tag_counter.py
from collections import defaultdict
import uthread2
from jobboard.client import job_board_signals, get_job_board_service

class ContentTagCounter(object):

    def __init__(self):
        self._content_tag_count = defaultdict(int)
        self._primary_feature_tag_count = defaultdict(int)
        job_board_signals.on_job_added.connect(self._on_job_added)
        job_board_signals.on_job_removed.connect(self._on_job_removed)
        job_board_signals.on_job_state_changed.connect(self._on_job_state_changed)

    def __del__(self):
        job_board_signals.on_job_added.disconnect(self._on_job_added)
        job_board_signals.on_job_removed.disconnect(self._on_job_removed)
        job_board_signals.on_job_state_changed.disconnect(self._on_job_state_changed)

    def clear(self):
        self._content_tag_count.clear()
        self._primary_feature_tag_count.clear()

    def get_content_tag_count(self):
        return self._content_tag_count

    def get_feature_tag_count(self):
        return self._primary_feature_tag_count

    def get_content_tag_count_by_id(self, content_tag_id):
        return self._content_tag_count.get(content_tag_id, 0)

    def get_feature_tag_count_by_id(self, content_tag_id):
        return self._primary_feature_tag_count.get(content_tag_id, 0)

    def _on_job_added(self, job):
        if not job.is_available_in_browse:
            return
        self._update_counter()

    def _on_job_removed(self, job):
        self._update_counter()

    def _on_job_state_changed(self, job):
        self._update_counter()

    @uthread2.debounce(0.2)
    def _update_counter(self):
        self._content_tag_count.clear()
        self._primary_feature_tag_count.clear()
        jobs = get_job_board_service().get_available_jobs()
        for job in jobs:
            self._add_to_count(job)

        job_board_signals.on_content_tag_count_updated()

    def _add_to_count(self, job):
        for content_tag_id in job.content_tag_ids:
            self._content_tag_count[content_tag_id] += 1

        feature_tag = job.feature_tag
        if feature_tag:
            self._primary_feature_tag_count[feature_tag.id] += 1
