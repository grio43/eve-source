#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\pythonEffects\remoteWebifierFalloff.py
from dogma.effects import Effect
from dogma import const as dogmaconst

class BaseRemoteWebifierFalloff(Effect):
    MODIFIER_CHANGES = [(dogmaconst.dgmAssPostPercent, dogmaconst.attributeMaxVelocity, dogmaconst.attributeSpeedFactorInterim)]
