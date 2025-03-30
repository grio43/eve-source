#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\pythonEffects\sensorFalloff.py
from dogma import const as dogmaConst
from dogma.effects.remoteEffect import RemoteEffect

class BaseSensorFalloffEffect(RemoteEffect):
    MODIFIER_CHANGES = [(dogmaConst.dgmAssPostPercent, dogmaConst.attributeScanGravimetricStrength, dogmaConst.attributeScanGravimetricStrengthPercentInterim),
     (dogmaConst.dgmAssPostPercent, dogmaConst.attributeScanLadarStrength, dogmaConst.attributeScanLadarStrengthPercentInterim),
     (dogmaConst.dgmAssPostPercent, dogmaConst.attributeScanMagnetometricStrength, dogmaConst.attributeScanMagnetometricStrengthPercentInterim),
     (dogmaConst.dgmAssPostPercent, dogmaConst.attributeScanRadarStrength, dogmaConst.attributeScanRadarStrengthPercentInterim),
     (dogmaConst.dgmAssPostPercent, dogmaConst.attributeScanResolution, dogmaConst.attributeScanResolutionBonusInterim),
     (dogmaConst.dgmAssPostPercent, dogmaConst.attributeMaxTargetRange, dogmaConst.attributeMaxTargetRangeBonusInterim)]
