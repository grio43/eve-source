#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\meshValidation.py
import os
import blue
import trinity
from trinity import effects
from evegraphics.validation.commonUtilities import Validate
from evegraphics.validation.validationFunctions import ValidateResPath
from evegraphics.validation import resources
from effectValidation import effectCache
MAX_BONES_PER_MESH = 58

def _GetGranny(context, resPath):
    return resources.GetResource(context, resPath, resources.ResourceType.GRANNY)


@Validate('Tr2Mesh')
def ValidResPath(context, mesh):
    ValidateResPath(context, mesh, 'geometryResPath', extensions=('.gr2',))


@Validate('Tr2InstancedMesh')
def ValidInstanceResPath(context, mesh):
    if mesh.instanceGeometryResPath:
        ValidateResPath(context, mesh, 'instanceGeometryResPath', extensions=('.gr2',))
    elif not mesh.instanceGeometryResource:
        context.Error(mesh, 'instanced mesh has no instance geometry resource')


@Validate('Tr2Mesh')
def ValidMeshIndex(context, mesh):
    granny = _GetGranny(context, mesh.geometryResPath)
    if not granny:
        return
    if mesh.meshIndex < 0 or mesh.meshIndex >= len(granny.meshes):
        context.Error(mesh, 'mesh index is out of range (should be between 0 and %s)' % (len(granny.meshes) - 1))


def _DeleteObject(context, default):
    obj = context.GetTop()
    root = context.GetStack()[0]

    def inner():
        for route in blue.FindRoute(root, obj):
            last = route[-1]
            if last[1] == 0:
                setattr(last[0], last[2], None)
            else:
                last[0].remove(obj)

        return True

    return ('Delete %s' % (getattr(obj, 'name', '') or type(obj).__name__), inner, default)


@Validate('Tr2Mesh')
def HasAreas(context, mesh):
    if len(_GetAllAreas(mesh)) == 0:
        actions = []
        if len(context.GetStack()) > 1:
            actions.append(_DeleteObject(context, True))
        context.Error(mesh, 'has no areas', actions=actions)


@Validate('Tr2MeshArea')
def AreaContainsEffect(context, area):
    if not area.effect:
        context.Error(area, 'mesh area without an effect')


def _GetMeshAreaCount(granny, meshIndex):
    try:
        return len(granny.meshes[meshIndex].trigroups)
    except IndexError:
        return 0


@Validate('Tr2Mesh(mesh)/.../Tr2MeshArea(area)')
def ValidMeshAreaIndex(context, mesh, area):
    granny = _GetGranny(context, mesh.geometryResPath)
    if not granny:
        return
    count = _GetMeshAreaCount(granny, mesh.meshIndex)
    if area.index < 0 or area.index + area.count > count:
        context.Error(area, 'mesh area index or count is out of range (should be between 0 and %s)' % (count - 1))


GRANNY_VERTEX_ELEMENT_TO_USAGE = {'Position': 0,
 'DiffuseColor': 1,
 'Normal': 2,
 'Tangent': 3,
 'Binormal': 4,
 'TextureCoordinates': 5,
 'BoneIndices': 6,
 'BoneWeights': 7}
USAGE_TO_GRANNY_VERTEX_ELEMENT = {v:k for k, v in GRANNY_VERTEX_ELEMENT_TO_USAGE.items()}

def _GrannyVertexElementToTrinityUsage(name, offset):
    for k, v in GRANNY_VERTEX_ELEMENT_TO_USAGE.items():
        if name.startswith(k):
            if name == k:
                return (v, offset)
            else:
                return (v, int(name[len(k):]) + offset)


def _TrinityUsageToGrannyVertexElement(usage, usageIndex):
    name = USAGE_TO_GRANNY_VERTEX_ELEMENT.get(usage, 'Unknown(%s)' % usage)
    if usageIndex:
        name += str(usageIndex)
    return name


def _GetAllAreas(mesh):
    areas = []
    if mesh.opaqueAreas:
        areas.extend(mesh.opaqueAreas)
    if mesh.decalAreas:
        areas.extend(mesh.decalAreas)
    if mesh.depthAreas:
        areas.extend(mesh.depthAreas)
    if mesh.transparentAreas:
        areas.extend(mesh.transparentAreas)
    if mesh.additiveAreas:
        areas.extend(mesh.additiveAreas)
    if mesh.pickableAreas:
        areas.extend(mesh.pickableAreas)
    if mesh.mirrorAreas:
        areas.extend(mesh.mirrorAreas)
    if mesh.decalNormalAreas:
        areas.extend(mesh.decalNormalAreas)
    if mesh.depthNormalAreas:
        areas.extend(mesh.depthNormalAreas)
    if mesh.opaquePrepassAreas:
        areas.extend(mesh.opaquePrepassAreas)
    if mesh.decalPrepassAreas:
        areas.extend(mesh.decalPrepassAreas)
    if mesh.geometryEraserAreas:
        areas.extend(mesh.geometryEraserAreas)
    if mesh.distortionAreas:
        areas.extend(mesh.distortionAreas)
    return areas


def _GetAllShaderInputs(mesh):
    areas = _GetAllAreas(mesh)
    inputs = set()
    for each in areas:
        if each.effect:
            inputs.update(effects.GetVertexShaderInputs(each.effect, effectCache))

    return inputs


def _SubtractVertexInputs(context, mesh, path, inputs, grannyName, offset):
    granny = _GetGranny(context, path)
    if not granny:
        return False
    try:
        grannyMesh = granny.meshes[mesh.meshIndex]
    except IndexError:
        return False

    decl = grannyMesh.GetVertexDeclaration()
    for each in decl.keys():
        i = _GrannyVertexElementToTrinityUsage(each, offset)
        if i is None:
            context.Error(mesh, '%s granny file contains invalid vertex element %s' % (grannyName, each))
        elif i in inputs:
            inputs.remove(i)

    return True


def _ValidVertexShaderInputs(context, mesh, path, inputs, grannyName):
    if not _SubtractVertexInputs(context, mesh, path, inputs, grannyName, 0):
        return
    err = []
    for usage, usageIndex in inputs:
        if (usage, usageIndex) == (5, 1):
            continue
        codeUsages = []
        for obj in context.GetStack():
            if getattr(obj, 'GetVertexElementAddedThroughCode', None) and callable(obj.GetVertexElementAddedThroughCode):
                codeUsages = obj.GetVertexElementAddedThroughCode()

        if (usage, usageIndex) in codeUsages:
            continue
        err.append(_TrinityUsageToGrannyVertexElement(usage, usageIndex))

    if err:
        context.Error(mesh, '%s: %s granny file is missing vertex elements required by the shader: %s' % (grannyName, path, ', '.join(err)))


def GetGrannyBoneCount(context, path):
    granny = _GetGranny(context, path)
    if not granny:
        return 0
    return max(granny.GetMeshesJointCount())


def GetBoneCountFromLoadedGranny(grannyObject):
    return max(grannyObject.GetMeshesJointCount())


def GetMeshBoneCount(context, mesh):
    return GetGrannyBoneCount(context, mesh.geometryResPath)


@Validate('=Tr2Mesh')
def ValidMeshVertexShaderInputs(context, mesh):
    inputs = _GetAllShaderInputs(mesh)
    _ValidVertexShaderInputs(context, mesh, mesh.geometryResPath, inputs, '')


@Validate('Tr2InstancedMesh')
def ValidInstancedMeshVertexShaderInputs(context, mesh):
    inputs = _GetAllShaderInputs(mesh)
    if not _SubtractVertexInputs(context, mesh, mesh.geometryResPath, inputs, '', 0):
        return
    ignoreInstanced = not _SubtractVertexInputs(context, mesh, mesh.instanceGeometryResPath, inputs, '', 8)
    err = []
    for usage, usageIndex in inputs:
        if ignoreInstanced and usageIndex >= 8:
            continue
        err.append(_TrinityUsageToGrannyVertexElement(usage, usageIndex))

    if err:
        context.Error(mesh, 'granny file "%s" is missing vertex elements required by the shader: %s' % (mesh.geometryResPath, ', '.join(err)))


@Validate('Tr2Mesh')
def MaxBonesLimit(context, mesh):
    count = GetGrannyBoneCount(context, mesh.geometryResPath)
    if count > MAX_BONES_PER_MESH:
        context.Error(mesh, 'granny file contains %s bones; maximum allowed count is %s' % (count, MAX_BONES_PER_MESH))


def _IsSkinned(context, resPath):
    granny = _GetGranny(context, resPath)
    return IsGrannySkinned(granny)


def IsGrannySkinned(grannyObject):
    if not grannyObject:
        return None
    for each in grannyObject.meshes:
        if 'BoneIndices' in each.GetVertexDeclaration():
            return True

    return False


def IsMeshSkinned(context, mesh):
    return _IsSkinned(context, mesh.geometryResPath)


@Validate('Tr2Mesh(mesh)/.../Tr2Effect(effect)')
def SkinnedUnskinnedMismatch(context, mesh, effect):
    if not effect.effectFilePath:
        return
    isSkinned = IsMeshSkinned(context, mesh)
    if isSkinned is None:
        return
    isEffectSkinned = 'skinned_' in effect.effectFilePath.lower()
    if not isSkinned and isEffectSkinned:
        context.Error(effect, 'skinned effect is applied to a non-skinned mesh')
