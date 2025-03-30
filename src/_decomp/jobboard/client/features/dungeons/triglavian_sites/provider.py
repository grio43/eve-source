#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\triglavian_sites\provider.py
from eve.common.script.sys.idCheckers import IsTriglavianSystem
from metadata.common.content_tags import ContentTags
from jobboard.client.features.dungeons.provider import AnomaliesProvider
from jobboard.client.provider_type import ProviderType
from .job import TriglavianSiteJob
POCHVEN_REGION_ID = 10000070

class TriglavianSitesProvider(AnomaliesProvider):
    PROVIDER_ID = ProviderType.TRIGLAVIAN_SITES
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_triglavian] + AnomaliesProvider.PROVIDER_CONTENT_TAGS
    JOB_CLASS = TriglavianSiteJob
    DUNGEON_TRACKER_ID = 'triglavian'
    INCLUDE_SYSTEMS_IN_ROUTE = False

    def _register_availability(self):
        sm.RegisterForNotifyEvent(self, 'OnSessionChanged')

    def _unregister_availability(self):
        sm.UnregisterForNotifyEvent(self, 'OnSessionChanged')

    def OnSessionChanged(self, _is_remote, _session, change):
        if 'solarsystemid2' in change:
            self._update_provider_state(self._should_enable())

    def _should_enable(self):
        return IsTriglavianSystem(session.solarsystemid2)

    def _should_refresh_on_init(self):
        return self.is_enabled

    def _get_relevant_solar_systems(self):
        return cfg.mapRegionCache[POCHVEN_REGION_ID].solarSystemIDs
