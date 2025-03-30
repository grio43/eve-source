#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\explorationscanner\common\cosmicAnomalyInfo.py
from explorationscanner.common.siteInfo import SiteInfo

class CosmicAnomalyInfo(SiteInfo):

    def __init__(self, position, targetID, difficulty, dungeonID, archetypeID, instanceID, dungeonNameID, factionID, scanStrengthAttribute, allowedTypes, entryObjectTypeID, solarSystemID):
        super(CosmicAnomalyInfo, self).__init__(position, targetID, difficulty, dungeonID, archetypeID)
        self.siteID = instanceID
        self.instanceID = instanceID
        self.dungeonNameID = dungeonNameID
        self.factionID = factionID
        self.scanStrengthAttribute = scanStrengthAttribute
        self.allowedTypes = allowedTypes
        self.entryObjectTypeID = entryObjectTypeID
        self.solarSystemID = solarSystemID
