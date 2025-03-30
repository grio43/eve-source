#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\solarsysteminterference\solarsystemInterferenceState.py
from carbon.common.lib.const import SEC
from solarsysteminterference.const import INTERFERENCE_BAND_NONE, INTERFERENCE_BAND_LOW, INTERFERENCE_BAND_MEDIUM, INTERFERENCE_BAND_HIGH, INTERFERENCE_BAND_HIGH_THRESHOLD, INTERFERENCE_BAND_MEDIUM_THRESHOLD

class SolarsystemInterferenceState(object):

    def __init__(self, interferenceLevel, lastDecayTickTimestamp, interferenceDecreasePerDecayTick, decayTickPeriod, maxInterferenceLevel, quiescentInterferenceLevel):
        if interferenceDecreasePerDecayTick <= 0:
            raise ValueError('interferenceDecreasePerDecayTick must be greater than 0')
        if decayTickPeriod <= 0:
            raise ValueError('decayTickPeriod must be greater than 0')
        if maxInterferenceLevel <= quiescentInterferenceLevel:
            raise ValueError('maxInterferenceLevel must be greater than quiescentInterferenceLevel')
        if interferenceLevel > maxInterferenceLevel:
            raise ValueError('interferenceLevel (%.2f) must be less than or equal to maxInterferenceLevel (%.2f)' % (interferenceLevel, maxInterferenceLevel))
        if interferenceLevel < quiescentInterferenceLevel:
            raise ValueError('interferenceLevel (%.2f) must be greater than or equal to quiescentInterferenceLevel (%.2f)' % (interferenceLevel, quiescentInterferenceLevel))
        self._interferenceLevel = interferenceLevel
        self._lastDecayTickTimestamp = lastDecayTickTimestamp
        self._interferenceDecreasePerDecayTick = interferenceDecreasePerDecayTick
        self._decayTickPeriod = decayTickPeriod
        self._maxInterferenceLevel = maxInterferenceLevel
        self._quiescentInterferenceLevel = quiescentInterferenceLevel

    def __repr__(self):
        return 'SolarsystemInterferenceState(interferenceLevel=%r, lastDecayTickTimestamp=%r, interferenceDecreasePerDecayTick=%r, decayTickPeriod=%r, maxInterferenceLevel=%r, quiescentInterferenceLevel=%r)' % (self._interferenceLevel,
         self._lastDecayTickTimestamp,
         self._interferenceDecreasePerDecayTick,
         self._decayTickPeriod,
         self._maxInterferenceLevel,
         self._quiescentInterferenceLevel)

    def __eq__(self, other):
        if other is None:
            return False
        return self._interferenceLevel == other._interferenceLevel and self._lastDecayTickTimestamp == other._lastDecayTickTimestamp and self._interferenceDecreasePerDecayTick == other._interferenceDecreasePerDecayTick and self._decayTickPeriod == other._decayTickPeriod and self._maxInterferenceLevel == other._maxInterferenceLevel and self._quiescentInterferenceLevel == other._quiescentInterferenceLevel

    @property
    def interferenceLevel(self):
        return self._interferenceLevel

    @property
    def lastDecayTickTimestamp(self):
        return self._lastDecayTickTimestamp

    @property
    def interferenceDecreasePerDecayTick(self):
        return self._interferenceDecreasePerDecayTick

    @property
    def decayTickPeriod(self):
        return self._decayTickPeriod

    @property
    def maxInterferenceLevel(self):
        return self._maxInterferenceLevel

    @property
    def quiescentInterferenceLevel(self):
        return self._quiescentInterferenceLevel

    @property
    def isAtQuiescentLevel(self):
        return self._interferenceLevel <= self._quiescentInterferenceLevel

    @property
    def interferenceRange(self):
        return self._maxInterferenceLevel - self._quiescentInterferenceLevel

    @property
    def normalisedInterferenceLevel(self):
        return (self._interferenceLevel - self._quiescentInterferenceLevel) / self.interferenceRange

    @property
    def interferenceBand(self):
        if self.isAtQuiescentLevel:
            return INTERFERENCE_BAND_NONE
        normalisedInterferenceLevel = self.normalisedInterferenceLevel
        if normalisedInterferenceLevel > INTERFERENCE_BAND_HIGH_THRESHOLD:
            return INTERFERENCE_BAND_HIGH
        if normalisedInterferenceLevel > INTERFERENCE_BAND_MEDIUM_THRESHOLD:
            return INTERFERENCE_BAND_MEDIUM
        return INTERFERENCE_BAND_LOW

    def CanAffordCost(self, solarsystemInterferenceCost):
        return self._interferenceLevel + solarsystemInterferenceCost <= self._maxInterferenceLevel


def _GetDecayResult(state, timestamp):
    timeDelta = timestamp - state.lastDecayTickTimestamp
    if timeDelta < 0:
        raise ValueError('_GetDecayResult cannot be calculated for negative timeDelta')
    numDecayTicks = timeDelta / (state.decayTickPeriod * SEC)
    interferenceDecrease = numDecayTicks * state.interferenceDecreasePerDecayTick
    newInterferenceLevel = max(state.quiescentInterferenceLevel, state.interferenceLevel - interferenceDecrease)
    newDecayTickTimestamp = state.lastDecayTickTimestamp + numDecayTicks * state.decayTickPeriod * SEC
    return (newInterferenceLevel, newDecayTickTimestamp)


def GetNewState(originalState, newInterferenceLevel, newDecayTickTimestamp):
    return SolarsystemInterferenceState(newInterferenceLevel, newDecayTickTimestamp, originalState.interferenceDecreasePerDecayTick, originalState.decayTickPeriod, originalState.maxInterferenceLevel, originalState.quiescentInterferenceLevel)


def CalculateStateAtTime(state, timestamp):
    if state.isAtQuiescentLevel:
        return state
    if timestamp < state.lastDecayTickTimestamp:
        return state
    newInterferenceLevel, newDecayTickTimestamp = _GetDecayResult(state, timestamp)
    return GetNewState(state, newInterferenceLevel, newDecayTickTimestamp)


def CalculateStateAfterAddingInterferenceAtTime(state, interferenceIncrease, timestamp):
    if interferenceIncrease <= 0.0:
        raise ValueError('interferenceIncrease must be greater-than 0')
    newInterferenceLevel, newDecayTickTimestamp = _GetDecayResult(state, timestamp)
    stateAtTime = GetNewState(state, newInterferenceLevel, newDecayTickTimestamp)
    if not stateAtTime.CanAffordCost(interferenceIncrease):
        raise ExcessInterferenceError('Too much interference')
    return GetNewState(state, newInterferenceLevel + interferenceIncrease, newDecayTickTimestamp)


class ExcessInterferenceError(StandardError):
    pass
