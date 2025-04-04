#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\development\skillHistoryRow.py
import characterskills as charskills
import evetypes
__author__ = 'aevar'

class SkillHistoryRow(object):

    def __init__(self, row, skillTimeConstant, config, stringDict, defaultString = None):
        self.skillTypeID = row.skillTypeID
        self.absolutePoints = row.absolutePoints
        self.logDate = row.logDate
        self.eventTypeID = row.eventTypeID
        self.actionString = stringDict.get(self.eventTypeID, defaultString)
        self.levels = None
        self.level = -1
        self.initLevels(skillTimeConstant)
        self.skillName = evetypes.GetName(self.skillTypeID)

    def initLevels(self, skillTimeConstant):
        self.skillTimeConstant = skillTimeConstant
        self.levels = charskills.GetSPForAllLevels(skillTimeConstant)
        self._calcCurrentLevel()

    def _calcCurrentLevel(self):
        level = 0
        for i in range(len(self.levels)):
            if self.levels[i] < self.absolutePoints:
                level = i + 1

        self.level = level

    def __str__(self):
        return 'SkillTypeID:' + str(self.skillTypeID) + ' absolutePoints:' + str(self.absolutePoints) + ' logDate:' + str(self.logDate) + ' actionString:' + str(self.actionString) + ' level:' + str(self.level) + ' SkillName:' + str(self.skillName)
