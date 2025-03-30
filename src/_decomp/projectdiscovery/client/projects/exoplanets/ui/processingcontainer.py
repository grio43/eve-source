#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\ui\processingcontainer.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from projectdiscovery.client import const
from signals import Signal

class ProcessingContainer(Container):

    def ApplyAttributes(self, attributes):
        super(ProcessingContainer, self).ApplyAttributes(attributes)
        self.processing_container = None
        self._gradient_height = 0
        self._is_expanded = False
        self.on_content_visible = Signal(signalName='on_content_visible')
        self.on_container_invisible = Signal(signalName='on_container_invisible')
        self._animating_objects = []
        self._expansion_callback = None
        self._setup_layout_of_processing_container()
        self.audio_service = sm.GetService('audio')

    def _setup_layout_of_processing_container(self):
        width = (self.GetAbsoluteRight() - self.GetAbsoluteLeft()) / uicore.dpiScaling if not self.width else self.width
        self._content = Container(name='ProcessingContainerContent', parent=self, align=uiconst.TOALL)
        self.processing_container = Container(name='processingContainer', parent=self, width=width - 1, height=70, align=uiconst.CENTER)
        self.expandTopContainer = Container(name='expandTopContainer', parent=self.processing_container, height=11, align=uiconst.TOTOP_NOPUSH)
        SpriteThemeColored(name='expandTop', parent=self.expandTopContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandTop.png', width=174, height=5, align=uiconst.CENTERTOP, top=5, colorType=uiconst.COLORTYPE_FLASH)
        self._expand_bracket_top = SpriteThemeColored(parent=self.expandTopContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandBrackets.png', width=width - 1, height=3, align=uiconst.TOTOP, top=11, colorType=uiconst.COLORTYPE_FLASH)
        self.expandBottomContainer = Transform(name='expandBottomContainer', parent=self.processing_container, height=11, align=uiconst.TOBOTTOM_NOPUSH, rotation=math.pi)
        SpriteThemeColored(parent=self.expandBottomContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandTop.png', width=174, height=5, align=uiconst.CENTERBOTTOM, top=4, colorType=uiconst.COLORTYPE_FLASH)
        self._expand_bracket_bottom = SpriteThemeColored(parent=self.expandBottomContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandBrackets.png', width=width - 1, height=3, align=uiconst.TOBOTTOM, colorType=uiconst.COLORTYPE_FLASH)
        self.expandGradient = SpriteThemeColored(name='ExpandGradient', parent=self.processing_container, align=uiconst.TOALL, padTop=11, padBottom=11, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandGradient.png')
        self._original_translation_top = self.expandTopContainer.translation
        self._original_translation_bottom = self.expandBottomContainer.translation

    def fade_in(self, duration = 0.5):
        self.reset_processing_screen()
        animations.FadeIn(self, timeOffset=0.1, duration=duration)

    def fade_in_and_expand(self, callback = None):

        def fade_in_callback():
            self.expand_screen(callback=callback)

        self.reset_processing_screen()
        animations.FadeIn(self, timeOffset=0.1, callback=fade_in_callback, duration=0.5)

    @property
    def gradient_height(self):
        return self._gradient_height

    @gradient_height.setter
    def gradient_height(self, value):
        self._gradient_height = value
        self.expandGradient.SetSize(self.displayWidth / uicore.dpiScaling - 1, self._gradient_height * uicore.dpiScaling)

    def gradient_height_callback(self):
        self._animating_objects = []
        animations.FadeIn(self._content, duration=0.5, callback=self.on_content_visible)
        if callable(self._expansion_callback):
            self._expansion_callback()
            self._expansion_callback = None

    def gradient_height_retract_callback(self):
        animations.FadeOut(self, duration=0.5, callback=self.on_container_invisible)

    def expand_screen(self, duration = 0.2, callback = None):
        self._is_expanded = True
        self._expansion_callback = callback
        expand_height = self.displayHeight / uicore.dpiScaling
        animations.MorphScalar(self.processing_container, 'height', self.processing_container.height, expand_height, duration=duration, callback=self.gradient_height_callback)
        self.audio_service.SendUIEvent(const.Sounds.AnalysisWindowMovePlay)

    def retract_screen(self, duration = 0.5, callback = None):
        self._is_expanded = False
        if callback is None:
            callback = self.gradient_height_retract_callback
        animations.MorphScalar(self.processing_container, 'height', self.processing_container.height, 70, duration=duration, callback=callback)
        self.audio_service.SendUIEvent(const.Sounds.AnalysisWindowMovePlay)

    def fade_out(self, callback = None):

        def animation_callback():
            self.reset_processing_screen()
            invoke_callback(callback)

        animations.FadeOut(self, duration=0.5, callback=animation_callback)

    def retract_and_fade_out(self):
        self.retract_screen(callback=self.fade_out)

    def fade_out_content_and_retract(self, callback = None):

        def fade_out_callback():
            self.retract_screen(callback=callback)

        animations.FadeOut(self._content, duration=0.5, callback=fade_out_callback)

    def reset_processing_screen(self):
        self._is_expanded = False
        self.processing_container.height = 70
        self._content.opacity = 0

    def UpdateAlignment(self, *args, **kwargs):
        budget = super(ProcessingContainer, self).UpdateAlignment(*args, **kwargs)
        if self.processing_container:
            width = self.displayWidth / uicore.dpiScaling - 1
            self.processing_container.SetSize(width, self.processing_container.height)
        return budget


def invoke_callback(callback, *args, **kwargs):
    if callable(callback):
        callback(*args, **kwargs)
