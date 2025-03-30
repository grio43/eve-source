#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\moonscan.py
from ballparkCommon.intersection import GetClosestIntersectionForRay
from carbon.common.script.sys.service import Service
from eve.client.script.ui.inflight.scannerFiles.moonScanner import MoonScanner
from eveexceptions import UserError
from inventorycommon.const import groupMoon, groupSurveyProbeLauncher
from localization import GetByLabel
from signals import Signal

class MoonScanSvc(Service):
    __guid__ = 'svc.moonScan'
    __update_on_reload__ = 1
    __notifyevents__ = ['OnScanNoMaterials',
     'OnMoonScanComplete',
     'OnNewMoonProbe',
     'OnRemoveMoonProbe',
     'OnBallAdded',
     'OnSessionChanged']

    def Run(self, *etc):
        Service.Run(self, *etc)
        self.scans = {}
        self.moonProbeTracker = MoonProbeTracker()

    def OnScanNoMaterials(self, moonID):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        slimItem = bp.GetInvItem(moonID)
        if slimItem is None:
            return
        if slimItem.groupID != groupMoon:
            text = GetByLabel('UI/Inflight/Scanner/SurveyProbeHitNonMoon', itemName=slimItem.name)
            raise UserError('CustomNotify', {'notify': text})
        self._UpdateScanMoonDict(moonID, {})

    def OnMoonScanComplete(self, moonID, results):
        self._UpdateScanMoonDict(moonID, results)

    def _UpdateScanMoonDict(self, moonID, results):
        self.scans[moonID] = results
        self.OpenAndLoadScanningWnd(moonID=moonID)

    def GetWndIfOpen(self):
        return MoonScanner.GetIfOpen()

    def GetScans(self):
        return self.scans

    def GetProbeData(self):
        return self.moonProbeTracker.GetProbeData()

    def OpenAndLoadScanningWnd(self, moonID = None):
        wnd = self.GetWndIfOpen()
        if wnd:
            wnd.Maximize()
            wnd.LoadWnd(moonID=moonID)
        else:
            MoonScanner.Open(moonID=moonID)

    def Clear(self):
        self.scans = {}
        wnd = self.GetWndIfOpen()
        if wnd:
            wnd.ClearMoons()

    def ClearEntry(self, celestialID):
        if celestialID in self.scans:
            del self.scans[celestialID]
        self.OpenAndLoadScanningWnd()

    def OnNewMoonProbe(self, probe):
        self.moonProbeTracker.AddProbe(probe)
        self.OpenAndLoadScanningWnd()

    def OnRemoveMoonProbe(self, probeID):
        self.moonProbeTracker.RemoveProbe(probeID)

    def GetActiveProbeTypeID(self):
        typeID = self.moonProbeTracker.GetProbeTypeID()
        if typeID:
            return typeID
        charges = self.GetChargesInProbeLauncher()
        if charges:
            return charges.typeID

    def GetOnlineProbeLauncher(self):
        launchers = self.GetOnlineProbeLaunchers()
        if launchers:
            return launchers[0]
        else:
            return None

    def GetOnlineProbeLaunchers(self):
        launchers = []
        ship = sm.GetService('godma').GetItem(session.shipid)
        if ship:
            for module in ship.modules:
                if module.isOnline and module.groupID == groupSurveyProbeLauncher:
                    launchers.append(module)

        return launchers

    def HasOnlineProbeLauncher(self):
        return bool(self.GetOnlineProbeLauncher())

    def GetChargesInProbeLauncher(self):
        launcher = self.GetOnlineProbeLauncher()
        if launcher is None:
            return
        flagID = launcher.flagID
        return sm.GetService('godma').GetStateManager().GetSubLocation(session.shipid, flagID)

    def OnBallAdded(self, slimItem):
        probe = self.moonProbeTracker.GetProbeData().get(slimItem.itemID, None)
        if not probe:
            return
        self.FindMoonForProbe(probe)

    def OnSessionChanged(self, isremote, sess, change):
        if 'solarsystemid' in change or 'structureid' in change:
            self.moonProbeTracker.RemoveAllProbes()

    def FindMoonForProbe(self, probe):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        probeBall = bp.GetBall(probe.probeID)
        if not probeBall:
            return
        origin = probe.pos
        direction = (probeBall.vx, probeBall.vy, probeBall.vz)
        celestialID, intersection = GetClosestIntersectionForRay(bp, origin, direction, probe.maxScanRange)
        celestialSlimItem = bp.slimItems.get(celestialID, None)
        if celestialSlimItem and celestialSlimItem.groupID == groupMoon:
            toRegister = celestialID
        else:
            toRegister = None
        self.moonProbeTracker.RegisterMoonToProbe(probe.probeID, toRegister)

    def GetMoonForProbe(self, probeID):
        return self.moonProbeTracker.GetMoonForProbe(probeID)


class MoonProbeTracker(object):

    def __init__(self):
        self.counter = 1
        self.probeData = {}
        self.moonsByProbIDs = {}
        self.on_probes_changed = Signal(signalName='on_probes_changed')

    def AddProbe(self, probe):
        self.probeData[probe.probeID] = probe
        probe.probeNumber = self.counter
        self.counter += 1
        self.on_probes_changed()

    def RemoveProbe(self, probeID):
        if probeID in self.probeData:
            del self.probeData[probeID]
        self.moonsByProbIDs.pop(probeID, None)
        self.on_probes_changed()

    def RemoveAllProbes(self):
        self.probeData.clear()
        self.moonsByProbIDs.clear()
        self.on_probes_changed()

    def GetProbeData(self):
        return self.probeData

    def GetProbeTypeID(self):
        if self.probeData:
            return self.probeData.values()[0].typeID

    def RegisterMoonToProbe(self, probeID, moonID):
        self.moonsByProbIDs[probeID] = moonID

    def GetMoonForProbe(self, probeID):
        return self.moonsByProbIDs.get(probeID, -1)

    def GetNumProbes(self):
        return len(self.probeData)
