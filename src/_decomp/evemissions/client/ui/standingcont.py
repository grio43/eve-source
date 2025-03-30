#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemissions\client\ui\standingcont.py
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from eve.common.script.util.standingUtil import OpenStandingsPanelOnOwnerByID
from carbon.common.script.util.format import FmtAmt
from localization import GetByLabel
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.gauge import Gauge
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveLabel
from carbonui.primitives.container import Container
from carbonui import const as uiconst

class StandingCont(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(StandingCont, self).ApplyAttributes(attributes)
        self.npc_character_id = attributes.npc_character_id
        self.standings_label = eveLabel.EveLabelMedium(name='standings_value', parent=self, align=uiconst.TOTOP, text=GetByLabel('UI/Common/Standing'))
        standing_bar = Container(name='standing_bar', parent=self, align=uiconst.TOTOP, height=8, top=10)
        background_color = eveColor.WHITE
        background_color_gauge = background_color[:3] + (0.2,)
        background_color_marker = background_color[:3] + (0.1,)
        self.standings_gauge = Gauge(name='standings_gauge', parent=standing_bar, align=uiconst.TOTOP, color=eveColor.CRYO_BLUE, backgroundColor=background_color_gauge, state=uiconst.UI_PICKCHILDREN)
        self.standings_gauge.gaugeCont.state = uiconst.UI_PICKCHILDREN
        self.bar_increase_parent = Container(name='bar_increase_parent', parent=self.standings_gauge, align=uiconst.TOALL, state=uiconst.UI_NORMAL, clipChildren=True, idx=0, padLeft=-1)
        self.bar_increase_offset = Container(name='bar_increase_offset', parent=self.bar_increase_parent, align=uiconst.TOLEFT_PROP, state=uiconst.UI_NORMAL, width=0.0, clipChildren=True)
        self.bar_increase = Container(name='bar_increase', parent=self.bar_increase_parent, align=uiconst.TOLEFT_PROP, state=uiconst.UI_NORMAL, width=0.0, clipChildren=True)
        self.bar_increase.OnClick = self.OnClick
        self.sprite_increase = Sprite(name='arrow_sprite_increase', bgParent=self.bar_increase, texturePath='res:/UI/Texture/Classes/AgentInteraction/increaseLine.png', opacity=1.0, tileX=True, align=uiconst.CENTERLEFT, color=eveColor.SUCCESS_GREEN)
        numMarkers = 10
        for i in xrange(1, numMarkers):
            self.standings_gauge.ShowMarker(float(i) / numMarkers, color=background_color_marker)

    def update_with_standings(self, value, value_with_gains = 0):
        gauge_value = value * 0.1
        color = eveColor.CRYO_BLUE
        if value < 0:
            gauge_value = -gauge_value
            color = eveColor.CHERRY_RED
        self.standings_gauge.SetValue(gauge_value, animate=False)
        self.standings_gauge.SetColor(color)
        formatted_value = FmtAmt(value, showFraction=2)
        text = '%s: %s ' % (GetByLabel('UI/Common/Standing'), formatted_value)
        self.standings_label.text = text
        if FloatCloseEnough(value, value_with_gains) or value > value_with_gains:
            gain_width = 0
            hint = ''
        else:
            increase = value_with_gains - value
            gain_width = max(0.3, increase)
            hint = GetByLabel('UI/Common/StandingsGain', standing=round(increase, 2))
            if value < 0:
                increase_aligment = uiconst.TORIGHT_PROP
                offset_width = 1 + value * 0.1
                color = eveColor.WHITE
            else:
                increase_aligment = uiconst.TOLEFT_PROP
                offset_width = value * 0.1
                color = eveColor.SUCCESS_GREEN
            self.bar_increase_offset.align = increase_aligment
            self.bar_increase.align = increase_aligment
            self.bar_increase_offset.width = offset_width
            self.sprite_increase.SetRGBA(*color)
        self.bar_increase.width = gain_width * 0.1
        self.bar_increase.hint = hint

    def OnClick(self, *args):
        OpenStandingsPanelOnOwnerByID(self.npc_character_id)

    def OnMouseEnter(self, *args):
        self.standings_gauge.opacity = 1.2

    def OnMouseExit(self, *args):
        self.standings_gauge.opacity = 1.0
