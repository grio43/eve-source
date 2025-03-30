#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\pythonEffects\remoteTrackingComputer.py
from dogma.effects.remoteEffect import RemoteEffect
from dogma import const as dogmaConst
import inventorycommon.const as invConst

class BaseRemoteTrackingComputer(RemoteEffect):
    SKILL_MODIFIER_CHANGES_FOR_LOCATION = [(dogmaConst.dgmAssPostPercent,
      invConst.typeGunnery,
      dogmaConst.attributeMaxRange,
      dogmaConst.attributeMaxRangeBonus), (dogmaConst.dgmAssPostPercent,
      invConst.typeGunnery,
      dogmaConst.attributeFalloff,
      dogmaConst.attributeFalloffBonus), (dogmaConst.dgmAssPostPercent,
      invConst.typeGunnery,
      dogmaConst.attributeTrackingSpeed,
      dogmaConst.attributeTrackingSpeedBonus)]
