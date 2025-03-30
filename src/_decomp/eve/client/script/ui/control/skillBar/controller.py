#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\skillBar\controller.py
from clonegrade import CLONE_STATE_ALPHA
from skills.client.skillController import SkillController
import signals

class SkillBarController(object):

    def __init__(self, skillController, requiredLevel = None, overrideLevel = None):
        self._skillController = skillController
        self._requiredLevel = requiredLevel
        self._overrideLevel = overrideLevel
        self.onUpdate = signals.Signal(signalName='onUpdate7')

    @property
    def typeID(self):
        return self._skillController.typeID

    @property
    def isRequired(self):
        return self._requiredLevel is not None and self._requiredLevel > 0

    @property
    def requiredLevel(self):
        return self._requiredLevel

    @requiredLevel.setter
    def requiredLevel(self, requiredLevel):
        changed = requiredLevel != self._requiredLevel
        self._requiredLevel = requiredLevel
        if changed:
            self.onUpdate()

    @property
    def level(self):
        return self._skillController.GetMyLevel()

    @property
    def isInjected(self):
        return self._skillController.IsInjected()

    @property
    def isRequirementsMet(self):
        return self._skillController.IsPrereqsMetIncludingSkillQueue()

    @property
    def isTraining(self):
        return self._skillController.IsInTraining()

    @property
    def isQueued(self):
        queue = self._skillController.skill_queue_service.GetQueue()
        return any((self.typeID == s.trainingTypeID for s in queue))

    @property
    def isRestricted(self):
        return sm.GetService('cloneGradeSvc').GetMaxSkillLevel(self.typeID) < 5

    @property
    def isPartiallyTrained(self):
        skillService = self._skillController.skill_service
        currentLevelSP = skillService.SkillPointsCurrentLevel(self.typeID)
        myCurrentSP = skillService.MySkillPoints(self.typeID) or 0
        return myCurrentSP - currentLevelSP > 0

    @property
    def restrictedLevel(self):
        return sm.GetService('cloneGradeSvc').GetMaxSkillLevel(self.typeID, CLONE_STATE_ALPHA)

    @property
    def points(self):
        return self._skillController.skill_service.MySkillPoints(self.typeID)

    def IsLevelQueued(self, level):
        if self._overrideLevel is not None:
            return level <= self._overrideLevel
        queue = self._skillController.skill_queue_service.GetQueue()
        q = filter(lambda s: s.trainingTypeID == self.typeID, queue)
        return any((level == s.trainingToLevel for s in q))

    def IsLevelTraining(self, level):
        if not self.isTraining:
            return False
        queue = self._skillController.skill_queue_service.GetQueue()
        if not queue:
            return False
        isSameType = queue[0].trainingTypeID == self.typeID
        isSameLevel = queue[0].trainingToLevel == level
        return isSameType and isSameLevel

    def IsLevelTrainable(self, level):
        if level <= self.level:
            return False
        elif not self.isInjected:
            return False
        elif not self.isRequirementsMet and self.points == 0:
            return False
        elif self.isRestricted and self.restrictedLevel < level:
            return False
        else:
            return True

    def IsLevelTrainedByExpertSystem(self, level):
        myskills = self._skillController.skill_service.GetSkills()
        if self.typeID in myskills:
            virtualSkillLevel = myskills[self.typeID].virtualSkillLevel
            if virtualSkillLevel is not None and virtualSkillLevel >= level:
                return True
        return False

    def GetMenu(self):
        return self._skillController.GetMenu()

    def GetDragData(self):
        return self._skillController.GetDragData()


def CreateSkillBarController(typeID, requiredLevel = None, overrideLevel = None):
    return SkillBarController(SkillController(typeID), requiredLevel=requiredLevel, overrideLevel=overrideLevel)
