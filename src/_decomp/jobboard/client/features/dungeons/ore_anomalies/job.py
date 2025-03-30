#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\ore_anomalies\job.py
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupOreAnomalies
from evedungeons.client.oreTypesInDungeons.util import get_consolidated_ore_types_in_dungeon
from jobboard.client.features.dungeons.job import DungeonJob

class OreAnomalyJob(DungeonJob):
    CONTENT_GROUP_ID = contentGroupOreAnomalies

    @property
    def resources(self):
        return set(get_consolidated_ore_types_in_dungeon(self.dungeon_id))
