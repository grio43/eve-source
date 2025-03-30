#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\menucheckers\bookmarkChecker.py
from menucheckers.decorators import decorated_checker, explain_failure_with
from menucheckers.celestialCheckers import CelestialChecker
import inventorycommon.const as invConst
import eve.common.lib.appConst as appConst
from evetypes import GetCategoryID
from eve.common.script.mgt.helpers.bookmark import should_treat_bookmark_as_solar_system
from eve.common.script.sys.idCheckers import IsSolarSystem, IsStation, IsDeprecatedStation
import geo2

@decorated_checker

class BookmarkChecker(CelestialChecker):

    def __init__(self, item, bookmark, cfg, sessionInfo = None, serviceManager = None):
        self.bookmark = bookmark
        self.parentID = bookmark.locationID
        super(BookmarkChecker, self).__init__(item, cfg, sessionInfo, serviceManager)

    def OfferAddWaypoint(self):
        if not super(BookmarkChecker, self).OfferAddWaypoint():
            return False
        if self.IsStructureNoLongerInSpaceButWasOnceInPilotSystem():
            return False
        return True

    def OfferApproachLocation(self):
        if self.GetBallpark() is None:
            return False
        if not self.IsSpecificItem():
            return False
        if not self.IsPilotFlyingInSameSystem():
            return False
        if self.session.isPilotWarping():
            return False
        if not (self.IsInPilotLocation() or self.bookmark.locationID == session.solarsystemid):
            return False
        dist = self.getDistanceToActiveShip()
        if dist is None or dist >= appConst.maxApproachDistance:
            return False
        return True

    def OfferAlignTo(self):
        if self.OfferApproachLocation():
            return False
        if self.GetBallpark() is None:
            return False
        if not self.IsSpecificItem():
            return False
        if self.IsAgentBookmark():
            return False
        if not self.IsPilotFlyingInSameSystem():
            return False
        if not self.session.isInWarpRange(self.getDistanceToActiveShip()):
            return False
        if self.session.isPilotWarping():
            return False
        return True

    def OfferEditBookmark(self):
        if self.IsAgentBookmark():
            return False
        if self.IsReadOnlyBookmark():
            return False
        return self.IsEditableWithCharacterRoles()

    def OfferOpenCargoHold(self):
        return False

    def OfferSetAsCameraInterest(self):
        if IsSolarSystem(self.itemID):
            return False
        return super(BookmarkChecker, self).OfferSetAsCameraInterest()

    def OfferSetDestination(self):
        if not super(BookmarkChecker, self).OfferSetDestination():
            return False
        if self.IsStructureNoLongerInSpaceButWasOnceInPilotSystem():
            return False
        return True

    def OfferWarpTo(self):
        return self._CanWarpToItem()

    def IsAgentBookmark(self):
        return bool(getattr(self.bookmark, 'agentID', 0) and hasattr(self.bookmark, 'locationNumber'))

    def IsDeadspaceBookmark(self):
        return bool(getattr(self.bookmark, 'deadspace', 0))

    def IsInPilotLocation(self):
        if self.session.solarsystemid in (self.item.itemID, self.bookmark.locationID):
            return True
        return super(BookmarkChecker, self).IsInPilotLocation()

    def IsReadOnlyBookmark(self):
        return isinstance(getattr(self.bookmark, 'bookmarkID', 0), tuple)

    def IsStructureNoLongerInSpaceButWasOnceInPilotSystem(self):
        return self.IsStructure() and not self.IsStructureInSpace() and self.IsInPilotLocation()

    def IsEditableWithCharacterRoles(self):
        folder = self.sm.GetService('bookmarkSvc').GetBookmarkFolder(self.bookmark.folderID)
        if folder.accessLevel in (appConst.ACCESS_PERSONAL, appConst.ACCESS_MANAGE, appConst.ACCESS_ADMIN):
            return True
        if folder.accessLevel == appConst.ACCESS_USE and self.bookmark.creatorID == self.session.charid:
            return True
        return False

    def ShouldNotTreatBookmarkAsSolarSystem(self):
        category_id = GetCategoryID(self.bookmark.typeID)
        if not should_treat_bookmark_as_solar_system(category_id=category_id, type_id=self.bookmark.typeID):
            return True
        return False

    @explain_failure_with('UI/Menusvc/MenuHints/NotInRange')
    def getDistanceToActiveShip(self):
        bp = self.GetBallpark()
        ownBall = self.session.getBall()
        bookmark = self.bookmark
        if not all([bp,
         bookmark,
         bookmark.locationID,
         bookmark.locationID == self.session.solarsystemid]):
            return
        if (bookmark.typeID == invConst.typeSolarSystem or bookmark.itemID == bookmark.locationID) and bookmark.x is not None:
            location = None
            if hasattr(bookmark, 'locationType') and bookmark.locationType in ('agenthomebase', 'objective'):
                location = self.sm.GetService('agents').GetAgentMoniker(bookmark.agentID).GetEntryPoint()
            if location is None:
                location = (bookmark.x, bookmark.y, bookmark.z)
            myLocation = (ownBall.x, ownBall.y, ownBall.z) if ownBall else None
            if myLocation and location:
                return geo2.Vec3DistanceD(myLocation, location)
            return 0.0
        if self.bookmark.itemID in bp.balls:
            b = bp.balls[self.bookmark.itemID]
            return b.surfaceDist
        if self.ShouldNotTreatBookmarkAsSolarSystem():
            try:
                return geo2.Vec3DistanceD((ownBall.x, ownBall.y, ownBall.z), (self.bookmark.x, self.bookmark.y, self.bookmark.z))
            except Exception:
                import log
                log.LogError('Error when trying to find bookmark location for bookmark %s' % bookmark)

        return 0.0

    def GetWaypointSolarsystemID(self):
        solarsystemID = super(BookmarkChecker, self).GetWaypointSolarsystemID()
        if solarsystemID:
            return solarsystemID
        itemID, typeID = self.GetMapIDs()
        if IsSolarSystem(itemID):
            return itemID
        if IsStation(itemID) and not IsDeprecatedStation(typeID):
            return self.cfg.stations.Get(itemID).solarSystemID
        if GetCategoryID(typeID) == invConst.categoryStructure:
            try:
                solarsystemID = self.cfg.evelocations.Get(self.item.itemID).solarSystemID
                if solarsystemID is not None:
                    return solarsystemID
            except (KeyError, ValueError):
                pass

            structureInfo = self.sm.GetService('structureDirectory').GetStructureInfo(itemID)
            if structureInfo and structureInfo.solarSystemID:
                return structureInfo.solarSystemID

    def GetMapIDs(self):
        typeID = self.item.typeID
        itemID = self.item.itemID
        if not any((self.IsStation(),
         self.IsStructure(),
         self.IsSolarsystem(),
         self.IsConstellation(),
         self.IsRegion())):
            itemID = self.parentID
            parentBookmarkItem = sm.GetService('map').GetItem(itemID)
            if parentBookmarkItem and parentBookmarkItem.groupID == invConst.groupSolarSystem:
                typeID = parentBookmarkItem.typeID
        return (itemID, typeID)
