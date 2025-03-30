#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\ice_belts\job.py
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupIceBelts
from evedungeons.client.iceTypesInDungeon.util import get_consolidated_ice_types_in_dungeon
from jobboard.client.features.dungeons.job import DungeonJob

class IceBeltJob(DungeonJob):
    CONTENT_GROUP_ID = contentGroupIceBelts

    @property
    def resources(self):
        return set(get_consolidated_ice_types_in_dungeon(self.dungeon_id))
