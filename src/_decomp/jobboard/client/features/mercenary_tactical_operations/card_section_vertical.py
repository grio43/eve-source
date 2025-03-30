#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\mercenary_tactical_operations\card_section_vertical.py
from jobboard.client import get_job_board_service
from jobboard.client.provider_type import ProviderType
from jobboard.client.ui.card_section_vertical import FeatureCardSectionVertical

class MTOFeatureCardSectionVertical(FeatureCardSectionVertical):

    def __init__(self, show_feature = False, show_solar_system = True, hide_empty = True, *args, **kwargs):
        provider = get_job_board_service().get_provider(ProviderType.MERCENARY_TACTICAL_OPS)
        super(MTOFeatureCardSectionVertical, self).__init__(show_feature, show_solar_system, hide_empty, provider, *args, **kwargs)

    def _fetch_all_jobs(self):
        return self._service.get_available_jobs(provider_id=self._provider_id)

    def _fetch_jobs(self):
        return self._fetch_all_jobs()[:10]
