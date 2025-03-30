#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\standingUtil.py
import math
from eve.common.lib import appConst
from eve.common.lib.appConst import factionsWhoseStandingsAreNotAffectedBySkillBonuses
from eve.common.script.sys import idCheckers
from npcs.npccorporations import get_corporation_faction_id
CRIMINAL_FACTIONS = (500010, 500011, 500012, 500019, 500020, 500029)
MAX_STANDING = 10.0
MIN_STANDING = -10.0

def GetStandingBonus(fromStanding, fromFactionID, skills):
    bonusType = GetStandingBonusSkillTypeID(GetFactionIDFromOwnerID(fromFactionID), fromStanding)
    bonus = 0.0
    if bonusType:
        skill = skills.get(bonusType, None)
        if skill:
            bonus = skill.effectiveSkillLevel * 0.4
    return (bonusType, bonus)


def GetStandingBonusSkillTypeID(fromFactionID, fromStanding):
    if fromFactionID in factionsWhoseStandingsAreNotAffectedBySkillBonuses:
        return
    elif fromStanding < 0.0:
        return appConst.typeDiplomacy
    elif fromFactionID is not None and fromFactionID in appConst.factionsPirates:
        return appConst.typeCriminalConnections
    else:
        return appConst.typeConnections


def ApplyBonusToStanding(bonus, standing):
    if not bonus:
        return standing
    return (1.0 - (1.0 - standing / 10.0) * (1.0 - bonus / 10.0)) * 10.0


def GetFactionIDFromOwnerID(ownerID):
    if idCheckers.IsCorporation(ownerID):
        return get_corporation_faction_id(ownerID)
    elif idCheckers.IsFaction(ownerID):
        return ownerID
    agent = sm.GetService('agents').GetAgentByID(ownerID)
    if agent is None:
        return
    else:
        return agent.factionID


def OpenStandingsPanelOnOwnerByID(ownerID):
    from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
    CharacterSheetWindow.OpenStandings()
    sm.ScatterEvent('OnNPCStandingsClicked', ownerID)


def CalculateStandingsByRawChange(currentStanding, rawChange):
    if rawChange > 0.0:
        if currentStanding < MAX_STANDING:
            return min(MAX_STANDING, 10.0 * (1.0 - (1.0 - currentStanding / 10.0) * (1.0 - rawChange)))
    elif currentStanding > MIN_STANDING:
        return max(MIN_STANDING, 10.0 * (currentStanding / 10.0 + (1.0 + currentStanding / 10.0) * rawChange))
    return currentStanding


def CalculateNewStandings(rawChange):
    return max(min(10.0 * rawChange, MAX_STANDING), MIN_STANDING)


def RoundStandingChange(modification):
    ret = round(modification, 3)
    return math.copysign(max(0.001, math.fabs(ret)), ret)
