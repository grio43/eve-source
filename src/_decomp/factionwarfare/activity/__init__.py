#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\factionwarfare\activity\__init__.py


class SolarSystemScores(object):

    def __init__(self, solar_system_id, scores):
        self.solar_system_id = solar_system_id
        self.scores = scores

    def __eq__(self, other):
        if not isinstance(other, SolarSystemScores):
            return NotImplemented
        return self.solar_system_id == other.solar_system_id and self.scores == other.scores

    def __ne__(self, other):
        return not self == other


class Score(object):

    def __init__(self, faction_id, contribution, floor):
        self.faction_id = faction_id
        self.contribution = contribution
        self.floor = floor

    def __eq__(self, other):
        if not isinstance(other, Score):
            return NotImplemented
        return self.faction_id == other.faction_id and self.contribution == other.contribution and self.floor == other.floor

    def __ne__(self, other):
        return not self == other
