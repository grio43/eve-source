#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\buttons.py
import logging
from carbonui import uiconst
from carbonui.fontconst import STYLE_DEFAULT, EVE_SMALL_FONTSIZE
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import Label
log = logging.getLogger(__name__)
OPACITY_LABEL_IDLE = 1.0

class ButtonTextBoldness(object):
    NEVER_BOLD = 0
    ALWAYS_BOLD = 1
    BOLD_ON_MOUSEOVER = 2


class TextButtonWithBackgrounds(Container):
    __guid__ = 'uicontrols.TextButtonWithBackgrounds'
    default_state = uiconst.UI_NORMAL
    default_text = ''
    default_fontsize = EVE_SMALL_FONTSIZE
    default_fontStyle = STYLE_DEFAULT
    default_boldText = ButtonTextBoldness.NEVER_BOLD
    default_mouseUpBGTexture = None
    default_mouseEnterBGTexture = None
    default_mouseDownBGTexture = None
    default_disabledBGTexture = None
    default_mouseUpBGOpacity = 1.0
    default_mouseEnterBGOpacity = 1.0
    default_mouseDownBGOpacity = 1.0
    default_disabledBGOpacity = 1.0
    default_mouseUpBGColor = None
    default_mouseEnterBGColor = None
    default_mouseDownBGColor = None
    default_disabledBGColor = None
    default_mouseUpTextColor = (1.0, 1.0, 1.0, 1.0)
    default_mouseEnterTextColor = (0.0, 0.0, 0.0, 1.0)
    default_mouseDownTextColor = (0.0, 0.0, 0.0, 1.0)
    default_disabledTextColor = (1.0, 1.0, 1.0, 1.0)
    default_bgFadeInDuration = 0.1
    default_bgFadeOutDuration = 0.1
    default_frameCornerSize = 0
    default_bgRotation = 0.0
    default_hoverSound = None
    default_selectedSound = None
    default_func = None
    default_args = None
    default_textContainerOpacity = 1.0
    default_isCapitalized = False
    default_letterspace = 0

    def ApplyAttributes(self, attributes):
        self.text = attributes.Get('text', self.default_text)
        self.fontsize = attributes.Get('fontsize', self.default_fontsize)
        self.fontStyle = attributes.Get('fontStyle', self.default_fontStyle)
        self.boldText = attributes.Get('boldText', self.default_boldText)
        self.isCapitalized = attributes.Get('isCapitalized', self.default_isCapitalized)
        self.letterspace = attributes.Get('letterspace', self.default_letterspace)
        self.mouseUpBGTexture = attributes.Get('mouseUpBGTexture', self.default_mouseUpBGTexture)
        self.mouseEnterBGTexture = attributes.Get('mouseEnterBGTexture', self.default_mouseEnterBGTexture)
        self.mouseDownBGTexture = attributes.Get('mouseDownBGTexture', self.default_mouseDownBGTexture)
        self.disabledBGTexture = attributes.Get('disabledBGTexture', self.default_disabledBGTexture)
        self.mouseUpBGOpacity = attributes.Get('mouseUpBGOpacity', self.default_mouseUpBGOpacity)
        self.mouseEnterBGOpacity = attributes.Get('mouseEnterBGOpacity', self.default_mouseEnterBGOpacity)
        self.mouseDownBGOpacity = attributes.Get('mouseDownBGOpacity', self.default_mouseDownBGOpacity)
        self.disabledBGOpacity = attributes.Get('disabledBGOpacity', self.default_disabledBGOpacity)
        self.mouseUpBGColor = attributes.Get('mouseUpBGColor', self.default_mouseUpBGColor)
        self.mouseEnterBGColor = attributes.Get('mouseEnterBGColor', self.default_mouseEnterBGColor)
        self.mouseDownBGColor = attributes.Get('mouseDownBGColor', self.default_mouseDownBGColor)
        self.disabledBGColor = attributes.Get('disabledBGColor', self.default_disabledBGColor)
        self.mouseUpTextColor = attributes.Get('mouseUpTextColor', self.default_mouseUpTextColor)
        self.mouseEnterTextColor = attributes.Get('mouseEnterTextColor', self.default_mouseEnterTextColor)
        self.mouseDownTextColor = attributes.Get('mouseDownTextColor', self.default_mouseDownTextColor)
        self.disabledTextColor = attributes.Get('disabledTextColor', self.default_disabledTextColor)
        self.bgFadeInDuration = attributes.Get('bgFadeInDuration', self.default_bgFadeInDuration)
        self.bgFadeOutDuration = attributes.Get('bgFadeOutDuration', self.default_bgFadeOutDuration)
        self.frameCornerSize = attributes.Get('frameCornerSize', self.default_frameCornerSize)
        self.bgRotation = attributes.Get('bgRotation', self.default_bgRotation)
        self.audio = sm.GetService('audio')
        self.hoverSound = attributes.Get('hoverSound', self.default_hoverSound)
        self.selectedSound = attributes.Get('selectedSound', self.default_selectedSound)
        self.func = attributes.get('func', self.default_func)
        self.args = attributes.get('args', self.default_args)
        textContainerOpacity = attributes.get('textContainerOpacity', self.default_textContainerOpacity)
        self.mouseUpBG = None
        self.mouseEnterBG = None
        self.mouseDownBG = None
        self.disabledBG = None
        Container.ApplyAttributes(self, attributes)
        self.BuildText(textContainerOpacity)
        self.BuildBackground()
        self.BuildMouseUpBackground()
        self.BuildMouseEnterBackground()
        self.BuildMouseDownBackground()
        self.BuildDisabledBackground()
        self.UpdateEnabledState()

    def BuildBackground(self):
        self.bgContainer = Container(name='bgContainer', parent=self, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height, state=uiconst.UI_DISABLED)

    def BuildMouseUpBackground(self):
        if self.mouseUpBGTexture:
            self.mouseUpBG = Frame(name='mouseUpBG', texturePath=self.mouseUpBGTexture, parent=self, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height, rotation=self.bgRotation, cornerSize=self.frameCornerSize, color=self.mouseUpBGColor)
        else:
            self.mouseUpBG = Container(name='mouseUpBG', parent=self, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height, bgColor=self.mouseUpBGColor)

    def BuildMouseEnterBackground(self):
        if self.mouseEnterBGTexture:
            self.mouseEnterBG = Frame(name='mouseEnterBG', parent=self, align=uiconst.TOTOP_NOPUSH, texturePath=self.mouseEnterBGTexture, width=self.width, height=self.height, opacity=0.0, rotation=self.bgRotation, cornerSize=self.frameCornerSize, color=self.mouseEnterBGColor)
        else:
            self.mouseEnterBG = Container(name='mouseEnterBG', parent=self, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height, bgColor=self.mouseEnterBGColor, opacity=0.0)

    def BuildMouseDownBackground(self):
        if self.mouseDownBGTexture:
            self.mouseDownBG = Frame(name='mouseDownBG', parent=self, align=uiconst.TOTOP_NOPUSH, texturePath=self.mouseDownBGTexture, width=self.width, height=self.height, opacity=0.0, rotation=self.bgRotation, cornerSize=self.frameCornerSize, color=self.mouseDownBGColor)
        else:
            self.mouseDownBG = Container(name='mouseDownBG', parent=self, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height, bgColor=self.mouseDownBGColor, opacity=0.0)

    def BuildDisabledBackground(self):
        if self.disabledBGTexture:
            self.disabledBG = Frame(name='disabledBG', parent=self, align=uiconst.TOTOP_NOPUSH, texturePath=self.disabledBGTexture, width=self.width, height=self.height, opacity=0.0, rotation=self.bgRotation, cornerSize=self.frameCornerSize, color=self.disabledBGColor)
        else:
            self.disabledBG = Container(name='disabledBG', parent=self, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height, bgColor=self.disabledBGColor, opacity=0.0)

    def BuildText(self, textContainerOpacity):
        self.textContainer = Container(name='textContainer', parent=self, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height, opacity=textContainerOpacity)
        self.label = Label(name='text', parent=self.textContainer, align=uiconst.CENTER, fontsize=self.fontsize, fontstyle=self.fontStyle, letterspace=self.letterspace, shadowOffset=(0, 0))
        self.SetText(self.text)
        self.SetTextColor(self.mouseUpTextColor)
        if self.boldText == ButtonTextBoldness.ALWAYS_BOLD:
            self.label.bold = True

    def StopBackgroundAnimations(self):
        uicore.animations.StopAllAnimations(self.mouseUpBG)
        uicore.animations.StopAllAnimations(self.mouseDownBG)
        uicore.animations.StopAllAnimations(self.mouseEnterBG)
        uicore.animations.StopAllAnimations(self.disabledBG)

    def SetText(self, text):
        self.text = text
        self.label.text = self.text.upper() if self.isCapitalized else self.text

    def SetTextColor(self, color):
        self.label.SetTextColor(color)
        _, _, _, opacity = color
        self.label.opacity = opacity

    def UpdateEnabledState(self):
        if self.disabledBG:
            self.StopBackgroundAnimations()
            isDisabled = self.IsDisabled()
            self.mouseUpBG.opacity = 0.0 if isDisabled else self.mouseUpBGOpacity
            self.disabledBG.opacity = self.disabledBGOpacity if isDisabled else 0.0
            textColor = self.disabledTextColor if isDisabled else self.mouseUpTextColor
            self.SetTextColor(textColor)

    def SetState(self, state):
        super(TextButtonWithBackgrounds, self).SetState(state)
        self.UpdateEnabledState()

    def IsDisabled(self):
        return self.pickState == uiconst.TR2_SPS_OFF

    def Enable(self, *args):
        super(TextButtonWithBackgrounds, self).Enable(*args)
        self.UpdateEnabledState()

    def Disable(self, *args):
        super(TextButtonWithBackgrounds, self).Disable(*args)
        self.UpdateEnabledState()

    def OnMouseDown(self, *args):
        self.StopBackgroundAnimations()
        self.mouseUpBG.opacity = 0.0
        self.mouseEnterBG.opacity = 0.0
        self.mouseDownBG.opacity = self.mouseDownBGOpacity
        self.SetTextColor(self.mouseDownTextColor)
        if self.boldText == ButtonTextBoldness.BOLD_ON_MOUSEOVER:
            self.label.bold = True

    def OnMouseUp(self, *args):
        self.StopBackgroundAnimations()
        uicore.animations.FadeOut(self.mouseDownBG, duration=self.bgFadeOutDuration)
        if uicore.uilib.mouseOver == self:
            startOpacity = self.mouseEnterBG.opacity
            endOpacity = self.mouseEnterBGOpacity
            uicore.animations.FadeTo(self.mouseEnterBG, startOpacity, endOpacity, duration=self.bgFadeInDuration)
            self.SetTextColor(self.mouseEnterTextColor)
            if self.boldText == ButtonTextBoldness.BOLD_ON_MOUSEOVER:
                self.label.bold = True
        else:
            startOpacity = self.mouseUpBG.opacity
            endOpacity = self.mouseUpBGOpacity
            uicore.animations.FadeTo(self.mouseUpBG, startOpacity, endOpacity, duration=self.bgFadeInDuration)
            self.SetTextColor(self.mouseUpTextColor)
            if self.boldText == ButtonTextBoldness.BOLD_ON_MOUSEOVER:
                self.label.bold = False

    def OnMouseEnter(self, *args):
        self.StopBackgroundAnimations()
        uicore.animations.FadeOut(self.mouseUpBG, duration=self.bgFadeOutDuration)
        uicore.animations.FadeOut(self.mouseDownBG, duration=self.bgFadeOutDuration)
        startOpacity = self.mouseEnterBG.opacity
        endOpacity = self.mouseEnterBGOpacity
        uicore.animations.FadeTo(self.mouseEnterBG, startOpacity, endOpacity, duration=self.bgFadeInDuration)
        self.SetTextColor(self.mouseEnterTextColor)
        if self.boldText == ButtonTextBoldness.BOLD_ON_MOUSEOVER:
            self.label.bold = True
        if self.hoverSound:
            self.audio.SendUIEvent(self.hoverSound)

    def OnMouseExit(self, *args):
        self.StopBackgroundAnimations()
        uicore.animations.FadeOut(self.mouseEnterBG, duration=self.bgFadeOutDuration)
        uicore.animations.FadeOut(self.mouseDownBG, duration=self.bgFadeOutDuration)
        startOpacity = self.mouseUpBG.opacity
        endOpacity = self.mouseUpBGOpacity
        uicore.animations.FadeTo(self.mouseUpBG, startOpacity, endOpacity, duration=self.bgFadeInDuration)
        self.SetTextColor(self.mouseUpTextColor)
        if self.boldText == ButtonTextBoldness.BOLD_ON_MOUSEOVER:
            self.label.bold = False

    def OnClick(self, *args):
        if self.selectedSound:
            self.audio.SendUIEvent(self.selectedSound)
        if self.func:
            self.ExecuteFunction()

    def ExecuteFunction(self):
        if type(self.args) == tuple:
            self.func(*self.args)
        elif self.args:
            self.func(self.args)
        else:
            self.func()

    def _OnResize(self, *args):
        if self.mouseUpBG:
            self.mouseUpBG.width = self.width
            self.mouseUpBG.height = self.height
        if self.mouseEnterBG:
            self.mouseUpBG.width = self.width
            self.mouseUpBG.height = self.height
        if self.mouseDownBG:
            self.mouseUpBG.width = self.width
            self.mouseUpBG.height = self.height
        if self.disabledBG:
            self.disabledBG.width = self.width
            self.disabledBG.height = self.height
