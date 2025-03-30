#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\common\util.py
import datetime
import datetimeutils
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import seasonSelectionLoader
except ImportError:
    seasonSelectionLoader = None

def parse_date_from_blue_to_datetime(windows_filetime):
    return datetimeutils.filetime_to_datetime(windows_filetime).replace(hour=11, minute=0, second=0, microsecond=0)


def is_current(start_date, end_date):
    return start_date <= datetime.date.today() < end_date


class SeasonSelectionLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/seasonSelection.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/seasonSelection.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/seasonSelection.fsdbinary'
    __loader__ = seasonSelectionLoader


def get_multiple_seasons_fsd():
    return SeasonSelectionLoader.GetData()
