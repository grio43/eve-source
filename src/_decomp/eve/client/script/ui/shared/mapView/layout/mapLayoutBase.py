#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\layout\mapLayoutBase.py
import weakref

class MapLayoutBase(object):
    cacheKey = None
    positionsBySolarSystemID = None
    visibleMarkers = None

    def __init__(self, layoutHandler):
        self.layoutHandler = weakref.ref(layoutHandler)

    def ClearCache(self):
        self.cacheKey = None
        self.positionsBySolarSystemID = None
        self.visibleMarkers = None
