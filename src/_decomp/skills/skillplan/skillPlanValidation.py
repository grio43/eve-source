#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\skillPlanValidation.py
import blue
import evetypes
import logging
import telemetry
from collections import Counter, OrderedDict
import dogma
from eve.common.lib import appConst
from inventorycommon.const import categorySkill
logger = logging.getLogger(__name__)
_allSkillTypeIDs = None
_allPrereqs = None

def _InitializeData(allSkillTypeIDs = None, allPrereqs = None):
    global _allPrereqs
    global _allSkillTypeIDs
    if allSkillTypeIDs is None:
        if _allSkillTypeIDs is None:
            _allSkillTypeIDs = evetypes.GetTypeIDsByCategory(categorySkill)
        allSkillTypeIDs = _allSkillTypeIDs
    if allPrereqs is None:
        if _allPrereqs is None:
            _allPrereqs = {skillID:sm.GetService('skills').GetRequiredSkills(skillID) for skillID in allSkillTypeIDs}
        allPrereqs = _allPrereqs
    return (allSkillTypeIDs, allPrereqs)


@telemetry.ZONE_FUNCTION
def IsPlanValid(skillList, allSkillTypeIDs = None, allPrereqs = None):
    allSkillTypeIDs, allPrereqs = _InitializeData(allSkillTypeIDs, allPrereqs)
    return HasNoInvalidSkills(skillList, allSkillTypeIDs) and HasNoMissingOrDuplicateSkills(skillList) and HasNoMissingPrerequisites(skillList, allPrereqs) and HasNoIncorrectOrder(skillList, allPrereqs)


@telemetry.ZONE_FUNCTION
def ValidateSkillPlan(skillList, allSkillTypeIDs = None, allPrereqs = None):
    allSkillTypeIDs, allPrereqs = _InitializeData(allSkillTypeIDs, allPrereqs)
    changedInvalid = _RemoveInvalidSkills(skillList, allSkillTypeIDs)
    changedMissingOrDuplicate = _AddMissingAndRemoveDuplicateSkillLevels(skillList)
    changedMissingPrereqs = _AddMissingPrerequisites(skillList, allPrereqs)
    changedOrder = _VerifySkillOrdering(skillList, allPrereqs)
    return changedInvalid or changedMissingOrDuplicate or changedMissingPrereqs or changedOrder


@telemetry.ZONE_FUNCTION
def HasNoInvalidSkills(skillList, allSkillTypeIDs):
    return len(_GetInvalidSkills(skillList, allSkillTypeIDs)) == 0


@telemetry.ZONE_FUNCTION
def HasNoMissingOrDuplicateSkills(skillList):
    duplicateLevels, missingLevels = _GetDuplicateAndMissingLevels(skillList)
    return len(duplicateLevels) == 0 and len(missingLevels) == 0


@telemetry.ZONE_FUNCTION
def HasNoMissingPrerequisites(skillList, allPrereqs):
    skillPlanDict = _GetAsOrderedDictWithTargetLevels(skillList)
    for skillID in _GetSkillIDs(skillList):
        if len(_GetMissingPrerequisites(allPrereqs[skillID], skillPlanDict, skillID)) > 0:
            return False

    return True


@telemetry.ZONE_FUNCTION
def HasNoIncorrectOrder(skillList, allPrereqs):
    skillIDs = _GetSkillIDs(skillList)
    for skillID in skillIDs:
        for prereqSkillID, targetLevel in allPrereqs[skillID].iteritems():
            if _IsIncorrectOrder(prereqSkillID, targetLevel, skillID, 1, skillList):
                return False

    skillPlanDict = _GetAsOrderedDictWithTargetLevels(skillList)
    for skillID, targetLevel in skillPlanDict.iteritems():
        for level in range(2, targetLevel + 1):
            if _IsIncorrectOrder(skillID, level - 1, skillID, level, skillList):
                return False

    return True


@telemetry.ZONE_FUNCTION
def _RemoveInvalidSkills(skillList, allSkillTypeIDs):
    toRemove = _GetInvalidSkills(skillList, allSkillTypeIDs)
    for each in toRemove:
        skillList.remove(each)

    return len(toRemove) > 0


@telemetry.ZONE_FUNCTION
def _AddMissingAndRemoveDuplicateSkillLevels(skillList):
    duplicateLevels, missingLevels = _GetDuplicateAndMissingLevels(skillList)
    _RemoveSkillLevels(duplicateLevels, skillList, 'duplicate skill level')
    _InsertMissingSkillLevels(missingLevels, skillList, 'missing skill level')
    return len(duplicateLevels) > 0 or len(missingLevels) > 0


@telemetry.ZONE_FUNCTION
def _AddMissingPrerequisites(skillList, allPrereqs):
    skillIDsToProcess = _GetSkillIDs(skillList)
    changed = False
    while len(skillIDsToProcess) > 0:
        targetSkillID = skillIDsToProcess.pop(0)
        skillPlanDict = _GetAsOrderedDictWithTargetLevels(skillList)
        prereqsDict = allPrereqs[targetSkillID]
        missingPrereqs = _GetMissingPrerequisites(prereqsDict, skillPlanDict, targetSkillID)
        if len(missingPrereqs) > 0:
            changed = True
        _InsertMissingSkillLevelsBefore(missingPrereqs, skillList, 'missing requirement for skill %d' % targetSkillID)
        for skillID in prereqsDict.iterkeys():
            skillIDsToProcess.append(skillID)

        blue.pyos.BeNice()

    return changed


@telemetry.ZONE_FUNCTION
def _VerifySkillOrdering(skillList, allPrereqsDict):
    changed = _FixIncorrectPrerequisiteOrders(skillList, allPrereqsDict)
    changed = _FixIncorrectLevelOrders(skillList) or changed
    return changed


def _GetSkillIDs(skillList):
    ret = []
    for skillID, level in skillList:
        if skillID not in ret:
            ret.append(skillID)

    return ret


def _GetAsOrderedDictWithTargetLevels(skillList):
    ret = OrderedDict()
    for typeID, level in skillList:
        ret[typeID] = max(ret.get(typeID, 0), level)

    return ret


def _GetAsDictWithAllLevels(skillList):
    levelsPerSkill = {}
    for skillTypeID, skillLevel in skillList:
        if skillTypeID not in levelsPerSkill:
            levelsPerSkill[skillTypeID] = []
        levelsPerSkill[skillTypeID].append(skillLevel)

    return levelsPerSkill


def _IsSkillInvalid(skillID, allSkillTypeIDs):
    return skillID not in allSkillTypeIDs or not evetypes.IsPublished(skillID) or dogma.data.get_type_attribute(skillID, appConst.attributeSkillIsObsolete, False)


def _GetInvalidSkills(skillList, allSkillTypeIDs):
    result = []
    for skillID, level in skillList:
        if _IsSkillInvalid(skillID, allSkillTypeIDs):
            result.append((skillID, level))
            logger.warn('invalid skill (unpublished): removing (%d, %d)' % (skillID, level))

    return result


def _GetDuplicateAndMissingLevels(skillList):
    levelsPerSkill = _GetAsDictWithAllLevels(skillList)
    missingLevels = {}
    duplicateLevels = {}
    for skillID, skillLevels in levelsPerSkill.iteritems():
        targetLevel = max(skillLevels)
        if len(skillLevels) > targetLevel:
            for k, v in Counter(skillLevels).items():
                if v > 1:
                    if skillID not in duplicateLevels:
                        duplicateLevels[skillID] = []
                    duplicateLevels[skillID].extend([ k for _ in range(0, v - 1) ])

        for i in range(1, targetLevel):
            if i not in levelsPerSkill[skillID]:
                if skillID not in missingLevels:
                    missingLevels[skillID] = []
                missingLevels[skillID].append(i)

    return (duplicateLevels, missingLevels)


def _GetMissingPrerequisites(prereqsDict, skillPlanDict, targetSkillID):
    missingPrereqs = {}
    for skillID, targetLevel in prereqsDict.iteritems():
        if skillID not in skillPlanDict:
            missingPrereqs[skillID] = ([ x for x in range(1, targetLevel + 1) ], targetSkillID, 1)
        elif skillPlanDict[skillID] < targetLevel:
            missingPrereqs[skillID] = ([ x for x in range(skillPlanDict[skillID] + 1, targetLevel + 1) ], targetSkillID, 1)

    return missingPrereqs


def _RemoveSkillLevels(skillsToRemove, skillList, message):
    if not skillsToRemove:
        return
    skillList.reverse()
    for skillID, levelsToRemove in skillsToRemove.iteritems():
        for level in levelsToRemove:
            logger.warn('%s: removing (%d, %d)' % (message, skillID, level))
            skillAndLevel = (skillID, level)
            if skillAndLevel in skillList:
                skillList.remove(skillAndLevel)
                blue.pyos.BeNice()

    skillList.reverse()


def _InsertMissingSkillLevelsBefore(missingLevels, skillList, message):
    for missingSkillID, (missingLevels, targetSkillID, targetLevel) in missingLevels.iteritems():
        targetIndex = skillList.index((targetSkillID, targetLevel))
        for i in sorted(missingLevels, reverse=True):
            logger.warn('%s: adding skill (%d, %d)' % (message, missingSkillID, i))
            skillList.insert(targetIndex, (missingSkillID, i))
            blue.pyos.BeNice()


def _InsertMissingSkillLevels(missingLevels, skillList, message):
    for missingSkillID, missingLevels in missingLevels.iteritems():
        for i in sorted(missingLevels, reverse=True):
            try:
                targetIndex = skillList.index((missingSkillID, i + 1))
            except ValueError:
                targetIndex = len(skillList) - 1

            logger.warn('%s: adding skill (%d, %d)' % (message, missingSkillID, i))
            skillList.insert(targetIndex, (missingSkillID, i))
            blue.pyos.BeNice()


def _FixIncorrectPrerequisiteOrders(outputSkillList, allPrereqsDict):
    skillIDsToProcess = _GetSkillIDs(outputSkillList)
    return _FixIncorrectPrerequisiteOrdersForList(outputSkillList, skillIDsToProcess, allPrereqsDict)


def _FixIncorrectPrerequisiteOrdersForList(outputSkillList, skillIDsToProcess, allPrereqsDict):
    changed = False
    while len(skillIDsToProcess) > 0:
        skillID = skillIDsToProcess.pop(0)
        prereqsFixed = _FixIncorrectPrerequisiteOrdersForOneSkill(outputSkillList, skillID, allPrereqsDict)
        for prereq in prereqsFixed:
            if prereq in skillIDsToProcess:
                skillIDsToProcess.remove(prereq)

        if len(prereqsFixed) > 0:
            changed = True

    return changed


def _FixIncorrectPrerequisiteOrdersForOneSkill(outputSkillList, skillID, allPrereqsDict):
    prereqs = allPrereqsDict[skillID].keys()
    for prereqSkillID, targetLevel in allPrereqsDict[skillID].iteritems():
        _InsertBeforeIfIncorrectOrder(prereqSkillID, targetLevel, skillID, 1, outputSkillList, 'incorrect order for %d and its prereq %d' % (skillID, prereqSkillID))
        for level in range(targetLevel - 1, 0, -1):
            _InsertBeforeIfIncorrectOrder(prereqSkillID, level, prereqSkillID, level + 1, outputSkillList, 'incorrect order for %d' % prereqSkillID)
            blue.pyos.BeNice()

    _FixIncorrectPrerequisiteOrdersForList(outputSkillList, prereqs, allPrereqsDict)
    return prereqs


def _FixIncorrectLevelOrders(skillList):
    changed = False
    skillPlanDict = _GetAsOrderedDictWithTargetLevels(skillList)
    for skillID, targetLevel in skillPlanDict.iteritems():
        for level in range(2, targetLevel + 1):
            changed = _InsertAfterIfIncorrectOrder(skillID, level - 1, skillID, level, skillList, 'incorrect order for %d' % skillID) or changed
            blue.pyos.BeNice()

    return changed


def _IsIncorrectOrder(mustComeFirstSkill, mustComeFirstLevel, mustComeSecondSkill, mustComeSecondLevel, skillList):
    mustComeFirstIndex = skillList.index((mustComeFirstSkill, mustComeFirstLevel))
    mustComeSecondIndex = skillList.index((mustComeSecondSkill, mustComeSecondLevel))
    return mustComeSecondIndex < mustComeFirstIndex


def _InsertAfterIfIncorrectOrder(mustComeFirstSkill, mustComeFirstLevel, mustComeSecondSkill, mustComeSecondLevel, skillList, message):
    mustComeFirstIndex = skillList.index((mustComeFirstSkill, mustComeFirstLevel))
    mustComeSecondIndex = skillList.index((mustComeSecondSkill, mustComeSecondLevel))
    if mustComeSecondIndex < mustComeFirstIndex:
        skillList.insert(mustComeFirstIndex + 1, (mustComeSecondSkill, mustComeSecondLevel))
        skillList.pop(mustComeSecondIndex)
        logger.warn('%s: moving (%d, %d) after (%d, %d)' % (message,
         mustComeSecondSkill,
         mustComeSecondLevel,
         mustComeFirstSkill,
         mustComeFirstLevel))
        return True
    return False


def _InsertBeforeIfIncorrectOrder(mustComeFirstSkill, mustComeFirstLevel, mustComeSecondSkill, mustComeSecondLevel, skillList, message):
    mustComeFirstIndex = skillList.index((mustComeFirstSkill, mustComeFirstLevel))
    mustComeSecondIndex = skillList.index((mustComeSecondSkill, mustComeSecondLevel))
    if mustComeSecondIndex < mustComeFirstIndex:
        skillList.pop(mustComeFirstIndex)
        skillList.insert(mustComeSecondIndex, (mustComeFirstSkill, mustComeFirstLevel))
        logger.warn('%s: moving (%d, %d) before (%d, %d)' % (message,
         mustComeFirstSkill,
         mustComeFirstLevel,
         mustComeSecondSkill,
         mustComeSecondLevel))
        return True
    return False
