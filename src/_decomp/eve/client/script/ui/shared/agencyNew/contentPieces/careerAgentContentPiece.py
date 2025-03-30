#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\careerAgentContentPiece.py
import uuid
import eve.common.lib.appConst as appConst
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.agentContentPiece import AgentContentPiece
from eve.client.script.ui.shared.careerPortal import careerConst
from eve.client.script.ui.skillPlan.link import skillplan_link
from evemissions.client.const import CAREER_PATH_BY_DIVISION
from localization import GetByLabel
from npcs.divisions import get_division_description
from npcs.divisions import get_division_name
from skills.skillplan.skillPlanService import GetSkillPlanSvc
BLURB_LABEL_BY_DIVISION = {appConst.agentDivisionBusiness: 'UI/Agency/Blurbs/CareerAgentBusiness',
 appConst.agentDivisionExploration: 'UI/Agency/Blurbs/CareerAgentExploration',
 appConst.agentDivisionIndustry: 'UI/Agency/Blurbs/CareerAgentIndustry',
 appConst.agentDivisionMilitary: 'UI/Agency/Blurbs/CareerAgentMilitary',
 appConst.agentDivisionAdvMilitary: 'UI/Agency/Blurbs/CareerAgentAdvMilitary'}
skillPlansByRaceAndDivision = {(appConst.raceAmarr, appConst.agentDivisionBusiness): uuid.UUID(int=47),
 (appConst.raceAmarr, appConst.agentDivisionExploration): uuid.UUID(int=42),
 (appConst.raceAmarr, appConst.agentDivisionIndustry): uuid.UUID(int=46),
 (appConst.raceAmarr, appConst.agentDivisionMilitary): uuid.UUID(int=34),
 (appConst.raceAmarr, appConst.agentDivisionAdvMilitary): uuid.UUID(int=38),
 (appConst.raceCaldari, appConst.agentDivisionBusiness): uuid.UUID(int=47),
 (appConst.raceCaldari, appConst.agentDivisionExploration): uuid.UUID(int=43),
 (appConst.raceCaldari, appConst.agentDivisionIndustry): uuid.UUID(int=46),
 (appConst.raceCaldari, appConst.agentDivisionMilitary): uuid.UUID(int=35),
 (appConst.raceCaldari, appConst.agentDivisionAdvMilitary): uuid.UUID(int=39),
 (appConst.raceGallente, appConst.agentDivisionBusiness): uuid.UUID(int=47),
 (appConst.raceGallente, appConst.agentDivisionExploration): uuid.UUID(int=44),
 (appConst.raceGallente, appConst.agentDivisionIndustry): uuid.UUID(int=46),
 (appConst.raceGallente, appConst.agentDivisionMilitary): uuid.UUID(int=36),
 (appConst.raceGallente, appConst.agentDivisionAdvMilitary): uuid.UUID(int=40),
 (appConst.raceMinmatar, appConst.agentDivisionBusiness): uuid.UUID(int=47),
 (appConst.raceMinmatar, appConst.agentDivisionExploration): uuid.UUID(int=45),
 (appConst.raceMinmatar, appConst.agentDivisionIndustry): uuid.UUID(int=46),
 (appConst.raceMinmatar, appConst.agentDivisionMilitary): uuid.UUID(int=37),
 (appConst.raceMinmatar, appConst.agentDivisionAdvMilitary): uuid.UUID(int=41)}
sortOrder = [appConst.agentDivisionMilitary,
 appConst.agentDivisionIndustry,
 appConst.agentDivisionExploration,
 appConst.agentDivisionAdvMilitary,
 appConst.agentDivisionBusiness]

class CareerAgentContentPiece(AgentContentPiece):
    contentType = agencyConst.CONTENTTYPE_CAREERAGENTS

    def GetCareerAgentPathName(self):
        divisionID = self.GetDivisionID()
        if divisionID in appConst.agentDivisionsCareer:
            return get_division_name(divisionID)

    def GetCareerAgentDescription(self):
        divisionID = self.GetDivisionID()
        if divisionID in appConst.agentDivisionsCareer:
            return get_division_description(divisionID)

    def _GetDivisionSortKey(self):
        return -1

    def GetCardSortValue(self):
        divisionID = self.GetDivisionID()
        if divisionID in sortOrder:
            return sortOrder.index(divisionID)

    def GetBlurbText(self):
        divisionID = self.agent.divisionID
        if divisionID in BLURB_LABEL_BY_DIVISION:
            labelPath = BLURB_LABEL_BY_DIVISION[divisionID]
            return GetByLabel(labelPath)

    def IsCareerAgent(self):
        return True

    def GetCareerTexturePath(self):
        divisionID = self.agent.divisionID
        careerID = CAREER_PATH_BY_DIVISION.get(divisionID, None)
        if not careerID:
            return
        texturePath = careerConst.CAREERS_32_SIZES.get(careerID, None)
        return texturePath

    def SkillPlanLink(self):
        divisionID = self.agent.divisionID
        factionID = self.agent.factionID
        if not factionID:
            return
        raceID = appConst.raceByFaction.get(factionID)
        if not raceID:
            return
        planID = skillPlansByRaceAndDivision.get((raceID, divisionID), None)
        if not planID:
            return
        skillPlan = GetSkillPlanSvc().GetCertifiedSkillPlan(planID)
        if not skillPlan:
            return
        return skillplan_link(planID, skillPlan.GetName())
