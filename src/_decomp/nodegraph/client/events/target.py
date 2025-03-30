#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\target.py
from .base import Event

class TargetExploded(Event):
    atom_id = 167
    __notifyevents__ = ['OnTargets']

    def OnTargets(self, targets):
        for target in targets:
            target_length = len(target)
            event = target[1] if target_length > 1 else ''
            target_id = target[2] if target_length > 2 else ''
            reason = target[3] if target_length > 3 else ''
            if event == 'lost' and reason == 'Exploding':
                self.invoke(item_id=target_id)


class TargetLocked(Event):
    atom_id = 49
    __notifyevents__ = ['OnClientEvent_LockItem']

    def OnClientEvent_LockItem(self, slim_item):
        self.invoke(item_id=slim_item.itemID)


class TargetLockStarted(Event):
    atom_id = 50
    __notifyevents__ = ['OnTargetLockStarted']

    def OnTargetLockStarted(self, slim_item):
        self.invoke(item_id=slim_item.itemID)


class TargetLockStopped(Event):
    atom_id = 51
    __notifyevents__ = ['OnClientEvent_UnlockItem']

    def OnClientEvent_UnlockItem(self, target_id):
        self.invoke(item_id=target_id)


class TargetedByChanged(Event):
    atom_id = 613
    __notifyevents__ = ['OnClientEvent_TargetedByChanged']

    def OnClientEvent_TargetedByChanged(self):
        self.invoke()


class SpaceObjectSelectionChanged(Event):
    atom_id = 54
    __notifyevents__ = ['OnSpaceBracketSelectionChanged']

    def OnSpaceBracketSelectionChanged(self, slim_item):
        self.invoke(item_id=slim_item.itemID)


class SpaceObjectExploded(Event):
    atom_id = 168
    __notifyevents__ = ['OnObjectExplode']

    def OnObjectExplode(self, type_id, item_id):
        self.invoke(type_id=type_id, item_id=item_id)
