#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\layout\mapLayoutRegions.py
from eve.client.script.ui.shared.mapView.layout.mapLayoutBase import MapLayoutBase
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData

class MapLayoutRegions(MapLayoutBase):

    def PrimeLayout(self, expandedItems = None, yScaleFactor = False):
        if (expandedItems, yScaleFactor) == self.cacheKey:
            return
        self.cacheKey = (expandedItems, yScaleFactor)
        showMarkers = mapViewData.GetKnownUniverseRegions().keys()
        solarSystemID_position = {}
        for regionID, regionItem in mapViewData.GetKnownUniverseRegions().iteritems():
            if expandedItems and regionID in expandedItems:
                for solarSystemID in regionItem.solarSystemIDs:
                    solarSystemItem = mapViewData.GetKnownSolarSystem(solarSystemID)
                    x, y, z = solarSystemItem.mapPosition
                    if yScaleFactor is not None:
                        y *= yScaleFactor
                    solarSystemID_position[solarSystemID] = (x, y, z)

                showMarkers += regionItem.constellationIDs
                showMarkers += regionItem.solarSystemIDs
            else:
                x, y, z = regionItem.mapPosition
                if yScaleFactor is not None:
                    y *= yScaleFactor
                for solarSystemID in regionItem.solarSystemIDs:
                    solarSystemID_position[solarSystemID] = (x, y, z)

        self.positionsBySolarSystemID = solarSystemID_position
        self.visibleMarkers = showMarkers
