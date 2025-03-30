#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\standings\standingData.py
import inventorycommon.const as invconst
from carbonui.util.color import Color
from eve.client.script.ui.shared.standings import standingUIConst
from eve.client.script.ui.station.agents.agentDialogueUtil import GetAgentNameAndLevel
from eve.common.script.util import standingUtil
from eve.common.script.util.standingUtil import GetStandingBonusSkillTypeID, GetFactionIDFromOwnerID
STANDINGS_SKILLS = (invconst.typeDiplomacy, invconst.typeConnections, invconst.typeCriminalConnections)

class StandingData(object):

    def __init__(self, ownerID1, ownerID2, standing1to2 = None, standing2to1 = None, standingIncrease = None):
        self.ownerID1 = ownerID1
        self.ownerID2 = ownerID2
        self.standing1to2 = standing1to2
        self.standing2to1 = standing2to1
        self.standingIncrease = standingIncrease
        if standing1to2 is None and standing2to1 is None:
            raise ValueError('No standings set')

    def GetOwnerID1(self):
        return self.ownerID1

    def GetOwnerID2(self):
        return self.ownerID2

    def GetStanding2To1(self):
        return self._GetStandingWithBonus(self.ownerID2, self.ownerID1, self.standing2to1)

    def GetStanding1To2(self):
        return self._GetStandingWithBonus(self.ownerID1, self.ownerID2, self.standing1to2)

    def GetStandingIncrease(self):
        if self.standingIncrease > 0.01:
            return min(self.standingIncrease, 10.0)
        return 0.0

    def GetOwner1Name(self):
        return self._GetOwnerName(self.ownerID1)

    def GetOwner2Name(self):
        return self._GetOwnerName(self.ownerID2)

    def GetSkillTypeID1To2(self):
        factionID = GetFactionIDFromOwnerID(self.ownerID1)
        return GetStandingBonusSkillTypeID(factionID, self.standing1to2)

    def GetSkillTypeID2To1(self):
        factionID = GetFactionIDFromOwnerID(self.ownerID2)
        return GetStandingBonusSkillTypeID(factionID, self.standing2to1)

    def _GetOwnerName(self, ownerID):
        agentsSvc = sm.GetService('agents')
        if agentsSvc.IsAgent(ownerID):
            agent = agentsSvc.GetAgentByID(ownerID)
            return GetAgentNameAndLevel(ownerID, agent.level)
        else:
            return cfg.eveowners.Get(ownerID).ownerName

    def GetOwner1TypeID(self):
        return cfg.eveowners.Get(self.ownerID1).typeID

    def GetOwner2TypeID(self):
        return cfg.eveowners.Get(self.ownerID2).typeID

    def _GetStandingWithBonus(self, fromID, toID, standing):
        if toID == session.charid:
            _, bonus = standingUtil.GetStandingBonus(standing, fromID, self.GetStandingsSkills())
        else:
            bonus = 0.0
        return standingUtil.ApplyBonusToStanding(bonus, standing)

    def GetStandingBonus2To1(self):
        bonus = round(self.GetStanding2To1() - self.standing2to1, 2)
        bonus = bonus if bonus > 0.0 else 0.0
        return bonus

    def GetStandingBonus1To2(self):
        bonus = round(self.GetStanding1To2() - self.standing1to2, 2)
        bonus = bonus if bonus > 0.0 else 0.0
        return bonus

    @staticmethod
    def GetStandingsSkills():
        skills = {}
        skillSvc = sm.GetService('skills')
        for skillTypeID in STANDINGS_SKILLS:
            skill = skillSvc.GetSkill(skillTypeID)
            if skill is not None:
                skills[skillTypeID] = skill

        return skills

    def GetStanding1To2Formatted(self):
        return self._GetStandingFormatted(self.GetStanding1To2())

    def GetStanding2To1Formatted(self):
        return self._GetStandingFormatted(self.GetStanding2To1())

    @staticmethod
    def _GetStandingFormatted(standing):
        if standing >= 9.995:
            standing = 10.0
        return round(standing, 2)

    @staticmethod
    def GetStandingColor(standing):
        if standing < -2.0:
            color = standingUIConst.COLOR_BAD
        elif standing < 2.0:
            color = standingUIConst.COLOR_NEUTRAL
        else:
            color = standingUIConst.COLOR_GOOD
        return Color.RGBtoHex(*color)

    def IsRightToLeft(self):
        return self.standing2to1 is not None and self.standing1to2 is None

    def IsTwoWay(self):
        return self.standing1to2 is not None and self.standing2to1 is not None

    def GetHint1To2(self):
        return self.GetStanding1To2Formatted()

    def GetHint2To1(self):
        return self.GetStanding2To1Formatted()
