#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\buyPlexButton.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.shared.vgs.const import COLOR_PLEX
from fastcheckout.const import FROM_WALLET_PLUS_BUTTON
from localization import GetByLabel
DEFAULT_OPACITY = 0.3
MOUSE_HOVER_OPACITY = 0.75
MOUSE_DOWN_OPACITY = 0.55

class BuyPlexButton(Container):
    default_width = 16
    default_height = 16
    default_state = uiconst.UI_NORMAL
    default_hint = GetByLabel('UI/VirtualGoodsStore/Buttons/BuyPlex')

    def ApplyAttributes(self, attributes):
        super(BuyPlexButton, self).ApplyAttributes(attributes)
        self.ConstructLayout()

    def ConstructLayout(self):
        self.icon = Sprite(name='icon', parent=self, align=uiconst.CENTER, height=14, width=14, texturePath='res:/UI/Texture/Shared/DarkStyle/buttonIconPlus.png', state=uiconst.UI_DISABLED)
        self.fill = Frame(parent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/buttonSmall_Solid.png', cornerSize=6, color=COLOR_PLEX, opacity=DEFAULT_OPACITY)
        self.stroke = Frame(parent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/buttonSmall_Stroke.png', cornerSize=6, color=COLOR_PLEX, opacity=0.75)

    def OnClick(self, *args):
        self.BuyPlex()

    def BuyPlex(self):
        uicore.cmd.CmdBuyPlex(FROM_WALLET_PLUS_BUTTON)

    def OnMouseEnter(self, *args):
        self.fill.SetAlpha(MOUSE_HOVER_OPACITY)

    def OnMouseExit(self, *args):
        self.fill.SetAlpha(DEFAULT_OPACITY)

    def OnMouseDown(self, *args):
        self.fill.SetAlpha(MOUSE_DOWN_OPACITY)

    def OnMouseUp(self, *args):
        self.fill.SetAlpha(MOUSE_HOVER_OPACITY)
