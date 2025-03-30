#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterdata\races.py
from caching import Memoize
from characterskills import GetSPForLevelRaw
from dogma.const import attributeSkillTimeConstant
from dogma.data import get_type_attribute
from eve.common.lib.appConst import raceAmarr
from eve.common.lib.appConst import raceCaldari
from eve.common.lib.appConst import raceGallente
from eve.common.lib.appConst import raceMinmatar
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import racesLoader
except ImportError:
    racesLoader = None

CHARACTER_CREATION_RACE_IDS = [raceCaldari,
 raceGallente,
 raceMinmatar,
 raceAmarr]

class RacesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/races.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/races.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/races.fsdbinary'
    __loader__ = racesLoader


def _get_races():
    return RacesLoader.GetData()


def iter_races():
    for race_id, race_data in _get_races().iteritems():
        yield (race_id, race_data)


def iter_race_ids():
    for race_id in _get_races().iterkeys():
        yield race_id


def get_race(race_id):
    return _get_races()[race_id]


def get_race_id_name_mapping(language_id = None):
    return {race_id:get_race_name(race_data.nameID, race_data, language_id) for race_id, race_data in iter_races()}


def iter_race_id_name_mapping(language_id = None):
    for race_id, race_name in get_race_id_name_mapping(language_id).iteritems():
        yield (race_id, race_name)


@Memoize
def get_newbie_skills_for_race(race_id):
    skills = get_race_skills(race_id, {})
    newbie_skills = {}
    for skill_type_id, levels in skills.iteritems():
        type_attribute = get_type_attribute(skill_type_id, attributeSkillTimeConstant)
        if type_attribute:
            skill_points = GetSPForLevelRaw(type_attribute, levels)
            newbie_skills[skill_type_id] = {'skillPoints': skill_points,
             'skillLevel': levels}

    return newbie_skills


def get_newbie_skill_points_for_race(race_id):
    newbie_skills = get_newbie_skills_for_race(race_id)
    return {skill_type_id:newbie_skill['skillPoints'] for skill_type_id, newbie_skill in newbie_skills.iteritems()}


def race_exists(race_id):
    return race_id in _get_races()


def get_race_skills(race_id, default = None):
    race = get_race(race_id)
    return getattr(race, 'skills', default)


def get_race_name(race_id, race = None, language_id = None):
    if not race:
        race = get_race(race_id)
    return _get_message(race.nameID, language_id)


def get_race_description(race_id, race = None):
    if not race:
        race = get_race(race_id)
    return _get_message(race.descriptionID)


def get_race_name_id(race_id):
    return get_race(race_id).nameID


def get_race_description_id(race_id):
    return get_race(race_id).descriptionID


def _get_message(message_id, language_id = None):
    import localization
    return localization.GetByMessageID(message_id, language_id)


def get_ship_type_id(race_id):
    return get_race(race_id).shipTypeID
