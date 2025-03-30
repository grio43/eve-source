#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\travel.py
from .base import Event
from uthread2 import StartTasklet

class AutopilotOn(Event):
    atom_id = 80
    __notifyevents__ = ['OnAutoPilotOn']

    def OnAutoPilotOn(self):
        self.invoke()


class AutopilotJump(Event):
    atom_id = 81
    __notifyevents__ = ['OnAutoPilotJump']

    def OnAutoPilotJump(self):
        self.invoke()


class DestinationSet(Event):
    atom_id = 82
    __notifyevents__ = ['OnDestinationSet']

    def OnDestinationSet(self, destination_id):
        self.invoke(location_id=destination_id)


class DestinationCleared(Event):
    atom_id = 226
    __notifyevents__ = ['OnDestinationCleared']

    def OnDestinationCleared(self):
        self.invoke()


class DockCommand(Event):
    atom_id = 227
    __notifyevents__ = ['OnClientEvent_DockCmdExecuted']

    def OnClientEvent_DockCmdExecuted(self, location_id):
        self.invoke(location_id=location_id)


class DockingAccepted(Event):
    atom_id = 83
    __notifyevents__ = ['OnClientEvent_DockingStarted']

    def OnClientEvent_DockingStarted(self, location_id):
        self.invoke(location_id=location_id)


class DockingCompleted(Event):
    atom_id = 223
    __notifyevents__ = ['OnClientEvent_DockingFinished']

    def __init__(self, *args, **kwargs):
        super(DockingCompleted, self).__init__(*args, **kwargs)

    def OnClientEvent_DockingFinished(self, location_id):
        self.invoke(location_id=location_id)


class JumpStarted(Event):
    atom_id = 84
    __notifyevents__ = ['OnClientEvent_JumpStarted']

    def OnClientEvent_JumpStarted(self, *args):
        self.invoke()


class JumpFinished(Event):
    atom_id = 85
    __notifyevents__ = ['OnClientEvent_JumpFinished']

    def OnClientEvent_JumpFinished(self, *args, **kwargs):
        self.invoke()


class RouteNextSystemJump(Event):
    atom_id = 86
    __notifyevents__ = ['OnClientEvent_JumpedToNextSystemInRoute']

    def OnClientEvent_JumpedToNextSystemInRoute(self):
        self.invoke()


class RouteNextSystemJumpCommand(Event):
    atom_id = 87
    __notifyevents__ = ['OnClientEvent_JumpToNextSystemInRouteCmdExecuted']

    def OnClientEvent_JumpToNextSystemInRouteCmdExecuted(self):
        self.invoke()


class UndockingStarted(Event):
    atom_id = 157
    __notifyevents__ = ['OnClientEvent_UndockingStarted']

    def OnClientEvent_UndockingStarted(self, *args):
        self.invoke()


class UndockingCompleted(Event):
    atom_id = 158
    __notifyevents__ = ['OnClientEvent_UndockingFinished']

    def OnClientEvent_UndockingFinished(self, itemID):
        self.invoke()


class UndockingAborted(Event):
    atom_id = 310
    __notifyevents__ = ['OnClientEvent_UndockingAborted']

    def OnClientEvent_UndockingAborted(self, itemID):
        self.invoke()


class BallparkLoaded(Event):
    atom_id = 228
    __notifyevents__ = ['DoBallsAdded']

    def DoBallsAdded(self, *args, **kwargs):
        StartTasklet(self.invoke)


class WarpActive(Event):
    atom_id = 88
    __notifyevents__ = ['OnWarpActive']

    def OnWarpActive(self, item_id, type_id):
        self.invoke(item_id=item_id, type_id=type_id)


class WarpArrived(Event):
    atom_id = 89
    __notifyevents__ = ['OnWarpArrived']

    def OnWarpArrived(self, item_id, type_id):
        self.invoke(item_id=item_id, type_id=type_id)


class WarpFinished(Event):
    atom_id = 90
    __notifyevents__ = ['OnClientEvent_WarpFinished']

    def OnClientEvent_WarpFinished(self, item_id, type_id):
        self.invoke(item_id=item_id, type_id=type_id)


class WarpStarted(Event):
    atom_id = 91
    __notifyevents__ = ['OnClientEvent_WarpStarted']

    def OnClientEvent_WarpStarted(self, item_id, type_id):
        self.invoke(item_id=item_id, type_id=type_id)
