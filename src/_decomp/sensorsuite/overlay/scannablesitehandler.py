#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sensorsuite\overlay\scannablesitehandler.py
from sensorsuite.overlay.scannablesitedata import ScannableSiteData
from sensorsuite.overlay.sitehandler import SiteHandler

class ScannableSiteHandler(SiteHandler):

    def __init__(self):
        SiteHandler.__init__(self)

    def GetSiteData(self, siteID, siteInfo):
        return ScannableSiteData(siteID, siteInfo)

    def ProcessSiteUpdate(self, addedSites, removedSites):
        SiteHandler.ProcessSiteUpdate(self, addedSites, removedSites)
        sm.GetService('sensorSuite').InjectScannerResults(self.siteType)
