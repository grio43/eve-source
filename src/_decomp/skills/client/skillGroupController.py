#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\client\skillGroupController.py
import telemetry
import evetypes
from characterskills import GetSkillPointsPerMinute
from clonegrade.const import CLONE_STATE_ALPHA
from skills.skillConst import ICON_BY_GROUPID, DESCRIPTION_BY_GROUPID, FILTER_SHOWALL, FILTER_TRAINABLENOW, FILTER_HAVEPREREQUISITS, FILTER_INJECTED, FILTER_CERTIFICATES
from skills.certificates.certificateConst import CERTIFICATE_LEVEL_MAX
from skills.client.skillController import SkillController
LEVELS_PER_SKILL = 5

class SkillGroupController(object):

    @telemetry.ZONE_METHOD
    def __init__(self, groupID):
        self.groupID = groupID

    @telemetry.ZONE_METHOD
    def GetAllSkills(self):
        allSkills = sm.GetService('skills').GetSkillControllers()
        return allSkills[self.groupID].values()

    @telemetry.ZONE_METHOD
    def GetNumSkills(self):
        return len(self.GetAllSkills())

    @telemetry.ZONE_METHOD
    def GetSkillsInjected(self):
        return [ skill for skill in self.GetAllSkills() if skill.IsInjected() ]

    @telemetry.ZONE_METHOD
    def GetSkillsTrainableNow(self):
        return [ skill for skill in self.GetAllSkills() if skill.IsTrainableNow() ]

    def GetSkillsDisabled(self):
        return [ skill for skill in self.GetAllSkills() if not skill.IsCloneStateMet() ]

    @telemetry.ZONE_METHOD
    def GetSkillsFiltered(self, skillFilter, txtFilter = None, certificateID = None, certificateLevel = None, certGroupID = None):
        if skillFilter == FILTER_SHOWALL:
            skills = self.GetAllSkills()
        elif skillFilter == FILTER_INJECTED:
            skills = self.GetSkillsInjected()
        elif skillFilter == FILTER_TRAINABLENOW:
            skills = self.GetSkillsTrainableNow()
        elif skillFilter == FILTER_HAVEPREREQUISITS:
            skills = self.GetSkillsHaveSkillPrerequisitsFor()
        elif skillFilter == FILTER_CERTIFICATES:
            if not certificateID:
                return []
            skills = self.GetCertificateSkills(certificateID, certificateLevel, certGroupID)
        if txtFilter:
            skills = filter(lambda x: self.FilterSkillByText(x, txtFilter), skills)
        return sorted(skills, key=self.GetSkillSortKey)

    @telemetry.ZONE_METHOD
    def GetSkillsHaveSkillPrerequisitsFor(self):
        return [ skill for skill in self.GetAllSkills() if self._HavePrerequisitesForFilter(skill) ]

    def _HavePrerequisitesForFilter(self, skill):
        if skill.IsFullyTrained():
            return False
        return skill.IsInjected() or skill.IsPrereqsMetIncludingSkillQueue()

    @telemetry.ZONE_METHOD
    def GetCertificateSkills(self, certificateID, certificateLevel, certGroupID = None):
        certificate = sm.GetService('certificates').GetCertificate(certificateID)
        certSkills = certificate.SkillsByTypeAndLevel(certificateLevel)
        ret = [ SkillController(typeID) for typeID, _ in certSkills ]
        if certGroupID:
            ret = [ skill for skill in ret if evetypes.GetGroupID(skill.typeID) == certGroupID ]
        return ret

    @telemetry.ZONE_METHOD
    def GetAccumulatedCertificateLevelsTrained(self):
        certificates = self.GetAllCertificates()
        return sum((cert.GetLevel() or 0 for cert in certificates))

    @telemetry.ZONE_METHOD
    def GetAllCertificates(self):
        return sm.GetService('certificates').GetCertificatesByGroupID(self.groupID)

    def GetNumCertificates(self):
        return len(self.GetAllCertificates())

    @telemetry.ZONE_METHOD
    def GetAccumulatedCertificateLevelsTotal(self):
        certificates = self.GetAllCertificates()
        return len(certificates) * CERTIFICATE_LEVEL_MAX

    def GetSkillSortKey(self, skill):
        return (skill.GetRank(), len(skill.GetPrereqSkills()), skill.GetName())

    def FilterSkillByText(self, skill, txt):
        return txt.lower() in skill.GetName().lower()

    def GetHint(self):
        return '<b>%s</b><br>%s' % (self.GetName(), self.GetDescription())

    def GetName(self):
        return evetypes.GetGroupNameByGroup(self.groupID)

    def GetDescription(self):
        return DESCRIPTION_BY_GROUPID.get(self.groupID, None)

    @telemetry.ZONE_METHOD
    def GetAccumulatedLevelsTrained(self):
        levels = (skill.GetMyLevel() for skill in self.GetSkillsInjected())
        return sum(levels)

    @telemetry.ZONE_METHOD
    def GetAccumulatedLevelsTrainedAndEnabled(self):
        levels = (skill.GetMyLevel() for skill in self.GetSkillsInjected())
        return sum(levels)

    def GetAccumulatedLevelsTrainedAndDisabled(self):
        levels = (max(skill.GetMyLevel() - skill.GetCurrCloneStateMaxLevel(), 0) for skill in self.GetSkillsInjected())
        return sum(levels)

    @telemetry.ZONE_METHOD
    def GetAccumulatedSkillPointsTrained(self):
        skills = self.GetSkillsInjected()
        levels = (skill.GetSkillpointsTrained() for skill in skills)
        return sum(levels)

    def GetAccumulatedSkillPointsTrainedAndDisabled(self):
        skills = self.GetSkillsInjected()
        levels = (skill.GetSkillPointsTrainedAndDisabled() for skill in skills)
        return sum(levels)

    @telemetry.ZONE_METHOD
    def GetAccumulatedSkillPointsTotal(self):
        skills = self.GetAllSkills()
        levels = (skill.GetSkillPointsTotal() for skill in skills)
        return sum(levels)

    @telemetry.ZONE_METHOD
    def GetAccumulatedLevelsTotal(self):
        return len(self.GetAllSkills()) * LEVELS_PER_SKILL

    @telemetry.ZONE_METHOD
    def GetAccumulatedLevelsTrainedRatio(self):
        if not self.GetAccumulatedLevelsTotal():
            return 0
        return float(self.GetAccumulatedLevelsTrained()) / self.GetAccumulatedLevelsTotal()

    def GetAccumulatedLevelsTrainedAndDisabledRatio(self):
        return float(self.GetAccumulatedLevelsTrainedAndDisabled()) / self.GetAccumulatedLevelsTotal()

    @telemetry.ZONE_METHOD
    def GetMyTotalSkillPoints(self):
        return sm.GetService('skills').GetSkillPoints(self.groupID)

    def GetIcon(self):
        return ICON_BY_GROUPID.get(self.groupID, None)

    @telemetry.ZONE_METHOD
    def GetTotalOmegaLevels(self):
        ret = 0
        for skill in self.GetAllSkills():
            ret += 5.0 - sm.GetService('cloneGradeSvc').GetMaxSkillLevel(skill.typeID, CLONE_STATE_ALPHA)

        return ret

    @telemetry.ZONE_METHOD
    def GetOmegaSkillLevelsRatio(self):
        return float(self.GetTotalOmegaLevels()) / self.GetAccumulatedLevelsTotal()

    def GetSpPerMinute(self, attributeID1, attributeID2):
        skillSvc = sm.GetService('skills')
        playerPrimaryAttribute = skillSvc.GetCharacterAttribute(attributeID1)
        playerSecondaryAttribute = skillSvc.GetCharacterAttribute(attributeID2)
        return GetSkillPointsPerMinute(playerPrimaryAttribute, playerSecondaryAttribute)
