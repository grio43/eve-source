#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\reserve_bank\__init__.py
import contextlib
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from dynamicresources.client.ess.bracket.panel import BracketPanel, get_absolute_bounds, Priority
from dynamicresources.client.ess.bracket.reserve_bank.locked import Idle
from dynamicresources.client.ess.bracket.reserve_bank.unlocked import Unlocked
from dynamicresources.client.ess.bracket.state_machine import StateMachine
from dynamicresources.client.ess.bracket.tether import BracketTether
from dynamicresources.client.ess.bracket.transform import BankPanelTransformController, BankTransformSide
from dynamicresources.client.service import get_dynamic_resource_service

class ReserveBank(BracketPanel):

    def __init__(self, parent, camera, ess_root_transform, on_focus = None):
        self._camera = camera
        self._ess_root_transform = ess_root_transform
        self._watch_token = None
        self._state_machine = StateMachine()
        self._panel_transform = BankPanelTransformController(root=ess_root_transform, camera=camera, side=BankTransformSide.right, offset_y=-2000.0, radius=800.0)
        super(ReserveBank, self).__init__(name='ess_reserve_bank', transform=self._panel_transform.transform, layer=parent, camera=camera, clipping_dead_zone=50, collapse_at_camera_distance=100000.0, on_focus=on_focus, collapsed=True)
        self.playerRequestedCollapseToken = None
        self._base = ContainerAutoSize(name='ess_reserve_bank', alignMode=uiconst.TOPLEFT)
        self._content_bounds = ContainerAutoSize(parent=self._base, align=uiconst.TOPLEFT, alignMode=uiconst.TOPLEFT, left=120)
        self._content = ContainerAutoSize(parent=self._content_bounds, align=uiconst.TOPLEFT, alignMode=uiconst.TOPLEFT, state=uiconst.UI_DISABLED if self.is_collapsed else uiconst.UI_PICKCHILDREN, left=-20 if self.is_collapsed else 0, opacity=0.0 if self.is_collapsed else 1.0)
        self._content_tracker_token = self.tracker.add(self._base, anchor=(0.0, 0.0), offset=(0, -16))
        self._tether = BracketTether(name='ess_reserve_bank_tether', parent=self._base, align=uiconst.CENTERLEFT, on_click=self._on_tether_click, on_close_point_click=self._on_close_point_click, collapsed=True)
        self.tracker.add(self._tether, anchor=(0.0, 0.5))
        self._on_state_update()

    @property
    def content(self):
        return self._content

    @property
    def content_bounds(self):
        return get_absolute_bounds(self._content_bounds)

    @property
    def camera(self):
        return self._camera

    @property
    def ess_root_transform(self):
        return self._ess_root_transform

    @property
    def content_anchor(self):
        return self._content_tracker_token.anchor

    @content_anchor.setter
    def content_anchor(self, anchor):
        self._content_tracker_token.anchor = anchor

    @property
    def content_offset(self):
        return self._content_tracker_token.offset

    @content_offset.setter
    def content_offset(self, offset):
        self._content_tracker_token.offset = offset

    @contextlib.contextmanager
    def tracking_override(self, anchor = None, offset = None):
        if anchor is None:
            anchor = self.content_anchor
        if offset is None:
            offset = self.content_offset
        old_anchor = self.content_anchor
        old_offset = self.content_offset
        self.content_anchor = anchor
        self.content_offset = offset
        try:
            yield
        finally:
            self.content_anchor = old_anchor
            self.content_offset = old_offset

    def collapse(self, lock = False):
        self._tether.collapse(lock=lock)
        self._content.state = uiconst.UI_DISABLED
        animations.MorphScalar(self._content, 'left', startVal=self._content.left, endVal=-20, duration=0.2, callback=self._content.DisableAutoSize)
        animations.FadeOut(self._content, duration=0.2)

    def expand(self):
        self._tether.expand()
        self._content.state = uiconst.UI_PICKCHILDREN
        animations.MorphScalar(self._content, 'left', startVal=self._content.left, endVal=0, duration=0.2, timeOffset=0.2, callback=self._content.EnableAutoSize)
        animations.FadeIn(self._content, duration=0.2, timeOffset=0.2)

    def close(self):
        self._panel_transform.close()
        self._state_machine.close()
        self._base.Close()
        self._tether.close()
        super(ReserveBank, self).close()

    def _on_tether_click(self):
        if self.playerRequestedCollapseToken:
            self.playerRequestedCollapseToken.clear()
        self.force_expand()

    def _on_close_point_click(self):
        self.playerRequestedCollapseToken = self.request_collapse(Priority.control_point)

    def _on_state_update(self, state = None):
        service = get_dynamic_resource_service()
        unlocked, self._watch_token = service.ess_state_provider.select(callback=self._on_state_update, lens=lambda s: s.reserve_bank.unlocked)
        if unlocked:
            self._state_machine.move_to(Unlocked(self))
        else:
            self._state_machine.move_to(Idle(self))


from dynamicresources.client.ess.bracket.debug import __reload_update__
