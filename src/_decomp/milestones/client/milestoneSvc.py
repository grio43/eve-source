#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\milestones\client\milestoneSvc.py
from carbon.common.script.sys.service import Service

class MilestoneService(Service):
    __guid__ = 'svc.milestoneSvc'
    __displayname__ = 'Milestone Client Service'
    __notifyevents__ = ['OnCharacterSessionChanged', 'OnMilestoneTimerStarted']

    def __init__(self):
        super(MilestoneService, self).__init__()
        self.timeLeft = None

    def OnCharacterSessionChanged(self, oldCharacterID, newCharacterID):
        self.timeLeft = None
        sm.RemoteSvc('milestoneMgr').ProcessCharacterLogon()

    def OnMilestoneTimerStarted(self, timeLeft):
        self.timeLeft = timeLeft

    def GetTimeLeftInMilestone(self):
        return self.timeLeft

    def ClaimRewards(self, milestoneID):
        self.timeLeft = None
        sm.RemoteSvc('milestoneMgr').ClaimRewards(milestoneID)
