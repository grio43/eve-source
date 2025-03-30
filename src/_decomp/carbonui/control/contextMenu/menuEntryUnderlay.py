#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\contextMenu\menuEntryUnderlay.py
from carbonui import uiconst
from carbonui.primitives.fill import Fill
from carbonui.uicore import uicore
from eve.client.script.ui import eveThemeColor, eveColor
import trinity

class MenuEntryUnderlay(Fill):
    OPACITY_IDLE = 0.0
    OPACITY_HOVER = 0.2
    OPACITY_SELECTED = 0.4
    default_color = eveThemeColor.THEME_FOCUSDARK
    default_opacity = OPACITY_IDLE
    default_padBottom = 1
    default_outputMode = trinity.Tr2SpriteTarget.COLOR_AND_GLOW
    default_glowBrightness = 0.3

    def OnMouseEnter(self):
        uicore.animations.FadeTo(self, self.opacity, self.OPACITY_HOVER, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        uicore.animations.FadeTo(self, self.opacity, self.OPACITY_IDLE, duration=uiconst.TIME_EXIT)

    def OnMouseDown(self, *args):
        uicore.animations.SpColorMorphTo(self, self.GetRGBA(), eveColor.WHITE, duration=uiconst.TIME_MOUSEDOWN)

    def OnMouseUp(self, *args):
        color = list(self.default_color[:])
        color[3] = self.OPACITY_HOVER
        uicore.animations.SpColorMorphTo(self, self.GetRGBA(), color, duration=uiconst.TIME_MOUSEUP)

    def OnColorThemeChanged(self):
        super(MenuEntryUnderlay, self).OnColorThemeChanged()
        self.SetRGBA(*(self.default_color[:3] + (self.opacity,)))
