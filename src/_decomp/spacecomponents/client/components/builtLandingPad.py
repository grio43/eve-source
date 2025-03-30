#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\builtLandingPad.py
from spacecomponents import Component
import logging
from spacecomponents.client.messages import MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_LOAD_OBJECT, MSG_ON_ADDED_TO_SPACE
from shipcaster.shipcasterConst import LANDING_PAD_SLIM_STATE_DISRUPTED, LANDING_PAD_SLIM_STATE_LINKED, LANDING_PAD_SLIM_STATE_UNLINKED, LANDING_PAD_SLIM_STATE_ATTRIBUTE
from structures import STATE_UNKNOWN, STATE_ONLINING_VULNERABLE, STATE_UNANCHORED, STATE_SHIELD_VULNERABLE, STATE_FOB_INVULNERABLE
logger = logging.getLogger(__name__)

class BuiltLandingPad(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_LOAD_OBJECT, self.OnLoadObject)
        self.modelState = LANDING_PAD_SLIM_STATE_UNLINKED
        self.itemID = itemID
        self._playInitialSpawnAnimation = False
        self._restartControllersOnNextUpdate = False
        self._damageStates = [1.0, 1.0, 1.0]
        self._upkeepState = STATE_SHIELD_VULNERABLE

    def OnSlimItemUpdated(self, slimItem):
        self._damageStates = slimItem.damage
        self._upkeepState = slimItem.state
        ball = sm.GetService('michelle').GetBall(self.itemID)
        if slimItem.unanchoring:
            ball.SetControllerVariable('Deathless_FOB_Cloak_Duration', 60.0)
            ball.SetControllerVariable('Deathless_FOB_Cloak', 0.0)
        self.modelState = getattr(slimItem, LANDING_PAD_SLIM_STATE_ATTRIBUTE, None)
        self._UpdateModel(ball)

    def OnAddedToSpace(self, slimItem):
        self._restartControllersOnNextUpdate = True

    def OnLoadObject(self, ball):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        slimItem = bp.GetInvItem(self.itemID)
        self.OnSlimItemUpdated(slimItem)

    def _UpdateModel(self, ball):
        if self._playInitialSpawnAnimation:
            ball.SetControllerVariable('Deathless_FOB_Cloak', 0.0)
            if hasattr(ball, 'model') and ball.model is not None:
                ball.model.StartControllers()
            ball.SetControllerVariable('Deathless_FOB_Cloak', 1.0)
            self.playInitialSpawnAnimation = False
        if self.modelState == LANDING_PAD_SLIM_STATE_DISRUPTED:
            ball.SetControllerVariable('Active', 1.0)
            ball.SetControllerVariable('In_Hardening', 1.0)
        elif self.modelState == LANDING_PAD_SLIM_STATE_UNLINKED:
            ball.SetControllerVariable('Active', 0.0)
            ball.SetControllerVariable('In_Hardening', 0.0)
        elif self.modelState == LANDING_PAD_SLIM_STATE_LINKED:
            ball.SetControllerVariable('Active', 1.0)
            ball.SetControllerVariable('In_Hardening', 0.0)
        try:
            operatingState = 0
            if self._upkeepState is not None:
                if self._upkeepState == STATE_ONLINING_VULNERABLE or self._upkeepState == STATE_FOB_INVULNERABLE:
                    operatingState = STATE_UNKNOWN
                else:
                    operatingState = STATE_UNANCHORED + (self._upkeepState - STATE_SHIELD_VULNERABLE)
            ball.SetControllerVariable('operatingState', float(operatingState))
        except TypeError:
            logger.error('buildLandingPad._UpdateModel: landing pad updateState attribute error')

        if hasattr(ball, 'model') and ball.model is not None:
            if self._damageStates is not None:
                ball.model.SetImpactDamageState(self._damageStates[0], self._damageStates[1], self._damageStates[2], True)
            if self._restartControllersOnNextUpdate:
                ball.model.StartControllers()
                self._restartControllersOnNextUpdate = False
