#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\reprocessingsvc.py
import carbon.client.script.util.lg as lg
import uthread
from carbon.common.script.sys.service import Service
from carbonui.uicore import uicore
from eve.common.script.net import eveMoniker

class ReprocessingSvc(Service):
    __exportedcalls__ = {'ReprocessDlg': [],
     'GetReprocessingSvc': []}
    __guid__ = 'svc.reprocessing'
    __notifyevents__ = ['ProcessSessionChange', 'DoSessionChanging']
    __servicename__ = 'reprocessing'
    __displayname__ = 'Reprocessing Service'
    __dependencies__ = ['settings']

    def __init__(self):
        Service.__init__(self)
        self.optionsByItemType = {}
        self.crits = {}
        self.oreEfficiency = None
        self.efficiency = None

    def LogInfo(self, *args):
        lg.Info(self.__guid__, *args)

    def Run(self, memStream = None):
        self.LogInfo('Starting Reprocessing Service')
        self.ReleaseReprocessingSvc()

    def Stop(self, memStream = None):
        self.ReleaseReprocessingSvc()

    def __EnterCriticalSection(self, k, v = None):
        if (k, v) not in self.crits:
            self.crits[k, v] = uthread.CriticalSection((k, v))
        self.crits[k, v].acquire()

    def __LeaveCriticalSection(self, k, v = None):
        self.crits[k, v].release()
        if (k, v) in self.crits and self.crits[k, v].IsCool():
            del self.crits[k, v]

    def ProcessSessionChange(self, isremote, session, change):
        if 'charid' in change or 'stationid' in change or 'structureid' in change:
            self.ReleaseReprocessingSvc()

    def DoSessionChanging(self, isRemote, session, change):
        if 'charid' in change or 'stationid' in change or 'structureID' in change:
            sm.StopService(self.__guid__[4:])

    def GetReprocessingSvc(self):
        if hasattr(self, 'moniker') and self.moniker is not None:
            return self.moniker
        self.moniker = eveMoniker.GetReprocessingManager()
        return self.moniker

    def ReleaseReprocessingSvc(self):
        if hasattr(self, 'moniker') and self.moniker is not None:
            self.moniker = None

    def ReprocessDlg(self, items = None):
        uthread.new(self.uthread_ReprocessDlg, items)

    def uthread_ReprocessDlg(self, items):
        self.__EnterCriticalSection('reprocessingDlg')
        try:
            uicore.cmd.GetCommandAndExecute('OpenReprocessingPlant', items)
        finally:
            self.__LeaveCriticalSection('reprocessingDlg')
