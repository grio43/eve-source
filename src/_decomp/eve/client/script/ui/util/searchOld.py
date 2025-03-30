#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\util\searchOld.py
import evetypes
import localization
from eve.client.script.ui.control.listwindow import ListWindow
from eve.client.script.ui.util import searchUtil
from eve.common.lib import appConst
from eve.common.script.search.const import MatchBy, ResultType
from eve.common.script.sys import idCheckers
from inventorycommon.util import IsNPC
from bannedwords.client import bannedwords

def _PrimeSearchResultsInEveOwners(results):
    if results:
        cfg.eveowners.Prime(results)


def __Search(searchStr, groupID, exact, filterCorpID, hideNPC = False):
    result = []
    if groupID == appConst.groupCharacter:
        groupIDList = [ResultType.character]
        if not hideNPC:
            groupIDList.append(ResultType.agent)
        result = searchUtil.GetResultsList(searchStr, groupIDList, exact)
        _PrimeSearchResultsInEveOwners(result)
    elif groupID == appConst.groupCorporation:
        onlyAltName = False
        groupIDList = [ResultType.corporation]
        if exact == -1:
            onlyAltName = True
        elif filterCorpID == -1:
            hideNPC = True
        result = searchUtil.GetResultsList(searchStr, groupIDList, exact, hideNPC=hideNPC, onlyAltName=onlyAltName)
        _PrimeSearchResultsInEveOwners(result)
    elif groupID == appConst.groupAlliance:
        onlyAltName = False
        groupIDList = [ResultType.alliance]
        if exact == -1:
            onlyAltName = True
        result = searchUtil.GetResultsList(searchStr, groupIDList, exact, onlyAltName=onlyAltName)
        _PrimeSearchResultsInEveOwners(result)
    elif groupID == appConst.groupStation:
        result = searchUtil.GetResultsList(searchStr, [ResultType.station, ResultType.structure_with_inlined_data], exact)
    elif groupID == appConst.groupFaction:
        result = searchUtil.GetResultsList(searchStr, [ResultType.faction], exact)
    elif groupID == appConst.groupSolarSystem:
        result = searchUtil.GetResultsList(searchStr, [ResultType.solar_system, ResultType.wormhole], exact)
    elif evetypes.GetCategoryIDByGroup(groupID) == appConst.categoryCelestial:
        result = sm.RemoteSvc('lookupSvc').LookupKnownLocationsByGroup(groupID, searchStr)
        result = [ each.itemID for each in result ]
        if result:
            cfg.evelocations.Prime(result)
    return result


def __ValidSearch(searchStr, getError, exact):
    searchStr = searchStr.replace('%', '').replace('?', '')
    if len(searchStr) < 1:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Common/PleaseTypeSomething')
        eve.Message('LookupStringMinimum', {'minimum': 1})
        return None
    if len(searchStr) >= 100 or exact == -1 and len(searchStr) > 5:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Common/SearchStringTooLong')
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Common/SearchStringTooLong')})
        return None
    bannedwords.check_search_words_allowed(searchStr)
    return searchStr


def Search(searchStr, groupID, categoryID = None, modal = 1, exact = MatchBy.partial_terms, getError = 0, notifyOneMatch = 0, filterCorpID = None, hideNPC = 0, searchWndName = 'mySearch', getWindow = 1, listType = None, hideDustChars = False):
    searchStr = __ValidSearch(searchStr, getError, exact)
    if not searchStr:
        return
    attrGroupName = {appConst.groupCharacter: 'Character',
     appConst.groupCorporation: 'Corporation',
     appConst.groupFaction: 'Faction',
     appConst.groupStation: 'Station',
     appConst.groupAsteroidBelt: 'Asteroid Belt',
     appConst.groupSolarSystem: 'SolarSystem',
     appConst.groupConstellation: 'Constellation',
     appConst.groupRegion: 'Region',
     appConst.groupAlliance: 'Alliance'}.get(groupID, '')
    attrLocGroupNamePlural = {appConst.groupCharacter: 'UI/Common/Characters',
     appConst.groupCorporation: 'UI/Common/Corporations',
     appConst.groupFaction: 'UI/Common/Factions',
     appConst.groupStation: 'UI/Common/Stations',
     appConst.groupAsteroidBelt: 'UI/Common/AsteroidBelts',
     appConst.groupSolarSystem: 'UI/Common/SolarSystems',
     appConst.groupConstellation: 'UI/Common/Constellations',
     appConst.groupRegion: 'UI/Common/Regions',
     appConst.groupAlliance: 'UI/Common/Alliances'}.get(groupID, '')
    if categoryID:
        if categoryID == appConst.categoryOwner:
            groupIDList = [ResultType.character, ResultType.corporation]
            if not hideNPC:
                groupIDList.append(ResultType.agent)
            result = searchUtil.GetResultsList(searchStr, groupIDList, exact, hideNPC=hideNPC)
            _PrimeSearchResultsInEveOwners(result)
            displayGroupName = localization.GetByLabel('UI/Common/Owner')
            displayGroupNamePlural = localization.GetByLabel('UI/Common/Owners')
        elif categoryID == appConst.categoryStructure:
            groupIDList = [ResultType.structure_with_inlined_data, ResultType.station]
            result = searchUtil.GetResultsList(searchStr, groupIDList, exact)
            displayGroupName = localization.GetByLabel('UI/Common/Location')
            displayGroupNamePlural = localization.GetByLabel('UI/Common/Locations')
    else:
        displayGroupName = evetypes.GetGroupNameByGroup(groupID)
        if attrGroupName and attrLocGroupNamePlural:
            displayGroupNamePlural = localization.GetByLabel(attrLocGroupNamePlural)
        else:
            displayGroupNamePlural = displayGroupName
        result = __Search(searchStr, groupID, exact, filterCorpID, hideNPC)
    if not result:
        sm.GetService('loading').StopCycle()
        if searchStr[-1] == '*':
            searchStr = searchStr[:-1]
        if getError:
            return localization.GetByLabel('UI/Search/NoGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)
        if exact and groupID == appConst.groupCharacter:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/NoCharacterFoundWith', searchTerm=searchStr)})
        else:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/NoGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)})
        return
    if len(result) == 1:
        if (categoryID == appConst.categoryStructure or groupID == appConst.groupStation) and getattr(result[0], 'structureID', None):
            return result[0].structureID
        if result[0] and modal:
            if notifyOneMatch:
                return (result[0], 1)
            return result[0]
        hint = localization.GetByLabel('UI/Search/OneGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)
    else:
        hint = localization.GetByLabel('UI/Search/ManyGroupsFoundWith', itemCount=len(result), groupNames=displayGroupNamePlural, searchTerm=searchStr)
    tmplist = []
    corpTickersToPrime = []
    for each in result:
        itemID = each
        if categoryID == appConst.categoryOwner:
            ownerData = cfg.eveowners.Get(each)
            if ownerData.typeID == appConst.typeCorporation:
                groupID = appConst.groupCorporation
            elif ownerData.typeID == appConst.typeAlliance:
                groupID = appConst.groupAlliance
            else:
                groupID = appConst.groupCharacter
        if groupID == appConst.groupCorporation:
            corpTickersToPrime.append(each)
        if groupID == appConst.groupCharacter and IsNPC(each):
            agentInfo = sm.GetService('agents').GetAgentByID(each)
            if agentInfo is not None and agentInfo.agentTypeID == appConst.agentTypeAura:
                if each != sm.GetService('agents').GetAuraAgentID():
                    continue
        if (categoryID == appConst.categoryStructure or groupID == appConst.groupStation) and not idCheckers.IsStation(each):
            typeID = each.typeID
            name = each.itemName
            itemID = each.structureID
        else:
            typeID = _GetType(each, groupID)
            name = _GetName(each, groupID)
        if each and name:
            tmplist.append((name, itemID, typeID or 0))

    cfg.corptickernames.Prime(corpTickersToPrime)
    sm.GetService('loading').StopCycle()
    if getWindow:
        selectionText = localization.GetByLabel('UI/Search/GenericSelection', groupName=displayGroupName)
        if listType is None:
            listType = attrGroupName.lower()
            if not listType:
                listType = 'Generic'
        chosen = ListWindow.ShowList(tmplist, listType, [displayGroupNamePlural, selectionText][modal], hint, 1, minChoices=modal, isModal=modal, windowName=searchWndName, unstackable=1)
        if chosen:
            return chosen[1]
    else:
        return tmplist


def _GetName(rec, groupID = None):
    if groupID in (appConst.groupCharacter,
     appConst.groupCorporation,
     appConst.groupFaction,
     appConst.groupAlliance):
        return cfg.eveowners.Get(rec).name
    if groupID in (appConst.groupStation,
     appConst.groupAsteroidBelt,
     appConst.groupSolarSystem,
     appConst.groupConstellation,
     appConst.groupRegion):
        return cfg.evelocations.Get(rec).name
    return ''


def _GetType(rec, groupID = None):
    if groupID in (appConst.groupCharacter,
     appConst.groupCorporation,
     appConst.groupFaction,
     appConst.groupAlliance):
        return cfg.eveowners.Get(rec).typeID
    if groupID == appConst.groupStation:
        return cfg.stations.Get(rec).stationTypeID
    if groupID == appConst.groupSolarSystem:
        return appConst.typeSolarSystem
    if groupID == appConst.groupConstellation:
        return appConst.typeConstellation
    if groupID == appConst.groupRegion:
        return appConst.typeRegion
    if groupID == appConst.groupAsteroidBelt:
        return appConst.typeAsteroidBelt
    return 0


def SearchOwners(searchStr, groupIDs = None, exact = False, notifyOneMatch = False, hideNPC = False, getError = False, searchWndName = 'mySearch'):
    if type(groupIDs) == int:
        groupIDs = [groupIDs]
    elif groupIDs is None:
        groupIDs = [appConst.groupCharacter,
         appConst.groupCorporation,
         appConst.groupAlliance,
         appConst.groupFaction]
    groupNames = {appConst.groupCharacter: [localization.GetByLabel('UI/Common/Character'), localization.GetByLabel('UI/Common/Characters')],
     appConst.groupCorporation: [localization.GetByLabel('UI/Common/Corporation'), localization.GetByLabel('UI/Common/Corporations')],
     appConst.groupAlliance: [localization.GetByLabel('UI/Common/Alliance'), localization.GetByLabel('UI/Common/Alliances')],
     appConst.groupFaction: [localization.GetByLabel('UI/Common/Faction'), localization.GetByLabel('UI/Common/Factions')]}
    searchStr = searchStr.replace('%', '').replace('?', '')
    if len(searchStr) < 1:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Common/PleaseTypeSomething')
        eve.Message('LookupStringMinimum', {'minimum': 1})
        return
    if len(searchStr) >= 100 or exact == -1 and len(searchStr) > 5:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Common/SearchStringTooLong')
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Common/SearchStringTooLong')})
        return
    displayGroupName = ''
    displayGroupNamePlural = ''
    for g in groupNames:
        if g in groupIDs:
            displayGroupName += groupNames[g][0] + '/'
            displayGroupNamePlural += groupNames[g][1] + '/'

    displayGroupName = displayGroupName[:-1]
    displayGroupNamePlural = displayGroupNamePlural[:-1]
    if hideNPC:
        owners = sm.RemoteSvc('lookupSvc').LookupPCOwners(searchStr, exact)
    else:
        owners = sm.RemoteSvc('lookupSvc').LookupOwners(searchStr, exact)
    list = []
    for o in owners:
        if o.groupID in groupIDs:
            list.append(('%s %s' % (o.ownerName, groupNames[o.groupID][0]), o.ownerID, o.typeID))

    if not list:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Search/NoGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/NoGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)})
        return
    if len(list) == 1 and not notifyOneMatch:
        return list[0][1]
    hint = localization.GetByLabel('UI/Search/ManyGroupsFoundWith', itemCount=len(list), groupNames=displayGroupNamePlural, searchTerm=searchStr)
    chosen = ListWindow.ShowList(lst=list, listtype='owner', caption=localization.GetByLabel('UI/Search/GenericSelection', groupName=displayGroupName), hint=hint, ordered=1, minChoices=1, windowName=searchWndName)
    if chosen:
        return chosen[1]
