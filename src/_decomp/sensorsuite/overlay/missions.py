#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sensorsuite\overlay\missions.py
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToBookmark
import localization
from sensorsuite.overlay.bookmarks import GetBookmarkPosition, GetBookmarkSiteActions
from sensorsuite.overlay.brackets import SensorSuiteBracket, INNER_ICON_COLOR
from sensorsuite.overlay.siteconst import SITE_COLOR_MISSION, SITE_MISSION
from sensorsuite.overlay.sitedata import SiteData
from sensorsuite.overlay.sitehandler import SiteHandler
from sensorsuite.overlay.sitetype import MISSION
import logging
from eveservices.menu import GetMenuService
logger = logging.getLogger(__name__)

class MissionSiteData(SiteData):
    siteType = MISSION
    baseColor = SITE_COLOR_MISSION

    def __init__(self, siteID, position, bookmark):
        SiteData.__init__(self, siteID, position)
        self.bookmark = bookmark
        self.name = localization.GetByMessageID(bookmark.missionNameID)

    def GetBracketClass(self):
        return MissionBracket

    def GetName(self):
        return self.name

    def GetMenu(self):
        return GetMenuService().BookmarkMenu(self.bookmark)

    def WarpToAction(self, itemID, distance, *args):
        WarpToBookmark(self.bookmark, warpRange=distance)

    def GetSiteActions(self):
        return GetBookmarkSiteActions(self.bookmark)


class MissionBracket(SensorSuiteBracket):
    outerColor = SITE_COLOR_MISSION.GetRGBA()
    innerColor = INNER_ICON_COLOR.GetRGBA()
    innerIconResPath = 'res:/UI/Texture/classes/SensorSuite/missions.png'
    outerTextures = ('res:/UI/Texture/classes/SensorSuite/bracket_mission_1.png', 'res:/UI/Texture/classes/SensorSuite/bracket_mission_2.png', 'res:/UI/Texture/classes/SensorSuite/bracket_mission_3.png', 'res:/UI/Texture/classes/SensorSuite/bracket_mission_4.png')

    def ApplyAttributes(self, attributes):
        SensorSuiteBracket.ApplyAttributes(self, attributes)
        self.UpdateSiteName(localization.GetByMessageID(self.data.bookmark.missionNameID))

    def GetMenu(self):
        return self.data.GetMenu()


class MissionHandler(SiteHandler):
    siteType = MISSION
    filterIconPath = 'res:/UI/Texture/classes/SensorSuite/missions.png'
    filterLabel = 'UI/Inflight/Scanner/MissionSiteFilterLabel'
    color = SITE_COLOR_MISSION
    siteIconData = SITE_MISSION

    def __init__(self, bookmarkSvc):
        SiteHandler.__init__(self)
        self.bookmarkSvc = bookmarkSvc

    def GetSitesForSolarSystem(self, solarSystemID):
        agentBookmarks = self.bookmarkSvc.GetAgentBookmarks()
        return {bm.bookmarkID:bm for bm in agentBookmarks.itervalues() if bm.locationID == solarSystemID}

    def GetSiteData(self, siteID, bookmark):
        return MissionSiteData(siteID, GetBookmarkPosition(bookmark), bookmark=bookmark)

    def OnSitesUpdated(self, sites):
        for agentMissionSiteId, siteData in sites.iteritems():
            bookmark = self.bookmarkSvc.GetAgentBookmarks()[agentMissionSiteId]
            self._UpdateSitePosition(siteData, bookmark)

    def _UpdateSitePosition(self, siteData, bookmark):
        bookmarkPosition = (bookmark.x, bookmark.y, bookmark.z)
        if bookmarkPosition != siteData.position:
            siteData.bookmark = bookmark
            siteData.position = (bookmark.x, bookmark.y, bookmark.z)
            self.siteController.UpdateSitePosition(siteData)
