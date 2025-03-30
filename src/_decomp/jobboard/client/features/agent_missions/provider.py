#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\agent_missions\provider.py
import gametime
from eve.common.lib import appConst
from evemissions.client.mission import Mission
from metadata.common.content_tags import ContentTags
from jobboard.client import job_board_signals
from jobboard.client.feature_flag import are_missions_in_job_board_available
from jobboard.client.features.agent_missions.job import AgentMissionJob, FleetMembersAgentMissionJob
from jobboard.client.job_provider import JobProvider
from jobboard.client.provider_type import ProviderType

class AgentMissionsJobProvider(JobProvider):
    PROVIDER_ID = ProviderType.AGENT_MISSIONS
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_agent_missions]
    __notifyevents__ = ['OnAgentMissionChanged', 'OnSessionChanged']

    def __init__(self, *args, **kwargs):
        self._add_to_tracked = set()
        super(AgentMissionsJobProvider, self).__init__(*args, **kwargs)

    def _should_refresh_on_init(self):
        result = super(AgentMissionsJobProvider, self)._should_refresh_on_init()
        if not result and not settings.char.ui.HasKey(self._tracked_setting_id):
            return True
        return result

    def _should_refresh_on_window_initializing(self):
        return self.is_dirty

    def fetch_fleet_members_mission(self, agent_id, character_id):
        instance_id = u'{}_{}'.format(agent_id, character_id)
        job_id = self.get_job_id(instance_id)
        mission_info = sm.GetService('agents').GetMissionInfo(agent_id, character_id, None)
        current_job = self.get_job(job_id)
        if current_job and mission_info and current_job.content_id == mission_info['contentID']:
            return
        if current_job:
            self._remove_job(job_id)
        if not mission_info:
            return
        job = FleetMembersAgentMissionJob(job_id=job_id, provider=self, agent_mission=Mission(mission_id=mission_info['contentID'], agent_id=agent_id, state=mission_info['missionState']), character_id=character_id)
        self._add_job(job)

    def _register_availability(self):
        job_board_signals.on_missions_feature_availability_changed.connect(self._on_availability_changed)

    def _unregister_availability(self):
        job_board_signals.on_missions_feature_availability_changed.disconnect(self._on_availability_changed)

    def _on_availability_changed(self, _old_value, _new_value):
        self._update_provider_state(are_missions_in_job_board_available())

    def _get_instance_id(self, journal_entry):
        _, _, _, _, agent_id, _, _, _, _, _ = journal_entry
        return agent_id

    def _get_all_content(self):
        return sm.GetService('journal').GetMyAgentJournalDetails()[0]

    def _construct_job(self, job_id, journal_entry):
        mission_state, is_important, mission_type, mission_name, agent_id, expiration_time, bookmarks, remote_offerable, remote_completable, content_id = journal_entry
        return AgentMissionJob(job_id, self, Mission(mission_id=content_id, agent_id=agent_id, state=mission_state, expiration_time=expiration_time, is_important=is_important))

    def OnSessionChanged(self, is_remote, session, change):
        if 'shipid' in change or 'stationid' in change:
            self._update_jobs()

    def OnAgentMissionChanged(self, mission_event, agent_id):
        job_id = self.get_job_id(agent_id)
        job = self._jobs.get(job_id)
        remove_and_refresh = True
        if job:
            remove_and_refresh = False
            if mission_event == appConst.agentMissionCompleted:
                self.service.add_relevance_score(job.content_tag_ids)
                job.update(mission_state=appConst.agentMissionStateCompleted)
                job_board_signals.on_job_state_changed(job)
                job_board_signals.on_job_completed(job)
                self.remove_tracked_job(job)
            elif mission_event == appConst.agentMissionAccepted:
                job.update(mission_state=appConst.agentMissionStateAccepted)
                job_board_signals.on_job_state_changed(job)
                self._add_to_tracked.add(job.job_id)
                self._refresh_tracked_jobs()
            elif mission_event in (appConst.agentMissionModified,
             appConst.agentMissionDungeonMoved,
             appConst.agentMissionFailed,
             appConst.agentMissionOfferExpired):
                job.update()
                self._cleanup_tracked_jobs()
            elif mission_event in (appConst.agentMissionOffered,
             appConst.agentMissionDeclined,
             appConst.agentMissionOfferDeclined,
             appConst.agentMissionOfferRemoved,
             appConst.agentMissionQuit,
             appConst.agentMissionReset):
                remove_and_refresh = True
        if remove_and_refresh:
            self._remove_job(job_id)
            self.refresh_jobs()

    def _on_jobs_refreshed(self):
        self._refresh_tracked_jobs()

    def _should_enable(self):
        return are_missions_in_job_board_available()

    def _refresh_tracked_jobs(self):
        for index, job_id in enumerate(self._add_to_tracked):
            job = self.get_job(job_id)
            if job:
                self.add_tracked_job(job, set_expanded=index == 0)

        self._add_to_tracked.clear()
        self._cleanup_tracked_jobs()

    def _cleanup_tracked_jobs(self):
        if not settings.char.ui.HasKey(self._tracked_setting_id):
            self._track_all_accepted_missions()
        else:
            super(AgentMissionsJobProvider, self)._cleanup_tracked_jobs()

    def _track_all_accepted_missions(self):
        tracked_job_ids = {}
        for job in self._jobs.itervalues():
            if not job.is_accepted or job.is_expired:
                continue
            tracked_job_ids[job.job_id] = job.accepted_timestamp or gametime.GetWallclockTime()

        self._set_tracked_job_ids(tracked_job_ids)
