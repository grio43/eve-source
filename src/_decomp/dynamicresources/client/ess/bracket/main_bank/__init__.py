#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\main_bank\__init__.py
import contextlib
import math
import signals
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from dynamicresources.client.ess.bracket.main_bank.hacking import Hacking
from dynamicresources.client.ess.bracket.main_bank.idle import Idle
from dynamicresources.client.ess.bracket.state_machine import StateMachine
from dynamicresources.client.ess.bracket.panel import BracketPanel, get_absolute_bounds, Priority
from dynamicresources.client.ess.bracket.tether import BracketTether
from dynamicresources.client.ess.bracket.transform import BankPanelTransformController, BankTransformSide
from dynamicresources.client.service import get_dynamic_resource_service

class MainBank(BracketPanel):

    def __init__(self, parent, camera, ess_root_transform, on_focus = None):
        self._camera = camera
        self._ess_root_transform = ess_root_transform
        self._watch_token = None
        self._state_machine = StateMachine()
        self._main_bank_transform = BankPanelTransformController(root=ess_root_transform, camera=camera, side=BankTransformSide.left, offset_y=2500.0, radius=800.0)
        super(MainBank, self).__init__(name='ess_main_bank', transform=self._main_bank_transform.transform, layer=parent, camera=camera, collapse_at_camera_distance=100000.0, clipping_dead_zone=50, on_focus=on_focus, collapsed=True)
        self.playerRequestedCollapseToken = None
        self._base = ContainerAutoSize(name='ess_main_bank', alignMode=uiconst.CENTERRIGHT)
        self._main_content = ContainerAutoSize(parent=self._base, align=uiconst.CENTERRIGHT, alignMode=uiconst.TOPRIGHT, left=120)
        self._content = ContainerAutoSize(parent=self._main_content, align=uiconst.TOPRIGHT, alignMode=uiconst.TOPLEFT, state=uiconst.UI_DISABLED if self.is_collapsed else uiconst.UI_PICKCHILDREN, left=-20 if self.is_collapsed else 0, opacity=0.0 if self.is_collapsed else 1.0)
        self._content_tracker_token = self.tracker.add(self._base, anchor=(1.0, 0.0), offset=(0, -16))
        tether_cont = Transform(name='ess_main_bank_tether', rotation=math.radians(180.0), width=100, height=30)
        self._tether = BracketTether(parent=tether_cont, align=uiconst.TOPLEFT, collapsed=True, on_click=self._on_tether_click, on_close_point_click=self._on_close_point_click)
        self.tracker.add(tether_cont, anchor=(1.0, 0.5))
        self._on_main_bank_state_update()

    @property
    def camera(self):
        return self._camera

    @property
    def ess_root_transform(self):
        return self._ess_root_transform

    @property
    def content_bounds(self):
        return get_absolute_bounds(self._main_content)

    @property
    def content(self):
        return self._content

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
        self._main_content.DisableAutoSize()
        self._content.state = uiconst.UI_DISABLED
        self._tether.collapse(lock=lock)
        animations.MorphScalar(self._content, 'left', startVal=self._content.left, endVal=-20, duration=0.2)
        animations.FadeOut(self._content, duration=0.2, callback=self._main_content.EnableAutoSize)

    def expand(self):
        self._tether.expand()
        self._content.state = uiconst.UI_PICKCHILDREN
        animations.MorphScalar(self._content, 'left', startVal=self._content.left, endVal=0, duration=0.2, timeOffset=0.2, callback=self._main_content.EnableAutoSize)
        animations.FadeIn(self._content, duration=0.2, timeOffset=0.2)

    def close(self):
        self._state_machine.close()
        self._base.Close()
        self._tether.parent.Close()
        self._watch_token = None
        self._main_bank_transform.close()
        super(MainBank, self).close()

    def _on_tether_click(self):
        if self.playerRequestedCollapseToken:
            self.playerRequestedCollapseToken.clear()
        self.force_expand()

    def _on_close_point_click(self):
        self.playerRequestedCollapseToken = self.request_collapse(Priority.control_point)

    def _on_main_bank_state_update(self, link = None):
        service = get_dynamic_resource_service()
        link, self._watch_token = service.ess_state_provider.select(callback=self._on_main_bank_state_update, lens=lambda s: s.main_bank.link)
        if link is None:
            self.unfocus()
            self._state_machine.move_to(Idle(self))
        elif link:
            if link.character_id == session.charid:
                self.focus()
            self._state_machine.move_to(Hacking(self, link))


from dynamicresources.client.ess.bracket.debug import __reload_update__
