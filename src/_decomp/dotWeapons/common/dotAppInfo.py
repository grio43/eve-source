#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dotWeapons\common\dotAppInfo.py
from carbon.common.script.util.mathCommon import FloatCloseEnough
from dotWeapons.common.dotUtil import GetEffectiveDamage

class DotApplicationInfo(object):

    def __init__(self, *args, **kwargs):
        self._attackerID = kwargs.get('attackerID', None)
        self._weaponTypeID = kwargs.get('weaponTypeID', None)
        self._expiryTime = kwargs.get('expiryTime', None)
        self._maxDamage = kwargs.get('maxDamage', None)
        self._maxHPNormalizedRatio = kwargs.get('maxHPNormalizedRatio', None)
        self._activityState = kwargs.get('activityState', None)
        self._targetID = kwargs.get('targetID', None)

    @property
    def attackerID(self):
        return self._attackerID

    @property
    def targetID(self):
        return self._targetID

    @property
    def weaponTypeID(self):
        return self._weaponTypeID

    @property
    def expiryTime(self):
        return self._expiryTime

    @property
    def maxDamage(self):
        return self._maxDamage

    @property
    def maxHPNormalizedRatio(self):
        return self._maxHPNormalizedRatio

    @property
    def activityState(self):
        return self._activityState

    def GetEffectiveDamage(self, totalHP):
        return GetEffectiveDamage(self.maxDamage, self.maxHPNormalizedRatio, totalHP)

    def IsMaskedBy(self, otherDotAppInfo, totalHp):
        myDmg = self.GetEffectiveDamage(totalHp)
        otherDmg = otherDotAppInfo.GetEffectiveDamage(totalHp)
        if otherDmg >= myDmg and otherDotAppInfo.expiryTime >= self.expiryTime:
            return True
        return False

    def __repr__(self):
        return '<DotApplicationInfo %s>, %s' % (self.__dict__, id(self))
