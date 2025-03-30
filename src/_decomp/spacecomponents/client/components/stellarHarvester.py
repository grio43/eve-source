#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\stellarHarvester.py
import logging
from clienteffects import StartShipEffect, StopShipEffect, StartStretchEffect, StopStretchEffect
from spacecomponents.client.messages import MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_LOAD_OBJECT
from spacecomponents.common.components.component import Component
from spacecomponents.client.messages import MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE
logger = logging.getLogger(__name__)

class StellarHarvesterEffect(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        super(StellarHarvesterEffect, self).__init__(itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)
        self.SubscribeToMessage(MSG_ON_LOAD_OBJECT, self.OnLoadObject)
        self.graphicInfo = dict()

    def OnAddedToSpace(self, slimItem):
        self.OnSlimItemUpdated(slimItem)

    def OnRemovedFromSpace(self):
        StopShipEffect(self.itemID, self.attributes.effectGUID, graphicInfo=self.graphicInfo)

    def OnSlimItemUpdated(self, slimItem):
        pass

    def OnLoadObject(self, ball):
        self.graphicInfo['radius'] = self.attributes.radius
        cycleDuration = self.attributes.updateInterval * 1000
        numRepeats = int(self.attributes.duration / self.attributes.updateInterval)
        scm = sm.GetService('sceneManager')
        scene = scm.GetRegisteredScene('default')
        targetBall = scene.sunBall if scene else None
        StartStretchEffect(self.itemID, targetBall.id, self.attributes.effectGUID, cycleDuration, numRepeats)
        logger.debug('StellarHarvesterEffect.OnLoadObject %d', self.itemID)
