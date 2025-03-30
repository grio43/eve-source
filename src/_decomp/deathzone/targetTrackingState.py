#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\deathzone\targetTrackingState.py
from uthread import SEC

class TargetTrackingState(object):

    def __init__(self, trackedSinceTimestamp, damageTickPeriod, safetyDuration, peakHullDamageFractionPerTick, hullDamageFractionIncreasePerTick):
        if trackedSinceTimestamp is None:
            raise ValueError('trackedSinceTimestamp cannot be None')
        if damageTickPeriod is None or damageTickPeriod <= 0:
            raise ValueError('damageTickPeriod must be positive number')
        if safetyDuration is None or safetyDuration <= 0:
            raise ValueError('safetyDuration must be positive number')
        if peakHullDamageFractionPerTick is None or peakHullDamageFractionPerTick <= 0:
            raise ValueError('peakHullDamageFractionPerTick must be positive number')
        if hullDamageFractionIncreasePerTick is None or hullDamageFractionIncreasePerTick <= 0:
            raise ValueError('hullDamageFractionIncreasePerTick must be positive number')
        self._trackedSinceTimestamp = trackedSinceTimestamp
        self._damageTickPeriod = damageTickPeriod
        self._safetyDuration = safetyDuration
        self._peakHullDamageFractionPerTick = peakHullDamageFractionPerTick
        self._hullDamageFractionIncreasePerTick = hullDamageFractionIncreasePerTick

    def __repr__(self):
        return 'TargetTrackingState(trackedSinceTimestamp=%r, safetyDuration=%r)' % (self._trackedSinceTimestamp, self._safetyDuration)

    def __eq__(self, other):
        if isinstance(other, TargetTrackingState):
            return self._trackedSinceTimestamp == other._trackedSinceTimestamp and self._damageTickPeriod == other._damageTickPeriod and self._safetyDuration == other._safetyDuration and self._peakHullDamageFractionPerTick == other._peakHullDamageFractionPerTick and self._hullDamageFractionIncreasePerTick == other._hullDamageFractionIncreasePerTick
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def trackedSinceTimestamp(self):
        return self._trackedSinceTimestamp

    @property
    def damageTickPeriod(self):
        return self._damageTickPeriod

    @property
    def safetyDuration(self):
        return self._safetyDuration

    @property
    def peakHullDamageFractionPerTick(self):
        return self._peakHullDamageFractionPerTick

    @property
    def hullDamageFractionIncreasePerTick(self):
        return self._hullDamageFractionIncreasePerTick

    def IsDamageActive(self, timestamp):
        return timestamp > self._trackedSinceTimestamp + self._safetyDuration * SEC

    def GetSafetyTimeRemaining(self, timestamp):
        return max(0, (self._trackedSinceTimestamp - timestamp) / SEC + self._safetyDuration)

    def GetHullDamageFractionPerTick(self, timestamp):
        if not self.IsDamageActive(timestamp):
            return 0.0
        timeSinceDamageStart = timestamp - (self._trackedSinceTimestamp + self._safetyDuration * SEC)
        ticksSinceDamageStart = timeSinceDamageStart / (self._damageTickPeriod * SEC)
        tickDamage = ticksSinceDamageStart * self._hullDamageFractionIncreasePerTick
        return min(tickDamage, self._peakHullDamageFractionPerTick)
