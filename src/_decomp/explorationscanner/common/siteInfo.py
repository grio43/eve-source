#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\explorationscanner\common\siteInfo.py


class SiteInfo(object):

    def __init__(self, position, targetID, difficulty, dungeonID, archetypeID):
        self.position = position
        self.targetID = targetID
        self.difficulty = difficulty
        self.dungeonID = dungeonID
        self.archetypeID = archetypeID

    def AsDictionary(self):
        return self.__dict__
