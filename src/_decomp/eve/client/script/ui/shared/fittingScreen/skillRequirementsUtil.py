#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\skillRequirementsUtil.py


def GetAllSkillsAndLevels(typeIDs):
    allSkillsAndLevels = []
    for eachTypeID in typeIDs:
        skillsForType = []
        _GetSkillTypeIDAndLevelRequired(eachTypeID, skillsForType)
        for skillTypeID, skillLvl in skillsForType:
            for nextLvl in xrange(1, skillLvl + 1):
                skillLvlTuple = (skillTypeID, nextLvl)
                if skillLvlTuple not in allSkillsAndLevels:
                    allSkillsAndLevels.append(skillLvlTuple)

    return allSkillsAndLevels


def _GetSkillTypeIDAndLevelRequired(typeID, ret):
    for skillTypeID, lvl in sm.GetService('skills').GetRequiredSkills(typeID).iteritems():
        if skillTypeID != typeID:
            _GetSkillTypeIDAndLevelRequired(skillTypeID, ret)
        skillLvlTuple = (skillTypeID, int(lvl))
        if skillLvlTuple not in ret:
            ret.append(skillLvlTuple)
