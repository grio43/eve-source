#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\pythonEffects\remoteTargetPaintFalloff.py
from dogma.effects import Effect
from dogma import const as dogmaconst

class BaseRemoteTargetPaintFalloff(Effect):
    MODIFIER_CHANGES = [(dogmaconst.dgmAssPostPercent, dogmaconst.attributeSignatureRadius, dogmaconst.attributeSignatureRadiusBonusInterim)]
