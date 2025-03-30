#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterdata\careers.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import characterCareersLoader
except ImportError:
    characterCareersLoader = None

class CharacterCareersLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/characterCareers.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/characterCareers.fsdbinary'
    __loader__ = characterCareersLoader


def get_careers():
    return CharacterCareersLoader.GetData()


def iter_careers():
    for career_id, data in get_careers().iteritems():
        yield (career_id, data)


def get_career(career_id, default = None):
    return get_careers().get(career_id, default)


def get_career_name(career_id):
    return get_career_attribute(career_id, 'careerName')


def get_career_race_id(career_id):
    return get_career_attribute(career_id, 'raceID')


def get_career_attribute(career_id, attribute, default = None):
    career = get_career(career_id)
    return getattr(career, attribute, default)
