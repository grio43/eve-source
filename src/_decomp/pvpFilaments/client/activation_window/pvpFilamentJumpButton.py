#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pvpFilaments\client\activation_window\pvpFilamentJumpButton.py
import threadutils
import eveui
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.shared.industry.submitButton import PrimaryButton
from .errorTooltipPanel import ErrorTooltipPanel

class PVPFilamentJumpButton(PrimaryButton):

    def ApplyAttributes(self, attributes):
        super(PVPFilamentJumpButton, self).ApplyAttributes(attributes)
        self._error_icon = eveui.Sprite(parent=self, align=eveui.Align.center_left, texturePath='res:/UI/Texture/classes/Agency/iconExclamation.png', color=(1, 0, 0, 0.6), height=20, width=20, left=4)
        self.controller = attributes.controller
        self.UpdateState()
        self.controller.onChange.connect(self.UpdateState)

    def IsActive(self):
        return self.controller.isReady or self.controller.isActivating or self.controller.isInQueue

    def IsBlinking(self):
        return self.controller.isActivating

    def IsErrorPresent(self):
        return bool(self.controller.errors) and not self.controller.isReady

    def GetColor(self):
        if self.IsErrorPresent():
            return Color.RED
        else:
            return sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)

    def UpdateBlinkByState(self):
        pass

    def UpdateIsEnabledByState(self):
        if self.controller.isReady:
            self.Enable()
        else:
            self.Disable()

    def UpdateState(self):
        super(PVPFilamentJumpButton, self).UpdateState()
        super(PVPFilamentJumpButton, self).UpdateBlinkByState()
        uicore.uilib.tooltipHandler.RefreshTooltipForOwner(self)
        if self.controller.errors:
            self.errorFrame.Show()
            self._error_icon.Show()
        else:
            self._error_icon.Hide()

    @threadutils.throttled(4.0)
    def ClickFunc(self, *args):
        if self.controller.isInQueue:
            self.controller.LeaveQueue()
            self.UpdateLabel()
        else:
            self.controller.JoinQueue()

    def LoadTooltipPanel(self, panel, *args):
        if not self.controller.isFinished:
            ErrorTooltipPanel(panel, self.controller.displayed_errors)

    def GetText(self):
        return self.controller.GetText()
