#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evetypes\skills.py
from collections import defaultdict
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import requiredSkillsForTypesLoader
except ImportError:
    requiredSkillsForTypesLoader = None

try:
    import requiredSkillsIndexLoader
except ImportError:
    requiredSkillsIndexLoader = None

class RequiredSkillsForTypes(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/requiredSkillsForTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/requiredSkillsForTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/requiredSkillsForTypes.fsdbinary'
    __loader__ = requiredSkillsForTypesLoader


class RequiredSkillsIndex(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/requiredSkillsIndex.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/requiredSkillsIndex.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/requiredSkillsIndex.fsdbinary'
    __loader__ = requiredSkillsIndexLoader


def _get_required_skills_for_types():
    return RequiredSkillsForTypes.GetData()


def get_required_skills_index():
    return RequiredSkillsIndex.GetData()


def get_types_with_skill_type(skill_type_id):
    skills_index = get_required_skills_index()
    res = []
    for index in skills_index.get(skill_type_id, {}).itervalues():
        for nested_index in index.values():
            for type_id in nested_index.itervalues():
                res.append(type_id)

    return res


def get_dogma_required_skills(type_id):
    return _get_required_skills_for_types().get(type_id, {})


def get_dogma_required_skills_recursive(type_id):
    ret = defaultdict(int)
    _get_dogma_required_skills_recursive(type_id, ret)
    return dict(ret)


def _get_dogma_required_skills_recursive(type_id, ret):
    for type_id, level in get_dogma_required_skills(type_id).iteritems():
        ret[type_id] = max(ret[type_id], level)
        _get_dogma_required_skills_recursive(type_id, ret)
