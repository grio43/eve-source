#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\baseContentProviderCosmicAnomalies.py
import uthread2
import uthread
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProviderDungeons import BaseContentProviderDungeons

class BaseContentProviderCosmicAnomalies(BaseContentProviderDungeons):
    __notifyevents__ = []
    DUNGEON_TRACKER_ID = None

    def __init__(self):
        self._tracker = sm.GetService('dungeonTracking').get_tracker(self.DUNGEON_TRACKER_ID)
        super(BaseContentProviderCosmicAnomalies, self).__init__()
        self._tracker.on_sites_updated.connect(self._OnSitesUpdated)
        self._tracker.on_sites_invalidated.connect(self._OnSitesInvalidated)

    @uthread2.debounce(0.5)
    def Reset(self):
        self.InvalidateDungeonInstances()
        self.InvalidateContentPieces()

    def _GetAllDungeonInstances(self):
        return {solar_system_id:dungeons for solar_system_id, dungeons in self._tracker.get_sites().iteritems() if dungeons}

    def _OnSitesUpdated(self):
        self.Reset()

    def _OnSitesInvalidated(self):
        self.Reset()


class BaseContentProviderCosmicAnomaliesWithUnknown(BaseContentProviderCosmicAnomalies):

    def _GetAllDungeonInstances(self):
        unknown_sites, known_sites = uthread.parallel([(self._tracker.get_unknown_sites, ()), (self._tracker.get_sites, ())])
        result = unknown_sites
        result.update(known_sites)
        return {solar_system_id:dungeons for solar_system_id, dungeons in result.iteritems() if dungeons}
