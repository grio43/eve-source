#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\target.py
from .base import GetterAtom

class GetLockedTargets(GetterAtom):
    atom_id = 203

    def get_values(self):
        return {'item_ids': sm.GetService('target').GetTargets().keys()}


class GetSelectedSpaceObject(GetterAtom):
    atom_id = 251

    def get_values(self):
        from eve.client.script.parklife.states import selected
        return {'item_id': sm.GetService('stateSvc').GetExclState(selected)}


class GetOrbitTarget(GetterAtom):
    atom_id = 252

    def get_values(self):
        orbit_target_id = None
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark:
            orbit_target_id = ballpark.GetOrbitTarget()
        return {'item_id': orbit_target_id}


class GetMaxTargetRange(GetterAtom):
    atom_id = 337

    def get_values(self):
        return {'range': int(sm.GetService('target').GetMaxTargetRange())}


class GetDistanceToTarget(GetterAtom):
    atom_id = 437

    def __init__(self, item_id = None, **kwargs):
        self.item_id = item_id

    def get_values(self, **kwargs):
        return {'distance': sm.GetService('target').GetDistanceToTarget(self.item_id)}
