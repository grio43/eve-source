#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\skinrInSceneContainer.py
import geo2
import math
from carbonui import Align, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.ui3d import InSceneContainer
from carbonui.uianimations import animations
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from eve.client.script.ui import eveColor
from eve.client.script.ui.cosmetics.ship import shipUtil
from eve.client.script.ui.cosmetics.ship.pages.collection import collectionSignals

class SkinrInSceneContainer(InSceneContainer):
    default_isFullscreen = False
    default_width = 1638
    default_height = 1638

    def __init__(self, *args, **kwargs):
        super(SkinrInSceneContainer, self).__init__(*args, **kwargs)
        self.scale_offset = 0.0
        self._is_expanded = False
        self.content = Container(name='content', parent=self)
        self.bg_sprite = Sprite(parent=self.content, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/scene_bg.png', align=Align.CENTER, pos=(0, 0, 1340, 1316), color=eveColor.TUNGSTEN_GREY, opacity=0.15)
        animations.FadeTo(self.content, 0.0, 1.0, duration=2.4)
        self.connect_signals()

    def connect_signals(self):
        self._camera.on_update.connect(self.on_camera_update)
        self._camera.on_orbit.connect(self.on_orbit)
        collectionSignals.on_activated_skin_license_selected.connect(self.on_activated_skin_license_selected)
        ship_skin_signals.on_skin_state_set.connect(self.on_skin_state_set)

    def update(self):
        self.update_bg_color()

    def on_skin_state_set(self, ship_id, skin_state):
        self.update_bg_color()

    def update_bg_color(self):
        ship_skin_state = shipUtil.get_active_ship_skin_state()
        if ship_skin_state is None or ship_skin_state.skin_type != ShipSkinType.THIRD_PARTY_SKIN:
            is_applied = False
        else:
            is_applied = ship_skin_state.skin_data.skin_id == current_skin_design.get().design_hex
        self._update_bg_color(is_applied)

    def _update_bg_color(self, is_applied):
        color = self.get_bg_color(is_applied)
        animations.SpColorMorphTo(self.bg_sprite, self.bg_sprite.rgba, color, duration=0.3)

    def on_activated_skin_license_selected(self, skin_license):
        is_applied = shipUtil.is_currently_applied_skin(skin_license.skin_hex)
        self._update_bg_color(is_applied)

    def get_bg_color(self, is_applied):
        if is_applied:
            return list(eveColor.CRYO_BLUE[:3]) + [0.3]
        else:
            return list(eveColor.TUNGSTEN_GREY[:3]) + [0.15]

    def on_orbit(self):
        if self._is_expanded:
            return
        self._is_expanded = True
        animations.FadeTo(self.content, self.content.opacity, 0.75, duration=0.6)

    def on_mouse_up(self, button):
        if button not in (uiconst.MOUSELEFT, uiconst.MOUSERIGHT):
            return
        self._is_expanded = False
        animations.FadeTo(self.content, self.content.opacity, 1.0, duration=0.6)
        animations.MorphScalar(self, 'scale_offset', self.scale_offset, 0.0, duration=0.6)

    def on_camera_update(self):
        translation = geo2.Vec3Add(self._camera.eyePosition, geo2.Vec3Scale(self._camera.GetLookAtDirection(), -1000))
        self.transform.translation = translation
        self.transform.rotation = geo2.QuaternionRotationSetYawPitchRoll(self._camera.yaw, math.pi / 2 - self._camera.pitch, 0.25 * self.scale_offset + self._camera.centerOffset)
        self.scaling = (1.0 - 0.1 * self._camera.zoom + self.scale_offset) * self.width

    def disable_render_steps(self):
        pass

    @property
    def scaling(self):
        return self.transform.scaling[0]

    @scaling.setter
    def scaling(self, value):
        self.transform.scaling = (value, value, 1.0)
