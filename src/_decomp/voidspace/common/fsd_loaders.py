#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\voidspace\common\fsd_loaders.py
from fsdBuiltData.common.base import BuiltDataLoader
from utillib import KeyVal
try:
    import voidSpaceEncountersLoader
except ImportError:
    voidSpaceEncounterLoaders = None

class VoidSpaceEncountersLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/voidSpaceEncounters.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/voidSpaceEncounters.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/voidSpaceEncounters.fsdbinary'
    __loader__ = voidSpaceEncountersLoader


def get_void_space_encounters():
    return VoidSpaceEncountersLoader.GetData()


def get_void_space_encounter_static_data(filament_type_id):
    encounter = get_void_space_encounters()[filament_type_id]
    return _construct_content_info(encounter)


def _construct_content_info(encounter):
    return KeyVal(dungeonIDs=encounter.dungeonIDs, nebulaGraphicIDs=encounter.nebulaGraphicIDs, validShipTypeListID=encounter.validShipTypeListID, numberOfPlayers=encounter.numberOfPlayers, encounterDescriptionID=encounter.encounterDescriptionID, shipRestrictionsDescriptionID=encounter.shipRestrictionsDescriptionID, traceDescriptionTitleID=encounter.traceDescriptionTitleID, traceDescriptionID=encounter.traceDescriptionID)
