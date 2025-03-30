#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\layout\mapLayoutSolarSystems.py
from eve.client.script.ui.shared.mapView.layout.mapLayoutBase import MapLayoutBase
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData

class MapLayoutSolarSystems(MapLayoutBase):

    def PrimeLayout(self, yScaleFactor = False, **kwds):
        if yScaleFactor == self.cacheKey:
            return
        self.cacheKey = yScaleFactor
        solarSystemID_position = {}
        for solarSystemID, solarSystemItem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
            x, y, z = solarSystemItem.mapPosition
            if yScaleFactor is not None:
                y *= yScaleFactor
            solarSystemID_position[solarSystemID] = (x, y, z)

        self.positionsBySolarSystemID = solarSystemID_position
