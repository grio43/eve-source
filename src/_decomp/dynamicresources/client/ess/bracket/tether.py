#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\tether.py
import math
import chroma
import eveui
import signals
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.util.color import Color
from dynamicresources.client import color

class BracketTether(Container):
    _dot_size = 17
    _end_cap_size = 7
    _interaction_point_size = 24

    def __init__(self, parent = None, align = None, left = 0, top = 0, collapsed = False, on_click = None, name = None, on_close_point_click = None, width = 100):
        if align is None:
            align = self.default_align
        super(BracketTether, self).__init__(parent=parent, align=align, left=left, top=top, width=width, height=30, name=name or '')
        self._collapsed = collapsed
        self._locked = False
        self.on_click = signals.Signal()
        if on_click:
            self.on_click.connect(on_click)
        self.on_close_point_click = signals.Signal()
        if on_close_point_click:
            self.on_close_point_click.connect(on_close_point_click)
        self._construct_close_interaction_point()
        self._interaction_point = Container(parent=self, name='interaction_point', align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, width=self._interaction_point_size, height=self._interaction_point_size, opacity=1.0 if self._collapsed else 0.0)
        self._interaction_point.OnClick = self._on_interaction_point_click
        self._interaction_point.OnMouseEnter = self._on_interaction_point_enter
        self._interaction_point.OnMouseExit = self._on_interaction_point_exit
        if not self._collapsed:
            self._interaction_point.Disable()
        self._head_outer_segments = Transform(parent=self._interaction_point, align=uiconst.TOALL, rotationCenter=(0.5, 0.5), scalingCenter=(0.5, 0.5))
        self._interaction_outer_segments = Sprite(parent=self._head_outer_segments, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=18, height=18, texturePath='res:/UI/Texture/classes/ess/bracket/tether_head_outer_segments.png')
        animations.MorphScalar(self._head_outer_segments, 'rotation', endVal=math.pi * 2.0, duration=4.0, curveType=uiconst.ANIM_LINEAR, loops=-1)
        self._interaction_center_dot = Sprite(parent=self._interaction_point, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=18, height=18, texturePath='res:/UI/Texture/classes/ess/bracket/tether_head_inner.png')
        self._head_cont = Container(parent=self, name='head_cont', align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=3, width=17, height=17)
        self._head_inner = Sprite(parent=self._head_cont, name='_head_inner', align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/ess/bracket/tether_head_inner.png', opacity=1.0 if not self._collapsed else 0.0)
        self._head_outer = Sprite(parent=self._head_cont, name='_head_outer', align=uiconst.TOALL, scale=(1.0, 1.0) if not self._collapsed else (2.0, 2.0), texturePath='res:/UI/Texture/classes/ess/bracket/tether_head_outer.png', opacity=1.0 if not self._collapsed else 0.0)
        self._stem = Fill(parent=self, align=uiconst.CENTERLEFT, left=19, height=1, width=self._stem_width if not self._collapsed else 0, color=color.white.rgb, opacity=1.0 if not self._collapsed else 0.0)
        self._end_cap = Sprite(parent=self, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, height=self._end_cap_size if not self._collapsed else 0, width=self._end_cap_size, texturePath='res:/UI/Texture/classes/ess/bracket/tether_cap.png', opacity=1.0 if not self._collapsed else 0.0)

    def _construct_close_interaction_point(self):
        self._close_bracket_interaction_point = Container(parent=self, name='close_bracket_interaction_point', align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, width=self._interaction_point_size, height=self._interaction_point_size)
        if self._collapsed:
            self._close_bracket_interaction_point.Disable()
        self._close_bracket_interaction_point.OnClick = self._on_close_interaction_point_click
        self._close_bracket_interaction_point.OnMouseEnter = self._on_close_interaction_point_enter
        self._close_bracket_interaction_point.OnMouseExit = self._on_close_interaction_point_exit
        self._close_head_outer_segments = Transform(parent=self._close_bracket_interaction_point, align=uiconst.TOALL, rotationCenter=(0.5, 0.5), scalingCenter=(0.5, 0.5))
        self._close_interaction_outer_segments = Sprite(parent=self._close_head_outer_segments, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=18, height=18, texturePath='res:/UI/Texture/classes/ess/bracket/tether_head_outer_segments.png', color=Color.WHITE)
        self._close_bracket_interaction_point.opacity = 0.0
        animations.MorphScalar(self._close_interaction_outer_segments, 'rotation', endVal=math.pi * 2.0, duration=4.0, curveType=uiconst.ANIM_LINEAR, loops=-1)

    def _on_close_interaction_point_enter(self, *args):
        animations.FadeOut(self._head_outer, duration=0.2)
        animations.FadeIn(self._close_bracket_interaction_point, duration=0.2)
        animations.MorphVector2(self._close_interaction_outer_segments, 'scale', startVal=self._close_interaction_outer_segments.scale, endVal=(0.9, 0.9), duration=0.2)
        animations.MorphVector3(self, '_interaction_point_color', startVal=self._interaction_point_color, endVal=color.focus.rgb, duration=0.2)

    def _on_close_interaction_point_exit(self, *args):
        if not self._collapsed:
            animations.FadeIn(self._head_outer, duration=0.2)
        animations.FadeOut(self._close_bracket_interaction_point, duration=0.2)
        animations.MorphVector2(self._close_interaction_outer_segments, 'scale', startVal=self._close_interaction_outer_segments.scale, endVal=(1.0, 1.0), duration=0.2)
        animations.MorphVector3(self, '_interaction_point_color', startVal=self._interaction_point_color, endVal=color.white.rgb, duration=0.3)

    def _on_close_interaction_point_click(self, *args):
        self.on_close_point_click()
        eveui.Sound.button_click.play()
        self.ping()

    def _on_interaction_point_click(self, *args):
        self.on_click()
        eveui.Sound.button_click.play()
        self.ping()

    def _on_interaction_point_enter(self):
        animations.MorphVector2(self._head_outer_segments, 'scale', startVal=self._head_outer_segments.scale, endVal=(1.2, 1.2), duration=0.2)
        animations.MorphVector3(self, '_interaction_point_color', startVal=self._interaction_point_color, endVal=color.focus.rgb, duration=0.2)

    def _on_interaction_point_exit(self):
        animations.MorphVector2(self._head_outer_segments, 'scale', startVal=self._head_outer_segments.scale, endVal=(1.0, 1.0), duration=0.3)
        animations.MorphVector3(self, '_interaction_point_color', startVal=self._interaction_point_color, endVal=color.white.rgb, duration=0.3)

    def close(self):
        self.Close()

    def expand(self):
        if not self._collapsed:
            return
        self._locked = False
        self._collapsed = False
        self._close_bracket_interaction_point.Enable()
        self._interaction_point.Disable()
        animations.FadeOut(self._interaction_point, duration=0.1)
        animations.MorphVector2(self._head_outer, 'scale', startVal=(2.0, 2.0), endVal=(1.0, 1.0), duration=0.1)
        animations.FadeIn(self._head_inner, duration=0.1)
        animations.FadeIn(self._head_outer, duration=0.1)
        animations.FadeIn(self._stem, duration=0.2)
        animations.MorphScalar(self._stem, 'width', startVal=self._stem.width, endVal=self._stem_width, duration=0.2)
        animations.FadeIn(self._end_cap, duration=0.1, timeOffset=0.2)
        animations.MorphScalar(self._end_cap, 'height', startVal=self._end_cap.height, endVal=self._end_cap_size, duration=0.15, timeOffset=0.15)
        self._head_cont.Enable()

    def show_collapsed_interaction_point(self, show):
        if show:
            self._interaction_point.Enable()
            animations.FadeIn(self._interaction_point, duration=0.15)
        else:
            self._interaction_point.Disable()
            animations.FadeOut(self._interaction_point, duration=0.15)

    def collapse(self, lock = False):
        if not lock and self._locked and self._collapsed:
            self.show_collapsed_interaction_point(True)
            self._locked = False
            return
        if lock and not self._locked and self._collapsed:
            self.show_collapsed_interaction_point(False)
            self._locked = True
            return
        if self._collapsed:
            return
        self._collapsed = True
        self._locked = lock
        animations.FadeOut(self._close_bracket_interaction_point, duration=0.2)
        self._close_bracket_interaction_point.Disable()
        self._head_cont.Disable()
        animations.MorphScalar(self._end_cap, 'height', startVal=self._end_cap.height, endVal=0, duration=0.2)
        animations.FadeOut(self._end_cap, duration=0.1, timeOffset=0.1)
        animations.MorphScalar(self._stem, 'width', startVal=self._stem.width, endVal=0, duration=0.2, timeOffset=0.2)
        animations.FadeOut(self._stem, duration=0.2, timeOffset=0.2)
        animations.MorphVector2(self._head_outer, 'scale', startVal=(1.0, 1.0), endVal=(2.0, 2.0), duration=0.15, timeOffset=0.3)
        animations.FadeOut(self._head_outer, duration=0.15, timeOffset=0.3)
        animations.FadeOut(self._head_inner, duration=0.15, timeOffset=0.3)
        if not lock:
            self._interaction_point.Enable()
            animations.FadeIn(self._interaction_point, duration=0.15, timeOffset=0.3)
        self.ping(time_offset=0.3)

    def ping(self, time_offset = 0.0):
        ping = Sprite(parent=self._head_cont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ess/circle_256.png', width=0, height=0, opacity=0.5)
        animations.MorphScalar(ping, 'width', endVal=32, duration=0.3, timeOffset=time_offset)
        animations.MorphScalar(ping, 'height', endVal=32, duration=0.3, timeOffset=time_offset)
        animations.FadeOut(ping, duration=0.2, timeOffset=0.1 + time_offset, callback=ping.Close)

    def play_enter_animation(self):
        self.ping()
        animations.FadeTo(self._interaction_point, startVal=0.0, endVal=1.0, duration=0.2)
        animations.FadeTo(self._stem, startVal=0.0, endVal=1.0, duration=0.2, timeOffset=0.2)
        animations.MorphScalar(self._stem, 'width', startVal=0, endVal=self._stem_width, duration=0.2, timeOffset=0.2)
        animations.MorphScalar(self._end_cap, 'height', startVal=0, endVal=self._end_cap_size, duration=0.2, timeOffset=0.4)

    @property
    def _stem_width(self):
        return self.width - self._interaction_point_size + (self._interaction_point_size - self._dot_size) / 2.0

    @property
    def _interaction_point_color(self):
        return self._interaction_center_dot.color.GetRGB()

    @_interaction_point_color.setter
    def _interaction_point_color(self, color):
        rgb_color = chroma.Color.from_any(color).rgb
        self._interaction_center_dot.color = rgb_color
        self._interaction_outer_segments.color = rgb_color
        self._close_interaction_outer_segments.color = rgb_color
        self._head_inner.color = rgb_color


from dynamicresources.client.ess.bracket.debug import __reload_update__
