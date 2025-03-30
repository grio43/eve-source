#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\client\skyBoxEffects.py
import skyBoxEffectsLoader
from fsdBuiltData.common.base import BuiltDataLoader

class SkyBoxEffects(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/skyBoxEffects.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/skyBoxEffects.fsdbinary'
    __loader__ = skyBoxEffectsLoader


def GetSkyBoxEffects():
    return SkyBoxEffects.GetData()


def GetSkyBoxEffect(sky_box_effect_id):
    return GetSkyBoxEffects().get(sky_box_effect_id, None)


def GetAttribute(sky_box_effect_id, attr, default = None):
    return getattr(GetSkyBoxEffect(sky_box_effect_id), attr, default)


def _GetSource(sky_box_effect_id):
    source = GetAttribute(sky_box_effect_id, 'source')
    if source is None:
        raise RuntimeError('SkyBoxEffects: No Source is defined for %s' % sky_box_effect_id)
    return source


def GetSkyBoxEffectWorldPosition(sky_box_effect_id):
    source = _GetSource(sky_box_effect_id)
    return getattr(source, 'worldPosition', None)


def GetSkyBoxEffectSourceSolarSystem(sky_box_effect_id):
    source = _GetSource(sky_box_effect_id)
    return getattr(source, 'solarSystemID', None)


def _GetSkyBoxEffectSource(sky_box_effect_id):
    return GetAttribute(sky_box_effect_id, 'source')


def GetSkyBoxEffectName(sky_box_effect_id):
    return GetAttribute(sky_box_effect_id, 'name')


def GetSkyBoxEffectPath(sky_box_effect_id):
    return GetAttribute(sky_box_effect_id, 'path')


def GetSkyBoxEffectFarScale(sky_box_effect_id):
    return GetAttribute(sky_box_effect_id, 'far').scale


def GetSkyBoxEffectFarDistInLightYears(sky_box_effect_id):
    return GetAttribute(sky_box_effect_id, 'far').distInLightYears


def GetSkyBoxEffectNearScale(sky_box_effect_id):
    return GetAttribute(sky_box_effect_id, 'near').scale


def GetSkyBoxEffectNearDistInLightYears(sky_box_effect_id):
    return GetAttribute(sky_box_effect_id, 'near').distInLightYears
