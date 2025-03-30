#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\normalMapValidation.py
import os
from evegraphics.validation.commonUtilities import Validate
import evegraphics.validation.resources as resources
_FILE_ENDINGS = ['.ZH', '']

def GetRegionPath(path, suffix = '.zh'):
    base, ext = os.path.splitext(path)
    return base + suffix + ext


def shouldValidateMap(context, path):
    key = ('normalMapPath', path)
    if key in context.cache:
        return False
    else:
        context.cache[key] = 1
        return True


@Validate('EveSOFDataTexture')
def ValidateNormalMaps(context, t):
    if 'NormalMap' in t.name and shouldValidateMap(context, t.name):
        for ext in _FILE_ENDINGS:
            path = GetRegionPath(t.resFilePath, ext)
            tmap = resources.GetResource(context, path, resources.ResourceType.BITMAP)
            if not tmap:
                continue
            foundZero = tmap.CountPixelsOfValue('rgb', 0)
            if foundZero:
                context.Error(t, 'texture %s contains a zero-valued pixel' % path)
