#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\factionValidation.py
from evegraphics.validation.commonUtilities import Validate, IsContent
from evegraphics.validation.validationFunctions import ListAttributesAreDistinct, VisibilityGroupIsValid

@Validate('EveSOFDataFaction')
def ValidateSofFaction(context, faction):
    pass


@Validate('EveSOFDataFactionColorSet')
def ValidateSofFactionColorSet(context, colorset):
    for m in colorset.__members__:
        a = getattr(colorset, m)
        if a is not None and isinstance(a, tuple) and m != 'Black':
            if a[:3] == (0.0, 0.0, 0.0):
                context.Error(colorset, 'Black color in faction colorset found! Why?')


@Validate('EveSOFDataLogoSet')
def ValidateSofDataLogoSet(context, logoSet):
    neededTextureNames = ['DecalRoughnessMap',
     'DecalFresnelMap',
     'DecalNormalMap',
     'DecalAlbedoMap',
     'DecalTransparencyMap']
    _ValidateLogoSet(context, logoSet, neededTextureNames)


def _ValidateLogoSet(context, logoSet, neededTextureNames):
    if logoSet is not None:
        logoSubSets = ['Primary',
         'Secondary',
         'Tertiary',
         'Marking_01',
         'Marking_02']
        for attribute in logoSubSets:
            logo = getattr(logoSet, attribute)
            if logo is None:
                continue
            for texture in logo.textures:
                if texture.name not in neededTextureNames:
                    context.Error(logo, "Logo '%s' has an incorrect texture name '%s'" % (attribute, texture.name))


def _LowerCasify(visibilityGroup):

    def inner():
        visibilityGroup.str = visibilityGroup.str.lower()

    return ('Convert to Lower Case', inner, True)


@Validate('EveSOFDataFactionVisibilityGroupSet')
def ValidateSofFactionVisibilityGroupSet(context, visgroupset):
    context.Expect(visgroupset.visibilityGroups, None, ListAttributesAreDistinct('str'))
    for vg in visgroupset.visibilityGroups:
        if any((c.isupper() for c in vg.str)):
            context.Error(visgroupset, 'No upper case letters in visibilityGroup!', actions=[_LowerCasify(vg)])
        if not VisibilityGroupIsValid(context, vg.str):
            context.Error(visgroupset, 'Visibility "%s" does not exist' % vg.str)
