#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\loyaltypoints\lpUtil.py
from inventorycommon.const import stationFulcrumZarzakh, ownerMalakimZealots, ownerCommandoGuri
hardcoded_lp_stores = {stationFulcrumZarzakh: [ownerMalakimZealots, ownerCommandoGuri]}

def get_hardcoded_lp_stores(stationID):
    return hardcoded_lp_stores.get(stationID, [])


def get_normal_lp_stores_in_station(stationID, stationOwner):
    hardCodedStores = get_hardcoded_lp_stores(stationID)
    if hardCodedStores:
        return hardCodedStores
    return [stationOwner]


def get_hardcoded_lp_stations_for_corp(corpID):
    stationIDsForCorp = []
    for stationID, corpIDsInStation in hardcoded_lp_stores.iteritems():
        if corpID in corpIDsInStation:
            stationIDsForCorp.append(stationID)

    return stationIDsForCorp
