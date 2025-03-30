#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterskills\common\character_skill_entry.py
from characterskills import GetSkillLevelRaw

class CharacterSkillEntry(object):

    def __init__(self, typeID, trainedSkillLevel, skillPoints, skillRank, virtualSkillLevel):
        self._typeID = typeID
        self._trainedSkillLevel = trainedSkillLevel
        self._skillPoints = skillPoints
        self._skillRank = skillRank
        self._virtualSkillLevel = virtualSkillLevel

    def __repr__(self):
        return 'CharacterSkillEntry(typeID=%r, trainedSkillLevel=%r, skillPoints=%r, skillRank=%r, virtualSkillLevel=%r)' % (self._typeID,
         self._trainedSkillLevel,
         self._skillPoints,
         self._skillRank,
         self._virtualSkillLevel)

    @property
    def typeID(self):
        return self._typeID

    @property
    def skillLevel(self):
        raise DeprecationWarning('skillLevel is obsolete - use one of effectiveSkillLevel/trainedSkillLevel/virtualSkillLevel as appropriate')

    @property
    def effectiveSkillLevel(self):
        return max(self._trainedSkillLevel, self._virtualSkillLevel)

    @property
    def trainedSkillLevel(self):
        return self._trainedSkillLevel

    @property
    def virtualSkillLevel(self):
        return self._virtualSkillLevel

    @property
    def skillPoints(self):
        raise DeprecationWarning('skillPoints is obsolete - use trainedSkillPoints')

    @property
    def trainedSkillPoints(self):
        return self._skillPoints

    @property
    def skillRank(self):
        return self._skillRank

    def GetCopyWithNewSkillPoints(self, newSkillPoints):
        if newSkillPoints is None:
            return CharacterSkillEntry(self._typeID, None, None, self._skillRank, self._virtualSkillLevel)
        if newSkillPoints == -1:
            return CharacterSkillEntry(self._typeID, -1, -1, self._skillRank, self._virtualSkillLevel)
        newTrainedSkillLevel = GetSkillLevelRaw(newSkillPoints, self._skillRank)
        return CharacterSkillEntry(self._typeID, newTrainedSkillLevel, newSkillPoints, self._skillRank, self._virtualSkillLevel)

    def GetCopyWithModifiedVirtualLevel(self, newVirtualSkillLevel):
        return CharacterSkillEntry(self._typeID, self._trainedSkillLevel, self._skillPoints, self._skillRank, newVirtualSkillLevel)
