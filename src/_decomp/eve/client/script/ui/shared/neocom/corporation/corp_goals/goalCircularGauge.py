#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_goals\goalCircularGauge.py
from carbonui import uiconst, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.donutSegment import DonutSegment
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.shared.neocom.corporation.corp_goals import goalColors
LINE_WIDTH = 2

class GoalCircularGauge(Container):
    default_radius = 20
    default_showLabel = True

    def ApplyAttributes(self, attributes):
        super(GoalCircularGauge, self).ApplyAttributes(attributes)
        radius = attributes.radius
        showLabel = attributes.get('showLabel', self.default_showLabel)
        self.width = self.height = 2 * radius
        self._goal_state = None
        self.gauge = GaugeCircular(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, radius=radius - 6, showMarker=False, lineWidth=2, glow=True, glowBrightness=0.5, colorBg=(0, 0, 0, 0.9))
        GaugeCircular(name='background_gauge', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, radius=radius, showMarker=False, lineWidth=14, colorBg=(0, 0, 0, 0.9))
        Sprite(bgParent=self, texturePath='res:/UI/Texture/circle_full.png', color=eveColor.BLACK, opacity=0.2)
        if showLabel:
            self.progressLabel = eveLabel.EveLabelLarge(parent=self, align=uiconst.CENTER, color=TextColor.SECONDARY)
        else:
            self.progressLabel = None

    def SetValue(self, value, goal_state, animate = True):
        self._goal_state = goal_state
        self.gauge.SetValue(value, animate)
        self._UpdateGaugeColor()
        if self.progressLabel:
            self.progressLabel.SetText(u'{value}%'.format(value=int(value * 100)))

    def _UpdateGaugeColor(self):
        if self._goal_state:
            color = goalColors.get_color(self._goal_state)
            self.gauge.SetColor(color, color)

    def OnColorThemeChanged(self):
        self._UpdateGaugeColor()
