#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\sections\corp.py
import eveicon
from carbonui import uiconst, Align, ButtonVariant, TextBody, TextHeadline
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.button import Button
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from cosmetics.client.ships.skins.live_data.skin_listing_target import ListingTargetType, SellerMembershipType
from cosmetics.client.ships.skins.static_data.store_section import StoreSection
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.controls.shipFilterMenuButton import ShipFilterMenuButton
from eve.client.script.ui.cosmetics.ship.pages.store import storeSettings, storeSignals
from eve.client.script.ui.cosmetics.ship.pages.store.sections.baseSkinsSection import BaseSkinsSection
from eve.client.script.ui.cosmetics.ship.pages.store.sections.baseSkinsSectionContainer import BaseSkinsSectionContainer, SortByMenuButtonIcon, MAX_NUM_PER_PAGE
from eve.client.script.ui.cosmetics.ship.pages.store.storeSettings import listed_by_setting
from eve.common.script.sys.idCheckers import IsNPCCorporation
from localization import GetByLabel

class CorpListingsSection(BaseSkinsSection):
    page_id = SkinrPage.STORE_SKINS
    category = StoreSection.SKINS_CORP
    name = 'UI/Personalization/ShipSkins/SKINR/Store/CorpSkins'

    def reset_pagination_controller(self, order_by, ascending):
        self.pagination_controller.reset(self.get_type_filter(), order_by, ascending, self.num_per_page, ListingTargetType.CORPORATION, SellerMembershipType.UNSPECIFIED)


class CorpListingsSectionContainer(BaseSkinsSectionContainer):

    def _set_section_controller(self, section_controller = None):
        self.section_controller = CorpListingsSection(num_per_page=None, apply_filtering=False)

    def construct_header(self):
        self.construct_header_layout_grid()
        self.header_layout_grid.columns = 3
        OwnerIcon(name='corp_icon', parent=self.header_layout_grid, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, ownerID=session.corpid, pos=(0, 0, 48, 48))
        self.construct_header_name_label()
        self.construct_header_num_items_label()

    def construct_cards(self, card_controllers):
        if card_controllers and len(card_controllers) > 0:
            super(CorpListingsSectionContainer, self).construct_cards(card_controllers)

    def construct_empty_state(self):
        if IsNPCCorporation(session.corpid):
            self.construct_join_player_corp_banner()
        else:
            super(CorpListingsSectionContainer, self).construct_empty_state()

    def construct_join_player_corp_banner(self):
        self.no_content_caption.display = False
        join_player_corp_banner = JoinPlayerCorpBanner(name='join_player_corp_banner', parent=self.content_overlay, align=Align.TOTOP)


class CorpSectionFilterMenuButtonIcon(MenuButtonIcon):
    hint = GetByLabel('UI/Common/Filter')
    default_texturePath = eveicon.filter

    def GetMenu(self):
        m = MenuData()
        m.AddCaption(GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ListedBy'))
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ListedByBrandManager'), SellerMembershipType.BRAND_MANAGER, listed_by_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ListedByCorpMember'), SellerMembershipType.MEMBER, listed_by_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ListedByAnyone'), SellerMembershipType.UNSPECIFIED, listed_by_setting)
        return m


class ViewAllCorpListingsSection(CorpListingsSection):

    def get_type_filter(self):
        if self.apply_filtering:
            ship_type = storeSettings.skins_hull_type_filter_setting.get()
            if ship_type:
                return [ship_type]
            return []
        else:
            return []

    def reset_pagination_controller(self, order_by, ascending):
        self.pagination_controller.reset(self.get_type_filter(), order_by, ascending, self.num_per_page, listing_target_type=ListingTargetType.CORPORATION, seller_membership_type=listed_by_setting.get())


class ViewAllCorpSkinsSectionContainer(BaseSkinsSectionContainer):

    def __init__(self, **kw):
        storeSettings.skins_hull_type_filter_setting.set(None)
        storeSettings.listed_by_setting.set(SellerMembershipType.UNSPECIFIED)
        super(ViewAllCorpSkinsSectionContainer, self).__init__(**kw)

    def _set_section_controller(self, section_controller = None):
        self.section_controller = ViewAllCorpListingsSection(MAX_NUM_PER_PAGE)

    def connect_signals(self):
        super(ViewAllCorpSkinsSectionContainer, self).connect_signals()
        storeSettings.skins_hull_type_filter_setting.on_change.connect(self.skins_hull_type_filter_setting)
        storeSettings.listed_by_setting.on_change.connect(self.on_listed_by_setting)

    def disconnect_signals(self):
        super(ViewAllCorpSkinsSectionContainer, self).disconnect_signals()
        storeSettings.skins_hull_type_filter_setting.on_change.disconnect(self.skins_hull_type_filter_setting)
        storeSettings.listed_by_setting.on_change.disconnect(self.on_listed_by_setting)

    def on_listed_by_setting(self, *args):
        self.reconstruct_cards()

    def construct_header(self):
        self.construct_header_layout_grid()
        self.header_layout_grid.columns = 3
        OwnerIcon(name='corp_icon', parent=self.header_layout_grid, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, ownerID=session.corpid, pos=(0, 0, 48, 48))
        self.construct_header_name_label()
        self.construct_header_num_items_label()

    def skins_hull_type_filter_setting(self, type_id):
        self.reconstruct_cards()

    def construct_filter_and_sorting(self):
        CorpSectionFilterMenuButtonIcon(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT, left=48)
        ShipFilterMenuButton(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT, left=20, hull_type_setting=storeSettings.skins_hull_type_filter_setting)
        SortByMenuButtonIcon(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT, show_name_option=False)

    def construct_pagination_container(self):
        self.pagination_container = Container(name='pagination_container', parent=self, align=Align.TOTOP, height=32)

    def construct_empty_state(self):
        if IsNPCCorporation(session.corpid):
            self.construct_join_player_corp_banner()
        else:
            super(ViewAllCorpSkinsSectionContainer, self).construct_empty_state()

    def construct_join_player_corp_banner(self):
        self.no_content_caption.display = False
        join_player_corp_banner = JoinPlayerCorpBanner(name='join_player_corp_banner', parent=self.content_overlay, align=Align.TOTOP)


class JoinPlayerCorpBanner(Container):
    default_clipChildren = True
    default_height = 198

    def __init__(self, *args, **kwargs):
        super(JoinPlayerCorpBanner, self).__init__(*args, **kwargs)
        self.construct_layout()
        self.update()

    def OnGlobalFontSizeChanged(self):
        self.update()

    def UpdateUIScaling(self, *args):
        self.update()

    def construct_layout(self):
        self.text_container = Container(name='text_container', parent=self, align=Align.VERTICALLY_CENTERED, padLeft=16)
        self.body_label = TextBody(parent=self.text_container, align=Align.TOTOP)
        self.header_label = TextHeadline(parent=self.text_container, align=Align.TOTOP)
        join_button = Button(parent=self, align=Align.BOTTOMRIGHT, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/JoinCorpBannerButton'), variant=ButtonVariant.PRIMARY, func=self.on_join_corp_button, left=24, top=24)
        Sprite(parent=self, align=Align.CENTER, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/Pages/ParagonHub/join_player_corp_banner.png', pos=(0, 0, 872, 198))

    def on_join_corp_button(self, *args):
        storeSignals.on_join_player_corp_banner()

    def update(self):
        body_text = GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/JoinCorpBannerBody')
        body_width, body_height = TextBody.MeasureTextSize(body_text)
        header_text = GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/JoinCorpBannerHeader')
        header_width, header_height = TextHeadline.MeasureTextSize(header_text)
        self.text_container.height = body_height + header_height
        self.body_label.text = body_text
        self.header_label.text = header_text
