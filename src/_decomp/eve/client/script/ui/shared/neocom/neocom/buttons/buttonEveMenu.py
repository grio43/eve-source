#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\buttonEveMenu.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.themeColored import FillThemeColored, SpriteThemeColored
from eve.client.script.ui.shared.neocom.neocom.buttons.baseNeocomButton import BaseNeocomButton
from eve.client.script.ui.shared.neocom.neocom.buttons.neocomButtonConst import COLOR_HOVER
from eve.client.script.ui.tooltips.tooltipUtil import RefreshTooltipForOwner
import trinity

class ButtonEveMenu(BaseNeocomButton):
    default_isDraggable = False
    default_adjustPositionManually = False

    def ApplyAttributes(self, attributes):
        super(ButtonEveMenu, self).ApplyAttributes(attributes)
        self._openNeocomPanel = None
        Fill(bgParent=self, color=(0, 0, 0, 0.4))

    def ConstructIcon(self):
        self.icon = Sprite(parent=self, name='EVEMenuIcon', align=uiconst.TOPLEFT_PROP, state=uiconst.UI_DISABLED, pos=(0.5, 0.5, 0.5, 0.5), minWidth=20, minHeight=20, idx=0, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0)

    def ConstructBlinkSprite(self):
        self.blinkSprite = Sprite(parent=self, name='blinkSprite', align=uiconst.TOPLEFT_PROP, pos=(0.5, 0.5, 0.55, 0.55), minWidth=24, minHeight=24, state=uiconst.UI_HIDDEN, texturePath=self.icon.texturePath, outputMode=uiconst.OUTPUT_GLOW, blendMode=trinity.TR2_SBM_ADD)

    def OnClick(self, *args):
        self.ToggleNeocomPanel()
        self.btnData.CheckContinueBlinking()

    def _GetTexturePath(self):
        return 'res:/UI/Texture/Icons/79_64_11.png'

    def GetIconColor(self):
        if uicore.uilib.mouseOver == self:
            return COLOR_HOVER
        else:
            return eveColor.PLATINUM_GREY

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self._IsNeocomPanelOpen():
            return
        tooltipPanel.LoadGeneric3ColumnTemplate()
        cmd = uicore.cmd.commandMap.GetCommandByName('OpenEveMenu')
        tooltipPanel.AddCommandTooltip(cmd)

    def ToggleNeocomPanel(self):
        isOpen = self._IsNeocomPanelOpen()
        sm.GetService('neocom').CloseAllPanels()
        if isOpen:
            self._openNeocomPanel = None
            PlaySound(uiconst.SOUND_COLLAPSE)
        else:
            self._openNeocomPanel = sm.GetService('neocom').ShowEveMenu()
        RefreshTooltipForOwner(self)

    def _IsNeocomPanelOpen(self):
        return self._openNeocomPanel and not self._openNeocomPanel.destroyed

    def GetMenu(self):
        return sm.GetService('neocom').GetMenu()
