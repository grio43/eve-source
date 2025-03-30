#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\drones\dronesWarpWarning.py
import math
import localization
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.services.setting import CharSettingBool
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.inflight.drones.dronesUtil import stop_and_recall_drones
warp_warning_enabled_setting = CharSettingBool('drone_warp_warning_enabled', True)

class WarpWarning(ContainerAutoSize):
    default_alignMode = uiconst.TOTOP
    default_opacity = 0.0

    def __init__(self, **kwargs):
        super(WarpWarning, self).__init__(**kwargs)
        self.constructed = False
        self.is_active = False
        self.whiteout = None

    def layout(self):
        self.whiteout = Container(parent=self, align=uiconst.TOALL, bgColor=(1.0, 1.0, 1.0), opacity=0.5)
        Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', rotation=math.pi, cornerSize=9, color=eveColor.WARNING_ORANGE, opacity=0.15)
        Sprite(name='cornerSprite', parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/DarkStyle/cornerTriSmall.png', width=5, height=5, color=eveColor.WARNING_ORANGE, opacity=0.5)
        warning_icon = Sprite(name='warningIcon', parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=32, height=32, left=10, top=8, texturePath='res:/UI/Texture/classes/agency/iconExclamation.png', color=eveColor.WARNING_ORANGE)
        animations.FadeTo(warning_icon, startVal=0.5, endVal=1.5, duration=0.7, loops=-1, curveType=uiconst.ANIM_WAVE)
        EveLabelMedium(name='warningLabel', parent=self, align=uiconst.TOTOP, padding=(52, 8, 8, 8), text=localization.GetByLabel('UI/Drones/WarpWarningMessage'), color=eveColor.WARNING_ORANGE)
        button_row_cont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, padding=(52, 0, 8, 8))
        Button(parent=button_row_cont, align=uiconst.TOPLEFT, label=localization.GetByLabel('UI/Drones/StopAndRecall'), func=stop_and_recall_drones, args=())
        self.constructed = True

    def FadeIn(self):
        if not self.constructed:
            self.layout()
        if self.is_active:
            return
        self.is_active = True
        sm.GetService('audio').SendUIEvent('ui_warning_abandoning_drones')
        self.Show()
        animations.StopAllAnimations(self)
        animations.FadeIn(self, duration=0.3)
        animations.FadeTo(self.whiteout, startVal=0.0, endVal=1.0, duration=0.3, timeOffset=0.1, curveType=uiconst.ANIM_WAVE)

    def FadeOut(self):
        if not self.constructed:
            return
        self.is_active = False
        animations.StopAllAnimations(self.whiteout)
        animations.FadeOut(self.whiteout, duration=0.1)
        animations.FadeOut(self, duration=0.3, callback=self.Hide)
