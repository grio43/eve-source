#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\esiUtils.py
from crimewatch.util import GetKillReportHashValue
from eveCommonUtils import CopyTextToClipboard
from globalConfig.getFunctions import GetESIBaseUrl, GetESIDatasource, GetESIKillmailVersion, GetESIFleetVersion

def GetESIKillmailUrl(killmail):
    machoNet = sm.GetService('machoNet')
    baseUrl = GetESIBaseUrl(machoNet)
    datasource = GetESIDatasource(machoNet)
    killmailVersion = GetESIKillmailVersion(machoNet)
    killmailHash = GetKillReportHashValue(killmail)
    killmailUrl = '{baseUrl}/{version}/killmails/{id}/{hash}/?datasource={datasource}'.format(baseUrl=baseUrl, version=killmailVersion, id=killmail.killID, hash=killmailHash, datasource=datasource)
    return killmailUrl


def GetESIFleetUrl(fleetID):
    machoNet = sm.GetService('machoNet')
    baseUrl = GetESIBaseUrl(machoNet)
    datasource = GetESIDatasource(machoNet)
    fleetVersion = GetESIFleetVersion(machoNet)
    fleetUrl = '{baseUrl}/{version}/fleets/{id}/?datasource={datasource}'.format(baseUrl=baseUrl, version=fleetVersion, id=fleetID, datasource=datasource)
    return fleetUrl


def CopyESIKillmailUrlToClipboard(killmail):
    url = GetESIKillmailUrl(killmail)
    CopyTextToClipboard(url)


def CopyESIFleetUrlToClipboard(fleetID):
    url = GetESIFleetUrl(fleetID)
    CopyTextToClipboard(url)
