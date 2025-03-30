#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\underConstruction\underConstructionStates.py
from carbonui.primitives.containerAutoSize import ContainerAutoSize
import threadutils
import uthread2
import carbonui.const as uiconst
from carbonui.uianimations import animations
from dynamicresources.client.ess.bracket.state_machine import State, StateMachine, Transition
from spacecomponents.client.ui.underConstruction.bracketPanel import UnderConstructionBracketPanel
from spacecomponents.client.ui.underConstruction.underConstructionCont import UnderConstructionCont

class Online(State):

    def __init__(self, bracket):
        self._bracket = bracket
        self._state_machine = StateMachine()

    def enter(self):
        self._on_state_change()

    def close(self):
        self._state_machine.close()

    def _on_state_change(self):
        if self._bracket.root:
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
        self._content = ContainerAutoSize(name='idleCont', parent=self._panel.content, pos=(0, 0, 300, 170), align=uiconst.TOPLEFT)
        cont = UnderConstructionCont(parent=self._content, itemID=self._panel.item_id, typeID=self._panel.type_id)
        animations.FadeTo(self._content, duration=0.3)

    def exit(self):
        self._button.Disable()
        transition = Exit(self._content)
        self._content = None
        return transition

    def close(self):
        if self._content:
            self._content.Close()

    def Jump(self):
        self._button.Disable()
        try:
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


class InRange(State):
    __notifyevents__ = []

    def __init__(self, bracket):
        self._bracket = bracket
        self._underConstruction_panel = None

    def enter(self):
        self._underConstruction_panel = UnderConstructionBracketPanel(parent=self._bracket.layer, camera=self._bracket.camera, under_construction_root_transform=self._bracket.root, itemID=self._bracket.item_id, typeID=self._bracket.type_id)

    def close(self):
        self._underConstruction_panel.close()
