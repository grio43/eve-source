#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dotWeapons\common\dotApplicationStore.py
from dotWeapons.common.dotAppsOnTarget import DotAppsOnTarget

class DotApplicationStore(object):

    def __init__(self, dogmaLM):
        self.dogmaLM = dogmaLM
        self._dotAppsByTargetID = {}

    def Insert(self, targetItemID, dotApplication):
        dotAppsOnTarget = self.GetDotAppsOnTarget(targetItemID)
        if not dotAppsOnTarget:
            dotAppsOnTarget = DotAppsOnTarget(targetItemID, self.dogmaLM)
            self._dotAppsByTargetID[targetItemID] = dotAppsOnTarget
        dotAppsOnTarget.AddDotApplication(dotApplication)

    def GetDotAppsOnTarget(self, targetItemID):
        dotApplications = self._dotAppsByTargetID.get(targetItemID, None)
        return dotApplications

    def IterateApplicationByTargetID(self):
        for targetID, dotApplicationsForTarget in self._dotAppsByTargetID.iteritems():
            yield (targetID, dotApplicationsForTarget)

    def IsTargetRecored(self, targetID):
        return targetID in self._dotAppsByTargetID

    def DoesTargetHaveValidApplication(self, targetID):
        dotAppsOnTarget = self.GetDotAppsOnTarget(targetID)
        if not dotAppsOnTarget:
            return False
        return dotAppsOnTarget.HasValidApplications()

    def DeleteAllForTarget(self, targetItemID):
        return self._dotAppsByTargetID.pop(targetItemID, None)

    def GetDotApplicationsForAllTargets(self):
        return self._dotAppsByTargetID.values()
