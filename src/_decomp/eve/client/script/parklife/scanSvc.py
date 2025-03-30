#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\scanSvc.py
import functools
import blue
import geo2
import carbonui.const as uiconst
import evetypes
import localization
import probescanning.customFormations as customFormations
import probescanning.probeTracker as probeTracker
import probescanning.resultFilter as resultFilter
import probescanning.scanHandler as scanHandler
import uthread
import utillib
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_ANY, ROLE_GML, ROLE_QA, ROLE_WORLDMOD
from carbon.common.script.util.format import FmtDist
from menu import MenuLabel
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.uicore import uicore
from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow as Scanner
from eve.client.script.ui.shared.maps import mapcommon
from eve.common.script.sys import idCheckers
from eveexceptions import ExceptionEater, UserError
from eveservices.menu import GetMenuService
from probescanning.const import COMBAT_TARGETS
from probescanning.explorationSites import get_exploration_site_name
from probescanning.fiFoDict import FiFoDict
from probescanning.formations import SELF_CENTER_FORMATION
from probescanning.util import IsExplorationSite
RECONNECT_DELAY_MINUTES = 1
MIN_PROBE_RECOVER_DISTANCE = 2000
NAME_BY_SCANGROUPID = {const.probeScanGroupAnomalies: 'UI/Inflight/Scanner/CosmicAnomaly',
 const.probeScanGroupSignatures: 'UI/Inflight/Scanner/CosmicSignature',
 const.probeScanGroupShips: 'UI/Inflight/Scanner/Ship',
 const.probeScanGroupStructures: 'UI/Inflight/Scanner/Structure',
 const.probeScanGroupDrones: 'UI/Inflight/Scanner/Drone',
 const.probeScanGroupCharges: 'UI/Inflight/Scanner/Charge',
 const.probeScanGroupNPCs: 'UI/Inflight/Scanner/NPC',
 const.probeScanGroupFighters: 'UI/Inflight/Scanner/Fighter',
 const.probeScanGroupStarBase: 'UI/Inflight/Scanner/StarBase',
 const.probeScanGroupOrbitals: 'UI/Inflight/Scanner/Orbital',
 const.probeScanGroupDeployable: 'UI/Inflight/Scanner/Deployable',
 const.probeScanGroupSovereignty: 'UI/Inflight/Scanner/Sovereignty',
 const.probeScanGroupAbyssalTraces: 'UI/Inflight/Scanner/AbyssalTrace'}

def UserErrorIfScanning(action, *args, **kwargs):

    @functools.wraps(action)
    def wrapper(*args, **kwargs):
        if sm.StartService('scanSvc').IsScanning():
            raise UserError('ScanInProgressGeneric')
        return action(*args, **kwargs)

    return wrapper


class ScanSvc(Service):
    __guid__ = 'svc.scanSvc'
    __servicename__ = 'svc.scanSvc'
    __displayname__ = 'Scanner Probe Service'
    __notifyevents__ = ['OnSessionChanged',
     'OnSystemScanStarted',
     'OnSystemScanStopped',
     'OnProbeWarpStart',
     'OnProbesIdle',
     'OnProbeStateChanged',
     'OnNewProbe',
     'OnRemoveProbe',
     'OnScannerInfoRemoved',
     'DoSimClockRebase']
    __dependencies__ = ['michelle', 'godma', 'audio']
    __uthreads__ = []
    __exportedcalls__ = {'SetProbeDestination': [ROLE_ANY],
     'SetProbeRangeStep': [ROLE_ANY],
     'GetProbeData': [ROLE_ANY],
     'GetScanResults': [ROLE_ANY],
     'RequestScans': [ROLE_ANY],
     'RecoverProbe': [ROLE_ANY],
     'RecoverProbes': [ROLE_ANY],
     'ReconnectToLostProbes': [ROLE_ANY],
     'DestroyProbe': [ROLE_ANY],
     'GetScanRangeStepsByTypeID': [ROLE_ANY],
     'QAScanSites': [ROLE_QA]}
    __configvalues__ = {'max_scan_systems_stored': 50}

    def __init__(self):
        Service.__init__(self)
        self.lastResults = None
        self.probeLabels = {}
        self.selectedSites = set()
        self.lastReconnection = None
        self.lastRangeStepUsed = 5
        self.remoteObject = None
        self.probeTracker = None
        self.resultFilter = None
        self.scanHandlerBySystem = None

    def Run(self, memStream = None):
        self.probeTracker = probeTracker.ProbeTracker(self, sm.ScatterEvent)
        self.resultFilter = resultFilter.ResultFilter()
        self.scanHandlerBySystem = FiFoDict(max_size=self.max_scan_systems_stored, default_factory=scanHandler.ScanHandler, factory_params=(self, self.resultFilter))

    def GetScanMan(self):
        if self.remoteObject is None:
            self.remoteObject = sm.RemoteSvc('scanMgr').GetSystemScanMgr()
        return self.remoteObject

    def OnNewProbe(self, probe):
        self.probeTracker.AddProbe(probe)

    def OnRemoveProbe(self, probeID):
        self.probeTracker.RemoveProbe(probeID)

    def DoSimClockRebase(self, times):
        if not self.lastReconnection:
            return
        oldSimTime, newSimTime = times
        self.lastReconnection += newSimTime - oldSimTime

    def GetActiveProbes(self):
        return self.probeTracker.GetActiveProbes()

    def HasAvailableProbes(self):
        return self.probeTracker.HasAvailableProbes()

    def GetProbeState(self, probeID):
        return self.probeTracker.GetProbeState(probeID)

    def IsProbeActive(self, probeID):
        return self.probeTracker.IsProbeActive(probeID)

    def GetProbeData(self):
        return self.probeTracker.GetProbeData()

    def GetScaledProbes(self, point, probeIDs):
        return self.probeTracker.GetScaledProbes(point, probeIDs, mapcommon.SYSTEMMAP_SCALE)

    def OnSessionChanged(self, isRemote, sess, change):
        if 'charid' in change and change['charid'][1] is not None:
            self.probeTracker.Refresh()
            self.scanHandlerBySystem.clear()
        if 'solarsystemid' in change or 'shipid' in change or 'structureid' in change:
            if self.IsScanning():
                self.OnSystemScanStopped(self.GetScanningProbes(), None, None)
            self.FlushScannerState(reinjectSites='solarsystemid' not in change)
            if sess.charid is None and 'charid' in change:
                self.scanHandlerBySystem.clear()
            if sess.solarsystemid:
                self.ClearCombatTargets()

    def ClearCombatTargets(self):
        self.scanHandlerBySystem[session.solarsystemid].ClearCombatTargets()

    def SetProbeDestination(self, probeID, location):
        self.probeTracker.SetProbeDestination(probeID, location)

    def SetProbeRangeStep(self, probeID, rangeStep):
        self.probeTracker.SetProbeRangeStep(probeID, rangeStep)

    def SetProbeActiveState(self, probeID, state):
        self.probeTracker.SetProbeActiveState(probeID, state)

    @UserErrorIfScanning
    def RequestScans_Check(self):
        if idCheckers.IsAbyssalSpaceSystem(session.solarsystemid2):
            key = 'ProbeScannerAbyssalSpaceWarning'
            response = eve.Message(key, buttons=uiconst.YESNO, suppress=uiconst.ID_YES)
            if response == uiconst.ID_NO:
                return
        elif idCheckers.IsVoidSpaceSystem(session.solarsystemid2):
            raise UserError('ProbeScannerVoidSpaceHint')
        self.RequestScans()

    def RequestScans(self):
        probes = self.probeTracker.GetProbesForScanning()
        self.GetScanMan().RequestScans(probes)
        probeIDs = probes.keys() if probes is not None else [session.shipid]
        self.scanHandlerBySystem[session.solarsystemid].SetProbesAsScanning(probeIDs)
        self.probeTracker.SetProbesAsMoving(probes)

    def OnProbeStateChanged(self, probeID, probeState):
        self.probeTracker.OnProbeStateChanged(probeID, probeState)

    def GetScanningProbes(self):
        return self.scanHandlerBySystem[session.solarsystemid].GetScanningProbes()

    def GetScanResults(self):
        return self.scanHandlerBySystem[session.solarsystemid].GetScanResults()

    def GetCurrentScan(self):
        return self.scanHandlerBySystem[session.solarsystemid].GetCurrentScan()

    def GetIgnoredResults(self):
        return self.scanHandlerBySystem[session.solarsystemid].GetIgnoredResults()

    def GetIgnoredResultsDesc(self):
        resultIDs = self.GetIgnoredResults()
        descList = []
        for id in resultIDs:
            result = self.scanHandlerBySystem[session.solarsystemid].resultsHistory.GetResult(id)
            if result.id:
                descList.append((id, self.GetDisplayName(result)))

        return descList

    def OnProbeWarpStart(self, probeID, fromPos, toPos, startTime, duration):
        self.LogInfo('OnProbeWarpStart', probeID)

    def OnProbesIdle(self, probes):
        self.probeTracker.OnProbesIdle(probes)

    def UpdateProbeState(self, probeID, state, caller = None, notify = True):
        self.probeTracker.UpdateProbeState(probeID, state, caller=None, notify=True)

    def UpdateProbePosition(self, probeID, position):
        self.probeTracker.UpdateProbePosition(probeID, position)

    def OnSystemScanStarted(self, startTime, durationMs, probes):
        self.scanHandlerBySystem[session.solarsystemid].OnSystemScanStarted(startTime, durationMs, probes)
        sm.ScatterEvent('OnSystemScanBegun')
        PlaySound('msg_newscan_probe_analyze_play')

    def OnSystemScanStopped(self, probes, results, absentTargets):
        PlaySound('msg_newscan_probe_analyze_play')
        PlaySound('msg_newscan_probe_analyze_stop')
        if not results:
            uicore.Message('ScnNoResults')
        self.scanHandlerBySystem[session.solarsystemid].OnSystemScanStopped(probes, results, absentTargets)
        sm.ScatterEvent('OnSystemScanDone')

    def GetScanRangeStepsByTypeID(self, typeID):
        return self.probeTracker.GetScanRangeStepsByTypeID(typeID)

    def DestroyProbe(self, probeID):
        self.probeTracker.DestroyProbe(probeID, self.GetScanMan().DestroyProbe)

    def ReconnectToLostProbes(self):
        if not session.solarsystemid2:
            return
        ship = sm.StartService('michelle').GetItem(eve.session.shipid)
        if ship and ship.groupID == const.groupCapsule:
            raise UserError('ScnProbeRecoverToPod')
        if self.CanClaimProbes():
            self.lastReconnection = blue.os.GetSimTime()
            try:
                self.lastReconnection = blue.os.GetSimTime()
                self.GetScanMan().ReconnectToLostProbes()
            finally:
                uthread.new(self.Thread_ShowReconnectToProbesAvailable, self.lastReconnection)

        else:
            seconds = RECONNECT_DELAY_MINUTES * const.MIN - (blue.os.GetSimTime() - self.lastReconnection)
            raise UserError('ScannerProbeReconnectWait', {'when': seconds})

    def Thread_ShowReconnectToProbesAvailable(self, lastReconnection):
        snooze = (RECONNECT_DELAY_MINUTES * const.MIN - (blue.os.GetSimTime() - self.lastReconnection)) / const.MSEC
        while snooze > 0:
            blue.pyos.synchro.SleepSim(snooze)
            if self.lastReconnection is None:
                break
            snooze = (RECONNECT_DELAY_MINUTES * const.MIN - (blue.os.GetSimTime() - self.lastReconnection)) / const.MSEC

        sm.ScatterEvent('OnReconnectToProbesAvailable')

    def CanClaimProbes(self):
        if self.HasOnlineProbeLauncher() and (self.lastReconnection is None or blue.os.GetSimTime() - self.lastReconnection > RECONNECT_DELAY_MINUTES * const.MIN):
            return True
        return False

    def HasOnlineProbeLauncher(self):
        shipItem = sm.GetService('godma').GetStateManager().GetItem(session.shipid)
        if shipItem is not None:
            for module in shipItem.modules:
                if module.groupID == const.groupScanProbeLauncher and module.isOnline:
                    return True

        return False

    def GetProbeLabel(self, probeID):
        if probeID in self.probeLabels:
            return self.probeLabels[probeID]
        newlabel = localization.GetByLabel('UI/Inflight/Scanner/ProbeLabel', probeIndex=len(self.probeLabels) + 1)
        self.probeLabels[probeID] = newlabel
        return newlabel

    def RecoverProbe(self, probeID):
        self.RecoverProbes([probeID])

    def RecoverProbes(self, probeIDs):
        ship = sm.StartService('michelle').GetItem(eve.session.shipid)
        if ship and ship.groupID == const.groupCapsule:
            raise UserError('ScnProbeRecoverToPod')
        ballpark = sm.GetService('michelle').GetBallpark()
        for id in probeIDs:
            try:
                if ballpark.GetBall(id).surfaceDist < MIN_PROBE_RECOVER_DISTANCE:
                    raise UserError('ProbesTooCloseToRecover')
            except AttributeError:
                continue

        PlaySound('msg_newscan_probe_recover_play')
        self.probeTracker.RecoverProbes(probeIDs, self.AskServerToRecallProbes)

    def AskServerToRecallProbes(self, probeIDs):
        return self.GetScanMan().RecoverProbes(probeIDs)

    def OnScannerInfoRemoved(self):
        self.LogInfo('OnScannerInfoRemoved received: flushing scanner state')
        self.FlushScannerState(clearResults=True)

    def QAOverrideProbeExpiry(self, duration):
        self.GetScanMan().QAOverrideProbeExpiry(duration)
        for probe in self.probeTracker.GetProbeData().values():
            probe.expiry = blue.os.GetSimTime() + long(10000 * duration)

    def FlushScannerState(self, reinjectSites = True, clearResults = False):
        self.LogInfo('FlushScannerState: resetting state and scattering OnScannerDisconnected')
        if clearResults:
            del self.scanHandlerBySystem[session.solarsystemid2]
        self.probeTracker.Refresh()
        if reinjectSites:
            with ExceptionEater('Failure Reinjecting Anomalies'):
                self.InjectSitesAsScanResults(sm.GetService('sensorSuite').probeScannerController.GetAllSites())
        self.remoteObject = None
        PlaySound('msg_newscan_probe_analyze_stop')
        sm.ScatterEvent('OnScannerDisconnected')

    def PruneSites(self):
        sites = [ site['id'] for site in sm.GetService('sensorSuite').probeScannerController.GetAllSites() ]
        sitesToPrune = []
        for site in self.GetResults(applyFiltering=False)[0]:
            if site['id'] not in sites and site['scanGroupID'] not in COMBAT_TARGETS:
                sitesToPrune.append(site['id'])

        self.ClearResults(*sitesToPrune)

    def IsScanning(self):
        return self.scanHandlerBySystem[session.solarsystemid].IsScanning()

    def GetProbeMenu(self, probeID, probeIDs = None, *args):
        menu = []
        if probeID == eve.session.shipid:
            return menu
        bp = sm.StartService('michelle').GetBallpark(doWait=True)
        if bp is None:
            return menu
        probeIDs = probeIDs or [probeID]
        if probeID not in probeIDs:
            probeIDs.append(probeID)
        if eve.session.role & (ROLE_GML | ROLE_WORLDMOD):
            menu.append(('CopyID', self._GMCopyID, (probeID,)))
            menu.append(None)
        probes = self.GetProbeData()
        if probeID in probes:
            probe = probes[probeID]
            scanRanges = self.GetScanRangeStepsByTypeID(probe.typeID)
            menu.append((MenuLabel('UI/Inflight/Scanner/ScanRange'), [ (FmtDist(range), self.SetScanRange_Check, (probeID,
               probeIDs,
               range,
               index + 1)) for index, range in enumerate(scanRanges) ]))
        menu.append((MenuLabel('UI/Inflight/Scanner/RecoverProbe'), self.RecoverProbe_Check, (probeID, probeIDs)))
        return menu

    def _GMCopyID(self, id):
        blue.pyos.SetClipboardData(str(id))

    @UserErrorIfScanning
    def SetScanRange_Check(self, probeID, probeIDs, range, rangeStep):
        for _probeID in probeIDs:
            self.SetProbeRangeStep(_probeID, rangeStep)

    @UserErrorIfScanning
    def RecoverProbe_Check(self, probeID, probeIDs):
        for _probeID in probeIDs:
            self.RecoverProbe(_probeID)

    @UserErrorIfScanning
    def SetProbeActiveStateOn_Check(self, probeID, probeIDs):
        for _probeID in probeIDs:
            self.GetScanMan().SetActivityState(probeIDs, True)
            self.SetProbeActiveState(_probeID, True)

    @UserErrorIfScanning
    def SetProbeActiveStateOff_Check(self, probeID, probeIDs):
        for _probeID in probeIDs:
            self.GetScanMan().SetActivityState(probeIDs, False)
            self.SetProbeActiveState(_probeID, False)

    @UserErrorIfScanning
    def DestroyProbe_Check(self, probeID, probeIDs):
        if probeIDs and eve.Message('DestroySelectedProbes', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            for _probeID in probeIDs:
                self.DestroyProbe(_probeID)

    def IgnoreResult(self, *targets):
        self.scanHandlerBySystem[session.solarsystemid2].IgnoreResult(*targets)

    def ClearIgnoredResults(self):
        self.scanHandlerBySystem[session.solarsystemid2].ClearIgnoredResults()

    def ClearResults(self, *targets):
        self.scanHandlerBySystem[session.solarsystemid2].ClearResults(*targets)

    def AlignToPosition(self, position):
        ballpark = self.michelle.GetBallpark()
        myBall = self.michelle.GetBall(ballpark.ego)
        myPosition = (myBall.x, myBall.y, myBall.z)
        directionalVector = geo2.Vec3SubtractD(position, myPosition)
        rbp = self.michelle.GetRemotePark()
        rbp.CmdGotoDirection(directionalVector[0], directionalVector[1], directionalVector[2])

    def IgnoreOtherResults(self, *targets):
        self.scanHandlerBySystem[session.solarsystemid].IgnoreOtherResults(*targets)

    def ShowIgnoredResult(self, targetID):
        self.scanHandlerBySystem[session.solarsystemid].ShowIgnoredResult(targetID)

    def GetProbeLauncher(self):
        ship = self.godma.GetItem(session.shipid)
        if ship:
            for module in ship.modules:
                if not module.isOnline:
                    continue
                if module.groupID == const.groupScanProbeLauncher:
                    return module

    def FindModuleAndLaunchProbes(self, numProbes):
        ship = self.godma.GetItem(session.shipid)
        module = self.GetProbeLauncher()
        if ship and module and any((s.locationID == session.shipid and s.flagID == module.flagID for s in ship.sublocations)):
            for effect in module.effects.itervalues():
                if effect.isDefault:
                    dogmaLM = self.godma.GetStateManager().GetDogmaLM()
                    dogmaLM.LaunchProbes(module.itemID, numProbes)
                    PlaySound('msg_newscan_probe_launch_play')
                    return

    def GetNumChargesInProbeLauncher(self):
        charge = self.GetChargesInProbeLauncher()
        if charge is None:
            return 0
        return charge.quantity

    def GetChargesInProbeLauncher(self):
        launcher = self.GetProbeLauncher()
        if launcher is None:
            return
        flagID = launcher.flagID
        return self.godma.GetStateManager().GetSubLocation(session.shipid, flagID)

    def CanLaunchFormation(self, formationID):
        if formationID == SELF_CENTER_FORMATION:
            return bool(self.GetActiveProbes())
        charges = self.GetNumChargesInProbeLauncher()
        return self.probeTracker.CanCreateFormation(formationID, charges)

    def MoveProbesToFormation(self, formationID, initialPosition = None):
        self.probeTracker.MoveProbesToFormation(formationID, self.FindModuleAndLaunchProbes, self.GetNumChargesInProbeLauncher(), initialPosition=initialPosition)

    def ScaleFormationSpread(self, scaling):
        self.probeTracker.ScaleAllProbes(scaling, scaleScanRange=False)

    def ScaleFormation(self, scaling):
        probeData = self.probeTracker.GetProbeData()
        for probeID, probe in probeData.iteritems():
            currentRange = probe.scanRange
            newRange = currentRange * scaling
            rangeSteps = self.probeTracker.GetScanRangeStepsByTypeID(probe.typeID)
            if newRange not in rangeSteps:
                return

        self.probeTracker.ScaleAllProbes(scaling)

    def GetProbeTracker(self):
        return self.probeTracker

    def SetProbesAsScanning(self, probes):
        return self.probeTracker.SetProbesAsScanning(probes)

    def ProbeControlSelect(self):
        uicore.layer.systemmapBrackets.state = uiconst.UI_DISABLED

    def ProbeControlDeselected(self):
        uicore.layer.systemmapBrackets.state = uiconst.UI_PICKCHILDREN

    def FocusOnProbe(self, probeID):
        try:
            probeID = int(probeID)
        except ValueError:
            uicore.layer.systemmap.FocusOnPoint(self.probeTracker.GetCenterOfActiveProbes())
        else:
            uicore.layer.systemmap.FocusOnPoint(self.probeTracker.GetProbe(probeID).destination)

    def GetFilterOptions(self):
        return self.resultFilter.GetFilters()

    def GetActiveFilterSet(self):
        return self.resultFilter.GetActiveFilterSet()

    def AddToActiveFilterSet(self, filterID):
        self.resultFilter.AddToActiveFilterSet(filterID)
        sm.ScatterEvent('OnSystemScanFilterChanged')

    def RemoveFromActiveFilterSet(self, filterID):
        self.resultFilter.RemoveFromActiveFilterSet(filterID)
        sm.ScatterEvent('OnSystemScanFilterChanged')

    def DeleteFilter(self, filterID):
        self.resultFilter.DeleteFilter(filterID)

    def GetResults(self, applyFiltering = True):
        results, ignored, filtered, anomalies = self.scanHandlerBySystem[session.solarsystemid].GetResults(applyFiltering)
        results = [ utillib.KeyVal(**r) for r in results ]
        return (results,
         ignored,
         filtered,
         anomalies)

    def GetResultFilter(self, filterID):
        return self.resultFilter.GetFilter(filterID)

    def CreateResultFilter(self, name, groups):
        self.resultFilter.CreateFilter(name, groups)

    def EditResultFilter(self, filterID, name, groups):
        self.resultFilter.EditFilter(filterID, name, groups)

    def GetDisplayName(self, result):
        displayName = ''
        if result.typeID:
            displayName = self.GetTypeName(result)
        if not displayName and result.groupID:
            displayName = self.GetGroupName(result)
        if not displayName:
            displayName = self.GetScanGroupName(result)
        return displayName

    def GetTypeName(self, result):
        if IsExplorationSite(result):
            if result.dungeonNameID is not None:
                return localization.GetByMessageID(result.dungeonNameID)
            return ''
        if result.typeID is not None:
            return evetypes.GetName(result.typeID)
        return ''

    def GetGroupName(self, result):
        if IsExplorationSite(result):
            if result.strengthAttributeID is None:
                return ''
            return self.GetExplorationSiteType(result.strengthAttributeID, result.archetypeID)
        elif result.groupID is not None:
            return evetypes.GetGroupNameByGroup(result.groupID)
        else:
            return ''

    def GetExplorationSiteType(self, attributeID, archetypeID):
        return get_exploration_site_name(site_type=attributeID, archetype_id=archetypeID)

    def GetScanGroupName(self, result):
        return localization.GetByLabel(NAME_BY_SCANGROUPID[result.scanGroupID])

    def RestoreProbesFromBackup(self):
        self.probeTracker.RestoreProbesFromBackup()

    def CenterProbesOnMe(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        egoBall = ballpark.GetBall(ballpark.ego)
        if not egoBall:
            return
        oldFormation = customFormations.GetSelectedFormationID()
        probeInfo = self.probeTracker.GetProbePositionAndRangeInfo()
        formationID = customFormations.PersistFormation('tempFormation', probeInfo.values())
        self.MoveProbesToFormation(formationID, initialPosition=(egoBall.x, egoBall.y, egoBall.z))
        customFormations.DeleteFormation(formationID)
        customFormations.SelectFormation(oldFormation)

    def StartMoveMode(self):
        self.probeTracker.StartMoveMode()

    def PurgeBackupData(self):
        self.probeTracker.PurgeBackupData()

    def GetResultForTargetID(self, targetID):
        return self.scanHandlerBySystem[session.solarsystemid].resultsHistory.GetResultAsDict(targetID)

    def GetIgnoreResultMenu(self, targetID, scanGroupID = None):
        menu = []
        menu.append(None)
        menu.append((MenuLabel('UI/Inflight/Scanner/IngoreResult'), self.IgnoreResult, (targetID,)))
        menu.append((MenuLabel('UI/Inflight/Scanner/IgnoreOtherResults'), self.IgnoreOtherResults, (targetID,)))
        return menu

    def GetAccurateScannedDownMenu(self, scanResult):
        menu = []
        if scanResult.IsAccurate():
            menu.extend(self.GetScannedDownMenu(scanResult))
        return menu

    def GetScanResultMenuWithIgnore(self, scanResult, scanGroupId):
        menu = []
        menu.extend(self.GetAccurateScannedDownMenu(scanResult))
        menu.extend(self.GetIgnoreResultMenu(scanResult.targetID, scanGroupId))
        return menu

    def GetScanResultMenuWithoutIgnore(self, scanResult):
        return self.GetAccurateScannedDownMenu(scanResult)

    def GetScannedDownMenu(self, scanResult):
        menu = []
        if self.michelle.IsPositionWithinWarpDistance(scanResult.position):
            menu.extend(GetMenuService().SolarsystemScanMenu(scanResult.targetID))
            menu.append(None)
        _scanResultNameID, scanResultName = scanResult.GetScanName()
        menu.extend(self.GetAlignToMenu(scanResult.position))
        bookmarkData = utillib.KeyVal(id=scanResult.targetID, position=scanResult.position, name='%s %s' % (scanResult.targetID, scanResultName))
        menu.append((MenuLabel('UI/Inflight/BookmarkLocation'), sm.GetService('addressbook').BookmarkLocationPopup, (session.solarsystemid,
          None,
          None,
          None,
          bookmarkData)))
        return menu

    def GetAlignToMenu(self, position):
        return [(MenuLabel('UI/Inflight/AlignTo'), self.AlignToPosition, (position,))]

    def InjectSitesAsScanResults(self, sites, force = False):
        if session.solarsystemid:
            self.scanHandlerBySystem[session.solarsystemid].InjectResults(sites, force=force)

    def ShowAnomalies(self):
        self.resultFilter.ShowAnomalies()
        sm.ScatterEvent('OnSystemScanFilterChanged')

    def StopShowingAnomalies(self):
        self.resultFilter.StopShowingAnomalies()
        sm.ScatterEvent('OnSystemScanFilterChanged')

    def ClickLink(self, action):
        if action == 'ShowAnomalies':
            self.ShowAnomalies()
        elif action == 'HideAnomalies':
            self.StopShowingAnomalies()
        elif action == 'ClearIgnored':
            self.scanHandlerBySystem[session.solarsystemid].ClearIgnoredResults()
        else:
            raise RuntimeError('scanSvc::ClickLink - Not supported action (%s)' % action)
        wnd = Scanner.GetIfOpen()
        if wnd is not None:
            wnd.LoadFilterOptionsAndResults()

    def IsShowingAnomalies(self):
        return self.resultFilter.IsShowingAnomalies()

    def PersistCurrentFormation(self, name):
        probeInfo = self.probeTracker.GetProbePositionAndRangeInfo()
        customFormations.PersistFormation(name, probeInfo.values())

    def SetSelectedSites(self, siteIDs):
        self.selectedSites.clear()
        for siteID in siteIDs:
            self.selectedSites.add(siteID)

        sm.ScatterEvent('OnSiteSelectionChanged')

    def SelectSite(self, siteID):
        multiSelect = uicore.uilib.Key(uiconst.VK_SHIFT) or uicore.uilib.Key(uiconst.VK_CONTROL)
        if not multiSelect:
            self.selectedSites.clear()
        if siteID not in self.selectedSites:
            self.selectedSites.add(siteID)
        elif multiSelect:
            self.selectedSites.remove(siteID)
        sm.ScatterEvent('OnSiteSelectionChanged')

    def DeselectSite(self, siteID):
        if siteID in self.selectedSites:
            self.selectedSites.remove(siteID)
            sm.ScatterEvent('OnSiteSelectionChanged')

    def IsSiteSelected(self, siteID):
        return siteID in self.selectedSites

    def GetActiveProbeTypeID(self):
        typeID = self.probeTracker.GetProbeTypeID()
        if typeID:
            return typeID
        charges = self.GetChargesInProbeLauncher()
        if charges:
            return charges.typeID

    def QAScanSites(self, *siteIDs):
        sites = self.GetScanMan().QAScanSites(siteIDs)
        if sites:
            self.scanHandlerBySystem[session.solarsystemid].InjectResults(sites, True)
