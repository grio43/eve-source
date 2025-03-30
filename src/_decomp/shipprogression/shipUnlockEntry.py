#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\shipUnlockEntry.py


class ShipUnlockEntry(object):

    def __init__(self, shipGroupID, unlocked, seen):
        self._shipGroupID = shipGroupID
        self._unlocked = unlocked
        self._seen = seen

    @property
    def shipGroupID(self):
        return self._shipGroupID

    @property
    def unlocked(self):
        return self._unlocked

    def SetUnlocked(self, unlocked):
        self._unlocked = unlocked

    @property
    def seen(self):
        return self._seen

    def SetSeen(self, seen):
        self._seen = seen

    @property
    def FactionID(self):
        return self.shipGroupID[0]

    @property
    def GroupID(self):
        return self.shipGroupID[1]
