#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\epic_arcs\provider.py
from eve.client.script.ui.shared.epicArcs import epicArcConst
from metadata.common.content_tags import ContentTags
from jobboard.client import job_board_signals
from jobboard.client.job_provider import JobProvider
from jobboard.client.provider_type import ProviderType
from jobboard.client.feature_flag import are_missions_in_job_board_available
from .job import EpicArcJob

class EpicArcsProvider(JobProvider):
    PROVIDER_ID = ProviderType.EPIC_ARCS
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_epic_arcs]
    JOB_CLASS = EpicArcJob
    __notifyevents__ = ['OnEpicArcDataChanged']

    def __init__(self, *args, **kwargs):
        self._epic_arc_service = sm.StartService('epicArc')
        super(EpicArcsProvider, self).__init__(*args, **kwargs)

    def _should_refresh_on_window_initializing(self):
        return self.is_dirty

    def OnEpicArcDataChanged(self):
        self._invalidate_cache()

    def _get_instance_id(self, epic_arc):
        return epic_arc.epicArcID

    def _get_all_content(self):
        return [ epic_arc for epic_arc in self._epic_arc_service.GetEpicArcs() ]

    def _construct_job(self, job_id, epic_arc):
        return EpicArcJob(job_id, self, epic_arc)

    def _register_availability(self):
        job_board_signals.on_missions_feature_availability_changed.connect(self._on_availability_changed)

    def _unregister_availability(self):
        job_board_signals.on_missions_feature_availability_changed.disconnect(self._on_availability_changed)

    def _on_availability_changed(self, _old_value, _new_value):
        self._update_provider_state(are_missions_in_job_board_available())

    def _should_enable(self):
        return are_missions_in_job_board_available()
