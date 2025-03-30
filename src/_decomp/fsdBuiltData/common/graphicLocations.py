#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\graphicLocations.py
try:
    import graphicLocationsLoader
except ImportError:
    graphicLocationsLoader = None

from fsdBuiltData.common.base import BuiltDataLoader
import logging
log = logging.getLogger(__file__)

class GraphicLocations(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/graphicLocations.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/graphicLocations.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/graphicLocations.fsdbinary'
    __loader__ = graphicLocationsLoader


def GetGraphicLocationDictionary():
    return GraphicLocations.GetData()


def GetGraphicLocation(graphicLocationID):
    return GraphicLocations.GetData().get(graphicLocationID, None)


def GetGraphicLocationAttribute(graphicLocationID, attributeName, default = None):
    if isinstance(graphicLocationID, (int, long)):
        item = getattr(GetGraphicLocation(graphicLocationID), attributeName, None) or default
        return item
    return getattr(graphicLocationID, attributeName, None) or default


def GetLocators(graphicLocationID, default = None):
    return GetGraphicLocationAttribute(graphicLocationID, 'locators', default)


def GetDirectionalLocators(graphicLocationID, default = None):
    return GetGraphicLocationAttribute(graphicLocationID, 'directionalLocators', default)


def GetDirectionalLocatorForCategory(graphicLocationID, category, locator_name):
    for location in GetDirectionalLocators(graphicLocationID, default=[]):
        if location.category == category and location.name == locator_name:
            return location
