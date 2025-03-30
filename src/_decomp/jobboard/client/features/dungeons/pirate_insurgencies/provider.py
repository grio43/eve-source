#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\pirate_insurgencies\provider.py
from metadata.common.content_tags import ContentTags
from jobboard.client import job_board_signals
from jobboard.client.features.dungeons.provider import AnomaliesProvider
from jobboard.client.feature_flag import are_pirate_insurgency_sites_in_job_board_available
from jobboard.client.provider_type import ProviderType
from .job import PirateInsurgencyJob

class PirateInsurgenciesProvider(AnomaliesProvider):
    PROVIDER_ID = ProviderType.PIRATE_INSURGENCIES
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_pirate_insurgencies] + AnomaliesProvider.PROVIDER_CONTENT_TAGS
    JOB_CLASS = PirateInsurgencyJob
    __notifyevents__ = AnomaliesProvider.__notifyevents__ + ['OnEnlistmentStateUpdated_Local']
    DUNGEON_TRACKER_ID = 'pirate_insurgency'

    @property
    def is_enlisted(self):
        return bool(sm.GetService('fwEnlistmentSvc').GetMyFaction())

    def _register_availability(self):
        super(PirateInsurgenciesProvider, self)._register_availability()
        job_board_signals.on_pirate_insurgency_feature_availability_changed.connect(self._on_availability_changed)

    def _unregister_availability(self):
        super(PirateInsurgenciesProvider, self)._unregister_availability()
        job_board_signals.on_pirate_insurgency_feature_availability_changed.disconnect(self._on_availability_changed)

    def OnEnlistmentStateUpdated_Local(self):
        self._invalidate_cache()
        job_board_signals.on_job_provider_state_changed(self)

    def _should_enable(self):
        return super(PirateInsurgenciesProvider, self)._should_enable() and are_pirate_insurgency_sites_in_job_board_available()

    def _get_all_content(self):
        if not self.is_enlisted:
            return []
        return super(PirateInsurgenciesProvider, self)._get_all_content()
