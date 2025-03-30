#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\shipcaster\shipcasterStates.py
import threadutils
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.uianimations import animations
from dynamicresources.client.ess.bracket.state_machine import State, StateMachine, Transition
from spacecomponents.client.ui.shipcaster.launcherCont import LauncerCont
from spacecomponents.client.ui.shipcaster.bracketPanel import ShipcasterBracketPanel

class Online(State):

    def __init__(self, bracket):
        self._bracket = bracket
        self._state_machine = StateMachine()

    def enter(self):
        self._on_shipcaster_state_change()

    def close(self):
        self._state_machine.close()

    def _on_shipcaster_state_change(self):
        self._state_machine.move_to(InRange(self._bracket))

    @threadutils.threaded
    def _close_timer(self, timer):
        timer.play_exit_animation(sleep=True)
        timer.close()


class Idle(State):

    def __init__(self, panel):
        self._panel = panel
        self._content = None
        self._button = None

    def enter(self):
        self._content = Container(name='idleCont', parent=self._panel.content, pos=(0, 0, 300, 170), align=uiconst.TOPLEFT)
        cont = LauncerCont(parent=self._content, align=uiconst.TOBOTTOM, height=170, itemID=self._panel.item_id, typeID=self._panel.type_id)
        animations.FadeTo(self._content, duration=0.3)

    def exit(self):
        self._button.Disable()
        transition = Exit(self._content)
        self._content = None
        return transition

    def close(self):
        if self._content:
            self._content.Close()


class Exit(Transition):

    def __init__(self, content):
        super(Exit, self).__init__()
        self._content = content

    def animation(self):
        animations.FadeOut(self._content, duration=0.2)
        self.sleep(0.2)

    def on_close(self):
        self._content.Close()


class InRange(State):
    __notifyevents__ = []

    def __init__(self, bracket):
        self._bracket = bracket
        self._shipcaster_panel = None
        self._main_bank_state_token = None
        self._main_bank_timer = None
        self._reserve_bank_state_token = None

    def enter(self):
        self._shipcaster_panel = ShipcasterBracketPanel(parent=self._bracket.layer, camera=self._bracket.camera, shipcaster_root_transform=self._bracket.root, itemID=self._bracket.item_id, typeID=self._bracket.type_id)

    def close(self):
        self._shipcaster_panel.close()
