#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\playerOwnedTargetMgr.py
import sys
import uthread
from carbon.common.script.sys.service import Service
from eve.client.script.parklife import states as state
from carbonui.uicore import uicore
from eveexceptions import UserError

class PlayerOwnedTargetMgr(Service):
    __guid__ = 'svc.pwntarget'
    __exportedcalls__ = {'OrderTarget': [],
     'CancelTargetOrder': []}
    __notifyevents__ = ['OnStateChange']
    __dependencies__ = ['michelle', 'godma']

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        self.Reset()

    def Stop(self, stream):
        Service.Stop(self)
        self.Reset()

    def Reset(self):
        self.needtarget = []

    def OnStateChange(self, itemID, flag, true, *args):
        if flag == state.selected and true and self.needtarget:
            clearCursor = False
            for each in self.needtarget:
                if hasattr(each, 'sr') and hasattr(each.sr, 'sourceID'):
                    if not self.IsTargetForStructure(each.sr.sourceID, itemID):
                        uthread.pool('TargetManager::OnStateChange-->LockTarget', self.LockTargetOBO, each.sr.sourceID, itemID, each)
                        clearCursor = True

            if clearCursor:
                self.HideTargetingCursor()
            self.needtarget = []

    def IsTargetForStructure(self, sid, tid):
        targetID = sm.GetService('pwn').GetCurrentTarget(sid)
        if targetID == tid:
            return 1
        return 0

    def OrderTarget(self, who):
        if who not in self.needtarget[:]:
            self.needtarget.append(who)
        self.ShowTargetingCursor()

    def CancelTargetOrder(self, who = None):
        if not who and len(self.needtarget):
            for each in self.needtarget:
                if each and not each.destroyed:
                    each.waitingForActiveTarget = 0

            self.needtarget = []
        elif who in self.needtarget:
            self.needtarget.remove(who)
            who.waitingForActiveTarget = 0
        if not len(self.needtarget):
            self.HideTargetingCursor()

    def ShowTargetingCursor(self):
        uicore.layer.inflight.sr.tcursor.display = True

    def HideTargetingCursor(self):
        uicore.layer.inflight.sr.tcursor.display = False

    def LockTargetOBO(self, sid, tid, who):
        self.StartLockTarget(sid, tid, who)
        try:
            flag, targetList = self.godma.GetDogmaLM().AddTargetOBO(sid, tid)
            if not flag:
                self.OnTargetAdded(sid, tid)
        except UserError as e:
            self.FailLockTarget(tid, who)
            if e.msg == 'DeniedShipChanged':
                sys.exc_clear()
                return
            eve.Message(e.msg, e.dict)
            sys.exc_clear()

        self.LogInfo('PlayerOwned targetMgr: Locking Target for ', tid, ' done')

    def UnLockTargetOBO(self, sid, tid):
        self.godma.GetDogmaLM().RemoveTargetOBO(sid, tid)

    def StartLockTarget(self, sid, tid, who):
        uthread.new(who.CountDown, tid)

    def FailLockTarget(self, tid, who):
        if not who or who.destroyed:
            return
        if not hasattr(who, 'countDown') or not hasattr(who, 'waitingForActiveTarget'):
            return
        who.countDown = False
        who.waitingForActiveTarget = 0

    def OnTargetAdded(self, sid, tid):
        sm.ScatterEvent('OnStructureTargetAdded', sid, tid)

    def OnTargetRemoved(self, sid, tid):
        sm.ScatterEvent('OnStructureTargetAdded', sid, tid)
