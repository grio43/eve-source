#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\filters\mapFilterIceBelts.py
from carbonui.util.color import Color
from eve.client.script.ui.shared.mapView.filters.baseMapFilterAnalog import BaseMapFilterAnalog
from localization import GetByLabel

class MapFilterIceBelts(BaseMapFilterAnalog):
    name = 'Ice Belts GM'
    color = Color.AQUA

    def _ConstructDataBySolarSystemID(self):
        self._tracker = sm.GetService('dungeonTracking').get_tracker('ice_belts')
        result = self._tracker.get_unknown_sites()
        result.update(self._tracker.get_sites())
        return result
