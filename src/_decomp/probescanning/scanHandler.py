#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\scanHandler.py
import logging
from collections import namedtuple
from carbon.client.script.environment.AudioUtil import PlaySound, SetSoundParameter
from probescanning.const import probeResultPerfect, probeStateIdle, probeScanGroupAnomalies, COMBAT_TARGETS
from results import ResultsHistory
CurrentScan = namedtuple('CurrentScan', ['startTime', 'duration', 'probeIDs'])

class ScanHandler(object):

    def __init__(self, scanSvc, resultFilter):
        self.logger = logging.getLogger('probescanning-scanHandler')
        self.currentScan = None
        self.resultsIgnored = set()
        self.resultsHistory = ResultsHistory()
        self.resultFilter = resultFilter
        self.scanningProbes = None
        self.scanSvc = scanSvc
        self.ScatterEvent = sm.ScatterEvent

    def OnSystemScanStarted(self, startTime, durationMs, probes):
        self.logger.debug('OnSystemScanStarted. startTime = %s, durationMs = %s', startTime, durationMs)
        self.currentScan = CurrentScan(startTime=startTime, duration=durationMs, probeIDs=self.scanSvc.SetProbesAsScanning(probes))

    def PlayResultSound(self, results):
        if results:
            certainty = max((result.certainty for result in results))
        else:
            certainty = 0.0
        SetSoundParameter('msg_newscan_probe_scan_results_rtpc', certainty)
        PlaySound('msg_newscan_probe_scan_results_play')

    def HasPerfectResults(self, results):
        return results and any((result.certainty >= probeResultPerfect for result in results))

    def OnSystemScanStopped(self, probes, results, absentTargets):
        self.logger.debug('OnSystemScanStopped probes = %s, results = %s', probes, results)
        for pID in probes:
            self.scanSvc.UpdateProbeState(pID, probeStateIdle, 'OnSystemScanStopped', notify=False)

        self.StopScanning()
        self.resultsHistory.RegisterResults(results)
        self.PlayResultSound(results)
        if self.HasPerfectResults(results):
            self.ScatterEvent('OnClientEvent_PerfectScanResultReached', results)
        if absentTargets:
            self.ClearResults(*absentTargets)

    def InjectResults(self, results, force = False):
        self.resultsHistory.RegisterResults(results, incrementScanNumber=False, force=force)
        self.ScatterEvent('OnRefreshScanResults')

    def GetCurrentScan(self):
        return self.currentScan

    def ClearResults(self, *targets):
        for targetID in targets:
            if targetID in self.resultsIgnored:
                self.resultsIgnored.remove(targetID)

        self.resultsHistory.ClearResults(*targets)
        self.ScatterEvent('OnRefreshScanResults')

    def IgnoreOtherResults(self, *targets):
        for result in self.resultsHistory.LastResultIterator():
            if result['id'] not in targets:
                self.resultsIgnored.add(result['id'])

        self.ScatterEvent('OnRefreshScanResults')

    def ShowIgnoredResult(self, targetID):
        if targetID in self.resultsIgnored:
            self.resultsIgnored.remove(targetID)
            self.ScatterEvent('OnRefreshScanResults')

    def ClearIgnoredResults(self):
        self.resultsIgnored = set()
        self.ScatterEvent('OnRefreshScanResults')

    def IgnoreResult(self, *targets):
        for targetID in targets:
            self.resultsIgnored.add(targetID)

        self.ScatterEvent('OnRefreshScanResults')

    def GetScanResults(self):
        return self.resultsHistory.GetLastResults()

    def SetProbesAsScanning(self, probeIDs):
        self.scanningProbes = probeIDs

    def StopScanning(self):
        self.currentScan = None
        self.scanningProbes = None

    def GetScanningProbes(self):
        return self.scanningProbes

    def IsScanning(self):
        return bool(self.scanningProbes)

    def GetIgnoredResults(self):
        return self.resultsIgnored

    def GetResultsHistory(self):
        return self.resultsHistory

    def ClearCombatTargets(self):
        combat_targets = []
        for result in self.resultsHistory.LastResultIterator():
            if result['scanGroupID'] in COMBAT_TARGETS:
                combat_targets.append(result['id'])

        self.ClearResults(*combat_targets)

    def GetResults(self, applyFiltering = True):
        ignored = 0
        filtered = 0
        anomaliesFiltered = 0
        results = []
        for result in self.resultsHistory.LastResultIterator():
            if applyFiltering:
                if result['id'] in self.resultsIgnored:
                    ignored += 1
                    continue
                if result['scanGroupID'] == probeScanGroupAnomalies:
                    if not self.resultFilter.IsShowingAnomalies():
                        anomaliesFiltered += 1
                        continue
                elif self.resultFilter.IsFilteredOut(result):
                    filtered += 1
                    continue
            results.append(result)

        return (results,
         ignored,
         filtered,
         anomaliesFiltered)
