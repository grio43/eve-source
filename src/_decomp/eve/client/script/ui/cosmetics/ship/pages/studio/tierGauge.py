#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\tierGauge.py
import math
from carbonui import Align, TextBody
from carbonui.primitives.container import Container
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals, studioUtil

class TierGauge(Container):
    ANGLE_DEG = 30
    ANGLE_OFFSET_DEG = 1.8

    def __init__(self, *args, **kwargs):
        super(TierGauge, self).__init__(*args, **kwargs)
        self._radius = 0.0
        self.construct_layout()
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(TierGauge, self).Close()

    def connect_signals(self):
        current_skin_design_signals.on_tier_level_changed.connect(self.on_tier_level_changed)
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)
        current_skin_design_signals.on_design_reset.connect(self.on_design_reset)
        current_skin_design_signals.on_existing_design_loaded.connect(self.on_existing_design_loaded)
        studioSignals.on_scene_zoom.connect(self.on_scene_zoom)

    def disconnect_signals(self):
        current_skin_design_signals.on_tier_level_changed.disconnect(self.on_tier_level_changed)
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.on_slot_fitting_changed)
        current_skin_design_signals.on_design_reset.disconnect(self.on_design_reset)
        current_skin_design_signals.on_existing_design_loaded.disconnect(self.on_existing_design_loaded)
        studioSignals.on_scene_zoom.disconnect(self.on_scene_zoom)

    def construct_layout(self):
        self.gauge = GaugeCircular(name='gauge', parent=self, align=Align.CENTER, lineWidth=5.0, startAngle=math.radians(90 - self.ANGLE_DEG * 0.5), angle=math.radians(self.ANGLE_DEG), clockwise=False, showMarker=False, colorStart=eveColor.CRYO_BLUE, colorEnd=eveColor.CRYO_BLUE, value=0.0)
        self.current_tier_container = Transform(name='current_tier_container', parent=self, align=Align.CENTER)
        self.current_tier_label = TextBody(name='current_tier_label', parent=self.current_tier_container, align=Align.CENTER, padBottom=7, padLeft=3)
        self.next_tier_container = Transform(name='next_tier_container', parent=self, align=Align.CENTER)
        self.next_tier_label = TextBody(name='next_tier_label', parent=self.next_tier_container, align=Align.CENTER, padBottom=7)
        self.update_tier_values()

    def update_tier_values(self):
        tier_tresholds = current_skin_design.get().tier_thresholds
        tier_level = current_skin_design.get().tier_level
        if tier_level < tier_tresholds.get_max_tier():
            self.current_tier_label.text = '{tier}'.format(tier=tier_level)
            self.next_tier_label.text = '{tier}'.format(tier=tier_level + 1)
        else:
            self.current_tier_label.text = ''
            self.next_tier_label.text = '{tier}'.format(tier=tier_level)
        if tier_tresholds:
            tier_points = current_skin_design.get().tier_points
            max_value = tier_tresholds.get_threshold_for_tier(tier_level)
            if tier_level > 1:
                min_value = tier_tresholds.get_threshold_for_tier(tier_level - 1)
            else:
                min_value = 0
            if max_value is not None:
                gauge_value = float(tier_points - min_value) / float(max_value - min_value)
            else:
                gauge_value = 1
            self.gauge.SetValue(gauge_value)
        else:
            self.gauge.SetValue(0.0)

    def on_tier_level_changed(self, tier_level):
        self.update_tier_values()

    def on_slot_fitting_changed(self, slot_id, component_instance):
        self.update_tier_values()

    def on_design_reset(self, *args):
        self.update_tier_values()

    def on_existing_design_loaded(self, *args):
        self.update_tier_values()

    def on_scene_zoom(self, is_zoomed):
        target_opacity = 0.0 if is_zoomed else 1.0
        animations.FadeTo(self, self.opacity, target_opacity, duration=0.15)

    def update_radial_position(self):
        tier_angle_offset = self.ANGLE_OFFSET_DEG + self.ANGLE_DEG * 0.5
        current_tier_angle = 90 + tier_angle_offset
        current_tier_x, current_tier_y = studioUtil.get_radial_position(self.radius, current_tier_angle)
        self.current_tier_container.left = current_tier_x
        self.current_tier_container.top = current_tier_y
        self.current_tier_container.rotation = math.radians(-tier_angle_offset)
        next_tier_angle = 90 - tier_angle_offset
        next_tier_x, next_tier_y = studioUtil.get_radial_position(self.radius, next_tier_angle)
        self.next_tier_container.left = next_tier_x
        self.next_tier_container.top = next_tier_y
        self.next_tier_container.rotation = math.radians(tier_angle_offset)
        self.gauge.SetRadius(self.radius)

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self.update_radial_position()
