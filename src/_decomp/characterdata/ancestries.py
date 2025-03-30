#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterdata\ancestries.py
import random
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import ancestriesLoader
except ImportError:
    ancestriesLoader = None

class AncestriesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/ancestries.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/ancestries.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/ancestries.fsdbinary'
    __loader__ = ancestriesLoader


def get_ancestries():
    return AncestriesLoader.GetData()


def iter_ancestries():
    for ancestry_id, data in get_ancestries().iteritems():
        yield (ancestry_id, data)


def get_ancestry(ancestry_id):
    return get_ancestries()[ancestry_id]


def get_ancestry_name(ancestry_id, ancestry = None, language_id = None):
    if not ancestry:
        ancestry = get_ancestry(ancestry_id)
    return _get_message(ancestry.nameID, language_id)


def iter_ancestry_id_name_mapping():
    for ancestry_id, ancestry_name in get_ancestry_id_name_mapping().iteritems():
        yield (ancestry_id, ancestry_name)


def get_ancestry_id_name_mapping(bloodline_id = None):
    return {ancestry_id:get_ancestry_name(ancestry_id, ancestry) for ancestry_id, ancestry in iter_ancestries() if not bloodline_id or ancestry.bloodlineID == bloodline_id}


def get_ancestries_for_bloodline(bloodline_id, shuffle = False):
    ancestries = [ (ancestry_id, ancestry) for ancestry_id, ancestry in iter_ancestries() if ancestry.bloodlineID == bloodline_id ]
    if ancestries and shuffle:
        random.shuffle(ancestries)
    return ancestries


def get_ancestry_ids_for_bloodline(bloodline_id = None):
    return [ ancestry_id for ancestry_id, ancestry in iter_ancestries() if not bloodline_id or ancestry.bloodlineID == bloodline_id ]


def get_random_ancestry_id(bloodline_id = None):
    return random.choice(get_ancestry_ids_for_bloodline(bloodline_id))


def get_ancestry_name_id(ancestry_id):
    return get_ancestry(ancestry_id).nameID


def get_ancestry_description(ancestry_id, ancestry = None, language_id = None):
    if not ancestry:
        ancestry = get_ancestry(ancestry_id)
    return _get_message(ancestry.descriptionID, language_id)


def _get_message(message_id, language_id = None):
    import localization
    return localization.GetByMessageID(message_id, language_id=language_id)
