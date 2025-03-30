#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\shipcaster\bracketPanel.py
import math
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from dynamicresources.client.ess.bracket.state_machine import StateMachine
from dynamicresources.client.ess.bracket.panel import BracketPanel, get_absolute_bounds, Priority
from dynamicresources.client.ess.bracket.tether import BracketTether
from spacecomponents.client.ui.rootTransformController import PanelTransformController

class ShipcasterBracketPanel(BracketPanel):

    def __init__(self, parent, camera, shipcaster_root_transform, on_focus = None, itemID = None, typeID = None):
        self._camera = camera
        self._shipcaster_root_transform = shipcaster_root_transform
        self._state_machine = StateMachine()
        self._item_id = itemID
        self._type_id = typeID
        self.playerRequestedCollapseToken = None
        self._shipcaster_transform = PanelTransformController(root=shipcaster_root_transform, camera=camera, offset_y=5500.0)
        super(ShipcasterBracketPanel, self).__init__(name='ShipcasterBracketPanel', transform=self._shipcaster_transform.transform, layer=parent, camera=camera, collapse_at_camera_distance=150000.0, clipping_dead_zone=50, on_focus=on_focus, collapsed=True)
        self._base = ContainerAutoSize(name='ShipcasterUI_base', alignMode=uiconst.CENTERBOTTOM)
        self._main_content = ContainerAutoSize(name='_main_content', parent=self._base, align=uiconst.CENTERBOTTOM, alignMode=uiconst.CENTERBOTTOM)
        self._content = ContainerAutoSize(name='_content', parent=self._main_content, align=uiconst.CENTERBOTTOM, alignMode=uiconst.TOPLEFT, state=uiconst.UI_DISABLED if self.is_collapsed else uiconst.UI_PICKCHILDREN, left=0, opacity=0.0 if self.is_collapsed else 1.0)
        self._content_tracker_token = self.tracker.add(self._base, anchor=(0.5, 0.5), offset=(0, -150))
        tether_cont = Transform(name='shipcaster_tether', rotation=math.radians(270.0), width=100, height=100)
        tether_cont.rotationCenter = (1.0, 0.5)
        tether_inner_cont = Transform(name='tether_inner_cont', parent=tether_cont, rotation=math.radians(180.0), width=tether_cont.width, height=tether_cont.height)
        self._tether = BracketTether(parent=tether_inner_cont, align=uiconst.TOPLEFT, collapsed=True, width=50, on_click=self._on_tether_click, on_close_point_click=self._on_close_point_click)
        self.tracker.add(tether_cont, anchor=(1.0, 0.5), offset=(35, 0))
        self._on_shipcaster_state_update()

    @property
    def item_id(self):
        return self._item_id

    @property
    def type_id(self):
        return self._type_id

    @property
    def camera(self):
        return self._camera

    @property
    def shipcaster_root_transform(self):
        return self._shipcaster_root_transform

    @property
    def content_bounds(self):
        return get_absolute_bounds(self._main_content)

    @property
    def content(self):
        return self._content

    def collapse(self, lock = False):
        self._main_content.DisableAutoSize()
        self._content.state = uiconst.UI_DISABLED
        self._tether.collapse(lock=lock)
        animations.MorphScalar(self._content, 'top', startVal=self._content.top, endVal=-20, duration=0.2)
        animations.FadeOut(self._content, duration=0.2, callback=self._main_content.EnableAutoSize)

    def expand(self):
        self._tether.expand()
        self._content.state = uiconst.UI_PICKCHILDREN
        animations.MorphScalar(self._content, 'top', startVal=self._content.top, endVal=0, duration=0.2, timeOffset=0.2, callback=self._main_content.EnableAutoSize)
        animations.FadeIn(self._content, duration=0.2, timeOffset=0.2)

    def close(self):
        self._state_machine.close()
        self._base.Close()
        self._tether.parent.Close()
        self._shipcaster_transform.close()
        super(ShipcasterBracketPanel, self).close()

    def _on_shipcaster_state_update(self):
        from spacecomponents.client.ui.shipcaster.shipcasterStates import Idle
        self._state_machine.move_to(Idle(self))

    def _on_tether_click(self):
        if self.playerRequestedCollapseToken:
            self.playerRequestedCollapseToken.clear()
        self.force_expand()

    def _on_close_point_click(self):
        self.playerRequestedCollapseToken = self.request_collapse(Priority.control_point)
