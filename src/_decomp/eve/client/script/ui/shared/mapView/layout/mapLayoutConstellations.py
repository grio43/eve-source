#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\layout\mapLayoutConstellations.py
from eve.client.script.ui.shared.mapView.layout.mapLayoutBase import MapLayoutBase
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData

class MapLayoutConstellations(MapLayoutBase):

    def PrimeLayout(self, expandedItems = None, yScaleFactor = None):
        if (expandedItems, yScaleFactor) == self.cacheKey:
            return
        self.cacheKey = (expandedItems, yScaleFactor)
        showMarkers = mapViewData.GetKnownUniverseRegions().keys()
        showMarkers += mapViewData.GetKnownUniverseConstellations().keys()
        solarSystemID_position = {}
        for constellationID, constellationItem in mapViewData.GetKnownUniverseConstellations().iteritems():
            if expandedItems and constellationID in expandedItems:
                for solarSystemID in constellationItem.solarSystemIDs:
                    solarSystemItem = mapViewData.GetKnownSolarSystem(solarSystemID)
                    x, y, z = solarSystemItem.mapPosition
                    if yScaleFactor is not None:
                        y *= yScaleFactor
                    solarSystemID_position[solarSystemID] = (x, y, z)

                showMarkers += constellationItem.solarSystemIDs
            else:
                x, y, z = constellationItem.mapPosition
                if yScaleFactor is not None:
                    y *= yScaleFactor
                for solarSystemID in constellationItem.solarSystemIDs:
                    solarSystemID_position[solarSystemID] = (x, y, z)

        self.positionsBySolarSystemID = solarSystemID_position
        self.visibleMarkers = showMarkers
