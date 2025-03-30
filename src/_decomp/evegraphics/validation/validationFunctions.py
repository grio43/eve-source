#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validationFunctions.py
import os
import re
import blue
import trinity
from evegraphics.validation import resources
from evegraphics.validation.commonUtilities import AreEqual
from evegraphics.validation.errors import MultipleObjectValidationError, MultipleValidationErrors
from evegraphics.validation.resources import GetResource, ResourceType

def ShouldBeLessThan(threshold):

    def _ShouldBeLessThan(actualValue, message = None):
        thresholdType = type(threshold)
        castValue = thresholdType(actualValue)
        if actualValue >= threshold:
            raise AssertionError(message or "should be less than '%s' but is cast to '%s' (actual value '%s')" % (threshold, castValue, actualValue))

    return _ShouldBeLessThan


def ShouldBeLessThanOrEqual(threshold):

    def _ShouldBeLessThanOrEqual(actualValue, message = None):
        thresholdType = type(threshold)
        castValue = thresholdType(actualValue)
        if actualValue > threshold:
            raise AssertionError(message or "should be less than or equal to '%s' but is cast to '%s' (actual value '%s')" % (threshold, castValue, actualValue))

    return _ShouldBeLessThanOrEqual


def ShouldBeGreaterThan(threshold):

    def _ShouldBeGreaterThan(actualValue, message = None):
        thresholdType = type(threshold)
        castValue = thresholdType(actualValue)
        if castValue <= threshold:
            raise AssertionError(message or "should be greater than '%s' but is cast to '%s' (actual value '%s')" % (threshold, castValue, actualValue))

    return _ShouldBeGreaterThan


def ShouldBeGreaterThanOrEqual(threshold):

    def _ShouldBeGreaterThanOrEqual(actualValue, message = None):
        thresholdType = type(threshold)
        castValue = thresholdType(actualValue)
        if castValue < threshold:
            raise AssertionError(message or "should be greater than or equal to '%s' but is cast to '%s' (actual value '%s')" % (threshold, castValue, actualValue))

    return _ShouldBeGreaterThanOrEqual


def EndsWith(suffix):

    def _EndsWith(actualString, message = None):
        if not actualString.endswith(suffix):
            raise AssertionError(message or "'%s' should end with '%s'" % (actualString, suffix))

    return _EndsWith


def ListIsNotEmpty(listObject, message):
    if len(listObject) == 0:
        raise AssertionError(message or 'is empty')


def ListIsEmpty(listObject, message):
    if len(listObject):
        raise AssertionError(message or 'is not empty')


def ListAttributesAreDistinct(attribute = None, listAttributesToCheck = None, listAttributesToIgnore = None):

    def _ListAttributeIsDistinct(listObject, message):
        if len(listObject) < 2:
            return
        equalThings = {}
        processedThings = []
        for index, o in enumerate(listObject[:-1]):
            if o in processedThings:
                continue
            oToCheck = getattr(o, attribute) if attribute else o
            for o2 in listObject[index + 1:]:
                o2ToCheck = getattr(o2, attribute) if attribute else o2
                if AreEqual(oToCheck, o2ToCheck, listAttributesToCheck, listAttributesToIgnore):
                    if index not in equalThings:
                        equalThings[index] = {o}
                    equalThings[index].add(o2)
                    processedThings.append(o2)

        if len(equalThings) > 0:
            errors = []
            message = message or "have the same attribute '%s'" % attribute if attribute else 'are equal'
            for listOfEqualThings in equalThings.values():
                errors.append(MultipleObjectValidationError(list(listOfEqualThings), message))

            raise MultipleValidationErrors(errors)

    return _ListAttributeIsDistinct


def _FixSlashes(obj, attribute):

    def inner():
        setattr(obj, attribute, getattr(obj, attribute).replace('\\', '/'))
        return True

    return ('Convert \\backslashes to /slashes', inner, True)


_interfaces = {}

def GetInterfaces():
    if not _interfaces:
        for each in blue.classes.GetClassTypes():
            _interfaces[each[0]['classname']] = each[1].keys()

    return _interfaces


def ValidateResPath(context, obj, attribute, extensions = (), allowDynamic = False, pathOverride = None, interfaces = ()):
    if not pathOverride:
        path = getattr(obj, attribute)
    else:
        path = pathOverride
    if not path:
        context.Error(obj, '%s is empty' % attribute)
        return
    if not path.startswith('res:/'):
        if not allowDynamic or not path.startswith('dynamic:/'):
            context.Error(obj, '%s should start with res:/' % attribute)
    if path.find('\\') >= 0:
        context.Error(obj, '%s contains \\backslashes' % attribute, (_FixSlashes(obj, attribute),))
    if extensions:
        if not path.lower().endswith(extensions) and (not allowDynamic or not path.startswith('dynamic:/')):
            context.Error(obj, '%s has invalid extension "%s"' % (attribute, os.path.splitext(path)[1]))
    if not blue.paths.exists(path) and (not allowDynamic or not path.startswith('dynamic:/')):
        context.Error(obj, '%s "%s" does not point to an existing file' % (attribute, path))
    elif path.endswith('.red') and interfaces and path.startswith('res:/'):
        key = ('redInterfaces', path.lower())
        if key in context.cache:
            typeName, hasInterfaces = context.cache[key]
        else:
            typeName = 'Unknown'
            hasInterfaces = ()
            contents = blue.paths.GetFileContentsWithYield(path).read()
            match = re.match('type:\\s+(\\w+).*', contents)
            if match:
                typeName = match.group(1)
                hasInterfaces = GetInterfaces().get(typeName, ())
            context.cache[key] = (typeName, hasInterfaces)
        for each in interfaces:
            if each in hasInterfaces:
                return

        context.Error(obj, 'File %s is of type %s which is not the expected type %s' % (path, typeName, ', '.join(interfaces)))


def _ValidateTextureDimension(context, img, obj, path):

    def createerror(att, value):
        context.Error(obj, '%s: Image %s is not in the power of two. Got size %s.' % (path, att, str(value)))

    if not img.width & img.width - 1 == 0 and img.width != 0:
        createerror('width', img.width)
    if not img.height & img.height - 1 == 0 and img.height != 0:
        createerror('height', img.height)


def ValidateTexturePath(context, obj, attribute, isContent, allowDynamic = True):
    if isContent:
        extensions = ('.tga', '.dds', '.png', '.vta')
    else:
        extensions = ('.dds', '.png', '.vta')
    ValidateResPath(context, obj, attribute, extensions, allowDynamic)
    path = getattr(obj, attribute)
    if not path.lower().endswith(extensions):
        return
    bmp = resources.GetResource(context, path, resources.ResourceType.BITMAP)
    if isContent and path.lower().endswith('.tga') and bmp:
        _ValidateTextureDimension(context, bmp, obj, path)
    if isContent and path.lower().endswith('.dds') and blue.paths.exists(path) and blue.paths.exists(path[:-3] + 'tga'):
        tgaFormats = (trinity.PIXEL_FORMAT.B8G8R8A8_UNORM,
         trinity.PIXEL_FORMAT.B8G8R8X8_UNORM,
         trinity.PIXEL_FORMAT.BC1_UNORM,
         trinity.PIXEL_FORMAT.BC2_UNORM,
         trinity.PIXEL_FORMAT.BC3_UNORM,
         trinity.PIXEL_FORMAT.BC7_UNORM,
         trinity.PIXEL_FORMAT.R8_UNORM)
        if bmp.imageType == trinity.TEXTURE_TYPE.TEX_TYPE_2D and bmp.format in tgaFormats:
            context.Error(obj, '%s: "%s"\n\nDDS texture referenced in content while a tga with the same name exists.\nPlease use the tga. If the offending dds exists in content please remove it.\nIf the dds is only in branch, the content asset needs to point to the content tga.\n\nFull dds path; %s\n' % (attribute, path, blue.paths.ResolvePath(path)))
    if path.lower().endswith('.dds'):
        if bmp:
            if trinity.PIXEL_FORMAT.GetNameFromValue(bmp.format).startswith('BC') and (bmp.width % 4 != 0 or bmp.height % 4 != 0):
                context.Error(obj, '%s: "%s" compressed texture sizes must be multiple of 4' % (attribute, path))
    if isContent and path.lower().endswith('.dds') and not 'scene in obj.resourcePath':
        if bmp.format not in [trinity.PIXEL_FORMAT.BC1_UNORM,
         trinity.PIXEL_FORMAT.BC2_UNORM,
         trinity.PIXEL_FORMAT.BC3_UNORM,
         trinity.PIXEL_FORMAT.BC7_UNORM]:
            if bmp.width > 512 and bmp.height > 512:
                context.Error(obj, '%s: "%s" Uncompressed DDS textures bigger than 512x512 are not allowed in content' % (attribute, path))


def VisibilityGroupIsValid(context, visibilityGroupName):
    genericData = GetResource(context, 'res:/dx9/model/spaceobjectfactory/generic.red', ResourceType.OBJECT)
    for vgroup in genericData.visibilityGroups:
        if vgroup.name == visibilityGroupName:
            return True

    return False
