#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\effects.py
import blue
import trinity
from shadercompiler import effectinfo

def _GetMergedParameters(resPath, options, cache):
    options = {name:value for name, value in options}
    frozen = tuple(options.items())

    def ShaderFilter(platform, sm, permutation):
        for option, value in permutation:
            if option.type != effectinfo.Permutation.STATIC:
                continue
            if option.name in options:
                if options[option.name] != value:
                    return False
            elif option.options[option.default_index] != value:
                return False

        return True

    resPath = resPath.lower().replace('\\', '/')
    if cache and (resPath, frozen) in cache:
        return (dict(cache[resPath, frozen][0]), dict(cache[resPath, frozen][1]), dict(cache[resPath, frozen][2]))
    path = blue.paths.ResolvePath(resPath)
    try:
        result = effectinfo.get_merged_parameters(path, shader_filter=ShaderFilter)
    except IOError:
        result = ({}, {}, {})

    if cache is not None:
        cache[resPath, frozen] = result
    return (dict(result[0]), dict(result[1]), dict(result[2]))


def GetMergedParameters(resPath, options = (), cache = None):
    return _GetMergedParameters(resPath, options, cache)


def GetPublicParameters(effect, cache = None):
    path = blue.paths.ResolvePath(effect.effectFilePath)
    params, resources, _ = _GetMergedParameters(path, effect.options, cache)
    return {name:param for name, param in params.items() if param.annotation.get('SasUiVisible', False)}


def GetPublicResources(effect, cache = None):
    path = blue.paths.ResolvePath(effect.effectFilePath)
    params, resources, _ = _GetMergedParameters(path, effect.options, cache)
    return {name:param for name, param in resources.items() if param.annotation.get('SasUiVisible', False)}


def GetSamplers(effect, cache = None):
    path = blue.paths.ResolvePath(effect.effectFilePath)
    return _GetMergedParameters(path, effect.options, cache)[2]


def PopulateParameters(effect, cache = None):
    path = blue.paths.ResolvePath(effect.effectFilePath)
    params, resources, _ = _GetMergedParameters(path, effect.options, cache)
    existing = set()
    for name, _ in effect.constParameters:
        existing.add(name)

    for param in effect.parameters:
        existing.add(param.name)

    for param in effect.resources:
        existing.add(param.name)

    for name, param in params.items():
        if name in existing:
            continue
        if not param.annotation.get('SasUiVisible', False):
            continue
        if param.trinity_type is None:
            if param.constant.type == 2 and param.annotation.get('BindlessHandleType', None) is not None:
                new = trinity.TriTextureParameter()
                new.name = name
                effect.resources.append(new)
        else:
            new = getattr(trinity, param.trinity_type)()
            new.name = name
            if param.constant.default_value is not None:
                new.value = param.constant.default_value
            effect.parameters.append(new)

    for name, param in resources.items():
        if name in existing:
            continue
        new = getattr(trinity, param.trinity_type)()
        new.name = name
        effect.resources.append(new)


def PruneParameters(effect, cache = None):
    path = blue.paths.ResolvePath(effect.effectFilePath)
    params, resources, _ = _GetMergedParameters(path, effect.options, cache)
    params.update(resources)
    params = set([ name for name, param in params.items() if param.annotation.get('SasUiVisible', False) ])
    delete = []
    for i, param in enumerate(effect.constParameters):
        if param[0] not in params:
            delete.append(i)

    for idx in reversed(delete):
        del effect.constParameters[idx]

    delete = []
    for i, param in enumerate(effect.parameters):
        if param.name not in params:
            delete.append(i)

    for idx in reversed(delete):
        del effect.parameters[idx]

    delete = []
    for i, param in enumerate(effect.resources):
        if param.name not in params:
            delete.append(i)

    for idx in reversed(delete):
        del effect.resources[idx]


def GetUnusedParameters(effect, cache = None):
    path = blue.paths.ResolvePath(effect.effectFilePath)
    params, resources, _ = _GetMergedParameters(path, effect.options, cache)
    params.update(resources)
    result = []
    for name, _ in effect.constParameters:
        if name not in params:
            result.append(name)

    for param in effect.parameters:
        if param.name not in params:
            result.append(param.name)

    for param in effect.resources:
        if param.name not in params:
            result.append(param.name)

    return result


def GetMissingResources(effect, cache = None):
    path = blue.paths.ResolvePath(effect.effectFilePath)
    _, resources, __ = _GetMergedParameters(path, effect.options, cache)
    existing = {p.name for p in effect.resources}
    return list(set(resources).difference(existing))


def IsParameterUsed(effect, name, cache = None):
    path = blue.paths.ResolvePath(effect.effectFilePath)
    params, resources, _ = _GetMergedParameters(path, effect.options, cache)
    return name in params or name in resources


def ConstToParameter(effect, name, cache = None):
    path = blue.paths.ResolvePath(effect.effectFilePath)
    params, _, _ = _GetMergedParameters(path, effect.options, cache)
    if name not in params:
        raise ValueError('parameter "%s" is not used by the effect' % name)
    for i, p in enumerate(effect.constParameters):
        if p[0] == name:
            param = getattr(trinity, params[name].trinity_type)()
            param.name = p[0]
            if isinstance(param.value, float):
                param.value = p[1][0]
            else:
                param.value = p[1][:len(param.value)]
            effect.parameters.append(param)
            del effect.constParameters[i]
            return

    raise ValueError('parameter "%s" is not found in constParameters' % name)


def ParameterToConst(effect, name):
    p = effect.parameters.FindByName(name)
    if not p:
        raise ValueError('parameter "%s" is not found in parameters' % name)
    if not isinstance(p.value, (float, tuple)):
        raise ValueError("don't know how to handle parameter type %s" % type(p))
    if isinstance(p.value, tuple):
        if len(p.value) > 4 or not isinstance(p.value[0], float):
            raise ValueError("don't know how to handle parameter type %s" % type(p))
        v = p.value + (0.0,) * (4 - len(p.value))
    else:
        v = (p.value,
         0.0,
         0.0,
         0.0)
    effect.constParameters.append((name, v))
    effect.parameters.remove(p)


class _VectorWrapper(object):

    def __init__(self, value):
        self._value = value

    def __getitem__(self, item):
        return self._value[item]

    def __getattr__(self, item):
        result = []
        for each in item:
            if each in ('r', 'x'):
                result.append(self._value[0])
            elif each in ('g', 'y'):
                result.append(self._value[1])
            elif each in ('b', 'z'):
                result.append(self._value[2])
            elif each in ('a', 'w'):
                result.append(self._value[3])
            else:
                raise AttributeError(item)

        if len(result) == 1:
            return result[0]
        return tuple(result)


class _MatrixWrapper(object):

    def __init__(self, value):
        self._value = value

    def __getitem__(self, item):
        return self._value[item]

    def __getattr__(self, item):
        if len(item) == 3 and item[0] == '_' and item[1] in '1234' and item[3] in '1234':
            row = ord(item[1]) - ord('1')
            col = ord(item[2]) - ord('1')
            return self._value[row][col]
        raise AttributeError(item)


def _WrapParameterValue(value, param):
    if param.constant.elements > 1:
        return []
    elif param.constant.dimension == 16:
        return _MatrixWrapper(value)
    elif param.constant.dimension == 1:
        if isinstance(value, tuple):
            return value[0]
        return value
    else:
        return _VectorWrapper(value)


def _WrapEffectParameters(effect, params):
    p = {}
    for n, v in effect.constParameters:
        if n in params:
            p[n] = _WrapParameterValue(v, params[n])

    for each in effect.parameters:
        if each.name in params:
            p[each.name] = _WrapParameterValue(each.value, params[each.name])

    return p


def EvaluateExpression(effect, expression, cache = None):
    path = blue.paths.ResolvePath(effect.effectFilePath)
    params, resources, _ = _GetMergedParameters(path, effect.options, cache)
    p = _WrapEffectParameters(effect, params)
    return eval(expression, {}, p)


def ValidateParameterValue(effect, name, value, cache = None):
    path = blue.paths.ResolvePath(effect.effectFilePath)
    params, resources, _ = _GetMergedParameters(path, effect.options, cache)
    if name not in params:
        raise ValueError('parameter %s not found in the effect resource' % name)
    validation = params[name].annotation.get('Validation', '')
    if not validation:
        return
    p = _WrapEffectParameters(effect, params)
    p['self'] = _WrapParameterValue(value, params[name])
    if not eval(validation, {}, p):
        message = params[name].annotation.get('ValidationMessage', 'invalid value')
        raise AssertionError(params[name].annotation.get('ValidationMessage', message))


def GetEffectFilter(effect):
    options = {name:value for name, value in effect.options}

    def ShaderFilter(platform, sm, permutation):
        for option, value in permutation:
            if option.type != effectinfo.Permutation.STATIC:
                continue
            if option.name in options:
                if options[option.name] != value:
                    return False
            elif option.options[option.default_index] != value:
                return False

        return True

    return ShaderFilter


def GetVertexShaderInputs(effect, cache = None):
    inputs = set()
    options = {name:value for name, value in effect.options}
    frozen = tuple(options.items())
    resPath = effect.effectFilePath.lower().replace('\\', '/')
    if cache is not None and (resPath, frozen, 'GetVertexShaderInputs') in cache:
        return set(cache[resPath, frozen, 'GetVertexShaderInputs'])

    def inner(shader):
        for option, value in shader.options:
            if option.type != effectinfo.Permutation.STATIC:
                continue
            if option.name in options:
                if options[option.name] != value:
                    return
            elif option.options[option.default_index] != value:
                return

        for technique in shader.techniques:
            for each in technique.passes:
                if effectinfo.Stages.VERTEX_SHADER in each.stages:
                    vs = each.stages[effectinfo.Stages.VERTEX_SHADER]
                    inputs.update([ (x.usage, x.usage_index) for x in vs.inputs if x.used_mask ])

    effectinfo.apply_to_shaders(blue.paths.ResolvePath(effect.effectFilePath), inner, GetEffectFilter(effect))
    if cache is not None:
        cache[resPath, frozen, 'GetVertexShaderInputs'] = inputs
    return inputs


def PopulateDefaultOptions(effect):
    path = blue.paths.ResolvePath(effect.effectFilePath)
    for platform in effectinfo.PLATFORM_NAMES.iterkeys():
        for sm in effectinfo.SHADER_MODEL_NAMES.iterkeys():
            try:
                compiled = effectinfo.paths.get_compiled_path(path, sm, platform)
            except ValueError:
                continue

            try:
                info = effectinfo.EffectInfo(compiled)
            except IOError:
                continue

            for option in info.permutations:
                if option.name in [ x[0] for x in effect.options ]:
                    continue
                effect.options.append((option.name, option.options[option.default_index]))
