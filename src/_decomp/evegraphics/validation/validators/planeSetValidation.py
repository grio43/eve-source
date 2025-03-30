#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\planeSetValidation.py
from evegraphics.validation.commonUtilities import Validate, IsContent
from evegraphics.validation.validationFunctions import ListAttributesAreDistinct
from evegraphics.validation.validationFunctions import ValidateTexturePath

@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullPlaneSet(planeSet)')
def ValidateEveSOFDataHullPlaneSet(context, owner, planeSet):
    if not owner.isSkinned:
        if planeSet.skinned:
            context.Error(planeSet, 'Parent hull is not animated, but planeSet is: ' + str(planeSet.name))
    if planeSet.atlasSize == 0:
        context.Error(planeSet, 'atlasSize should never be zero! Please put it at least to 1' + str(planeSet.name))


@Validate('EveSOFDataHullPlaneSet(owner)/.../EveSOFDataHullPlaneSetItem(item)')
def ValidateEveSOFDataHullPlaneSet(context, owner, item):
    if item.maskMapAtlasIndex >= owner.atlasSize * owner.atlasSize:
        context.Error(item, 'maskMapAtlasIndex ' + str(item.maskMapAtlasIndex) + ' outside of atlas size ' + str(owner.atlasSize))


@Validate('List[EveSOFDataHullPlaneSet]')
def ValidateListOfEveSOFDataHullPlaneSet(context, planeSets):
    context.Expect(planeSets, None, ListAttributesAreDistinct('name'))
    context.Expect(planeSets, None, ListAttributesAreDistinct('items'))


@Validate('EveSOFDataHullPlaneSet')
def SofPlaneSetIsNotEmpty(context, spriteSets):
    if not spriteSets.items:
        context.Error(spriteSets, 'Plane set it empty')


@Validate('EveSOFDataHullPlaneSet', IsContent)
def ValidateEveSOFDataHullPlaneSetTextures(context, planeSet):
    ValidateTexturePath(context, planeSet, 'layer1MapResPath', context.GetArgument(IsContent) == IsContent.CONTENT)
    ValidateTexturePath(context, planeSet, 'layer2MapResPath', context.GetArgument(IsContent) == IsContent.CONTENT)
    ValidateTexturePath(context, planeSet, 'maskMapResPath', context.GetArgument(IsContent) == IsContent.CONTENT)
