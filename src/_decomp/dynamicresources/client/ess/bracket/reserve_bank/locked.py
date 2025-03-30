#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\reserve_bank\locked.py
import signals
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from dynamicresources.client import text
from dynamicresources.client.ess.bracket.label import Header
from dynamicresources.client.ess.bracket.reserve_bank.key_select import KeySelect
from dynamicresources.client.ess.bracket.state_machine import State, StateMachine, Transition

class Idle(State):

    def __init__(self, panel):
        super(Idle, self).__init__()
        self._panel = panel
        self._content = None
        self._state_machine = StateMachine()

    def enter(self):
        self._state_machine.move_to(Initial(parent=self._panel.content, on_unlock=self._on_unlock))

    def exit(self):
        self._state_machine.move_to(None)
        self._panel.unfocus()

    def close(self):
        self._state_machine.close()

    def _on_unlock(self):
        self._panel.focus()
        self._state_machine.move_to(KeySelect(parent=self._panel.content, on_cancel=self._on_cancel_key_select))

    def _on_cancel_key_select(self):
        self._panel.unfocus()
        self._state_machine.move_to(Initial(parent=self._panel.content, on_unlock=self._on_unlock))


class Initial(State):

    def __init__(self, parent, on_unlock = None):
        super(Initial, self).__init__()
        self._parent = parent
        self._content = None
        self._label = None
        self._button = None
        self.on_unlock = signals.Signal()
        if on_unlock:
            self.on_unlock.connect(on_unlock)

    def enter(self):
        self._content = ContainerAutoSize(parent=self._parent)
        self._label = Header(parent=self._content, align=uiconst.TOPLEFT, text=text.title_reserve_bank())
        self._button = Button(parent=self._content, align=uiconst.TOPLEFT, top=30, label=text.action_unlock_reserve_bank(), func=self._unlock, args=())
        animations.FadeTo(self._content, duration=0.2)

    def exit(self):
        animations.FadeOut(self._button, duration=0.15)
        transition = Exit(self._content, self._label)
        self._content = None
        return transition

    def close(self):
        if self._content:
            self._content.Close()

    def _unlock(self):
        self._button.Disable()
        self.on_unlock()


class Exit(Transition):

    def __init__(self, content, label):
        super(Exit, self).__init__()
        self._content = content
        self._label = label

    def animation(self):
        animations.FadeOut(self._label, duration=0.15)
        animations.MorphScalar(self._label, 'top', startVal=self._label.top, endVal=-10, duration=0.15)
        self.sleep(0.15)

    def close(self):
        self._content.Close()


from dynamicresources.client.ess.bracket.debug import __reload_update__
