#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\overflowButton.py
import math
import eveicon
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.shared.neocom.neocom import neocomPanels, neocomConst, neocomSettings
from eve.client.script.ui.shared.neocom.neocom.buttons.wrapperButton import WrapperButton
from eve.client.script.ui.tooltips.tooltipUtil import RefreshTooltipForOwner

class OverflowButton(WrapperButton):
    __notifyevents__ = ['OnNeocomPanelsClosed']
    default_state = uiconst.UI_HIDDEN
    default_name = 'overflowButtonCont'
    default_pos = (0, 0, 20, 0)

    def ApplyAttributes(self, attributes):
        super(OverflowButton, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self._openNeocomPanel = None
        self.icon = Sprite(parent=self, width=16, height=16, align=uiconst.CENTER, state=uiconst.UI_DISABLED, blendMode=trinity.TR2_SBM_ADD, color=eveColor.SILVER_GREY, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0)
        self.UpdateIconRotation()

    def UpdateIconRotation(self):
        isLeftAligned = neocomSettings.neocom_align_setting.is_equal(uiconst.TOLEFT)
        self.icon.texturePath = eveicon.caret_right if isLeftAligned else eveicon.caret_left

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.ToggleNeocomPanel()

    def OnMouseEnter(self, *args):
        super(OverflowButton, self).OnMouseEnter(*args)
        animations.MorphScalar(self.icon, 'glowBrightness', self.mouseHoverSprite.glowBrightness, 0.4, duration=uiconst.TIME_ENTRY)
        animations.SpColorMorphTo(self.icon, self.icon.rgba, eveColor.WHITE, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        super(OverflowButton, self).OnMouseExit(*args)
        animations.MorphScalar(self.icon, 'glowBrightness', self.mouseHoverSprite.glowBrightness, 0.0, duration=uiconst.TIME_EXIT)
        animations.SpColorMorphTo(self.icon, self.icon.rgba, eveColor.SILVER_GREY, duration=uiconst.TIME_ENTRY)

    def OnDblClick(self, *args):
        pass

    def ToggleNeocomPanel(self):
        isOpen = self._openNeocomPanel and not self._openNeocomPanel.destroyed
        sm.GetService('neocom').CloseAllPanels()
        if isOpen:
            self._openNeocomPanel = None
        else:
            self._openNeocomPanel = sm.GetService('neocom').ShowPanel(self, neocomPanels.PanelOverflow, neocomConst.PANEL_SHOWONSIDE, parent=uicore.layer.abovemain, btnData=None)
        RefreshTooltipForOwner(self)

    def BlinkOnMinimize(self):
        self.BlinkOnce()

    def ProcessNeocomBlinkPulse(self):
        for btnData in sm.GetService('neocom').GetNeocomContainer().overflowButtons:
            if btnData.IsBlinking():
                self.BlinkOnce()
                return
