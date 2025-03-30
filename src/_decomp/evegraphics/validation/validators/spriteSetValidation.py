#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\spriteSetValidation.py
from evegraphics.validation.commonUtilities import Validate, DeleteTopAction
from evegraphics.validation.errors import SingleObjectValidationError
from evegraphics.validation.validationFunctions import ListIsNotEmpty, ListAttributesAreDistinct
from evegraphics.validation.validators.meshValidation import IsMeshSkinned, GetMeshBoneCount, GetGrannyBoneCount

@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullSpriteSetItem(spriteSetItem)')
def ValidateSofSpriteSetItem(context, owner, spriteSetItem):
    if spriteSetItem.minScale == 0.0 and spriteSetItem.maxScale == 0.0:
        context.AddError(SingleObjectValidationError(spriteSetItem, 'has minScale and maxScale equal to 0.0'))
    count = GetGrannyBoneCount(context, owner.geometryResFilePath)
    if count == 0:
        if spriteSetItem.boneIndex != 0:
            context.Error(spriteSetItem, 'boneIndex is not zero, but the owner is not skinned')
    elif spriteSetItem.boneIndex >= count:
        context.Error(spriteSetItem, 'invalid boneIndex, the owner has only %s bones' % count)


@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullSpriteSet(spriteSet)')
def ValidateEveSOFDataHullSpriteSet(context, owner, spriteSet):
    if not owner.isSkinned and spriteSet.skinned:
        context.Error(spriteSet, 'Parent hull is not animated, but spriteset is: ' + str(spriteSet.name))
    if any((c.isupper() for c in spriteSet.visibilityGroup)):
        context.Error(spriteSet, 'No upper case letters in visibilityGroup!')


@Validate('EveSOFDataHullSpriteSet(spriteSet)/.../EveSOFDataHullSpriteSetItem(item)')
def ValidateEveSOFDataHullNonSkinnedBoneIndicies(context, spriteSet, item):
    if not spriteSet.skinned and item.boneIndex > 0:
        context.Error(item, 'Parent spriteset is not skinned and spritesetItem has a boneIndex')


@Validate('List[EveSOFDataHullSpriteSet]')
def ValidateSofSpriteSets(context, spriteSets):
    context.Expect(spriteSets, None, ListAttributesAreDistinct('name'))
    context.Expect(spriteSets, None, ListAttributesAreDistinct('items'))


@Validate('EveSOFDataHullSpriteSet')
def SofSpriteSetIsNotEmpty(context, spriteSets):
    if not spriteSets.items:
        context.Error(spriteSets, 'Sprite set it empty')


@Validate('EveSpriteSet')
def SpriteSetDisplay(context, spriteSet):
    if not spriteSet.display and not context.IsBoundAsDestination(spriteSet, 'display'):
        context.Error(spriteSet, 'display is off - sprite set is invisible')


@Validate('EveSpriteSet')
def SpriteSetMustHaveSprites(context, spriteSet):
    if not spriteSet.sprites:
        context.Error(spriteSet, 'has no sprites', actions=(DeleteTopAction(context, True),))


@Validate('EveSpriteSet')
def SpriteSetMustHaveEffect(context, spriteSet):
    if not spriteSet.effect:
        context.Error(spriteSet, 'has no effect')


@Validate('EveSpaceObject2(owner)/List/EveSpriteSet(spriteSet)')
def SpriteSkinnedCorrespondsToOwner(context, owner, spriteSet):
    mesh = owner.mesh
    isSkinned = IsMeshSkinned(context, mesh)
    if isSkinned is None or isSkinned:
        return
    if isSkinned != spriteSet.skinned:
        context.Error(spriteSet, 'is %sskinned, while the owner space object is %sskinned' % ('' if spriteSet.skinned else 'non-', '' if isSkinned else 'non-'))


@Validate('EveSpriteSet')
def SpriteSetIntensityIsOne(context, spriteSet):
    if not context.IsBoundAsDestination(spriteSet, 'intensity') and spriteSet.intensity != 1:
        context.Error(spriteSet, 'intensity must be set at 1.0')


@Validate('EveSpriteSetItem')
def SpriteSetItemColorIsValid(context, item):
    if any((x < 0 for x in item.color)):
        context.Error(item, 'color is negative')
    if item.color[0:3] == (0, 0, 0):
        context.Error(item, 'color is black')


@Validate('EveSpriteSetItem')
def SpriteSetItemWarpColorIsValid(context, item):
    if any((x < 0 for x in item.warpColor)):
        context.Error(item, 'warpColor is negative')


@Validate('EveSpriteSetItem')
def SpriteSetItemScaleIsValid(context, item):
    if item.minScale == 0 and item.maxScale == 0:
        context.Error(item, 'min and max scale are zero')


@Validate('EveSpaceObject2(owner)/List/EveSpriteSet/.../EveSpriteSetItem(item)')
def SpriteSetItemBoneIndexIsValid(context, owner, item):
    mesh = owner.mesh
    if not mesh or not mesh.geometryResPath:
        return
    count = GetMeshBoneCount(context, mesh)
    if count == 0:
        if item.boneIndex != 0:
            context.Error(item, 'boneIndex is not zero, but the owner is not skinned')
    elif item.boneIndex >= count:
        context.Error(item, 'invalid boneIndex, the owner has only %s bones' % count)


@Validate('EveChildMesh(owner)/List/EveSpriteSet/.../EveSpriteSetItem(item)')
def ChildMeshSpriteSetItemBoneIndexIsValid(context, owner, item):
    mesh = owner.mesh
    if not mesh or not mesh.geometryResPath:
        return
    count = GetMeshBoneCount(context, mesh)
    if count == 0:
        if item.boneIndex != 0:
            context.Error(item, 'boneIndex is not zero, but the owner is not skinned')
    elif item.boneIndex >= count:
        context.Error(item, 'invalid boneIndex, the owner has only %s bones' % count)
