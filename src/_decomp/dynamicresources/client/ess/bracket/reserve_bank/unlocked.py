#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\reserve_bank\unlocked.py
import locks
import threadutils
import uthread2
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from dynamicresources.client import text
from dynamicresources.client.ess.bracket.label import Header
from dynamicresources.client.ess.bracket.notification import COLOR_ALERT, COLOR_WARN, ICON_ALERT, ICON_WARN, TransitionNotification
from dynamicresources.client.ess.bracket.state_machine import State, StateMachine, Transition
from dynamicresources.client.service import get_dynamic_resource_service

class Unlocked(State):

    def __init__(self, panel):
        super(Unlocked, self).__init__()
        self._panel = panel
        self._watch_token = None
        self._state_machine = StateMachine()

    def enter(self):
        self._on_state_update()

    def exit(self):
        self._panel.clear_force_collapse()
        self._panel.unfocus()

    def close(self):
        if self._state_machine:
            self._state_machine.close()

    def _on_state_update(self, *args):
        service = get_dynamic_resource_service()
        linked, self._watch_token = service.ess_state_provider.select(callback=self._on_state_update, lens=lambda s: s.reserve_bank.linked)
        if linked:
            self._panel.focus()
            self._state_machine.move_to(Linked(self._panel))
        else:
            self._panel.unfocus()
            self._state_machine.move_to(Unlinked(self._panel))


class Unlinked(State):

    def __init__(self, panel):
        self._panel = panel
        self._content = None
        self._button = None

    def enter(self):
        self._content = ContainerAutoSize(parent=self._panel.content)
        animations.FadeTo(self._content, duration=0.3)
        Header(parent=self._content, align=uiconst.TOPLEFT, text=text.title_reserve_bank())
        self._button = Button(parent=self._content, align=uiconst.TOPLEFT, top=30, label=text.action_link_to_reserve_bank(), func=self._link, args=())

    def close(self):
        self._content.Close()

    @locks.SingletonCall
    @threadutils.threaded
    def _link(self):
        self._button.Disable()
        try:
            service = get_dynamic_resource_service()
            error = service.RequestESSReserveBankLink()
            if error is not None:
                message = text.link_error_description(error)
                if message is not None:
                    uicore.Message('CustomNotify', {'notify': message})
            uthread2.sleep(1.0)
        finally:
            if not self._button.destroyed:
                self._button.Enable()


class Linked(State):

    def __init__(self, panel):
        self._panel = panel
        self._content = None
        self._button = None

    def enter(self):
        self._content = ContainerAutoSize(parent=self._panel.content)
        return Link(self._content, self._panel)

    def exit(self):
        transition = Unlink(self._panel, self._content)
        self._content = None
        return transition

    def close(self):
        if self._content:
            self._content.Close()


class Link(Transition):

    def __init__(self, content, panel):
        super(Link, self).__init__()
        self.content = content
        self.panel = panel
        self._button = None

    def animation(self):
        notification = TransitionNotification(parent=self.content, align=uiconst.TOPLEFT, text=text.reserve_bank_linked(), iconHexColor=COLOR_WARN, icon=ICON_WARN)
        notification.show()
        self.sleep(2.0, interruptable=False)
        notification.hide(close=True)
        self.sleep(0.3, interruptable=False)
        animations.FadeTo(self.content, duration=0.3, callback=self.panel.force_collapse)
        Header(parent=self.content, align=uiconst.TOPLEFT, text=text.title_reserve_bank())
        self._button = Button(parent=self.content, align=uiconst.TOPLEFT, top=30, label=text.action_unlink_from_reserve_bank(), func=self._unlink, args=())

    @locks.SingletonCall
    @threadutils.threaded
    def _unlink(self):
        self._button.Disable()
        try:
            service = get_dynamic_resource_service()
            service.RequestESSReserveBankUnlink()
        finally:
            uthread2.sleep(1.0)
            if not self._button.destroyed:
                self._button.Enable()


class Unlink(Transition):

    def __init__(self, panel, content):
        super(Unlink, self).__init__()
        self.panel = panel
        self.content = content

    def animation(self):
        animations.FadeOut(self.content, duration=0.3)
        self.sleep(0.31)
        self.content.Flush()
        self.content.opacity = 1.0
        with self.panel.tracking_override(anchor=(0.0, 0.5), offset=(0, 0)):
            notification = TransitionNotification(parent=self.content, align=uiconst.TOPLEFT, text=text.reserve_bank_unlinked(), iconHexColor=COLOR_ALERT, icon=ICON_ALERT)
            notification.show()
            self.sleep(2.0, interruptable=False)
            notification.hide(close=True)
            self.sleep(0.3, interruptable=False)
        self.panel.clear_force_collapse()

    def on_close(self):
        self.content.Close()


from dynamicresources.client.ess.bracket.debug import __reload_update__
