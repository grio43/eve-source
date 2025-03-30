#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\storylines\provider.py
from metadata.common.content_tags import ContentTags
from jobboard.client.job_provider import JobProvider
from jobboard.client.provider_type import ProviderType
from .job import StorylineJob
from .const import NODE_GRAPH_ID_TO_CONTENT_ID

class StorylinesProvider(JobProvider):
    PROVIDER_ID = ProviderType.STORYLINES
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_introductions]
    __notifyevents__ = ['OnNodeGraphStarted', 'OnNodeGraphStopped']

    def _should_refresh_on_init(self):
        return True

    def _refresh_jobs(self):
        self._fetching = True
        for node_graph_id in NODE_GRAPH_ID_TO_CONTENT_ID:
            self._add_job_by_graph_id(node_graph_id)

        self._is_dirty = False
        self._fetching = False

    def _get_instance_id(self, mission):
        return mission['content_id']

    def _get_all_content(self):
        return []

    def _construct_job(self, job_id, mission):
        return StorylineJob(job_id, self, mission)

    def OnNodeGraphStarted(self, instance_id, node_graph_id):
        if node_graph_id in NODE_GRAPH_ID_TO_CONTENT_ID:
            self._add_job_by_graph_id(node_graph_id)

    def OnNodeGraphStopped(self, instance_id, node_graph_id):
        if node_graph_id in NODE_GRAPH_ID_TO_CONTENT_ID:
            self._remove_job(self.get_job_id(NODE_GRAPH_ID_TO_CONTENT_ID[node_graph_id]))

    def _add_job_by_graph_id(self, node_graph_id):
        node_graph = sm.GetService('node_graph').get_active_node_graph_by_id(node_graph_id)
        if not node_graph:
            return
        job = self._create_job({'content_id': NODE_GRAPH_ID_TO_CONTENT_ID[node_graph_id],
         'node_graph': node_graph})
        if job.is_trackable and not job.is_tracked and job.job_id not in self._untracked_job_ids:
            self.add_tracked_job(job, set_expanded=True)

    def add_tracked_job(self, job, set_expanded = True):
        super(StorylinesProvider, self).add_tracked_job(job, set_expanded=True)
        untracked_job_ids = self._untracked_job_ids
        if job.job_id in untracked_job_ids:
            untracked_job_ids.discard(job.job_id)
            settings.char.ui.Set(self._untracked_setting_id, untracked_job_ids)

    def toggle_tracked_job_by_player(self, job):
        if job.job_id in self.get_tracked_job_ids():
            untracked_job_ids = self._untracked_job_ids
            untracked_job_ids.add(job.job_id)
            settings.char.ui.Set(self._untracked_setting_id, untracked_job_ids)
        super(StorylinesProvider, self).toggle_tracked_job_by_player(job)

    @property
    def _untracked_job_ids(self):
        return settings.char.ui.Get(self._untracked_setting_id, set())

    @property
    def _untracked_setting_id(self):
        return 'untracked_opportunities_{}'.format(self.PROVIDER_ID)
