#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcaster\launcherData.py


class LauncherData(object):

    def __init__(self, itemID, solarSystemID, factionID, extraLinkedFactionIDs):
        self._itemID = itemID
        self._solarSystemID = solarSystemID
        self._factionID = factionID
        self._extraLinkedFactionIDs = extraLinkedFactionIDs

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
    def extraLinkedFactionIDs(self):
        return self._extraLinkedFactionIDs
