#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\filters\mapFilterAsteroidBelts.py
from carbonui.util.color import Color
from eve.client.script.ui.shared.mapView.filters.baseMapFilterAnalog import BaseMapFilterAnalog

class MapFilterAsteroidBelts(BaseMapFilterAnalog):
    name = 'Asteroid Belts GM'
    color = Color.GREEN

    def _ConstructDataBySolarSystemID(self):
        self._tracker = sm.GetService('dungeonTracking').get_tracker('ore_anomalies')
        result = self._tracker.get_unknown_sites()
        result.update(self._tracker.get_sites())
        return result
