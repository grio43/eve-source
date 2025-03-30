#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\client\environmentTemplates.py
from carbon.common.lib import telemetry
from fsdBuiltData.common.base import BuiltDataLoader
import evetypes
STATIC_PARTICLE_FIELD = 'staticParticleField'
CLOUD_FIELD = 'cloudField'
DISTANCE_FIELD = 'distanceField'
POST_PROCESS = 'postProcess'
ENVIRONMENT_AUDIO = 'audioTriggers'
IS_SYSTEM_WIDE = 'isSystemWide'
CAMERA_ATTACHMENTS = 'cameraAttachments'
NEBULA_OVERRIDES = 'nebulaOverrides'
GRAPHIC_ID_ATTACHMENTS = 'graphicIDAttachments'
EXAMPLE_USAGE_UNKNOWN = 0
EXAMPLE_USAGE_SPAWNABLE = 1
EXAMPLE_USAGE_LOCATION = 2
EXAMPLE_USAGE_DUNGEON = 3
EXAMPLE_USAGE_ABYSS = 4
AVAILABLE_ATTRIBUTES = [DISTANCE_FIELD,
 STATIC_PARTICLE_FIELD,
 CLOUD_FIELD,
 POST_PROCESS,
 ENVIRONMENT_AUDIO,
 CAMERA_ATTACHMENTS,
 NEBULA_OVERRIDES,
 GRAPHIC_ID_ATTACHMENTS]
INCURSION_ENVIRONMENT_TEMPLATE_ID = 2
SHATTERED_WORMHOLE_ENVIRONMENT_TEMPLATE_ID = 3
INVASION_ENVIRONMENT_TEMPLATE_CORE_ID = 124
INVASION_ENVIRONMENT_TEMPLATE_NEIGHBOURHOOD_ID = 125
INVASION_ENVIRONMENT_TEMPLATE_FRINGE_ID = 126
try:
    import environmentTemplateAnchorTypeIDsLoader
except ImportError:
    environmentTemplateAnchorTypeIDsLoader = None

class EnvironmentTemplateAnchorTypeIDs(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/environmentTemplateAnchorTypeIDs.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/environmentTemplateAnchorTypeIDs.fsdbinary'
    __loader__ = environmentTemplateAnchorTypeIDsLoader


try:
    import environmentTemplateAnchorGroupIDsLoader
except ImportError:
    environmentTemplateAnchorGroupIDsLoader = None

class EnvironmentTemplateAnchorGroupIDs(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/environmentTemplateAnchorGroupIDs.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/environmentTemplateAnchorGroupIDs.fsdbinary'
    __loader__ = environmentTemplateAnchorGroupIDsLoader


try:
    import environmentTemplateAnchorCategoryIDsLoader
except ImportError:
    environmentTemplateAnchorCategoryIDsLoader = None

class EnvironmentTemplateAnchorCategoryIDs(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/environmentTemplateAnchorCategoryIDs.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/environmentTemplateAnchorCategoryIDs.fsdbinary'
    __loader__ = environmentTemplateAnchorCategoryIDsLoader


try:
    import environmentTemplatesLoader
except ImportError:
    environmentTemplatesLoader = None

class EnvironmentTemplates(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/environmentTemplates.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/environmentTemplates.fsdbinary'
    __loader__ = environmentTemplatesLoader
    __typeTemplateCache__ = {}
    __templateCache__ = {}
    __cacheReady__ = False

    @classmethod
    def CacheTemplates(cls):
        cls.__cacheReady__ = False
        cls.__typeTemplateCache__ = {}
        cls.__templateCache__ = {}
        environmentTemplates = cls.GetData()
        cls.__typeTemplateCache__.update(EnvironmentTemplateAnchorTypeIDs.GetData())
        for groupID, templateID in EnvironmentTemplateAnchorGroupIDs.GetData().iteritems():
            cls.__typeTemplateCache__.update({typeID:templateID for typeID in evetypes.GetTypeIDsByGroup(groupID)})

        for categoryID, templateID in EnvironmentTemplateAnchorCategoryIDs.GetData().iteritems():
            cls.__typeTemplateCache__.update({typeID:templateID for typeID in evetypes.GetTypeIDsByCategory(categoryID)})

        for templateID, template in environmentTemplates.iteritems():
            cls.__templateCache__[templateID] = template

        cls.__cacheReady__ = True

    @classmethod
    def GetTemplateID(cls, typeID):
        if not cls.__cacheReady__:
            cls.CacheTemplates()
        return cls.__typeTemplateCache__.get(typeID, None)

    @classmethod
    def GetTemplate(cls, templateID):
        if not cls.__cacheReady__:
            cls.CacheTemplates()
        return cls.__templateCache__[templateID]


def GetEnvironmentTemplateBaseObject():
    return EnvironmentTemplates.GetData()


def GetEnvironmentTemplates():
    return EnvironmentTemplates.GetData()


def GetEnvironmentTemplate(environmentTemplateID):
    try:
        return EnvironmentTemplates.GetTemplate(environmentTemplateID)
    except KeyError:
        return None


def GetEnvironmentTemplateAttribute(environmentTemplateID, attributeName, default = None):
    if isinstance(environmentTemplateID, (int, long)):
        template = GetEnvironmentTemplate(environmentTemplateID)
    else:
        template = environmentTemplateID
    authoredValue = getattr(template, attributeName)
    if authoredValue is not None:
        return authoredValue
    return default


def GetActivationRadius(environmentTemplateID):
    return GetEnvironmentTemplateAttribute(environmentTemplateID, 'activationRadius')


def IsSystemWide(environmentTemplateID):
    return GetEnvironmentTemplateAttribute(environmentTemplateID, 'isSystemWide', False)


def GetAllSubEnvironmentTypeIDs():
    subEnvironmentTypes = []
    for templateID in GetEnvironmentTemplates():
        subEnvironmentTypes.extend([ tid for tid in GetSubEnvironmentTypeIDs(templateID) ])

    return list(set(subEnvironmentTypes))


def HasAssociatedTemplateID(typeID, materialSetID):
    return GetTemplateID(typeID, materialSetID) is not None


@telemetry.ZONE_METHOD
def GetTemplateID(typeID, materialSetID):
    templateMapping = EnvironmentTemplates.GetTemplateID(typeID)
    if templateMapping is None:
        return
    overrides = templateMapping.overrides or {}
    if materialSetID in overrides:
        return templateMapping.overrides[materialSetID]
    try:
        return templateMapping.baseEnvironment
    except AttributeError:
        return


def GetDescription(environmentTemplateID):
    return GetEnvironmentTemplateAttribute(environmentTemplateID, 'description', '')


def GetSubEnvironmentTypeIDs(environmentTemplateID):
    return GetEnvironmentTemplateAttribute(environmentTemplateID, 'subEnvironmentTypeIDs', [])


def GetAllEnvironmentModifiers(environmentTemplate):
    return {attribute:getattr(environmentTemplate, attribute) for attribute in AVAILABLE_ATTRIBUTES if getattr(environmentTemplate, attribute) is not None}
