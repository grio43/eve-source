#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\ice_belts\provider.py
from metadata.common.content_tags import ContentTags
from jobboard.client import job_board_signals
from jobboard.client.features.dungeons.provider import AnomaliesProvider
from jobboard.client.feature_flag import are_ice_belts_in_job_board_available
from jobboard.client.provider_type import ProviderType
from .job import IceBeltJob

class IceBeltsProvider(AnomaliesProvider):
    PROVIDER_ID = ProviderType.ICE_BELTS
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_ice_belts] + AnomaliesProvider.PROVIDER_CONTENT_TAGS
    JOB_CLASS = IceBeltJob
    DUNGEON_TRACKER_ID = 'ice_belts'
    JUMPS_WHERE_DUNGEONS_ARE_ALWAYS_VISIBLE = 1
    JUMPS_WHERE_DUNGEONS_CAN_BE_VISIBLE = 1
    INCLUDE_SYSTEMS_IN_ROUTE = False

    def _register_availability(self):
        super(IceBeltsProvider, self)._register_availability()
        job_board_signals.on_ice_belts_feature_availability_changed.connect(self._on_availability_changed)

    def _unregister_availability(self):
        super(IceBeltsProvider, self)._unregister_availability()
        job_board_signals.on_ice_belts_feature_availability_changed.disconnect(self._on_availability_changed)

    def _should_enable(self):
        return super(IceBeltsProvider, self)._should_enable() and are_ice_belts_in_job_board_available()
