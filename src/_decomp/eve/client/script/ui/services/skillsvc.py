#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\skillsvc.py
import operator
from carbon.common.script.sys.service import Service
from collections import defaultdict, OrderedDict
from copy import deepcopy
import blue
import telemetry
import carbonui.const as uiconst
import characterskills
import clonegrade
import eve.common.script.util.notificationconst as notificationConst
import evetypes
import localization
import uthread
import utillib
from carbon.client.script.environment.AudioUtil import PlaySound
from characterskills.client import skill_signals
from characterskills.client.skill_training import ClientCharacterSkillInterface
from characterskills.common.character_skill_entry import CharacterSkillEntry
from characterskills.skill_accelerators import SkillAcceleratorBoosters
from characterskills.skill_training import SkillTrainingTimeCalculator
from characterskills.util import GetSkillPointsPerMinute, GetSPForLevelRaw, GetSkillLevelRaw, GetAllSkillGroups
from dogma.const import attributePrimaryAttribute, attributeSkillTimeConstant, attributeSecondaryAttribute
from dogma.effects import IsBoosterSkillAccelerator
from eve.common.script.sys import eveCfg
from shipprogression.shipUnlockSvc import GetShipUnlockService
from skills.client.skillController import SkillController
from eve.client.script.ui.skilltrading.skillExtractorWindow import SkillExtractorWindow
from eve.common.lib import appConst as const
from eveexceptions import UserError
from evetypes.skills import get_required_skills_index, get_dogma_required_skills
from inventorycommon import const as invconst
from notifications.common.formatters.skillPoints import UnusedSkillPointsFormatter
from notifications.common.notification import Notification, SimpleNotification
from eve.common.script.util import notificationconst
SKILLREQ_DONTHAVE = 1
SKILLREQ_HAVEBUTNOTTRAINED = 2
SKILLREQ_HAVEANDTRAINED = 3
SKILLREQ_HAVEANDTRAINEDFULLY = 4
SKILLREQ_TRIALRESTRICTED = 5
TEXTURE_PATH_BY_SKILLREQ = {SKILLREQ_DONTHAVE: 'res:/UI/Texture/Classes/Skills/doNotHaveFrame.png',
 SKILLREQ_HAVEBUTNOTTRAINED: 'res:/UI/Texture/Classes/Skills/levelPartiallyTrainedFrame.png',
 SKILLREQ_HAVEANDTRAINED: 'res:/UI/Texture/Classes/Skills/levelTrainedFrame.png',
 SKILLREQ_HAVEANDTRAINEDFULLY: 'res:/UI/Texture/Classes/Skills/fullyTrainedFrame.png',
 SKILLREQ_TRIALRESTRICTED: 'res:/UI/Texture/Classes/Skills/trialRestrictedFrame.png'}
SHIP_SKILLREQ_HINT = {SKILLREQ_DONTHAVE: 'UI/InfoWindow/ShipSkillReqDoNotHave',
 SKILLREQ_HAVEBUTNOTTRAINED: 'UI/InfoWindow/ShipSkillReqPartiallyTrained',
 SKILLREQ_HAVEANDTRAINED: 'UI/InfoWindow/ShipSkillReqTrained',
 SKILLREQ_HAVEANDTRAINEDFULLY: 'UI/InfoWindow/ShipSkillReqFullyTrained',
 SKILLREQ_TRIALRESTRICTED: 'UI/InfoWindow/ShipSkillReqRestrictedForTrial'}
SKILL_SKILLREQ_HINT = {SKILLREQ_DONTHAVE: 'UI/InfoWindow/SkillReqDoNotHave',
 SKILLREQ_HAVEBUTNOTTRAINED: 'UI/InfoWindow/SkillReqPartiallyTrained',
 SKILLREQ_HAVEANDTRAINED: 'UI/InfoWindow/SkillReqTrained',
 SKILLREQ_HAVEANDTRAINEDFULLY: 'UI/InfoWindow/SkillReqFullyTrained',
 SKILLREQ_TRIALRESTRICTED: 'UI/InfoWindow/SkillReqRestrictedForTrial'}
ITEM_SKILLREQ_HINT = {SKILLREQ_DONTHAVE: 'UI/InfoWindow/ItemSkillReqDoNotHave',
 SKILLREQ_HAVEBUTNOTTRAINED: 'UI/InfoWindow/ItemSkillReqPartiallyTrained',
 SKILLREQ_HAVEANDTRAINED: 'UI/InfoWindow/ItemSkillReqTrained',
 SKILLREQ_HAVEANDTRAINEDFULLY: 'UI/InfoWindow/ItemSkillReqFullyTrained',
 SKILLREQ_TRIALRESTRICTED: 'UI/InfoWindow/ItemSkillReqRestrictedForTrial'}
HIGHLIGHT_SKILLS_TRAINED = 2243
HIGHLIGHT_SP_ADDED = 2244
HIGHLIGHT_SKILLS_TRAINED_AND_SP_ADDED = 2259

class SkillsSvc(Service):
    __guid__ = 'svc.skills'
    __notifyevents__ = ['ProcessSessionChange',
     'OnServerSkillsChanged',
     'OnServerSkillsRemoved',
     'OnSkillForcedRefresh',
     'OnRespecInfoChanged',
     'OnFreeSkillPointsChanged',
     'OnServerBoostersChanged',
     'OnServerImplantsChanged',
     'OnCloneDestruction',
     'OnLogonSkillsTrained',
     'OnAlphaInjectionAvailable',
     'OnSkillBundleInjected',
     'OnSessionReset']
    __servicename__ = 'skills'
    __displayname__ = 'Skill Client Service'
    __dependencies__ = ['nonDiminishingInjection', 'settings']
    __startupdependencies__ = ['godma']

    def Run(self, memStream = None):
        self.LogInfo('Starting Skills')
        self.Reset()
        GetShipUnlockService(self)

    def Stop(self, memStream = None):
        self.Reset()

    def ProcessSessionChange(self, isremote, session, change):
        if session.charid is None:
            self.Reset()

    def OnSessionReset(self):
        self.Reset()
        self.ResetSkillHistory()

    def Reset(self):
        self.allskills = None
        self.skillGroups = None
        self.respecInfo = None
        self.depedentSkills = None
        self.myskills = None
        self.mySkillsIncludingLapsed = None
        self.skillHistory = None
        self.freeSkillPoints = None
        self.skillHandler = None
        self.boosters = None
        self.implants = None
        self.characterAttributes = None
        self._skillAcceleratorBoosters = None
        self.skillsByGroupIDTypeID = None
        self._charTotalSkillPoints = None

    def ResetSkillHistory(self):
        self.skillHistory = None

    def GetSkillHandler(self):
        if not self.skillHandler:
            self.skillHandler = session.ConnectToRemoteService('skillMgr2').GetMySkillHandler()
        return self.skillHandler

    def RefreshMySkills(self):
        if self.myskills is not None:
            self.LogError('skillSvc is force refreshing client side skill state!')
        self.myskills = self.GetSkillHandler().GetSkills()

    def RefreshMySkillsIncludingLapsed(self):
        if self.mySkillsIncludingLapsed is not None:
            self.LogError('skillSvc is force refreshing client side skill state!')
        self.mySkillsIncludingLapsed = self.GetSkillHandler().GetAllSkills()

    def OnLogonSkillsTrained(self, skillInfos, canTrain):
        levelsTrained = []
        for skillTypeID, skillInfo in skillInfos.iteritems():
            for x in xrange(skillInfo.currentLevel + 1, skillInfo.skillLevel + 1):
                levelsTrained.append((skillTypeID, x))

        if levelsTrained:
            PlaySound('msg_SkillTrained_play')
            self.TriggerSkillsTrainedNotification(levelsTrained)
        if canTrain:
            self._CheckTriggerNoSkillsInQueueNotification()
        GetShipUnlockService().OnSkillsChanged(skillInfos)

    def OnServerSkillsChanged(self, skillInfos, event, timeStamp):
        levelsTrained = self._UpdateMySkillsAndReturnLevelsTrained(skillInfos, timeStamp)
        self.ResetSkillHistory()
        sm.GetService('skillqueue').OnServerSkillsChanged(skillInfos)
        if levelsTrained:
            PlaySound('msg_SkillTrained_play')
            self.TriggerSkillsTrainedNotification(levelsTrained)
            sm.ScatterEvent('OnSkillLevelsTrained', levelsTrained)
            skill_signals.on_skill_levels_trained(levelsTrained)
        if event:
            sm.ScatterEvent(event, skillInfos)
        sm.ScatterEvent('OnSkillsChanged', skillInfos)

    def OnServerSkillsRemoved(self, skillInfos, timeStamp):
        self._UpdateMySkillsAndReturnLevelsTrained(skillInfos, timeStamp)
        self.ResetSkillHistory()
        sm.GetService('skillqueue').OnServerSkillsChanged(skillInfos)
        sm.ScatterEvent('OnSkillsChanged', skillInfos)

    def _UpdateMySkillsAndReturnLevelsTrained(self, skillInfos, timeStamp):
        levelsTrained = []
        self.GetSkills()
        skills = self.GetSkillsIncludingLapsed()
        for skillTypeID, skillInfo in skillInfos.iteritems():
            if skillInfo.trainedSkillPoints >= 0:
                currentSkill = skills.get(skillTypeID, None)
                if currentSkill and getattr(currentSkill, 'timeStamp', 0) > timeStamp:
                    continue
                if not currentSkill or currentSkill.trainedSkillLevel != skillInfo.trainedSkillLevel:
                    if currentSkill and currentSkill.trainedSkillLevel:
                        startLevel = currentSkill.trainedSkillLevel + 1
                    else:
                        startLevel = 1
                    endLevel = skillInfo.trainedSkillLevel + 1
                    for x in xrange(startLevel, endLevel):
                        levelsTrained.append((skillTypeID, x))

                skillInfo.timeStamp = timeStamp
                self.myskills[skillTypeID] = skillInfo
                self.mySkillsIncludingLapsed[skillTypeID] = skillInfo
            elif skillInfo.virtualSkillLevel is not None:
                currentSkill = skills.get(skillTypeID, None)
                if currentSkill and getattr(currentSkill, 'timeStamp', 0) > timeStamp:
                    continue
                skillInfo = skillInfo.GetCopyWithNewSkillPoints(None)
                skillInfo.timeStamp = timeStamp
                self.myskills[skillTypeID] = skillInfo
                self.mySkillsIncludingLapsed[skillTypeID] = skillInfo
            else:
                del self.myskills[skillTypeID]
                del self.mySkillsIncludingLapsed[skillTypeID]

        return levelsTrained

    def GetSkills(self, renew = 0):
        if self.myskills is None or renew:
            self.RefreshMySkills()
        return self.myskills

    def GetCharacterAttributes(self, renew = False):
        if self.characterAttributes is None or renew:
            self.GetBoosters(True)
            self.GetImplants(True)
            self.characterAttributes = self.GetSkillHandler().GetAttributes()
            for attributeID, attributeValue in self.characterAttributes.iteritems():
                self.godma.GetStateManager().ApplyAttributeChange(session.charid, session.charid, attributeID, blue.os.GetWallclockTime(), attributeValue, None, False)

        return deepcopy(self.characterAttributes)

    def GetCharacterAttribute(self, attributeID, includeBoosters = True):
        if sm.GetService('cloneGradeSvc').IsOmega():
            attrValue = self.GetCharacterAttributes()[attributeID]
        else:
            attrValue = self.GetCharacterAttributes()[attributeID] * clonegrade.ALPHA_TRAINING_MULTIPLIER
        if not includeBoosters:
            boosters = self.GetSkillAcceleratorBoosters()
            bonus = boosters.get_attribute_bonus(attributeID)
            if not sm.GetService('cloneGradeSvc').IsOmega():
                bonus = bonus * clonegrade.ALPHA_TRAINING_MULTIPLIER
            attrValue -= bonus
        return attrValue

    def GetSkill(self, skillTypeID, renew = 0):
        if self.myskills is None or renew:
            self.RefreshMySkills()
        return self.myskills.get(skillTypeID, None)

    def GetSkillIncludingLapsed(self, skillTypeID, renew = 0):
        if self.mySkillsIncludingLapsed is None or renew:
            self.RefreshMySkillsIncludingLapsed()
        return self.mySkillsIncludingLapsed.get(skillTypeID, None)

    def GetSkillsIncludingLapsed(self, renew = 0):
        if self.mySkillsIncludingLapsed is None or renew:
            self.RefreshMySkillsIncludingLapsed()
        return self.mySkillsIncludingLapsed

    @telemetry.ZONE_METHOD
    def MySkillLevel(self, skillTypeID):
        skill = self.GetSkill(skillTypeID)
        if skill is not None:
            return skill.trainedSkillLevel
        return 0

    def MySkillLevelIncludingQueued(self, skillID):
        inQueue = self.GetMaxSkillLevelsInQueue()
        skill = self.GetSkillIncludingLapsed(skillID)
        if skill is None:
            return 0
        return max(skill.trainedSkillLevel, inQueue.get(skillID, 0))

    def MySkillPoints(self, skillTypeID):
        skill = self.GetSkill(skillTypeID)
        if skill is not None:
            return skill.trainedSkillPoints

    def MyEffectiveSkillLevelsByID(self, renew = 0):
        skills = {}
        for skillTypeID, skill in self.GetSkills(renew).iteritems():
            skills[skillTypeID] = skill.effectiveSkillLevel

        return skills

    def SkillPointsCurrentLevel(self, skillTypeID):
        skill = self.GetSkillIncludingLapsed(skillTypeID)
        return GetSPForLevelRaw(skill.skillRank, skill.trainedSkillLevel)

    def SkillpointsNextLevel(self, skillTypeID):
        skill = self.GetSkillIncludingLapsed(skillTypeID)
        if not skill or skill.trainedSkillLevel >= characterskills.MAX_SKILL_LEVEL:
            return None
        return GetSPForLevelRaw(skill.skillRank, skill.trainedSkillLevel + 1)

    def HasSkill(self, skillTypeID):
        return skillTypeID in self.GetSkillsIncludingLapsed()

    def IsSkillInjected(self, skillTypeID):
        skill = self.GetSkillIncludingLapsed(skillTypeID)
        return skill and skill.trainedSkillLevel is not None

    @telemetry.ZONE_METHOD
    def GetAllSkills(self):
        if not self.allskills:
            self.allskills = {}
            for typeID in evetypes.GetTypeIDsByCategory(const.categorySkill):
                if evetypes.IsPublished(typeID):
                    self.allskills[typeID] = CharacterSkillEntry(typeID, 0, 0, self.GetSkillRank(typeID), None)

        return self.allskills

    def GetEffectiveLevel(self, typeID):
        skills = self.GetSkills()
        if typeID in skills:
            return skills[typeID].effectiveSkillLevel

    def GetMyLevel(self, typeID):
        skills = self.GetSkills()
        if typeID in skills:
            return skills[typeID].trainedSkillLevel

    def GetMyLevelIncludingLapsed(self, typeID):
        skills = self.GetSkillsIncludingLapsed()
        if typeID in skills:
            return skills[typeID].trainedSkillLevel

    def GetMySkillPoints(self, typeID):
        skills = self.GetSkills()
        if typeID in skills:
            return skills[typeID].trainedSkillPoints
        else:
            return 0

    def GetMySkillPointsIncludingLapsed(self, typeID):
        skills = self.GetSkillsIncludingLapsed()
        if typeID in skills:
            return skills[typeID].trainedSkillPoints
        else:
            return 0

    @telemetry.ZONE_METHOD
    def GetAllSkillGroups(self):
        if not self.skillGroups:
            skillGroupIDs = GetAllSkillGroups()
            skillgroups = [ utillib.KeyVal(groupID=groupID, groupName=evetypes.GetGroupNameByGroup(groupID)) for groupID in skillGroupIDs ]
            skillgroups = localization.util.Sort(skillgroups, key=operator.attrgetter('groupName'))
            self.skillGroups = skillgroups
        return self.skillGroups

    @telemetry.ZONE_METHOD
    def GetSkillHistory(self, maxresults = 50):
        if self.skillHistory is None:
            self.skillHistory = self.GetSkillHandler().GetSkillHistory(maxresults)
        return self.skillHistory

    def GetDependentSkills(self, typeID):
        if self.depedentSkills is None:
            self.depedentSkills = defaultdict(dict)
            for skillTypeID in self.GetAllSkills():
                requirements = self.GetRequiredSkills(skillTypeID)
                for dependentTypeID, level in requirements.iteritems():
                    self.depedentSkills[dependentTypeID][skillTypeID] = level

        return self.depedentSkills[typeID]

    @telemetry.ZONE_METHOD
    def GetRecentlyTrainedSkills(self):
        skillChanges = {}
        skillData = self.GetSkillHandler().GetSkillChangesForISIS()
        for typeID, pointChange in skillData:
            currentSkillPoints = self.MySkillPoints(typeID) or 0
            timeConstant = self.godma.GetTypeAttribute2(typeID, const.attributeSkillTimeConstant)
            pointsBefore = currentSkillPoints - pointChange
            oldLevel = GetSkillLevelRaw(pointsBefore, timeConstant)
            if self.MySkillLevel(typeID) > oldLevel:
                skillChanges[typeID] = oldLevel

        return skillChanges

    @telemetry.ZONE_METHOD
    def GetSkillGroups(self, advanced = False):
        if session.charid:
            ownSkills = self.GetSkills()
            skillQueue = sm.GetService('skillqueue').GetServerQueue()
            skillsInQueue = [ skill.trainingTypeID for skill in skillQueue ]
        else:
            ownSkills = []
            skillsInQueue = []
        ownSkillTypeIDs = []
        ownSkillsByGroupID = defaultdict(list)
        ownSkillsInTrainingByGroupID = defaultdict(list)
        ownSkillsInQueueByGroupID = defaultdict(list)
        ownSkillPointsByGroupID = defaultdict(int)
        for skillTypeID, skill in ownSkills.iteritems():
            groupID = evetypes.GetGroupID(skillTypeID)
            ownSkillsByGroupID[groupID].append(skill)
            if sm.GetService('skillqueue').SkillInTraining(skillTypeID):
                ownSkillsInTrainingByGroupID[groupID].append(skill)
            if skillTypeID in skillsInQueue:
                ownSkillsInQueueByGroupID[groupID].append(skillTypeID)
            ownSkillPointsByGroupID[groupID] += skill.skillPoints
            ownSkillTypeIDs.append(skillTypeID)

        missingSkillsByGroupID = defaultdict(list)
        if advanced:
            allSkills = self.GetAllSkills()
            for skillTypeID, skill in allSkills.iteritems():
                if skillTypeID not in ownSkillTypeIDs:
                    groupID = evetypes.GetGroupID(skillTypeID)
                    missingSkillsByGroupID[groupID].append(skill)

        skillsByGroup = []
        skillgroups = self.GetAllSkillGroups()
        for invGroup in skillgroups:
            mySkillsInGroup = ownSkillsByGroupID[invGroup.groupID]
            skillsIDontHave = missingSkillsByGroupID[invGroup.groupID]
            mySkillsInTraining = ownSkillsInTrainingByGroupID[invGroup.groupID]
            mySkillsInQueue = ownSkillsInQueueByGroupID[invGroup.groupID]
            skillPointsInGroup = ownSkillPointsByGroupID[invGroup.groupID]
            skillsByGroup.append([invGroup,
             mySkillsInGroup,
             skillsIDontHave,
             mySkillsInTraining,
             mySkillsInQueue,
             skillPointsInGroup])

        return skillsByGroup

    def IsSkillRequirementMet(self, typeID):
        required = self.GetRequiredSkills(typeID)
        for skillTypeID, lvl in required.iteritems():
            if self.MySkillLevel(skillTypeID) < lvl:
                return False

        return True

    def IsSkillRequirementMetIncludingSkillQueue(self, typeID):
        required = self.GetRequiredSkills(typeID)
        inQueue = self.GetMaxSkillLevelsInQueue()
        for skillTypeID, lvl in required.iteritems():
            if self.MySkillLevel(skillTypeID) < lvl:
                if skillTypeID not in inQueue or inQueue[skillTypeID] < lvl:
                    return False

        return True

    @telemetry.ZONE_METHOD
    def GetMaxSkillLevelsInQueue(self, maxQueueIdx = None):
        skillQueue = sm.GetService('skillqueue').GetQueue()
        if maxQueueIdx is not None:
            skillQueue = skillQueue[:maxQueueIdx + 1]
        inQueue = {}
        for skill in skillQueue:
            inQueue[skill.trainingTypeID] = skill.trainingToLevel

        return inQueue

    def GetSkillInQueueIndex(self, skillID, level):
        for i, skill in enumerate(sm.GetService('skillqueue').GetQueue()):
            if skill.trainingTypeID == skillID and skill.trainingToLevel == level:
                return i

    @telemetry.ZONE_METHOD
    def GetRequiredSkills(self, typeID):
        return get_dogma_required_skills(typeID)

    def GetRequiredSkillsLevel(self, skills):
        if not skills:
            return SKILLREQ_HAVEANDTRAINED
        allLevel5 = True
        haveAll = True
        missingSkill = False
        for skillTypeID, level in skills:
            mySkill = self.GetSkill(skillTypeID)
            if mySkill is None:
                missingSkill = True
                continue
            if mySkill.trainedSkillLevel < level:
                haveAll = False
            if mySkill.trainedSkillLevel != 5:
                allLevel5 = False

        if missingSkill:
            return SKILLREQ_DONTHAVE
        elif not haveAll:
            return SKILLREQ_HAVEBUTNOTTRAINED
        elif allLevel5:
            return SKILLREQ_HAVEANDTRAINEDFULLY
        else:
            return SKILLREQ_HAVEANDTRAINED

    def IsUnlockedWithExpertSystem(self, typeID):
        skills = self.GetRequiredSkills(typeID)
        isUnlockedWithExpertSystem = False
        for skillTypeID, requiredLevel in skills.iteritems():
            mySkill = self.GetSkill(skillTypeID)
            if mySkill:
                trainedSkillLevel = mySkill.trainedSkillLevel or 0
            else:
                return False
            if trainedSkillLevel < requiredLevel and mySkill.effectiveSkillLevel >= requiredLevel:
                isUnlockedWithExpertSystem = True
            elif trainedSkillLevel < requiredLevel:
                return False

        return isUnlockedWithExpertSystem

    def GetRequiredSkillsLevelTexturePathAndHint(self, skills, typeID = None):
        skillLevel = self.GetRequiredSkillsLevel(skills)
        texturePath = TEXTURE_PATH_BY_SKILLREQ[skillLevel]
        if typeID is None:
            hint = ITEM_SKILLREQ_HINT[skillLevel]
        else:
            categoryID = evetypes.GetCategoryID(typeID)
            if categoryID == invconst.categoryShip:
                hint = SHIP_SKILLREQ_HINT[skillLevel]
            elif categoryID == invconst.categorySkill:
                hint = SKILL_SKILLREQ_HINT[skillLevel]
            else:
                hint = ITEM_SKILLREQ_HINT[skillLevel]
        return (texturePath, localization.GetByLabel(hint))

    def GetRequiredSkillsRecursive(self, typeID):
        ret = {}
        self._GetAllSkillsRequiredToUseTypeRecursive(typeID, ret)
        return ret

    def _GetAllSkillsRequiredToUseTypeRecursive(self, typeID, ret):
        for skillTypeID, lvl in self.GetRequiredSkills(typeID).iteritems():
            ret[skillTypeID] = max(ret.get(skillTypeID, 0), lvl)
            if skillTypeID != typeID:
                self._GetAllSkillsRequiredToUseTypeRecursive(skillTypeID, ret)

    def GetTopLevelSkillsMissingToUseItem(self, typeID):
        requiredSkills = self.GetRequiredSkills(typeID)
        ret = []
        for typeID, level in requiredSkills.iteritems():
            if self.GetMyLevel(typeID) < level:
                ret.append((typeID, level))

        return ret

    def GetTotalMissingSkillLevelsToUseItem(self, typeID):
        requiredSkills = self.GetRequiredSkillsRecursive(typeID)
        missingLevels = 0
        for typeID, level in requiredSkills.iteritems():
            myLevel = self.GetMyLevel(typeID)
            if myLevel is None:
                myLevel = 0
            if myLevel < level:
                missingLevels += level - myLevel

        return missingLevels

    def GetMissingSkillBooksFromList(self, skills):
        missingSkills = []
        for skillID, level in skills:
            skill = self.GetSkill(skillID)
            if not skill or skill.trainedSkillPoints is None:
                missingSkills.append(skillID)

        return missingSkills

    def GetSkillsMissingToUseItemRecursiveList(self, typeID):
        missingDict = self.GetSkillsMissingToUseItemRecursive(typeID)
        return [ (typeID, level) for typeID, level in missingDict.iteritems() ]

    def GetSkillsMissingToUseItemRecursive(self, typeID):
        ret = OrderedDict()
        self._GetMissingSkillsRequiredToUseTypeRecursive(typeID, ret)
        return ret

    def _GetMissingSkillsRequiredToUseTypeRecursive(self, typeID, ret):
        for skillTypeID, lvl in self.GetRequiredSkills(typeID).iteritems():
            if self.GetMyLevel(skillTypeID) < lvl:
                if skillTypeID != typeID:
                    mySkill = self.GetSkillIncludingLapsed(skillTypeID)
                    if not mySkill or mySkill.trainedSkillPoints <= 0:
                        self._GetMissingSkillsRequiredToUseTypeRecursive(skillTypeID, ret)
                ret[skillTypeID] = max(ret.get(skillTypeID, 0), lvl)

    def GetSkillBooksMissingFromList(self, skills):
        return [ typeID for typeID in skills.iterkeys() if self.GetSkillIncludingLapsed(typeID) is None ]

    def GetSkillsMissingToUseAllSkillsFromListRecursiveAsList(self, skills):
        missingDict = self.GetSkillsMissingToUseAllSkillsFromListRecursive(skills)
        return [ (typeID, level) for typeID, level in missingDict.iteritems() ]

    def GetSkillsMissingToUseAllSkillsFromListRecursive(self, skills):
        ret = OrderedDict()
        self._GetSkillsMissingToUseAllSkillsFromListRecursive(skills, ret)
        return ret

    def _GetSkillsMissingToUseAllSkillsFromListRecursive(self, skills, ret):
        for skillTypeID, lvl in skills:
            if self.GetMyLevel(skillTypeID) < lvl:
                if skillTypeID not in skills:
                    mySkill = self.GetSkillIncludingLapsed(skillTypeID)
                    if not mySkill or mySkill.trainedSkillPoints <= 0:
                        self._GetMissingSkillsRequiredToUseTypeRecursive(skillTypeID, ret)
                ret[skillTypeID] = max(ret.get(skillTypeID, 0), lvl)

    def GetSkillTrainingTimeLeftToUseType(self, skillTypeID, includeBoosters = True):
        if self.IsSkillRequirementMet(skillTypeID):
            return 0L
        required = self.GetRequiredSkillsRecursive(skillTypeID)
        totalTime = self.GetSkillTrainingTimeLeftForTypesAndLevels(required, includeBoosters)
        return long(totalTime)

    def GetSkillTrainingTimeLeftForTypesAndLevels(self, required, includeBoosters):
        totalTime = 0
        skillsIncludingLapsed = self.GetSkillsIncludingLapsed()
        requiredMax = {}
        for typeID, lvl in required.iteritems():
            haveSkill = skillsIncludingLapsed.get(typeID, None)
            if haveSkill and haveSkill.trainedSkillLevel >= lvl:
                continue
            elif typeID not in requiredMax:
                requiredMax[typeID] = int(lvl)

        for typeID, trainToLevel in requiredMax.iteritems():
            trainedSkillLevel = 0
            skillEntry = skillsIncludingLapsed.get(typeID, None)
            if skillEntry and skillEntry.trainedSkillLevel is not None:
                trainedSkillLevel = skillEntry.trainedSkillLevel
            for trainingLevel in xrange(trainedSkillLevel + 1, trainToLevel + 1):
                totalTime += self.GetRawTrainingTimeForSkillLevel(typeID, trainingLevel, includeBoosters=includeBoosters)

        return totalTime

    def GetSkillPointsRequiredForSkills(self, skillTypeIDsAndLevels):

        def _get_skillpoint_cost_for_level(skill_rank, skill_level):
            if skill_level <= 0:
                return 0
            return GetSPForLevelRaw(skill_rank, skill_level) - GetSPForLevelRaw(skill_rank, skill_level - 1)

        pointsBySkillTypeID = OrderedDict()
        for skillTypeID, level in skillTypeIDsAndLevels:
            if self.GetMyLevel(skillTypeID) >= level:
                continue
            rank = self.GetSkillRank(skillTypeID)
            pointsPresent = 0
            existingSkill = self.GetSkill(skillTypeID)
            if existingSkill is not None and existingSkill.trainedSkillLevel == level - 1:
                pointsPresent = existingSkill.trainedSkillPoints - GetSPForLevelRaw(rank, existingSkill.trainedSkillLevel)
            remainingPointsToLevel = _get_skillpoint_cost_for_level(rank, level) - pointsPresent
            pointsBySkillTypeID[skillTypeID] = remainingPointsToLevel + pointsBySkillTypeID.get(skillTypeID, 0)

        return pointsBySkillTypeID

    def GetTrainingTimeLeftForSkillLevels(self, skillsLevels, includeBoosters = True):
        requiredSkills = {}
        for skillTypeID, level in skillsLevels.iteritems():
            if requiredSkills.get(skillTypeID, 0) < level:
                requiredSkills[skillTypeID] = level
            newRequirements = self.GetRequiredSkillsRecursive(skillTypeID)
            for newSkillID, newLevel in newRequirements.iteritems():
                if requiredSkills.get(newSkillID, 0) < newLevel:
                    requiredSkills[newSkillID] = newLevel

        totalTime = self.GetSkillTrainingTimeLeftForTypesAndLevels(requiredSkills, includeBoosters)
        return totalTime

    def GetSkillToolTip(self, skillTypeID, level):
        if session.charid is None:
            return
        mySkill = self.GetSkill(skillTypeID)
        mySkillLevel = 0
        if mySkill is not None:
            mySkillLevel = mySkill.trainedSkillLevel or 0
        tooltipText = evetypes.GetDescription(skillTypeID)
        tooltipTextList = []
        for i in xrange(int(mySkillLevel) + 1, int(level) + 1):
            timeLeft = self.GetRawTrainingTimeForSkillLevel(skillTypeID, i)
            tooltipTextList.append(localization.GetByLabel('UI/SkillQueue/Skills/SkillLevelAndTrainingTime', skillLevel=i, timeLeft=long(timeLeft)))

        levelsText = '<br>'.join(tooltipTextList)
        if levelsText:
            tooltipText += '<br><br>' + levelsText
        return tooltipText

    def GetSkillpointsPerMinute(self, skillTypeID, includeBoosters = True):
        primaryAttributeID = self.GetPrimarySkillAttribute(skillTypeID)
        secondaryAttributeID = self.GetSecondarySkillAttribute(skillTypeID)
        playerPrimaryAttribute = self.GetCharacterAttribute(primaryAttributeID, includeBoosters=includeBoosters)
        playerSecondaryAttribute = self.GetCharacterAttribute(secondaryAttributeID, includeBoosters=includeBoosters)
        return GetSkillPointsPerMinute(playerPrimaryAttribute, playerSecondaryAttribute)

    def GetRawTrainingTimeForSkillLevel(self, skillTypeID, skillLevel, includeBoosters = True):
        skillTimeConstant = self.GetSkillRank(skillTypeID)
        rawSkillPointsToTrain = GetSPForLevelRaw(skillTimeConstant, skillLevel)
        trainingRate = self.GetSkillpointsPerMinute(skillTypeID, includeBoosters=includeBoosters)
        existingSP = 0
        priorLevel = skillLevel - 1
        skillInfo = self.GetSkills().get(skillTypeID, None)
        if skillInfo:
            existingSP = GetSPForLevelRaw(skillTimeConstant, priorLevel)
            if priorLevel >= 0 and priorLevel == skillInfo.trainedSkillLevel:
                existingSP = sm.GetService('skillqueue').GetSkillPointsFromSkillObject(skillTypeID, skillInfo)
        if existingSP > rawSkillPointsToTrain:
            return 0
        skillPointsToTrain = rawSkillPointsToTrain - existingSP
        trainingTimeInMinutes = float(skillPointsToTrain) / float(trainingRate)
        return trainingTimeInMinutes * const.MIN

    @telemetry.ZONE_METHOD
    def GetSkillCount(self):
        return len(self.GetSkills())

    @telemetry.ZONE_METHOD
    def GetSkillPoints(self, groupID = None):
        return sum([ skillInfo.trainedSkillPoints or 0 for skillTypeID, skillInfo in self.GetSkills().iteritems() if groupID is None or evetypes.GetGroupID(skillTypeID) == groupID ])

    def GetTotalSkillPointsForCharacter(self):
        trainedSkillPoints = sum([ skillInfo.trainedSkillPoints or 0 for skillTypeID, skillInfo in self.GetSkillsIncludingLapsed().iteritems() ])
        unallocatedSkillPoints = self.GetFreeSkillPoints()
        return trainedSkillPoints + unallocatedSkillPoints

    def GetTotalSkillPointsForCharacterCached(self):
        if not self._charTotalSkillPoints:
            self._charTotalSkillPoints = self.GetTotalSkillPointsForCharacter()
        return self._charTotalSkillPoints

    def GetSkillRank(self, skillTypeID):
        return self.godma.GetTypeAttribute(skillTypeID, attributeSkillTimeConstant)

    def GetPrimarySkillAttribute(self, skillTypeID):
        return self.godma.GetTypeAttribute(skillTypeID, attributePrimaryAttribute)

    def GetSecondarySkillAttribute(self, skillTypeID):
        return self.godma.GetTypeAttribute(skillTypeID, attributeSecondaryAttribute)

    def GetSkillAcceleratorBoosters(self):
        if self._skillAcceleratorBoosters is None:
            self._skillAcceleratorBoosters = self._GetSkillAcceleratorBoosters()
        return self._skillAcceleratorBoosters

    def _GetSkillAcceleratorBoosters(self):
        myGodmaItem = self.godma.GetItem(session.charid)
        skillBoosters = SkillAcceleratorBoosters(self.godma.GetTypeAttribute2)
        dogmaStaticMgr = sm.GetService('clientDogmaStaticSvc')
        for booster in myGodmaItem.boosters:
            if IsBoosterSkillAccelerator(dogmaStaticMgr, booster):
                skillBoosters.add_booster(booster.expiryTime, booster.boosterTypeID)

        return skillBoosters

    def Train(self, skillX):
        skill = sm.GetService('skillqueue').SkillInTraining()
        if skill and eve.Message('ConfirmResetSkillTraining', {'name': evetypes.GetName(skill.typeID),
         'lvl': skill.skillLevel + 1}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return
        self.GetSkillHandler().CharStartTrainingSkill(skillX.itemID, skillX.locationID)

    def InjectSkillIntoBrain(self, skillX):
        skillIDList = [ skill.itemID for skill in skillX ]
        if not skillIDList:
            return
        for skill in skillX:
            if not evetypes.IsPublished(skill.typeID):
                raise UserError('ItemNotASkill', {'skillName': skill.typeID})

        try:
            self.godma.GetDogmaLM().InjectSkillIntoBrain(skillIDList)
        except UserError as e:
            raise
        else:
            for skill in skillX:
                sm.GetService('notificationSvc').MakeAndScatterNotification(notificationConst.notificationTypeSkillInjected, data={'typeID': skill.typeID})

            PlaySound(uiconst.SOUND_ADD_OR_USE)

    def AbortTrain(self):
        self.GetSkillHandler().AbortTraining()

    @telemetry.ZONE_METHOD
    def GetRespecInfo(self):
        if self.respecInfo is None:
            self.respecInfo = self.GetSkillHandler().GetRespecInfo()
        return self.respecInfo

    def OnRespecInfoChanged(self, *args):
        self.respecInfo = None
        self.GetCharacterAttributes(True)
        sm.ScatterEvent('OnRespecInfoUpdated')

    def OnOpenCharacterSheet(self, skillIDs, *args):
        sm.GetService('charactersheet').ForceShowSkillHistoryHighlighting(skillIDs)

    def MakeSkillQueueEmptyNotification(self, skillQueueNotification):
        queueText = localization.GetByLabel('UI/SkillQueue/NoSkillsInQueue')
        skillQueueNotification = Notification.MakeSkillNotification(header=queueText, text='', created=blue.os.GetWallclockTime(), callBack=sm.StartService('skills').OnOpenCharacterSheet, callbackargs=None, notificationType=Notification.SKILL_NOTIFICATION_EMPTYQUEUE)
        return skillQueueNotification

    def TriggerSkillsTrainedNotification(self, levelsTrained):
        if len(levelsTrained) > 1:
            text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingComplete')
            subtext = localization.GetByLabel('UI/SkillQueue/Skills/NumberOfSkills', amount=len(levelsTrained))
            self._TriggerSkillNotification(levelsTrained, text, subtext)
        else:
            skillTypeID, level = levelsTrained[0]
            text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingComplete')
            subtext = localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndLevel', skill=skillTypeID, amount=level)
            self._TriggerSkillNotification(levelsTrained, text, subtext)

    def _CheckTriggerNoSkillsInQueueNotification(self):
        queue = sm.GetService('skillqueue').GetServerQueue()
        if not len(queue):
            emptyQueueNotification = self.MakeSkillQueueEmptyNotification(None)
            sm.ScatterEvent('OnNewNotificationReceived', emptyQueueNotification)

    def _TriggerSkillNotification(self, skillChanges, text, subtext):
        header = '%s - %s' % (text, subtext)
        skillNotification = Notification.MakeSkillNotification(header=header, text='', created=blue.os.GetWallclockTime(), callBack=sm.StartService('skills').OnOpenCharacterSheet, callbackargs=skillChanges)
        sm.ScatterEvent('OnNewNotificationReceived', skillNotification)

    def OnFreeSkillPointsChanged(self, newFreeSkillPoints):
        self.SetFreeSkillPoints(newFreeSkillPoints)

    @telemetry.ZONE_METHOD
    def GetFreeSkillPoints(self):
        if self.freeSkillPoints is None:
            self.freeSkillPoints = self.GetSkillHandler().GetFreeSkillPoints()
        return self.freeSkillPoints

    def ApplyFreeSkillPointsToSkills(self, skillTypeIDsAndLevels):
        if self.freeSkillPoints is None:
            self.GetFreeSkillPoints()
        for skillTypeID, level in skillTypeIDsAndLevels:
            if self.IsSkillInjected(skillTypeID) == False:
                raise UserError('CannotApplyFreePointsDoNotHaveSkill', {'skillName': evetypes.GetName(skillTypeID)})
            skill = self.GetSkill(skillTypeID)
            if skill is None:
                raise UserError('CannotApplyFreePointsDoNotHaveSkill', {'skillName': evetypes.GetName(skillTypeID)})

    def ApplyFreeSkillPoints(self, skillTypeID, pointsToApply):
        if self.freeSkillPoints is None:
            self.GetFreeSkillPoints()
        inTraining = sm.GetService('skillqueue').SkillInTraining()
        if inTraining is not None and inTraining.typeID == skillTypeID:
            raise UserError('CannotApplyFreePointsWhileTrainingSkill')
        if self.IsSkillInjected(skillTypeID) == False:
            raise UserError('CannotApplyFreePointsDoNotHaveSkill', {'skillName': evetypes.GetName(skillTypeID)})
        skill = self.GetSkill(skillTypeID)
        if skill is None:
            raise UserError('CannotApplyFreePointsDoNotHaveSkill', {'skillName': evetypes.GetName(skillTypeID)})
        spAtMaxLevel = GetSPForLevelRaw(skill.skillRank, 5)
        if skill.trainedSkillPoints + pointsToApply > spAtMaxLevel:
            pointsToApply = spAtMaxLevel - skill.trainedSkillPoints
        if pointsToApply > self.freeSkillPoints:
            raise UserError('CannotApplyFreePointsNotEnoughRemaining', {'pointsRequested': pointsToApply,
             'pointsRemaining': self.freeSkillPoints})
        if pointsToApply <= 0:
            return
        newFreePoints = self.GetSkillHandler().ApplyFreeSkillPoints(skill.typeID, pointsToApply)
        self.SetFreeSkillPoints(newFreePoints)

    def SetFreeSkillPoints(self, newFreePoints):
        isFreeSkillPointsChange = self.freeSkillPoints is None or newFreePoints != self.freeSkillPoints
        if not isFreeSkillPointsChange:
            return
        isFreeSkillPointsIncrease = self.freeSkillPoints is None or newFreePoints > self.freeSkillPoints
        if isFreeSkillPointsIncrease:
            uthread.new(self.ShowSkillPointsNotification_thread)
        self.freeSkillPoints = newFreePoints
        sm.ScatterEvent('OnFreeSkillPointsChanged_Local')
        if isFreeSkillPointsIncrease:
            sm.GetService('uiHighlightingService').highlight_ui_element(HIGHLIGHT_SP_ADDED)

    def MakeAndScatterSkillPointNotification(self):
        notificationData = UnusedSkillPointsFormatter.MakeData()
        sm.GetService('notificationSvc').MakeAndScatterNotification(type=notificationConst.notificationTypeUnusedSkillPoints, data=notificationData)

    def ShowSkillPointsNotification(self, number = (0, 0), time = 5000, *args):
        skillPointsNow = self.GetFreeSkillPoints()
        skillPointsLast = settings.user.ui.Get('freeSkillPoints', -1)
        if skillPointsLast == skillPointsNow:
            return
        if skillPointsNow <= 0:
            return
        self.MakeAndScatterSkillPointNotification()
        settings.user.ui.Set('freeSkillPoints', skillPointsNow)

    def ShowSkillPointsNotification_thread(self):
        blue.pyos.synchro.SleepWallclock(5000)
        if session.charid:
            self.ShowSkillPointsNotification()

    def OnSkillForcedRefresh(self):
        uthread.Pool('skillSvc::OnSkillForcedRefresh', self.ForceRefresh)

    def ForceRefresh(self):
        self.Reset()
        sm.ScatterEvent('OnSkillQueueRefreshed')

    def OnServerBoostersChanged(self, *args):
        self.GetCharacterAttributes(True)
        self._skillAcceleratorBoosters = None
        sm.ScatterEvent('OnBoosterUpdated')
        sm.ScatterEvent('OnSkillQueueRefreshed')

    def OnServerImplantsChanged(self, *args):
        skillQueueSvc = sm.GetService('skillqueue')
        self.GetCharacterAttributes(True)
        if skillQueueSvc.GetQueue():
            sm.ScatterEvent('OnSkillQueueRefreshed')
        sm.ScatterEvent('OnImplantsChanged')

    def OnCloneDestruction(self, *args):
        self.GetCharacterAttributes(True)
        sm.ScatterEvent('OnBoosterUpdated')

    def OnJumpCloneTransitionCompleted(self):
        self.GetCharacterAttributes(True)
        sm.ScatterEvent('OnBoosterUpdated')

    def GetBoosters(self, forced = 0):
        if self.boosters is None or forced:
            self.boosters = self.GetSkillHandler().GetBoosters()
        return self.boosters

    def GetImplants(self, forced = 0):
        if self.implants is None or forced:
            self.implants = self.GetSkillHandler().GetImplants()
        return self.implants

    def ExtractSkills(self, skills, itemID):
        skills = {s:p for s, p in skills.iteritems()}
        token = sm.GetService('connection').GetAccessToken()
        self.GetSkillHandler().ExtractSkills(skills, itemID, token)

    def ActivateSkillInjector(self, itemID, quantity):
        self.GetSkillHandler().InjectSkillpoints(itemID, quantity)
        sm.GetService('audio').SendUIEvent('st_activate_skill_injector_play')
        sm.ScatterEvent('OnSkillPointsInjected_Local', quantity)

    def CheckInjectionConstraints(self, itemID, quantity):
        self.GetSkillHandler().CheckInjectionConstraints(itemID, quantity)

    def ActivateSkillExtractor(self, item):
        if eveCfg.InSpace():
            raise UserError('SkillExtractorNotDockedInStation', {'extractor': const.typeSkillExtractor})
        skillPoints = self.GetSkillHandler().GetSkillPoints()
        freeSkillPoints = self.GetSkillHandler().GetFreeSkillPoints()
        if skillPoints + freeSkillPoints < const.SKILL_TRADING_MINIMUM_SP_TO_EXTRACT:
            raise UserError('SkillExtractionNotEnoughSP', {'limit': const.SKILL_TRADING_MINIMUM_SP_TO_EXTRACT,
             'extractor': const.typeSkillExtractor})
        if blue.pyos.packaged:
            token = sm.GetService('connection').GetAccessToken()
            if token is None:
                raise UserError('TokenRequiredForSkillExtraction')
        SkillExtractorWindow.OpenOrReload(itemID=item.itemID)

    def GetSkillPointAmountFromInjectors(self, typeID, quantity):
        nonDiminishingInjectionsRemaining = self.nonDiminishingInjection.GetRemaining()
        return self.GetSkillHandler().GetDiminishedSpFromInjectors(typeID, quantity, nonDiminishingInjectionsRemaining)

    def GetNextAlphaInjectionDateTime(self):
        return sm.RemoteSvc('alphaInjectorMgr').GetNextAvailableInjection()

    def GetDurationUntilNextAlphaInjection(self):
        return max(0, self.GetNextAlphaInjectionDateTime() - blue.os.GetWallclockTime())

    def SplitSkillInjector(self, itemID, quantity):
        self.GetSkillHandler().SplitSkillInjector(itemID, quantity)

    def CombineSkillInjector(self, itemID, quantity):
        if quantity < const.SKILL_TRADING_SMALL_INJECTOR_DIVISOR:
            raise UserError('CombineSkillInjectorTooFewInjectors', {'minQuantity': const.SKILL_TRADING_SMALL_INJECTOR_DIVISOR,
             'injectorType': const.typeSmallSkillInjector})
        self.GetSkillHandler().CombineSkillInjector(itemID, quantity)

    def GetSkillTrainingTimeCalculator(self):
        return SkillTrainingTimeCalculator(ClientCharacterSkillInterface(self))

    def GetTypesUnlockedByTrainingToLevel(self, skillTypeID, level, includeQueue = True):
        typeIndex = get_required_skills_index().get(skillTypeID, {})
        typeIndex = typeIndex.get(level, {})
        if includeQueue:
            maxQueueIdx = self.GetSkillInQueueIndex(skillTypeID, level)
            skillsInQueue = self.GetMaxSkillLevelsInQueue(maxQueueIdx)
        else:
            skillsInQueue = {}
        ret = defaultdict(dict)
        for marketGroupID, typesByMetaGroupID in typeIndex.iteritems():
            for metaGroupID, typeIDs in typesByMetaGroupID.iteritems():
                publishedTypeIDs = [ typeID for typeID in typeIDs if self._IsUnlockedType(skillTypeID, typeID, skillsInQueue) ]
                if publishedTypeIDs:
                    ret[marketGroupID][metaGroupID] = publishedTypeIDs

        return dict(ret)

    def _IsUnlockedType(self, skillID, typeID, skillsInQueue):
        required = self.GetRequiredSkills(typeID)
        for requiredSkillID, requiredLevel in required.iteritems():
            if requiredSkillID == skillID:
                continue
            elif self.MySkillLevel(requiredSkillID) < requiredLevel:
                if skillsInQueue.get(requiredSkillID, 0) < requiredLevel:
                    return False

        return True

    def _ConstructSkillControllers(self):
        self.skillsByGroupIDTypeID = defaultdict(dict)
        typeIDs = evetypes.GetTypeIDsByCategory(invconst.categorySkill)
        for typeID in typeIDs:
            if not evetypes.IsPublished(typeID) and not self.GetSkill(typeID):
                continue
            groupID = evetypes.GetGroupID(typeID)
            self.skillsByGroupIDTypeID[groupID][typeID] = SkillController(typeID)

    def GetSkillControllers(self):
        if self.skillsByGroupIDTypeID is None:
            self._ConstructSkillControllers()
        return self.skillsByGroupIDTypeID

    def OnAlphaInjectionAvailable(self):
        uthread.new(self._NotifyAlphaInjectionAvailable)

    def _NotifyAlphaInjectionAvailable(self):
        notification = SimpleNotification(subject=localization.GetByLabel('UI/SkillTrading/AlphaInjectionAvailable'), created=blue.os.GetWallclockTime(), notificationID=None, notificationTypeID=notificationconst.notificationTypeAlphaInjectorAvailable)
        sm.ScatterEvent('OnNewNotificationReceived', notification)

    def PurchaseSkills(self, skillTypeIDs, confirm = True, skillPlanTemplate = None):
        context = characterskills.client.SkillPurchaseContext(skill_service=self, skill_plan_template=skillPlanTemplate)
        return characterskills.client.purchase_skills(context, skillTypeIDs, confirm=confirm)

    def WaitUntilSkillsAreAvailable(self, skillTypeIDs):
        skill_type_ids = set(skillTypeIDs)
        seen = set()
        while skill_type_ids != seen:
            blue.pyos.BeNice()
            for skill_type_id in skill_type_ids:
                if self.GetSkillIncludingLapsed(skill_type_id) is None:
                    break
                seen.add(skill_type_id)

        sm.ScatterEvent('OnSkillsAvailable', skillTypeIDs)

    def GetSkillBundleInfo(self, skillBundleID):
        return self.GetSkillHandler().GetSkillBundleInfo(skillBundleID)

    def GetSkillBundleHighlight(self, numberOfSkills, sp):
        if numberOfSkills > 0 and sp > 0:
            return HIGHLIGHT_SKILLS_TRAINED_AND_SP_ADDED
        if numberOfSkills > 0:
            return HIGHLIGHT_SKILLS_TRAINED
        if sp > 0:
            return HIGHLIGHT_SP_ADDED

    def OnSkillBundleInjected(self, numberOfSkills, sp):
        highlight_id = self.GetSkillBundleHighlight(numberOfSkills, sp)
        if highlight_id:
            sm.GetService('uiHighlightingService').highlight_ui_element(highlight_id)

    def GetTrainingTimeForSkills(self, skills):
        trainingTime = 0
        for skillID, level in skills.iteritems():
            try:
                myLevel = self.GetSkillIncludingLapsed(skillID).trainedSkillLevel or 0
            except AttributeError:
                myLevel = 0

            for i in xrange(int(myLevel) + 1, int(level) + 1):
                trainingTime += self.GetRawTrainingTimeForSkillLevel(skillID, i)

        return trainingTime

    def GetTrainingTimeForSkillsExcludeTrained(self, skills):
        trainingTime = 0
        for skillID, level in skills.iteritems():
            for i in xrange(1, int(level) + 1):
                trainingTime += self.GetRawTrainingTimeForSkillLevel(skillID, i)

        return trainingTime
