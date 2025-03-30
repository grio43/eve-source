#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sensorsuite\overlay\scannablesitedata.py
from menu import MenuLabel
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import SimpleRadialMenuAction
from eve.client.script.ui.shared.radialMenu.spaceRadialMenuFunctions import bookMarkOption
from localization import GetByMessageID
from sensorsuite.overlay.sitedata import SiteData
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService

class BaseScannableSiteData(SiteData):
    scanGroupID = None
    groupID = None

    def __init__(self, siteID, position, targetID):
        SiteData.__init__(self, siteID, position)
        self.targetID = targetID

    def GetMenu(self):
        scanSvc = sm.GetService('scanSvc')
        menu = [(MenuLabel(uicore.cmd.ToggleProbeScanner.nameLabelPath), uicore.cmd.ToggleProbeScanner, [])]
        menu.extend(scanSvc.GetScanResultMenuWithIgnore(self, self.scanGroupID))
        return menu

    def GetSiteActions(self):
        return []

    def GetSecondaryActions(self):
        return [bookMarkOption, SimpleRadialMenuAction(option1='UI/Inflight/Scanner/IngoreResult'), SimpleRadialMenuAction(option1='UI/Inflight/Scanner/IgnoreOtherResults')]

    def WarpToAction(self, _, distance, *args):
        return GetMenuService().WarpToScanResult(self.targetID, minRange=distance)

    def GetScanName(self):
        return (None, '')


class ScannableSiteData(BaseScannableSiteData):
    scanGroupID = None
    groupID = None

    def __init__(self, siteID, position, targetID, difficulty, dungeonID, archetypeID, dungeonNameID, factionID, scanStrengthAttribute):
        BaseScannableSiteData.__init__(self, siteID, position, targetID)
        self.difficulty = difficulty
        self.dungeonNameID = dungeonNameID
        self.factionID = factionID
        self.scanStrengthAttribute = scanStrengthAttribute
        self.dungeonID = dungeonID
        self.archetypeID = archetypeID

    def GetName(self):
        return self.targetID

    def GetScanName(self):
        if self.dungeonNameID:
            return (self.dungeonNameID, self.GetDungeonName())
        return (None, '')

    def GetDungeonName(self):
        return GetByMessageID(self.dungeonNameID)
