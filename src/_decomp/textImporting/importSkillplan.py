#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\textImporting\importSkillplan.py
import evetypes
import inventorycommon.const as invconst
from eve.client.script.ui.shared.fittingScreen.skillRequirementsUtil import GetAllSkillsAndLevels
from textImporting import GetLines, SplitAndStrip, CleanText
from textImporting.importSkillplanConst import REQ_ADD, MANUAL_ADD, FAILED_PREVIOUSLY_TRAINED, FAILED_TOO_MANY_SKILLS, FAILED_SKILL_IN_QUEUE
from textImporting.textToTypeIDFinder import TextToTypeIDFinder

class ImportSkillPlan(object):

    def __init__(self, usingDefaultLanguage = True):
        skillTypeIDs = evetypes.GetTypeIDsByCategory(invconst.categorySkill)
        self.typeIDFinder = TextToTypeIDFinder(skillTypeIDs, usingDefaultLanguage)
        self.levelDict = {'i': 1,
         'ii': 2,
         'iii': 3,
         'iv': 4,
         'v': 5}
        self.validLevelStrings = ('1', '2', '3', '4', '5')

    def GetSkillsToAdd(self, text, clearQueue = True):
        if not text:
            return ([], [''])
        skillsAndLevels, failed = self.GetSkillsAndLevelsFromText(text)
        skillListWithPrereqs = self.GetSkillsWithPreReqs(skillsAndLevels, clearQueue)
        return (skillListWithPrereqs, failed)

    def GetSkillsAndLevelsFromText(self, text):
        lines = GetLines(text)
        skillsAndLevels = []
        failed = []
        for eachLine in lines:
            parts = SplitAndStrip(eachLine, ' ')
            if not parts:
                continue
            levelString = parts[-1]
            if levelString in self.validLevelStrings:
                level = int(levelString)
            else:
                level = self.levelDict.get(levelString.lower(), None)
            if not level:
                failed.append(eachLine)
                continue
            skillName = ' '.join(parts[:-1]).strip()
            typeID = self._GetSkillTypeID(skillName)
            if typeID:
                skillsAndLevels.append((typeID, level))
            else:
                failed.append(eachLine)

        return (skillsAndLevels, failed)

    def _GetSkillTypeID(self, skillName):
        try:
            typeID = int(skillName)
            if evetypes.IsSkill(typeID):
                return typeID
            return None
        except ValueError:
            pass

        skillName = CleanText(skillName)
        skillNameLower = skillName.lower()
        typeID = self.GetTypeIDFromName(skillNameLower)
        return typeID

    def GetTypeIDFromName(self, skillNameLower):
        return self.typeIDFinder.GetTypeIDFromEitherLangage(skillNameLower)

    def GetSkillsWithPreReqs(self, wantedSkillAndLevels, clearQueue):
        from collections import OrderedDict
        allSkillsLevelsAndWhy = OrderedDict()
        skillSvc = sm.GetService('skills')
        for eachSkillTypeID, eachLevel in wantedSkillAndLevels:
            if skillSvc.GetSkill(eachSkillTypeID) is not None:
                reqSkillsAndLevels = GetAllSkillsAndLevels([eachSkillTypeID])
                for typeID, lvl in reqSkillsAndLevels:
                    key = (typeID, lvl)
                    if key in allSkillsLevelsAndWhy:
                        continue
                    allSkillsLevelsAndWhy[key] = REQ_ADD

            for newLvl in xrange(1, eachLevel):
                key = (eachSkillTypeID, newLvl)
                if key in allSkillsLevelsAndWhy:
                    continue
                allSkillsLevelsAndWhy[key] = REQ_ADD

            allSkillsLevelsAndWhy[eachSkillTypeID, eachLevel] = MANUAL_ADD

        skillQueueSvc = sm.GetService('skillqueue')
        for skillInfo, why in allSkillsLevelsAndWhy.items():
            skillTypeID, skillLvl = skillInfo
            skill = skillSvc.GetSkillIncludingLapsed(skillTypeID)
            if skill is not None and skill.trainedSkillLevel >= skillLvl and why == REQ_ADD:
                allSkillsLevelsAndWhy.pop(skillInfo)
            elif not clearQueue and why == REQ_ADD:
                posInQueue = skillQueueSvc.FindInQueue(skillTypeID, skillLvl)
                if posInQueue is not None:
                    allSkillsLevelsAndWhy.pop(skillInfo)

        return [ (x[0], x[1], y) for x, y in allSkillsLevelsAndWhy.iteritems() ]


class SkillPlanImportingStatus(object):

    def __init__(self):
        self.failedLevels = []
        self.failedSkillTypeIDs = {}
        self.alreadyTrainedLevels = []
        self.alreadyInQueueLevels = []
        self.skillLevelsAdded = 0
        self.tooManySkills = False

    def AddToFailed(self, typeID, skillLevel, reason = None):
        infoTuple = (typeID, skillLevel, reason)
        if reason == FAILED_PREVIOUSLY_TRAINED:
            self.alreadyTrainedLevels.append(infoTuple)
        elif reason == FAILED_SKILL_IN_QUEUE:
            self.alreadyInQueueLevels.append(infoTuple)
        else:
            self.failedLevels.append(infoTuple)
            if reason == FAILED_TOO_MANY_SKILLS:
                self.tooManySkills = True
            if typeID in self.failedSkillTypeIDs:
                lowestLevelWithError = self.failedSkillTypeIDs[typeID][0]
            else:
                lowestLevelWithError = 6
            if skillLevel < lowestLevelWithError:
                self.failedSkillTypeIDs[typeID] = (skillLevel, reason)

    def TooManySkillsAdded(self):
        return self.tooManySkills

    def ReasonForFailingForLowerLevel(self, typeID, skillLevel):
        if typeID not in self.failedSkillTypeIDs:
            return None
        failureInfo = self.failedSkillTypeIDs[typeID]
        if skillLevel > failureInfo[0]:
            return failureInfo[1]

    def IncreaseAddedCount(self):
        self.skillLevelsAdded += 1
