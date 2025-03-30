#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\squadrons\squadronManagementController.py


class SquadronMgmtController(object):

    def __init__(self):
        self.fighterSvc = sm.GetService('fighters')

    def LoadFightersToTube(self, fighterID, tubeFlagID):
        self.fighterSvc.LoadFightersToTube(fighterID, tubeFlagID)

    def UnloadTubeToFighterBay(self, tubeFlagID):
        self.fighterSvc.UnloadTubeToFighterBay(tubeFlagID)

    def LaunchFightersFromTube(self, tubeFlagID):
        self.fighterSvc.LaunchFightersFromTubes([tubeFlagID])

    def RecallFighterToTube(self, fighterID):
        self.fighterSvc.RecallFightersToTubes([fighterID])
