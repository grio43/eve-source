#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\ownerprimer.py
import uthread
from carbon.common.script.sys.service import Service

class OwnerPrimer(Service):
    __guid__ = 'svc.ownerprimer'
    __notifyevents__ = ['DoBallsAdded']

    def Run(self, *etc):
        Service.Run(self, *etc)
        sm.FavourMe(self.DoBallsAdded)
        self.waitingowners = {}

    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::ownerprimer')
        try:
            return self.DoBallsAdded_(*args, **kw)
        finally:
            t.PopTimer(timer)

    def DoBallsAdded_(self, entries):
        if len(entries) < 2:
            return
        uthread.new(self.DoBallsAdded_thread, entries).context = 'ownerprimer::DoBallsAdded'

    def DoBallsAdded_thread(self, entries):
        tmp = {}
        for ball, slimItem in entries:
            if slimItem is not None and slimItem.ownerID is not None:
                tmp[slimItem.ownerID] = None

        cfg.eveowners.Prime(tmp.keys())
