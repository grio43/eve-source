#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\root\status.py
import eveformat
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control import eveLabel
from dynamicresources.client import color, text
from dynamicresources.client.ess.bracket.panel import BracketPanel, get_absolute_bounds
from dynamicresources.client.ess.bracket.state_machine import State, Transition
from dynamicresources.client.ess.bracket.transform import BankPanelTransformController

class StatusBase(State):

    def __init__(self, bracket, message):
        self._bracket = bracket
        self._message = message
        self._panel = None
        self._transform = None

    def enter(self):
        self._transform = BankPanelTransformController(root=self._bracket.ess_root, camera=self._bracket.camera, offset_y=3300.0)
        self._panel = StatusPanel(parent=self._bracket.layer, transform=self._transform.transform, camera=self._bracket.camera, message=self._message)

    def exit(self):
        transition = Exit(self._panel, self._transform)
        self._panel = None
        self._transform = None
        return transition

    def close(self):
        if self._panel:
            self._panel.close()
        if self._transform:
            self._transform.close()


class OutOfRange(StatusBase):

    def __init__(self, bracket):
        super(OutOfRange, self).__init__(bracket=bracket, message=text.status_out_of_range())


class Offline(StatusBase):

    def __init__(self, bracket):
        super(Offline, self).__init__(bracket=bracket, message=text.status_offline())


class Exit(Transition):

    def __init__(self, panel, transform):
        super(Exit, self).__init__()
        self._panel = panel
        self._transform = transform

    def animation(self):
        self._panel.play_exit_animation()
        self.sleep(0.3)

    def on_close(self):
        self._panel.close()
        self._transform.close()


class StatusPanel(BracketPanel):

    def __init__(self, parent, transform, camera, message):
        self._first_expand = True
        super(StatusPanel, self).__init__(name='ess_status_panel', transform=transform, layer=parent, camera=camera, collapse_at_camera_distance=100000.0, clipping_dead_zone=25, collapsed=True)
        self._base = LayoutGrid(name='ess_status_panel', columns=1)
        self._message_cont = ContainerAutoSize(parent=self._base, align=uiconst.TOPLEFT, alignMode=uiconst.TOPLEFT, bgColor=color.black.with_alpha(0.5).rgba, opacity=0.0 if self.is_collapsed else 1.0)
        if self.is_collapsed:
            self._message_cont.DisableAutoSize()
        eveLabel.EveHeaderLarge(parent=self._message_cont, align=uiconst.TOPLEFT, text=eveformat.color(message, (1.0, 1.0, 1.0, 1.0)), padding=(24, 12, 24, 12))
        Frame(bgParent=self._message_cont, idx=0)
        self._stem = Fill(parent=self._base, align=uiconst.CENTER, width=1, height=0 if self.is_collapsed else 32, color=color.white.rgba)
        Sprite(parent=self._base, align=uiconst.CENTER, state=uiconst.UI_DISABLED, height=5, width=5, texturePath='res:/UI/Texture/classes/ess/bracket/dot_5px.png')
        self.tracker.add(self._base, anchor=(0.5, 1.0))
        if not self.is_collapsed:
            self._first_expand = False
            animations.FadeTo(self._base, duration=0.1, loops=3, curveType=uiconst.ANIM_LINEAR)

    @property
    def content_bounds(self):
        return get_absolute_bounds(self._message_cont)

    def close(self):
        self._base.Close()
        super(StatusPanel, self).close()

    def expand(self):
        if self._first_expand:
            self._first_expand = False
            animations.FadeTo(self._base, duration=0.1, loops=3, curveType=uiconst.ANIM_LINEAR)
        animations.MorphScalar(self._stem, 'height', startVal=self._stem.height, endVal=32, duration=0.2)
        animations.BlinkIn(self._message_cont, timeOffset=0.2)
        width, height = self._message_cont.GetAutoSize()
        self._message_cont.width = width
        animations.MorphScalar(self._message_cont, 'height', startVal=self._message_cont.height, endVal=height, duration=0.2, timeOffset=0.1, callback=self._message_cont.EnableAutoSize)

    def collapse(self, lock = False):
        self._message_cont.DisableAutoSize()
        animations.MorphScalar(self._message_cont, 'height', startVal=self._message_cont.height, endVal=0, duration=0.2)
        animations.FadeOut(self._message_cont, duration=0.1)
        animations.MorphScalar(self._stem, 'height', startVal=self._stem.height, endVal=0, duration=0.2, timeOffset=0.1)

    def play_exit_animation(self):
        animations.FadeOut(self._base, duration=0.2)


from dynamicresources.client.ess.bracket.debug import __reload_update__
