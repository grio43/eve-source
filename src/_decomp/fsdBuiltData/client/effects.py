#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\client\effects.py
import effectsLoader
from fsdBuiltData.common.base import BuiltDataLoader

class Effects(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/effects.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/effects.fsdbinary'
    __loader__ = effectsLoader


def GetEffectData():
    return Effects.GetData()


def GetEffectGuids():
    return Effects.GetData().keys()


def IsValidEffect(effectGuid):
    return effectGuid in GetEffectData()


def GetEffect(effectGuid):
    return GetEffectData().get(effectGuid, None)


def GetEffectAttribute(effectGuid, attributeName, default = None):
    if isinstance(effectGuid, str):
        effect = GetEffect(effectGuid)
    else:
        effect = effectGuid
    return getattr(effect, attributeName, None) or default


def GetEffectType(effectGuid):
    return GetEffectAttribute(effectGuid, 'type')


def GetEffectGraphicID(effectGuid):
    return GetEffectAttribute(effectGuid, 'graphicID')


def GetEffectSourceDamage(effectGuid):
    return GetEffectAttribute(effectGuid, 'sourceDamage')


def GetEffectTargetDamage(effectGuid):
    return GetEffectAttribute(effectGuid, 'targetDamage')


def GetSourceDamageDuration(effectGuid, default = 0):
    damage = GetEffectSourceDamage(effectGuid)
    return getattr(damage, 'duration', default)


def GetSourceDamageDelay(effectGuid, default = 0):
    damage = GetEffectSourceDamage(effectGuid)
    return getattr(damage, 'delay', default)


def GetSourceDamageSize(effectGuid, default = 0):
    damage = GetEffectSourceDamage(effectGuid)
    return getattr(damage, 'size', default)


def GetTargetDamageDuration(effectGuid, default = 0):
    damage = GetEffectTargetDamage(effectGuid)
    return getattr(damage, 'duration', default)


def GetTargetDamageDelay(effectGuid, default = 0):
    damage = GetEffectTargetDamage(effectGuid)
    return getattr(damage, 'delay', default)


def GetTargetDamageSize(effectGuid, default = 0):
    damage = GetEffectTargetDamage(effectGuid)
    return getattr(damage, 'size', default)
