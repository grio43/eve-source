#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterdata\bloodlines.py
import random
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import bloodlinesLoader
except ImportError:
    bloodlinesLoader = None

class BloodlinesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/bloodlines.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/bloodlines.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/bloodlines.fsdbinary'
    __loader__ = bloodlinesLoader


def _get_bloodlines():
    return BloodlinesLoader.GetData()


def iter_bloodlines():
    for bloodline_id, data in _get_bloodlines().iteritems():
        yield (bloodline_id, data)


def get_bloodline(bloodline_id):
    return _get_bloodlines()[bloodline_id]


def get_race_id(bloodline_id):
    return get_bloodline(bloodline_id).raceID


def get_bloodline_corporation_id(bloodline_id):
    return get_bloodline(bloodline_id).corporationID


def bloodline_exists(bloodline_id):
    return bloodline_id in _get_bloodlines()


def get_bloodline_name(bloodline_id, bloodline = None, language_id = None):
    if not bloodline:
        bloodline = get_bloodline(bloodline_id)
    return _get_message(bloodline.nameID, language_id=language_id)


def get_bloodline_ids_by_race_id(race_id, shuffle = False):
    bloodlines = [ bloodline_id for bloodline_id, bloodline in iter_bloodlines() if bloodline.raceID == race_id ]
    if bloodlines and shuffle:
        random.shuffle(bloodlines)
    return bloodlines


def get_bloodline_description(bloodline_id, bloodline = None, language_id = None):
    if not bloodline:
        bloodline = get_bloodline(bloodline_id)
    return _get_message(bloodline.descriptionID, language_id=language_id)


def _get_message(message_id, language_id = None):
    import localization
    return localization.GetByMessageID(message_id, language_id=language_id)
