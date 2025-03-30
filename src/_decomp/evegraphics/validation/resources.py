#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\resources.py
import blue
import greatergranny
import imageutils
import trinity

class ResourceType(object):
    BITMAP = 0
    GRANNY = 1
    OBJECT = 2
    TEXTURE_ANIMATION = 3


def GetResource(context, path, resourceType):
    path = blue.paths.ResolvePath(path)
    key = ('resource', path.lower(), resourceType)
    if key in context.cache:
        return context.cache[key]
    if resourceType == ResourceType.BITMAP:
        result = trinity.Tr2HostBitmap()
        result.CreateFromFile(path)
        if not result.IsValid():
            result = None
    elif resourceType == ResourceType.GRANNY:
        try:
            result = greatergranny.GrannyFile(blue.paths.ResolvePath(blue.paths.ResolvePath(path)))
        except IOError:
            result = None

    else:
        if resourceType == ResourceType.OBJECT:
            return blue.resMan.LoadObject(path)
        if resourceType == ResourceType.TEXTURE_ANIMATION:
            try:
                result = imageutils.load_vta_info(path)
            except (imageutils.ImageIOError, IOError):
                result = None

        else:
            raise ValueError('invalid resource type')
    context.cache[key] = result
    return result
