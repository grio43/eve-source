#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\lpOffers\data.py
from collections import defaultdict
import utillib
from fsdBuiltData.common.base import BuiltDataLoader
from npcs.npccorporations import get_corporation_lp_offer_tables, get_corporation_faction_id
try:
    import lpOffersLoader
except ImportError:
    lpOffersLoader = None

try:
    import lpOfferTablesLoader
except ImportError:
    lpOfferTablesLoader = None

class LPOffers(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/lpOffers.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/lpOffers.fsdbinary'
    __loader__ = lpOffersLoader


class LPOfferTables(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/lpOfferTables.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/lpOfferTables.fsdbinary'
    __loader__ = lpOfferTablesLoader


def _get_lp_offer_tables():
    return LPOfferTables.GetData()


def _get_lp_offer_table(table_id):
    return _get_lp_offer_tables().get(table_id, None)


def _get_lp_offers():
    return LPOffers.GetData()


def _get_lp_offer(offer_id):
    return _get_lp_offers().get(offer_id, None)


def get_lp_offers_for_corporation(corporation_id):
    table_ids = get_corporation_lp_offer_tables(corporation_id)
    if not table_ids:
        return []
    offers = {}
    for table_id in table_ids:
        table = _get_lp_offer_table(table_id)
        table_standings = getattr(table, 'requiredStandings', None)
        for offer_id in table.offers:
            offer = _get_offer(offer_id, corporation_id, table_standings)
            offers[offer_id] = offer

    return offers.values()


def get_lp_offer_for_corporation(offer_id, corporation_id):
    table_ids = get_corporation_lp_offer_tables(corporation_id)
    if not table_ids:
        return
    for table_id in table_ids:
        table = _get_lp_offer_table(table_id)
        if offer_id not in table.offers:
            continue
        table_standings = getattr(table, 'requiredStandings', None)
        offer = _get_offer(offer_id, corporation_id, table_standings)
        return offer


def _get_offer(offer_id, corporation_id, table_standings):
    offer = _get_lp_offer(offer_id)
    if not offer:
        return None
    standings_required = getattr(offer, 'requiredStandings') or table_standings
    if standings_required:
        standings_required = utillib.KeyVal(value=standings_required.standingsValue, ownerID=get_corporation_faction_id(corporation_id) if standings_required.factionRestricted else corporation_id)
    return utillib.KeyVal(corpID=corporation_id, offerID=offer_id, typeID=offer.offeredType, qty=offer.quantity, lpCost=offer.lpCost, iskCost=offer.iskCost, akCost=offer.akCost, reqItems=offer.requiredItems.items(), requiredStandings=standings_required)


def get_min_lp_cost_per_quantity_for_types():
    min_lp_for_type = {}
    for type_id, offers in _get_offers_by_type().iteritems():
        min_lp_for_type[type_id] = min(_get_min_lp_cost_for_offers(offers))

    return min_lp_for_type


def _get_offers_by_type():
    offers_by_type = defaultdict(set)
    for offer_id in _get_lp_offers():
        type_id = get_offered_type(offer_id)
        offers_by_type[type_id].add(offer_id)

    return offers_by_type


def _get_min_lp_cost_for_offers(offers):
    lp_costs = []
    for offer_id in offers:
        quantity = get_offered_type_quantity(offer_id)
        lp_cost = get_loyalty_point_cost_for_offer(offer_id)
        lp_costs.append(lp_cost / float(quantity))

    return lp_costs


def get_lp_offer_table_ids():
    return {table_id for table_id in _get_lp_offer_tables()}


def get_lp_offers_for_table(table_id):
    lp_offer_table = _get_lp_offer_table(table_id)
    return set(lp_offer_table.offers)


def iter_required_types_for_offer(offer_id):
    lp_offer = _get_lp_offer(offer_id)
    if lp_offer is None:
        return
    return [ (type_id, quantity) for type_id, quantity in lp_offer.requiredItems.iteritems() ]


def get_isk_cost_for_offer(offer_id):
    lp_offer = _get_lp_offer(offer_id)
    if lp_offer is None:
        return
    return lp_offer.iskCost


def get_analysis_kredit_cost_for_offer(offer_id):
    lp_offer = _get_lp_offer(offer_id)
    if lp_offer is None:
        return
    return lp_offer.akCost


def get_offered_type(offer_id):
    lp_offer = _get_lp_offer(offer_id)
    if lp_offer is None:
        return
    return lp_offer.offeredType


def get_offered_type_quantity(offer_id):
    lp_offer = _get_lp_offer(offer_id)
    if lp_offer is None:
        return
    return lp_offer.quantity


def get_loyalty_point_cost_for_offer(offer_id):
    lp_offer = _get_lp_offer(offer_id)
    if lp_offer is None:
        return
    return lp_offer.lpCost


def get_lp_offer_table_name(table_id):
    table = _get_lp_offer_table(table_id)
    return table.name


def get_lp_offer_name(offer_id):
    lp_offer = _get_lp_offer(offer_id)
    if lp_offer is None:
        return
    return lp_offer.name
