#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\sofHullValidation.py
import os
import blue
import trinity
from trinity.effects import GetMergedParameters
from evegraphics.validation.commonUtilities import Validate, IsContent
from evegraphics.validation.validationFunctions import ShouldBeLessThanOrEqual, ListAttributesAreDistinct, ValidateResPath
from evegraphics.validation.validators import limits
from evegraphics.validation import resources
from evegraphics.validation.validators.meshValidation import IsGrannySkinned, GetBoneCountFromLoadedGranny
ALLIANCE_LOGO = 0
CORP_LOGO = 1

def _GetAllHullAreas(hull):
    allAreas = []
    areaParameters = ['additiveAreas',
     'decalAreas',
     'depthAreas',
     'distortionAreas',
     'opaqueAreas',
     'transparentAreas']
    for areaName in areaParameters:
        areas = getattr(hull, areaName, None)
        if areas is not None:
            allAreas.extend(areas)

    return allAreas


@Validate('EveSOFDataHull')
def ValidateHullCategory(context, hull):
    category = hull.category
    if len(category) == 0:
        context.Error(hull, 'No category set for hull')
    elif limits.GetLimits(context, category) is None:
        context.Error(hull, 'No limits found for category: ' + category)


@Validate('EveSOFDataHull')
def ValidateThatMeshPointsToValidGrannyFile(context, hull):
    gr2ResPath = hull.geometryResFilePath
    granny = resources.GetResource(context, gr2ResPath, resources.ResourceType.GRANNY)
    if not granny:
        context.Error(hull, "geometryResFilePath '%s' does not point to a valid gr2 file" % gr2ResPath)


@Validate('EveSOFDataHull')
def ValidateMeshIndicesUsedInAreas(context, hull):
    gr2ResPath = hull.geometryResFilePath
    granny = resources.GetResource(context, gr2ResPath, resources.ResourceType.GRANNY)
    if not granny:
        return
    meshCount = len(granny.meshes)
    if meshCount < 1:
        context.Error(hull, "resPath '%s' should have 1 mesh, has %d" % (gr2ResPath, meshCount))
        return
    meshGroupsIndices = [ i for i in range(len(granny.meshes[0].trigroups)) ]
    areaIndices = [ a.index + i for a in _GetAllHullAreas(hull) for i in range(a.count) ]
    for meshGroupIndex in meshGroupsIndices:
        if meshGroupIndex not in areaIndices:
            context.Error(hull, "meshgroup with index '%d' is not referenced by any area" % meshGroupIndex)

    for areaIndex in areaIndices:
        if areaIndex not in meshGroupsIndices:
            context.Error(hull, "mesharea with index '%d' is not found in granny" % areaIndex)


@Validate('EveSOFDataHull')
def ValidateHullTriangleCount(context, hull):
    max_triangles = limits.GetValue(hull.category, limits.TRIANGLE_BUDGET)
    if max_triangles is None:
        return
    gr2ResPath = hull.geometryResFilePath
    granny = resources.GetResource(context, gr2ResPath, resources.ResourceType.GRANNY)
    if not granny:
        context.Error(hull, "resPath '%s' does not point to a valid gr2 file" % gr2ResPath)
        return
    count = 0
    for mesh in granny.meshes:
        for each in mesh['trigroups']:
            count += each['TriCount']

        break

    message = 'Geometry triangle count too high for %s. Is %i but should be less than %i' % (gr2ResPath, count, max_triangles)
    context.ExpectValue(hull, count, ShouldBeLessThanOrEqual(max_triangles), message)


@Validate('EveSOFDataHull')
def ValidateNameAndDescription(context, hull):
    attributesToCheck = ['name', 'description']
    for attributeName in attributesToCheck:
        value = getattr(hull, attributeName)
        if not value.islower() or ' ' in value:
            context.Error(hull, "%s '%s' should be lowercase and have no spaces" % (attributeName, value), actions=[_ForceCorrectString(hull, attributeName)])


def _ForceCorrectString(hull, hullAttribute):

    def inner():
        currentString = getattr(hull, hullAttribute)
        setattr(hull, hullAttribute, currentString.lower().replace(' ', ''))
        return True

    return ('Force lowercase and delete spaces', inner, True)


@Validate('EveSOFDataHull')
def ValidateSkinningIsCorrect(context, hull):
    grannyObject = resources.GetResource(context, hull.geometryResFilePath, resources.ResourceType.GRANNY)
    isSkinned = IsGrannySkinned(grannyObject)
    if isSkinned is None:
        return
    if hull.isSkinned:
        if not isSkinned and GetBoneCountFromLoadedGranny(grannyObject) != 1:
            context.Error(hull, "Granny file isn't skinned, but hull is marked as skinned", actions=[_SetValidIsSkinnedAttribute(hull, isSkinned)])
    elif isSkinned:
        context.Error(hull, 'Granny file is skinned, but hull is not set as skinned', actions=[_SetValidIsSkinnedAttribute(hull, isSkinned)])


def _SetValidIsSkinnedAttribute(hull, newIsSkinnedValue):

    def inner():
        hull.isSkinned = newIsSkinnedValue
        return True

    return ("Set 'isSkinned' to correct value", inner, True)


@Validate('EveSOFDataHullArea')
def ValidateGlassArea(context, area):
    if area.areaType is trinity.EveSOFDataAreaType.Glass and 'glass' not in area.shader:
        context.Error(area, 'Glass area does not use glass shader. Got %s.' % area.shader)


@Validate('EveSOFDataHullArea')
def ValidateRockArea(context, area):
    if 'rockv5' in area.shader:
        if area.areaType != trinity.EveSOFDataAreaType.Rock:
            context.Error(area, 'Rock shaders require ROCK areaType!')


@Validate('EveSOFDataHullArea')
def ValidateTechLevelsUsed(context, area):
    techLevels = ('_t1_', '_t2_', '_t2a_', '_t2b_', '_t2c_', '_t3_')
    resPathLst = [ tex.resFilePath.lower() for tex in area.textures ]
    techLevelCollector = {t:False for t in techLevels}
    for level in techLevels:
        techLevelCollector[level] = any((level in s for s in resPathLst))

    techLevelsUsed = sum([ 1 for b in techLevelCollector.itervalues() if b ])
    if techLevelsUsed > 1:
        context.Error(area, 'Different tech levels used in textures of this area')


def _GetSofAreaShaderPath(context, area):
    generic = resources.GetResource(context, 'res:/dx9/model/spaceobjectfactory/generic.red', resources.ResourceType.OBJECT)
    if not generic:
        return ''
    head, tail = os.path.split(area.shader)
    return '%s/%s/%s%s' % (generic.areaShaderLocation,
     head,
     generic.shaderPrefix,
     tail)


@Validate('EveSOFDataHullArea')
def HullAreaHasValidShader(context, area):
    shaderPath = _GetSofAreaShaderPath(context, area)
    if shaderPath and not blue.paths.exists(shaderPath):
        context.Error(area, 'Area shader does not exit')


def _GetGenericShader(context, shader):
    generic = resources.GetResource(context, 'res:/dx9/model/spaceobjectfactory/generic.red', resources.ResourceType.OBJECT)
    if not generic:
        return None
    for each in generic.areaShaders:
        if each.shader.lower() == shader.lower():
            return each


@Validate('EveSOFDataHullArea')
def ValidateHullAreaTextures(context, area):
    shaderPath = _GetSofAreaShaderPath(context, area)
    if not shaderPath or not blue.paths.exists(shaderPath):
        return
    params, res, _ = GetMergedParameters(shaderPath)
    for each in area.textures:
        if each.name not in res:
            context.Error(each, 'Texture %s is not used by shader %s' % (each.name, area.shader))

    generic = _GetGenericShader(context, area.shader)
    defaultTextures = []
    if generic:
        defaultTextures = [ x.name for x in generic.defaultTextures ]
    existing = {x.name:x for x in area.textures}
    missing = set(res.keys()).difference(existing).difference(defaultTextures)
    if missing:
        context.Error(area, 'Area is missing textures %s required by shader %s' % (', '.join(missing), area.shader))


@Validate('EveSOFDataHullArea')
def ValidateHullAreaParameters(context, area):
    shaderPath = _GetSofAreaShaderPath(context, area)
    if not shaderPath or not blue.paths.exists(shaderPath):
        return
    params, res, _ = GetMergedParameters(shaderPath)
    for each in area.parameters:
        if each.name not in params:
            context.Error(each, 'Parameter %s is not used by shader %s' % (each.name, area.shader))


@Validate('EveSOFDataInstancedMesh')
def ValidateInstancedMesh(context, instancedMesh):
    context.Expect(instancedMesh.textures, None, ListAttributesAreDistinct('name'))


@Validate('EveSOFDataHull')
def HullRotationCurvePathIsValid(context, hull):
    if hull.modelRotationCurvePath:
        ValidateResPath(context, hull, 'modelRotationCurvePath', ('.red',))


@Validate('EveSOFDataHull')
def HullTranslationCurvePathIsValid(context, hull):
    if hull.modelTranslationCurvePath:
        ValidateResPath(context, hull, 'modelTranslationCurvePath', ('.red',))


@Validate('EveSOFDataHull', IsContent)
def ValidateBannerSets(context, hull):
    if context.GetArgument(IsContent) == IsContent.CONTENT:
        return
    category = hull.category
    min_corp_banners = limits.GetValue(category, limits.MIN_CORP_BANNERS)
    min_alliance_banners = limits.GetValue(category, limits.MIN_ALLIANCE_BANNERS)
    max_corp_banners = limits.GetValue(category, limits.MAX_CORP_BANNERS)
    max_alliance_banners = limits.GetValue(category, limits.MAX_ALLIANCE_BANNERS)
    if min_corp_banners is None:
        min_corp_banners = 0
    if min_alliance_banners is None:
        min_alliance_banners = 0
    if max_corp_banners is None:
        max_corp_banners = 0
    if max_alliance_banners is None:
        max_alliance_banners = 0
    alliance_count = 0
    corp_count = 0
    if not hull.banners:
        if min_corp_banners:
            context.Error(hull, 'Missing Corp Logo Banners.')
        if min_alliance_banners:
            context.Error(hull, 'Missing Alliance Logo Banners.')
        return
    for banner in hull.banners:
        if banner.usage == ALLIANCE_LOGO:
            alliance_count += 1
        if banner.usage == CORP_LOGO:
            corp_count += 1

    if alliance_count < min_alliance_banners:
        context.Error(hull, 'Missing Alliance Logo Banners.')
    if corp_count < min_corp_banners:
        context.Error(hull, 'Missing Corp Logo Banners.')
    if corp_count > max_corp_banners:
        context.Error(hull, 'Too many Corp Logo banners.')
    if alliance_count > max_alliance_banners:
        context.Error(hull, 'Too many Alliance Logo banners.')


@Validate('EveSOFDataHullController')
def HullControllerPathIsValid(context, controllerRef):
    ValidateResPath(context, controllerRef, 'path', ('.red',))


@Validate('List[EveSOFDataHullController]')
def NoDuplicateHullControllerReferences(context, controllerRefs):
    context.Expect(controllerRefs, None, ListAttributesAreDistinct('path'))


def _LowerCasify(decalSet):

    def inner():
        decalSet.visibilityGroup = decalSet.visibilityGroup.lower()
        return True

    return ('Convert to Lower Case', inner, True)


@Validate('EveSOFDataDecalSet')
def ValidateDecalSet(context, decalSet):
    if decalSet.visibilityGroup != decalSet.visibilityGroup.lower():
        context.Error(decalSet, "%s visibilityGroup '%s' should be lowercase" % (decalSet.name, decalSet.visibilityGroup), actions=[_LowerCasify(decalSet)])


@Validate('List[EveSOFDataDecalSetItem]')
def NoDuplicateHullDecalSetItemss(context, decalSetItems):
    context.Expect(decalSetItems, None, ListAttributesAreDistinct('position'))


@Validate('EveSOFDataDecalSetItem')
def ValidateDecalSetItem(context, decalSetItem):
    if len(decalSetItem.textures) == 0 and decalSetItem.usage == trinity.DecalUsage.Standard:
        context.Error(decalSetItem, "DecalSetItem should have textures when defined with 'Standard' usage")
    if len(decalSetItem.textures) > 0 and decalSetItem.usage == trinity.DecalUsage.Logo:
        context.Error(decalSetItem, "DecalSetItem has textures but is defined with 'Logo' usage, which uses textures from the logoset")


@Validate('EveSOFDataLightSetItem')
def ValidateLightSetItem(context, lightSetItem):
    if lightSetItem.radius == 0:
        context.Error(lightSetItem, 'LightSetItem has no radius!')
    elif lightSetItem.radius < 0:
        context.Error(lightSetItem, 'LightSetItem has negative radius!')
    if lightSetItem.innerRadius < 0:
        context.Error(lightSetItem, 'LightSetItem has negative innerRadius!')
    if lightSetItem.brightness == 0:
        context.Error(lightSetItem, 'LightSetItem has no brightness!')
    elif lightSetItem.brightness < 0:
        context.Error(lightSetItem, 'LightSetItem has negative brightness!')
    if lightSetItem.texturePath != '' and not lightSetItem.texturePath.startsWith('dynamic:/'):
        context.Error(lightSetItem, 'LightSetItem cannot have a non dynamic texture!')


@Validate('EveSOFDataHullSoundEmitter')
def SofSoundEmitterHasName(context, emitter):
    if not emitter.name:
        context.Error(emitter, 'sound emitter must have a name')


@Validate('EveSOFDataHull')
def SofHullHasCorrectShapeEllipsoidRadius(context, hull):
    r = hull.shapeEllipsoidRadius
    if not (all([ element == -1 for element in r ]) or all([ element > 0 for element in r ])):
        context.Error(hull, 'Shape ellipsoid radius is invalid (either all -1 or all positive')


def _FixUVSetSelectorParameter(parameter, newValue):

    def inner():
        parameter.value = newValue
        return True

    return ('Set UVSetSelector to %s' % newValue[1], inner, True)


@Validate('EveSOFDataHull')
def SofHullCheckUvSetExists(context, hull):
    gr2ResPath = hull.geometryResFilePath
    granny = resources.GetResource(context, gr2ResPath, resources.ResourceType.GRANNY)
    if not granny or len(granny.meshes) == 0:
        return
    textureCoordIndices = set()
    for mesh in granny.meshes:
        for declaration in mesh.GetVertexDeclaration():
            if declaration.startswith('TextureCoordinates'):
                textureCoordIndices.add(int(declaration.replace('TextureCoordinates', '')))

    for area in _GetAllHullAreas(hull):
        gd = area.parameters.FindByName('GeneralData')
        if gd and int(gd.value[1]) not in textureCoordIndices:
            context.Error(gd, 'UVSetSelector is set to %d by the SOF Hull but granny file only has [%s]' % (int(gd.value[1]), ', '.join([ str(i) for i in textureCoordIndices ])), actions=[ _FixUVSetSelectorParameter(gd, (gd.value[0],
             i,
             gd.value[2],
             gd.value[3])) for i in textureCoordIndices ])
