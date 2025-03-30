#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterenergy\characterEnergyState.py
from carbon.common.lib.const import SEC

class CharacterEnergyState(object):

    def __init__(self, energyLevel, lastRechargeTickTimestamp, energyIncreasePerRechargeTick, rechargeTickPeriod, minEnergyLevel, quiescentEnergyLevel):
        if energyIncreasePerRechargeTick <= 0:
            raise ValueError('energyIncreasePerRechargeTick must be greater than 0')
        if rechargeTickPeriod <= 0:
            raise ValueError('rechargeTickPeriod must be greater than 0')
        if minEnergyLevel >= quiescentEnergyLevel:
            raise ValueError('maxInterferenceLevel must be less than quiescentInterferenceLevel')
        if energyLevel < minEnergyLevel:
            raise ValueError('energyLevel (%.2f) must be greater than or equal to minEnergyLevel (%.2f)' % (energyLevel, minEnergyLevel))
        if energyLevel > quiescentEnergyLevel:
            raise ValueError('energyLevel (%.2f) must be less than or equal to quiescentEnergyLevel (%.2f)' % (energyLevel, quiescentEnergyLevel))
        self._energyLevel = energyLevel
        self._lastRechargeTickTimestamp = lastRechargeTickTimestamp
        self._energyIncreasePerRechargeTick = energyIncreasePerRechargeTick
        self._rechargeTickPeriod = rechargeTickPeriod
        self._minEnergyLevel = minEnergyLevel
        self._quiescentEnergyLevel = quiescentEnergyLevel

    def __repr__(self):
        return 'CharacterEnergyState(energyLevel=%r, lastRechargeTickTimestamp=%r, energyIncreasePerRechargeTick=%r, rechargeTickPeriod=%r, minEnergyLevel=%r, quiescentEnergyLevel=%r)' % (self._energyLevel,
         self._lastRechargeTickTimestamp,
         self._energyIncreasePerRechargeTick,
         self._rechargeTickPeriod,
         self._minEnergyLevel,
         self._quiescentEnergyLevel)

    def __eq__(self, other):
        if other is None:
            return False
        return self._energyLevel == other._energyLevel and self._lastRechargeTickTimestamp == other._lastRechargeTickTimestamp and self._energyIncreasePerRechargeTick == other._energyIncreasePerRechargeTick and self._rechargeTickPeriod == other._rechargeTickPeriod and self._minEnergyLevel == other._minEnergyLevel and self._quiescentEnergyLevel == other._quiescentEnergyLevel

    @property
    def energyLevel(self):
        return self._energyLevel

    @property
    def lastRechargeTickTimestamp(self):
        return self._lastRechargeTickTimestamp

    @property
    def energyIncreasePerRechargeTick(self):
        return self._energyIncreasePerRechargeTick

    @property
    def rechargeTickPeriod(self):
        return self._rechargeTickPeriod

    @property
    def minEnergyLevel(self):
        return self._minEnergyLevel

    @property
    def quiescentEnergyLevel(self):
        return self._quiescentEnergyLevel

    @property
    def isAtQuiescentLevel(self):
        return self._energyLevel >= self._quiescentEnergyLevel

    @property
    def energyRange(self):
        return self._quiescentEnergyLevel - self._minEnergyLevel

    @property
    def normalisedEnergyLevel(self):
        return (self._energyLevel - self._minEnergyLevel) / self.energyRange

    def CanAffordCost(self, energyCost):
        return self._energyLevel - energyCost >= self._minEnergyLevel


def _GetRechargeResult(characterEnergyState, timestamp):
    timeDelta = timestamp - characterEnergyState.lastRechargeTickTimestamp
    if timeDelta < 0:
        raise ValueError('GetRechargeResult cannot be calculated for negative timeDelta')
    numRechargeTicks = timeDelta / (characterEnergyState.rechargeTickPeriod * SEC)
    energyIncrease = numRechargeTicks * characterEnergyState.energyIncreasePerRechargeTick
    newEnergyLevel = min(characterEnergyState.quiescentEnergyLevel, characterEnergyState.energyLevel + energyIncrease)
    newRechargeTime = characterEnergyState.lastRechargeTickTimestamp + numRechargeTicks * characterEnergyState.rechargeTickPeriod * SEC
    return (newEnergyLevel, newRechargeTime)


def GetNewState(originalState, newEnergyLevel, newRechargeTime):
    return CharacterEnergyState(newEnergyLevel, newRechargeTime, originalState.energyIncreasePerRechargeTick, originalState.rechargeTickPeriod, originalState.minEnergyLevel, originalState.quiescentEnergyLevel)


def CalculateStateAtTime(characterEnergyState, timestamp):
    if characterEnergyState.isAtQuiescentLevel:
        return characterEnergyState
    if timestamp < characterEnergyState.lastRechargeTickTimestamp:
        return characterEnergyState
    newEnergyLevel, newRechargeTickTimestamp = _GetRechargeResult(characterEnergyState, timestamp)
    return GetNewState(characterEnergyState, newEnergyLevel, newRechargeTickTimestamp)


def CalculateStateAfterSpendingEnergyAtTime(characterEnergyState, energyCost, timestamp):
    if energyCost <= 0.0:
        raise ValueError('energyCost must be greater-than 0')
    newEnergyLevel, newRechargeTickTimestamp = _GetRechargeResult(characterEnergyState, timestamp)
    stateAtTime = GetNewState(characterEnergyState, newEnergyLevel, newRechargeTickTimestamp)
    if not stateAtTime.CanAffordCost(energyCost):
        raise InsufficientEnergyError('Not enough energy')
    return GetNewState(characterEnergyState, newEnergyLevel - energyCost, newRechargeTickTimestamp)


class InsufficientEnergyError(StandardError):
    pass
