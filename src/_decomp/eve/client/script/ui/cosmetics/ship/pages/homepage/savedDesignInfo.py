#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\homepage\savedDesignInfo.py
import blue
from carbonui import Align, AxisAlignment, ButtonStyle, Density, uiconst, ButtonVariant
from carbonui import TextAlign, TextBody, TextColor, TextHeadline
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships.link.ship_skin_design_link_creation import create_link
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.client.shipSkinDesignSvc import get_ship_skin_design_svc
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.const import ANIM_DURATION_LONG, SkinrPage
from eve.client.script.ui.cosmetics.ship.controls.shipName import ShipName
from eve.client.script.ui.cosmetics.ship.pages import current_page
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from eve.client.script.ui.cosmetics.ship.pages.studio.skinDesignDragData import SkinDesignDragData
from eve.client.script.ui.cosmetics.ship.pages.studio.studioUtil import SHARE_BUTTON_ANALYTIC_ID
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException

class SavedDesignInfo(Container):
    default_opacity = 0.0

    def __init__(self, *args, **kwargs):
        super(SavedDesignInfo, self).__init__(*args, **kwargs)
        self.saved_skin_design_id = None
        self.skin_design = None
        self.construct_layout()
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(SavedDesignInfo, self).Close()

    def connect_signals(self):
        studioSignals.on_saved_design_selected.connect(self.on_saved_design_selected)
        studioSignals.on_sequencing_job_selected.connect(self.on_sequencing_job_selected)
        studioSignals.on_page_opened.connect(self.on_page_opened)

    def disconnect_signals(self):
        studioSignals.on_saved_design_selected.disconnect(self.on_saved_design_selected)
        studioSignals.on_sequencing_job_selected.disconnect(self.on_sequencing_job_selected)
        studioSignals.on_page_opened.disconnect(self.on_page_opened)

    def construct_layout(self):
        self.construct_buttons()
        self.construct_tier_indicator()
        self.construct_name_and_line()
        self.construct_ship_name()

    def construct_ship_name(self):
        self.ship_name = ShipName(name='ship_name', parent=self, align=Align.CENTERTOP)

    def construct_name_and_line(self):
        self.skin_line_label = TextBody(name='skin_line_label', parent=self, align=Align.TOBOTTOM, textAlign=TextAlign.CENTER)
        self.skin_name_label = TextHeadline(name='skin_name_label', parent=self, align=Align.TOBOTTOM, textAlign=TextAlign.CENTER, color=TextColor.HIGHLIGHT)

    def construct_tier_indicator(self):
        self.tier_container = Container(name='tier_container', parent=self, align=Align.TOBOTTOM, width=336, height=58, padding=(0, 8, 0, 32))
        self.tier_label = TextHeadline(name='tier_label', parent=self.tier_container, align=Align.TOTOP_NOPUSH, textAlign=TextAlign.CENTER, color=eveColor.BLACK, shadowOffset=(0, 0), bold=True, padTop=14)
        self.tier_background = Sprite(name='tier_background', parent=self.tier_container, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, width=336, height=58)

    def get_skin_tier_level(self):
        if self.skin_design:
            return self.skin_design.tier_level
        return 1

    def get_skin_tier_texture(self):
        tier_level = self.get_skin_tier_level()
        return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/tier/tier_{level}.png'.format(level=tier_level)

    def construct_buttons(self):
        self.button_group = ButtonGroup(name='button_group', parent=self, align=Align.TOBOTTOM, button_alignment=AxisAlignment.END, density=Density.EXPANDED, button_size_mode=ButtonSizeMode.DYNAMIC, padTop=32)
        self.share_btn = Button(texturePath='res:/UI/Texture/classes/HyperNet/hyperlink_icon.png', hint=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ShareDesign'), func=self.on_share_button_click, iconSize=28)
        self.share_btn.underlay.opacity = 0.0
        self.share_btn.MakeDragObject()
        self.share_btn.GetDragData = lambda : SkinDesignDragData(self.skin_design, self.saved_skin_design_id)
        self.share_btn.analyticID = SHARE_BUTTON_ANALYTIC_ID
        self.button_group.add_button(self.share_btn)
        self.button_group.add_button(Button(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/CreateNewDesign'), func=self.on_create_design_button, variant=ButtonVariant.PRIMARY))
        self.button_group.add_button(Button(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/EditDesign'), func=self.on_edit_design_button))
        self.button_group.add_button(Button(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/DeleteDesign'), style=ButtonStyle.DANGER, func=self.on_delete_design_button))

    def on_share_button_click(self, *args):
        try:
            link = create_link(character_id=self.skin_design.creator_character_id, design_id=self.saved_skin_design_id, name=self.skin_design.name)
            blue.clipboard.SetClipboardData(link)
            ShowQuickMessage(GetByLabel('UI/Personalization/ShipSkins/SKINR/LinkCopiedToClipboard'))
        except OSError as e:
            ShowQuickMessage(GetByLabel('UI/Personalization/ShipSkins/SKINR/LinkClipboardError'))

    def on_create_design_button(self, *args):
        if current_skin_design.get().has_fitted_components():
            ship_type_id = current_skin_design.get().ship_type_id
            current_skin_design.create_blank_design(ship_type_id)
        current_page.set_page_id(SkinrPage.STUDIO_DESIGNER)

    def on_edit_design_button(self, *args):
        current_page.set_page_id(SkinrPage.STUDIO_DESIGNER, page_args=self.saved_skin_design_id)

    def on_delete_design_button(self, *args):
        if uicore.Message('DeleteDesign', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        try:
            get_ship_skin_design_svc().delete_design(self.saved_skin_design_id)
            current_skin_design.create_blank_design()
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))

    def update(self):
        self.update_ship_name()
        self.update_name_labels()
        self.update_tier()

    def update_ship_name(self):
        self.ship_name.ship_type_id = self.skin_design.ship_type_id if self.skin_design else None

    def update_name_labels(self):
        self.skin_name_label.text = self.skin_design.name
        if self.skin_design.line_name:
            self.skin_line_label.display = True
            self.skin_line_label.text = self.skin_design.line_name
        else:
            self.skin_line_label.display = False

    def update_tier(self):
        self.tier_background.texturePath = self.get_skin_tier_texture()
        self.tier_label.text = '{tier}'.format(tier=self.get_skin_tier_level())

    def on_saved_design_selected(self, saved_skin_design_id, skin_design):
        self.saved_skin_design_id = saved_skin_design_id
        self.skin_design = skin_design
        if saved_skin_design_id is None or skin_design is None:
            self.fade_out()
        else:
            self.fade_out(callback=self.on_fade_out_complete)

    def on_sequencing_job_selected(self, *args):
        self.fade_out()

    def on_page_opened(self, page_id, page_args, last_page_id, animate = True):
        self.fade_out()

    def fade_out(self, callback = None):
        if callback is None:
            self.saved_skin_design_id = None
            self.skin_design = None
        self.state = uiconst.UI_DISABLED
        animations.FadeTo(self, self.opacity, 0.0, ANIM_DURATION_LONG, callback=callback)

    def fade_in(self):
        self.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self, self.opacity, 1.0, 0.5)

    def on_fade_out_complete(self):
        self.update()
        self.fade_in()
