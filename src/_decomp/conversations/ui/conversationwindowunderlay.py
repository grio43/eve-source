#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\conversations\ui\conversationwindowunderlay.py
import trinity
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from conversations.ui.conversationwindowstyle import has_background_settings
from carbonui.window.underlay import BaseWindowUnderlay

class ConversationWindowUnderlay(BaseWindowUnderlay):

    def ApplyAttributes(self, attributes):
        super(ConversationWindowUnderlay, self).ApplyAttributes(attributes)
        self.style = None

    def ApplyStyle(self, style):
        self.style = style
        self.Flush()
        if not has_background_settings(self.style):
            return
        self.add_styled_header_bar_background()
        self.add_styled_background_glow()
        self.add_styled_background()

    def add_styled_header_bar_background(self):
        styled_header_bar_background_container = Container(parent=self, align=uiconst.TOALL, name='styledHeaderBarBackgroundContainer')
        Frame(bgParent=styled_header_bar_background_container, name='styledHeaderBarBackground', texturePath=self.style.header_bar_background_texture, cornerSize=self.style.header_bar_background_corner_size)

    def add_styled_background(self):
        styled_background_container = Container(parent=self, align=uiconst.TOALL, name='styledBackgroundContainer')
        Frame(bgParent=styled_background_container, name='styledBackground', texturePath=self.style.background_texture, cornerSize=self.style.background_corner_size)
        BlurredBackgroundSprite(bgParent=styled_background_container, name='styledBackgroundBlur', color=self.style.background_blur_color, align=uiconst.TOALL)

    def add_styled_background_glow(self):
        outer_padding = self.style.background_glow_outer_padding
        styled_background_glow_container = Container(parent=self, align=uiconst.TOALL, name='styledBackgroundGlowContainer', padding=-outer_padding)
        Frame(bgParent=styled_background_glow_container, name='auraStyleBackgroundGlow', align=uiconst.TOALL, texturePath=self.style.background_glow_texture, cornerSize=self.style.background_glow_corner_size, blendMode=trinity.TR2_SBM_ADD)


class BlurredBackgroundSprite(Sprite):
    __notifyevents__ = ['OnBlurredBufferCreated']
    default_name = 'BlurredBackgroundSprite'
    default_state = uiconst.UI_DISABLED
    default_spriteEffect = trinity.TR2_SFX_BLURBACKGROUND

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        if uicore.uilib.blurredBackBufferAtlas:
            self.texture.atlasTexture = uicore.uilib.blurredBackBufferAtlas
        trinity.device.RegisterResource(self)

    def OnCreate(self, *args):
        pass

    def OnBlurredBufferCreated(self, *args):
        if not self.destroyed:
            self.texture.atlasTexture = uicore.uilib.blurredBackBufferAtlas
