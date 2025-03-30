#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sensorsuite\overlay\anomalies.py
from inventorycommon.const import groupCosmicAnomaly
import localization
from probescanning.const import probeScanGroupAnomalies
from sensorsuite.overlay.brackets import SensorSuiteBracket, INNER_ICON_COLOR
from sensorsuite.overlay.scannablesitedata import ScannableSiteData
from sensorsuite.overlay.scannablesitehandler import ScannableSiteHandler
from sensorsuite.overlay.siteconst import SITE_COLOR_ANOMALY, SITE_ANOMALY
from sensorsuite.overlay.sitetype import ANOMALY

class AnomalySiteData(ScannableSiteData):
    siteType = ANOMALY
    baseColor = SITE_COLOR_ANOMALY
    hoverSoundEvent = 'ui_scanner_state_anomaly'
    scanGroupID = probeScanGroupAnomalies
    groupID = groupCosmicAnomaly

    def __init__(self, siteID, instanceID, position, targetID, difficulty, dungeonID, archetypeID, dungeonNameID, factionID, scanStrengthAttribute, allowedTypes):
        ScannableSiteData.__init__(self, siteID, position, targetID, difficulty, dungeonID, archetypeID, dungeonNameID, factionID, scanStrengthAttribute)
        self.instanceID = instanceID
        self.deviation = 0.0
        self.signalStrength = 1.0
        self.allowedTypes = allowedTypes

    def GetBracketClass(self):
        return AnomalyBracket


class AnomalyBracket(SensorSuiteBracket):
    outerColor = SITE_COLOR_ANOMALY.GetRGBA()
    innerColor = INNER_ICON_COLOR.GetRGBA()
    innerIconResPath = 'res:/UI/Texture/classes/SensorSuite/diamond2.png'
    outerTextures = ('res:/UI/Texture/classes/SensorSuite/bracket_anomaly_1.png', 'res:/UI/Texture/classes/SensorSuite/bracket_anomaly_2.png', 'res:/UI/Texture/classes/SensorSuite/bracket_anomaly_3.png', 'res:/UI/Texture/classes/SensorSuite/bracket_anomaly_4.png')

    def ApplyAttributes(self, attributes):
        SensorSuiteBracket.ApplyAttributes(self, attributes)
        self.UpdateSiteName(localization.GetByMessageID(self.data.dungeonNameID))

    def GetMenu(self):
        return self.data.GetMenu()

    def GetBracketLabelText(self):
        return self.data.targetID


class AnomalyHandler(ScannableSiteHandler):
    siteType = ANOMALY
    filterIconPath = 'res:/UI/Texture/classes/SensorSuite/diamond2.png'
    filterLabel = 'UI/Inflight/Scanner/AnomalySiteFilterLabel'
    color = SITE_COLOR_ANOMALY
    siteIconData = SITE_ANOMALY

    def GetSiteData(self, siteID, siteInfo):
        return AnomalySiteData(siteID, siteInfo.instanceID, siteInfo.position, siteInfo.targetID, siteInfo.difficulty, siteInfo.dungeonID, siteInfo.archetypeID, siteInfo.dungeonNameID, siteInfo.factionID, siteInfo.scanStrengthAttribute, siteInfo.allowedTypes)

    def ProcessSiteUpdate(self, addedSites, removedSites):
        oldSites = self.GetSites()
        changesByArchetypeID = set()
        for site in addedSites.values():
            changesByArchetypeID.add(site.archetypeID)

        for instanceID in removedSites:
            site = oldSites.get(instanceID)
            if site:
                changesByArchetypeID.add(site.archetypeID)

        super(AnomalyHandler, self).ProcessSiteUpdate(addedSites, removedSites)
        dungeon_trackers = sm.GetService('dungeonTracking').trackers
        for tracker in dungeon_trackers.itervalues():
            tracker.scan_results_updated(has_changes=not changesByArchetypeID.isdisjoint(tracker.ARCHETYPE_IDS))
