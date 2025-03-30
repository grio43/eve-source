#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\static_data\component_rarity.py
from itertoolsext.Enum import Enum
from fsdBuiltData.common.base import BuiltDataLoader
from localization import GetByMessageID
try:
    import ship_skin_design_components_raritiesLoader
except ImportError:
    ship_skin_design_components_raritiesLoader = None

class _ComponentRaritiesDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/ship_skin_design_component_rarities.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/ship_skin_design_component_rarities.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/ship_skin_design_component_rarities.fsdbinary'
    __loader__ = ship_skin_design_components_raritiesLoader


def get_component_ratities_data():
    return _ComponentRaritiesDataLoader.GetData()


@Enum

class ComponentRarityLevel(object):
    STANDARD = 1
    ADVANCED = 2
    ELITE = 3
    SUPERIOR = 4
    STELLAR = 5
    EMPYREAN = 6


def get_rarities_by_priority(ascending = True):
    rarities_data = get_component_ratities_data()
    rarities = []
    for rarity_id, rarity_data in rarities_data.iteritems():
        rarities.append((get_rarity_from_fsd(rarity_id), rarity_data.rank))

    return [ a for a, b in sorted(rarities, key=lambda x: x[1], reverse=not ascending) ]


def get_rarity_name(rarity_level):
    rarities_data = get_component_ratities_data()
    for fsd_rarity_id, data in rarities_data.iteritems():
        if get_rarity_from_fsd(fsd_rarity_id) == rarity_level:
            return GetByMessageID(data.name)


def get_rarity_from_fsd(fsd_rarity_id):
    if fsd_rarity_id == 1:
        return ComponentRarityLevel.STANDARD
    if fsd_rarity_id == 2:
        return ComponentRarityLevel.ADVANCED
    if fsd_rarity_id == 3:
        return ComponentRarityLevel.ELITE
    if fsd_rarity_id == 4:
        return ComponentRarityLevel.SUPERIOR
    if fsd_rarity_id == 5:
        return ComponentRarityLevel.STELLAR
    if fsd_rarity_id == 6:
        return ComponentRarityLevel.EMPYREAN
