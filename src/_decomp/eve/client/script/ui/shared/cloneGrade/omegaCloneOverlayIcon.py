#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\omegaCloneOverlayIcon.py
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
import carbonui.const as uiconst
from carbonui.uianimations import animations
from localization import GetByLabel
from eve.client.script.ui.shared.cloneGrade import cloneStateUtil
OPACITY_FRAME_IDLE = 0.7
OPACITY_FRAME_HOVER = 1.0

class OmegaCloneOverlayIcon(Container):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_iconSize = 40

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.cloneGradeSvc = sm.GetService('cloneGradeSvc')
        iconSize = attributes.get('iconSize', self.default_iconSize)
        self.origin = attributes.origin
        self.reason = attributes.reason
        self.frame = Frame(name='frame', parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/Classes/CloneGrade/Omega_Overlay_1_64.png', opacity=OPACITY_FRAME_IDLE)
        self.iconCont = Container(name='iconCont', parent=self, state=uiconst.UI_DISABLED, bgColor=(0.0, 0.0, 0.0, 0.75), opacity=0.0)
        Sprite(name='icon', parent=self.iconCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/Classes/CloneGrade/omega_icon.png', pos=(0,
         0,
         iconSize,
         iconSize))

    def IsRestricted(self):
        return not self.cloneGradeSvc.IsOmega()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if not self.IsRestricted():
            text = GetByLabel('UI/CloneState/RequiresOmegaCloneIsOmega')
        else:
            text = GetByLabel('UI/CloneState/RequiresOmegaClone')
        cloneStateUtil.LoadTooltipPanel(tooltipPanel, text, self.origin, self.reason)

    def OnMouseEnter(self, *args):
        if self.IsRestricted():
            animations.FadeTo(self.iconCont, self.iconCont.opacity, 1.0, duration=0.15)
        animations.FadeTo(self.frame, self.frame.opacity, OPACITY_FRAME_HOVER, duration=0.15)

    def OnMouseExit(self, *args):
        if self.IsRestricted():
            animations.FadeTo(self.iconCont, self.iconCont.opacity, 0.0, duration=0.3)
        animations.FadeTo(self.frame, self.frame.opacity, OPACITY_FRAME_IDLE, duration=0.3)
