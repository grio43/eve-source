#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\results.py
from collections import defaultdict
import logging
import geo2
from .util import ShouldCacheResult, IsExplorationSite, GetCenter, IsCacheable, IsPerfectResult
from .const import probeResultGood, probeResultPerfect

class Result(object):

    def __repr__(self):
        return '<Result : {} - {}, {}, {}>'.format(self.id, self.scanGroupID, self.groupID, self.typeID)

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.id = None
        self.scanGroupID = None
        self.groupID = None
        self.typeID = None
        self.strengthAttributeID = None
        self.dungeonID = None
        self.dungeonNameID = None
        self.archetypeID = None
        self.factionID = None
        self.pos = None
        self.certainties = []
        self.scanNumberPerfect = None
        self.isPerfect = False
        self.isIdentified = False
        self.itemID = None
        self.difficulty = None
        self.data = None

    def AddEntry(self, entry, scanNumber):
        if self.IsCached():
            return
        self.id = entry.id
        self.data = getattr(entry, 'data', None)
        self._SetPersistableAttributes(entry)
        self.isPerfect = IsPerfectResult(entry)
        self.pos = self._GetPosition(entry)
        self.scanGroupID = entry.scanGroupID
        self._AddCertainty(entry, scanNumber)
        self._SetCachedState(entry, scanNumber)
        self._SetIdentifiedState(entry)
        self.difficulty = getattr(entry, 'difficulty', None)

    def _SetPersistableAttributes(self, entry):
        self._AddPersistableAttribute('itemID', entry)
        self._AddPersistableAttribute('typeID', entry)
        self._AddPersistableAttribute('groupID', entry)
        self._AddPersistableAttribute('strengthAttributeID', entry)
        self._AddPersistableAttribute('dungeonNameID', entry)
        self._AddPersistableAttribute('dungeonID', entry)
        self._AddPersistableAttribute('archetypeID', entry)
        self._AddPersistableAttribute('factionID', entry)

    def IsCached(self):
        return self.scanNumberPerfect is not None

    def IsValid(self, scanNumber):
        if not self.id:
            return False
        if IsExplorationSite(self):
            return True
        lastScanNumber, _ = self.certainties[-1]
        return lastScanNumber == scanNumber

    def GetAsDict(self, scanNumber):
        currentCertainty, prevCertainty = self._GetCertainties(scanNumber)
        return {'id': self.id,
         'scanGroupID': self.scanGroupID,
         'groupID': self.groupID,
         'typeID': self.typeID,
         'certainty': currentCertainty,
         'prevCertainty': prevCertainty,
         'data': self.data,
         'strengthAttributeID': self.strengthAttributeID,
         'dungeonID': self.dungeonID,
         'dungeonNameID': self.dungeonNameID,
         'archetypeID': self.archetypeID,
         'pos': self.pos,
         'factionID': self.factionID,
         'GetDistance': self._GetDistance,
         'isPerfect': self.isPerfect,
         'isIdentified': self.isIdentified,
         'itemID': self.itemID,
         'difficulty': self.difficulty}

    def _GetPosition(self, entry):
        if isinstance(entry.data, tuple):
            center = entry.data
        elif isinstance(entry.data, float):
            center = entry.pos
        elif hasattr(entry.data, 'point'):
            center = entry.data.point
        elif isinstance(entry.data, list):
            center = GetCenter(entry.data)
        else:
            self.logger.error("_Center couldn't find it's center, id=%s, type=%s", self.id, type(self.data))
            center = None
        return center

    def _GetDistance(self, pos):
        if self.pos is not None:
            return geo2.Vec3DistanceD(pos, self.pos)
        else:
            return

    def _GetCertainties(self, scanNumber):
        if self.IsCached():
            if self.scanNumberPerfect == scanNumber:
                return (probeResultPerfect, self._GetCertainty(scanNumber - 1))
            else:
                return (probeResultPerfect, probeResultPerfect)
        return (self._GetCertainty(scanNumber), self._GetCertainty(scanNumber - 1))

    def _GetCertainty(self, scanNumber):
        for s, c in self.certainties:
            if s == scanNumber:
                return c

        return 0.0

    def _AddGroupID(self, entry):
        self._AddPersistableAttribute('groupID', entry)

    def _AddStrengthAttributeID(self, entry):
        self._AddPersistableAttribute('strengthAttributeID', entry)

    def _AddPersistableAttribute(self, attribute, entry):
        val = getattr(entry, attribute, None)
        if val is not None:
            setattr(self, attribute, val)

    def _AddTypeID(self, entry):
        self.typeID = getattr(entry, 'typeID', None)

    def _AddCertainty(self, entry, scanNumber):
        self.certainties.append((scanNumber, entry.certainty))

    def _SetCachedState(self, entry, scanNumber):
        if self.IsCached():
            return
        if ShouldCacheResult(entry):
            self.scanNumberPerfect = scanNumber

    def _SetIdentifiedState(self, entry):
        if self.isIdentified:
            return
        if entry.certainty >= probeResultGood:
            self.isIdentified = True


class ResultsHistory(object):

    def __init__(self):
        self.scanNumber = 0
        self.resultsByTargetID = defaultdict(lambda : Result())
        self.logger = logging.getLogger('probescanning-ResultsHistory')

    def RegisterResults(self, results, incrementScanNumber = True, force = False):
        if incrementScanNumber:
            self.scanNumber += 1
        if results:
            for result in results:
                if result.id in self.resultsByTargetID and not incrementScanNumber and not force:
                    continue
                self.resultsByTargetID[result.id].AddEntry(result, self.scanNumber)

    def LastResultIterator(self):
        for targetID, result in self.resultsByTargetID.iteritems():
            if result.IsValid(self.scanNumber):
                yield result.GetAsDict(self.scanNumber)

    def ClearResults(self, *targetIDs):
        for targetID in targetIDs:
            try:
                del self.resultsByTargetID[targetID]
            except KeyError:
                self.logger.warning("Tried to clear result %s but it wasn't there", targetID)

    def GetLastResults(self):
        return list(self.LastResultIterator())

    def GetResult(self, targetID):
        try:
            return self.resultsByTargetID[targetID]
        except KeyError:
            return None

    def GetResultAsDict(self, targetID):
        try:
            return self.resultsByTargetID[targetID].GetAsDict(self.scanNumber)
        except KeyError:
            return None
