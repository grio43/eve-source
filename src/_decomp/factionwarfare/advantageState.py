#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\factionwarfare\advantageState.py
MAX_ACTIVITY_POINTS = 100000.0

class AdvantageState(object):

    def __init__(self, contributionAndTerrainByFactionID):
        self._contributionAndTerrainByFactionID = {}
        for factionID, (contribution, terrain) in contributionAndTerrainByFactionID.iteritems():
            if contribution < 0.0 or contribution > 1.0:
                raise ValueError('contribution value must be in range (0.0 to 1.0)')
            if terrain < 0.0 or terrain > 1.0:
                raise ValueError('terrain value must be in range (0.0 to 1.0)')
            if contribution + terrain > 1.0:
                raise ValueError('sum of contribution+terrain cannot exceed 1.0')
            self._contributionAndTerrainByFactionID[factionID] = (contribution, terrain)

    @staticmethod
    def CreateAdvantageStateFromActivityState(activityTrackerState, maxActivityPoints = MAX_ACTIVITY_POINTS):
        maxActivityPoints = float(maxActivityPoints)
        contributionAndTerrainByFactionID = {factionID:(contributionPoints / maxActivityPoints, terrainPoints / maxActivityPoints) for factionID, (contributionPoints, terrainPoints) in activityTrackerState.iteritems()}
        return AdvantageState(contributionAndTerrainByFactionID)

    def __repr__(self):
        return 'AdvantageState<%r>' % self._contributionAndTerrainByFactionID

    def __eq__(self, other):
        if isinstance(other, AdvantageState):
            return self._contributionAndTerrainByFactionID == other._contributionAndTerrainByFactionID
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def factionIDs(self):
        return self._contributionAndTerrainByFactionID.keys()

    def _GetScores(self, factionID):
        return self._contributionAndTerrainByFactionID.get(factionID, (0, 0))

    def GetContributionPoints(self, factionID):
        return self._GetScores(factionID)[0] * MAX_ACTIVITY_POINTS

    def GetContributionScore(self, factionID):
        return self._GetScores(factionID)[0]

    def GetTerrainScore(self, factionID):
        return self._GetScores(factionID)[1]

    def GetAdvantageScore(self, factionID):
        return sum(self._GetScores(factionID))

    def GetNetAdvantageScore(self, factionID, otherFactionID):
        return self.GetAdvantageScore(factionID) - self.GetAdvantageScore(otherFactionID)

    def GetBonusPointsFromAdvantage(self, points, factionID, otherFactionID):
        netAdvantageScore = self.GetNetAdvantageScore(factionID, otherFactionID)
        if netAdvantageScore <= 0:
            return 0
        bonusPoints = int(max(netAdvantageScore * abs(points), 1))
        if points < 0:
            bonusPoints = -bonusPoints
        return bonusPoints
