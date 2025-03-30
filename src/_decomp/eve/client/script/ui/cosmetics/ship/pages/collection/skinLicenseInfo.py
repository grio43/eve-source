#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\collection\skinLicenseInfo.py
import carbonui
import uthread2
from carbonui import Align, AxisAlignment, Density, uiconst, PickState
from carbonui import TextAlign, TextBody, TextColor, TextHeadline
from carbonui.button.group import ButtonGroup, ButtonSizeMode, OverflowAlign
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from cosmetics.client.shipSkinApplicationSvc import get_ship_skin_application_svc
from cosmetics.client.shipSkinLicensesSvc import get_ship_skin_license_svc
from cosmetics.client.shipSkinTradingSvc import get_ship_skin_trading_svc
from cosmetics.common.ships.skins import trading_util
from cosmetics.common.ships.skins.static_data import trading_const
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship import shipUtil
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.controls.characterInfo import MadeByCharacterInfo
from eve.client.script.ui.cosmetics.ship.controls.shipName import ShipName
from eve.client.script.ui.cosmetics.ship.pages.collection.baseLicenseInfo import LicenseInfo
from eve.client.script.ui.cosmetics.ship.pages.collection.sellSkinDialogue import SellSkinDialogue
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from eve.client.script.ui.shared.shipTree.infoBubble import SkillEntry
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from skills.client.util import get_skill_service
from stackless_response_router.exceptions import TimeoutException

class SkinLicenseInfo(LicenseInfo):
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self, *args, **kwargs):
        sm.RegisterNotify(self)
        self.license_id = None
        self.skin_license = None
        self.is_activated_license = False
        self.update_thread = None
        super(SkinLicenseInfo, self).__init__(*args, **kwargs)

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(SkinLicenseInfo, self).Close()

    def connect_signals(self):
        super(SkinLicenseInfo, self).connect_signals()
        studioSignals.on_page_opened.connect(self.on_page_opened)

    def disconnect_signals(self):
        super(SkinLicenseInfo, self).disconnect_signals()
        studioSignals.on_page_opened.disconnect(self.on_page_opened)

    def OnSessionChanged(self, isRemote, sess, change):
        if 'shipid' in change:
            self.update()

    def construct_layout(self):
        self.construct_bottom_container()
        self.construct_tier_indicator()
        self.construct_name_and_line()
        self.construct_ship_name()

    def construct_name_and_line(self):
        self.skin_line_label = TextBody(name='skin_line_label', parent=self, align=Align.TOBOTTOM, textAlign=TextAlign.CENTER)
        self.skin_name_label = TextHeadline(name='skin_name_label', parent=self, align=Align.TOBOTTOM, textAlign=TextAlign.CENTER, color=TextColor.HIGHLIGHT)

    def construct_tier_indicator(self):
        self.tier_container = Container(name='tier_container', parent=self, align=Align.TOBOTTOM, width=336, height=58, padTop=8)
        self.tier_label = TextHeadline(name='tier_label', parent=self.tier_container, align=Align.TOTOP_NOPUSH, textAlign=TextAlign.CENTER, color=eveColor.BLACK, shadowOffset=(0, 0), bold=True, padTop=14)
        self.tier_background = Sprite(name='tier_background', parent=self.tier_container, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, width=336, height=58)

    def get_skin_tier_level(self):
        if self.skin_license:
            return self.skin_license.skin_design.tier_level
        return 1

    def get_skin_tier_texture(self):
        tier_level = self.get_skin_tier_level()
        return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/tier/tier_{level}.png'.format(level=tier_level)

    def construct_bottom_container(self):
        self.bottom_cont = Container(name='bottom_cont', height=64, parent=self, padTop=32, align=Align.TOBOTTOM)
        self.character_info = MadeByCharacterInfo(name='character_info', parent=self.bottom_cont, align=Align.TOLEFT)
        self.construct_button_container()

    def construct_button_container(self):
        self.button_container = Container(name='button_container', parent=self.bottom_cont, padLeft=8)
        self.button_group = ButtonGroup(name='button_group', parent=self.button_container, align=Align.TOBOTTOM, button_alignment=AxisAlignment.END, density=Density.EXPANDED, button_size_mode=ButtonSizeMode.DYNAMIC, overflow_align=OverflowAlign.LEFT)
        self.reconstruct_buttons()

    def construct_ship_name(self):
        self.ship_name = ShipName(name='ship_name', parent=self, align=Align.CENTERTOP)

    def reconstruct_buttons(self):
        self.button_group.FlushButtons()
        if not self.skin_license:
            return
        self.add_apply_button()
        self.add_unapply_button()
        self.add_activate_apply_button()
        self.add_activate_button()
        self.add_sell_button()

    def add_apply_button(self):
        if not self.skin_license.activated or not self.is_activated_license:
            return
        if shipUtil.is_currently_applied_skin(self.skin_license.skin_hex):
            return
        if self.is_license_for_active_ship():
            enabled = True
            hint = None
        else:
            enabled = False
            hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/SkinApplyDisabledHint')
        self.apply_button = Button(name='apply_button', label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/Apply'), func=self.on_apply_button, enabled=enabled, hint=hint)
        self.button_group.add_button(self.apply_button)

    def add_unapply_button(self):
        if not self.skin_license.activated or not self.is_activated_license:
            return
        applied_skin = shipUtil.get_active_ship_skin_state()
        if applied_skin.skin_type == ShipSkinType.THIRD_PARTY_SKIN and applied_skin.skin_data.skin_id == self.skin_license.skin_hex:
            self.unapply_button = Button(name='unapply_button', label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/UnApply'), func=self.on_unapply_button)
            self.button_group.add_button(self.unapply_button)

    def add_activate_apply_button(self):
        if self.skin_license.activated or self.is_activated_license:
            return
        if not self.is_license_for_active_ship():
            return
        self.apply_activate_button = Button(name='apply_activate_button', label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/ActivateAndApply'), func=self.on_apply_activate_button)
        self.button_group.add_button(self.apply_activate_button)

    def add_activate_button(self):
        if self.skin_license.activated or self.is_activated_license:
            return
        self.activate_button = Button(name='activate_button', label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/Activate'), func=self.on_activate_button)
        self.button_group.add_button(self.activate_button)

    def add_sell_button(self):
        if self.is_activated_license:
            return
        if not self.skin_license.activated or self.skin_license.nb_unactivated > 0:
            self.sell_button = SellButton(name='sell_button', label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/Sell'), func=self.on_sell_button)
            self.button_group.add_button(self.sell_button)

    def on_apply_activate_button(self, *args):
        if uicore.Message('ActivateAndApply', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        try:
            get_ship_skin_application_svc().apply_third_party_skin(shipUtil.get_active_ship_item_id(), self.license_id, apply_license=True, activate_license=True)
        except Exception as e:
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))

    def on_activate_button(self, *args):
        if uicore.Message('ActivateSkin', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        try:
            get_ship_skin_license_svc().activate_license(self.license_id)
        except Exception as e:
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))

    def on_sell_button(self, *args):
        dialogue = SellSkinDialogue(self.skin_license)
        dialogue.ShowModal()
        self.sell_button.update_enabled_state()

    def on_apply_button(self, *args):
        try:
            self.apply_button.busy = True
            get_ship_skin_application_svc().apply_third_party_skin(shipUtil.get_active_ship_item_id(), self.license_id, apply_license=True, activate_license=False)
        except Exception as e:
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            self.apply_button.busy = False

    def on_unapply_button(self, *args):
        try:
            self.unapply_button.busy = True
            get_ship_skin_application_svc().apply_third_party_skin(shipUtil.get_active_ship_item_id(), self.license_id, apply_license=False, activate_license=False)
        except Exception as e:
            self.unapply_button.busy = False
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))

    def on_page_opened(self, page_id, page_args, last_page_id, animate = True):
        any_collection_page = [SkinrPage.COLLECTION, SkinrPage.COLLECTION_COMPONENTS, SkinrPage.COLLECTION_SKINS]
        if page_id in any_collection_page and last_page_id in any_collection_page:
            self.fade_out()

    def update(self):
        if self.update_thread:
            self.update_thread.kill()
        self.update_thread = uthread2.start_tasklet(self._update)

    def _update(self):
        self.skin_name_label.text = self.get_skin_name()
        self.update_skin_line_label()
        self.update_ship_name()
        uthread2.start_tasklet(self.update_character_info)
        self.reconstruct_buttons()
        self.update_tier()
        self.update_thread = None

    def get_skin_name(self):
        if self.skin_license:
            return self.skin_license.skin_design.name
        return ''

    def update_skin_line_label(self):
        if not self.skin_license:
            self.skin_line_label.display = False
            return
        if self.skin_license.skin_design.line_name:
            self.skin_line_label.display = True
            self.skin_line_label.text = self.skin_license.skin_design.line_name
        else:
            self.skin_line_label.display = False
            self.skin_line_label.text = ''

    def update_tier(self):
        self.tier_label.text = '{tier}'.format(tier=self.get_skin_tier_level())
        self.tier_background.texturePath = self.get_skin_tier_texture()

    def update_character_info(self):
        if self.skin_license:
            self.character_info.character_id = self.skin_license.skin_design.creator_character_id

    def update_ship_name(self):
        self.ship_name.ship_type_id = self.skin_license.skin_design.ship_type_id if self.skin_license else None

    def is_license_for_active_ship(self):
        return shipUtil.get_active_ship_type_id() == self.skin_license.skin_design.ship_type_id

    def on_unactivated_skin_license_selected(self, skin_license):
        self.license_id = skin_license.skin_hex
        self.is_activated_license = False
        self.skin_license = skin_license
        self.fade_out(callback=self.on_fade_out_complete)

    def on_activated_skin_license_selected(self, skin_license):
        self.license_id = skin_license.skin_hex
        self.is_activated_license = True
        self.skin_license = skin_license
        self.fade_out(callback=self.on_fade_out_complete)

    def on_component_license_selected(self, *args):
        self.fade_out()

    def on_skin_state_set(self, _ship_instance_id, skin_state):
        if skin_state.character_id == session.charid:
            uthread2.start_tasklet(self.update)

    def fade_out(self, callback = None):
        if callback is None:
            self.license_id = None
            self.skin_license = None
        self.state = uiconst.UI_DISABLED
        animations.FadeTo(self, self.opacity, 0.0, uiconst.TIME_EXIT, callback=callback)

    def on_fade_out_complete(self):
        self.update()
        self.fade_in()

    def fade_in(self):
        self.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self, self.opacity, 1.0, uiconst.TIME_ENTRY)


class SellButton(Button):
    default_enabled = False

    def __init__(self, get_menu_entry_data_func = None, **kwargs):
        super(SellButton, self).__init__(get_menu_entry_data_func, **kwargs)
        uthread2.start_tasklet(self.update_enabled_state)

    def update_enabled_state(self):
        self.max_listings = trading_util.get_maximum_concurrent_skin_listings(get_skill_service().GetMyLevel)
        try:
            self.num_listings = len(get_ship_skin_trading_svc().get_owned_listings())
        except (TimeoutException, GenericException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            self.num_listings = 0

        if self.num_listings >= self.max_listings:
            self.disable()
        else:
            self.enable()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 2
        tooltipPanel.pickState = PickState.ON
        if self.num_listings >= self.max_listings:
            tooltipPanel.AddCell(carbonui.TextBody(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/UnableToListMoreSKINs', num_listings=self.num_listings), width=300, color=eveColor.WARNING_ORANGE), colSpan=2)
        tooltipPanel.AddCell(carbonui.TextBody(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/MaxListingsTooltip'), width=300, color=TextColor.SECONDARY), colSpan=2)
        for type_id in trading_const.max_concurrent_listings_skills:
            level = get_skill_service().GetMyLevel(type_id)
            tooltipPanel.AddRow(rowClass=SkillEntry, typeID=type_id, level=level, showLevel=False)
