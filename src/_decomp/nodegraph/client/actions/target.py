#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\target.py
import eve.client.script.parklife.states as states
from .base import Action

class SelectSpaceObject(Action):
    atom_id = 147

    def __init__(self, item_id = None, **kwargs):
        super(SelectSpaceObject, self).__init__(**kwargs)
        self.item_id = item_id

    def start(self, **kwargs):
        super(SelectSpaceObject, self).start(**kwargs)
        sm.GetService('stateSvc').SetState(self.item_id, states.selected, 1)
        sm.GetService('menu').TacticalItemClicked(self.item_id)


class LockTarget(Action):
    atom_id = 200

    def __init__(self, item_id = None, **kwargs):
        super(LockTarget, self).__init__(**kwargs)
        self.item_id = item_id

    def start(self, **kwargs):
        super(LockTarget, self).start(**kwargs)
        sm.GetService('target').TryLockTarget(self.item_id)


class UnlockTarget(Action):
    atom_id = 201

    def __init__(self, item_id = None, **kwargs):
        super(UnlockTarget, self).__init__(**kwargs)
        self.item_id = item_id

    def start(self, **kwargs):
        super(UnlockTarget, self).start(**kwargs)
        sm.GetService('target').CancelAddTarget(self.item_id)
        sm.GetService('target').UnlockTarget(self.item_id)


class UnlockAllTargets(Action):
    atom_id = 202

    def start(self, **kwargs):
        super(UnlockAllTargets, self).start(**kwargs)
        sm.GetService('target').UnlockTargets()
