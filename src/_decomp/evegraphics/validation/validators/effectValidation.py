#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\effectValidation.py
import os
import blue
import trinity
from trinity import effects
from evegraphics.validation.commonUtilities import Validate, IsContent, DeleteTopAction
from evegraphics.validation.validationFunctions import ListIsEmpty, ValidateResPath
from evegraphics.validation.resources import GetResource, ResourceType
effectCache = {}

def _MoveConstToParameter(effect, default):

    def inner():
        names = [ x[0] for x in effect.constParameters ]
        for each in names:
            try:
                effects.ConstToParameter(effect, each, effectCache)
            except ValueError:
                pass

        return True

    return ('Move constParameters to parameters', inner, default)


def _MoveParameterToConst(effect, names, default):

    def inner():
        for each in names:
            effects.ParameterToConst(effect, each.name)

        return True

    return ('Move parameters to constParameters', inner, default)


def _DeleteParams(effect, default):

    def inner():
        effects.PruneParameters(effect, effectCache)
        return True

    return ('Delete unused parameters', inner, default)


def _PopulateParams(effect, default):

    def inner():
        effects.PopulateParameters(effect, effectCache)
        return True

    return ('Populate missing parameters', inner, default)


def _DeleteSamplerOverrides(effect, overrides):

    def inner():
        for each in overrides:
            for i in range(len(effect.samplerOverrides)):
                if effect.samplerOverrides[i][0] == each:
                    del effect.samplerOverrides[i]
                    break

        return True

    return ('Delete unused sampler overrides', inner, True)


def _FixSwizzles(binding, old, new):
    if isinstance(old.value, tuple) and isinstance(new.value, float):
        binding.SetBoundAttribute(binding.GetBoundAttribute().split('.')[0])
    elif isinstance(old.value, float) and isinstance(new.value, tuple):
        binding.SetBoundAttribute(binding.GetBoundAttribute() + '.x')
    else:
        raise RuntimeError('could not fix binding')


def _FixBindings(bindings, old, new):
    for binding in bindings:
        if binding.Patch(old, new):
            _FixSwizzles(binding, old, new)


def _FixParameterType(bindings, effect, param, expected):

    def inner():
        new = getattr(trinity, expected.trinity_type)()
        new.name = param.name
        if isinstance(new.value, float):
            new.value = param.value if isinstance(param.value, float) else param.value[0]
        elif isinstance(param.value, float):
            new.value = (param.value,) + expected.constant.default_value[1:]
        elif len(new.value) > len(param.value):
            new.value = param.value + expected.constant.default_value[len(param.value):]
        else:
            new.value = param.value[0:len(new.value)]
        try:
            _FixBindings(bindings, param, new)
        except RuntimeError:
            return False

        effect.parameters.remove(param)
        effect.parameters.append(new)
        return True

    return ('Convert parameter to %s' % expected.trinity_type, inner, True)


@Validate('Tr2Effect')
def ValidEffectResPath(context, effect):
    ValidateResPath(context, effect, 'effectFilePath', '.fx')


@Validate('Tr2Effect', IsContent(IsContent.CONTENT))
def NoConstantParametersInContent(context, effect):
    context.Expect(effect, 'constParameters', ListIsEmpty, actions=(_MoveConstToParameter(effect, True),))


@Validate('Tr2Effect', IsContent(IsContent.BRANCH))
def NoUnboundParametersInBranch(context, effect):
    skip = (trinity.TriVariableParameter, trinity.TriTransformParameter, trinity.Tr2Matrix4Parameter)
    params = [ x for x in effect.parameters if not isinstance(x, skip) and not context.IsBoundAsDestination(x) ]
    if params:
        names = ('"%s"' % x.name for x in params)
        context.Error(effect, 'effect parameters %s need to be moved to constParameters' % ', '.join(names), actions=(_MoveParameterToConst(effect, params, True),))


@Validate('Tr2Effect')
def NoDuplicateParameters(context, effect):
    params = {}
    for name, value in effect.constParameters:
        params.setdefault(name, []).append((name, value))

    for param in effect.parameters:
        params.setdefault(param.name, []).append(param)

    for param in effect.resources:
        params.setdefault(param.name, []).append(param)

    duplicates = []
    for name, params in params.items():
        if len(params) > 1:
            duplicates.append(name)

    if duplicates:
        names = [ '"%s"' % x for x in duplicates ]
        context.Error(effect, 'effect contains duplicate parameters: %s' % ', '.join(names))


@Validate('Tr2Effect')
def NoUnusedParameters(context, effect):
    try:
        unused = effects.GetUnusedParameters(effect, effectCache)
    except (ValueError, OSError, IOError):
        return

    if unused:
        context.Error(effect, 'parameters %s are not used and should be deleted' % ', '.join(unused), actions=(_DeleteParams(effect, True),))


@Validate('Tr2Effect')
def NoMissingParameters(context, effect):
    try:
        missing = effects.GetMissingResources(effect, effectCache)
    except (ValueError, OSError, IOError):
        return

    if missing:
        errorMessage = 'Resources %s are missing from the effect %s (%s) and should be added' % (', '.join(missing), effect.name, effect.effectFilePath)
        context.Error(effect, errorMessage, actions=(_PopulateParams(effect, True),))


@Validate('Tr2Effect')
def ValidParameterTypes(context, effect):
    try:
        params = effects.GetPublicParameters(effect, effectCache)
    except (ValueError, OSError, IOError):
        return

    for each in effect.parameters:
        if each.name not in params:
            continue
        if params[each.name].trinity_type != type(each).__name__:
            if isinstance(each, trinity.TriVariableParameter):
                continue
            if params[each.name].trinity_type == 'Tr2Matrix4Parameter' and isinstance(each, trinity.TriTransformParameter):
                continue
            fixableTypes = ('Tr2FloatParameter', 'Tr2Vector2Parameter', 'Tr2Vector3Parameter', 'Tr2Vector4Parameter')
            if type(each).__name__ in fixableTypes and params[each.name].trinity_type in fixableTypes:
                actions = (_FixParameterType(context.GetBindings(), effect, each, params[each.name]),)
            else:
                actions = ()
            context.Error(each, 'parameter type should be %s' % params[each.name].trinity_type, actions=actions)


@Validate('Tr2Effect')
def ValidResourceTypes(context, effect):
    try:
        params = effects.GetPublicResources(effect, effectCache)
    except (ValueError, OSError, IOError):
        return

    for each in effect.resources:
        if each.name not in params:
            continue
        expected = params[each.name].trinity_type
        existing = type(each).__name__
        if expected != existing:
            if expected == 'TriTextureParameter' and existing in ('EveCloudVolumeTextureParameter', 'Tr2TextureAnimationParameter'):
                pass
            else:
                context.Error(each, 'resource type should be %s' % expected)


@Validate('Tr2Effect')
def ValidSamplerOverrides(context, effect):
    try:
        samplers = effects.GetSamplers(effect, effectCache)
    except (ValueError, OSError, IOError):
        return

    unused = []
    for each in effect.samplerOverrides:
        if each[0] not in samplers:
            unused.append(each[0])

    if unused:
        context.Error(effect, 'sampler overrides %s are not used and need to be deleted' % ', '.join(unused), actions=(_DeleteSamplerOverrides(effect, unused),))


@Validate('Tr2Effect')
def RunShaderParameterValidation(context, effect):
    for each in effect.constParameters:
        try:
            effects.ValidateParameterValue(effect, each[0], each[1], effectCache)
        except AssertionError as e:
            context.Error(effect, 'parameter %s: %s' % (each[0], str(e)))
        except ValueError:
            pass

    for each in effect.parameters:
        if not hasattr(each, 'value') or not hasattr(each, 'name'):
            continue
        try:
            effects.ValidateParameterValue(effect, each.name, each.value, effectCache)
        except AssertionError as e:
            context.Error(effect, 'parameter %s: %s' % (each.name, str(e)))
        except ValueError:
            pass


@Validate('EveChildSocket', IsContent(IsContent.BRANCH))
def ValidateChildSocketExistsInBranch(context, socket):
    context.Error(socket, 'EveChildSockets are not allowed in branch.\n\nEither the file needs to be published or the socket should be removed.', actions=(DeleteTopAction(context, True),))


@Validate('EveChildPlug', IsContent(IsContent.BRANCH))
def ValidateChildPlugExistsInBranch(context, socket):
    context.Error(socket, 'EveChildPlugs are not allowed in branch.\n\nEither the file needs to be published or the socket should be removed.', actions=(DeleteTopAction(context, True),))


@Validate('EveChildRef', IsContent(IsContent.BRANCH))
def ValidateChildRefExistsInBranch(context, ref):
    if len(context.GetStack()) > 1:
        parent = context.GetStack()[-2]
        name = type(parent).__name__
        if name.startswith(('EveChildProcedural', 'EveProcedural')):
            return
    context.Error(ref, 'EveChildRefs are not allowed in branch.\n\nEither the file needs to be published or the child should be removed.', actions=(DeleteTopAction(context, True),))


@Validate('EveChildSocket')
def ChildSocketPlugPathExists(context, childSocket):
    ValidateResPath(context, childSocket, 'resPath', ('.red',), interfaces=('EveChildPlug',))


@Validate('EveChildRef')
def ChildRefPathExists(context, childRef):
    ValidateResPath(context, childRef, 'resPath', ('.red',), interfaces=('IEveSpaceObjectChild',))
    if childRef.child:
        key = ('childRef', childRef.resPath)
        if key in context.cache:
            context.SkipObject(childRef.child)
        else:
            context.cache[key] = True


def RemoveSocketParameter(socket, socketParameter, default):

    def inner():
        socket.parameters.remove(socketParameter)
        return True

    name = getattr(socketParameter, 'name', '') or type(socketParameter).__name__
    return ('Remove %s parameter' % name, inner, default)


@Validate('EveChildSocket', IsContent(IsContent.CONTENT))
def ValidateChildSocketParameterUsage(context, socket):
    for socketParameter in socket.parameters:
        if not socketParameter.Used():
            context.Error(socketParameter, "EveSocketParameter isn't used and should be removed.", actions=(RemoveSocketParameter(socket, socketParameter, True),))


@Validate('EveChildMesh(childMesh)/.../Tr2MeshArea(meshArea)/.../Tr2Effect(effect)', IsContent(IsContent.CONTENT))
def ValidUbershaderUse(context, childMesh, meshArea, effect):
    if effect.effectFilePath != 'res:/Graphics/Effect/Managed/Space/SpecialFX/Ubershader.fx':
        return
    whiteTga = 'res:/texture/global/white.tga'
    for resource in effect.resources:
        if resource.name == 'DiffuseMap1':
            continue
        if resource.resourcePath == whiteTga and 'DiffuseMap' in resource.name:
            context.Error(effect, 'Effect is using a white diffuse map, the effect should use less diffuse maps %s-%s' % (childMesh.name, meshArea.name))


@Validate('Tr2Mesh(mesh)/.../Tr2Effect(effect)', IsContent(IsContent.CONTENT))
def AvoidUnpackedShadersForSOFHullGeometry(context, mesh, effect):
    import glob
    geoPath = mesh.geometryResPath.lower().replace('\\', '/')
    geoDir = os.path.dirname(blue.paths.ResolvePath(geoPath))
    sofhullPaths = glob.glob(os.path.join(geoDir, 'sofhull_*.red'))
    usedInSofHull = False
    for each in sofhullPaths:
        sofHull = trinity.Load(each)
        if sofHull and geoPath == sofHull.geometryResFilePath.lower().replace('\\', '/'):
            usedInSofHull = True
            break

    geoBasename = os.path.basename(geoPath)
    if not geoBasename.lower().endswith('_unpackedts.gr2') and usedInSofHull and effect.effectFilePath:
        key = ('is_using_compressed_tangents', blue.paths.ResolvePath(effect.effectFilePath).lower())
        if key in context.cache:
            compressedTangents = context.cache[key]
        else:
            compressedTangents = os.path.basename(effect.effectFilePath).lower().startswith('unpacked_') or trinity.effects.effectinfo.is_using_compressed_tangents(blue.paths.ResolvePath(effect.effectFilePath), trinity.effects.GetEffectFilter(effect))
        if not compressedTangents:
            effectBasename = os.path.basename(effect.effectFilePath)
            suggestedName = geoBasename.replace('.gr2', '_unpackedts.gr2')
            message = 'Mesh %s is used with effect %s, but is also referenced in a sofhull. Please either change the effect to one that requires compressed tangents or duplicate and rename the mesh to %s.' % (geoBasename, effectBasename, suggestedName)
            context.Error(effect, message)


@Validate('Tr2Mesh(mesh)/.../Tr2Effect(effect)')
def AvoidPackedShadersWithSharedGeo(context, mesh, effect):
    geoPath = mesh.geometryResPath.lower().replace('\\', '/')
    geoIsShared = any((x in geoPath for x in ['/graphics/', '/global/', '/shared/']))
    geoBasename = os.path.basename(geoPath)
    if not geoBasename.lower().endswith('_packedts.gr2') and geoIsShared and effect.effectFilePath:
        key = ('is_using_compressed_tangents', blue.paths.ResolvePath(effect.effectFilePath).lower())
        if key in context.cache:
            compressedTangents = context.cache[key]
        else:
            compressedTangents = os.path.basename(effect.effectFilePath).lower().startswith('unpacked_') or trinity.effects.effectinfo.is_using_compressed_tangents(blue.paths.ResolvePath(effect.effectFilePath), trinity.effects.GetEffectFilter(effect))
            context.cache[key] = compressedTangents
        if compressedTangents:
            effectBasename = os.path.basename(effect.effectFilePath)
            suggestedName = geoBasename.replace('.gr2', '_packedts.gr2')
            message = 'Shared mesh "%s" used with effect "%s" which requires compressed tangents. Either use a different effect, make a non-shared version of "%s" or rename it to %s' % (geoBasename,
             effectBasename,
             geoBasename,
             suggestedName)
            context.Error(effect, message)


@Validate('EveChildMesh(childMesh)/.../Tr2Mesh(mesh)')
def ValidateShaderDiscrepancies(context, childMesh, mesh):

    def getarealist(currentAreas):
        areas = []
        for currentArea in currentAreas:
            for area in currentArea:
                areas.append(True if '/v5/' in area.effect.effectFilePath.lower() else False)

        return areas

    areaList = getarealist([mesh.additiveAreas, mesh.opaqueAreas, mesh.transparentAreas])
    if areaList != [] and any(areaList) != all(areaList):
        message = 'Mesh area "%s" has two areas that have incompatible shader areas. \nV5 areas and non-V5 areas will create errors on export. \nMake sure that all the areas of the mesh use the same type of effect.\n' % childMesh.name + '\n Area List: ' + str(areaList)
        context.Error(mesh, message)


@Validate('Tr2TextureAnimationParameter')
def TextureAnimationParameterMustHaveAnimation(context, param):
    if not param.animation:
        context.Error(param, 'Parameter should have animation object assigned' % param.name)


@Validate('Tr2TextureAnimationParameter')
def TextureAnimationParameterChannelIsValid(context, param):
    if not param.animation:
        return
    res = GetResource(context, param.animation.resPath, ResourceType.TEXTURE_ANIMATION)
    if res:
        for each in res.grids():
            if param.channel == each.name:
                return

    context.Error(param, 'channel "%s" is not present in VTA file' % param.channel)


@Validate('Tr2TextureAnimation')
def TextureAnimationPathIsValid(context, animation):
    ValidateResPath(context, animation, 'resPath', '.vta')


@Validate('Tr2TextureAnimation')
def TextureAnimationFpsIsValid(context, animation):
    if animation.fps < 0:
        context.Error(animation, 'FPS cannot be less than zero')
    if animation.fps > 60:
        context.Error(animation, 'FPS for animation is too high, chances are the client will not be able to maintain it')


@Validate('EveChildCloud2(cloud)/.../Tr2TextureAnimationParameter(param)')
def TextureAnimationFpsNotTooHigh(context, cloud, param):
    if param.animation != cloud.animation:
        context.Error(param, 'animation for the parameter is different from the owner cloud animation. Copy/paste error?')
