#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\patternValidation.py
from evegraphics.validation.commonUtilities import Validate, IsContent
from evegraphics.validation.resources import GetResource, ResourceType
import threadutils
import blue

@threadutils.Memoize
def GetContentHullNames():
    import os
    hulls = []
    root = blue.paths.ResolvePath('res:/dx9/model')
    for root, dirs, files in os.walk(root):
        for filePath in files:
            if filePath.startswith('sofhull_') and filePath.endswith('.red'):
                hulls.append(filePath.replace('sofhull_', '').replace('.red', ''))

    return hulls


@threadutils.Memoize
def GetClientHullNames():
    return [ each.name for each in blue.resMan.LoadObject('res:/dx9/model/spaceobjectfactory/data.red').hull ]


@Validate('EveSOFDataPattern', IsContent)
def ValidateLayerCountConsistency(context, pattern):
    if context.GetArgument(IsContent) == IsContent.CONTENT:
        hulls = GetContentHullNames()
    else:
        hulls = GetClientHullNames()
    layerCount = 0
    layerCount += 1 if pattern.layer1 is not None else 0
    layerCount += 1 if pattern.layer2 is not None else 0
    for proj in pattern.projections:
        c = 0
        c += 1 if proj.transformLayer1 is not None else 0
        c += 1 if proj.transformLayer2 is not None else 0
        if layerCount != c:
            context.Error(proj, 'Different layer count on ' + str(proj.name))
        if proj.name not in hulls:
            context.Error(proj, 'No hull named ' + str(proj.name))


@Validate('EveSOFDataPattern')
def ValidatePatternName(context, pattern):
    if not pattern.name.islower() or ' ' in pattern.name:
        context.Error(pattern, "name '%s' should be lowercase and have no spaces" % pattern.name, actions=[_ForceCorrectName(pattern)])


def _ForceCorrectName(pattern):

    def inner():
        pattern.name = pattern.name.lower().replace(' ', '')
        return True

    return ('Force lowercase and delete spaces', inner, True)


@Validate('EveSOFDataPatternLayer(layer)')
def TextureExists(context, layer):
    if not blue.paths.exists(layer.textureResFilePath):
        context.Error(layer, "Texture %s doesn't exist." % layer.textureResFilePath)
    res = GetResource(context, layer.textureResFilePath, ResourceType.BITMAP)
    if res is None:
        context.Error(layer, 'Could not load ' + layer.textureResFilePath)
    elif res.width * res.height > 262144:
        context.Error(layer, 'Pattern texture ' + layer.textureResFilePath + ' is too big! Max allowed is the multiplication of 512x512')
