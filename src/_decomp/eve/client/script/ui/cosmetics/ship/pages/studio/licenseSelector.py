#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\licenseSelector.py
import eveicon
import uthread2
from carbonui import Align, TextBody, TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from cosmetics.client.ships.skins.live_data import current_skin_design_signals
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.pages.sequence import sequence_ui_signals
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException

class LicenseSelector(ContainerAutoSize):
    default_height = 20

    def __init__(self, component_instance, *args, **kwargs):
        super(LicenseSelector, self).__init__(*args, **kwargs)
        self._component_instance = component_instance
        self.bound_license = None
        self.unbound_license = None
        self._update_thread = None
        self._update_component_license_granted_thread = None
        self.construct_layout()
        self.update_async()
        self.connect_signals()

    def Close(self):
        try:
            self.kill_threads()
            self.disconnect_signals()
        finally:
            super(LicenseSelector, self).Close()

    def kill_threads(self):
        self.kill_update_thread()
        self.kill_update_component_license_granted_thread()

    def kill_update_thread(self):
        if self._update_thread is not None:
            self._update_thread.kill()
            self._update_thread = None

    def kill_update_component_license_granted_thread(self):
        if self._update_component_license_granted_thread is not None:
            self._update_component_license_granted_thread.kill()
            self._update_component_license_granted_thread = None

    def connect_signals(self):
        current_skin_design_signals.on_component_instance_license_to_use_changed.connect(self.on_component_instance_license_to_use_changed)
        ship_skin_signals.on_component_license_granted.connect(self.on_component_license_granted)

    def disconnect_signals(self):
        current_skin_design_signals.on_component_instance_license_to_use_changed.disconnect(self.on_component_instance_license_to_use_changed)
        ship_skin_signals.on_component_license_granted.disconnect(self.on_component_license_granted)

    def on_component_instance_license_to_use_changed(self, component_id, license):
        if self.component_instance and self.component_instance.component_id == component_id:
            self.update_async()

    def on_component_license_granted(self, component_id, license_type, quantity):
        self.update_component_license_granted_async(component_id, license_type)

    def update_component_license_granted_async(self, component_id, license_type):
        self.kill_update_component_license_granted_thread()
        self._update_component_license_granted_thread = uthread2.start_tasklet(self.update_component_license_granted, component_id, license_type)

    def update_component_license_granted(self, component_id, license_type):
        if self.component_instance and self.component_instance.component_id == component_id:
            self.load_license_status()
            if not self.has_available_license:
                return
            if license_type == ComponentLicenseType.UNLIMITED and self.unbound_license:
                self.component_instance.component_license_to_use = self.unbound_license
            elif license_type == ComponentLicenseType.LIMITED and self.bound_license:
                self.component_instance.component_license_to_use = self.bound_license

    def construct_layout(self):
        self.construct_unbound_indicator()
        self.construct_slash()
        self.construct_bound_indicator()

    def construct_unbound_indicator(self):
        self.unbound_indicator = UnboundLicenseIndicator(name='unbound_indicator', parent=self, align=Align.TOLEFT)
        self.unbound_indicator.OnClick = self.on_unbound_click

    def construct_slash(self):
        self.slash = SlashDivider(name='slash', parent=self, align=Align.TOLEFT, padTop=1)

    def construct_bound_indicator(self):
        self.bound_indicator = BoundLicenseIndicator(name='bound_indicator', parent=self, align=Align.TOLEFT)
        self.bound_indicator.OnClick = self.on_bound_click

    def update_async(self):
        self.kill_update_thread()
        self._update_thread = uthread2.start_tasklet(self.update)

    def update(self):
        self.load_license_status()
        self.display = self.has_available_license
        self.update_unbound_indicator()
        self.update_bound_indicator()
        self.update_selection()
        self.update_slash()
        if self.component_instance and self.component_instance.component_license_to_use:
            self.show()
        else:
            self.hide()

    def load_license_status(self):
        self.bound_license = self.unbound_license = None
        if not self.component_instance:
            return
        try:
            self.bound_license = get_ship_skin_component_svc().get_bound_license(component_id=self.component_instance.component_id, component_type=self.component_instance.get_component_data().category)
            self.unbound_license = get_ship_skin_component_svc().get_unbound_license(component_id=self.component_instance.component_id, component_type=self.component_instance.get_component_data().category)
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))

    def update_unbound_indicator(self):
        self.unbound_indicator.component_license = self.unbound_license
        self.unbound_indicator.component_instance = self.component_instance

    def update_bound_indicator(self):
        self.bound_indicator.component_license = self.bound_license
        self.bound_indicator.component_instance = self.component_instance

    def update_selection(self):
        self.bound_indicator.is_selected = False
        self.unbound_indicator.is_selected = False
        if not self.component_instance:
            return
        license = self.component_instance.get_component_license()
        if not license:
            return
        if license.license_type == ComponentLicenseType.UNLIMITED:
            self.unbound_indicator.is_selected = True
        elif license.license_type == ComponentLicenseType.LIMITED:
            self.bound_indicator.is_selected = self.has_bound_uses_remaining

    def update_slash(self):
        self.slash.display = self.unbound_license is not None and self.bound_license is not None
        if self.bound_indicator.is_selected:
            self.slash.close()
        else:
            self.slash.open()

    def show(self, animate = True):
        self.state = uiconst.UI_PICKCHILDREN
        if animate:
            animations.FadeTo(self, self.opacity, 1.0, duration=0.2)
        else:
            self.opacity = 1.0

    def hide(self, animate = True):
        self.state = uiconst.UI_DISABLED
        if animate:
            animations.FadeTo(self, self.opacity, 0.0, duration=0.2)
        else:
            self.opacity = 0.0

    def on_unbound_click(self, *args):
        self.unbound_indicator.is_selected = True
        self.bound_indicator.is_selected = False
        self.component_instance.component_license_to_use = self.unbound_license
        sequence_ui_signals.on_component_license_selection_changed()

    def on_bound_click(self, *args):
        self.bound_indicator.is_selected = True
        self.unbound_indicator.is_selected = False
        self.component_instance.component_license_to_use = self.bound_license
        sequence_ui_signals.on_component_license_selection_changed()

    @property
    def has_available_license(self):
        return self.bound_license is not None or self.unbound_license is not None

    @property
    def has_bound_uses_remaining(self):
        if self.bound_license:
            return self.bound_license.remaining_license_uses and self.bound_license.remaining_license_uses > 0
        return False

    @property
    def component_instance(self):
        return self._component_instance

    @component_instance.setter
    def component_instance(self, value):
        if self._component_instance == value:
            return
        self._component_instance = value
        self.update_async()


class BaseLicenseIndicator(Container):
    default_width = 28
    default_height = 20
    default_state = uiconst.UI_NORMAL

    def __init__(self, component_license = None, component_instance = None, *args, **kwargs):
        super(BaseLicenseIndicator, self).__init__(*args, **kwargs)
        self._component_license = component_license
        self._component_instance = component_instance
        self._is_selected = False
        self.construct_layout()
        self.update()

    def construct_layout(self):
        self.construct_background()

    def construct_background(self):
        self.background_sprite = StretchSpriteHorizontal(name='background_sprite', parent=self, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Cosmetics/Ship/license_indicator_bg.png', color=eveColor.SMOKE_BLUE, opacity=0.3, leftEdgeSize=8, rightEdgeSize=8)

    def update(self):
        self.update_display()
        if not self.display:
            return
        self.update_width()
        self.update_background()

    def update_display(self):
        self.display = self.component_license is not None

    def update_width(self):
        self.width = self.default_width

    def update_background(self):
        self.background_sprite.pos = (0,
         0,
         self.width,
         self.default_height)
        target_opacity = 1.0 if self.is_selected else 0.3
        animations.FadeTo(self.background_sprite, self.background_sprite.opacity, target_opacity, duration=0.2)

    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value):
        if self._is_selected == value:
            return
        self._is_selected = value
        self.update()

    @property
    def component_license(self):
        return self._component_license

    @component_license.setter
    def component_license(self, value):
        if self._component_license == value:
            return
        self._component_license = value
        self.update()

    @property
    def component_instance(self):
        return self._component_instance

    @component_instance.setter
    def component_instance(self, value):
        if self._component_instance == value:
            return
        self._component_instance = value
        self.update()


class BoundLicenseIndicator(BaseLicenseIndicator):

    def construct_layout(self):
        self.label = TextBody(name='label', parent=self, align=Align.CENTER, opacity=0.5)
        super(BoundLicenseIndicator, self).construct_layout()

    def update(self):
        super(BoundLicenseIndicator, self).update()
        self.update_label()

    def update_display(self):
        self.display = self.has_uses_remaining

    def update_width(self):
        text_width, _ = TextBody.MeasureTextSize(self.label_text)
        self.width = max(self.default_width, text_width + 16)

    def update_label(self):
        self.label.text = self.label_text
        target_opacity = 1.0 if self.is_selected else 0.5
        animations.FadeTo(self.label, self.label.opacity, target_opacity, duration=0.2)

    @property
    def has_uses_remaining(self):
        if self.component_license:
            return self.component_license.remaining_license_uses and self.component_license.remaining_license_uses > 0
        return False

    @property
    def label_text(self):
        if self.component_license:
            return self.component_license.remaining_license_uses
        return ''

    def GetHint(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/UseLimitedDesignElement') + '\n' + GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/NumLimitedDesignElementsAvailable', num_available=self.component_license.remaining_license_uses)


class UnboundLicenseIndicator(BaseLicenseIndicator):

    def construct_layout(self):
        self.icon = Sprite(name='icon', parent=self, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath=eveicon.infinity, color=TextColor.NORMAL, opacity=0.5, pos=(0, 0, 16, 16))
        super(UnboundLicenseIndicator, self).construct_layout()

    def update(self):
        super(UnboundLicenseIndicator, self).update()
        self.update_icon()

    def update_icon(self):
        target_opacity = 1.0 if self.is_selected else 0.5
        animations.FadeTo(self.icon, self.icon.opacity, target_opacity, duration=0.2)

    def GetHint(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/UnlimitedDesignElementRequirement', type_id=self.component_instance.sequence_binder_type_id, amount=self.component_instance.sequence_binder_amount_required_if_bound)


class SlashDivider(Container):
    default_width = 13
    default_height = 18

    def __init__(self, *args, **kwargs):
        super(SlashDivider, self).__init__(*args, **kwargs)
        self.construct_layout()

    def construct_layout(self):
        self.open_sprite = Sprite(name='open_sprite', parent=self, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Cosmetics/Ship/slash_open.png', color=eveColor.FOCUS_BLUE, pos=(0, 0, 33, 38), display=False)
        self.closed_sprite = Sprite(name='closed_sprite', parent=self, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Cosmetics/Ship/slash_closed.png', color=eveColor.FOCUS_BLUE, pos=(0, 0, 27, 26))

    def open(self):
        self.open_sprite.display = True
        self.closed_sprite.display = False

    def close(self):
        self.open_sprite.display = False
        self.closed_sprite.display = True
