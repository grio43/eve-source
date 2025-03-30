#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\npcs\divisions.py
import localization
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import npcCorporationDivisionsLoader
except ImportError:
    npcCorporationDivisionsLoader = None

class NpcCorporationDivisionsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/npcCorporationDivisions.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/npcCorporationDivisions.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/npcCorporationDivisions.fsdbinary'
    __loader__ = npcCorporationDivisionsLoader


def _get():
    return NpcCorporationDivisionsLoader.GetData()


def get_division(division_id):
    return _get().get(division_id)


def iter_divisions():
    for division_id, division in _get().iteritems():
        yield (division_id, division)


def get_division_name(division_id, division = None, languageID = None):
    if not division:
        division = _get().get(division_id)
    if division:
        return localization.GetByMessageID(division.nameID, languageID)


def get_division_description(division_id):
    division = _get().get(division_id)
    if division:
        return localization.GetByMessageID(division.descriptionID)


def get_division_internal_name(division_id):
    division = get_division(division_id)
    if division:
        return division.internalName
