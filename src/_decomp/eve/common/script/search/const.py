#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\search\const.py


class MatchBy(object):
    partial_terms = 0
    exact_terms = 1
    exact_phrase = 2
    exact_phrase_only = 3


class ResultType(object):
    agent = 1
    character = 2
    corporation = 3
    alliance = 4
    faction = 5
    constellation = 6
    solar_system = 7
    region = 8
    station = 9
    item_type = 10
    wormhole = 11
    structure = 12
    structure_with_inlined_data = 13


owner_result_types = [ResultType.agent,
 ResultType.character,
 ResultType.corporation,
 ResultType.alliance,
 ResultType.faction]
location_result_types = [ResultType.constellation,
 ResultType.solar_system,
 ResultType.region,
 ResultType.station,
 ResultType.structure]
all_result_types = [ResultType.agent,
 ResultType.alliance,
 ResultType.character,
 ResultType.corporation,
 ResultType.constellation,
 ResultType.faction,
 ResultType.item_type,
 ResultType.region,
 ResultType.solar_system,
 ResultType.station,
 ResultType.structure,
 ResultType.wormhole]
max_result_count = 500
min_wildcard_length = 3

def get_legacy_search_const():
    import utillib
    return utillib.KeyVal(searchResultAgent=ResultType.agent, searchResultCharacter=ResultType.character, searchResultCorporation=ResultType.corporation, searchResultAlliance=ResultType.alliance, searchResultFaction=ResultType.faction, searchResultConstellation=ResultType.constellation, searchResultSolarSystem=ResultType.solar_system, searchResultRegion=ResultType.region, searchResultStation=ResultType.station, searchResultInventoryType=ResultType.item_type, searchResultWormHoles=ResultType.wormhole, searchResultStructure=ResultType.structure, searchByPartialTerms=MatchBy.partial_terms, searchByExactTerms=MatchBy.exact_terms, searchByExactPhrase=MatchBy.exact_phrase, searchByOnlyExactPhrase=MatchBy.exact_phrase_only)
