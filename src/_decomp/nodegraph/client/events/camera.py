#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\camera.py
from .base import Event

class CameraRotated(Event):
    atom_id = 41
    __notifyevents__ = ['OnClientMouseSpinInSpace']

    def OnClientMouseSpinInSpace(self):
        self.invoke()


class CameraZoomIn(Event):
    atom_id = 42
    __notifyevents__ = ['OnClientMouseZoomInSpace']

    def OnClientMouseZoomInSpace(self, amount):
        self.invoke()


class CameraZoomOut(Event):
    atom_id = 43
    __notifyevents__ = ['OnClientMouseZoomOutSpace']

    def OnClientMouseZoomOutSpace(self, amount):
        self.invoke()


class CameraLookAt(Event):
    atom_id = 44
    __notifyevents__ = ['OnCameraLookAt']

    def OnCameraLookAt(self, is_self, item_id):
        self.invoke(is_self=is_self, item_id=item_id)


class CameraLookAtSelf(Event):
    atom_id = 45
    __notifyevents__ = ['OnCameraLookAt']

    def OnCameraLookAt(self, is_self, item_id):
        if is_self:
            self.invoke()


class CameraLookAtObject(Event):
    atom_id = 46
    __notifyevents__ = ['OnCameraLookAt']

    def OnCameraLookAt(self, is_self, item_id):
        if not item_id:
            return
        self.invoke(item_id=item_id)


class CameraTrackingObject(Event):
    atom_id = 101
    __notifyevents__ = ['OnCameraTrack']

    def OnCameraTrack(self, item_id):
        if not item_id:
            return
        self.invoke(item_id=item_id)


class CameraTrackingStopped(Event):
    atom_id = 102
    __notifyevents__ = ['OnCameraTrack']

    def OnCameraTrack(self, item_id):
        if not item_id:
            self.invoke()
