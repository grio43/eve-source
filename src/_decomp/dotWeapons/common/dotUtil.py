#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dotWeapons\common\dotUtil.py


def GetEffectiveDamage(maxDamage, maxHPNormalizedRatio, totalHp):
    effectiveDamage = maxHPNormalizedRatio * totalHp
    effectiveDamage = int(min(effectiveDamage, maxDamage))
    return effectiveDamage
