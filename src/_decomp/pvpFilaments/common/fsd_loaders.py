#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pvpFilaments\common\fsd_loaders.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import pvpFilamentMatchTypesLoader
    import pvpFilamentEventDatesLoader
except ImportError:
    pvpFilamentMatchTypesLoader = None
    pvpFilamentEventDatesLoader = None

class PVPFilamentMatchTypesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/pvpFilamentMatchTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/pvpFilamentMatchTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/pvpFilamentMatchTypes.fsdbinary'
    __loader__ = pvpFilamentMatchTypesLoader


class PVPFilamentEventDatesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/pvpFilamentEventDates.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/pvpFilamentEventDates.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/pvpFilamentEventDates.fsdbinary'
    __loader__ = pvpFilamentEventDatesLoader


def get_match_types():
    return PVPFilamentMatchTypesLoader.GetData()


def get_event_dates():
    return PVPFilamentEventDatesLoader.GetData()
