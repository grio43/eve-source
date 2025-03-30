#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\util\searchUtil.py
from collections import defaultdict
import localization
import evetypes
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.universe import SolarSystem, SolarSystemStructure
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.userentry import AgentEntry, User
from eve.common.lib import appConst
from eve.common.script.search import const as search_const
from eveexceptions import UserError
from globalConfig.getFunctions import ArePointerLinksActive
from localization import GetByLabel
from bannedwords.client import bannedwords
SEARCHBY_OPTIONS = ([GetByLabel('UI/Search/UniversalSearch/PartialTerms'), search_const.MatchBy.partial_terms],
 [GetByLabel('UI/Search/UniversalSearch/ExactTerms'), search_const.MatchBy.exact_terms],
 [GetByLabel('UI/Search/UniversalSearch/ExactPhrase'), search_const.MatchBy.exact_phrase],
 [GetByLabel('UI/Search/UniversalSearch/OnlyExactPhrase'), search_const.MatchBy.exact_phrase_only])
RESULT_ORDER = (search_const.ResultType.agent,
 search_const.ResultType.character,
 search_const.ResultType.faction,
 search_const.ResultType.corporation,
 search_const.ResultType.alliance,
 search_const.ResultType.region,
 search_const.ResultType.solar_system,
 search_const.ResultType.station,
 search_const.ResultType.structure,
 search_const.ResultType.structure_with_inlined_data,
 search_const.ResultType.constellation,
 search_const.ResultType.item_type)
RESULT_LABELS = {search_const.ResultType.agent: 'UI/Search/UniversalSearch/Agents',
 search_const.ResultType.character: 'UI/Search/UniversalSearch/Characters',
 search_const.ResultType.faction: 'UI/Search/UniversalSearch/Factions',
 search_const.ResultType.corporation: 'UI/Search/UniversalSearch/Corporations',
 search_const.ResultType.alliance: 'UI/Search/UniversalSearch/Alliances',
 search_const.ResultType.region: 'UI/Search/UniversalSearch/Regions',
 search_const.ResultType.solar_system: 'UI/Search/UniversalSearch/SolarSystems',
 search_const.ResultType.station: 'UI/Common/LocationTypes/Stations',
 search_const.ResultType.structure: 'UI/Common/LocationTypes/Structures',
 search_const.ResultType.structure_with_inlined_data: 'UI/Common/LocationTypes/Structures',
 search_const.ResultType.constellation: 'UI/Search/UniversalSearch/Constellations',
 search_const.ResultType.item_type: 'UI/Search/UniversalSearch/Types'}

def GetSearchByChoices():
    return SEARCHBY_OPTIONS


def GetResultsScrollList(searchStr, groupIDList, searchBy = search_const.MatchBy.partial_terms, searchWndName = 'mySearch', corpMemberIDs = None):
    resultsByType = GetResultsByGroupID(searchStr, groupIDList, searchBy)
    return _GetResultsScrollList(resultsByType, corpMemberIDs)


def GetResultsInNewWindow(searchStr, groupIDList, searchBy = search_const.MatchBy.partial_terms, searchWndName = 'mySearch', corpMemberIDs = None, includeUiElements = False):
    resultsByType = GetResultsByGroupID(searchStr, groupIDList, searchBy)
    scrolllist = _GetResultsScrollList(resultsByType, corpMemberIDs)
    header = localization.GetByLabel('UI/Common/SearchResults')
    numUiElements = 0
    if includeUiElements:
        uiElementResults, numUiElements = _GetResultsForUiElements(searchStr)
        scrolllist += uiElementResults
    totalResults = sum([ len(results) for results in resultsByType.values() ])
    if totalResults >= search_const.max_result_count:
        top = localization.GetByLabel('UI/Search/UniversalSearch/WindowHeaderOverMax', maxNumber=search_const.max_result_count, searchStr=searchStr)
    else:
        totalResults += numUiElements
        top = localization.GetByLabel('UI/Search/UniversalSearch/WindowHeaderNumResults', numResults=totalResults, searchStr=searchStr)
    noContentHint = localization.GetByLabel('UI/Search/UniversalSearch/NoResultsReturned', searchStr=searchStr)
    from eve.client.script.ui.control.listwindow import ListWindow
    chosen = ListWindow.ShowList(scrolllist, 'generic', header, top, 0, isModal=0, minChoices=0, windowName=searchWndName, lstDataIsGrouped=1, unstackable=1, noContentHint=noContentHint, showCollapseBtn=True)
    if chosen:
        return chosen[1]


def _GetResultsScrollList(resultsByType, corpMemberIDs):
    scrolllist = []
    for resultType in RESULT_ORDER:
        if resultType not in resultsByType:
            continue
        results = resultsByType[resultType]
        entryList = GetScrollEntryData(results, resultType, corpMemberIDs)
        if entryList:
            _AppendScrollGroups(entryList, resultType, scrolllist)

    return scrolllist


def _GetResultsForUiElements(searchStr):
    if ArePointerLinksActive(sm.GetService('machoNet')):
        return sm.GetService('helpPointer').SearchPointers(searchStr)
    return ([], 0)


def _AppendScrollGroups(entryList, resultType, scrolllist):
    if resultType == search_const.ResultType.item_type:
        _AppendScrollGroupsInvItems(entryList, resultType, scrolllist)
    else:
        _AppendScrollGroup(entryList, resultType, scrolllist)


def _AppendScrollGroupsInvItems(entryList, resultType, scrolllist):
    entriesByCategory = defaultdict(list)
    for entry in entryList:
        categoryID = evetypes.GetCategoryID(entry['typeID'])
        entriesByCategory[categoryID].append(entry)

    for categoryID, entries in sorted(entriesByCategory.items()):
        searchGroupID = 'inv_%s_%s' % (resultType, categoryID)
        data = GetScrollListGroup(entries, _GetInvItemEntryType(categoryID), evetypes.GetCategoryNameByCategory(categoryID), searchGroupID)
        scrolllist.append(GetFromClass(ListGroup, data))


def _GetInvItemEntryType(categoryID):
    return Item


def _AppendScrollGroup(entryList, resultType, scrolllist):
    label = localization.GetByLabel(RESULT_LABELS[resultType])
    entryType = GetScrollEntryType(resultType)
    data = GetScrollListGroup(entryList, entryType, label, str(resultType))
    scrolllist.append(GetFromClass(ListGroup, data))


def GetScrollListGroup(entryList, entryType, label, searchGroupID):
    sectionHeader = localization.GetByLabel('UI/Search/UniversalSearch/SectionHeader', resultType=label, numberReturned=len(entryList))
    data = {'GetSubContent': GetSearchSubContent,
     'label': sectionHeader,
     'groupItems': (entryType, entryList),
     'id': ('search_cat', searchGroupID),
     'sublevel': 0,
     'showlen': 0,
     'showicon': 'hide',
     'state': 'locked'}
    return data


def GetScrollEntryData(results, resultType, corpMemberIDs):
    entryList = []
    if resultType == search_const.ResultType.agent:
        for agentID in results:
            if sm.GetService('agents').GetAgentByID(agentID) is None:
                continue
            data = {'charID': agentID,
             'sublevel': 0}
            entryList.append(data)

    elif resultType in (search_const.ResultType.corporation,
     search_const.ResultType.alliance,
     search_const.ResultType.faction,
     search_const.ResultType.character):
        for ownerID in results:
            if corpMemberIDs and ownerID not in corpMemberIDs:
                continue
            data = {'charID': ownerID,
             'sublevel': 0,
             'showinfo': True}
            entryList.append(data)

    elif resultType == search_const.ResultType.solar_system:
        for itemID in results:
            data = {'itemID': itemID,
             'solarSystemID': itemID,
             'typeID': appConst.typeSolarSystem,
             'label': cfg.evelocations.Get(itemID).name,
             'sublevel': 0,
             'showinfo': True}
            entryList.append(data)

    elif resultType == search_const.ResultType.constellation:
        for itemID in results:
            data = {'itemID': itemID,
             'typeID': appConst.typeConstellation,
             'label': cfg.evelocations.Get(itemID).name,
             'sublevel': 0,
             'showinfo': True}
            entryList.append(data)

    elif resultType == search_const.ResultType.region:
        for itemID in results:
            data = {'itemID': itemID,
             'typeID': appConst.typeRegion,
             'label': cfg.evelocations.Get(itemID).name,
             'sublevel': 0,
             'showinfo': True}
            entryList.append(data)

    elif resultType == search_const.ResultType.structure:
        for itemID in results:
            info = sm.GetService('structureDirectory').GetStructureInfo(itemID)
            data = {'itemID': itemID,
             'solarSystemID': info.solarSystemID,
             'sublevel': 0,
             'typeID': info.typeID,
             'label': info.itemName,
             'showinfo': True}
            entryList.append(data)

    elif resultType == search_const.ResultType.structure_with_inlined_data:
        for info in results:
            data = {'itemID': info.structureID,
             'sublevel': 0,
             'typeID': info.typeID,
             'label': info.itemName}
            entryList.append(data)

    elif resultType == search_const.ResultType.station:
        for itemID in results:
            station = cfg.stations.Get(itemID)
            data = {'itemID': itemID,
             'solarSystemID': station.solarSystemID,
             'typeID': station.stationTypeID,
             'label': cfg.evelocations.Get(itemID).name,
             'sublevel': 0,
             'showinfo': True}
            entryList.append(data)

    elif resultType == search_const.ResultType.item_type:
        for typeID in results:
            if not evetypes.Exists(typeID):
                continue
            data = {'itemID': None,
             'typeID': typeID,
             'getIcon': 1,
             'label': evetypes.GetName(typeID),
             'sublevel': 0,
             'showinfo': True}
            entryList.append(data)

    return entryList


def GetScrollEntryType(resultType):
    if resultType == search_const.ResultType.agent:
        return AgentEntry
    elif resultType in (search_const.ResultType.corporation,
     search_const.ResultType.alliance,
     search_const.ResultType.faction,
     search_const.ResultType.character):
        return User
    elif resultType == search_const.ResultType.item_type:
        return Item
    elif resultType == search_const.ResultType.structure:
        return SolarSystemStructure
    elif resultType in (search_const.ResultType.solar_system, search_const.ResultType.station):
        return SolarSystem
    else:
        return Generic


def GetResultsByGroupID(searchStr, groupIDList, searchBy = search_const.MatchBy.partial_terms):
    searchStr = _FormatSearchInput(searchStr)
    _ValidateSearchInput(searchStr, searchBy)
    searchMgr = sm.ProxySvc('search')
    resultsByType = searchMgr.Query(searchStr, groupIDList, exact=searchBy)
    if resultsByType:
        _PrimeResults(resultsByType)
    _SortResults(resultsByType)
    return resultsByType or {}


def _SortResults(resultsByType):
    for resultID, results in resultsByType.iteritems():
        if resultID in search_const.location_result_types:
            results.sort(key=lambda x: cfg.evelocations.Get(x).locationName)
        elif resultID in search_const.owner_result_types:
            results.sort(key=lambda x: cfg.eveowners.Get(x).ownerName)
        elif resultID == search_const.ResultType.item_type:
            results.sort(key=lambda x: evetypes.GetName(x))


def GetResultsList(searchStr, groupIDList, searchBy = search_const.MatchBy.partial_terms, hideNPC = 0, onlyAltName = 0):
    searchStr = _FormatSearchInput(searchStr)
    _ValidateSearchInput(searchStr, searchBy)
    searchMgr = sm.ProxySvc('search')
    return searchMgr.QuickQuery(searchStr, groupIDList, hideNPC=hideNPC, onlyAltName=onlyAltName, exact=searchBy)


def _FormatSearchInput(searchStr):
    searchStr = searchStr.replace('*', '')
    searchStr = searchStr.strip()
    return searchStr


def _ValidateSearchInput(searchStr, exact):
    if len(searchStr) < 1:
        raise UserError('LookupStringMinimum', {'minimum': 1})
    elif len(searchStr) >= 100:
        raise UserError('CustomInfo', {'info': localization.GetByLabel('UI/Common/SearchStringTooLong')})
    elif exact == search_const.MatchBy.partial_terms and not localization.util.IsTextInConciseLanguage(session.languageID, searchStr):
        if len([ x for x in searchStr.split() if len(x) >= search_const.min_wildcard_length ]) == 0:
            raise UserError('PartialSearchLessThanMinLength', {'minChars': search_const.min_wildcard_length})
    bannedwords.check_search_words_allowed(searchStr)


def _PrimeResults(resultsByType):
    _PrimeOwners(resultsByType)
    _PrimeCorpTickers(resultsByType)
    _RemoveNonExistingTypes(resultsByType)


def _PrimeCorpTickers(resultsByType):
    results = resultsByType.get(search_const.ResultType.corporation, None)
    if results:
        cfg.corptickernames.Prime(results)


def _PrimeOwners(resultsByType):
    toPrime = []
    for resultType in search_const.owner_result_types:
        toPrime.extend(resultsByType.get(resultType, []))

    cfg.eveowners.Prime(toPrime)


def _RemoveNonExistingTypes(resultsByType):
    if search_const.ResultType.item_type in resultsByType:
        results = resultsByType[search_const.ResultType.item_type]
        filteredResults = filter(evetypes.Exists, results)
        resultsByType[search_const.ResultType.item_type] = filteredResults


def GetSearchSubContent(dataX, *args):
    scrolllist = []
    entryType, typeList = dataX['groupItems']
    for data in typeList:
        scrolllist.append(GetFromClass(entryType, data))

    return scrolllist


def SearchCharacters(searchStr, searchBy = search_const.MatchBy.partial_terms):
    scrolllist = GetResultsScrollList(searchStr, [search_const.ResultType.character], searchBy=searchBy)
    if len(scrolllist):
        return GetSearchSubContent(scrolllist[0])
    return []


def SearchCharactersInCorp(searchStr, corpMemberIDs):
    scrolllist = GetResultsScrollList(searchStr, [search_const.ResultType.character], corpMemberIDs=corpMemberIDs)
    if len(scrolllist):
        return GetSearchSubContent(scrolllist[0])
    return []


def SearchCorporations(searchStr, searchBy = search_const.MatchBy.partial_terms):
    scrolllist = GetResultsScrollList(searchStr, [search_const.ResultType.corporation], searchBy=searchBy)
    if len(scrolllist):
        return GetSearchSubContent(scrolllist[0])
    return []


def IsMatch(searchStr, candidate, exact):
    if exact == search_const.MatchBy.partial_terms and not localization.util.IsTextInConciseLanguage(session.languageID, searchStr):
        if len([ x for x in searchStr.split() if len(x) >= search_const.min_wildcard_length ]) == 0:
            exact = search_const.MatchBy.exact_terms
    searchStr = searchStr.lower().strip()
    candidate = candidate.lower().strip()
    if exact == search_const.MatchBy.partial_terms:
        searchTermList = searchStr.split()
        candTermList = candidate.lower().split()
        matches = True
        for searchTerm in searchTermList:
            termMatches = False
            for candTerm in candTermList:
                if candTerm.startswith(searchTerm):
                    termMatches = True
                    break

            if not termMatches:
                matches = False
                break

        return matches
    if exact == search_const.MatchBy.exact_terms:
        candTermList = candidate.split()
        return all([ s in candTermList for s in searchStr.split() ])
    if exact == search_const.MatchBy.exact_phrase:
        searchTermList = searchStr.split()
        lBound = 0
        uBound = len(searchTermList)
        candTermList = candidate.split()
        for idx in range(uBound, len(candTermList) + 1):
            if searchTermList == candTermList[lBound:idx]:
                return True
            lBound += 1

        return False
    if exact == search_const.MatchBy.exact_phrase_only:
        return searchStr == candidate
    raise RuntimeError('Unknown value passed in for exact flag')
