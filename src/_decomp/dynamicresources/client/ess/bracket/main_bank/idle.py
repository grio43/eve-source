#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\main_bank\idle.py
import uthread2
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from dynamicresources.client import text
from dynamicresources.client.ess.bracket.label import Header
from dynamicresources.client.ess.bracket.state_machine import State, Transition
from dynamicresources.client.service import get_dynamic_resource_service

class Idle(State):

    def __init__(self, panel):
        self._panel = panel
        self._content = None
        self._button = None

    def enter(self):
        self._content = ContainerAutoSize(parent=self._panel.content)
        Header(parent=self._content, align=uiconst.TOPRIGHT, text=text.title_main_bank())
        self._button = Button(parent=self._content, align=uiconst.TOPRIGHT, top=30, label=text.action_hack_main_bank(), func=self._link, args=())
        animations.FadeTo(self._content, duration=0.3)

    def exit(self):
        self._button.Disable()
        transition = Exit(self._content)
        self._content = None
        return transition

    def close(self):
        if self._content:
            self._content.Close()

    def _link(self):
        self._button.Disable()
        try:
            service = get_dynamic_resource_service()
            error = service.RequestESSMainBankLink()
            if error is not None:
                message = text.link_error_description(error)
                if message is not None:
                    uicore.Message('CustomNotify', {'notify': message})
            uthread2.sleep(1.0)
        finally:
            if not self._button.destroyed:
                self._button.Enable()


class Exit(Transition):

    def __init__(self, content):
        super(Exit, self).__init__()
        self._content = content

    def animation(self):
        animations.FadeOut(self._content, duration=0.2)
        self.sleep(0.2)

    def on_close(self):
        self._content.Close()


from dynamicresources.client.ess.bracket.debug import __reload_update__
