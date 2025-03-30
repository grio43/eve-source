#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\data_types.py


class SovHubInfo(object):

    @property
    def hubID(self):
        return self._hubID

    @property
    def corporationID(self):
        return self._corporationID

    @property
    def ownerID(self):
        return self._corporationID

    @property
    def allianceID(self):
        return self._allianceID

    @property
    def claimTime(self):
        return self._claimTime

    @property
    def isSovHubMode(self):
        return self._isSovHubMode

    @property
    def isIHubMode(self):
        return not self._isSovHubMode

    def __init__(self, hubID, corporationID, allianceID, claimTime, isSovHubMode):
        self._hubID = hubID
        self._corporationID = corporationID
        self._allianceID = allianceID
        self._claimTime = claimTime
        self._isSovHubMode = isSovHubMode

    def __repr__(self):
        return '<SovHubInfo hubID=%s, corporationID=%s, allianceID=%s, isSovHubMode=%s>' % (self.hubID,
         self.corporationID,
         self.allianceID,
         self.isSovHubMode)


class SovClaimInfo(object):

    @property
    def claimStructureID(self):
        return self._claimStructureID

    @property
    def corporationID(self):
        return self._corporationID

    @property
    def ownerID(self):
        return self._corporationID

    @property
    def allianceID(self):
        return self._allianceID

    def __init__(self, claimStructureID, corporationID, allianceID):
        self._claimStructureID = claimStructureID
        self._corporationID = corporationID
        self._allianceID = allianceID

    def __repr__(self):
        return '<SovClaimInfo claimStructureID=%s, corporationID=%s, allianceID=%s>' % (self.claimStructureID, self.corporationID, self.allianceID)
