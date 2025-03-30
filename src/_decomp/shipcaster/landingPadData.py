#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcaster\landingPadData.py


class LandingPadData(object):

    def __init__(self, itemID, solarSystemID, factionID, isBuilt, linkTimestamp = None, isDisrupted = False):
        self._itemID = itemID
        self._solarSystemID = solarSystemID
        self._factionID = factionID
        self._isBuilt = isBuilt
        self._linkTimestamp = linkTimestamp
        self._isDisrupted = isDisrupted

    def __eq__(self, other):
        if isinstance(other, LandingPadData):
            return self._itemID == other._itemID and self._solarSystemID == other._solarSystemID and self._factionID == other._factionID and self._isBuilt == other._isBuilt and self._linkTimestamp == other._linkTimestamp and self._isDisrupted == other._isDisrupted
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._itemID,
         self._solarSystemID,
         self._factionID,
         self._isBuilt,
         self._linkTimestamp,
         self._isDisrupted))

    __cmp__ = None

    @property
    def itemID(self):
        return self._itemID

    @property
    def solarSystemID(self):
        return self._solarSystemID

    @property
    def factionID(self):
        return self._factionID

    @property
    def isBuilt(self):
        return self._isBuilt

    @property
    def linkTimestamp(self):
        if not self._isBuilt:
            return None
        return self._linkTimestamp

    @property
    def isLinked(self):
        return bool(self.linkTimestamp)

    @property
    def isDisrupted(self):
        return self._isDisrupted

    @property
    def canBeLinked(self):
        if not self.isBuilt:
            return False
        if self.isDisrupted:
            return False
        return True

    def GetCopyWithNewTimestamp(self, timestamp):
        return LandingPadData(self._itemID, self._solarSystemID, self._factionID, self._isBuilt, timestamp, self._isDisrupted)

    def GetCopyWithNewDisruptState(self, isDisrupted):
        return LandingPadData(self._itemID, self._solarSystemID, self._factionID, self._isBuilt, self._linkTimestamp, isDisrupted)

    def __repr__(self):
        return 'LandingPadData: itemID=%s, solarSystemID=%s, factionID=%s, isBuilt=%s, timestamp=%s, isDisrupted=%s' % (self._itemID,
         self._solarSystemID,
         self._factionID,
         self._isBuilt,
         self._linkTimestamp,
         self.isDisrupted)
