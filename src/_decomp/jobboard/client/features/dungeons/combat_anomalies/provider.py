#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\combat_anomalies\provider.py
from jobboard.client import job_board_signals
from jobboard.client.features.dungeons.combat_anomalies.job import CombatAnomalyJob
from jobboard.client.features.dungeons.provider import AnomaliesProvider
from jobboard.client.feature_flag import are_combat_anomalies_in_job_board_available
from metadata.common.content_tags import ContentTags
from jobboard.client.provider_type import ProviderType

class CombatAnomaliesProvider(AnomaliesProvider):
    PROVIDER_ID = ProviderType.COMBAT_ANOMALIES
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_combat_anomalies] + AnomaliesProvider.PROVIDER_CONTENT_TAGS
    JOB_CLASS = CombatAnomalyJob
    DUNGEON_TRACKER_ID = 'combat_anomalies'
    JUMPS_WHERE_DUNGEONS_ARE_ALWAYS_VISIBLE = 1
    JUMPS_WHERE_DUNGEONS_CAN_BE_VISIBLE = 1
    INCLUDE_SYSTEMS_IN_ROUTE = False

    def _register_availability(self):
        super(CombatAnomaliesProvider, self)._register_availability()
        job_board_signals.on_combat_anomalies_feature_availability_changed.connect(self._on_availability_changed)

    def _unregister_availability(self):
        super(CombatAnomaliesProvider, self)._unregister_availability()
        job_board_signals.on_combat_anomalies_feature_availability_changed.disconnect(self._on_availability_changed)

    def _should_enable(self):
        return super(CombatAnomaliesProvider, self)._should_enable() and are_combat_anomalies_in_job_board_available()
