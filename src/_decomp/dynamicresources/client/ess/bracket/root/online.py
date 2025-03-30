#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\root\online.py
import threadutils
from dynamicresources.client.ess.bracket.main_bank import MainBank
from dynamicresources.client.ess.bracket.main_bank.timer import HackingTimer
from dynamicresources.client.ess.bracket.panel import Priority
from dynamicresources.client.ess.bracket.reserve_bank import ReserveBank
from dynamicresources.client.ess.bracket.reserve_bank.timer import ReserveBankTimer
from dynamicresources.client.ess.bracket.root.status import OutOfRange
from dynamicresources.client.ess.bracket.state_machine import State, StateMachine

class Online(State):

    def __init__(self, bracket):
        self._bracket = bracket
        self._main_bank_timer = None
        self._reserve_bank_timer = None
        self._ess_state_watch_token = None
        self._state_machine = StateMachine()

    def enter(self):
        self._on_ess_state_change()

    def close(self):
        if self._main_bank_timer:
            self._close_timer(self._main_bank_timer)
            self._main_bank_timer = None
        if getattr(self, '_reserve_bank_timer', None):
            self._close_timer(self._reserve_bank_timer)
            self._reserve_bank_timer = None
        if self._ess_state_watch_token:
            self._ess_state_watch_token.unsubscribe()
        self._state_machine.close()

    def _on_ess_state_change(self, state = None):
        state, self._ess_state_watch_token = self._bracket.ess_state_provider.select(self._on_ess_state_change, lens=EssStateSubset.from_ess_state)
        if state.in_range:
            self._state_machine.move_to(InRange(self._bracket))
        else:
            self._state_machine.move_to(OutOfRange(self._bracket))
        if state.main_bank_active:
            if not self._main_bank_timer:
                self._main_bank_timer = HackingTimer(camera=self._bracket.camera, ess_root_transform=self._bracket.ess_root.transform, link_state=self._bracket.ess_state_provider.state.main_bank.link, radius=488, line_width=42, offset_y=3600, scale=5000)
                self._main_bank_timer.play_enter_animation()
        elif self._main_bank_timer:
            self._close_timer(self._main_bank_timer)
            self._main_bank_timer = None
        if state.reserve_bank_active:
            if not self._reserve_bank_timer:
                self._reserve_bank_timer = ReserveBankTimer(camera=self._bracket.camera, ess_root_transform=self._bracket.ess_root.transform, offset_y=-2000, scale=5000)
                self._reserve_bank_timer.play_enter_animation()
        elif self._reserve_bank_timer:
            self._close_timer(self._reserve_bank_timer)
            self._reserve_bank_timer = None

    @threadutils.threaded
    def _close_timer(self, timer):
        timer.play_exit_animation(sleep=True)
        timer.close()


class EssStateSubset(object):

    def __init__(self, in_range, main_bank_active, reserve_bank_active):
        self.in_range = in_range
        self.main_bank_active = main_bank_active
        self.reserve_bank_active = reserve_bank_active

    @staticmethod
    def from_ess_state(state):
        return EssStateSubset(in_range=state.in_range, main_bank_active=state.main_bank.link is not None, reserve_bank_active=state.reserve_bank.unlocked)


class InRange(State):

    def __init__(self, bracket):
        self._bracket = bracket
        self._main_bank_panel = None
        self._main_bank_state_token = None
        self._main_bank_timer = None
        self._reserve_bank_panel = None
        self._reserve_bank_state_token = None
        self._ess_state_watch_token = None

    def enter(self):
        self._main_bank_panel = MainBank(parent=self._bracket.layer, camera=self._bracket.camera, ess_root_transform=self._bracket.ess_root)
        self._reserve_bank_panel = ReserveBank(parent=self._bracket.layer, camera=self._bracket.camera, ess_root_transform=self._bracket.ess_root)
        self._main_bank_panel.on_focus.connect(self._on_panel_focus)
        self._reserve_bank_panel.on_focus.connect(self._on_panel_focus)
        self._update_panel_collapse_state()

    def close(self):
        self._main_bank_panel.close()
        self._reserve_bank_panel.close()
        if self._main_bank_state_token:
            self._main_bank_state_token.clear()
        if self._reserve_bank_state_token:
            self._reserve_bank_state_token.clear()
        if self._ess_state_watch_token:
            self._ess_state_watch_token.unsubscribe()

    def _update_panel_collapse_state(self):
        if self._main_bank_state_token:
            self._main_bank_state_token.clear()
            self._main_bank_state_token = None
        if self._reserve_bank_state_token:
            self._reserve_bank_state_token.clear()
            self._reserve_bank_state_token = None
        if self._main_bank_panel.focused:
            self._reserve_bank_state_token = self._reserve_bank_panel.request_collapse(Priority.no_content, lock=True)
        if self._reserve_bank_panel.focused:
            self._main_bank_state_token = self._main_bank_panel.request_collapse(Priority.no_content, lock=True)

    def _on_panel_focus(self, _focused):
        self._update_panel_collapse_state()


from dynamicresources.client.ess.bracket.debug import __reload_update__
