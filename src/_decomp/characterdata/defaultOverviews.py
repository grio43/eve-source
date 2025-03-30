#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterdata\defaultOverviews.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import defaultOverviewsLoader
except ImportError:
    defaultOverviewsLoader = None

class DefaultOverviewsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/defaultOverviews.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/defaultOverviews.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/defaultOverviews.fsdbinary'
    __loader__ = defaultOverviewsLoader


DEFAULT_PRESET = 'default'
DEFAULT_TAB_NAMES = ['default', 'defaultmining', 'defaultwarpto']

def _get_default_overviews():
    return DefaultOverviewsLoader.GetData()


def iter_default_overviews():
    for default_overview_id, data in _get_default_overviews().iteritems():
        yield (default_overview_id, data)


def get_all_overviews():
    return [ {'default_overview_id': default_overview_id,
     'overview_name_id': do.overviewNameID,
     'overview_short_name': do.overviewShortName,
     'default_overview_groups': do.defaultOverviewGroups} for default_overview_id, do in iter_default_overviews() ]


def get_default_overview(default_overview_id):
    return _get_default_overviews()[default_overview_id]


def default_overview_exists(default_overview_id):
    return default_overview_id in _get_default_overviews()


def get_default_overview_groups(default_overview_id):
    return get_default_overview(default_overview_id).defaultOverviewGroups


def get_default_overview_name(default_overview_id, default_overview = None, language_id = None):
    if not default_overview:
        default_overview = get_default_overview(default_overview_id)
    return _get_message(default_overview.overviewNameID, language_id=language_id)


def _get_message(message_id, language_id = None):
    import localization
    return localization.GetByMessageID(message_id, language_id=language_id)


def get_default_preset():
    return DEFAULT_PRESET


def _get_default_tab_for_default_preset(default_preset_name):
    for default_overview_id, default_overview in iter_default_overviews():
        if default_overview.overviewShortName == default_preset_name:
            return {'name': get_default_overview_name(default_overview_id),
             'color': None,
             'overviewPreset': default_preset_name,
             'bracketPreset': None}

    return {}


def get_default_tabs():
    return {tab_id:_get_default_tab_for_default_preset(default_preset_name) for tab_id, default_preset_name in enumerate(DEFAULT_TAB_NAMES)}
