#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\mouseInputHandler.py


class MouseInputHandler(object):
    __notifyevents__ = ['OnCameraZoomModifierChanged']

    def __init__(self):
        self.SetZoomModifier()
        sm.RegisterNotify(self)

    def GetCameraZoomModifier(self):
        return self.cameraZoomModifier

    def OnCameraZoomModifierChanged(self):
        self.SetZoomModifier()

    def SetZoomModifier(self):
        invertCameraZoom = settings.user.ui.Get('invertCameraZoom', False)
        if invertCameraZoom:
            self.cameraZoomModifier = -1
        else:
            self.cameraZoomModifier = 1
