#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dotWeapons\common\dotApplication.py
import gametime
import mathext
from dotWeapons.common.dotAppInfo import DotApplicationInfo
from dotWeapons.common.dotConst import DOT_IDLE
from dotWeapons.common.dotUtil import GetEffectiveDamage
from utillib import KeyVal

class DotApplication(object):

    def __init__(self, addedTimestamp, missileInfo, targetID):
        self._id = id(self)
        self._missileInfo = missileInfo
        self._addedTimestamp = addedTimestamp
        self._maxHpPercentage = mathext.clamp(missileInfo.maxHPPercentagePerTick, 0, 100)
        self._maxHPNormalizedRatio = mathext.clamp(self._maxHpPercentage / 100.0, 0, 1)
        self._expiryTime = missileInfo.duration + addedTimestamp
        self._activityState = DOT_IDLE
        self._targetID = targetID

    @property
    def id(self):
        return self._id

    @property
    def sourceShipItem(self):
        return self._missileInfo.sourceShipItem

    @property
    def sourceTypeID(self):
        return self.sourceShipItem.typeID

    @property
    def weaponItem(self):
        return self._missileInfo.weaponItem

    @property
    def weaponTypeID(self):
        return self.weaponItem.typeID

    @property
    def charID(self):
        return self._missileInfo.charID

    @property
    def maxHPNormalizedRatio(self):
        return self._maxHPNormalizedRatio

    @property
    def maxDamage(self):
        return self._missileInfo.maxDamagePerTick

    @property
    def expiryTime(self):
        return self._expiryTime

    @property
    def isExpired(self):
        return self._expiryTime < gametime.GetSimTime()

    @property
    def activityState(self):
        return self._activityState

    @activityState.setter
    def activityState(self, value):
        self._activityState = value

    def GetValues(self):
        return KeyVal(duration=self._missileInfo.duration, addedTimestamp=self._addedTimestamp, expiryTime=self._expiryTime, maxDamage=self.maxDamage, maxHpPercentage=self._maxHpPercentage)

    def GetBasicInfoForClientUpdate(self):
        return DotApplicationInfo(attackerID=self.charID, weaponTypeID=self.weaponTypeID, expiryTime=self.expiryTime, maxDamage=self.maxDamage, maxHPNormalizedRatio=self.maxHPNormalizedRatio, activityState=self.activityState, targetID=self._targetID)

    def GetEffectiveDamage(self, totalHP):
        return GetEffectiveDamage(self.maxDamage, self.maxHPNormalizedRatio, totalHP)

    def __repr__(self):
        return '<DotApplication %s>, %s' % (self.__dict__, id(self))
