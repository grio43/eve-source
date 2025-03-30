#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\cosmic_signatures\provider.py
from eve.common.lib.appConst import typeDeadspaceSignature
from jobboard.client.features.dungeons.cosmic_signatures.job import CosmicSignatureJob
from jobboard.client.features.dungeons.provider import BaseDungeonsProvider
from metadata.common.content_tags import ContentTags
from jobboard.client.provider_type import ProviderType

class CosmicSignaturesProvider(BaseDungeonsProvider):
    PROVIDER_ID = ProviderType.COSMIC_SIGNATURES
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_cosmic_signatures] + BaseDungeonsProvider.PROVIDER_CONTENT_TAGS
    JOB_CLASS = CosmicSignatureJob

    @property
    def feature_tag(self):
        return None

    @property
    def is_hidden(self):
        return True

    def try_fetch_job(self, job_id):
        job = super(CosmicSignaturesProvider, self).try_fetch_job(job_id)
        if job:
            return job
        current_dungeon = sm.GetService('dungeonTracking').current_dungeon
        if current_dungeon and current_dungeon.objective_chain and self._is_site_relevant(current_dungeon.archetype_id, current_dungeon.entry_type_id):
            job = self._create_job({'solar_system_id': session.solarsystemid2,
             'dungeon_id': current_dungeon.dungeon_id,
             'instance_id': current_dungeon.instance_id,
             'scan_result': sm.GetService('sensorSuite').GetAnomaly(current_dungeon.instance_id)})
            return job

    def OnDungeonExited(self, _dungeon_id, instance_id):
        job_id = self.get_job_id(instance_id)
        job = self._jobs.get(job_id, None)
        if not job:
            return
        self._remove_job(job_id)

    def _is_site_relevant(self, archetype_id, entry_type_id):
        return entry_type_id == typeDeadspaceSignature

    def _get_all_content(self):
        return []
