#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\marketgroups\data.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import localization
except ImportError:
    localization = None

try:
    import marketGroupsLoader
except ImportError:
    marketGroupsLoader = None

class MarketGroups(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/marketGroups.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/marketGroups.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/marketGroups.fsdbinary'
    __dataemporiumDatasetName__ = 'staticdata:/marketGroups/marketGroups'
    __loader__ = marketGroupsLoader


class MarketGroupObject:

    def __init__(self, market_group_id):
        self.marketGroupID = market_group_id
        self.marketGroupName = get_market_group_name(market_group_id)
        self.marketGroupNameID = get_market_group_name_id(market_group_id)
        self.description = get_market_group_description(market_group_id)
        self.descriptionID = get_market_group_description_id(market_group_id)
        self.parentGroupID = get_market_group_parent_id(market_group_id)
        self.iconID = get_market_group_icon_id(market_group_id)
        self.hasTypes = market_group_has_types(market_group_id)

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)


marketGroupData = None

def _get_market_groups():
    global marketGroupData
    if not marketGroupData:
        marketGroupData = MarketGroups.GetData()
    return marketGroupData


def get_market_group_ids():
    return [ _id for _id in _get_market_groups().iterkeys() ]


def get_market_group_name_id(market_group_id):
    market_group = _get_market_group(market_group_id)
    return market_group.nameID


def get_market_group_description_id(market_group_id):
    market_group = _get_market_group(market_group_id)
    return market_group.descriptionID


def get_market_group_name(market_group_id):
    market_group = _get_market_group(market_group_id)
    if market_group.nameID is not None:
        return localization.GetByMessageID(market_group.nameID)


def _get_market_group(market_group_id):
    return _get_market_groups().get(market_group_id)


def get_market_group_description(market_group_id):
    market_group = _get_market_group(market_group_id)
    if market_group.descriptionID is not None:
        return localization.GetByMessageID(market_group.descriptionID)


def market_group_has_types(market_group_id):
    market_group = _get_market_group(market_group_id)
    if market_group.hasTypes is not None:
        return market_group.hasTypes


def get_market_group_parent_id(market_group_id):
    if market_group_id is None:
        return
    market_group = _get_market_group(market_group_id)
    return market_group.parentGroupID


def get_market_group_icon_id(market_group_id):
    market_group = _get_market_group(market_group_id)
    if market_group.iconID is not None:
        return market_group.iconID
