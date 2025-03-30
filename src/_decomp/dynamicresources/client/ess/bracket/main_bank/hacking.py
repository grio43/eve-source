#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\main_bank\hacking.py
import eveui
import gametime
import uthread2
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from dynamicresources.common.ess.const import LINK_ERROR_LINK_OCCUPIED
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from dynamicresources.client import text
from dynamicresources.client.ess.bracket.label import Header
from dynamicresources.client.ess.bracket.notification import COLOR_ALERT, COLOR_SUCCESS, COLOR_WARN, ICON_ALERT, ICON_SUCCESS, ICON_WARN, TransitionNotification
from dynamicresources.client.ess.bracket.state_machine import State, Transition
from dynamicresources.client.service import get_dynamic_resource_service

class Hacking(State):

    def __init__(self, panel, link_state):
        self.panel = panel
        self._link_id = link_state.link_id
        self._link_state = link_state
        self.content = None
        self.state_token = None

    @property
    def link_state(self):
        service = get_dynamic_resource_service()
        link_state = service.ess_state_provider.state.main_bank.link
        if link_state is not None:
            self._link_state = link_state
        return self._link_state

    def close(self):
        if self.content:
            self.content.Close()
        if self.state_token:
            self.state_token.clear()

    def enter(self):
        self.content = ContainerAutoSize(parent=self.panel.content, align=uiconst.TOPLEFT)
        if session.charid != self.link_state.character_id:

            def display_link_error():
                message = text.link_error_description(LINK_ERROR_LINK_OCCUPIED)
                if message is not None:
                    uicore.Message('CustomNotify', {'notify': message})

            Header(parent=self.content, align=uiconst.TOPRIGHT, text=text.title_main_bank())
            self._button = Button(parent=self.content, align=uiconst.TOPRIGHT, top=30, label=text.action_hack_main_bank(), func=display_link_error, args=())

            def on_state_token(token):
                if self.state_token:
                    self.state_token.clear()
                self.state_token = token

            return EnterSomeoneElseIsHacking(self.panel, self.content, on_state_token)
        else:
            return EnterThisClientIsHacking(self.panel, self.content)

    def exit(self):
        self.panel.clear_force_collapse()
        transition = HackResultTransition(self._link_id, self.panel, self.content)
        self.content = None
        return transition


class EnterThisClientIsHacking(Transition):

    def __init__(self, panel, content):
        super(EnterThisClientIsHacking, self).__init__()
        self.panel = panel
        self.content = content
        self._button = None

    def animation(self):
        with self.panel.tracking_override(anchor=(1.0, 0.5), offset=(0, 0)):
            notification = TransitionNotification(parent=self.content, align=uiconst.TOPRIGHT, text=text.main_bank_hack_initiated(), iconHexColor=COLOR_WARN, icon=ICON_WARN)
            notification.show()
            self.sleep(2.0, interruptable=False)
            notification.hide(close=True)
            self.sleep(0.3, interruptable=False)
        Header(parent=self.content, align=uiconst.TOPRIGHT, text=text.title_main_bank())
        self._button = Button(parent=self.content, align=uiconst.TOPRIGHT, top=30, label=text.action_disconnect_main_bank(), func=self._unlink, args=())
        animations.FadeTo(self.content, duration=0.3)
        self.sleep(1.0)
        self.panel.force_collapse()

    def _unlink(self):
        self._button.Disable()
        try:
            service = get_dynamic_resource_service()
            service.RequestESSMainBankUnlink()
            uthread2.sleep(1.0)
        finally:
            if not self._button.destroyed:
                self._button.Enable()


class EnterSomeoneElseIsHacking(Transition):

    def __init__(self, panel, content, on_state_token):
        super(EnterSomeoneElseIsHacking, self).__init__()
        self.panel = panel
        self.content = content
        self.on_state_token = on_state_token

    def animation(self):
        self.on_state_token(self.panel.force_collapse())


class HackResultTransition(Transition):

    def __init__(self, link_id, panel, content):
        super(HackResultTransition, self).__init__()
        self.link_id = link_id
        self.panel = panel
        self.content = content

    def animation(self):
        animations.FadeOut(self.content, duration=0.3)
        self.sleep(0.32)
        self.content.Flush()
        self.content.opacity = 1.0
        with self.panel.tracking_override(anchor=(1.0, 0.5), offset=(0, 0)):
            wheel = LoadingWheel(parent=self.content, align=uiconst.TOPRIGHT, width=32, height=32, opacity=0.0)
            animations.FadeIn(wheel, duration=1.0, timeOffset=1.0)
            link_result = self._wait_for_link_result(self.link_id, timeout=10.0)
            animations.FadeOut(wheel, duration=0.3, callback=wheel.Close)
            if link_result is None:
                self.sleep(0.3, interruptable=False)
                return
            if link_result.character_id == session.charid:
                icon = None
                iconColor = None
                if link_result.successful:
                    icon = ICON_SUCCESS
                    iconColor = COLOR_SUCCESS
                    feedback_text = text.main_bank_hack_successful()
                else:
                    icon = ICON_ALERT
                    iconColor = COLOR_ALERT
                    feedback_text = text.main_bank_disconnected()
                feedback = TransitionNotification(parent=self.content, align=uiconst.TOPRIGHT, text=feedback_text, iconHexColor=iconColor, icon=icon)
                feedback.show()
                self.sleep(3.0, interruptable=False)
                feedback.hide()
                self.sleep(0.3, interruptable=False)

    def on_close(self):
        self.content.Close()

    def _wait_for_link_result(self, link_id, timeout):
        service = get_dynamic_resource_service()
        link_result = service.ess_state_provider.state.main_bank.link_result
        start = gametime.now()
        while link_result is None or link_result.link_id != link_id:
            if self.is_stopped or (gametime.now() - start).total_seconds() > timeout:
                return
            eveui.wait_for_next_frame()
            link_result = service.ess_state_provider.state.main_bank.link_result

        return link_result


from dynamicresources.client.ess.bracket.debug import __reload_update__
