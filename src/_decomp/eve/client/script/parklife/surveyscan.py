#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\surveyscan.py
import sys
import blue
import telemetry
import uthread
from carbon.common.script.sys.service import Service
from eve.client.script.ui.inflight.surveyscan import SurveyScanView

class SurveyScanSvc(Service):
    __guid__ = 'svc.surveyScan'
    __exportedcalls__ = {'Clear': []}
    __notifyevents__ = ['OnSurveyScanComplete', 'DoBallRemove', 'DoBallsRemove']

    def Run(self, memStream = None):
        super(SurveyScanSvc, self).Run(memStream)
        self.scans = {}
        self.isSettingEntries = False

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball.id in self.scans:
            del self.scans[ball.id]
            if not self.isSettingEntries:
                self.isSettingEntries = True
                uthread.pool('SurveyScanSvc::SetEntriesDelayed', self.SetEntriesDelayed)

    def SetEntriesDelayed(self):
        blue.pyos.synchro.SleepSim(2000)
        wnd = SurveyScanView.GetIfOpen()
        if wnd:
            wnd.SetEntries(self.scans)
        self.isSettingEntries = False

    def OnSurveyScanComplete(self, l):
        try:
            for ballID, typeID, quantity in l:
                self.scans[ballID] = (typeID, quantity)

            wnd = SurveyScanView.Open()
            if wnd:
                wnd.SetEntries(self.scans)
        except:
            import traceback
            traceback.print_exc()
            sys.exc_clear()

    def GetWnd(self, create = 0):
        if create:
            return SurveyScanView.Open()
        return SurveyScanView.GetIfOpen()

    def Clear(self):
        self.scans = {}
        SurveyScanView.CloseIfOpen()
