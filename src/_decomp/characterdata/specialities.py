#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterdata\specialities.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import characterSpecialitiesLoader
except ImportError:
    characterSpecialitiesLoader = None

class CharacterSpecialitiesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/characterSpecialities.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/characterSpecialities.fsdbinary'
    __loader__ = characterSpecialitiesLoader


def get_specialities():
    return CharacterSpecialitiesLoader.GetData()


def iter_specialities():
    for speciality_id, data in get_specialities().iteritems():
        yield (speciality_id, data)


def get_speciality_ids_by_career_id(career_id):
    return [ speciality_id for speciality_id, speciality in iter_specialities() if speciality.careerID == career_id ]


def get_speciality(speciality_id, default = None):
    return get_specialities().get(speciality_id, default)


def get_speciality_name(speciality_id, speciality = None, language_id = None):
    if not speciality:
        speciality = get_speciality(speciality_id)
    return _get_message(getattr(speciality, 'nameID', None), language_id)


def get_speciality_description(speciality_id, speciality = None, language_id = None):
    if not speciality:
        speciality = get_speciality(speciality_id)
    return _get_message(getattr(speciality, 'descriptionID', None), language_id)


def _get_message(message_id, language_id = None):
    import localization
    return localization.GetByMessageID(message_id, language_id=language_id)
