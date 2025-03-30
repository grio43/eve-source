#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphs\tutorialgraph.py
from carbonui.graphs.axis import AxisOrientation
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.primitives.sprite import StreamingVideoSprite, Sprite
from trinity import TR2_SFX_COPY, TR2_SFX_COLOROVERLAY, TR2_SBM_BLEND, TR2_SBM_ADD
BRACKET_TO_BOX_LINE_COLOR = (172 / 255.0,
 213 / 255.0,
 241 / 255.0,
 1.0)
BRACKET_TO_BOX_LINE_WIDTH = 0.8
BRACKET_SIZE = 16
BRACKET_SPRITE_SIZE = 100
BRACKET_INTRO_VIDEO = 'res:/UI/Texture/classes/HighlightTool/HighlightRing_Intro.webm'
BRACKET_LOOP_VIDEO = 'res:/UI/Texture/classes/HighlightTool/HighlightRing_Loop.webm'
BRACKET_GLOW_TEXTURE = 'res:/UI/Texture/classes/HighlightTool/highlightRingGlow.png'

class TutorialGraph(Container):

    def ApplyAttributes(self, attributes):
        super(TutorialGraph, self).ApplyAttributes(attributes)
        self.pickState = uiconst.TR2_SPS_OFF
        self._category_axis = attributes.get('categoryAxis')
        self._value_axis = attributes.get('valueAxis')
        self._transit_selection = attributes.get('transitSelection')
        data = self._transit_selection.get_closest_points_to_centers()
        self._values = [ y for x, y in data ]
        self._category_axis.set_data_points([ x for x, y in data ])
        self._orientation = attributes.get('orientation', AxisOrientation.VERTICAL)
        self._locked = False
        self._dirty = False
        self._is_animating = False
        self._sprites = []
        self._filtered_centers = []
        self._category_axis.onChange.connect(self._axis_changed)
        self._value_axis.onChange.connect(self._axis_changed)
        self._transit_selection.on_data_change.connect(self._update)
        self._build()

    def _update(self):
        self.LockGraphUpdates()
        data = self._transit_selection.get_closest_points_to_centers()
        self._values = [ y for x, y in data ]
        self._category_axis.set_data_points([ x for x, y in data ])

    def animate_appearing(self, callback = None):

        def animation_callback():
            self._is_animating = False
            if callable(callback):
                callback()

        time_offsets = self.get_along_axis_time_offsets()
        self._is_animating = True
        for i, (sprite, time_offset) in enumerate(zip(self._sprites, time_offsets)):
            the_callback = animation_callback if i == len(time_offsets) - 1 else None
            animations.FadeTo(sprite, 0, 1, timeOffset=time_offset, callback=the_callback)

    def animate_disappearing(self, callback = None):

        def animation_callback():
            self._is_animating = False
            if callable(callback):
                callback()

        time_offsets = self.get_along_axis_time_offsets()
        self._is_animating = True
        for i, (sprite, time_offset) in enumerate(zip(self._sprites, time_offsets)):
            the_callback = animation_callback if i == len(time_offsets) - 1 else None
            animations.FadeTo(sprite, 1, 0, timeOffset=time_offset, callback=the_callback)

    def LockGraphUpdates(self):
        self._locked = True

    def UnlockGraphUpdates(self):
        if self._locked:
            self._locked = False
            if self._dirty:
                self._rescale()

    def _axis_changed(self, _):
        if self._locked:
            self._dirty = True
        else:
            self._rescale()

    def _build(self):
        vertices = self._get_vertex_positions()
        width = self.get_highlight_size()
        height = width
        half_width = width / 2.0
        half_height = height / 2.0
        for x, y in vertices:
            sprite = HighlightSprite(name='HighlightSprite', parent=self, align=uiconst.RELATIVE, top=y - half_height, left=x - half_width, width=width, height=height)
            self._sprites.append(sprite)

    def _rescale(self):
        dpi_scaling = uicore.dpiScaling
        vertices = self._get_vertex_positions()
        width = self.get_highlight_size()
        height = width
        half_width = width / 2.0
        half_height = height / 2.0
        for (x, y), sprite in zip(vertices, self._sprites):
            old_left = sprite.left
            sprite.width = width
            sprite.height = height
            y_fix = y + half_height - self.ReverseScaleDpi(self.displayHeight)
            y_fix = 0 if y_fix < 0 or not self.displayHeight else y_fix
            sprite.top = y - half_height - y_fix
            sprite.left = max(min(x - half_width, self.ReverseScaleDpi(self.displayWidth)), 0 - width)
            if old_left >= 0 > sprite.left:
                sm.ScatterEvent('OnTutorialGraphSpriteLeftOutOfRange', True, sprite)
            elif old_left < 0 <= sprite.left:
                sm.ScatterEvent('OnTutorialGraphSpriteLeftOutOfRange', False, sprite)

        self._filter()

    def get_highlight_size(self):
        time_range = self._transit_selection.get_estimated_eclipse_time()
        if time_range:
            start_time = self._category_axis.get_actual_data_points()[0]
            end_time = start_time + time_range
            mapped = list(self._category_axis.MapSequenceToViewport([self._category_axis.map_actual_value_to_normalized_value(start_time), self._category_axis.map_actual_value_to_normalized_value(end_time)]))
            width = mapped[1] - mapped[0]
            return min(width + 30, 300)
        return 30

    def get_along_axis_time_offsets(self):
        return [ 1.3 * value for value in self._category_axis.GetDataPoints() ]

    def _get_vertex_positions(self):
        if self._orientation == AxisOrientation.VERTICAL:
            vertices = zip(self._category_axis.MapDataPointsToViewport(), self._value_axis.MapSequenceToViewport(self._values))
        else:
            vertices = zip(self._value_axis.MapSequenceToViewport(self._values), self._category_axis.MapDataPointsToViewport())
        return vertices

    def Close(self):
        self._category_axis.onChange.disconnect(self._axis_changed)
        self._value_axis.onChange.disconnect(self._axis_changed)
        self._transit_selection.on_data_change.disconnect(self._update)
        self._sprites = []
        super(TutorialGraph, self).Close()

    def set_transit_selection_filter(self, transit_selections):
        self._filtered_centers = []
        for selection in transit_selections:
            for center in selection.get_centers():
                self._filtered_centers.append(center)

        self._filter()

    def _filter(self):
        half_eclipse = self._transit_selection.get_estimated_eclipse_time() / 2.0
        for time, sprite in zip(self._category_axis.get_actual_data_points(), self._sprites):
            min_time, max_time = time - half_eclipse, time + half_eclipse
            is_in_filter = any([ True for center in self._filtered_centers if min_time <= center <= max_time ])
            if is_in_filter:
                sprite.hide()
            else:
                sprite.show()

    def _get_highlight_time_range(self):
        mapped_from_viewport = [self._category_axis.MapFromViewport(0), self._category_axis.MapFromViewport(self.get_highlight_size())]
        min_time = self._category_axis.map_normalized_value_to_actual_value(mapped_from_viewport[0])
        max_time = self._category_axis.map_normalized_value_to_actual_value(mapped_from_viewport[1])
        return (max_time - min_time) * 0.3


class HighlightSprite(Container):
    default_align = uiconst.RELATIVE

    def ApplyAttributes(self, attributes):
        super(HighlightSprite, self).ApplyAttributes(attributes)
        self._create_video_sprites()
        self._PlayIntro()
        self._is_hidden = False

    def _create_video_sprites(self):
        self.bracketSpriteLoop = StreamingVideoSprite(parent=self, name='spaceObjectHighlightBracketLoopVideo', videoPath=BRACKET_LOOP_VIDEO, videoLoop=True, align=uiconst.TOALL, state=uiconst.UI_DISABLED, blendMode=TR2_SBM_BLEND, spriteEffect=TR2_SFX_COLOROVERLAY, opacity=0.0, disableAudio=True)
        self.bracketSpriteLoop.Pause()
        self.bracketSpriteIntro = StreamingVideoSprite(parent=self, name='spaceObjectHighlightBracketIntroVideo', videoPath=BRACKET_INTRO_VIDEO, videoLoop=False, align=uiconst.TOALL, state=uiconst.UI_DISABLED, blendMode=TR2_SBM_BLEND, spriteEffect=TR2_SFX_COLOROVERLAY, opacity=0.0, disableAudio=True)
        self.bracketSpriteIntro.Pause()
        self.bracketSpriteIntro.OnVideoFinished = self._PlayLoop
        self._glow = Sprite(parent=self, name='spaceObjectHighlightBracketGlow', align=uiconst.TOALL, texturePath=BRACKET_GLOW_TEXTURE, state=uiconst.UI_DISABLED, blendMode=TR2_SBM_ADD)

    def Close(self):
        super(HighlightSprite, self).Close()

    def _PlayIntro(self):
        self.bracketSpriteIntro.opacity = 1.0
        self.bracketSpriteIntro.Play()

    def _PlayLoop(self):
        self.bracketSpriteIntro.opacity = 0.0
        self.bracketSpriteLoop.opacity = 1.0
        self.bracketSpriteLoop.Play()

    def hide(self):
        if not self._is_hidden:
            animations.FadeOut(self)
        self._is_hidden = True

    def show(self):
        if self._is_hidden:
            animations.FadeIn(self)
        self._is_hidden = False
