#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dotWeapons\common\dotMissileInfo.py


class DotMissileInfo(object):

    def __init__(self, duration, maxDamagePerTick, maxHPPercentagePerTick, sourceShipItem, weaponItem, charID):
        self._duration = duration
        self._maxDamagePerTick = maxDamagePerTick
        self._maxHPPercentagePerTick = maxHPPercentagePerTick
        self._sourceShipItem = sourceShipItem
        self._weaponItem = weaponItem
        self._charID = charID

    @property
    def duration(self):
        return self._duration

    @property
    def maxDamagePerTick(self):
        return self._maxDamagePerTick

    @property
    def maxHPPercentagePerTick(self):
        return self._maxHPPercentagePerTick

    @property
    def sourceShipItem(self):
        return self._sourceShipItem

    @property
    def weaponItem(self):
        return self._weaponItem

    @property
    def charID(self):
        return self._charID

    def __repr__(self):
        return '<DotMissileInfo %s>, %s' % (self.__dict__, id(self))
