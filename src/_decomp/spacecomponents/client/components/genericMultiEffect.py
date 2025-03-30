#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\genericMultiEffect.py
import logging
from clienteffects import StartShipEffect, StopShipEffect
from spacecomponents.client.messages import MSG_ON_SLIM_ITEM_UPDATED
from spacecomponents.common.components.component import Component
from spacecomponents.client.messages import MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE
logger = logging.getLogger(__name__)

class GenericMultiEffect(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        super(GenericMultiEffect, self).__init__(itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)
        self.graphicInfo = dict()

    def OnAddedToSpace(self, slimItem):
        self.graphicInfo['timeAddedToSpace'] = slimItem.timeAddedToSpace
        effectTargets = {}
        for index, object in enumerate(self.attributes.objects['_items_']):
            effectTargets[index] = object.enumObject

        self.graphicInfo['effectTargets'] = effectTargets
        cycleDuration = self.attributes.updateInterval * 1000
        numRepeats = int(self.attributes.duration / self.attributes.updateInterval)
        StartShipEffect(self.itemID, self.attributes.effectGUID, cycleDuration, numRepeats, graphicInfo=self.graphicInfo)
        logger.debug('MultiEffect.OnAddedToSpace %d', self.itemID)
        self.OnSlimItemUpdated(slimItem)

    def OnRemovedFromSpace(self):
        StopShipEffect(self.itemID, self.attributes.effectGUID, graphicInfo=self.graphicInfo)

    def OnSlimItemUpdated(self, slimItem):
        pass
