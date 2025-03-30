#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\newFeatures\newFeatureNotifyButton.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import Label
from carbonui.primitives.frame import Frame
COLOR_IDLE = (0.5, 0.5, 0.5, 1.0)
COLOR_HOVER = (1, 1, 1, 0.5)

class NewFeatureButton(Container):
    default_state = uiconst.UI_NORMAL
    default_color = (0.0, 0.0, 0.0, 1.0)
    default_fill_color = (1.0, 1.0, 1.0, 0.9)
    default_fontSize = 14
    default_upperCase = True
    default_stretchTexturePath = 'res:/UI/Texture/Classes/NewFeatureNotify/button.png'
    default_hiliteTexturePath = 'res:/UI/Texture/Classes/NewFeatureNotify/button.png'
    default_textureEdgeSize = 8
    default_hoverSound = 'upgrade_menu_button_hover_play'
    default_clickSound = 'upgrade_future_play'
    default_isBold = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        text = attributes.text
        self.labelColor = attributes.get('labelColor', self.default_color)
        self.fillColor = attributes.get('fillColor', self.default_fill_color)
        self.onMouseEnterCallback = attributes.onMouseEnterCallback
        self.onMouseExitCallback = attributes.onMouseExitCallback
        self.onClick = attributes.onClick
        self.fontSize = attributes.get('fontSize', self.default_fontSize)
        self.upperCase = attributes.get('upperCase', self.default_upperCase)
        self.stretchTexturePath = attributes.get('stretchTexturePath', self.default_stretchTexturePath)
        self.textureEdgeSize = attributes.get('textureEdgeSize', self.default_textureEdgeSize)
        self.hiliteTexturePath = attributes.get('hiliteTexturePath', self.default_hiliteTexturePath)
        self.hoverSound = attributes.get('hoverSound', self.default_hoverSound)
        self.clickSound = attributes.get('clickSound', self.default_clickSound)
        self.buttonColor = attributes.get('buttonColor', COLOR_IDLE)
        self.hoverColor = attributes.get('hoverColor', COLOR_HOVER)
        self.mouseLeaveColor = attributes.get('mouseLeaveColor', self.buttonColor)
        self.isBold = attributes.get('isBold', self.default_isBold)
        self.label = Label(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, text=text, fontsize=self.fontSize, bold=self.isBold, color=self.labelColor)
        self.hilite = Frame(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=self.hiliteTexturePath, cornerSize=self.textureEdgeSize, opacity=0.0)
        self.bg = Frame(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=self.stretchTexturePath, cornerSize=self.textureEdgeSize, color=self.buttonColor)

    def SetText(self, text):
        self.label.SetText(text)

    def OnMouseEnter(self, *args):
        if self.hoverSound is not None:
            PlaySound(self.hoverSound)
        animations.SpColorMorphTo(self.hilite, self.hoverColor, self.fillColor, duration=0.3)
        if self.onMouseEnterCallback:
            self.onMouseEnterCallback()

    def OnMouseExit(self, *args):
        duration = 0.15
        animations.SpColorMorphTo(self.hilite, self.hilite.GetRGBA(), self.mouseLeaveColor, duration=duration)
        if self.onMouseExitCallback:
            self.onMouseExitCallback()

    def OnClick(self, *args):
        if self.clickSound is not None:
            PlaySound(self.clickSound)
        self.onClick()
        animations.SpColorMorphTo(self.label, self.label.GetRGBA(), self.labelColor, duration=0.3)
        animations.SpColorMorphTo(self.hilite, (1.0, 1.0, 1.0, 1.0), self.mouseLeaveColor, duration=0.3)
