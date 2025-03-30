#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterdata\schools.py
import logging
import random
from collections import defaultdict
from monolithconfig import get_value
from fsdBuiltData.common.base import BuiltDataLoader
from npcs.npccorporations import get_corporation_station_id
try:
    import schoolsLoader
except ImportError:
    schoolsLoader = None

logger = logging.getLogger(__name__)

class SchoolsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/schools.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/schools.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/schools.fsdbinary'
    __loader__ = schoolsLoader


def _get_schools():
    return SchoolsLoader.GetData()


def iter_schools():
    for school_id, data in _get_schools().iteritems():
        yield (school_id, data)


def get_school(school_id):
    return _get_schools()[school_id]


def get_school_race_id(school_id):
    return get_school(school_id).raceID


def get_school_corporation_id(school_id):
    return get_school(school_id).corporationID


def get_all_school_ids():
    return _get_schools().keys()


def get_all_school_race_ids():
    return [ school.raceID for school in _get_schools().itervalues() ]


def get_all_schools_by_race():
    schools_by_race = defaultdict(list)
    for school_id, school in _get_schools().iteritems():
        schools_by_race[school.raceID].append(school_id)

    return schools_by_race


def get_all_school_corporation_ids():
    return [ school.corporationID for school in _get_schools().itervalues() ]


def get_career_id(school_id):
    return get_school(school_id).careerID


def get_school_ids_by_race_id(race_id):
    return [ school_id for school_id, school in iter_schools() if school.raceID == race_id ]


def school_exists(school_id):
    return school_id in _get_schools()


def get_school_name(school_id, school = None, language_id = None):
    if not school:
        school = get_school(school_id)
    return _get_message(school.nameID, language_id=language_id)


def get_school_description(school_id, school = None, language_id = None):
    if not school:
        school = get_school(school_id)
    return _get_message(school.descriptionID, language_id=language_id)


def get_school_title(school_id, school = None, language_id = None):
    if not school:
        school = get_school(school_id)
    return _get_message(school.titleID, language_id=language_id)


def get_school_character_description(school_id, school = None, language_id = None):
    if not school:
        school = get_school(school_id)
    return _get_message(school.characterDescriptionID, language_id=language_id)


def _get_message(message_id, language_id = None):
    import localization
    return localization.GetByMessageID(message_id, language_id=language_id)


def get_school_starting_station(school_id):
    try:
        stations = get_school(school_id).startingStations or []
        number_of_newbie_systems = get_value('Newbie-System-Count', 'Character') or 1
        station_index = random.randint(0, int(number_of_newbie_systems) - 1)
        return stations[station_index]
    except IndexError:
        corporation_id = get_school_corporation_id(school_id)
        return get_corporation_station_id(corporation_id)
    except KeyError:
        logger.error('Failed to load school with id: %s', school_id)
        raise
