#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sensorsuite\overlay\structures.py
from menu import MenuLabel
from probescanning.const import probeScanGroupStructures
from sensorsuite.overlay.brackets import SensorSuiteBracket, INNER_ICON_COLOR
from sensorsuite.overlay.scannablesitedata import BaseScannableSiteData
from sensorsuite.overlay.siteconst import SITE_COLOR_STRUCTURE, SITE_STRUCTURE
from sensorsuite.overlay.sitehandler import SiteHandler
from sensorsuite.overlay.sitetype import STRUCTURE
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService

class StructureSiteData(BaseScannableSiteData):
    siteType = STRUCTURE
    baseColor = SITE_COLOR_STRUCTURE
    scanGroupID = probeScanGroupStructures

    def __init__(self, structureID, typeID, groupID, categoryID, position, targetID):
        self.typeID = typeID
        self.groupID = groupID
        self.categoryID = categoryID
        self.deviation = 0.0
        self.signalStrength = 1.0
        self.scanStrengthAttribute = 1.0
        BaseScannableSiteData.__init__(self, structureID, position, targetID)

    def GetBracketClass(self):
        return StructureBracket

    def GetName(self):
        return cfg.evelocations.Get(self.siteID).name

    def GetScanName(self):
        return (self.siteID, self.GetName())

    def GetMenu(self):
        scanSvc = sm.GetService('scanSvc')
        menu = [(MenuLabel(uicore.cmd.ToggleProbeScanner.nameLabelPath), uicore.cmd.GetCommandToExecute('ToggleProbeScanner'), [])]
        menu.extend(scanSvc.GetIgnoreResultMenu(self.targetID, self.scanGroupID))
        menu += GetMenuService().GetMenuFromItemIDTypeID(self.siteID, self.typeID)
        return menu

    def GetItemID(self):
        return self.siteID


class StructureBracket(SensorSuiteBracket):
    outerColor = SITE_STRUCTURE.color.GetRGBA()
    outerTextures = SITE_STRUCTURE.outerTextures
    innerColor = INNER_ICON_COLOR.GetRGBA()
    innerIconResPath = SITE_STRUCTURE.icon

    def ApplyAttributes(self, attributes):
        typeID = attributes.data.typeID
        self.innerIconResPath = sm.GetService('bracket').GetBracketDataByTypeID(typeID).texturePath
        SensorSuiteBracket.ApplyAttributes(self, attributes)

    def GetMenu(self):
        return self.data.GetMenu()

    def GetItemID(self):
        return self.data.GetItemID()


class StructureHandler(SiteHandler):
    siteType = STRUCTURE
    filterIconPath = 'res:/UI/Texture/Shared/Brackets/citadelLarge.png'
    filterLabel = 'UI/Inflight/Scanner/StructureFilterLabel'
    color = SITE_COLOR_STRUCTURE
    siteIconData = SITE_STRUCTURE

    def __init__(self):
        self.structureProximityTracker = sm.GetService('structureProximityTracker')
        SiteHandler.__init__(self)

    def GetSiteData(self, structureID, structureInfo):
        return StructureSiteData(structureID, structureInfo.typeID, structureInfo.groupID, structureInfo.categoryID, structureInfo.position, structureInfo.targetID)

    def ProcessSiteUpdate(self, addedSites, removedSites):
        self._PrimeSites(addedSites)
        SiteHandler.ProcessSiteUpdate(self, addedSites, removedSites)

    def _PrimeSites(self, sites):
        cfg.evelocations.Prime([ siteID for siteID in sites ])

    def IsVisible(self, siteData):
        isVisible = not self.structureProximityTracker.IsStructureVisible(siteData.siteID)
        return isVisible
