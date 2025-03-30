#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\agents\agentUtil.py
import blue
import telemetry
from carbonui.util.color import Color
from eve.client.script.ui.station.agents.agentConst import MISSIONSTATELABELS, COLOR_ACCEPTED, COLOR_OFFERED, COLOR_EXPIRED
from eve.common.lib import appConst
from localization import GetByLabel
from npcs.npccorporations import get_corporation_faction_id
import eveformat.client
STORYLINE_AGENTS = (appConst.agentTypeGenericStorylineMissionAgent, appConst.agentTypeStorylineMissionAgent)
NORMAL_AGENTS = (appConst.agentTypeResearchAgent,
 appConst.agentTypeBasicAgent,
 appConst.agentTypeEventMissionAgent,
 appConst.agentTypeHeraldry)
AGENTS_IN_CORP_SHOW_INFO = (appConst.agentTypeResearchAgent,
 appConst.agentTypeBasicAgent,
 appConst.agentTypeFactionalWarfareAgent,
 appConst.agentTypeHeraldry)

def IsAgentAvailable(agentID):
    if sm.GetService('journal').IsMissionActiveWithAgent(agentID):
        return True
    agent = sm.GetService('agents').GetAgentByID(agentID)
    if not agent:
        return False
    if agent.agentTypeID in NORMAL_AGENTS:
        return IsAgentStandingSufficientToUse(agent)
    if agent.agentTypeID == appConst.agentTypeCareerAgent:
        return IsAgentStandingSufficientToUse(agent) and not sm.GetService('agents').IsCareerAgentCompleted(agentID)
    if agent.agentTypeID == appConst.agentTypeFactionalWarfareAgent:
        isLimitedToFacWar = False
        facWarSvc = sm.StartService('facwar')
        if agent.agentTypeID == appConst.agentTypeFactionalWarfareAgent and facWarSvc.GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
            isLimitedToFacWar = True
        standingIsSufficient = IsAgentStandingSufficientToUse(agent)
        return not isLimitedToFacWar and standingIsSufficient
    if agent.agentTypeID == appConst.agentTypeEpicArcAgent:
        standingIsSufficient = IsAgentStandingSufficientToUse(agent)
        epicArcStatusSvc = sm.RemoteSvc('epicArcStatus')
        return standingIsSufficient and epicArcStatusSvc.AgentHasEpicMissionsForCharacter(agent.agentID)
    if agent.agentTypeID == appConst.agentTypeAura:
        return False


def GetAgentUnavailableReason(agentID):
    if sm.GetService('journal').IsMissionActiveWithAgent(agentID):
        return None
    agent = sm.GetService('agents').GetAgentByID(agentID)
    if agent.agentTypeID in NORMAL_AGENTS:
        if not IsAgentStandingSufficientToUse(agent):
            return _GetInsufficientStandingsHint(agent)
    elif agent.agentTypeID == appConst.agentTypeCareerAgent:
        if sm.GetService('agents').IsCareerAgentCompleted(agentID):
            return GetByLabel('UI/Agents/CareerAgentCompleted')
        if not IsAgentStandingSufficientToUse(agent):
            return _GetInsufficientStandingsHint(agent)
    elif agent.agentTypeID == appConst.agentTypeFactionalWarfareAgent:
        facWarSvc = sm.GetService('facwar')
        if facWarSvc.GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
            return GetByLabel('UI/Agents/UnavailableRequiresFacWarfare', agent=agentID)
    elif agent.agentTypeID == appConst.agentTypeEpicArcAgent:
        epicArcStatusSvc = sm.RemoteSvc('epicArcStatus')
        if not epicArcStatusSvc.AgentHasEpicMissionsForCharacter(agent.agentID):
            return GetByLabel('UI/Agents/UnavailableRequiresReference', agent=agentID)
        if not IsAgentStandingSufficientToUse(agent):
            return _GetInsufficientStandingsHint(agent)
    elif agent.agentTypeID in (appConst.agentTypeStorylineMissionAgent, appConst.agentTypeGenericStorylineMissionAgent):
        return GetByLabel('UI/Agents/UnavailableRequiresReference', agent=agentID)


def GetAgentStartConversationHint(agentID):
    unavailableReason = GetAgentUnavailableReason(agentID)
    if unavailableReason:
        return unavailableReason
    else:
        return GetByLabel('UI/Chat/StartConversationAgent')


def _GetInsufficientStandingsHint(agent):
    requiredStanding = GetAgentStandingThreshold(agent.level)
    return GetByLabel('UI/Agents/UnavailableInsufficientStandings', agent=agent.agentID, requiredStanding=requiredStanding, minStanding=-2.0)


def IsAgentStandingSufficientToUse(agent):
    standingSvc = sm.GetService('standing')
    return standingSvc.CanUseAgent(agent.factionID, agent.corporationID, agent.agentID, agent.level, agent.agentTypeID)


def GetAgentStandingThreshold(level):
    if level == 1:
        return -10.0
    if level == 2:
        return 1.0
    if level == 3:
        return 3.0
    if level == 4:
        return 5.0
    if level == 5:
        return 7.0


def GetAgentDerivedStanding(agentID):
    standings = _GetAgentDerivedStandingsList(agentID)
    if standings[-1][0] <= -2.0:
        return standings[-1]
    else:
        return standings[0]


def _GetAgentDerivedStandingsList(agentID):
    standingSvc = sm.GetService('standing')
    agentInfo = sm.GetService('agents').GetAgentByID(agentID)
    standings = [(standingSvc.GetStandingWithSkillBonus(agentInfo.factionID, session.charid), agentInfo.factionID), (standingSvc.GetStandingWithSkillBonus(agentInfo.corporationID, session.charid), agentInfo.corporationID), (standingSvc.GetStandingWithSkillBonus(agentInfo.agentID, session.charid), agentInfo.agentID)]
    return sorted(standings, reverse=True)


def GetNPCCorpDerivedStanding(corpID):
    standingSvc = sm.GetService('standing')
    factionID = get_corporation_faction_id(corpID)
    standings = [(standingSvc.GetStandingWithSkillBonus(factionID, session.charid), factionID), (standingSvc.GetStandingWithSkillBonus(corpID, session.charid), corpID)]
    standings.sort()
    return standings[-1]


@telemetry.ZONE_METHOD
def GetAgentDerivedStandingsSortedList(agentID):
    standingList = _GetAgentDerivedStandingsList(agentID)
    return [ standing for standing, _ in standingList ]


def GetAgentLocationText(solarSystemID):
    return eveformat.solar_system_with_security_and_jumps(solarSystemID)


def GetMissionExpirationAndStateText(missionState, expirationTime):
    if missionState in (appConst.agentMissionStateAllocated, appConst.agentMissionStateOffered):
        stateText = '<color=0xFFFFFF00>' + MISSIONSTATELABELS[missionState] + '<color=0xffffffff>'
        if expirationTime > blue.os.GetWallclockTime() + appConst.WEEK + appConst.MIN:
            expirationText = GetByLabel('UI/Journal/JournalWindow/Agents/OfferExpiresAt', expirationTime=expirationTime)
        elif expirationTime > blue.os.GetWallclockTime() + appConst.DAY:
            expirationText = GetByLabel('UI/Journal/JournalWindow/Agents/OfferExpiresAtExact', expirationTime=expirationTime)
        else:
            if expirationTime:
                expirationTime -= blue.os.GetWallclockTime()
                expirationTime = int(expirationTime / appConst.MIN) * appConst.MIN
            if expirationTime == 0:
                expirationText = GetByLabel('UI/Journal/JournalWindow/Agents/OfferDoesNotExpire')
            elif not expirationTime:
                expirationText = GetByLabel('UI/Journal/JournalWindow/Agents/OfferUndefinedExpiration')
            elif expirationTime > 0:
                expirationText = GetByLabel('UI/Journal/JournalWindow/Agents/OfferExpiresIn', expirationTime=expirationTime)
            else:
                expirationText = GetByLabel('UI/Journal/JournalWindow/Agents/OfferExpired')
                stateText = '<color=0xffeb3700>' + GetByLabel('UI/Journal/JournalWindow/Agents/StateOfferExpired') + '<color=0xffffffff>'
    elif missionState in (appConst.agentMissionStateAccepted, appConst.agentMissionStateFailed):
        if missionState == appConst.agentMissionStateAccepted:
            stateText = '<color=0xff00FF00>' + MISSIONSTATELABELS[missionState] + '<color=0xffffffff>'
        else:
            stateText = '<color=0xffeb3700>' + MISSIONSTATELABELS[missionState] + '<color=0xffffffff>'
        if expirationTime > blue.os.GetWallclockTime() + appConst.WEEK + appConst.MIN:
            expirationText = GetByLabel('UI/Journal/JournalWindow/Agents/MissionExpiresAt', expirationTime=expirationTime)
        elif expirationTime > blue.os.GetWallclockTime() + appConst.DAY:
            expirationText = GetByLabel('UI/Journal/JournalWindow/Agents/MissionExpiresAtExact', expirationTime=expirationTime)
        else:
            if expirationTime:
                expirationTime -= blue.os.GetWallclockTime()
                expirationTime = int(expirationTime / appConst.MIN) * appConst.MIN
            if expirationTime == 0:
                expirationText = GetByLabel('UI/Journal/JournalWindow/Agents/MissionDoesNotExpire')
            elif not expirationTime:
                expirationText = GetByLabel('UI/Journal/JournalWindow/Agents/MissionUndefinedExpiration')
            elif expirationTime > 0:
                expirationText = GetByLabel('UI/Journal/JournalWindow/Agents/MissionExpiresIn', expirationTime=expirationTime)
            else:
                expirationText = GetByLabel('UI/Journal/JournalWindow/Agents/MissionExpired')
                stateText = '<color=0xffeb3700>' + GetByLabel('UI/Journal/JournalWindow/Agents/StateMissionExpired') + '<color=0xffffffff>'
    else:
        stateText = expirationText = ''
    return (stateText, expirationText)


def GetMissionExpirationText(missionState, expirationTime, short = False):
    if missionState in (appConst.agentMissionStateAllocated, appConst.agentMissionStateOffered):
        if expirationTime:
            expirationTime -= blue.os.GetWallclockTime()
        if expirationTime == 0:
            return GetByLabel('UI/Journal/JournalWindow/Agents/OfferDoesNotExpire')
        elif not expirationTime:
            return GetByLabel('UI/Journal/JournalWindow/Agents/OfferUndefinedExpiration')
        elif expirationTime > 0:
            if short:
                return GetByLabel('UI/Agency/ExpiresIn', remaining=expirationTime)
            return GetByLabel('UI/Journal/JournalWindow/Agents/OfferExpiresIn', expirationTime=expirationTime)
        else:
            return GetByLabel('UI/Journal/JournalWindow/Agents/OfferExpired')
    elif missionState in (appConst.agentMissionStateAccepted, appConst.agentMissionStateFailed):
        if expirationTime:
            expirationTime -= blue.os.GetWallclockTime()
        if expirationTime == 0:
            return GetByLabel('UI/Journal/JournalWindow/Agents/MissionDoesNotExpire')
        elif not expirationTime:
            return GetByLabel('UI/Journal/JournalWindow/Agents/MissionUndefinedExpiration')
        elif expirationTime > 0:
            if short:
                return GetByLabel('UI/Agency/ExpiresIn', remaining=expirationTime)
            return GetByLabel('UI/Journal/JournalWindow/Agents/MissionExpiresIn', expirationTime=expirationTime)
        else:
            return GetByLabel('UI/Journal/JournalWindow/Agents/MissionExpired')
    else:
        return ''


def GetMissionStateText(missionState, expirationTime):
    if missionState in (appConst.agentMissionStateAllocated, appConst.agentMissionStateOffered):
        if expirationTime < 0:
            return GetByLabel('UI/Journal/JournalWindow/Agents/StateOfferExpired')
        else:
            return MISSIONSTATELABELS[missionState]
    elif missionState in (appConst.agentMissionStateAccepted, appConst.agentMissionStateFailed):
        if expirationTime < 0:
            GetByLabel('UI/Journal/JournalWindow/Agents/StateMissionExpired')
        else:
            return MISSIONSTATELABELS[missionState]
    else:
        return ''


def GetMissionStateColor(missionState, expirationTime):
    if missionState in (appConst.agentMissionStateAllocated, appConst.agentMissionStateOffered):
        if expirationTime < 0:
            return COLOR_EXPIRED
        else:
            return COLOR_OFFERED
    elif missionState in (appConst.agentMissionStateAccepted, appConst.agentMissionStateFailed):
        if expirationTime < 0:
            return COLOR_EXPIRED
        else:
            return COLOR_ACCEPTED
    else:
        return Color.WHITE
