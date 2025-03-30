#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\effects.py
import trinity
BACKGROUND_VARIATION = 'VARIATION'
BACKGROUND_VARIATION_SCANNING = 'SCANNING'
BACKGROUND_VARIATION_REGULAR = 'REGULAR'
BACKGROUND_TINT = 'Tint'

def _FindStructureListIndex(structureList, name):
    for i, keyVal in enumerate(structureList):
        key, _ = keyVal
        if key == name:
            return i


def SetEffectOption(effect, option, value):
    i = _FindStructureListIndex(effect.options, option)
    if i is not None:
        effect.options[i] = (option, value)
    else:
        effect.options.append((option, value))
    effect.RebuildCachedData()


def SetParameterComponentValue(effect, name, value, componentIndex):
    param = effect.parameters.FindByName(name)
    if param is not None:
        l = list(param.value)
        l[componentIndex] = value
        param.value = l
        return True
    i = _FindStructureListIndex(effect.constParameters, name)
    if i is not None:
        l = list(effect.constParameters[i][1])
        l[componentIndex] = value
        effect.constParameters[i] = (name, tuple(l))
        effect.RebuildCachedData()
        return True
    return False


def GetParameterValue(effect, name):
    param = effect.parameters.FindByName(name)
    if param is not None:
        return param.value
    i = _FindStructureListIndex(effect.constParameters, name)
    if i is not None:
        return effect.constParameters[i][1]


def SetParameterValue(effect, name, value):
    param = effect.parameters.FindByName(name)
    if param is not None:
        param.value = value
        return True
    i = _FindStructureListIndex(effect.constParameters, name)
    if i is not None:
        effect.constParameters[i] = (name, value)
        effect.RebuildCachedData()
        return True
    return False


def ApplyEffectOverride(effect, overrideEffect):
    for each in overrideEffect.parameters:
        if not SetParameterValue(effect, each.name, each.value):
            effect.parameters.append(each)

    for name, value in overrideEffect.constParameters:
        if not SetParameterValue(effect, name, value):
            effect.constParameters.append((name, value))

    for each in overrideEffect.resources:
        effect.resources.append(each)

    effect.RebuildCachedData()


def ApplyEffectOverrideFromPath(effect, overridePath):
    override = trinity.Load(overridePath)
    ApplyEffectOverride(effect, override)
