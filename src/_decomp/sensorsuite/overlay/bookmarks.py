#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sensorsuite\overlay\bookmarks.py
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToBookmark
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import SimpleRadialMenuAction
from eve.common.script.sys.idCheckers import IsSolarSystem
from inventorycommon.const import groupStation
import logging
from sensorsuite.error import BookmarkInvalidPositionError
from sensorsuite.overlay.bookmarkvisibilitymanager import GetBookmarkFolderVisibilityManager
from sensorsuite.overlay.brackets import SensorSuiteBracket, INNER_ICON_COLOR
from sensorsuite.overlay.siteconst import SITE_COLOR_BOOKMARK, SITE_BOOKMARK, SITE_COLOR_SHARED_BOOKMARK, SITE_SHARED_BOOKMARK, SITE_OUTER_TEXTURE_SHARED_BOOKMARK, SITE_ICON_SHARED_BOOKMARK
from sensorsuite.overlay.sitedata import SiteData
from sensorsuite.overlay.sitehandler import SiteHandler
from sensorsuite.overlay.sitetype import BOOKMARK, SHARED_BOOKMARK
import evetypes
from eveservices.menu import GetMenuService
import telemetry
logger = logging.getLogger(__name__)
MAX_VISIBLE_NAME_LENGTH = 20

def CleanText(text):
    if text is None:
        text = ''
    else:
        text.strip()
    return text


def GetBookmarkPosition(bookmark):
    if bookmark.itemID and not IsSolarSystem(bookmark.itemID):
        try:
            loc = cfg.evelocations.Get(bookmark.itemID)
            position = (loc.x, loc.y, loc.z)
            return position
        except KeyError:
            logger.debug('Item %s not found, probably a deleted structure', bookmark.itemID)

    if None in (bookmark.x, bookmark.y, bookmark.z):
        logger.warning('Skipping bookmark %s, as position not valid: (%s, %s, %s)', bookmark.bookmarkID, bookmark.x, bookmark.y, bookmark.z)
        raise BookmarkInvalidPositionError('Invalid bookmark position')
    position = (bookmark.x, bookmark.y, bookmark.z)
    return position


def GetBookmarkSiteActions(bookmark):
    groupID = evetypes.GetGroupID(bookmark.typeID)
    if groupID == groupStation:
        return [SimpleRadialMenuAction(option1='UI/Inflight/DockInStation')]
    else:
        return None


class BookmarkSiteData(SiteData):
    siteType = BOOKMARK
    baseColor = SITE_COLOR_BOOKMARK

    def __init__(self, siteID, position, bookmark = None):
        SiteData.__init__(self, siteID, position)
        self.bookmark = bookmark
        self.name = CleanText(bookmark.memo)

    def GetBracketClass(self):
        return BookmarkBracket

    def GetName(self):
        return self.name

    def WarpToAction(self, itemID, distance, *args):
        WarpToBookmark(self.bookmark, warpRange=distance)

    def GetMenu(self):
        return GetMenuService().BookmarkMenu(self.bookmark)

    def GetSiteActions(self):
        return GetBookmarkSiteActions(self.bookmark)


class BookmarkBracket(SensorSuiteBracket):
    outerColor = SITE_COLOR_BOOKMARK.GetRGBA()
    innerColor = INNER_ICON_COLOR.GetRGBA()
    innerIconResPath = 'res:/UI/Texture/Icons/38_16_150.png'
    outerTextures = ('res:/UI/Texture/classes/SensorSuite/bracket_bookmark_1.png', 'res:/UI/Texture/classes/SensorSuite/bracket_bookmark_2.png', 'res:/UI/Texture/classes/SensorSuite/bracket_bookmark_3.png', 'res:/UI/Texture/classes/SensorSuite/bracket_bookmark_4.png')

    def ApplyAttributes(self, attributes):
        SensorSuiteBracket.ApplyAttributes(self, attributes)
        self.UpdateSiteName(CleanText(self.data.bookmark.note))

    def GetMenu(self):
        return self.data.GetMenu()

    def AlignTo(self):
        GetMenuService().AlignToBookmark(self.data.bookmark.bookmarkID)

    def OnMouseDown(self, *args):
        GetMenuService().TryExpandActionMenu(None, self, siteData=self.data, bookmarkInfo=self.data.bookmark)


class SharedBookmarkSiteData(BookmarkSiteData):
    siteType = SHARED_BOOKMARK
    baseColor = SITE_COLOR_SHARED_BOOKMARK

    def GetBracketClass(self):
        return SharedBookmarkBracket


class SharedBookmarkBracket(BookmarkBracket):
    outerColor = SITE_COLOR_SHARED_BOOKMARK.GetRGBA()
    innerColor = INNER_ICON_COLOR.GetRGBA()
    innerIconResPath = SITE_ICON_SHARED_BOOKMARK
    outerTextures = SITE_OUTER_TEXTURE_SHARED_BOOKMARK

    def GetCaptionText(self):
        return self.data.GetName()


class BookmarkHandler(SiteHandler):
    siteType = BOOKMARK
    filterIconPath = 'res:/UI/Texture/Icons/38_16_150.png'
    filterLabel = 'UI/Inflight/Scanner/PersonalSiteFilterLabel'
    color = SITE_COLOR_BOOKMARK
    siteIconData = SITE_BOOKMARK

    def __init__(self, sensorSuiteSvc, bookmarkSvc):
        SiteHandler.__init__(self)
        self.sensorSuiteSvc = sensorSuiteSvc
        self.bookmarkSvc = bookmarkSvc

    def GetSiteData(self, siteID, bookmark):
        return BookmarkSiteData(siteID, GetBookmarkPosition(bookmark), bookmark=bookmark)

    @telemetry.ZONE_METHOD
    def GetSitesForSolarSystem(self, solarSystemID):
        return self.bookmarkSvc.GetActiveBookmarksFiltered(solarSystemID=solarSystemID, usePersonalFilter=True, personal=True)

    def IsVisible(self, siteData):
        return GetBookmarkFolderVisibilityManager().IsFolderVisible((siteData.bookmark.folderID, siteData.bookmark.subfolderID))

    def OnSitesUpdated(self, sites):
        for siteID, siteData in sites.iteritems():
            bm = self.bookmarkSvc.GetBookmark(siteData.bookmark.bookmarkID)
            siteData.bookmark = bm
            siteData.name = CleanText(bm.memo)
            bracket = self.siteController.spaceLocations.GetBracketBySiteID(siteID)
            if bracket:
                bracket.UpdateSiteLabel()
                bracket.UpdateSiteName(CleanText(bm.note))


class SharedBookmarkHandler(BookmarkHandler):
    siteType = SHARED_BOOKMARK
    filterIconPath = 'res:/UI/Texture/classes/Bookmarks/sharedBookmarkSensorOverlay.png'
    filterLabel = 'UI/Inflight/Scanner/SharedSiteFilterLabel'
    color = SITE_COLOR_SHARED_BOOKMARK
    siteIconData = SITE_SHARED_BOOKMARK

    def GetSiteData(self, siteID, bookmark):
        return SharedBookmarkSiteData(siteID, GetBookmarkPosition(bookmark), bookmark=bookmark)

    @telemetry.ZONE_METHOD
    def GetSitesForSolarSystem(self, solarSystemID):
        return self.bookmarkSvc.GetActiveBookmarksFiltered(solarSystemID=solarSystemID, usePersonalFilter=True, personal=False)
