#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\client\travelEffects.py
import travelEffectsLoader
from fsdBuiltData.common.base import BuiltDataLoader

class TravelEffects(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/travelEffects.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/travelEffects.fsdbinary'
    __loader__ = travelEffectsLoader


def GetTravelEffectData():
    return TravelEffects.GetData()


def GetTravelEffectsGuids():
    return TravelEffects.GetData().keys()


def IsTravelEffect(effectGuid):
    return effectGuid in GetTravelEffectsGuids()


def GetTravelEffect(effectGuid):
    return GetTravelEffectData().get(effectGuid, None)


def GetTravelEffectAttribute(effectGuid, attributeName, default = None):
    if isinstance(effectGuid, str):
        effect = GetTravelEffect(effectGuid)
    else:
        effect = effectGuid
    return getattr(effect, attributeName, None) or default


def GetEffect(effectGuid):
    return GetTravelEffectAttribute(effectGuid, 'effect')


def GetMultiEffect(effectGuid):
    return GetTravelEffectAttribute(effectGuid, 'multiEffect')


def GetTransitionScene(effectGuid):
    return GetTravelEffectAttribute(effectGuid, 'transitionScene')


def GetOriginEffect(effectGuid):
    return GetTravelEffectAttribute(effectGuid, 'originEffect')


def GetHidingEffect(effectGuid):
    return GetTravelEffectAttribute(effectGuid, 'hidingEffect')


def GetHidingEffectPath(effectGuid):
    effect = GetHidingEffect(effectGuid)
    return getattr(effect, 'path', None)


def GetShipHideDelay(effectGuid):
    effect = GetHidingEffect(effectGuid)
    return getattr(effect, 'shipHideDelay', None)


def GetHidingEffectDuration(effectGuid):
    effect = GetHidingEffect(effectGuid)
    duration = getattr(effect, 'effectDuration', 0)
    if duration is None:
        return 0
    return duration


def IsJumpWithinSystem(effectGuid):
    return GetTravelEffectAttribute(effectGuid, 'type') == 'WithinSystem'
