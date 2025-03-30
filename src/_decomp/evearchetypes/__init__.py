#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evearchetypes\__init__.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import archetypesLoader
except ImportError:
    archetypesLoader = None

class Archetypes(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/archetypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/archetypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/archetypes.fsdbinary'
    __loader__ = archetypesLoader


def GetArchetypes():
    return Archetypes.GetData()


def GetArchetype(archetypeID):
    return Archetypes.GetData().get(archetypeID, None)


def GetArchetypeName(archetypeID):
    archetype = GetArchetype(archetypeID)
    if archetype:
        return archetype.archetypeName
    return ''


def GetArchetypeTitle(archetypeID):
    archetype = GetArchetype(archetypeID)
    try:
        return archetype.titleID
    except AttributeError:
        return None


def GetArchetypeDescription(archetypeID):
    archetype = GetArchetype(archetypeID)
    try:
        return archetype.descriptionID
    except AttributeError:
        return None
