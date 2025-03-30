#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\factional_warfare\provider.py
from eve.common.lib import appConst
from metadata.common.content_tags import ContentTags
from jobboard.client import job_board_signals
from jobboard.client.features.dungeons.provider import AnomaliesProvider
from jobboard.client.feature_flag import are_factional_warfare_sites_in_job_board_available
from jobboard.client.provider_type import ProviderType
from .job import FactionalWarfareJob

class FactionalWarfareProvider(AnomaliesProvider):
    PROVIDER_ID = ProviderType.FACTIONAL_WARFARE
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_factional_warfare] + AnomaliesProvider.PROVIDER_CONTENT_TAGS
    JOB_CLASS = FactionalWarfareJob
    __notifyevents__ = AnomaliesProvider.__notifyevents__ + ['OnEnlistmentStateUpdated_Local']
    DUNGEON_TRACKER_ID = 'factional_warfare'

    @property
    def is_enlisted(self):
        return sm.GetService('fwEnlistmentSvc').GetMyFaction() in appConst.factionsEmpires

    def _register_availability(self):
        super(FactionalWarfareProvider, self)._register_availability()
        job_board_signals.on_factional_warfare_feature_availability_changed.connect(self._on_availability_changed)

    def _unregister_availability(self):
        super(FactionalWarfareProvider, self)._unregister_availability()
        job_board_signals.on_factional_warfare_feature_availability_changed.disconnect(self._on_availability_changed)

    def OnEnlistmentStateUpdated_Local(self):
        self._invalidate_cache()
        job_board_signals.on_job_provider_state_changed(self)

    def _should_enable(self):
        return super(FactionalWarfareProvider, self)._should_enable() and are_factional_warfare_sites_in_job_board_available()

    def _get_all_content(self):
        if not self.is_enlisted:
            return []
        return super(FactionalWarfareProvider, self)._get_all_content()
