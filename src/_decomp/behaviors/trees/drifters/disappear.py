#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\drifters\disappear.py
from behaviors.composites import Sequence
from behaviors.actions.ballparks import GetItemIdByTypeId, ApproachObject, GetObjectSpaceLocation
from behaviors.actions.ballparks import GetRandomDeepSpacePosition, TransferToLocation
from behaviors.actions.effects import PlayOneShotShipEffectAction
from behaviors.actions.timer import SucceedAfterTimeoutAction
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.decorators.modifiers import Uninterruptible, Invulnerable, Cloaked
from brennivin.itertoolsext import Bundle
WORMHOLE_TYPE_IDS = [35650,
 35651,
 35652,
 35653,
 35654]
WORMHOLE = (ScopeTypes.EntityGroup, 'WORMHOLE')
WORMHOLE_LOCATION = (ScopeTypes.EntityGroup, 'WORMHOLE_LOCATION')
DISAPPEAR_WORMHOLE = (ScopeTypes.EntityGroup, 'DISAPPEAR_WORMHOLE')
DISAPPEAR_DURATION_SEC = 1800
CLOAK_EFFECT_DELAY_SEC = 2
INVULNERABILITY_REASON = 'Hideout'
WORMHOLE_EFFECT = 'effects.WormholeActivity'
WORMHOLE_DURATION_MSEC = 2000

def CreateDisappearBehavior():

    def CreateApproachWormhole():
        node = Sequence(Bundle(name='Approach Wormhole'))
        node.AddSubTask(GetItemIdByTypeId(Bundle(typeIds=WORMHOLE_TYPE_IDS, itemIdAddress=WORMHOLE)))
        node.AddSubTask(ApproachObject(Bundle(itemIdAddress=WORMHOLE, notifyRange=2500, approachRange=500, blocking=True)))
        return node

    def CreateHideoutAndThenReturn():
        return Uninterruptible().AddSubTask(Invulnerable(attributes=Bundle(reason=INVULNERABILITY_REASON)).AddSubTask(Cloaked().AddSubTask(Sequence(Bundle(name='Go Hideout, then Return')).AddSubTask(GetRandomDeepSpacePosition(Bundle(locationAddress=DISAPPEAR_WORMHOLE))).AddSubTask(PlayOneShotShipEffectAction(Bundle(effectDuration=WORMHOLE_DURATION_MSEC, effectName=WORMHOLE_EFFECT, effectTargetAddress=WORMHOLE))).AddSubTask(SucceedAfterTimeoutAction(Bundle(timeoutSeconds=CLOAK_EFFECT_DELAY_SEC))).AddSubTask(TransferToLocation(Bundle(locationAddress=DISAPPEAR_WORMHOLE))).AddSubTask(SucceedAfterTimeoutAction(Bundle(timeoutSeconds=DISAPPEAR_DURATION_SEC))).AddSubTask(GetObjectSpaceLocation(Bundle(itemIdAddress=WORMHOLE, locationAddress=WORMHOLE_LOCATION))).AddSubTask(TransferToLocation(Bundle(locationAddress=WORMHOLE_LOCATION))).AddSubTask(SucceedAfterTimeoutAction(Bundle(timeoutSeconds=CLOAK_EFFECT_DELAY_SEC))))))

    root = Sequence(Bundle(name='Disappear'))
    root.AddSubTask(CreateApproachWormhole())
    root.AddSubTask(CreateHideoutAndThenReturn())
    return root
