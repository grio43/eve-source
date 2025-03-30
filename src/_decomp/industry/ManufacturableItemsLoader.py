#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\industry\ManufacturableItemsLoader.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import manufacturableItemsLoader
except ImportError:
    manufacturableItemsLoader = None

class ManufacturableItems(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/manufacturableItems.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/manufacturableItems.fsdbinary'
    __loader__ = manufacturableItemsLoader


def get_data():
    return ManufacturableItems.GetData()


def is_manufacturable_item(type_id):
    return type_id in get_data()['ManufacturableItems']
