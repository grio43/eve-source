#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterskills\util.py
import collections
import math
import characterskills
from dogma.const import attributeSkillTimeConstant
from inventorycommon.const import categorySkill, groupFakeSkills
DIVCONSTANT = math.log(2) * 2.5

def GetLevelProgress(skillPoints, skillTimeConstant):
    level = GetSkillLevelRaw(skillPoints, skillTimeConstant)
    if level >= characterskills.MAX_SKILL_LEVEL:
        return 0.0
    baseLevelPoints = GetSPForLevelRaw(skillTimeConstant, level)
    nextLevelPoints = GetSPForLevelRaw(skillTimeConstant, level + 1)
    return (skillPoints - baseLevelPoints) / float(nextLevelPoints - baseLevelPoints)


def GetSkillLevelRaw(skillPoints, skillTimeConstant):
    baseSkillLevelConstant = float(skillTimeConstant) * characterskills.SKILL_POINT_MULTIPLIER
    if baseSkillLevelConstant > skillPoints or baseSkillLevelConstant == 0:
        return 0
    level = 1 + int(math.log(skillPoints / baseSkillLevelConstant) / DIVCONSTANT)
    return min(level, characterskills.MAX_SKILL_LEVEL)


def GetSkillPointsPerMinute(primaryAttributeValue, secondaryAttributeValue):
    return primaryAttributeValue + secondaryAttributeValue / 2.0


def GetSPForAllLevels(skillTimeConstant):
    levelList = []
    for i in range(characterskills.MAX_SKILL_LEVEL + 1):
        levelList.append(GetSPForLevelRaw(skillTimeConstant, i))

    return levelList


def GetSPForLevelRaw(skillTimeConstant, level):
    if level <= 0:
        return 0
    if level > characterskills.MAX_SKILL_LEVEL:
        level = characterskills.MAX_SKILL_LEVEL
    preMultipliedSkillPoints = float(skillTimeConstant) * characterskills.SKILL_POINT_MULTIPLIER
    return int(math.ceil(preMultipliedSkillPoints * 2 ** (2.5 * (level - 1))))


def GetAllSkillGroups():
    import evetypes
    all_groups = evetypes.GetGroupIDsByCategory(categorySkill)
    if groupFakeSkills in all_groups:
        all_groups.remove(groupFakeSkills)
    return all_groups


def GetSkillTimeConstant(typeID):
    import dogma.data as dogma_data
    return dogma_data.get_type_attribute(typeID, attributeSkillTimeConstant)


def GetProgressRatioForSkillLevels(requiredSkills):
    spTotal = GetTotalSkillPoints(requiredSkills)
    if not spTotal:
        return 0
    else:
        spTrained = GetTrainedSkillPoints(requiredSkills)
        return float(spTrained) / spTotal


def GetTotalSkillPoints(requiredSkills):
    return sum((GetSPForLevelRaw(GetSkillTimeConstant(typeID), level) for typeID, level in requiredSkills.iteritems()))


def GetTrainedSkillPoints(requiredSkills):
    spTrained = 0
    for typeID, level in requiredSkills.iteritems():
        spRequiredForLevel = GetSPForLevelRaw(GetSkillTimeConstant(typeID), level)
        spTrained += min(spRequiredForLevel, sm.GetService('skillqueue').GetEstimatedSkillPointsTrained(typeID))

    return spTrained


def GetInTrainingSkillPoints(requiredSkills):
    inQueueSkills = sm.GetService('skillqueue').GetSkillLevelsInQueue()
    sp = 0
    for typeID, level in requiredSkills.iteritems():
        if typeID not in inQueueSkills:
            continue
        level = min(level, inQueueSkills[typeID])
        spRequiredForLevel = GetSPForLevelRaw(GetSkillTimeConstant(typeID), level)
        trained = min(spRequiredForLevel, sm.GetService('skillqueue').GetEstimatedSkillPointsTrained(typeID))
        sp += spRequiredForLevel - trained

    return sp


def GetInTrainingRatioForSkillLevels(requiredSkills):
    spTotal = GetTotalSkillPoints(requiredSkills)
    if not spTotal:
        return 0
    else:
        spInTraining = GetInTrainingSkillPoints(requiredSkills)
        return float(spInTraining) / spTotal


def GetSkillRequirementsDictFromSkillLevels(skillLevels):
    requiredSkills = collections.defaultdict(int)
    for typeID, level in skillLevels:
        requiredSkills[typeID] = max(level, requiredSkills[typeID])

    return requiredSkills
