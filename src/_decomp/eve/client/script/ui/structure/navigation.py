#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\navigation.py
import evecamera
import carbonui.const as uiconst
from carbonui.uicore import uicore
from carbonui.control.layer import LayerCore
from eve.client.script.ui.camera.structureCameraController import StructureCameraController
from eveservices.menu import GetMenuService

class StructureLayer(LayerCore):
    __notifyevents__ = ['OnActiveCameraChanged']
    __guid__ = 'uicls.StructureLayer'

    def __init__(self, *args, **kwargs):
        self.cameraController = None
        LayerCore.__init__(self, *args, **kwargs)

    def OnOpenView(self, **kwargs):
        sm.GetService('sceneManager').SetPrimaryCamera(evecamera.CAM_STRUCTURE)
        self.OnActiveCameraChanged(evecamera.CAM_SHIPORBIT)

    def OnActiveCameraChanged(self, cameraID):
        if cameraID == evecamera.CAM_STRUCTURE:
            self.cameraController = StructureCameraController()

    def OnMouseDown(self, *args):
        if self.cameraController:
            self.cameraController.OnMouseDown(*args)
        if uicore.uilib.leftbtn:
            self.SetCursor(uiconst.UICURSOR_DRAGGABLE, True)

    def OnMouseUp(self, button, *args):
        if self.cameraController:
            self.cameraController.OnMouseUp(button, *args)
        if not uicore.uilib.leftbtn:
            self.SetCursor(None, False)

    def OnMouseMove(self, *args):
        if uicore.IsDragging():
            return
        if self.cameraController:
            self.cameraController.OnMouseMove(*args)

    def OnMouseWheel(self, *args):
        if self.cameraController:
            self.cameraController.OnMouseWheel(*args)

    def OnDblClick(self, *args):
        uicore.cmd.GetCommandAndExecute('OpenInventory')

    def GetMenu(self):
        return GetMenuService().CelestialMenu(session.structureid)

    def SetCursor(self, cursor, clip):
        self.cursor = cursor
        if clip:
            uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
            uicore.uilib.SetCapture(self)
        else:
            uicore.uilib.UnclipCursor()
            if uicore.uilib.GetCapture() == self:
                uicore.uilib.ReleaseCapture()
