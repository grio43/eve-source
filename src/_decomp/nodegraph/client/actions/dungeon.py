#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\dungeon.py
import logging
from .base import Action
logger = logging.getLogger('atoms')

class SendMessageToClientDungeon(Action):
    atom_id = 543

    def __init__(self, dungeon_id = None, message_key = None, message_value = None, **kwargs):
        super(SendMessageToClientDungeon, self).__init__(**kwargs)
        self.dungeon_id = dungeon_id
        self.message_key = message_key
        self.message_value = message_value

    def start(self, **kwargs):
        if not self.dungeon_id or not self.message_key:
            logger.debug('SendMessageToClientDungeon requires dungeon_id and message_key')
            return
        sm.ScatterEvent('OnDungeonMessage', self.dungeon_id, self.message_key, self.message_value)

    @classmethod
    def get_subtitle(cls, message_key = None, **kwargs):
        return message_key
