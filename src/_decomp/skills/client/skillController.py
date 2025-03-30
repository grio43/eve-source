#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\client\skillController.py
import telemetry
import characterskills
import evetypes
import localization
from carbon.common.script.util.format import IntToRoman
from carbonui import TextColor
from carbonui.util.color import Color
from dogma.const import attributeSkillTimeConstant
from eve.common.lib import appConst
from eveservices.menu import GetMenuService
from localization import GetByLabel
from localization.formatters.timeIntervalFormatters import FormatTimeIntervalShortWritten, TIME_CATEGORY_DAY, TIME_CATEGORY_MINUTE
from logmodule import LogException
from skills.client.util import buy_missing_skills
from utillib import KeyVal

class SkillController(object):

    def __init__(self, typeID):
        self.typeID = typeID
        self.skill_service = sm.GetService('skills')
        self.skill_queue_service = sm.GetService('skillqueue')
        self.menu_service = GetMenuService()
        self.godma = sm.GetService('godma')
        self.expert_system_service = sm.GetService('expertSystemSvc')

    def GetName(self):
        return evetypes.GetName(self.typeID)

    def GetTypeID(self):
        return self.typeID

    def GetGroupID(self):
        return evetypes.GetGroupID(self.typeID)

    def GetNameWithRank(self):
        return GetByLabel('UI/SkillQueue/Skills/SkillNameAndRankValue', skill=self.typeID, rank=int(self.GetRank()))

    def GetMenu(self):
        return self.menu_service.GetMenuForSkill(self.typeID)

    def GetDragData(self):
        skill = self.skill_service.GetSkillIncludingLapsed(self.typeID)
        ret = KeyVal(__guid__='listentry.SkillEntry', typeID=self.typeID, invtype=self.typeID, skillID=self.typeID, label=evetypes.GetName(self.typeID), skill=skill, inQueue=False, trained=skill is not None)
        return (ret,)

    def GetHint(self):
        return self.GetDescription()

    def GetDescription(self):
        return evetypes.GetDescription(self.typeID)

    def GetMyExpertSystems(self):
        return self.expert_system_service.GetMyExpertSystems()

    def IsInTraining(self):
        return self.skill_queue_service.SkillInTraining(self.typeID)

    @telemetry.ZONE_METHOD
    def IsInQueue(self, level = None):
        skillQueue = self.skill_queue_service.GetQueue()
        for skill in skillQueue:
            if self.typeID == skill.trainingTypeID:
                if level:
                    if level == skill.trainingToLevel:
                        return True
                else:
                    return True

        return False

    @telemetry.ZONE_METHOD
    def IsInjected(self):
        return self.skill_service.IsSkillInjected(self.typeID)

    def IsAllPrereqsInjected(self):
        typeIDs = self.GetPrereqSkillsRecursive().keys()
        return all([ self.skill_service.IsSkillInjected(typeID) for typeID in typeIDs ])

    def BuyAllRequiredSkillbooks(self):
        skills = self.GetPrereqSkillsRecursive()
        typeIDs = skills.keys() + [self.typeID]
        buy_missing_skills(typeIDs)

    @telemetry.ZONE_METHOD
    def IsPrereqsMet(self):
        return self.skill_service.IsSkillRequirementMet(self.typeID)

    @telemetry.ZONE_METHOD
    def IsSkillAvailableForPurchase(self):
        return evetypes.IsSkillAvailableForPurchase(self.typeID)

    @telemetry.ZONE_METHOD
    def IsPrereqsMetIncludingSkillQueue(self):
        return self.skill_service.IsSkillRequirementMetIncludingSkillQueue(self.typeID)

    @telemetry.ZONE_METHOD
    def IsTrainableNow(self):
        prereqsOrSkillpoints = self.IsPrereqsMetIncludingSkillQueue() or self.GetSkillpointsTrained() > 0
        return self.IsInjected() and prereqsOrSkillpoints and self.IsCloneStateMet() and not self.IsFullyTrained()

    @telemetry.ZONE_METHOD
    def IsFullyTrained(self):
        return self.GetMyLevel() == characterskills.MAX_SKILL_LEVEL

    @telemetry.ZONE_METHOD
    def IsCloneStateMet(self):
        myLevel = self.GetMyLevel()
        restrictLevel = self.GetCurrCloneStateMaxLevel()
        return myLevel < restrictLevel

    @telemetry.ZONE_METHOD
    def GetCurrCloneStateMaxLevel(self):
        return sm.GetService('cloneGradeSvc').GetMaxSkillLevel(self.typeID)

    def GetDescriptionAndLevelInRoman(self, level):
        romanNumber = IntToRoman(min(characterskills.MAX_SKILL_LEVEL, level)) if level > 0 else '-'
        return '%s %s' % (self.GetName(), romanNumber)

    @telemetry.ZONE_METHOD
    def GetRequiredSkillNameAndLevelComparedToTrainedLevel(self, requiredLevel):
        color = Color.RGBtoHex(*TextColor.NORMAL)
        return localization.GetByLabel('UI/InfoWindow/RequiredSkillNameAndLevel', skill=self.typeID, level=IntToRoman(requiredLevel), levelColor=color)

    @telemetry.ZONE_METHOD
    def GetTimeToTrainToLevel(self, level):
        total_time = 0
        skill = self.skill_service.GetSkillIncludingLapsed(self.typeID)
        if skill and skill.trainedSkillLevel is not None:
            trainedLevel = skill.trainedSkillLevel or 0
            levels_left = level - trainedLevel
            if levels_left > 0:
                for level in range(int(trainedLevel + 1), int(level + 1)):
                    total_time += self.GetTimeLeftToTrain(level)

        else:
            for level in range(int(level + 1)):
                total_time += self.GetTimeLeftToTrain(level)

        return total_time

    def GetTimeLeftToTrain(self, level = None, includeBoosters = False):
        if level is None:
            level = self.GetNextLevel()
        if level is not None:
            return long(self.skill_service.GetRawTrainingTimeForSkillLevel(self.typeID, level, includeBoosters=includeBoosters))

    def GetTimeLeftToTrainText(self, level = None, includeBoosters = False):
        duration = self.GetTimeLeftToTrain(level, includeBoosters=includeBoosters)
        if duration is None:
            return
        if duration > appConst.DAY:
            showTo = 'hour'
        elif duration > appConst.HOUR:
            showTo = 'minute'
        else:
            showTo = 'second'
        return FormatTimeIntervalShortWritten(duration, showFrom='day', showTo=showTo)

    def GetTrainingTimeForLevelText(self, level, includeBoosters = False):
        time = self.GetTimeLeftToTrain(level, includeBoosters)
        return FormatTimeIntervalShortWritten(long(time), showFrom=TIME_CATEGORY_DAY, showTo=TIME_CATEGORY_MINUTE)

    @telemetry.ZONE_METHOD
    def GetTimeToTrainToLevelText(self, level):
        if level is None:
            return
        time = self.GetTimeToTrainToLevel(level)
        if time:
            return FormatTimeIntervalShortWritten(long(time), showFrom=TIME_CATEGORY_DAY, showTo=TIME_CATEGORY_MINUTE)
        return ''

    @telemetry.ZONE_METHOD
    def GetTimeToTrainToNextLevelText(self):
        level = self.GetNextLevelToAddToQueue()
        if level is None:
            return
        time = self.GetTimeLeftToTrain(level)
        return FormatTimeIntervalShortWritten(long(time), showFrom=TIME_CATEGORY_DAY, showTo=TIME_CATEGORY_MINUTE)

    @telemetry.ZONE_METHOD
    def GetTrainingProgressForCurrLevel(self):
        skillPointsTrained = self.skill_queue_service.GetEstimatedSkillPointsTrained(self.typeID)
        nextLevel = self.GetNextLevel()
        if nextLevel is None:
            return 1.0
        skillPointsNextLevel = self.GetSkillPointsRequiredForLevel(nextLevel)
        skillPointsCurrLevel = self.GetSkillPointsRequiredForLevel(self.GetMyLevel())
        return (skillPointsTrained - skillPointsCurrLevel) / float(skillPointsNextLevel - skillPointsCurrLevel)

    @telemetry.ZONE_METHOD
    def GetSkillpointsTrained(self):
        return self.skill_service.GetMySkillPointsIncludingLapsed(self.typeID)

    @telemetry.ZONE_METHOD
    def GetSkillpointsTrainedAndEnabled(self):
        return self.skill_service.GetMySkillPoints(self.typeID)

    def GetSkillPointsTrainedAndDisabled(self):
        skillPoints = self.GetSkillpointsTrainedAndEnabled()
        return self.skill_service.GetMySkillPointsIncludingLapsed(self.typeID) - skillPoints

    @telemetry.ZONE_METHOD
    def GetSkillPointsTotal(self):
        level = characterskills.MAX_SKILL_LEVEL
        return self.GetSkillPointsRequiredForLevel(level)

    def GetSkillPointsMissingForLevel(self, level):
        return self.GetSkillPointsRequiredForLevel(level) - self.GetSkillpointsTrainedAndEnabled()

    def GetSkillPointsRequiredForLevel(self, level):
        return characterskills.GetSPForLevelRaw(self.GetRank(), level)

    @telemetry.ZONE_METHOD
    def GetMyLevel(self):
        return self.skill_service.GetMyLevelIncludingLapsed(self.typeID) or 0

    @telemetry.ZONE_METHOD
    def GetMyActiveLevel(self):
        return self.skill_service.GetMyLevel(self.typeID) or 0

    def GetNextLevelToAddToQueue(self):
        nextLevel = self.skill_queue_service.FindNextLevel(self.typeID, skillQueue=self.skill_queue_service.GetQueue())
        if nextLevel is None:
            nextLevel = self.GetMyLevel() + 1
        if nextLevel > characterskills.MAX_SKILL_LEVEL:
            nextLevel = None
        return nextLevel

    def GetNextLevel(self):
        currLevel = self.GetMyLevel()
        if currLevel == characterskills.MAX_SKILL_LEVEL:
            return None
        else:
            return currLevel + 1

    def AddToTrainingQueue(self):
        self.skill_queue_service.AddSkillToQueue(self.GetTypeID())

    @telemetry.ZONE_METHOD
    def GetRank(self):
        rank = self.godma.GetTypeAttribute(self.typeID, attributeSkillTimeConstant)
        if rank is None:
            LogException('No rank found for skill, typeID=%s' % self.typeID)
            rank = 1
        return rank

    @telemetry.ZONE_METHOD
    def GetCertificateRequiredSkillLevel(self, certificateID, certificateLevel):
        if not certificateID:
            return None
        certificate = sm.GetService('certificates').GetCertificate(certificateID)
        return certificate.skills[self.typeID][certificateLevel]

    def GetPrereqSkills(self):
        return self.skill_service.GetRequiredSkills(self.GetTypeID())

    def GetPrereqSkillsRecursive(self):
        return self.skill_service.GetRequiredSkillsRecursive(self.GetTypeID())
