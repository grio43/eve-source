#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\shipFittingSimulationButton.py
import carbonui.const as uiconst
import uthread2
from carbonui.primitives.container import Container
from carbonui.control.buttonIcon import ButtonIcon

class ShipFittingSimulationButton(ButtonIcon):
    default_name = __name__
    default_texturePath = 'res:/UI/Texture/classes/Fitting/iconSimulatorToggle.png'
    default_hoverTexture = 'res:/UI/Texture/classes/Fitting/iconSimulatorHover.png'
    default_exitTexturePath = 'res:/UI/Texture/classes/Fitting/iconSimulatorExit.png'
    default_exitHoverTexturePath = 'res:/UI/Texture/classes/Fitting/iconSimulatorExitHover.png'
    default_width = 32
    default_height = 32
    default_iconSize = 32
    default_showGlow = True
    GLOWAMOUNT_MOUSECLICK = 1.5
    GLOWAMOUNT_MOUSEHOVER = 0.5

    def ApplyAttributes(self, attributes):
        self.default_func = self.ToggleGhostFittingForActiveShip
        super(ShipFittingSimulationButton, self).ApplyAttributes(attributes)
        self.fittingSvc = sm.GetService('fittingSvc')
        self.enableButtonThread = None

    def Close(self):
        self.KillEnableButtonThread()
        Container.Close(self)

    def ToggleGhostFittingForActiveShip(self, *args):
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        self.KillEnableButtonThread()
        self.state = uiconst.UI_DISABLED
        try:
            ghostFittingSvc.ToggleGhostFitting()
        finally:
            self.EnableButtonWithDelay()

    def EnableButtonWithDelay(self):
        self.KillEnableButtonThread()
        self.enableButtonThread = uthread2.call_after_wallclocktime_delay(self.EnableButton, 0.5)

    def EnableButton(self):
        self.state = uiconst.UI_NORMAL
        self.enableButtonThread = None

    def KillEnableButtonThread(self):
        if self.enableButtonThread:
            self.enableButtonThread.kill()
            self.enableButtonThread = None

    def ShowExitTextures(self):
        self.texturePath = self.default_exitTexturePath
        self.SetTexturePath(self.default_exitTexturePath)
        self.hoverTexture = self.default_exitHoverTexturePath

    def ShowDefaultTextures(self):
        self.texturePath = self.default_texturePath
        self.SetTexturePath(self.default_texturePath)
        self.hoverTexture = self.default_hoverTexture
