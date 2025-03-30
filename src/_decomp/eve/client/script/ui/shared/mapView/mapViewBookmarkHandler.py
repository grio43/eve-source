#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\mapViewBookmarkHandler.py
from eve.client.script.ui.shared.mapView.mapViewConst import MARKERID_BOOKMARK, MARKERS_OPTION_PERSONAL_LOCATION, VIEWMODE_MARKERS_SETTINGS, MARKERS_OPTION_SHARED_LOCATION
from eve.client.script.ui.shared.mapView.mapViewSettings import GetMapViewSetting
from eve.client.script.ui.shared.mapView.markers.mapMarkerBookmark import MarkerBookmark, MarkerBookmarkUniverseLevel
from eve.client.script.ui.shared.mapView.mapViewUtil import SolarSystemPosToMapPos
import weakref
import geo2
from eve.client.script.util.bookmarkUtil import IsCoordinateBookmark
from eve.common.lib import appConst
from eve.common.script.sys.idCheckers import IsSolarSystem, IsConstellation
import evetypes
import blue
import telemetry
import logging
log = logging.getLogger(__name__)
MAX_BOOKMARKS_DISPLAYED_ON_MAP = 250

class MapViewBookmarkHandler(object):
    __metaclass__ = telemetry.ZONE_PER_METHOD
    __notifyevents__ = ['OnRefreshBookmarks']
    _mapView = None

    def __init__(self, mapView, loadUniverseBookmarks = False, solarSystemScaling = None):
        self.bookmarkSvc = sm.GetService('bookmarkSvc')
        self.mapView = mapView
        self.loadedSolarSystemID = None
        self.loadUniverseBookmarks = loadUniverseBookmarks
        self.solarSystemScaling = solarSystemScaling
        sm.RegisterNotify(self)

    def StopHandler(self):
        sm.UnregisterNotify(self)

    @apply
    def mapView():

        def fget(self):
            if self._mapView:
                return self._mapView()

        def fset(self, value):
            self._mapView = weakref.ref(value)

        return property(**locals())

    def OnRefreshBookmarks(self):
        self.LoadBookmarkMarkers(loadSolarSystemID=self.loadedSolarSystemID)

    def LoadBookmarkMarkers(self, loadSolarSystemID = None, showChanges = False):
        self.loadedSolarSystemID = loadSolarSystemID
        bookmarks = self.GetAllEnabledBookmarks()
        bookmarksBySolarSystemID = self.GetBookmarksBySolarSystemID(bookmarks)
        bookmarkMarkers = self.mapView.markersHandler.GetMarkersByType(MARKERID_BOOKMARK)
        bookmarkMarkerIDs = set([ markerObject.markerID for markerObject in bookmarkMarkers ])
        personalFolderIDs, _ = self.bookmarkSvc.GetPersonalAndSharedFolders()
        markerIDs = set()
        if not self.mapView:
            return markerIDs
        for solarSystemID, bookmarksInSystem in bookmarksBySolarSystemID.iteritems():
            if self.loadUniverseBookmarks:
                solarSystemBookmarks = self.GetSolarSystemBookmarks(bookmarksInSystem)
                if solarSystemBookmarks:
                    self.CheckAddUniverseLevelBookmark(solarSystemID, solarSystemBookmarks, markerIDs, showChanges)
            if loadSolarSystemID and solarSystemID == loadSolarSystemID:
                for bookmark in bookmarksInSystem[:MAX_BOOKMARKS_DISPLAYED_ON_MAP]:
                    isPersonal = bookmark.folderID in personalFolderIDs
                    self.CheckAddSolarSystemLevelBookmark(solarSystemID, bookmark, bookmarkMarkerIDs, markerIDs, showChanges, isPersonal)

            blue.pyos.BeNice()

        for removeMarkerID in bookmarkMarkerIDs.difference(markerIDs):
            self.mapView.markersHandler.RemoveMarker(removeMarkerID)

        return markerIDs

    def GetAllEnabledBookmarks(self):
        loadPersonal = IsMarkerGroupEnabled(MARKERS_OPTION_PERSONAL_LOCATION, self.mapView.mapViewID)
        loadShared = IsMarkerGroupEnabled(MARKERS_OPTION_SHARED_LOCATION, self.mapView.mapViewID)
        if not loadPersonal and not loadShared:
            return []
        usePersonalFilter = not (loadPersonal and loadShared)
        bookmarks = sm.GetService('bookmarkSvc').GetActiveBookmarksFiltered(None, usePersonalFilter=usePersonalFilter, personal=loadPersonal).values()
        return bookmarks

    def GetBookmarksBySolarSystemID(self, bookmarks):
        bookmarksBySolarSystemID = {}
        for bookmark in bookmarks:
            solarSystemID = self.GetSolarSystemID(bookmark)
            if solarSystemID:
                bookmarksBySolarSystemID.setdefault(solarSystemID, []).append(bookmark)

        return bookmarksBySolarSystemID

    def GetSolarSystemID(self, bookmark):
        if IsSolarSystem(bookmark.locationID):
            return bookmark.locationID
        if IsConstellation(bookmark.locationID):
            return bookmark.itemID

    def GetSolarSystemBookmarks(self, bookmarks):
        return [ bookmark for bookmark in bookmarks if bookmark.typeID == appConst.typeSolarSystem and not IsCoordinateBookmark(bookmark) ]

    def CheckAddSolarSystemLevelBookmark(self, solarSystemID, bookmark, bookmarkMarkerIDs, markerIDs, showChanges, isPersonal):
        markerID = (MARKERID_BOOKMARK, bookmark.bookmarkID)
        if markerID in bookmarkMarkerIDs:
            markerIDs.add(markerID)
            return
        try:
            localBookmarkPosition = self.GetBookmarkPosition(bookmark)
        except RuntimeError:
            log.warn('Failed to get bookmark position, bookmark.bookmarkID, bookmark.itemID: %s, %s' % (bookmark.bookmarkID, bookmark.itemID))
            return

        try:
            mapPositionLocal = SolarSystemPosToMapPos(localBookmarkPosition)
            if self.solarSystemScaling:
                mapPositionLocal = geo2.Vec3ScaleD(mapPositionLocal, self.solarSystemScaling)
        except TypeError:
            log.warn('Failed to get bookmark position, localBookmarkPosition: %s' % repr(localBookmarkPosition))
            return

        solarSystemPosition = (0, 0, 0)
        if getattr(self.mapView, 'layoutHandler', None):
            mapNode = self.mapView.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
            if mapNode:
                solarSystemPosition = mapNode.position
        self.mapView.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerBookmark, bookmarkData=bookmark, solarSystemID=solarSystemID, highlightOnLoad=showChanges, mapPositionLocal=mapPositionLocal, mapPositionSolarSystem=solarSystemPosition, isPersonal=isPersonal)
        markerIDs.add(markerID)

    def CheckAddUniverseLevelBookmark(self, solarSystemID, bookmarks, markerIDs, showChanges):
        if not self.mapView.layoutHandler:
            return
        mapNode = self.mapView.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
        if not mapNode:
            return
        markerID = (MARKERID_BOOKMARK, solarSystemID)
        markerObject = self.mapView.markersHandler.GetMarkerByID(markerID)
        if markerObject:
            markerObject.bookmarksData = bookmarks
        else:
            self.mapView.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerBookmarkUniverseLevel, bookmarksData=bookmarks, solarSystemID=solarSystemID, highlightOnLoad=showChanges, mapPositionLocal=(0, 0, 0), mapPositionSolarSystem=mapNode.position)
        markerIDs.add(markerID)

    def GetBookmarkPosition(self, bookmark):
        localPosition = None
        if bookmark and (bookmark.itemID == bookmark.locationID or bookmark.typeID == const.typeSolarSystem) and bookmark.x is not None:
            localPosition = (bookmark.x, bookmark.y, bookmark.z)
        elif evetypes.Exists(bookmark.typeID) and evetypes.GetCategoryID(bookmark.typeID) == const.categoryStructure:
            structure = sm.GetService('map').GetMapDataForStructure(bookmark.locationID, bookmark.itemID)
            if structure:
                localPosition = (structure.x, structure.y, structure.z)
        else:
            mapSvc = sm.GetService('map')
            try:
                itemStarMapData = mapSvc.GetItem(bookmark.itemID)
            except KeyError:
                log.error('Map data not found for bookmark.itemID: %s' % bookmark.itemID)
                return

            if itemStarMapData:
                localPosition = (itemStarMapData.x, itemStarMapData.y, itemStarMapData.z)
            elif evetypes.GetGroupID(bookmark.typeID) == const.groupStargate:
                try:
                    solarSystemData = cfg.mapSolarSystemContentCache[bookmark.locationID]
                except KeyError:
                    log.error('Stargate data not found for bookmark.locationID: %s' % bookmark.locationID)
                    return

                starGateInfo = solarSystemData.stargates.get(bookmark.itemID, None)
                if starGateInfo:
                    position = starGateInfo.position
                    localPosition = (position.x, position.y, position.z)
        if localPosition is None:
            localPosition = (0, 0, 0)
        return localPosition


def IsMarkerGroupEnabled(markerGroupID, mapViewID):
    markerGroups = GetMapViewSetting(VIEWMODE_MARKERS_SETTINGS, mapViewID)
    return markerGroupID in markerGroups
