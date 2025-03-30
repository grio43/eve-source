#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\standings\standingsUIUtil.py
import inventorycommon.const as invconst
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.standings import standingUIConst
from eve.client.script.ui.shared.standings.standingData import StandingData
from eve.client.script.ui.shared.standings.standingEntry import StandingEntry
from eve.client.script.ui.shared.standings.standingsUtil import RoundStandingTo10
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from eve.common.script.util import standingUtil
from localization import GetByLabel
from npcs.npccorporations import get_corporation_faction_id
import evestations.standingsrestriction
THRESHOLD_BAD = 0.0
STANDING_SETTING_CONFIG_NAME = 'charactersheetStandingsPanelOwner'

def GetStandingScrollGroups(standings, ownerID, searchText = ''):
    scrollList = []
    for each in CategoriseStandingsByOwnerType(ownerID, standings):
        if each:
            label = ''
            groupID = each[0][1].groupID
            if groupID == invconst.groupFaction:
                label = GetByLabel('UI/Common/Factions')
            elif groupID == invconst.groupCorporation:
                label = GetByLabel('UI/Common/Corporations')
            elif idCheckers.IsNPC(each[0][1].id):
                label = GetByLabel('UI/Common/Agents')
            if searchText:
                standingEntries = [ entry[2] for entry in each if search_entry(entry[2], searchText.lower()) >= 0 ]
            else:
                standingEntries = [ entry[2] for entry in each ]
            if standingEntries:
                scrollList.append(GetFromClass(ListGroup, {'GetSubContent': GetStandingScrollGroupSubContent,
                 'label': label,
                 'entries': standingEntries,
                 'id': ('groupID', each[0][1].groupID),
                 'tabs': [],
                 'state': 'locked',
                 'showicon': 'hide',
                 'showlen': 0,
                 'openByDefault': True,
                 'BlockOpenWindow': True}))

    return scrollList


def search_entry(entry, searchText):
    name = entry.standingData.GetOwner2Name().lower()
    find_result = name.find(searchText)
    return find_result


def GetStandingScrollGroupSubContent(data, *args):
    scrollList = []
    for entry in data.entries:
        scrollList.append(entry)

    return scrollList


def AppendEntriesSection(listEntries, scrolllist, label):
    if listEntries:
        scrolllist.append(GetFromClass(Header, {'label': GetByLabel(label)}))
        for listEntry in listEntries:
            scrolllist.append(listEntry[2])


def CategoriseStandingsByOwnerType(toID, standings):
    factions = []
    alliances = []
    corps = []
    chars = []
    agents = []
    for each in standings:
        standing = each[1]
        ownerID = each[0]
        ownerinfo = cfg.eveowners.Get(ownerID)
        entry = (round(standing, 2), ownerinfo, GetStandingEntry(ownerID, toID, standing))
        if ownerinfo.groupID == invconst.groupFaction:
            factions.append(entry)
        elif ownerinfo.groupID == invconst.groupCorporation:
            corps.append(entry)
        elif idCheckers.IsNPC(ownerID):
            if sm.GetService('agents').GetAgentByID(ownerID) is None:
                continue
            agents.append(entry)

    return (factions,
     corps,
     agents,
     alliances,
     chars)


def GetStandingEntry(ownerID, toID, standing):
    standing = RoundStandingTo10(standing)

    def OnClick(node):
        if node.standingData:
            ownerID = node.standingData.GetOwnerID2()
            settings.char.ui.Set(STANDING_SETTING_CONFIG_NAME, ownerID)

    return GetFromClass(StandingEntry, {'standingData': StandingData(toID, ownerID, standing2to1=standing),
     'OnClick': OnClick})


def GetStandingSkillBonus(standing, fromID, toID):
    bonus = None
    relevantSkills = {}
    if toID == session.charid and idCheckers.IsNPC(fromID):
        if idCheckers.IsCorporation(fromID):
            fromFactionID = get_corporation_faction_id(fromID)
        elif idCheckers.IsFaction(fromID):
            fromFactionID = fromID
        else:
            agent = sm.GetService('agents').GetAgentByID(fromID)
            if agent is None:
                fromFactionID = None
            else:
                fromFactionID = agent.factionID
        skillSvc = sm.GetService('skills')
        for skillTypeID in (invconst.typeDiplomacy, invconst.typeConnections, invconst.typeCriminalConnections):
            skill = skillSvc.GetSkill(skillTypeID)
            if skill is not None:
                relevantSkills[skillTypeID] = skill

        _, bonus = standingUtil.GetStandingBonus(standing, fromFactionID, relevantSkills)
    return bonus


def GetStandingColor(standing):
    if standing < THRESHOLD_BAD:
        return standingUIConst.COLOR_BAD
    else:
        return standingUIConst.COLOR_GOOD


def GetStandingIconTexturePath(standing):
    if standing < THRESHOLD_BAD:
        return 'res:/UI/Texture/Icons/38_16_229.png'
    else:
        return 'res:/UI/Texture/Icons/38_16_230.png'


def GetStandingActionIDs(ownerID):
    if not idCheckers.IsNPC(ownerID):
        return []
    if idCheckers.IsFaction(ownerID):
        actions = list(standingUIConst.ACTIONS_FACTION)
        if ownerID in appConst.factionsEmpires:
            actions.append(standingUIConst.ACTION_FACTIONALWARFARE)
        return actions
    if idCheckers.IsCorporation(ownerID):
        return standingUIConst.ACTIONS_NPCCORPS
    if idCheckers.IsNPCCharacter(ownerID):
        return standingUIConst.ACTIONS_AGENTS


def GetStandingBenefitIDs(ownerID):
    if not idCheckers.IsNPC(ownerID):
        return []
    elif idCheckers.IsFaction(ownerID):
        return standingUIConst.BENEFITS_FACTION
    elif idCheckers.IsCorporation(ownerID):
        return standingUIConst.BENEFITS_NPCCORP
    else:
        return []


def GetStandingEventIcon(eventID):
    actionID = standingUIConst.ACTIONID_BY_EVENTID.get(eventID, standingUIConst.ACTION_OTHER)
    return standingUIConst.ICONS_BY_ACTIONID.get(actionID, None)


def GetStandingThresholdIDs(fromID, toID):
    if not idCheckers.IsNPC(fromID):
        return []
    if idCheckers.IsCorporation(toID):
        ids = []
        if fromID in appConst.factionsEmpires:
            ids = [(standingUIConst.THRESHOLD_FACTIONALWARFARE, toID)]
        ids.extend(_GetStationServiceThresholdIDs(fromID, True))
        return ids
    if idCheckers.IsFaction(fromID):
        return _GetFactionStandingThresholdIDs(fromID)
    if IsResourceWarsCorporation(fromID):
        return _GetResourceWarsStandingThresholdIDs(fromID)
    if idCheckers.IsCorporation(fromID):
        return _GetNPCCorpStandingThresholdIDs(fromID)
    if idCheckers.IsNPCCharacter(fromID):
        return _GetAgentStandingThresholdIDs(fromID)


def _TresholdTypeIDsToThresholdIDs(thresholdIDs):
    return [ (thresholdID, None) for thresholdID in thresholdIDs ]


def _GetNPCCorpStandingThresholdIDs(fromID):
    agents = sm.GetService('agents').GetAgentsByCorpID(fromID)
    thresholdIDs = []
    if agents:
        thresholdIDs.extend(_TresholdTypeIDsToThresholdIDs(standingUIConst.THRESHOLDS_FACTIONORCORPWITHAGENTS))
    thresholdIDs.extend(_GetEpicArcThresholdIDs(fromID))
    return thresholdIDs


def _GetAgentStandingThresholdIDs(fromID):
    agent = sm.GetService('agents').GetAgentByID(fromID)
    if agent.level > 1:
        return [(standingUIConst.THRESHOLD_NOACCESSTOAGENT, None), (standingUIConst.THRESHOLD_AGENTOFFERSMISSIONS, agent.level)]
    else:
        return []


def _GetFactionStandingThresholdIDs(fromID):
    thresholdIDs = _TresholdTypeIDsToThresholdIDs(standingUIConst.THRESHOLDS_FACTION)
    if fromID in appConst.factionsEmpires:
        thresholdIDs.append((standingUIConst.THRESHOLD_FACTIONALWARFARE, None))
    if fromID not in appConst.factionsWithoutAgents:
        thresholdIDs.extend(_TresholdTypeIDsToThresholdIDs(standingUIConst.THRESHOLDS_FACTIONORCORPWITHAGENTS))
    thresholdIDs.extend(_GetEpicArcThresholdIDs(fromID))
    thresholdIDs.extend(_GetStationServiceThresholdIDs(fromID))
    return thresholdIDs


def _GetEpicArcThresholdIDs(ownerID):
    ret = []
    for agentID in standingUIConst.EPIC_ARC_STARTER_AGENTS:
        agent = sm.GetService('agents').GetAgentByID(agentID)
        if ownerID in (agent.factionID, agent.corporationID):
            ret.append((standingUIConst.THRESHOLD_EPICARCUNLOCK, agentID))

    return ret


def GetEpicArcThresholdIDs(ownerID):
    for agentID in standingUIConst.EPIC_ARC_STARTER_AGENTS:
        agent = sm.GetService('agents').GetAgentByID(agentID)
        if agent.factionID == ownerID:
            pass


def _GetResourceWarsStandingThresholdIDs(ownerID):
    return _TresholdTypeIDsToThresholdIDs(standingUIConst.THRESHOLDS_RESOURCE_WARS)


def _GetStationServiceThresholdIDs(ownerID, forCorporation = False):
    thresholdIDs = []
    if forCorporation:
        thresholdTypeID = standingUIConst.THRESHOLD_STATIONSERVICE_CORPORATION
        restrictions = evestations.standingsrestriction.get_all_station_standings_restrictions_corporate(ownerID)
    else:
        thresholdTypeID = standingUIConst.THRESHOLD_STATIONSERVICE
        restrictions = evestations.standingsrestriction.get_all_station_standings_restrictions_personal(ownerID)
    groups = set()
    for serviceID, standingsValue in restrictions.iteritems():
        roundedValue = round(standingsValue) + 0
        groups.add(roundedValue)

    for group in groups:
        thresholdIDs.append((thresholdTypeID, group))

    return thresholdIDs


def GetStandingThresholdIcon(thresholdID):
    thresholdTypeID = thresholdID[0]
    if thresholdTypeID == standingUIConst.THRESHOLD_AGENTOFFERSMISSIONS:
        agentLvl = thresholdID[1]
        if agentLvl == 2:
            return 'res:/UI/Texture/Classes/Standings/Thresholds/agentsLvl2.png'
        if agentLvl == 3:
            return 'res:/UI/Texture/Classes/Standings/Thresholds/agentsLvl3.png'
        if agentLvl == 4:
            return 'res:/UI/Texture/Classes/Standings/Thresholds/agentsLvl4.png'
        if agentLvl == 5:
            return 'res:/UI/Texture/Classes/Standings/Thresholds/agentsLvl5.png'
    else:
        return standingUIConst.ICONS_BY_THRESHOLDTYPEID.get(thresholdTypeID, None)


def GetBGOpacity(isEvenRow):
    if isEvenRow:
        return 0.15
    return 0.25


def IsResourceWarsCorporation(corpID):
    return sm.GetService('rwService').is_rw_corporation(corpID)


def GetStationServiceRestrictionsForThreshold(ownerID, thresholdValue, thresholdTypeID):
    if thresholdTypeID == standingUIConst.THRESHOLD_STATIONSERVICE_CORPORATION:
        restrictions = evestations.standingsrestriction.get_all_station_standings_restrictions_corporate(ownerID)
    else:
        restrictions = evestations.standingsrestriction.get_all_station_standings_restrictions_personal(ownerID)
    values = []
    for serviceID, standingsValue in restrictions.iteritems():
        roundedValue = round(standingsValue) + 0
        if roundedValue != thresholdValue:
            continue
        values.append((round(standingsValue, 2), serviceID))

    values.sort()
    return values


def GetStationServiceLabel(serviceID):
    return GetByLabel(evestations.standingsrestriction.get_station_standings_restriction_label(serviceID))
