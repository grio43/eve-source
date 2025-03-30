#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\combat_anomalies\job.py
import localization
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupCombatAnomalies
from jobboard.client.features.dungeons.job import DungeonJob

class CombatAnomalyJob(DungeonJob):
    CONTENT_GROUP_ID = contentGroupCombatAnomalies

    @property
    def subtitle(self):
        faction_name = self.faction_name
        if self.difficulty:
            difficulty = localization.GetByLabel('UI/Agency/LevelX', level=self.difficulty)
            if faction_name:
                return u'{} - {}'.format(faction_name, difficulty)
            else:
                return difficulty
        return faction_name
