#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evecorporation\recruitment.py
from collections import defaultdict
from collections import namedtuple
from caching import Memoize
from eveprefs import boot
from localization import GetByMessageID
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import recruitmentGroupsLoader
    import recruitmentTypesLoader
except ImportError:
    recruitmentGroupsLoader = None
    recruitmentTypesLoader = None

RECRUITMENT_GROUP_PRIMARY_LANGUAGE = 10
RecruitmentType = namedtuple('RecruitmentType', ['typeID',
 'groupID',
 'typeMask',
 'typeName',
 'description'])
RecruitmentGroup = namedtuple('RecruitmentGroup', ['groupID', 'groupName', 'description'])

class RecruitmentGroupsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/recruitmentGroups.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/recruitmentGroups.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/recruitmentGroups.fsdbinary'
    __loader__ = recruitmentGroupsLoader


class RecruitmentTypesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/recruitmentTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/recruitmentTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/recruitmentTypes.fsdbinary'
    __loader__ = recruitmentTypesLoader


def _get_types():
    return RecruitmentTypesLoader.GetData()


def _get_groups():
    return RecruitmentGroupsLoader.GetData()


@Memoize
def get_recruitment_types():
    if boot.region == 'optic':
        _types = filter(lambda t: t[1].recruitmentGroupID != RECRUITMENT_GROUP_PRIMARY_LANGUAGE, _get_types().items())
    else:
        _types = _get_types().items()
    return {type_id:_recruitment_type(type_id, type_) for type_id, type_ in _types}


def get_recruitment_type(type_id, default = None):
    return get_recruitment_types().get(type_id, default)


@Memoize
def get_recruitment_groups():
    if boot.region == 'optic':
        groups = filter(lambda g: g[0] != RECRUITMENT_GROUP_PRIMARY_LANGUAGE, _get_groups().items())
    else:
        groups = _get_groups().items()
    return {group_id:_recruitment_group(group_id, group) for group_id, group in groups}


def get_recruitment_group_name(group_id, default = None):
    group = get_recruitment_groups().get(group_id)
    if group:
        return group.groupName
    return default


@Memoize
def get_recruitment_types_by_group_id():
    types_by_group = defaultdict(list)
    for type_id, type_ in get_recruitment_types().iteritems():
        types_by_group[type_.groupID].append(type_)

    return types_by_group


def get_recruitment_types_for_group_id(group_id, default = ()):
    return get_recruitment_types_by_group_id().get(group_id, default)


def _recruitment_type(type_id, type_):
    return RecruitmentType(type_id, type_.recruitmentGroupID, pow(2, type_id), GetByMessageID(type_.nameID), GetByMessageID(type_.descriptionID))


def _recruitment_group(group_id, group):
    return RecruitmentGroup(group_id, GetByMessageID(group.nameID), GetByMessageID(group.descriptionID))
