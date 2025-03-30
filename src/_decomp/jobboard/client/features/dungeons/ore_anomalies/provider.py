#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\ore_anomalies\provider.py
from metadata.common.content_tags import ContentTags
from jobboard.client import job_board_signals
from jobboard.client.features.dungeons.provider import AnomaliesProvider
from jobboard.client.feature_flag import are_ore_anomalies_in_job_board_available
from jobboard.client.provider_type import ProviderType
from .job import OreAnomalyJob

class OreAnomaliesProvider(AnomaliesProvider):
    PROVIDER_ID = ProviderType.ORE_ANOMALIES
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_ore_anomalies] + AnomaliesProvider.PROVIDER_CONTENT_TAGS
    JOB_CLASS = OreAnomalyJob
    DUNGEON_TRACKER_ID = 'ore_anomalies'
    JUMPS_WHERE_DUNGEONS_ARE_ALWAYS_VISIBLE = 1
    JUMPS_WHERE_DUNGEONS_CAN_BE_VISIBLE = 1
    INCLUDE_SYSTEMS_IN_ROUTE = False

    def _register_availability(self):
        super(OreAnomaliesProvider, self)._register_availability()
        job_board_signals.on_ore_anomalies_feature_availability_changed.connect(self._on_availability_changed)

    def _unregister_availability(self):
        super(OreAnomaliesProvider, self)._unregister_availability()
        job_board_signals.on_ore_anomalies_feature_availability_changed.disconnect(self._on_availability_changed)

    def _should_enable(self):
        return super(OreAnomaliesProvider, self)._should_enable() and are_ore_anomalies_in_job_board_available()
