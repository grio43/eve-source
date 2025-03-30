#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerBookmark.py
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
import localization
from eve.client.script.parklife import states as state
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase
from eve.client.script.ui.shared.mapView.markers.mapMarkerSpaceObjectRadialMenu import MapMarkerSpaceObjectRadialMenu
from eveservices.menu import GetMenuService
from localization import GetByLabel

class MarkerBookmarkUniverseLevel(MarkerIconBase):
    texturePath = 'res:/UI/Texture/Icons/38_16_150.png'
    distanceFadeAlphaNearFar = (mapViewConst.MAX_MARKER_DISTANCE * 0.01, mapViewConst.MAX_MARKER_DISTANCE)
    overlapEnabled = False
    distanceSortEnabled = False

    def __init__(self, *args, **kwds):
        MarkerIconBase.__init__(self, *args, **kwds)
        self.bookmarksData = kwds['bookmarksData']
        self.showChanges = kwds.get('showChanges', False)

    def GetLabelText(self):
        return GetByLabel('UI/Map/LocationsInSolarSystem', locationName=cfg.evelocations.Get(self.solarSystemID).name, amount=len(self.bookmarksData))

    def GetMenu(self):
        return GetMenuService().BookmarkMenu(self.bookmarksData[0])


class MarkerBookmark(MarkerIconBase):
    texturePath = 'res:/UI/Texture/Icons/38_16_150.png'
    distanceFadeAlphaNearFar = (0.0, mapViewConst.MAX_MARKER_DISTANCE * 0.1)

    def __init__(self, *args, **kwds):
        MarkerIconBase.__init__(self, *args, **kwds)
        self.bookmarkData = kwds['bookmarkData']
        isPersonal = kwds.get('isPersonal', None)
        if not isPersonal:
            self.texturePath = 'res:/ui/Texture/classes/Bookmarks/sharedBookmarkSensorOverlay.png'
        self.itemID = self.bookmarkData.itemID or self.bookmarkData.locationID
        self.typeID = self.bookmarkData.typeID
        self.CreateClientBall()

    def GetDisplayText(self):
        caption, note = sm.GetService('bookmarkSvc').UnzipMemo(self.bookmarkData.memo)
        return localization.GetByLabel('UI/Map/StarMap/hintSystemBookmark', memo=caption)

    def GetMenu(self):
        return GetMenuService().BookmarkMenu(self.bookmarkData)

    def OnClick(self, *args):
        doDScan = self.CheckDirectionalScanItem()
        if not doDScan:
            sm.GetService('stateSvc').SetState(self.itemID, state.selected, 1)
            MarkerIconBase.OnClick(self, *args)

    def OnMouseDown(self, *args):
        bookMarkInfo = self.bookmarkData
        if bookMarkInfo is None:
            return
        if self.clientBall:
            GetMenuService().TryExpandActionMenu(itemID=self.clientBall.id, clickedObject=self, bookmarkInfo=self.bookmarkData, radialMenuClass=MapMarkerSpaceObjectRadialMenu, markerObject=self)

    def SetYScaleFactor(self, yScaleFactor):
        x, y, z = self.position
        self.projectBracket.trackPosition = (x, y * yScaleFactor, z)

    def _GetSolarSystemPosition(self):
        bookmark = self.bookmarkData
        return (bookmark.x, bookmark.y, bookmark.z)
