#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\aura.py
import localization
from carbonui import Align, TextBody, PickState, uiconst
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.util.dpi import ReverseScaleDpi
from eve.client.script.ui import eveColor

class AuraDailyGoalPanel(SectionAutoSize):
    default_mirrored = False
    default_opacity = 1.0
    default_state = uiconst.UI_NORMAL
    __notifyevents__ = ['OnUIScalingChange']

    def __init__(self, job, *args, **kwargs):
        self._job = job
        self._header_background = None
        self._tag_container = None
        super(AuraDailyGoalPanel, self).__init__(*args, **kwargs)
        sm.RegisterNotify(self)

    def Close(self):
        sm.UnregisterNotify(self)
        super(AuraDailyGoalPanel, self).Close()

    def _ConstructHeader(self):
        header_container = Container(name='header_container', parent=self, align=Align.TOTOP, height=32)
        self._header_background = StretchSpriteHorizontal(name='header_background', parent=header_container, align=Align.NOALIGN, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_slant.png', color=eveColor.AURA_PURPLE, opacity=0.1, height=32, rightEdgeSize=26)
        self._tag_container = ContainerAutoSize(name='tag_container', parent=header_container, align=Align.TOLEFT, height=32)
        icon_container = Container(name='icon_container', parent=self._tag_container, align=Align.TOLEFT, width=16, padLeft=8)
        Sprite(name='aura_icon', parent=icon_container, align=Align.CENTERLEFT, texturePath='res:/UI/Texture/classes/careerPortal/aura/aura_icon_16x16.png', width=16, height=16)
        label_text = localization.GetByLabel('UI/CareerPortal/AuraAssistancePanelTitle')
        label_width, _ = TextBody.MeasureTextSize(label_text)
        label_container = Container(name='icon_container', parent=self._tag_container, align=Align.TOLEFT, padding=(8, 7, 8, 0), width=label_width + 16)
        TextBody(name='title_label', parent=label_container, align=Align.TOTOP, text=label_text, bold=True, color=eveColor.AURA_PURPLE)
        self._update_header_background()

    def _ConstructMainContainer(self):
        super(AuraDailyGoalPanel, self)._ConstructMainContainer()
        TextBody(name='description_label', parent=self.mainCont, align=Align.TOTOP, pickState=PickState.ON, text=self._job.help_text)

    def _update_header_background(self):
        if self._tag_container is None or self._header_background is None:
            return
        tag_width, _ = self._tag_container.GetAutoSize()
        if tag_width is None:
            return
        self._header_background.width = tag_width + ReverseScaleDpi(25)

    def OnUIScalingChange(self, *args):
        self._update_header_background()

    def OnGlobalFontSizeChanged(self):
        super(AuraDailyGoalPanel, self).OnGlobalFontSizeChanged()
        self._update_header_background()
