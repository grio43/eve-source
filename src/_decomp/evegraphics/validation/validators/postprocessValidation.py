#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\postprocessValidation.py
from evegraphics.validation.commonUtilities import Validate, IsContent
from evegraphics.validation.validationFunctions import ValidateTexturePath

@Validate('Tr2PPGodRaysEffect', IsContent)
def ProcessGodRaysTextures(context, item):
    ValidateTexturePath(context, item, 'noiseTexturePath', context.GetArgument(IsContent) == IsContent.CONTENT)


@Validate('Tr2PPBloomEffect', IsContent)
def ProcessBloomTextures(context, item):
    ValidateTexturePath(context, item, 'grimePath', context.GetArgument(IsContent) == IsContent.CONTENT)


@Validate('Tr2PPLutEffect', IsContent)
def ProcessLutTextures(context, item):
    ValidateTexturePath(context, item, 'path', context.GetArgument(IsContent) == IsContent.CONTENT)


@Validate('Tr2PPVignetteEffect', IsContent)
def ProcessVignetteTextures(context, item):
    ValidateTexturePath(context, item, 'shapePath', context.GetArgument(IsContent) == IsContent.CONTENT)
    ValidateTexturePath(context, item, 'detailPath', context.GetArgument(IsContent) == IsContent.CONTENT)
