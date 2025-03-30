#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\data\warzoneMapPositionsDataLoader.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import warZonesPositionDataLoader
except ImportError:
    warZonesPositionDataLoader = None

class WarzoneMapPositionsDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/warZonesPositionData.fsdbinary'
    __loader__ = warZonesPositionDataLoader


def get_frontlines_map_data():
    return WarzoneMapPositionsDataLoader.GetData()
