#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\baseContentProviderDungeons.py
from collections import defaultdict
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.agencyConst import SECURITY_THRESHOLDS
from eve.client.script.ui.shared.agencyNew.agencyUtil import GetRoundRobinMix
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem

class BaseContentProviderDungeons(BaseContentProvider):
    __notifyevents__ = BaseContentProvider.__notifyevents__ + ['OnSignalTrackerAnomalyUpdate',
     'OnSignalTrackerSignatureUpdate',
     'OnSessionChanged',
     'OnSystemScanDone']

    def __init__(self):
        super(BaseContentProviderDungeons, self).__init__()
        self.dungeonInstances = None
        sm.RegisterNotify(self)

    def _ConstructContentPieces(self):
        self.dungeonInstances = self.GetAllDungeonInstances()
        solarSystemIDsByBucket = self.GetSolarSystemIDsByBucket()
        contentPieces = []
        for solarSystemID in GetRoundRobinMix(solarSystemIDsByBucket, numMax=agencyConst.MAX_CONTENT_PIECES_MAX):
            if self.dungeonInstances is None or self.contentPieces is None:
                return
            if solarSystemID not in self.dungeonInstances:
                continue
            contentPiece = self.ConstructContentPiece(solarSystemID, self.dungeonInstances[solarSystemID])
            contentPieces.append(contentPiece)

        contentPieces = sorted(contentPieces, key=self._GetSortKey)
        self.ExtendContentPieces(contentPieces)

    def _GetSortKey(self, contentPiece):
        return contentPiece.GetJumpsToSelfFromCurrentLocation()

    def ConstructContentPiece(self, solarSystemID, dungeonInstances):
        raise NotImplementedError()

    def GetAllDungeonInstances(self):
        if not self.dungeonInstances:
            self.dungeonInstances = self._GetAllDungeonInstances()
        return self.dungeonInstances

    def _GetAllDungeonInstances(self):
        raise NotImplementedError

    def InvalidateDungeonInstances(self):
        self.dungeonInstances = None

    def CheckCriteria(self, solarSystemID):
        return self.CheckSecurityStatusFilterCriteria(solarSystemID) and self.CheckDistanceCriteria(solarSystemID)

    def GetSolarSystemIDsByBucket(self):
        buckets = defaultdict(list)
        if not IsKnownSpaceSystem(session.solarsystemid2):
            solarSystemIDs = (session.solarsystemid2,)
        else:
            solarSystemIDs = self.dungeonInstances.keys() if self.dungeonInstances else []
        for solarSystemID in solarSystemIDs:
            if not self.CheckCriteria(solarSystemID):
                continue
            bucketKey = self._GetBucketKey(solarSystemID)
            buckets[bucketKey].append(solarSystemID)

        bucketKeys = self.GetBucketKeysSorted(buckets)
        solarSystemsByBucket = [ iter(sorted(buckets[key], key=self._GetSystemSortKey)) for key in bucketKeys ]
        return solarSystemsByBucket

    def _GetBucketKey(self, solarSystemID):
        securityStatus = sm.GetService('map').GetSecurityStatus(solarSystemID)
        for i, threshold in enumerate(SECURITY_THRESHOLDS):
            if securityStatus > threshold:
                return i

        return len(SECURITY_THRESHOLDS)

    def GetBucketKeysSorted(self, buckets):
        bucketKeys = sorted(buckets.keys())
        for key, solarSystemIDs in buckets.iteritems():
            if session.solarsystemid2 in solarSystemIDs:
                bucketKeys.remove(key)
                bucketKeys.insert(0, key)

        return bucketKeys

    def _GetSystemSortKey(self, solarSystemID):
        return self.GetNumJumpsToSystem(solarSystemID)

    def OnSignalTrackerAnomalyUpdate(self, *args):
        self.InvalidateDungeonInstances()
        self.InvalidateContentPieces()

    def OnSignalTrackerSignatureUpdate(self, *args):
        self.InvalidateDungeonInstances()
        self.InvalidateContentPieces()

    def OnSystemScanDone(self):
        self.InvalidateDungeonInstances()
        self.InvalidateContentPieces()

    def OnSessionChanged(self, isremote, sess, change):
        if 'locationid' in change:
            self.InvalidateContentPieces()
        self.InvalidateDungeonInstances()
