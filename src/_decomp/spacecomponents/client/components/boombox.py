#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\boombox.py
import logging
from fsdBuiltData.client.musicTriggers import GetMusicTrigger
from spacecomponents.client.messages import MSG_ON_ADDED_TO_SPACE
from spacecomponents.client.messages import MSG_ON_SLIM_ITEM_UPDATED
from spacecomponents.common.componentConst import BOOMBOX_MUSIC_TRIGGER_SLIM_ITEM_FIELD
from spacecomponents.common.components.component import Component
logger = logging.getLogger(__name__)

class Boombox(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.musicTriggerID = 0
        self.musicSvc = sm.GetService('dynamicMusic')
        self.musicTriggerOnGridEntry = getattr(attributes, 'musicTriggerOnGridEntry', 0)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)
        logger.debug('Boombox component created in client for item %s with type %s.', itemID, typeID)

    def OnAddedToSpace(self, slimItem):
        if self.musicTriggerOnGridEntry > 0:
            logger.debug('Scheduling music trigger ID %s to play on grid entry for boombox item %s with type %s', self.musicTriggerOnGridEntry, self.itemID, self.typeID)
            self._ScheduleMusicTrigger(self.attributes.musicTriggerOnGridEntry, self.itemID)
        self.OnSlimItemUpdated(slimItem)

    def OnSlimItemUpdated(self, slimItem):
        updatedMusicTriggerID = getattr(slimItem, BOOMBOX_MUSIC_TRIGGER_SLIM_ITEM_FIELD, 0)
        if updatedMusicTriggerID > 0:
            self._ScheduleMusicTrigger(updatedMusicTriggerID, slimItem.itemID)

    def _ScheduleMusicTrigger(self, musicTriggerID, itemID):
        musicTriggerObj = GetMusicTrigger(musicTriggerID)
        musicEvent = getattr(musicTriggerObj, 'trigger', '')
        if musicTriggerID != self.musicTriggerID:
            self.musicSvc.SendMusicEvent(musicEvent)
            self.musicTriggerID = musicTriggerID
            logger.debug('Music trigger %s with ID %s was scheduled to be played for from boombox item %s', musicEvent, musicTriggerID, itemID)
        else:
            logger.debug('Boombox item %s ignored request to play music trigger %s with ID %s because it is already playing', itemID, musicEvent, musicTriggerID)
