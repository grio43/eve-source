#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveSpaceObject\targetingComponent.py
import tacticalNavigation.ballparkFunctions as ballparkFunctions

class TargetingSystemComponent:

    def __init__(self):
        self._behaviors = {}

    def AddTargetingBehavior(self, key, subsystem):
        if key in self._behaviors:
            pass
        self._behaviors[key] = subsystem

    def RemoveSystem(self, key):
        if key in self._behaviors:
            del self._behaviors[key]

    def GetTarget(self, targetID):
        for key in self._behaviors:
            target = self._behaviors[key].GetTarget(targetID)
            if target is not None:
                return target

        return ballparkFunctions.GetBall(targetID)
