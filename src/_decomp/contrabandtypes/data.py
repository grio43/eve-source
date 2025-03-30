#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contrabandtypes\data.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import contrabandTypesLoader
except ImportError:
    contrabandTypesLoader = None

class ContrabandTypes(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/contrabandTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/contrabandTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/contrabandTypes.fsdbinary'
    __loader__ = contrabandTypesLoader


def get_contraband_type_ids():
    return [ type_id for type_id in ContrabandTypes.GetData().iterkeys() ]


def get_contraband_types_factions(type_id):
    contraband_type = get_contraband_type(type_id)
    if contraband_type is not None:
        return [ faction_id for faction_id in contraband_type.factions.iterkeys() ]
    return []


def get_contraband_type(type_id):
    return ContrabandTypes.GetData().get(type_id, None)


def get_contraband_types_in_faction(faction_id):
    contraband_types = {}
    for type_id in get_contraband_type_ids():
        contraband_type = get_contraband_type(type_id)
        if contraband_type is not None and faction_id in contraband_type.factions:
            contraband_types[type_id] = contraband_type.factions[faction_id]

    return contraband_types


def get_contraband_types():
    return ContrabandTypes.GetData()
