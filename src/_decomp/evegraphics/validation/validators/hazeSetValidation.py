#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\hazeSetValidation.py
from evegraphics.validation.commonUtilities import Validate
from evegraphics.validation.validators.meshValidation import GetGrannyBoneCount

@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullHazeSet(hazeSet)/EveSOFDataHullHazeSetItem(hazeSetItem)')
def ValidateSofHazeSetItemSkinning(context, owner, hazeSet, hazeSetItem):
    count = GetGrannyBoneCount(context, owner.geometryResFilePath)
    if count == 0:
        if hazeSetItem.boneIndex > -1:
            context.Error(hazeSetItem, 'Haze set has a boneIndex, but the hull is un-skinned', actions=[_RemoveHazeSetItemBoneIndex(hazeSetItem)])
    elif hazeSetItem.boneIndex >= count:
        context.Error(hazeSetItem, 'invalid boneIndex %s, the hull has only %s bones' % (hazeSetItem.boneIndex, count))


@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullHazeSet(hazeSet)')
def ValidateSofHazeSetSkinning(context, owner, hazeSet):
    count = GetGrannyBoneCount(context, owner.geometryResFilePath)
    if count == 0 and hazeSet.skinned:
        context.Error(hazeSet, 'is skinned, but the hull is un-skinned', actions=[_SetHazeSetSkinned(hazeSet, False)])


@Validate('EveSOFDataHullHazeSet(hazeSet)')
def ValidateSofHazeSetSkinningConsistency(context, hazeSet):
    for hazeSetItem in hazeSet.items:
        if hazeSet.skinned and hazeSetItem.boneIndex == -1:
            context.Error(hazeSetItem, 'has an unset boneIndex but hazeSet is set as skinned')
        elif not hazeSet.skinned and hazeSetItem.boneIndex > -1:
            context.Error(hazeSetItem, 'has a boneIndex but hazeSet is set as un-skinned')


@Validate('EveSOFDataHullHazeSet(hazeSet)')
def ValidateSofHazeSet(context, hazeSet):
    if len(hazeSet.items) == 0:
        context.Error(hazeSet, 'is empty')


def _SetHazeSetSkinned(hazeSet, newSkinnedValue):

    def inner():
        hazeSet.skinned = newSkinnedValue
        return True

    return ('Set as %s' % ['un-skinned', 'skinned'][newSkinnedValue], inner, True)


def _RemoveHazeSetItemBoneIndex(hazeSetItem):

    def inner():
        hazeSetItem.boneIndex = -1
        return True

    return ("Remove 'boneIndex'", inner, True)
