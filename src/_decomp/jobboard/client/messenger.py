#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\messenger.py
from eveprefs import prefs
from eveProto.generated.eve_public.opportunity.api.event_pb2 import Viewed, Tracked, Untracked, Completed
from jobboard.client.provider_type import ProviderType, DUNGEON_PROVIDERS
from evedungeons.common.dungeon_proto_util import format_dungeon_instance_id
import logging

class JobBoardMessenger(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.logger = logging.getLogger('JobBoardMessenger')

    def on_job_viewed(self, job):
        event = Viewed()
        self._on_job_event(event, job)

    def on_job_tracked(self, job):
        event = Tracked()
        self._on_job_event(event, job)

    def on_job_untracked(self, job):
        event = Untracked()
        self._on_job_event(event, job)

    def on_job_completed(self, job):
        event = Completed()
        self._on_job_event(event, job)

    def _on_job_event(self, event, job):
        if not job:
            return
        character_id = session.charid
        if character_id is None:
            return
        self._publish(event, character_id, job)
        self._log(event, character_id, job)

    def _publish(self, event, character_id, job):
        try:
            provider_id = job.provider_id
            if provider_id == ProviderType.AGENT_MISSIONS:
                event.opportunity.mission.mission.sequential = job.mission_id
                event.opportunity.mission.agent.sequential = job.agent_id
            elif provider_id == ProviderType.CORPORATION_GOALS:
                event.opportunity.goal.uuid = job.goal_id.bytes
            elif provider_id in DUNGEON_PROVIDERS:
                event.opportunity.dungeon.dungeon.sequential = job.dungeon_id
                format_dungeon_instance_id(event.opportunity.dungeon.instance, job.instance_id)
            elif provider_id == ProviderType.EPIC_ARCS:
                event.opportunity.epicarc.sequential = job.epic_arc_id
            elif provider_id == ProviderType.FACTIONAL_WARFARE_ENLISTMENT:
                event.opportunity.enlistment.faction.sequential = job.faction_id
            elif provider_id == ProviderType.STORYLINES:
                event.opportunity.storyline.content_label = job.content_id
            elif provider_id == ProviderType.DAILY_GOALS:
                event.opportunity.daily_goal.uuid = job.goal_id.bytes
            else:
                return
            event.character.sequential = character_id
            self.public_gateway.publish_event_payload(event)
        except Exception as exc:
            logging.warning('Error publishing Opportunity protobuf event: %s', exc)

    def _log(self, event, character_id, job):
        if not self._should_log():
            return
        job_id = job.job_id
        content_id = job.content_id
        provider_id = job.provider_id
        event_name = event.DESCRIPTOR.name.upper()
        character_name = cfg.eveowners.Get(character_id).name
        info_text = 'Job Board Event: {event_name} - character {character_name} (ID: {character_id}), job {job_id}, content {content_id}, provider {provider_id}.\nContent of {event_name} event: \n{event_content}'.format(event_name=event_name, character_name=character_name, character_id=character_id, job_id=job_id, content_id=content_id, provider_id=provider_id, event_content=event)
        self.logger.info(info_text)

    def _should_log(self):
        return prefs.clusterMode != 'LIVE'
