#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\textureValidation.py
import os
import blue
import trinity
from trinity import effects
from evegraphics.validation.commonUtilities import Validate, IsContent
from evegraphics.validation.validationFunctions import ValidateTexturePath
from evegraphics.validation import resources
_effectCache = {}

@Validate('EveSOFDataTexture', IsContent)
def ValidateEveSOFDataTexture(context, texture):
    ValidateTexturePath(context, texture, 'resFilePath', context.GetArgument(IsContent) == IsContent.CONTENT)


SUFFIXES = {'AlbedoMap': 'a',
 'NormalMap': 'n',
 'GlowMap': 'g',
 'RoughnessMap': 'r',
 'PaintMaskMap': 'p3',
 'AoMap': 'o',
 'MaterialMap': 'm'}

@Validate('EveSOFDataTexture', IsContent)
def ValidateEveSOFDataTextureSuffix(context, texture):
    if texture.resFilePath and texture.name in SUFFIXES:
        splitname = os.path.splitext(texture.resFilePath)[0].rsplit('_', 1)
        if len(splitname) == 1:
            return None
        suffix = splitname[-1].lower()
        if suffix != SUFFIXES[texture.name]:
            context.Error(texture, 'Texture suffix for %s sould be "%s"' % (texture.name, SUFFIXES[texture.name]))


@Validate('=TriTextureParameter', IsContent)
def ValidTexturePathForContent(context, texture):
    ValidateTexturePath(context, texture, 'resourcePath', context.GetArgument(IsContent) == IsContent.CONTENT)


def _GetTextureType(context, path):
    if path.lower().endswith('.vta'):
        return trinity.TEXTURE_TYPE.TEX_TYPE_3D
    elif not path.lower().endswith('.dds'):
        return trinity.TEXTURE_TYPE.TEX_TYPE_2D
    bmp = resources.GetResource(context, path, resources.ResourceType.BITMAP)
    if not bmp:
        return None
    else:
        return bmp.imageType


def _ValidateTextureType(context, texture, resourcePath, effect):
    if not blue.paths.exists(resourcePath):
        return
    resources = effects.GetPublicResources(effect, _effectCache)
    if texture.name in resources:
        have = _GetTextureType(context, resourcePath)
        expected = resources[texture.name].constant.type
        if have != expected:
            names = {trinity.TEXTURE_TYPE.TEX_TYPE_1D: '1D',
             trinity.TEXTURE_TYPE.TEX_TYPE_2D: '2D',
             trinity.TEXTURE_TYPE.TEX_TYPE_3D: 'volume',
             trinity.TEXTURE_TYPE.TEX_TYPE_CUBE: 'cube',
             None: 'unknown'}
            context.Error(texture, 'texture is a %s texture, while the shader expects a %s texture' % (names.get(have, 'unknown'), names.get(expected, 'unknown')))


@Validate('Tr2Effect(effect)/.../=TriTextureParameter(texture)')
def ValidTextureType(context, effect, texture):
    if not blue.paths.exists(texture.resourcePath):
        return
    _ValidateTextureType(context, texture, texture.resourcePath, effect)
