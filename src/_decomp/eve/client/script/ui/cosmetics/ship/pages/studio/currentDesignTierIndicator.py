#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\currentDesignTierIndicator.py
from carbonui import Align, uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from cosmetics.client.ships.qa.menus import is_qa, get_qa_menu_for_tier_points
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from eve.client.script.ui.cosmetics.ship.controls.tierIndicator import TierIndicator
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from localization import GetByLabel

class CurrentDesignTierIndicator(Container):
    default_align = Align.CENTER
    default_state = uiconst.UI_NORMAL
    default_height = 58
    default_width = 336

    def __init__(self, *args, **kwargs):
        super(CurrentDesignTierIndicator, self).__init__(*args, **kwargs)
        self._radius = 0.0
        self.construct_layout()
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(CurrentDesignTierIndicator, self).Close()

    def connect_signals(self):
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)
        current_skin_design_signals.on_tier_level_changed.connect(self.on_tier_level_changed)
        current_skin_design_signals.on_design_reset.connect(self.on_design_reset)
        current_skin_design_signals.on_existing_design_loaded.connect(self.on_existing_design_loaded)
        studioSignals.on_scene_zoom.connect(self.on_scene_zoom)

    def disconnect_signals(self):
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.on_slot_fitting_changed)
        current_skin_design_signals.on_tier_level_changed.disconnect(self.on_tier_level_changed)
        current_skin_design_signals.on_design_reset.disconnect(self.on_design_reset)
        current_skin_design_signals.on_existing_design_loaded.disconnect(self.on_existing_design_loaded)
        studioSignals.on_scene_zoom.disconnect(self.on_scene_zoom)

    def construct_layout(self):
        self.tier_indicator = TierIndicator(parent=self, align=Align.CENTER)
        self.update_tier()

    def get_skin_tier_level(self):
        return current_skin_design.get().tier_level

    def on_slot_fitting_changed(self, slot_id, component_instance):
        self.update_tier()

    def on_tier_level_changed(self, tier_level):
        self.update_tier()

    def on_design_reset(self, *args):
        self.update_tier()

    def on_existing_design_loaded(self, *args):
        self.update_tier()

    def update_tier(self):
        self.tier_indicator.set_tier(self.get_skin_tier_level())

    def on_scene_zoom(self, is_zoomed):
        target_opacity = 0.0 if is_zoomed else 1.0
        animations.FadeTo(self, self.opacity, target_opacity, duration=0.15)

    def update_radial_position(self):
        self.top = self._radius - self.height

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self.update_radial_position()

    def GetMenu(self):
        if is_qa():
            return get_qa_menu_for_tier_points()

    @property
    def hint(self):
        hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/TierIndicatorHint')
        if is_qa():
            tier_level = current_skin_design.get().tier_level
            tier_tresholds = current_skin_design.get().tier_thresholds
            max_value = tier_tresholds.get_threshold_for_tier(tier_level)
            min_value = tier_tresholds.get_threshold_for_tier(tier_level - 1) + 1 if tier_level > 1 else 0
            hint += u'\n\nQA: Current Tier: {tier} ({min} - {max})\nCurrent Points: {points}'.format(tier=tier_level, min=min_value, max=max_value, points=current_skin_design.get().tier_points)
        return hint
