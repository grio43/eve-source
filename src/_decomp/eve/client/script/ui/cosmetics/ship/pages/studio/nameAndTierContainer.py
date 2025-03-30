#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\nameAndTierContainer.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from eve.client.script.ui.cosmetics.ship.const import ANIM_DURATION_LONG
from eve.client.script.ui.cosmetics.ship.pages.studio.skinNameEntry import SkinNameEntry
from eve.client.script.ui.cosmetics.ship.pages.studio.studioUtil import get_circular_layout_radius
from eve.client.script.ui.cosmetics.ship.pages.studio.tierGauge import TierGauge
from eve.client.script.ui.cosmetics.ship.pages.studio.currentDesignTierIndicator import CurrentDesignTierIndicator

class NameAndTierContainer(Container):

    def __init__(self, **kw):
        super(NameAndTierContainer, self).__init__(**kw)
        self.tier_gauge = TierGauge(name='tier_gauge', parent=self)
        self.tier_indicator = CurrentDesignTierIndicator(name='tier_indicator', parent=self)
        self.skin_name_entry = SkinNameEntry(name='skin_name_entry', parent=self)
        self.on_size_changed.connect(self._on_size_changed)

    def LoadPanel(self, animate = True):
        self.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self, self.opacity, 1.0, duration=0.6, timeOffset=ANIM_DURATION_LONG)
        self.skin_name_entry.update_text()
        self.tier_indicator.update_tier()
        self.tier_gauge.update_tier_values()

    def UnloadPanel(self, animate = True):
        self.Disable()
        animations.FadeTo(self, self.opacity, 0.0, duration=0.2, callback=self.Hide)

    def _on_size_changed(self, width, height):
        radius = get_circular_layout_radius(*self.GetAbsoluteSize())
        self.tier_gauge.radius = radius
        self.tier_indicator.radius = radius
        self.skin_name_entry.radius = radius
