#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\metaGroups\data.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import localization
except ImportError:
    localization = None

try:
    import metaGroupsLoader
except ImportError:
    metaGroupsLoader = None

class MetaGroups(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/metaGroups.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/metaGroups.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/metaGroups.fsdbinary'
    __loader__ = metaGroupsLoader


def exists(meta_group_id):
    return meta_group_id in _get_meta_groups()


def iter_meta_group_ids():
    return _get_meta_groups().iterkeys()


def get_name(meta_group_id):
    if meta_group_id is None:
        return ''
    meta_group = _get_meta_groups()[meta_group_id]
    return localization.GetByMessageID(meta_group.nameID)


def get_description(meta_group_id):
    if meta_group_id is None:
        return ''
    meta_group = _get_meta_groups()[meta_group_id]
    return localization.GetByMessageID(meta_group.descriptionID)


def get_color(meta_group_id):
    if meta_group_id is None:
        return
    meta_group = _get_meta_groups()[meta_group_id]
    return meta_group.color


def get_icon_id(meta_group_id):
    meta_group = _get_meta_groups().get(meta_group_id)
    return meta_group.iconID


def _get_meta_groups():
    return MetaGroups.GetData()
