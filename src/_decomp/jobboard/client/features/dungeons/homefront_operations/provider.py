#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\homefront_operations\provider.py
from metadata.common.content_tags import ContentTags
from jobboard.client import job_board_signals
from jobboard.client.features.dungeons.provider import AnomaliesProvider
from jobboard.client.feature_flag import are_homefront_operations_in_job_board_available
from jobboard.client.provider_type import ProviderType
from .job import HomefrontOperationJob

class HomefrontOperationsProvider(AnomaliesProvider):
    PROVIDER_ID = ProviderType.HOMEFRONT_OPERATIONS
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_homefront_operations] + AnomaliesProvider.PROVIDER_CONTENT_TAGS
    JOB_CLASS = HomefrontOperationJob
    DUNGEON_TRACKER_ID = 'homefront_operations'

    def _register_availability(self):
        super(HomefrontOperationsProvider, self)._register_availability()
        job_board_signals.on_homefront_operations_feature_availability_changed.connect(self._on_availability_changed)

    def _unregister_availability(self):
        super(HomefrontOperationsProvider, self)._unregister_availability()
        job_board_signals.on_homefront_operations_feature_availability_changed.disconnect(self._on_availability_changed)

    def _should_enable(self):
        return super(HomefrontOperationsProvider, self)._should_enable() and are_homefront_operations_in_job_board_available()
