#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\target.py
from eve.client.script.parklife import states as state
from eve.common.script.sys.eveCfg import InShipInSpace
from .parameters import SlimItemParameters

class TargetLocked(SlimItemParameters):
    atom_id = 130

    def validate(self, **kwargs):
        if not session.shipid:
            return False
        for target_id in sm.GetService('target').GetTargets():
            if super(TargetLocked, self).validate(item_id=target_id):
                return True

        return False


class SpaceObjectSelected(SlimItemParameters):
    atom_id = 131

    def validate(self, **kwargs):
        if not session.shipid:
            return False
        item_id = sm.GetService('stateSvc').GetExclState(state.selected)
        if not item_id:
            return False
        return super(SpaceObjectSelected, self).validate(item_id=item_id)


class IsTargeted(SlimItemParameters):
    atom_id = 615

    def validate(self, **kwargs):
        if not InShipInSpace():
            return False
        return sm.GetService('target').IsTargeted()
