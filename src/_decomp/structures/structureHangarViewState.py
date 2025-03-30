#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\structures\structureHangarViewState.py
from gametime import GetWallclockTime
from structures import STATES, ALL_UPKEEP_STATES

class StructureHangarViewState(object):
    _operatingState = None
    _upkeepState = None
    _damageState = None
    _timerStartAt = None
    _timerEndAt = None
    _timerPauseAt = None

    def __init__(self, operatingState, upkeepState, damageState, timer):
        if operatingState not in STATES:
            raise ValueError('Unknown operatingState')
        if upkeepState not in ALL_UPKEEP_STATES:
            raise ValueError('Unknown upkeepState')
        self._operatingState = operatingState
        self._upkeepState = upkeepState
        self._damageState = damageState
        if timer is not None:
            self._timerStartAt = timer[0]
            self._timerEndAt = timer[1]
            self._timerPauseAt = timer[2]

    def __repr__(self):
        return 'StructureHangarState(operatingState=%r, upkeepState=%r, damageState=%r, timer=%r)' % (self._operatingState,
         self._upkeepState,
         self._damageState,
         (self._timerStartAt, self._timerEndAt, self._timerPauseAt))

    @property
    def operatingState(self):
        return self._operatingState

    @property
    def upkeepState(self):
        return self._upkeepState

    @property
    def damageState(self):
        return self._damageState

    @property
    def timerIsProgressing(self):
        return self._timerStartAt is not None and self._timerPauseAt is None

    @property
    def timerIsPaused(self):
        return self._timerStartAt is not None and self._timerPauseAt is not None

    @property
    def timerEndAt(self):
        return self._timerEndAt

    @property
    def timerProgress(self):
        if self._timerStartAt is None or self._timerEndAt is None:
            return
        if self._timerPauseAt is not None:
            timerCurrent = self._timerPauseAt
        else:
            timerCurrent = GetWallclockTime()
        progress = (1.0 * timerCurrent - self._timerStartAt) / (self._timerEndAt - self._timerStartAt)
        return max(0.0, min(1.0, progress))
