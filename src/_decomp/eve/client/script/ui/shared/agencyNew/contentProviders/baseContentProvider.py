#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\baseContentProvider.py
import logging
import blue
import telemetry
import uthread2
from carbon.common.script.util.logUtil import LogInfo
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters, agencySignals
from eve.client.script.ui.shared.agencyNew.agencyUtil import GetNumberOfJumps, GetSystemsWithinJumpRange
from eve.common.lib import appConst
from eve.common.script.sys.idCheckers import IsVoidSpaceSystem
from eve.common.script.sys.idCheckers import IsWormholeSystem, IsAbyssalSpaceSystem, IsKnownSpaceSystem
logger = logging.getLogger(__name__)

class BaseContentProvider(object):
    contentType = None
    contentGroup = None
    contentTypeFilters = (agencyConst.CONTENTTYPE_SUGGESTED,)
    __notifyevents__ = ['OnNewState']

    def __init__(self):
        self.contentPieces = None
        self.isConstructing = False
        agencyFilters.onFilterChanged.connect(self.OnAgencyFilterChanged)
        sm.RegisterNotify(self)

    def OnNewState(self, bp):
        self.InvalidateContentPieces()

    def OnAgencyFilterChanged(self, contentGroupID, filterType, value):
        if contentGroupID != self.contentGroup:
            return
        self.contentPieces = None
        uthread2.StartTasklet(self.ConstructContentPieces)

    def GetContentPieces(self):
        if self.contentPieces is None:
            self.ConstructContentPieces()
        return self.contentPieces or []

    def InvalidateContentPieces(self):
        self.contentPieces = None
        agencySignals.on_content_pieces_invalidated(self.contentGroup)

    def ConstructContentPieces(self):
        self.isConstructing = True
        self.contentPieces = []
        startTime = blue.os.GetWallclockTimeNow()
        try:
            self._ConstructContentPieces()
        except (AttributeError, KeyError, IndexError):
            logger.exception('Content Provider could not construct content pieces')
        else:
            updateTime = (blue.os.GetWallclockTimeNow() - startTime) / appConst.MSEC
            LogInfo('%.1f ms Update time (Agency: %s content provider)' % (updateTime, self.__class__.__name__))
        finally:
            self.isConstructing = False
            agencySignals.on_content_pieces_constructed(self.contentGroup)

    def _ConstructContentPieces(self):
        pass

    @telemetry.ZONE_METHOD
    def CheckDistanceCriteria(self, solarSystemID):
        distance = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_DISTANCE)
        if solarSystemID is None:
            return False
        elif IsAbyssalSpaceSystem(session.solarsystemid2) or IsVoidSpaceSystem(session.solarsystemid2):
            return False
        elif distance == agencyConst.DISTANCE_REGION:
            return self.CheckRegionOrConstellationCriteria(solarSystemID)
        elif IsWormholeSystem(session.solarsystemid2) or distance == agencyConst.DISTANCE_CURRSYSTEM:
            return solarSystemID == session.solarsystemid2
        elif distance == agencyConst.DISTANCE_ANY:
            return True
        numJumps = self.GetNumJumpsToSystem(solarSystemID)
        if numJumps is None:
            return False
        else:
            return numJumps <= distance

    def CheckRegionOrConstellationCriteria(self, solarSystemID):
        constellationID = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_CONSTELLATION)
        if constellationID == agencyConst.CONSTELLATION_ANY:
            contentRegionID = cfg.mapSystemCache.Get(solarSystemID).regionID
            return contentRegionID == agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_REGION)
        else:
            contentConstellationID = cfg.mapSystemCache.Get(solarSystemID).constellationID
            return contentConstellationID == constellationID

    @telemetry.ZONE_METHOD
    def GetNumJumpsToSystem(self, solarSystemID):
        return GetNumberOfJumps(solarSystemID)

    @telemetry.ZONE_METHOD
    def IsInHighSec(self, solarSystemID):
        systemSec = sm.GetService('map').GetSecurityStatus(solarSystemID)
        return systemSec >= 0.5

    def AppendContentPiece(self, contentPiece):
        if self.contentPieces is not None:
            self.contentPieces.append(contentPiece)

    def ExtendContentPieces(self, contentPieces):
        if self.contentPieces is not None:
            self.contentPieces.extend(contentPieces)

    @telemetry.ZONE_METHOD
    def GetAllSolarSystemIDsWithinJumpRange(self, shouldIncludeAvoided = False):
        maxJumps = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_DISTANCE)
        if maxJumps == agencyConst.DISTANCE_REGION:
            region_id = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_REGION)
            return sorted(cfg.mapRegionCache[region_id].solarSystemIDs, key=lambda systemID: GetNumberOfJumps(systemID))
        if not IsKnownSpaceSystem(session.solarsystemid2):
            return [session.solarsystemid2]
        maxJumps = maxJumps + 1 if maxJumps > 0 else maxJumps
        systemsWithinJumpRange = GetSystemsWithinJumpRange(fromID=session.solarsystemid2, jumpCountMin=0, jumpCountMax=maxJumps, shouldIncludeAvoided=shouldIncludeAvoided)
        solarSystemIDsLists = systemsWithinJumpRange.values()
        return [ solarSystemID for solarSystemIDs in solarSystemIDsLists for solarSystemID in solarSystemIDs ]

    def ClearNewContent(self, contentPiece):
        pass

    def ApplyDefaultFilters(self):
        pass

    def CheckSecurityStatusFilterCriteria(self, solarSystemID):
        securityStatus = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_SECURITYSTATUS)
        if securityStatus == agencyConst.FILTERVALUE_ANY:
            return True
        systemSec = sm.GetService('map').GetSecurityStatus(solarSystemID)
        if securityStatus == agencyConst.SECURITYSTATUS_HIGHSEC:
            return systemSec >= 0.45
        elif securityStatus == agencyConst.SECURITYSTATUS_NULLSEC:
            return systemSec <= 0.0
        else:
            return 0.0 < systemSec < 0.45
