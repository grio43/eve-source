#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\proximityTrap.py
from spacecomponents.client.messages import MSG_ON_LOAD_OBJECT
from spacecomponents.common.components.component import Component
import logging
logger = logging.getLogger(__name__)

class ProximityTrap(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_LOAD_OBJECT, self.OnLoadObject)

    def OnLoadObject(self, ball):
        self._UpdateModel(ball)

    def _UpdateModel(self, ball):
        model = ball.GetModel()
        model.SetControllerVariable('Blast_Scale', self.attributes.triggerRange)
