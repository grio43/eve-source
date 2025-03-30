#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\navigation.py
from .base import Event

class ApproachCommand(Event):
    atom_id = 48
    __notifyevents__ = ['OnClientEvent_ApproachCommand']

    def OnClientEvent_ApproachCommand(self, slim_item):
        if slim_item:
            item_id = slim_item.itemID
        else:
            item_id = None
        self.invoke(item_id=item_id)


class ApproachExecuted(Event):
    atom_id = 105
    __notifyevents__ = ['OnClientEvent_ApproachExecuted']

    def OnClientEvent_ApproachExecuted(self, target_id):
        self.invoke(item_id=target_id)


class KeepAtRangeCommand(Event):
    atom_id = 108
    __notifyevents__ = ['OnClientEvent_KeepAtRangeCommand']

    def OnClientEvent_KeepAtRangeCommand(self, item_id, distance):
        self.invoke(item_id=item_id, distance=distance)


class KeepAtRangeExecuted(Event):
    atom_id = 109
    __notifyevents__ = ['OnClientEvent_KeepAtRangeExecuted']

    def OnClientEvent_KeepAtRangeExecuted(self, item_id, distance):
        self.invoke(item_id=item_id, distance=distance)


class AlignCommand(Event):
    atom_id = 354
    __notifyevents__ = ['OnClientEvent_AlignCommand']

    def OnClientEvent_AlignCommand(self, item_id):
        self.invoke(item_id=item_id)


class AlignExecuted(Event):
    atom_id = 355
    __notifyevents__ = ['OnClientEvent_AlignExecuted']

    def OnClientEvent_AlignExecuted(self, target_id):
        self.invoke(item_id=target_id)


class MoveTowardsCommand(Event):
    atom_id = 110
    __notifyevents__ = ['OnClientEvent_MoveTowardsCommand']

    def OnClientEvent_MoveTowardsCommand(self, target_id):
        self.invoke(item_id=target_id)


class MoveTowardsExecuted(Event):
    atom_id = 111
    __notifyevents__ = ['OnClientEvent_MoveTowardsExecuted']

    def OnClientEvent_MoveTowardsExecuted(self, target_id, distance):
        self.invoke(item_id=target_id, distance=distance)


class MoveTowardsPointCommand(Event):
    atom_id = 52
    __notifyevents__ = ['OnClientEvent_MoveTowardsPointCommand']

    def OnClientEvent_MoveTowardsPointCommand(self, *args):
        self.invoke()


class MoveTowardsPointExecuted(Event):
    atom_id = 106
    __notifyevents__ = ['OnClientEvent_MoveTowardsPointExecuted']

    def OnClientEvent_MoveTowardsPointExecuted(self):
        self.invoke()


class NavigationChanged(Event):
    atom_id = 174
    valid_events = None
    __notifyevents__ = ['OnBallparkCall']

    def OnBallparkCall(self, event, event_arguments):
        if event_arguments[0] != session.shipid:
            return
        if self.valid_events and event not in self.valid_events:
            return
        self.invoke(event=event)


class ShipStopped(Event):
    atom_id = 344
    __notifyevents__ = ['OnClientEvent_StopExecuted']

    def OnClientEvent_StopExecuted(self):
        self.invoke()


class OrbitCommand(Event):
    atom_id = 53
    __notifyevents__ = ['OnClientEvent_OrbitCommand']

    def OnClientEvent_OrbitCommand(self, targetID, *args):
        self.invoke(item_id=targetID)


class OrbitExecuted(Event):
    atom_id = 107
    __notifyevents__ = ['OnClientEvent_OrbitExecuted']

    def OnClientEvent_OrbitExecuted(self, item_id, distance):
        self.invoke(item_id=item_id, distance=distance)


class BoardCommand(Event):
    atom_id = 250
    __notifyevents__ = ['OnBeforeActiveShipChanged']

    def OnBeforeActiveShipChanged(self, new_ship_id, _old_ship_id):
        self.invoke(item_id=new_ship_id)
