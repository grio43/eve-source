#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\decalValidation.py
import os
import blue
import trinity
from platformtools.compatibility.exposure.artpipeline import decalutils
from evegraphics.validation.commonUtilities import Validate, IsContent
from evegraphics.validation.validationFunctions import ListAttributesAreDistinct
from evegraphics.validation import resources
import sofHullValidation
import limits
from trinity.effects import GetMergedParameters
MAX_DECAL_PRIMITIVE_COUNT = 1000
_VALID_FXPATH_LOC = 'res:/graphics/effect/managed/space/decals'
FACTION_PATH = 'res:/dx9/model/spaceobjectfactory/factions'

def GetFactionVisibilityGroups(context):
    factionVisibilityGroups = context.cache.get('factionVisibilityGroups', None)
    if factionVisibilityGroups is None:
        factions = []
        factionVisibilityGroups = {}
        for f in blue.paths.listdir(FACTION_PATH):
            if os.path.splitext(f)[1].lower() == '.red':
                factions.append(resources.GetResource(context, FACTION_PATH + '/' + f, resources.ResourceType.OBJECT))

        for faction in factions:
            if hasattr(faction, 'visibilityGroupSet'):
                factionVisibilityGroups[faction] = [ g.str for g in getattr(faction.visibilityGroupSet, 'visibilityGroups', []) ]
            else:
                factionVisibilityGroups[faction] = []

        context.cache['factionVisibilityGroups'] = factionVisibilityGroups
    return factionVisibilityGroups


@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullDecalSet(decalSet)')
def ValidateDecalSet(context, owner, decalSet):
    if decalSet.name == '':
        context.Error(decalSet, 'DecalSet has no name')
    if decalSet.visibilityGroup is None or decalSet.visibilityGroup == '':
        context.Error(decalSet, 'DecalSet %s has no visibilityGroup set' % str(decalSet.name))
    elif decalSet.visibilityGroup != decalSet.visibilityGroup.lower():
        context.Error(decalSet, 'DecalSet %s has a visibilityGroup with uppercase letters %s ' % (str(decalSet.name), str(decalSet.visibilityGroup)))
    killmarkCount = limits.GetValue(owner.category, limits.KILLMARK_DECAL)
    shouldHaveKillmarks = killmarkCount is not None and killmarkCount > 0
    if decalSet.visibilityGroup == 'primary':
        killcounters = [ item.name for item in decalSet.items if item.usage == trinity.DecalUsage.KillCounter ]
        if shouldHaveKillmarks and len(killcounters) == 0:
            context.Error(decalSet, 'DecalSet %s has no decals with usage KillCounter' % str(decalSet.name))
        elif not shouldHaveKillmarks and len(killcounters) > 0:
            context.Error(decalSet, "DecalSet %s has decals with usage KillCounter, but the owner category '%s' shouldn't have any" % (str(decalSet.name), str(owner.category)))


@Validate('EveSOFDataHull(owner)/.../List[EveSOFDataHullDecalSet](decalSets)')
def ValidateDecalLimit(context, owner, decalSets):
    factionVisibilityGroups = GetFactionVisibilityGroups(context)
    nonLogoDecalCountByVisibilityGroup = {decalSet.visibilityGroup:[ item for item in decalSet.items if item.usage != trinity.DecalUsage.Logo ] for decalSet in decalSets}
    logoDecalCountByVisibilityGroup = {decalSet.visibilityGroup:[ item for item in decalSet.items if item.usage == trinity.DecalUsage.Logo ] for decalSet in decalSets}
    decalLimit = limits.GetValue(owner.category, limits.MAX_DECAL_COUNT)
    decalLimit = 0 if decalLimit is None else decalLimit
    factionDecalCount = {}
    for faction, visibilityGroups in factionVisibilityGroups.iteritems():
        decalCount = 0
        for factionVisibilityGroup in visibilityGroups:
            decalCount += len(nonLogoDecalCountByVisibilityGroup.get(factionVisibilityGroup, []))
            if faction.logoSet is not None:
                logoDecals = logoDecalCountByVisibilityGroup.get(factionVisibilityGroup, [])
                for logoDecal in logoDecals:
                    factionLogos = [faction.logoSet.Primary,
                     faction.logoSet.Secondary,
                     faction.logoSet.Tertiary,
                     faction.logoSet.Marking_01,
                     faction.logoSet.Marking_02]
                    if factionLogos[logoDecal.logoType] is not None:
                        decalCount += 1

        factionDecalCount[faction.name] = decalCount

    offendingFactions = {factionName:decalCount for factionName, decalCount in factionDecalCount.iteritems() if decalCount > decalLimit}
    if len(offendingFactions):
        message = 'Hull exceeds decal limit of %s with a highest count of %s.\nThis limit is exceeded when hull is combined with the following factions;\n\n\t- %s' % (decalLimit, max(offendingFactions.values()), ',\n\t- '.join(offendingFactions.keys()))
        context.Error(owner, message)


@Validate('EveSOFDataHullDecalSet')
def ValidateNoRepetitionIsWithinDecalSet(context, decalSet):
    context.Expect(decalSet.items, None, ListAttributesAreDistinct('name'))
    context.Expect(decalSet.items, None, ListAttributesAreDistinct(None, listAttributesToIgnore=['name']))


@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullDecalSet(decalSet)')
def ValidateAllDecalsUseTheSameParentTextures(context, owner, decalSet):
    allAreas = sofHullValidation._GetAllHullAreas(owner)
    usedMaps = {'NormalMap': [],
     'DirtMap': []}
    for area in allAreas:
        for tex in area.textures:
            if tex.name in usedMaps.iterkeys() and tex.resFilePath.lower() not in usedMaps[tex.name]:
                usedMaps[tex.name].append(tex.resFilePath.lower())

    for decal in decalSet.items:
        for tex in decal.textures:
            if tex.name in usedMaps.iterkeys():
                if tex.resFilePath.lower() not in usedMaps[tex.name]:
                    context.Error(decal, 'Decal ' + str(decal.name) + ' uses wrong ' + str(tex.name) + ': ' + str(tex.resFilePath.lower()))


@Validate('EveSOFDataHullDecalSetItem')
def ValidateDecalSetItemTextures(context, decal):
    textures = []
    if decal.usage == trinity.DecalUsage.KillCounter:
        textures = ['DecalTransparencyMap']
    if decal.usage in (trinity.DecalUsage.Glow, trinity.DecalUsage.GlowCylindrical):
        textures = ['DecalTransparencyMap', 'DecalGlowMap']
    elif decal.usage == trinity.DecalUsage.Hole:
        textures = ['DecalInsideCubeMap', 'DecalHoleMap', 'DecalTransparencyMap']
    elif decal.usage in (trinity.DecalUsage.Standard, trinity.DecalUsage.Cylindrical):
        textures = ['DecalTransparencyMap',
         'DecalNormalMap',
         'DecalFresnelMap',
         'DecalAlbedoMap',
         'DecalRoughnessMap']
    _ValidateDecalSetItem(context, decal, textures)


def _ValidateDecalSetItem(context, decal, textureNames):
    texturesByName = {tex.name:tex.resFilePath for tex in decal.textures}
    missingTextures = set(textureNames).difference(set(texturesByName.keys()))
    if len(missingTextures) > 0:
        context.Error(decal, 'DecalSetItem %s has a missing textures %s' % (str(decal.name), missingTextures))
    unsetTextures = [ textureName for textureName, texturePath in texturesByName.iteritems() if texturePath is None or texturePath == '' ]
    if len(unsetTextures) > 0:
        context.Error(decal, 'DecalSetItem %s has unset textures %s' % (str(decal.name), unsetTextures))
    if decal.usage == trinity.DecalUsage.Logo and len(decal.textures) > 0:
        context.Error(decal, 'DecalSetItem %s is used as a logo but has textures %s. The textures should come from the factional logoset' % (str(decal.name), texturesByName.keys()))
    else:
        unusedTextures = set(texturesByName.keys()).difference(set(textureNames))
        if len(unusedTextures) > 0:
            context.Error(decal, 'DecalSetItem %s has a unused textures %s' % (str(decal.name), unusedTextures))


@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullDecalSetItem(decal)', IsContent(IsContent.CONTENT))
def DecalHasGeometry(context, owner, decal):
    grannyPath = owner.geometryResFilePath
    if not grannyPath:
        return
    ibs = decalutils.ComputeDecalIndexBuffers(decal.position, decal.rotation, decal.scaling, blue.paths.ResolvePath(grannyPath))
    if not ibs or not ibs[0]:
        context.Error(decal, 'decal is not touching any geometry')
    for ib in ibs:
        if len(ibs) / 3 > MAX_DECAL_PRIMITIVE_COUNT:
            context.Error(decal, 'too many triangles for the decal (maximum is %s)' % MAX_DECAL_PRIMITIVE_COUNT)


@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullDecalSetItem(decal)', IsContent(IsContent.BRANCH))
def SofDecalHasGeometry(context, owner, decal):
    grannyPath = owner.geometryResFilePath
    if not grannyPath:
        return
    existing = [ x.GetIndices() for x in decal.indexBuffers ]
    ibs = decalutils.ComputeDecalIndexBuffers(decal.position, decal.rotation, decal.scaling, blue.paths.ResolvePath(grannyPath))
    if existing != ibs:
        context.Error(decal, 'decal persisted index buffer is out of date')


@Validate('EveSpaceObjectDecal')
def ValidateEveSpaceObjectDecal(context, decal):
    if [ each for each in decal.GetDecalPrimitiveCounts() if each >= MAX_DECAL_PRIMITIVE_COUNT ]:
        context.Error(decal, 'decal index buffer is too large')


@Validate('List[EveSpaceObjectDecal]')
def ValidateListOfEveSpaceObjectDecal(context, decals):
    context.Expect(decals, None, ListAttributesAreDistinct(None))


@Validate('EveSpaceObjectDecal', IsContent(IsContent.BRANCH))
def PublishedDecalHasIB(context, decal):
    if not decal.hasStaticIndexBuffers:
        context.Error(decal, 'decal needs to have index buffers')


@Validate('EveSpaceObjectDecal', IsContent(IsContent.CONTENT))
def ContentDecalHasNoIB(context, decal):
    if decal.hasStaticIndexBuffers:
        context.Error(decal, 'decal should not have index buffers')


@Validate('EveSpaceObject2(owner)/.../EveSpaceObjectDecal(decal)', IsContent(IsContent.CONTENT))
def DecalHasGeometry(context, owner, decal):
    mesh = owner.mesh
    if isinstance(mesh, trinity.Tr2Mesh):
        grannyPath = mesh.geometryResPath
    else:
        return
    if not grannyPath:
        return
    ibs = decalutils.ComputeDecalIndexBuffers(decal.position, decal.rotation, decal.scaling, blue.paths.ResolvePath(grannyPath))
    if not ibs or not ibs[0]:
        context.Error(decal, 'decal is not touching any geometry')
    if len(ibs[0]) / 3 > MAX_DECAL_PRIMITIVE_COUNT:
        context.Error(decal, 'too many triangles for the decal (maximum is %s)' % MAX_DECAL_PRIMITIVE_COUNT)


@Validate('EveSpaceObject2(owner)/.../EveSpaceObjectDecal(decal)', IsContent(IsContent.BRANCH))
def DecalHasGeometry(context, owner, decal):
    mesh = owner.mesh
    if isinstance(mesh, trinity.Tr2Mesh):
        grannyPath = mesh.geometryResPath
    else:
        return
    if not grannyPath:
        return
    existing = decal.GetStaticIndexBuffers()
    ibs = decalutils.ComputeDecalIndexBuffers(decal.position, decal.rotation, decal.scaling, blue.paths.ResolvePath(grannyPath))
    if existing != ibs:
        context.Error(decal, 'decal persisted index buffer is out of date')


@Validate('EveSpaceObjectDecal')
def DecalNeedsAnEffect(context, decal):
    if not decal.decalEffect:
        context.Error(decal, 'decal is missing an effect')


@Validate('EveSpaceObjectDecal')
def ValidDecalEffectPath(context, decal):
    if decal.decalEffect and decal.decalEffect.effectFilePath:
        if not decal.decalEffect.effectFilePath.lower().startswith(_VALID_FXPATH_LOC):
            context.Error(decal, 'decal effect must be in %s' % _VALID_FXPATH_LOC)


@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullDecalSetItem(decal)')
def SofDecalMeshIndexIsValid(context, owner, decal):
    areas = set([ x.index for x in owner.opaqueAreas ])
    if decal.meshIndex >= 0 and decal.meshIndex not in areas:
        context.Error(decal, 'Mesh index does not reference any opaque area')


@Validate('EveSOFDataHullDecalSetItem')
def SofDecalWithParentTexturesShouldHaveMeshIndex(context, decalSetItem):
    if decalSetItem.meshIndex >= 0:
        return
    generic = resources.GetResource(context, 'res:/dx9/model/spaceobjectfactory/generic.red', resources.ResourceType.OBJECT)
    if not generic:
        return
    decalShader = _GetDecalSetItemShader(decalSetItem)
    for each in generic.decalShaders:
        if each.shader == decalShader:
            if each.parentTextures:
                context.Error(decalSetItem, 'Decal with parent textures must have meshIndex specified')


def _GetDecalSetItemShader(decalSetItem):
    shaderToPick = {trinity.DecalUsage.KillCounter: 'decalcounterv5.fx',
     trinity.DecalUsage.Standard: 'decalv5.fx',
     trinity.DecalUsage.Cylindrical: 'decalcylindricv5.fx',
     trinity.DecalUsage.Glow: 'decalglowv5.fx',
     trinity.DecalUsage.GlowCylindrical: 'decalglowcylindricv5.fx',
     trinity.DecalUsage.Logo: 'decalv5.fx',
     trinity.DecalUsage.Hole: 'decalholev5.fx'}
    shader = shaderToPick[decalSetItem.usage]
    return shader


def _GetParentTextures(context, decalSetItem):
    generic = resources.GetResource(context, 'res:/dx9/model/spaceobjectfactory/generic.red', resources.ResourceType.OBJECT)
    if not generic:
        return []
    decalShader = _GetDecalSetItemShader(decalSetItem)
    for each in generic.decalShaders:
        if each.shader == decalShader:
            return [ x.str for x in each.parentTextures ]

    return []


@Validate('EveSOFDataHullDecalSetItem(decal)/.../EveSOFDataTexture(texture)')
def SofDecalDoesNotContainParentTextures(context, decal, texture):
    if decal.meshIndex < 0:
        return
    textures = _GetParentTextures(context, decal)
    if texture.name in textures:
        context.Error(texture, 'Decal texture is inherited from the hull and needs to be deleted')


def _GetSofDecalSetItemShaderPath(context, decaSetItem):
    generic = resources.GetResource(context, 'res:/dx9/model/spaceobjectfactory/generic.red', resources.ResourceType.OBJECT)
    if not generic:
        return ''
    decalShader = _GetDecalSetItemShader(decaSetItem)
    head, tail = os.path.split(decalShader)
    return '%s/%s/%s%s' % (generic.decalShaderLocation,
     head,
     generic.shaderPrefix,
     tail)


@Validate('EveSOFDataHullDecalSetItem')
def ValidateSofDecalTextures(context, decalSetItem):
    shaderPath = _GetSofDecalSetItemShaderPath(context, decalSetItem)
    if not shaderPath or not blue.paths.exists(shaderPath):
        return
    params, res, _ = GetMergedParameters(shaderPath)
    decalShader = _GetDecalSetItemShader(decalSetItem)
    for each in decalSetItem.textures:
        if each.name not in res:
            context.Error(each, 'Texture %s is not used by shader %s' % (each.name, decalShader))


@Validate('EveSOFDataHullDecalSetItem')
def ValidateSofDecalParameters(context, decalSetItem):
    shaderPath = _GetSofDecalSetItemShaderPath(context, decalSetItem)
    if not shaderPath or not blue.paths.exists(shaderPath):
        return
    params, res, _ = GetMergedParameters(shaderPath)
    decalShader = _GetDecalSetItemShader(decalSetItem)
    for each in decalSetItem.parameters:
        if each.name not in params:
            context.Error(each, 'Parameter %s is not used by shader %s' % (each.name, decalShader))
