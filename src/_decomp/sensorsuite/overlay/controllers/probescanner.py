#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sensorsuite\overlay\controllers\probescanner.py
from eveexceptions.exceptionEater import ExceptionEater
from inventorycommon.const import categoryStructure
from probescanning.const import probeScanGroupAnomalies, probeScanGroupSignatures, probeScanGroupStructures
from sensorsuite.error import InvalidClientStateError
from sensorsuite.overlay.anomalies import AnomalySiteData
from sensorsuite.overlay.scannablesitedata import BaseScannableSiteData
from sensorsuite.overlay.signatures import SignatureSiteData
from sensorsuite.overlay.sitetype import ANOMALY, SIGNATURE, STRUCTURE
from sensorsuite.overlay.structures import StructureSiteData
from utillib import KeyVal
import logging
logger = logging.getLogger(__name__)
POSITIONAL_SITE_TYPES = [ANOMALY, STRUCTURE]

def GetSitesAsProbeResults(sites):
    results = []
    for site in sites:
        data, pos = GetSitePositionalData(site)
        nameID, name = GetSiteScanName(site)
        results.append(KeyVal(id=site.targetID, certainty=site.signalStrength, prevCertainty=site.signalStrength, groupID=site.groupID, strengthAttributeID=site.scanStrengthAttribute, scanGroupID=site.scanGroupID, data=data, pos=pos, dungeonName=name, dungeonNameID=nameID, dungeonID=site.dungeonID, archetypeID=site.archetypeID, typeID=site.groupID))

    return results


def GetSitePositionalData(site):
    if site.signalStrength > 0:
        data = site.position
    else:
        data = site.position if IsSitePositional(site) else site.deviation
    pos = None if IsSitePositional(site) else site.position
    return (data, pos)


def IsSitePositional(site):
    return site.GetSiteType() in POSITIONAL_SITE_TYPES


def GetSiteScanName(site):
    if isinstance(site, BaseScannableSiteData):
        return site.GetScanName()
    return (None, '')


def SiteDataFromScanResult(result):
    if result.scanGroupID == probeScanGroupAnomalies:
        return AnomalySiteData(result.id, None, result.pos, result.id, None, None, None, result.dungeonNameID, None, None, None)
    if result.scanGroupID == probeScanGroupSignatures:
        return SignatureSiteData(result.id, result.pos, result.id, None, None, None, result.dungeonNameID, deviation=None, signalStrength=result.certainty)
    if result.scanGroupID == probeScanGroupStructures:
        return StructureSiteData(result.itemID, result.typeID, result.groupID, categoryStructure, result.pos, result.id)
    return GetDefaultSiteData(result)


def GetDefaultSiteData(result):
    return SignatureSiteData(result.id, result.pos, result.id, None, None, None, result.dungeonNameID, deviation=None, signalStrength=result.certainty)


class ProbeScannerController:

    def __init__(self, scanSvc, michelle, siteController):
        self.scanSvc = scanSvc
        self.michelle = michelle
        self.siteController = siteController

    def UpdateProbeResultBrackets(self):
        updateSigData = set()
        for sigData in self.siteController.siteMaps.IterSitesByKey(SIGNATURE):
            with ExceptionEater('Updating signature overlay bracket'):
                result = self.scanSvc.GetResultForTargetID(sigData.targetID)
                if result['data'] is None:
                    continue
                if sigData.dungeonNameID is None:
                    dungeonNameID = result.get('dungeonNameID', None)
                    if dungeonNameID is not None:
                        sigData.dungeonNameID = dungeonNameID
                        updateSigData.add(sigData)
                if sigData.factionID is None:
                    factionID = result.get('factionID', None)
                    if factionID is not None:
                        sigData.factionID = factionID
                        updateSigData.add(sigData)
                if sigData.scanStrengthAttribute is None:
                    strengthAttributeID = result.get('strengthAttributeID', None)
                    if strengthAttributeID is not None:
                        sigData.scanStrengthAttribute = strengthAttributeID
                        updateSigData.add(sigData)
                if result['certainty'] > sigData.signalStrength and isinstance(result['data'], tuple):
                    sigData.signalStrength = result['certainty']
                    if result['certainty'] >= 1.0:
                        sigData.position = result['data']
                        bp = self.michelle.GetBallpark()
                        if bp is None:
                            raise InvalidClientStateError('ballpark not found')
                        if self.siteController.spaceLocations.ContainsSite(sigData.siteID):
                            ball = self.siteController.spaceLocations.GetBySiteID(sigData.siteID).ballRef()
                            bp.SetBallPosition(ball.id, *sigData.position)
                            self.siteController.NotifySiteChanged(sigData)
                    updateSigData.add(sigData)
            if updateSigData:
                for sigData_ in updateSigData:
                    self.UpdateScanData(sigData_)

    def UpdateScanData(self, sigData):
        bracket = self.siteController.spaceLocations.GetBracketBySiteID(sigData.siteID)
        if bracket:
            bracket.UpdateScanData()

    def GetAllSites(self):
        return GetSitesAsProbeResults(self.siteController.siteMaps.IterSitesByKeys(SIGNATURE, ANOMALY))

    def InjectSiteScanResults(self, sites):
        probeResults = GetSitesAsProbeResults(sites)
        self.scanSvc.InjectSitesAsScanResults(probeResults)
