#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\mercenaryDen.py
import gametime
import traceback
from logging import getLogger
from sovereignty.mercenaryden.client.mercenary_den_signals import on_mercenary_den_destroyed_on_server_signal
from spacecomponents import Component
from spacecomponents.common.componentConst import MERCENARY_DEN
from spacecomponents.client import MSG_ON_LOAD_OBJECT, MSG_ON_ADDED_TO_SPACE, MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_REMOVED_FROM_SPACE
from spacecomponents.client.components.activate import GetActivationDurationForItem
from carbon.common.script.sys.serviceManager import ServiceManager
logger = getLogger('mercenary_den')
REMOTE_CALL_EXTRACT_INFOMORPHS_TO_SHIP = 'ExtractInfomorphsToShip'

class MercenaryDen(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_LOAD_OBJECT, self.OnLoadObject)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)
        self.model = None
        self.activated = False

    def OnAddedToSpace(self, slimItem):
        self.OnSlimItemUpdated(slimItem)

    def OnLoadObject(self, ball):
        if not self.model:
            try:
                self.model = ball.GetModel()
            except AttributeError:
                return

        ballpark = ball.ballpark
        slimItem = ballpark.slimItems.get(ball.id)
        if slimItem.component_activate is not None:
            self._SetActivation(slimItem.component_activate, ball)
        self.model.StartControllers()

    def OnSlimItemUpdated(self, slimItem):
        ball = sm.GetService('michelle').GetBall(self.itemID)
        if ball and slimItem.component_activate is not None:
            try:
                self.model = ball.GetModel()
                self._SetActivation(slimItem.component_activate, ball)
            except AttributeError:
                return

    def _SetActivation(self, componentActivate, ball):
        if not self.model:
            return
        totalDuration = GetActivationDurationForItem(ball.ballpark, self.itemID) or 120
        if componentActivate[0] is True:
            elapsedTime = totalDuration + 1
            self.SetActiveState(True)
        else:
            activationTime = componentActivate[1] or -1
            remainingDuration = -gametime.GetSecondsSinceSimTime(activationTime)
            elapsedTime = max(0, totalDuration - remainingDuration)
            self.model.SetControllerVariable('IsUnderConstruction', 1.0)
        self.model.SetControllerVariable('IsBuilt', 1)
        self.model.SetControllerVariable('BuildDuration', totalDuration)
        self.model.SetControllerVariable('BuildElapsedTime', elapsedTime)

    def SetProductionState(self):
        if not self.model:
            return
        mercDenState = 0
        if self.activated:
            mercDenState = 1
        self.model.SetControllerVariable('mercdenState', mercDenState)

    def SetActiveState(self, state):
        self.activated = state
        self.SetProductionState()

    def _NotifyIfDestroyedOnServer(self):
        slim_item = sm.GetService('michelle').GetItem(self.itemID)
        if not hasattr(slim_item, '__server_removed_from_space_exploding'):
            return
        logger.debug('mercenary den destroyed on server: %s', self.itemID)
        try:
            on_mercenary_den_destroyed_on_server_signal(self.itemID)
        except Exception:
            logger.exception('Error notifying of server destroyed MDen: %s', traceback.format_exc())

    def OnRemovedFromSpace(self):
        self.SetActiveState(False)
        self._NotifyIfDestroyedOnServer()


def extract_infomorphs_to_ship(mercenary_den_id, flag_id, quantity_to_extract):
    sm = ServiceManager.Instance()
    remote_ballpark = sm.GetService('michelle').GetRemotePark()
    quantity_extracted = remote_ballpark.CallComponentFromClient(mercenary_den_id, MERCENARY_DEN, REMOTE_CALL_EXTRACT_INFOMORPHS_TO_SHIP, flag_id, quantity_to_extract)
    return quantity_extracted
