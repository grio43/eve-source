#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\skillQueueSvc.py
import sys
from contextlib import contextmanager
import blue
import carbonui.const as uiconst
import evetypes
import gametime
import localization
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.service import Service
from carbonui.util.various_unsorted import GetAttrs
from characterskills.queue import SKILLQUEUE_MAX_NUM_SKILLS, GetQueueEntry, GetSkillQueueTimeLength
from characterskills.skill_training import SkillLevelAlreadyTrainedError
from characterskills.util import GetSkillLevelRaw, GetLevelProgress
from eve.client.script.ui.util import uix
from eveexceptions import UserError
from menu import MenuLabel
from skills import skillConst
from skills.client.errors import SkillQueueOverwritten
from textImporting import IsUsingDefaultLanguage
from textImporting.importSkillplan import ImportSkillPlan
from uthread import UnLock, ReentrantLock
from utillib import KeyVal

class SkillQueueService(Service):
    __exportedcalls__ = {'SkillInTraining': []}
    __guid__ = 'svc.skillqueue'
    __servicename__ = 'skillqueue'
    __displayname__ = 'Skill Queue Client Service'
    __dependencies__ = ['godma', 'skills', 'machoNet']
    __notifyevents__ = ['OnSkillQueuePausedServer',
     'OnMultipleCharactersTrainingUpdated',
     'OnNewSkillQueueSaved',
     'OnSubscriptionChanged',
     'OnCharacterSessionChanged',
     'OnSessionReset']

    def __init__(self):
        super(SkillQueueService, self).__init__()
        self.skillQueue = []
        self.cachedSkillQueue = None
        self.skillQueueCache = None
        self.skillplanImporter = None
        self.maxSkillqueueTimeLength = None
        self._isAllCharacterTrainingSlotsUsed = None

    def Run(self, memStream = None):
        self.PrimeSkillQueue()

    def ReInitialize(self):
        self.skillQueue = []
        self.cachedSkillQueue = None
        self.skillQueueCache = None
        self.skillplanImporter = None
        self.maxSkillqueueTimeLength = None
        self._isAllCharacterTrainingSlotsUsed = None

    def OnCharacterSessionChanged(self, _oldCharacterID, newCharacterID):
        self.ReInitialize()
        self.PrimeCache()
        if newCharacterID is not None:
            self.PrimeSkillQueue()

    def OnSessionReset(self):
        self.ReInitialize()

    def PrimeSkillQueue(self):
        self.skillQueue, freeSkillPoints = self.GetSkillQueueAndFreeSPsFromServer()
        if freeSkillPoints is not None and freeSkillPoints > 0:
            self.skills.SetFreeSkillPoints(freeSkillPoints)

    def GetMaxSkillQueueLimitLength(self):
        if not self.maxSkillqueueTimeLength:
            self.maxSkillqueueTimeLength = GetSkillQueueTimeLength(sm.GetService('cloneGradeSvc').GetCloneGrade())
        return self.maxSkillqueueTimeLength

    def OnSubscriptionChanged(self):
        self.maxSkillqueueTimeLength = None

    def _ValidateCache(self):
        if self.IsTransactionOpen():
            raise SkillQueueOverwritten(session.charid, self.cachedSkillQueue)

    def BeginTransaction(self):
        with self.ChangeQueueLock():
            sendEvent = False
            skillInTraining = self.SkillInTraining()
            try:
                self._ValidateCache()
            except SkillQueueOverwritten as exc:
                sendEvent = True
                self.LogException(exc)

            self.skillQueueCache = None
            self.skillQueue, freeSkillPoints = self.GetSkillQueueAndFreeSPsFromServer()
            if freeSkillPoints > 0:
                self.skills.SetFreeSkillPoints(freeSkillPoints)
            self.cachedSkillQueue = self.GetQueue()
            if not skillInTraining:
                self.UpdateQueueTimestamps()
            if sendEvent:
                sm.ScatterEvent('OnSkillQueueRefreshed')

    def GetSkillQueueAndFreeSPsFromServer(self):
        return self.skills.GetSkillHandler().GetSkillQueueAndFreePoints()

    def UpdateQueueTimestamps(self):
        queueWithTimestamps = []
        for idx, trainingSkill in enumerate(self.skillQueue):
            startTime = None
            if idx > 0:
                startTime = self.skillQueue[idx - 1].trainingEndTime
            currentSkill = self.skills.GetSkillIncludingLapsed(trainingSkill.trainingTypeID)
            queueEntry = GetQueueEntry(trainingSkill.trainingTypeID, trainingSkill.trainingToLevel, idx, currentSkill, queueWithTimestamps, lambda x, y: self.GetTimeForTraining(x, y, startTime), KeyVal, True)
            queueWithTimestamps.append(queueEntry)

        self.skillQueue = queueWithTimestamps

    def RollbackTransaction(self):
        with self.ChangeQueueLock():
            if self.cachedSkillQueue is None:
                self.LogError('%s: Cannot rollback a skill queue transaction - no transaction was opened!' % session.charid)
                return
            self.skillQueue = self.cachedSkillQueue
            self.skillQueueCache = None
            self.cachedSkillQueue = None

    def CommitTransaction(self, activate = True):
        with self.ChangeQueueLock():
            if activate:
                self._CheckCloneGradeRestrictions()
            self.PrimeCache(force=True)
            if self.IsQueueChanged() or activate:
                try:
                    if activate:
                        self.TrimQueue()
                    queueInfo = {idx:(x.trainingTypeID, x.trainingToLevel) for idx, x in enumerate(self.skillQueue)}
                    skillHandler = self.skills.GetSkillHandler()
                    skillHandler.SaveNewQueue(queueInfo, activate=activate)
                    self.cachedSkillQueue = None
                    sm.ScatterEvent('OnSkillQueueRefreshed')
                except Exception as e:
                    msg = getattr(e, 'msg', None)
                    if msg not in ('UserAlreadyHasSkillInTraining', 'SkillInQueueRequiresOmegaCloneState', 'SkillInQueueOverAlphaSpTrainingSize'):
                        self.RollbackTransaction()
                        sm.ScatterEvent('OnSkillQueueRefreshed')
                    raise

    def _CheckCloneGradeRestrictions(self):
        cloneGradeSvc = sm.GetService('cloneGradeSvc')
        if cloneGradeSvc.IsOmega():
            return
        for skill in self.skillQueue:
            levelLimit = cloneGradeSvc.GetMaxSkillLevel(skill.trainingTypeID)
            if levelLimit < skill.trainingToLevel:
                raise UserError('SkillInQueueRequiresOmegaCloneState')

    def CheckCanAppendSkill(self, skillTypeID, skillLevel = None, check = False, performLengthTest = True):
        if skillLevel is None:
            skillLevel = self.FindNextLevel(skillTypeID, skillQueue=self.GetQueue())
        position = len(self.skillQueue)
        return self.CheckCanInsertSkillAtPosition(skillTypeID, skillLevel, position, check, performLengthTest)

    def CheckCanInsertSkillAtPosition(self, skillTypeID, skillLevel, position = None, check = 0, performLengthTest = True):
        if position is None or position < 0 or position > len(self.skillQueue):
            raise UserError('QueueInvalidPosition')
        self.PrimeCache()
        mySkill = self.skills.GetSkillIncludingLapsed(skillTypeID)
        ret = True
        try:
            if mySkill is None:
                raise UserError('QueueSkillNotUploaded')
            if mySkill.trainedSkillLevel >= skillLevel:
                raise UserError('QueueCannotTrainPreviouslyTrainedSkills')
            if mySkill.trainedSkillLevel >= skillConst.skill_max_level:
                raise UserError('QueueCannotTrainPastMaximumLevel', {'typeName': (const.UE_TYPEID, skillTypeID)})
            if skillTypeID in self.skillQueueCache:
                for lvl, lvlPosition in self.skillQueueCache[skillTypeID].iteritems():
                    if lvl < skillLevel and lvlPosition >= position:
                        raise UserError('QueueCannotPlaceSkillLevelsOutOfOrder')
                    elif lvl > skillLevel and lvlPosition < position:
                        raise UserError('QueueCannotPlaceSkillLevelsOutOfOrder')

            if position >= 0 and performLengthTest:
                timeLeft, _ = self.GetTrainingLengthOfQueue(position)
                if timeLeft > self.GetMaxSkillQueueLimitLength():
                    raise UserError('QueueTooLong')
            if mySkill.trainedSkillPoints == 0:
                requirements = sm.GetService('skills').GetRequiredSkills(skillTypeID)
                for requiredTypeID, requiredLevel in requirements.iteritems():
                    isRequirementsQueued = False
                    if requiredTypeID in self.skillQueueCache:
                        for level, queuedPosition in self.skillQueueCache[requiredTypeID].iteritems():
                            if level <= requiredLevel and queuedPosition > position:
                                raise UserError('QueueCannotPlaceSkillBeforeRequirements')
                            if level >= requiredLevel and queuedPosition < position:
                                isRequirementsQueued = True

                    skill = self.skills.GetSkill(requiredTypeID)
                    if skill is None:
                        raise UserError('QueueCannotPlaceSkillBeforeRequirements')
                    isRequirementsTrained = skill.trainedSkillLevel >= requiredLevel
                    if not isRequirementsTrained and not isRequirementsQueued:
                        raise UserError('QueueCannotPlaceSkillBeforeRequirements')

            dependencies = sm.GetService('skills').GetDependentSkills(skillTypeID)
            for dependentTypeID, requiredLevel in dependencies.iteritems():
                if dependentTypeID not in self.skillQueueCache:
                    continue
                for level, queuedPosition in self.skillQueueCache[dependentTypeID].iteritems():
                    if requiredLevel == skillLevel and queuedPosition < position:
                        raise UserError('QueueCannotPlaceSkillAfterDependentSkills')

            if sm.GetService('cloneGradeSvc').IsSkillLevelRestricted(skillTypeID, skillLevel):
                raise UserError('QueueCannotTrainOmegaRestrictedSkill', {'skillID': skillTypeID})
        except UserError as ue:
            checkedErrors = ('QueueCannotPlaceSkillAfterDependentSkills', 'QueueCannotPlaceSkillBeforeRequirements', 'QueueCannotPlaceSkillLevelsOutOfOrder', 'QueueCannotTrainPreviouslyTrainedSkills', 'QueueSkillNotUploaded', 'QueueTooLong', 'QueueCannotTrainOmegaRestrictedSkill', 'QueueCannotTrainPastMaximumLevel')
            if check and ue.msg in checkedErrors:
                sys.exc_clear()
                ret = False
            else:
                raise

        return ret

    def AddSkillToQueue(self, skillTypeID, skillLevel = None, position = None):
        if not evetypes.IsPublished(skillTypeID):
            raise UserError('ItemNotASkill', {'skillName': skillTypeID})
        if skillLevel is None:
            skillLevel = self.FindNextLevel(skillTypeID, skillQueue=self.GetQueue())
        if skillLevel > skillConst.skill_max_level:
            return
        if self.FindInQueue(skillTypeID, skillLevel) is not None:
            raise UserError('QueueSkillAlreadyPresent')
        skillQueueLength = len(self.skillQueue)
        if skillQueueLength >= SKILLQUEUE_MAX_NUM_SKILLS:
            raise UserError('QueueTooManySkills', {'num': SKILLQUEUE_MAX_NUM_SKILLS})
        newPos = position if position is not None and position >= 0 else skillQueueLength
        currentSkill = self.skills.GetSkill(skillTypeID)
        self.CheckCanInsertSkillAtPosition(skillTypeID, skillLevel, newPos)
        startTime = None
        if newPos != 0:
            startTime = self.skillQueue[newPos - 1].trainingEndTime
        queueEntry = GetQueueEntry(skillTypeID, skillLevel, newPos, currentSkill, self.skillQueue, lambda x, y: self.GetTimeForTraining(x, y, startTime), KeyVal, self.SkillInTraining() is not None)
        if newPos == skillQueueLength:
            self.skillQueue.append(queueEntry)
        else:
            if newPos > skillQueueLength:
                raise UserError('QueueInvalidPosition')
            self.skillQueue.insert(newPos, queueEntry)
            for entry in self.skillQueue[newPos + 1:]:
                entry.queuePosition += 1

            self.skillQueueCache = None
        self.AddToCache(skillTypeID, skillLevel, newPos)
        self.TrimQueue()
        self.OnClientQueueModified()
        PlaySound(uiconst.SOUND_ADD_OR_USE)
        if newPos == 0:
            sm.ScatterEvent('OnClientEvent_SkillPrioritized', skillTypeID)
        sm.ScatterEvent('OnClientEvent_SkillAddedToQueue', skillTypeID, skillLevel)
        return newPos

    def AddSkillsToQueue(self, skills, ignoreAlreadyPresent = False):
        numSkillsAdded = 0
        try:
            while skills:
                skillID, level = skills.pop(0)
                if level is None:
                    level = self.FindNextLevel(skillID, skillQueue=self.GetQueue())
                if self.FindInQueue(skillID, level) is not None:
                    if ignoreAlreadyPresent:
                        continue
                    raise UserError('QueueSkillAlreadyPresent')
                skillQueueLength = len(self.skillQueue)
                if skillQueueLength >= SKILLQUEUE_MAX_NUM_SKILLS:
                    if numSkillsAdded < 1:
                        raise UserError('QueueTooManySkills', {'num': SKILLQUEUE_MAX_NUM_SKILLS})
                    self.TrimQueue()
                    self.OnClientQueueModified()
                    skillList = '<br>'.join([ '- %s' % localization.GetByLabel('UI/InfoWindow/SkillAndLevel', skill=typeID, skillLevel=lvl) for typeID, lvl in [(skillID, level)] + skills ])
                    raise UserError('QueueTooManySkillNotAllAdded', {'maxNumSkills': SKILLQUEUE_MAX_NUM_SKILLS,
                     'skillList': skillList})
                position = len(self.skillQueue)
                self.CheckCanInsertSkillAtPosition(skillID, level, position)
                startTime = None
                if position > 0:
                    startTime = self.skillQueue[position - 1].trainingEndTime
                entry = GetQueueEntry(skillID, level, position, self.skills.GetSkillIncludingLapsed(skillID), self.skillQueue, lambda x, y: self.GetTimeForTraining(x, y, startTime), KeyVal, self.SkillInTraining() is not None)
                self.skillQueue.append(entry)
                numSkillsAdded += 1
                self.AddToCache(skillID, level, position)

            PlaySound(uiconst.SOUND_ADD_OR_USE)
        except Exception:
            self.LogException()
            return numSkillsAdded

        self.TrimQueue()
        self.OnClientQueueModified()
        return numSkillsAdded

    def AddSkillAndRequirementsToQueue(self, skillTypeID, skillLevel = None):
        if not self.IsTransactionOpen():
            self.BeginTransaction()
        if skillLevel is None:
            skillLevel = self.FindNextLevel(skillTypeID, skillQueue=self.GetQueue())
        if skillLevel > skillConst.skill_max_level:
            return
        required = self.skills.GetSkillsMissingToUseItemRecursive(skillTypeID)
        required[skillTypeID] = skillLevel

        def already_trained_or_queued(x):
            skillID, level = x
            skill = self.skills.GetSkillIncludingLapsed(skillID)
            if skill is None or skill.trainedSkillLevel is None or skill.trainedSkillLevel >= level:
                return False
            queued = self.skills.GetMaxSkillLevelsInQueue()
            if queued.get(skillID, 0) >= level:
                return False
            return True

        skills = filter(already_trained_or_queued, required.items())
        skillList = []
        while skills:
            skillID, level = skills.pop(0)
            required = self.skills.GetRequiredSkillsRecursive(skillID)
            if any((sid in required for sid, _ in skills)):
                skills.append((skillID, level))
                continue
            nextLevel = int(self.FindNextLevel(skillID, skillQueue=self.GetQueue()))
            for lvl in xrange(nextLevel, int(level + 1)):
                skillList.append((skillID, lvl))

        self.AddSkillsToQueue(skillList)

    def IsTransactionOpen(self):
        return self.cachedSkillQueue is not None

    def RemoveSkillFromQueue(self, skillTypeID, skillLevel):
        self.CheckCanRemoveSkillFromQueue(skillTypeID, skillLevel)
        self.InternalRemoveFromQueue(skillTypeID, skillLevel)
        self.OnClientQueueModified()
        PlaySound(uiconst.SOUND_REMOVE)
        sm.ScatterEvent('OnClientEvent_SkillsRemovedFromQueue', ((skillTypeID, skillLevel),))

    def RemoveSkillsFromQueue(self, skills):
        removed = []
        try:
            for typeID, level in skills:
                self.CheckCanRemoveSkillFromQueue(typeID, level)
                self.InternalRemoveFromQueue(typeID, level)
                removed.append((typeID, level))

        finally:
            if removed:
                self.OnClientQueueModified()
                PlaySound(uiconst.SOUND_REMOVE)
                sm.ScatterEvent('OnClientEvent_SkillsRemovedFromQueue', removed)

    def OnClientQueueModified(self):
        if self.IsAllCharacterTrainingSlotsUsed():
            activate = False
        else:
            activate = True
        try:
            self.CommitTransaction(activate)
            self.BeginTransaction()
            sm.ScatterEvent('OnSkillQueueModified')
        except UserError as e:
            if e.msg == 'SkillInQueueRequiresOmegaCloneState':
                sm.ScatterEvent('OnSkillQueueModified')
            elif e.msg == 'SkillInQueueOverAlphaSpTrainingSize':
                self.CommitTransaction(activate=False)
                self.BeginTransaction()
                sm.ScatterEvent('OnSkillQueueModified')
            else:
                raise

    def CheckCanRemoveSkillFromQueue(self, skillTypeID, skillLevel):
        self.PrimeCache()
        if skillTypeID not in self.skillQueueCache:
            return
        for cacheLevel in self.skillQueueCache[skillTypeID]:
            if cacheLevel > skillLevel:
                raise UserError('QueueCannotRemoveSkillsWithHigherLevelsStillInQueue')

        dependencies = sm.GetService('skills').GetDependentSkills(skillTypeID)
        for dependentTypeID, requiredLevel in dependencies.iteritems():
            if skillLevel <= requiredLevel and dependentTypeID in self.skillQueueCache:
                raise UserError('QueueCannotRemoveSkillsWithDependentSkillsInQueue')

    def FindInQueue(self, skillTypeID, skillLevel):
        self.PrimeCache()
        if skillTypeID not in self.skillQueueCache:
            return None
        if skillLevel not in self.skillQueueCache[skillTypeID]:
            return None
        return self.skillQueueCache[skillTypeID][skillLevel]

    def MoveSkillToPosition(self, skillTypeID, skillLevel, position):
        self.CheckCanInsertSkillAtPosition(skillTypeID, skillLevel, position)
        self.PrimeCache()
        currentPosition = self.skillQueueCache[skillTypeID][skillLevel]
        if currentPosition < position:
            position -= 1
        self.InternalRemoveFromQueue(skillTypeID, skillLevel)
        newPosition = self.AddSkillToQueue(skillTypeID, skillLevel, position)
        return newPosition

    def GetQueue(self):
        return self.skillQueue[:]

    def GetQueueAsRequirements(self):
        return [ (s.trainingTypeID, s.trainingToLevel) for s in self.GetQueue() ]

    def GetSkillLevelsInQueue(self):
        return {skill.trainingTypeID:skill.trainingToLevel for skill in self.GetQueue()}

    def GetServerQueue(self):
        if self.IsTransactionOpen():
            return self.cachedSkillQueue[:]
        else:
            return self.GetQueue()

    def GetNumberOfSkillsInQueue(self):
        return len(self.skillQueue)

    def GetTrainingLengthOfQueue(self, position = None):
        if position is not None and position < 0:
            raise RuntimeError('Invalid queue position: ', position)
        trainingTime = 0
        spInQueue = 0
        skillBoosters = self.GetSkillAcceleratorBoosters()
        playerTheoreticalSkillPoints = {}
        skills = self.skills.GetSkillsIncludingLapsed()
        currentIndex = 0
        finalIndex = position
        if finalIndex is None:
            finalIndex = len(self.skillQueue)
        for trainingSkill in self.skillQueue:
            queueSkillTypeID = trainingSkill.trainingTypeID
            queueSkillLevel = trainingSkill.trainingToLevel
            if currentIndex >= finalIndex:
                break
            currentIndex += 1
            if queueSkillTypeID not in playerTheoreticalSkillPoints:
                skill = self.skills.GetSkill(queueSkillTypeID)
                playerTheoreticalSkillPoints[queueSkillTypeID] = self.GetSkillPointsFromSkillObject(queueSkillTypeID, skill)
            addedSP, addedTime, isAccelerated = self.GetAddedSpAndAddedTimeForSkill(queueSkillTypeID, queueSkillLevel, skills, playerTheoreticalSkillPoints, trainingTime, skillBoosters)
            trainingTime += addedTime
            spInQueue += addedSP
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP

        return (trainingTime, spInQueue)

    def GetTrainingEndTimeOfQueue(self):
        timeLeft, _ = self.GetTrainingLengthOfQueue()
        timeEnd = gametime.GetWallclockTime() + timeLeft
        inTraining = self.SkillInTraining()
        if inTraining and self.FindInQueue(inTraining.typeID, inTraining.trainedSkillLevel + 1) > 0:
            fullTrainingTime = self.GetTrainingLengthOfSkill(inTraining.typeID, inTraining.trainedSkillLevel + 1)
            ETA = self.GetEndOfTraining(inTraining.typeID)
            if ETA is not None:
                timeEnd -= fullTrainingTime[1]
                leftTime = ETA - blue.os.GetWallclockTime()
                timeEnd += leftTime
        return long(timeEnd)

    def GetTrainingLengthOfSkill(self, skillTypeID, skillLevel, position = None):
        if position is not None and (position < 0 or position > len(self.skillQueue)):
            raise RuntimeError('GetTrainingLengthOfSkill received an invalid position.')
        trainingTime = 0
        currentIndex = 0
        targetIndex = position
        if targetIndex is None:
            targetIndex = self.FindInQueue(skillTypeID, skillLevel)
            if targetIndex is None:
                targetIndex = len(self.skillQueue)
        playerTheoreticalSkillPoints = {}
        skills = self.skills.GetSkillsIncludingLapsed()
        skillBoosters = self.GetSkillAcceleratorBoosters()
        for trainingSkill in self.skillQueue:
            queueSkillTypeID = trainingSkill.trainingTypeID
            queueSkillLevel = trainingSkill.trainingToLevel
            if currentIndex >= targetIndex:
                break
            elif queueSkillTypeID == skillTypeID and queueSkillLevel == skillLevel and currentIndex < targetIndex:
                currentIndex += 1
                continue
            addedSP, addedTime, _ = self.GetAddedSpAndAddedTimeForSkill(queueSkillTypeID, queueSkillLevel, skills, playerTheoreticalSkillPoints, trainingTime, skillBoosters)
            currentIndex += 1
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP

        addedSP, addedTime, isAccelerated = self.GetAddedSpAndAddedTimeForSkill(skillTypeID, skillLevel, skills, playerTheoreticalSkillPoints, trainingTime, skillBoosters)
        trainingTime += addedTime
        return (long(trainingTime), long(addedTime), isAccelerated)

    def GetSkillPointsAndTimeNeededToTrain(self, skillTypeID, skillLevel, existingSkillPoints = 0, trainingStartTime = None):
        calculator = self.skills.GetSkillTrainingTimeCalculator()
        try:
            if existingSkillPoints:
                skillPointsToTrain, trainingTime = calculator.get_skill_points_and_time_to_train_given_existing_skill_points(skillTypeID, skillLevel, trainingStartTime, existingSkillPoints)
            else:
                skillPointsToTrain, trainingTime = calculator.get_skill_points_and_time_to_train(skillTypeID, skillLevel, trainingStartTime)
        except SkillLevelAlreadyTrainedError:
            skillPointsToTrain = 0
            trainingTime = 0

        return (skillPointsToTrain, float(trainingTime))

    def TrimQueue(self):
        trainingTime = 0
        skillBoosters = self.GetSkillAcceleratorBoosters()
        playerTheoreticalSkillPoints = {}
        skills = self.skills.GetSkillsIncludingLapsed()
        cutoffIndex = 0
        for trainingSkill in self.skillQueue:
            queueSkillTypeID = trainingSkill.trainingTypeID
            queueSkillLevel = trainingSkill.trainingToLevel
            cutoffIndex += 1
            addedSP, addedTime, isAccelerated = self.GetAddedSpAndAddedTimeForSkill(queueSkillTypeID, queueSkillLevel, skills, playerTheoreticalSkillPoints, trainingTime, skillBoosters)
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP
            if trainingTime > self.GetMaxSkillQueueLimitLength():
                break

        if cutoffIndex < len(self.skillQueue):
            removedSkills = self.skillQueue[cutoffIndex:]
            self.skillQueue = self.skillQueue[:cutoffIndex]
            self.skillQueueCache = None
            eve.Message('skillQueueTrimmed', {'num': len(removedSkills)})

    def GetSkillAcceleratorBoosters(self):
        return self.skills.GetSkillAcceleratorBoosters()

    def GetAddedSpAndAddedTimeForSkill(self, skillTypeID, skillLevel, skillSet, theoreticalSkillPointsDict, trainingTimeOffset, skillBoosters):
        skillStartTime = long(trainingTimeOffset) + gametime.GetWallclockTime()
        isAccelerated = skillBoosters.is_any_booster_active_at_time(skillStartTime)
        if skillTypeID not in theoreticalSkillPointsDict:
            skillObj = skillSet.get(skillTypeID, None)
            theoreticalSkillPointsDict[skillTypeID] = self.GetSkillPointsFromSkillObject(skillTypeID, skillObj)
        addedSP, addedTime = self.GetSkillPointsAndTimeNeededToTrain(skillTypeID, skillLevel, theoreticalSkillPointsDict[skillTypeID], skillStartTime)
        return (addedSP, addedTime, isAccelerated)

    def GetAllTrainingLengths(self):
        trainingTime = 0
        skillBoosters = self.GetSkillAcceleratorBoosters()
        resultsDict = {}
        playerTheoreticalSkillPoints = {}
        skills = self.skills.GetSkillsIncludingLapsed()
        for trainingSkill in self.skillQueue:
            queueSkillTypeID = trainingSkill.trainingTypeID
            queueSkillLevel = trainingSkill.trainingToLevel
            addedSP, addedTime, isAccelerated = self.GetAddedSpAndAddedTimeForSkill(queueSkillTypeID, queueSkillLevel, skills, playerTheoreticalSkillPoints, trainingTime, skillBoosters)
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP
            resultsDict[queueSkillTypeID, queueSkillLevel] = (trainingTime, addedTime, isAccelerated)

        return resultsDict

    def ApplyFreeSkillPointsToQueue(self):
        handler = sm.GetService('skills').GetSkillHandler()
        pointsBySkillTypeID = handler.GetFreeSkillPointsAppliedToQueue()
        if pointsBySkillTypeID:
            handler.ApplyFreeSkillPointsToQueue()

    def ApplyFreeSkillPointsToSkills(self, skillTypeIDsAndLevels):
        handler = sm.GetService('skills').GetSkillHandler()
        pointsBySkillTypeID = handler.GetFreeSkillPointsAppliedToSkills(skillTypeIDsAndLevels)
        if pointsBySkillTypeID:
            handler.ApplyFreeSkillPointsToSkills(skillTypeIDsAndLevels)

    def GetSkillLevelAndProgressWithFreePoints(self, pointsBySkillTypeID):
        skillSvc = sm.GetService('skills')
        levelBySkillTypeID = {}
        for typeID, points in pointsBySkillTypeID.iteritems():
            currentPoints = skillSvc.MySkillPoints(typeID)
            totalPoints = currentPoints + points
            rank = skillSvc.GetSkillRank(typeID)
            level = GetSkillLevelRaw(totalPoints, rank)
            progress = GetLevelProgress(totalPoints, rank)
            levelBySkillTypeID[typeID] = (level, progress)

        return levelBySkillTypeID

    def GetProgressOfAllSkills(self):
        skillSvc = sm.GetService('skills')
        progressBySkillTypeID = {}
        for skill in self.GetQueue():
            currentPoints = skillSvc.MySkillPoints(skill.trainingTypeID)
            rank = skillSvc.GetSkillRank(skill.trainingTypeID)
            progress = GetLevelProgress(currentPoints, rank)
            progressBySkillTypeID[skill.trainingTypeID] = progress

        return progressBySkillTypeID

    def InternalRemoveFromQueue(self, skillTypeID, skillLevel):
        if not len(self.skillQueue):
            return
        skillPosition = self.FindInQueue(skillTypeID, skillLevel)
        if skillPosition is None:
            raise UserError('QueueSkillNotPresent')
        if skillPosition == len(self.skillQueue):
            del self.skillQueueCache[skillTypeID][skillLevel]
            self.skillQueue.pop()
        else:
            self.skillQueueCache = None
            self.skillQueue.pop(skillPosition)

    def ClearCache(self):
        self.skillQueueCache = None

    def AddToCache(self, skillTypeID, skillLevel, position):
        self.PrimeCache()
        if skillTypeID not in self.skillQueueCache:
            self.skillQueueCache[skillTypeID] = {}
        self.skillQueueCache[skillTypeID][skillLevel] = position

    def GetPlayerAttributeDict(self):
        return self.skills.GetCharacterAttributes()

    def PrimeCache(self, force = False):
        if force:
            self.skillQueueCache = None
        if self.skillQueueCache is None:
            i = 0
            self.skillQueueCache = {}
            for trainingSkill in self.skillQueue:
                self.AddToCache(trainingSkill.trainingTypeID, trainingSkill.trainingToLevel, i)
                i += 1

    def GetSkillPointsFromSkillObject(self, skillTypeID, skillInfo):
        if skillInfo is None:
            return 0
        totalSkillPoints = skillInfo.trainedSkillPoints or 0
        trainingSkill = self.SkillInTraining(skillTypeID)
        serverQueue = self.GetServerQueue()
        if trainingSkill and len(serverQueue):
            skillPointsTrained = self.GetEstimatedSkillPointsTrained(skillTypeID)
            totalSkillPoints = max(skillPointsTrained, totalSkillPoints)
        return totalSkillPoints

    def GetEstimatedSkillPointsTrained(self, skillTypeID):
        startTime = self.GetStartTimeOfQueue()
        currentTime = gametime.GetWallclockTime()
        if startTime is None:
            startTime = currentTime
        trainingCalculator = self.skills.GetSkillTrainingTimeCalculator()
        with trainingCalculator.specific_current_time_context(startTime):
            skillPointsTrained = trainingCalculator.get_skill_points_trained_at_sample_time(skillTypeID, startTime, currentTime)
        return skillPointsTrained

    def GetEstimatedTotalSkillPoints(self):
        cachedTotalSkillPoints = sm.GetService('skills').GetTotalSkillPointsForCharacter()
        currentSkill = self.SkillInTraining()
        if currentSkill:
            currentSkillPointsForSkill = self.GetSkillPointsFromSkillObject(currentSkill.typeID, currentSkill)
            cachedCurrentSkill = sm.GetService('skills').GetSkill(currentSkill.typeID)
            if cachedCurrentSkill:
                return cachedTotalSkillPoints - cachedCurrentSkill.trainedSkillPoints + currentSkillPointsForSkill
        return cachedTotalSkillPoints

    def OnServerSkillsChanged(self, skillInfos):
        self.PrimeCache()
        for skillTypeID, skillInfo in skillInfos.iteritems():
            skill = self.skills.GetSkill(skillTypeID)
            if not skill and skillInfo.trainedSkillLevel > 0:
                self.LogError('skillQueueSvc::OnServerSkillsChanged skill %s not found' % skillTypeID)
                continue
            self._RemoveSkillFromQueueCacheIfTrained(skillInfo, skillTypeID)
            self._RemoveSkillFromCachedQueueIfTrained(skillInfos, skillTypeID)

    def OnCloseApp(self):
        if self.IsQueueChanged():
            self.CommitTransaction()

    def _RemoveSkillFromQueueCacheIfTrained(self, skillInfo, skillTypeID):
        skillLevel = skillInfo.trainedSkillLevel
        if self.skillQueueCache and skillTypeID in self.skillQueueCache:
            if skillLevel in self.skillQueueCache[skillTypeID]:
                self.InternalRemoveFromQueue(skillTypeID, skillLevel)

    def _RemoveSkillFromCachedQueueIfTrained(self, skillInfos, skillTypeID):
        if self.cachedSkillQueue:
            keepSkills = []
            for trainingSkill in self.cachedSkillQueue:
                if trainingSkill.trainingTypeID == skillTypeID:
                    finishedSkill = skillInfos[skillTypeID]
                    if trainingSkill.trainingToLevel <= finishedSkill.trainedSkillLevel:
                        continue
                keepSkills.append(trainingSkill)

            self.cachedSkillQueue = keepSkills

    def OnSkillQueuePausedServer(self, *args):
        queue = self.skillQueue
        if self.IsTransactionOpen():
            queue = self.cachedSkillQueue
        if queue:
            for skillEntry in queue:
                skillEntry.trainingStartTime = skillEntry.trainingEndTime = None

        sm.ScatterEvent('OnSkillQueuePaused')
        PlaySound('skill_training_stop_play')

    def OnNewSkillQueueSaved(self, newQueue):
        if self.IsTransactionOpen():
            self.cachedSkillQueue = newQueue
        self.skillQueue = newQueue
        sm.ScatterEvent('OnSkillQueueChanged')

    def TrainSkillNow(self, skillTypeID, toSkillLevel, *args):
        inTraining = self.SkillInTraining()
        if inTraining and eve.Message('ConfirmSkillTrainingNow', {'name': evetypes.GetName(inTraining.typeID),
         'lvl': inTraining.trainedSkillLevel + 1}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return
        self.BeginTransaction()
        try:
            if self.FindInQueue(skillTypeID, toSkillLevel) is not None:
                self.MoveSkillToPosition(skillTypeID, toSkillLevel, 0)
                message = ('SkillQueueStarted',)
            else:
                self.AddSkillToQueue(skillTypeID, toSkillLevel, 0)
                skillName = localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndLevel', skill=skillTypeID, amount=toSkillLevel)
                if inTraining:
                    message = ('AddedToQueue', {'skillname': skillName})
                else:
                    message = ('AddedToQueueAndStarted', {'skillname': skillName})
            self.CommitTransaction()
            eve.Message(*message)
        except Exception:
            self.RollbackTransaction()
            raise

    def AddSkillToEnd(self, skillTypeID, current, nextLevel = None):
        queueLength = self.GetNumberOfSkillsInQueue()
        if queueLength >= SKILLQUEUE_MAX_NUM_SKILLS:
            raise UserError('QueueTooManySkills', {'num': SKILLQUEUE_MAX_NUM_SKILLS})
        totalTime, _ = self.GetTrainingLengthOfQueue()
        if totalTime > self.GetMaxSkillQueueLimitLength():
            raise UserError('QueueTooLong')
        if nextLevel is None:
            queue = self.GetServerQueue()
            nextLevel = self.FindNextLevel(skillTypeID, current, queue)
        if self.FindInQueue(skillTypeID, nextLevel) is not None:
            raise UserError('QueueSkillAlreadyPresent')
        self.BeginTransaction()
        try:
            self.AddSkillToQueue(skillTypeID, nextLevel)
            self.CommitTransaction()
        except Exception:
            self.RollbackTransaction()
            raise

        text = localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndLevel', skill=skillTypeID, amount=nextLevel)
        if self.SkillInTraining():
            eve.Message('AddedToQueue', {'skillname': text})
        else:
            eve.Message('AddedToQueueAndStarted', {'skillname': text})
        sm.ScatterEvent('OnSkillQueueRefreshed')

    def FindNextLevel(self, skillTypeID, current = None, skillQueue = None):
        skill = self.skills.GetSkillIncludingLapsed(skillTypeID)
        current = skill.trainedSkillLevel or 0 if skill else 0
        if skillQueue is None:
            skillQueue = self.GetServerQueue()
        skillQueue = [ (skill.trainingTypeID, skill.trainingToLevel) for skill in skillQueue ]
        nextLevel = None
        for i in xrange(1, 7):
            if i <= current:
                continue
            inQueue = bool((skillTypeID, i) in skillQueue)
            if inQueue is False:
                nextLevel = i
                break

        return nextLevel

    def OnMultipleCharactersTrainingUpdated(self):
        self.PrimeCache(True)
        self._isAllCharacterTrainingSlotsUsed = None
        sm.ScatterEvent('OnMultipleCharactersTrainingRefreshed')

    def GetMultipleCharacterTraining(self, force = False):
        userSvc = sm.RemoteSvc('userSvc')
        if force:
            userSvc.InvalidateMultiCharacterTrainingCache(session.userid)
        return userSvc.GetMultiCharactersTrainingSlots()

    def IsSkillInQueue(self, skillTypeID):
        self.PrimeCache()
        if skillTypeID in self.skillQueueCache:
            return True
        return False

    def IsAllCharacterTrainingSlotsUsed(self):
        if self._isAllCharacterTrainingSlotsUsed is None:
            queues = self.GetMultipleCharacterTraining().items()
            characterData = sm.GetService('cc').GetCharacterSelectionData()
            activeQueues = 1 + len(queues)
            usedQueues = 0
            for characterDetails in characterData.details.values():
                isTraining = characterDetails.GetSkillInTrainingInfo()['currentSkill'] is not None
                if characterDetails.charID != session.charid and isTraining:
                    usedQueues += 1

            self._isAllCharacterTrainingSlotsUsed = usedQueues == activeQueues
        return self._isAllCharacterTrainingSlotsUsed

    def IsQueueWndOpen(self):
        from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
        return CharacterSheetWindow.IsOpen()

    def FindHighestLevelInQueue(self, skillTypeID):
        if self.IsSkillInQueue(skillTypeID):
            return max(self.skillQueueCache[skillTypeID])

    def RemoveHighestLevelFromQueue(self, skillTypeID):
        if self.IsSkillInQueue(skillTypeID):
            self.RemoveSkillFromQueue(skillTypeID, self.FindHighestLevelInQueue(skillTypeID))

    def GetAddMenuForSkillEntries(self, skillTypeID, skillInfo):
        m = []
        if skillInfo is None:
            return m
        skillLevel = skillInfo.trainedSkillLevel
        if skillLevel is not None:
            if skillLevel < skillConst.skill_max_level:
                queue = self.GetQueue()
                nextLevel = self.FindNextLevel(skillTypeID, skillLevel, queue)
                if not self.SkillInTraining(skillTypeID):
                    trainingTime, totalTime, _ = self.GetTrainingLengthOfSkill(skillTypeID, skillLevel + 1, 0)
                    if trainingTime <= 0:
                        takesText = localization.GetByLabel('UI/SkillQueue/Skills/CompletionImminent')
                    else:
                        takesText = localization.GetByLabel('UI/SkillQueue/Skills/SkillTimeLeft', timeLeft=long(trainingTime))
                    if nextLevel < 6 and self.FindInQueue(skillTypeID, skillLevel + 1) is None:
                        trainText = MenuLabel('UI/SkillQueue/AddSkillMenu/AddToFrontOfQueueTime', {'takes': takesText})
                        m.append((trainText, self.AddSkillToQueue, (skillTypeID, nextLevel, 0)))
                if self.IsSkillInQueue(skillTypeID):
                    removeText = MenuLabel('UI/SkillQueue/AddSkillMenu/RemoveHighestLevelFromQueue', {'level': self.FindHighestLevelInQueue(skillTypeID)})
                    m.append((removeText, self.RemoveHighestLevelFromQueue, (skillTypeID,)))
                if nextLevel < 6:
                    label = MenuLabel('UI/SkillQueue/AddSkillMenu/AddToEndOfQueue', {'nextLevel': nextLevel})
                    m.append((label, self.AddSkillToQueue, (skillInfo.typeID,)))
                if sm.GetService('skills').GetFreeSkillPoints() > 0:
                    diff = sm.GetService('skills').SkillpointsNextLevel(skillTypeID) + 0.5 - skillInfo.trainedSkillPoints
                    m.append((MenuLabel('UI/SkillQueue/AddSkillMenu/ApplySkillPoints'), self.UseFreeSkillPoints, (skillInfo.typeID, diff)))
        if m:
            m.append(None)
        return m

    def UseFreeSkillPoints(self, skillTypeID, diff):
        inTraining = self.SkillInTraining()
        if inTraining is not None and inTraining.typeID == skillTypeID:
            eve.Message('CannotApplyFreePointsWhileTrainingSkill')
            return
        freeSkillPoints = sm.StartService('skills').GetFreeSkillPoints()
        text = localization.GetByLabel('UI/SkillQueue/AddSkillMenu/UseSkillPointsWindow', skill=skillTypeID, skillPoints=int(diff))
        caption = localization.GetByLabel('UI/SkillQueue/AddSkillMenu/ApplySkillPoints')
        ret = uix.QtyPopup(maxvalue=freeSkillPoints, caption=caption, label=text, setvalue=int(diff))
        if ret is None:
            return
        sp = int(ret.get('qty', ''))
        sm.StartService('skills').ApplyFreeSkillPoints(skillTypeID, sp)
        PlaySound('st_allocate_skillpoints_play')

    def SkillInTraining(self, skillTypeID = None):
        activeQueue = self.GetServerQueue()
        if len(activeQueue) and activeQueue[0].trainingEndTime:
            if skillTypeID is None or activeQueue[0].trainingTypeID == skillTypeID:
                return self.skills.GetSkill(activeQueue[0].trainingTypeID)

    def GetActiveSkillTypeID(self):
        skill = self.SkillInTraining()
        if skill:
            return skill.typeID

    def GetTimeForTraining(self, skillTypeID, toLevel, trainingStartTime = 0):
        currentTraining = self.SkillInTraining(skillTypeID)
        currentSkillPointsDict = {}
        currentTime = gametime.GetWallclockTime()
        if currentTraining:
            trainingEndTime = self.GetEndOfTraining(skillTypeID)
            timeForTraining = trainingEndTime - currentTime
        else:
            timeOffset = 0
            if trainingStartTime:
                timeOffset = trainingStartTime - currentTime
            skill = self.skills.GetSkill(skillTypeID)
            attributes = self.GetPlayerAttributeDict()
            skillBoosters = self.GetSkillAcceleratorBoosters()
            skillBoosters.apply_expired_attributes_at_time_offset(attributes, timeOffset)
            currentSkillPointsDict[skillTypeID] = self.GetSkillPointsFromSkillObject(skillTypeID, skill)
            _, timeForTraining = self.GetSkillPointsAndTimeNeededToTrain(skillTypeID, toLevel, currentSkillPointsDict[skillTypeID], trainingStartTime or currentTime)
        return long(timeForTraining)

    def GetEndOfTraining(self, skillTypeID):
        skillQueue = self.GetServerQueue()
        if not len(skillQueue) or skillQueue[0].trainingTypeID != skillTypeID:
            return None
        else:
            return skillQueue[0].trainingEndTime

    def GetStartTimeOfQueue(self):
        skillQueue = self.GetServerQueue()
        if not skillQueue:
            return None
        else:
            return skillQueue[0].trainingStartTime

    def IsMoveAllowed(self, draggedNode, checkedIdx):
        queue = self.GetQueue()
        if checkedIdx is None:
            checkedIdx = len(queue)
        guid = getattr(draggedNode, '__guid__', None)
        skillSvc = sm.GetService('skills')
        if getattr(draggedNode, 'skillID', None):
            if guid == 'listentry.SkillEntry':
                level = self.FindNextLevel(draggedNode.skillID, None, queue)
            else:
                level = draggedNode.Get('trainToLevel', 1)
                if draggedNode.inQueue is None:
                    level += 1
            return self.CheckCanInsertSkillAtPosition(draggedNode.skillID, level, checkedIdx, check=1, performLengthTest=False)
        if guid in ('xtriui.InvItem', 'listentry.InvItem'):
            category = GetAttrs(draggedNode, 'rec', 'categoryID')
            if category != const.categorySkill:
                return
            typeID = GetAttrs(draggedNode, 'rec', 'typeID')
            if typeID is None:
                return
            if skillSvc.IsSkillInjected(typeID):
                return False
            meetsReq = sm.StartService('godma').CheckSkillRequirementsForType(typeID)
            if not meetsReq:
                return False
            return True
        if guid == 'listentry.SkillTreeEntry':
            typeID = draggedNode.typeID
            if typeID is None:
                return False
            if not skillSvc.IsSkillInjected(typeID):
                return False
            skill = skillSvc.GetSkill(typeID)
            level = self.FindNextLevel(typeID, skill.trainedSkillLevel, queue)
            return self.CheckCanInsertSkillAtPosition(typeID, level, checkedIdx, check=1, performLengthTest=False)
        if getattr(draggedNode, 'typeID', None):
            if evetypes.GetCategoryID(draggedNode.typeID) == const.categorySkill:
                level = self.FindNextLevel(draggedNode.typeID, None, queue)
                return self.CheckCanInsertSkillAtPosition(draggedNode.typeID, level, checkedIdx, check=1, performLengthTest=False)

    def IsSkillEntry(self, draggedNode):
        if getattr(draggedNode, 'skillID', None):
            return True
        guid = getattr(draggedNode, '__guid__', None)
        if guid in ('xtriui.InvItem', 'listentry.InvItem'):
            category = GetAttrs(draggedNode, 'rec', 'categoryID')
            if category == const.categorySkill:
                return True
        else:
            if guid == 'listentry.SkillTreeEntry':
                return True
            if getattr(draggedNode, 'typeID', None):
                if evetypes.GetCategoryID(draggedNode.typeID) == const.categorySkill:
                    return True
        return False

    def IsRemoveAllowed(self, typeID, level):
        try:
            self.CheckCanRemoveSkillFromQueue(typeID, level)
            return True
        except UserError:
            return False

    def GetSkillPlanImporter(self):
        if self.skillplanImporter is None:
            self.skillplanImporter = ImportSkillPlan(IsUsingDefaultLanguage(session))
        return self.skillplanImporter

    @contextmanager
    def ChangeQueueLock(self):
        ReentrantLock(self, 'SkillQueueSvc:xActLock')
        try:
            yield
        finally:
            UnLock(self, 'SkillQueueSvc:xActLock')

    def IsQueueChanged(self):
        if self.cachedSkillQueue is None:
            return False
        if len(self.skillQueue) != len(self.cachedSkillQueue):
            return True
        for s1, s2 in zip(self.skillQueue, self.cachedSkillQueue):
            isSameType = s1.trainingTypeID == s2.trainingTypeID
            isSameLevel = s1.trainingToLevel == s2.trainingToLevel
            if not isSameType or not isSameLevel:
                return True

        return False

    def GetTimeSavedByUnallocatedPoints(self, unallocatedPoints):
        totalTimeSaved = 0
        allTrainingLengths = self.GetAllTrainingLengths()
        skillInTraining = self.SkillInTraining()
        actualEnd = self.GetEndOfTraining(skillInTraining.typeID) if skillInTraining else None
        for skill in self.GetQueue():
            trainingID = (skill.trainingTypeID, skill.trainingToLevel)
            if trainingID not in allTrainingLengths:
                continue
            timeLeft = allTrainingLengths[trainingID][1]
            if skillInTraining and skill.trainingTypeID == skillInTraining.typeID and skill.trainingToLevel - 1 == skillInTraining.trainedSkillLevel:
                if actualEnd is not None:
                    timeLeft = float(actualEnd - blue.os.GetWallclockTime())
            if unallocatedPoints > 0:
                pointsTrained = skill.trainingDestinationSP - skill.trainingStartSP
                if unallocatedPoints >= pointsTrained:
                    totalTimeSaved += timeLeft
                else:
                    fractionCovered = min(1.0, unallocatedPoints / float(pointsTrained))
                    totalTimeSaved += fractionCovered * timeLeft
                unallocatedPoints -= pointsTrained

        return totalTimeSaved
