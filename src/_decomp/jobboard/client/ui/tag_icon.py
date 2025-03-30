#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\tag_icon.py
from carbonui import Align, PickState, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveThemeColor

class TagIcon(Container):
    default_height = 20
    default_width = 20
    CIRCLE_LARGE = 'res:/UI/Texture/circle_full.png'
    CIRCLE_SMALL = 'res:/UI/Texture/Shared/bg_circle.png'

    def __init__(self, *args, **kwargs):
        self._underlayColor = None
        self._icon = None
        self._iconOutputMode = None
        self._iconGlowBrightness = None
        self._bg = None
        super(TagIcon, self).__init__(*args, **kwargs)

    def ApplyAttributes(self, attributes):
        super(TagIcon, self).ApplyAttributes(attributes)
        texturePath = attributes.texturePath
        underlayTexturePath = attributes.get('underlayTexturePath', self.CIRCLE_SMALL)
        self._underlayColor = attributes.get('underlayColor', eveThemeColor.THEME_FOCUSDARK)
        self._iconOutputMode = attributes.get('iconOutputMode', Sprite.default_outputMode)
        self._iconGlowBrightness = attributes.get('iconGlowBrightness', Sprite.default_glowBrightness)
        iconWidth = attributes.get('iconWidth', 16)
        iconHeight = attributes.get('iconHeight', 16)
        iconColor = attributes.get('iconColor', TextColor.SECONDARY)
        self._icon = Sprite(name='icon', parent=self, texturePath=texturePath, align=Align.CENTER, pickState=PickState.OFF, outputMode=self._iconOutputMode, glowBrightness=self._iconGlowBrightness, width=iconWidth, height=iconHeight, color=iconColor)
        self._bg = Sprite(bgParent=self, texturePath=underlayTexturePath, color=self._underlayColor, opacity=0.5)

    def OnColorThemeChanged(self):
        super(TagIcon, self).OnColorThemeChanged()
        if self._bg and self._underlayColor:
            self._bg.rgb = self._underlayColor[:3]
