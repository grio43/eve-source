#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\buttonIndicator.py
import uthread2
from carbon.common.script.util.format import FmtAmtCapped, FmtAmt
from carbonui import TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.shared.neocom.neocom.highlightState import GetIndicatorBackgroundColor, GetIndicatorColor, HighlightState, GetIndicatorGlowBrightness
ANIM_DURATION = 0.3
HEIGHT = 16
HEIGHT_SMALL = 8
LINE_WIDTH = 2

class ButtonIndicator(Container):
    default_width = LINE_WIDTH

    def ApplyAttributes(self, attributes):
        super(ButtonIndicator, self).ApplyAttributes(attributes)
        self.value = attributes.value
        self.maxValue = attributes.get('maxValue', None)
        highlightState = attributes.highlightState
        self.highlightState = None
        self.line = Line(parent=self, align=uiconst.TOLEFT, weight=LINE_WIDTH, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)
        self.content = Container(name='content', align=uiconst.TOLEFT, parent=self, clipChildren=True)
        self.bgFrame = Frame(bgParent=self.content, texturePath='res:/UI/Texture/Classes/Neocom/buttonIndicatorBG.png', cornerSize=4)
        Frame(bgParent=self.content, texturePath='res:/UI/Texture/Classes/Neocom/buttonIndicatorBG.png', cornerSize=4, color=(0, 0, 0, 0.3))
        self.label = eveLabel.EveLabelMedium(parent=self.content, align=uiconst.CENTERLEFT, color=TextColor.HIGHLIGHT, left=4)
        self.SetHighlightState(highlightState, animate=False)
        if self.value:
            self.SetCounterValue(self.value, animate=False)

    def SetHighlightState(self, highlightState, animate = True):
        self.highlightState = highlightState
        self.UpdateColor(animate)
        self.UpdateHeight(animate)
        self.UpdateOpacity(animate)
        self.UpdateLineGlowBrightness(animate)

    def UpdateLineGlowBrightness(self, animate = True):
        glowBrightness = GetIndicatorGlowBrightness(self.highlightState)
        if animate:
            animations.MorphScalar(self.line, 'glowBrightness', self.line.glowBrightness, glowBrightness, duration=ANIM_DURATION)
        else:
            self.line.glowBrightness = glowBrightness

    def UpdateColor(self, animate):
        lineColor = GetIndicatorColor(self.highlightState)
        bgColor = GetIndicatorBackgroundColor(self.highlightState)
        bgColor = Color(*bgColor).SetOpacity(0.4).GetRGBA()
        if animate:
            animations.SpColorMorphTo(self.line, self.line.rgba, lineColor, duration=ANIM_DURATION)
            animations.SpColorMorphTo(self.bgFrame, self.bgFrame.rgba, bgColor, duration=ANIM_DURATION)
        else:
            self.line.rgba = lineColor
            self.bgFrame.rgba = bgColor

    def SetCounterValue(self, value, animate = True):
        if value > self.value and animate:
            self._UpdateValueText(value)
            uthread2.StartTasklet(self._ShowValueBanner)
        self.value = value

    def _ShowValueBanner(self):
        uthread2.Sleep(3.0)
        width, _ = self.label.GetAbsoluteSize()
        width += 8
        self.label.opacity = 1.0
        animations.MorphScalar(self.content, 'width', self.content.width, width, duration=ANIM_DURATION)
        animations.FadeTo(self.content, 0.0, 1.0, duration=ANIM_DURATION)
        uthread2.Sleep(5.0)
        self._HideValueBanner()

    def _HideValueBanner(self, animate = True):
        if animate:
            duration = 0.6
            animations.MorphScalar(self.content, 'width', self.content.width, 0, duration=duration)
            animations.FadeOut(self.label, duration=0.1)
            animations.FadeOut(self.content, duration=duration)
        else:
            self.content.width = self.content.opacity = 0

    def _UpdateValueText(self, value):
        if self.maxValue and value > self.maxValue:
            text = FmtAmtCapped(self.maxValue, fmt='sn')
        else:
            text = FmtAmt(value, fmt='sn')
        self.label.text = text

    def UpdateOpacity(self, animate = True):
        opacity = 0.0 if self.highlightState == HighlightState.normal else 1.0
        if animate:
            animations.FadeTo(self, self.opacity, opacity, duration=ANIM_DURATION)
        else:
            self.opacity = opacity

    def UpdateHeight(self, animate):
        height = self._GetHeight()
        if animate:
            animations.MorphScalar(self, 'height', self.height, height, duration=0.2)
        else:
            self.height = height

    def _GetHeight(self):
        if self.highlightState in (HighlightState.important, HighlightState.active):
            return HEIGHT
        elif self.highlightState == HighlightState.open:
            return HEIGHT_SMALL
        else:
            return 0

    def OnColorThemeChanged(self):
        super(ButtonIndicator, self).OnColorThemeChanged()
        self.UpdateColor(animate=False)
