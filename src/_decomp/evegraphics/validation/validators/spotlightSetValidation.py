#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\spotlightSetValidation.py
from evegraphics.validation.commonUtilities import Validate, IsContent
from evegraphics.validation.validationFunctions import ListIsNotEmpty, ListAttributesAreDistinct
from evegraphics.validation.validators.meshValidation import IsMeshSkinned, GetMeshBoneCount, GetGrannyBoneCount
from evegraphics.validation.validationFunctions import ValidateTexturePath

@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullSpotlightSetItem(spotlightSetItem)')
def ValidateSofSpriteSetItem(context, owner, spotlightSetItem):
    count = GetGrannyBoneCount(context, owner.geometryResFilePath)
    if count == 0:
        if spotlightSetItem.boneIndex != 0:
            context.Error(spotlightSetItem, 'boneIndex is not zero, but the owner is not skinned')
    elif spotlightSetItem.boneIndex >= count:
        context.Error(spotlightSetItem, 'invalid boneIndex, the owner has only %s bones' % count)


@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullSpotlightSet(spotLightSet)')
def ValidateEveSOFDataHullSpotlightSet(context, owner, spotLightSet):
    if not owner.isSkinned:
        if spotLightSet.skinned:
            context.Error(spotLightSet, 'Parent hull is not animated, but spottightset is: ' + str(spotLightSet.name))


@Validate('List[EveSOFDataHullSpotlightSet]')
def ValidateListOfEveSOFDataHullSpotlightSet(context, spotLightSets):
    context.Expect(spotLightSets, None, ListAttributesAreDistinct('name'))
    context.Expect(spotLightSets, None, ListAttributesAreDistinct('items'))


@Validate('EveSOFDataHullSpotlightSet')
def SofSpotlightSetIsNotEmpty(context, spriteSets):
    if not spriteSets.items:
        context.Error(spriteSets, 'Spotlight set it empty')


@Validate('EveSOFDataHullSpotlightSetItem')
def ValidateEveSOFDataHullSpotlightSetItem(context, spotLightSetItem):
    if spotLightSetItem.groupIndex == -1:
        context.Error(spotLightSetItem, 'Spotlight item found with negative groupIndex!')


@Validate('EveSpotlightSet')
def SpotlightSetDisplay(context, spotlightSet):
    if not spotlightSet.display and not context.IsBoundAsDestination(spotlightSet, 'display'):
        context.Error(spotlightSet, 'display is off - spot light set is invisible')


@Validate('EveSpotlightSet')
def SpotlightSetMustHaveSprites(context, spotlightSet):
    if not spotlightSet.spotlightItems:
        context.Error(spotlightSet, 'has no items')


@Validate('EveSpotlightSet')
def SpotlightSetMustHaveEffect(context, spotlightSet):
    if not spotlightSet.glowEffect and not spotlightSet.coneEffect:
        context.Error(spotlightSet.glowEffect, 'has no glow or cone effect')


@Validate('EveSpaceObject2(owner)/List/EveSpotlightSet(spotlightSet)')
def SpotlightSkinnedCorrespondsToOwner(context, owner, spotlightSet):
    mesh = owner.mesh
    isSkinned = IsMeshSkinned(context, mesh)
    if isSkinned is None or isSkinned:
        return
    if isSkinned != spotlightSet.skinned:
        context.Error(spotlightSet, 'is %sskinned, while the owner space object is %sskinned' % ('' if spotlightSet.skinned else 'non-', '' if isSkinned else 'non-'))


@Validate('EveSpotlightSetItem')
def SpotlightSetItemConeColorIsValid(context, item):
    if any((x < 0 for x in item.coneColor)):
        context.Error(item, 'cone color is negative')


@Validate('EveSpotlightSetItem')
def SpotlightSetItemSpriteColorIsValid(context, item):
    if any((x < 0 for x in item.spriteColor)):
        context.Error(item, 'sprite color is negative')


@Validate('EveSpotlightSetItem')
def SpotlightSetItemFlareColorIsValid(context, item):
    if any((x < 0 for x in item.flareColor)):
        context.Error(item, 'flare color is negative')


@Validate('EveSpotlightSetItem')
def SpotlightSetItemIsNotBlack(context, item):
    if item.coneColor[0:3] == (0, 0, 0) and item.spriteColor[0:3] == (0, 0, 0) and item.flareColor[0:3] == (0, 0, 0):
        context.Error(item, 'item is black')


@Validate('EveSpaceObject2(owner)/List/EveSpotlightSet/.../EveSpotlightSetItem(item)')
def SpotlightSetItemBoneIndexIsValid(context, owner, item):
    mesh = owner.mesh
    if not mesh or not mesh.geometryResPath:
        return
    count = GetMeshBoneCount(context, mesh)
    if count == 0:
        if item.boneIndex != 0:
            context.Error(item, 'boneIndex is not zero, but the owner is not skinned')
    elif item.boneIndex >= count:
        context.Error(item, 'invalid boneIndex, the owner has only %s bones' % count)


@Validate('EveChildMesh(owner)/List/EveSpotlightSet/.../EveSpotlightSetItem(item)')
def ChildMeshSpotlightSetItemBoneIndexIsValid(context, owner, item):
    mesh = owner.mesh
    if not mesh or not mesh.geometryResPath:
        return
    count = GetMeshBoneCount(context, mesh)
    if count == 0:
        if item.boneIndex != 0:
            context.Error(item, 'boneIndex is not zero, but the owner is not skinned')
    elif item.boneIndex >= count:
        context.Error(item, 'invalid boneIndex, the owner has only %s bones' % count)


@Validate('EveSOFDataHullSpotlightSet', IsContent)
def ValidateEveSOFDataHullSpotlightSetTextures(context, spotlightSet):
    ValidateTexturePath(context, spotlightSet, 'glowTextureResPath', context.GetArgument(IsContent) == IsContent.CONTENT)
    ValidateTexturePath(context, spotlightSet, 'coneTextureResPath', context.GetArgument(IsContent) == IsContent.CONTENT)
