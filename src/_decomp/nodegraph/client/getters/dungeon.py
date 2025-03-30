#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\dungeon.py
import logging
from evedungeons.client.data import GetDungeon
from .base import GetterAtom
logger = logging.getLogger(__name__)

class GetDungeonInfo(GetterAtom):
    atom_id = 612

    def get_values(self, **kwargs):
        dungeon_id = sm.GetService('dungeonTracking').GetCurrentDungeonID()
        dungeonInfo = GetDungeon(dungeon_id)
        if dungeonInfo:
            return {'use_default_space_music': bool(dungeonInfo.useDefaultSpaceMusic)}
        logger.error('Could not get info for dungeon {}'.format(dungeon_id))
