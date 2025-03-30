#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\spriteLineSetValidation.py
from evegraphics.validation.commonUtilities import Validate
from evegraphics.validation.validationFunctions import ListIsNotEmpty, ShouldBeGreaterThan, ListAttributesAreDistinct

@Validate('EveSOFDataHullSpriteLineSetItem')
def ValidateEveSOFDataHullSpriteLineSetItem(context, spriteLineSetItem):
    context.ExpectAny(spriteLineSetItem, 'scaling', ShouldBeGreaterThan(1), 'has only one light')


@Validate('EveSOFDataHullSpriteLineSet')
def ValidateEveSOFDataHullSpriteLineSet(context, spriteLineSet):
    context.Expect(spriteLineSet, 'items', ListIsNotEmpty)
    if any((c.isupper() for c in spriteLineSet.visibilityGroup)):
        context.Error(spriteLineSet, 'No upper case letters in visibilityGroup!')


@Validate('List[EveSOFDataHullSpriteLineSet]')
def ValidateListOfEveSOFDataHullSpriteLineSet(context, spriteLineSets):
    context.Expect(spriteLineSets, None, ListAttributesAreDistinct('name'))
    context.Expect(spriteLineSets, None, ListAttributesAreDistinct('items'))


@Validate('EveSOFDataHullSpriteLineSet')
def SofSpriteLineSetIsNotEmpty(context, spriteSets):
    if not spriteSets.items:
        context.Error(spriteSets, 'Sprite line set it empty')
