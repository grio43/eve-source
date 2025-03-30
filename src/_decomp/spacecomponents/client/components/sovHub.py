#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\sovHub.py
import logging
from spacecomponents import Component
from spacecomponents.client import MSG_ON_ADDED_TO_SPACE
logger = logging.getLogger(__name__)

class SovHub(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)

    def OnAddedToSpace(self, slimItem):
        print 'sov hub added to space, slimItem= ', slimItem
