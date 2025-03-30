#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\statefulButton.py
from carbonui.control.button import Button
from eve.client.script.ui.const import buttonConst
from signals.signalUtil import ChangeSignalConnect

class StatefulButton(Button):
    default_iconSize = 24
    default_name = 'StatefulButton'

    def ApplyAttributes(self, attributes):
        self.controller = attributes.get('controller', None)
        self.UpdateVisibility = attributes.get('UpdateVisibility', None)
        super(StatefulButton, self).ApplyAttributes(attributes)
        if self.controller:
            self.ChangeSignalConnect()
            self.UpdateState()

    def ChangeSignalConnect(self, connect = True):
        if not self.controller:
            return
        signalAndCallback = [(self.controller.onNewState, self.UpdateState), (self.controller.onSetBusy, self.SetBusy)]
        ChangeSignalConnect(signalAndCallback, connect)

    def UpdateState(self, state = None):
        if not self.controller:
            return
        buttonState = self.controller.GetButtonState() if not state else state
        if not buttonState:
            return
        if buttonState == buttonConst.STATE_NONE:
            self.Hide()
            return
        self.Show()
        if self.UpdateVisibility:
            self.UpdateVisibility()
        if buttonState in buttonConst.BUTTON_DISABLED_STATES or not self.controller.IsButtonEnabled():
            self.Disable()
            self.SetHint(self.controller.GetDisabledHint())
        else:
            self.Enable()
        if buttonState in buttonConst.ACTIVE_BUTTON_STATES:
            self.SetBusy(buttonState)
        else:
            self.SetActive()
            self.texturePath = self.controller.GetButtonTexturePath()
        self.SetFunc(self.controller.GetButtonFunction())
        self.SetLabel(self.controller.GetButtonLabel())

    def OnClick(self, *args):
        super(StatefulButton, self).OnClick(*args)
        self.UpdateState()

    def SetController(self, controller):
        if self.controller == controller:
            return
        self.controller = controller
        self.ChangeSignalConnect()
        self.UpdateState()

    def Disable(self):
        if self.controller.buttonState == buttonConst.STATE_NONE:
            return
        super(StatefulButton, self).Disable()

    def Enable(self):
        if self.controller.buttonState == buttonConst.STATE_NONE:
            return
        super(StatefulButton, self).Enable()

    def SetBusy(self, buttonState):
        if self.busy:
            return
        if buttonState != buttonConst.STATE_UNDOCKING:
            self.Disable()
        self.texturePath = None
        self.busy = True

    def SetActive(self):
        if not self.busy:
            return
        self.Enable()
        self.busy = False
        self.texturePath = self.controller.GetButtonTexturePath()

    def Close(self):
        self.ChangeSignalConnect(connect=False)
        super(StatefulButton, self).Close()
