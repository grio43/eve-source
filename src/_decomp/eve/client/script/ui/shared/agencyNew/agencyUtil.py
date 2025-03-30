#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\agencyUtil.py
import itertools
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.standings.standingUIConst import THRESHOLD_VALUES_BY_THRESHOLDTYPE, THRESHOLDS_FACTIONORCORPWITHAGENTS, AGENT_LEVEL_BY_THRESHOLD_ID
from eve.common.script.sys import idCheckers
from eve.common.script.util.eveCommonUtils import lerp_color
from localization import GetByLabel
trainingDaysOverride = None

def GetRoundRobinMix(iterables, numMax = -1):
    pending = len(iterables)
    nexts = itertools.cycle((it.next for it in iterables))
    while pending and numMax:
        try:
            for next in nexts:
                yield next()
                if numMax is not None:
                    numMax -= 1
                    if not numMax:
                        return

        except StopIteration:
            pending -= 1
            nexts = itertools.cycle(itertools.islice(nexts, pending))


def GetRewardHint(rewardType, ownerID = None):
    label = agencyConst.HINT_BY_REWARDTYPE[rewardType]
    ownerName = cfg.eveowners.Get(ownerID).ownerName if ownerID else None
    if label:
        return GetByLabel(label, ownerName=ownerName)


def GetUnlockedAgents(fromID, newStanding, oldStanding):
    standingThresholdByThresholdID = {thresholdID:THRESHOLD_VALUES_BY_THRESHOLDTYPE[thresholdID] for thresholdID in THRESHOLDS_FACTIONORCORPWITHAGENTS}
    thresholdOvertaken = next(((thresholdID, threshold) for thresholdID, threshold in standingThresholdByThresholdID.iteritems() if oldStanding <= threshold <= newStanding), None)
    if thresholdOvertaken:
        agentLvlUnlocked = AGENT_LEVEL_BY_THRESHOLD_ID[thresholdOvertaken[0]]
        if idCheckers.IsFaction(fromID):
            allAgentsInFaction = sm.GetService('agents').GetAgentsByFactionID(fromID).Clone()
            allAgentsInFactionOfUnlockedLvl = allAgentsInFaction.Filter('level')[agentLvlUnlocked]
            return allAgentsInFactionOfUnlockedLvl
        if idCheckers.IsNPCCorporation(fromID):
            allAgentsInCorp = sm.GetService('agents').GetAgentsByCorpID(fromID).Clone()
            allAgentsInCorpOfUnlockedLvl = allAgentsInCorp.Filter('level')[agentLvlUnlocked]
            return allAgentsInCorpOfUnlockedLvl
    return []


def CheckTrainingDaysAbove(minDays):
    return True


def CheckTrainingDaysBelow(maxDays):
    pass


def GetTrainingDaysTotal():
    if trainingDaysOverride is not None:
        return trainingDaysOverride
    sp = sm.GetService('skills').GetTotalSkillPointsForCharacter()
    return SkillPointsToTrainingDays(sp)


def SkillPointsToTrainingDays(sp):
    return (sp - 366000) / 40000.0


def IsNewAgencyEnabled():
    return True


def GetTimeRemainingText(remaining):
    if remaining > 0:
        return GetByLabel('UI/Agency/ExpiresIn', remaining=remaining)
    else:
        return GetByLabel('UI/Inflight/Scanner/Expired')


def GetESSBountyColor(minBountyOutput, maxBountyOutput, equilibriumValue, bountiesOutput):
    if equilibriumValue <= bountiesOutput <= maxBountyOutput:
        newColor = lerp_color(max(bountiesOutput - equilibriumValue, 0), max(maxBountyOutput - equilibriumValue, 0), start_point=agencyConst.ESS_EQUILIBRIUM_PAYOUT_COLOR, end_point=agencyConst.ESS_HIGH_PAYOUT_COLOR)
    elif minBountyOutput <= bountiesOutput <= equilibriumValue / 2:
        newColor = lerp_color(max(bountiesOutput - equilibriumValue, 0), max(maxBountyOutput - equilibriumValue, 0), start_point=agencyConst.ESS_LOW_PAYOUT_COLOR, end_point=agencyConst.ESS_MEDIUM_PAYOUT_COLOR)
    else:
        newColor = lerp_color(bountiesOutput, maxBountyOutput, start_point=agencyConst.ESS_MEDIUM_PAYOUT_COLOR, end_point=agencyConst.ESS_EQUILIBRIUM_PAYOUT_COLOR)
    return newColor


def GetNumberOfJumps(solarSystemID):
    return sm.GetService('clientPathfinderService').GetAutopilotJumpCount(fromID=session.solarsystemid2, toID=solarSystemID)


def IsAvoidanceSystem(solarSystemID):
    return solarSystemID in sm.GetService('clientPathfinderService').GetExpandedAvoidanceItems()


def GetSystemsWithinJumpRange(fromID, jumpCountMin, jumpCountMax, shouldIncludeAvoided = False):
    pathFinderService = sm.GetService('clientPathfinderService')
    inRange = pathFinderService.GetSystemsWithinAutopilotJumpRange(fromID, jumpCountMin, jumpCountMax)
    if shouldIncludeAvoided:
        allAvoidedSolarSystemIDs = pathFinderService.GetExpandedAvoidanceItems()
        for solarSystemID in allAvoidedSolarSystemIDs:
            jumps = GetNumberOfJumps(solarSystemID)
            if solarSystemID in inRange[jumps]:
                continue
            if jumpCountMin <= jumps < jumpCountMax:
                inRange[jumps].append(solarSystemID)

    return inRange


def GetNoRouteFoundText(solarSystemID):
    return sm.GetService('clientPathfinderService').GetNoRouteFoundTextAutopilot(solarSystemID)
