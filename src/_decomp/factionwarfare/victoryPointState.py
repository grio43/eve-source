#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\factionwarfare\victoryPointState.py


class VictoryPointState(object):

    def __init__(self, vpScore, vpThreshold):
        if vpScore is None:
            raise ValueError('vpScore cannot be None')
        if vpThreshold is None:
            raise ValueError('vpThreshold cannot be None')
        if vpScore < 0:
            raise ValueError('vpScore must be >=0')
        if vpThreshold <= 0:
            raise ValueError('vpThreshold must be >0')
        self._vpScore = vpScore
        self._vpThreshold = vpThreshold

    def __repr__(self):
        return 'VictoryPointState(vpScore=%r, vpThreshold=%r)' % (self._vpScore, self._vpThreshold)

    def __eq__(self, other):
        if isinstance(other, VictoryPointState):
            return self._vpScore == other._vpScore and self._vpThreshold == other._vpThreshold
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def score(self):
        return self._vpScore

    @property
    def threshold(self):
        return self._vpThreshold

    @property
    def isVulnerable(self):
        return self._vpScore >= self._vpThreshold

    @property
    def isContested(self):
        return self._vpScore > 0

    @property
    def contestedFraction(self):
        return min(self._vpScore / float(self._vpThreshold), 1.0)
