#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\skinBrowser.py
from eve.client.script.ui.cosmetics.ship.pages.store.sections.activeShip import ViewAllSkinsActiveShipSectionContainer, ActiveShipSectionContainer
import carbonui
from carbonui import Align
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from cosmetics.client.shipSkinTradingSvc import get_ship_skin_trading_svc
from cosmetics.client.ships.feature_flag import are_skin_hub_offers_enabled
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.client.ships.skins.static_data.store_section import StoreSection
from eve.client.script.ui.cosmetics.ship.pages.store import storeSettings
from eve.client.script.ui.cosmetics.ship.pages.store.sections.allListings import ViewAllSkinsSectionContainer, ViewLinkedListingAndAllSkinsSectionContainer, AllSkinsSectionContainer
from eve.client.script.ui.cosmetics.ship.pages.store.sections.alliance import AllianceListingsSectionContainer, ViewAllAllianceSkinsSectionContainer
from eve.client.script.ui.cosmetics.ship.pages.store.sections.corp import CorpListingsSectionContainer, ViewAllCorpSkinsSectionContainer
from eve.client.script.ui.cosmetics.ship.pages.store.sections.emphasizedShip import ViewAllSkinsEmphasizedShipSectionContainer, EmphasizedShipSectionContainer
from eve.client.script.ui.cosmetics.ship.pages.store.sections.myListings import ListedByMeSectionContainer, ViewAllSkinsListedByMeSectionContainer
from eve.client.script.ui.cosmetics.ship.pages.store.sections.targetedAtMe import StoreViewAllSkinListingsTargetedAtMeSectionContainer, StoreSkinListingsTargetedAtMeSectionContainer
from localization import GetByLabel

class OffersDisabledPanel(ContainerAutoSize):
    default_padTop = 128

    def __init__(self, **kw):
        super(OffersDisabledPanel, self).__init__(**kw)
        textCont = ContainerAutoSize(parent=self, align=Align.CENTERTOP, width=450)
        carbonui.TextHeader(parent=textCont, align=Align.TOTOP, padTop=32, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/SKINOffersDisabled'))


class SkinBrowser(ScrollContainer):
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self, **kw):
        super(SkinBrowser, self).__init__(**kw)
        self.is_loaded = False
        sm.RegisterNotify(self)

    def Close(self, *args):
        try:
            sm.UnregisterNotify(self)
        finally:
            super(SkinBrowser, self).Close()

    def LoadPanel(self, section_id = None, linked_listing = None):
        self.Flush()
        self.opacity = 0.0
        self.StopAnimations()
        if not are_skin_hub_offers_enabled():
            OffersDisabledPanel(parent=self, align=Align.TOTOP)
        elif section_id == StoreSection.SKINS_ALL:
            self.construct_view_all_skins_section()
        elif section_id == StoreSection.SKINS_ACTIVE_SHIP:
            self.construct_view_all_for_active_ship_section()
        elif section_id == StoreSection.SKINS_EMPHASIZED_SHIP:
            self.construct_view_all_for_emphasized_ship_section()
        elif section_id == StoreSection.SKINS_MY_LISTINGS:
            self.construct_view_all_my_listings_sections()
        elif section_id == StoreSection.SKINS_LINKED_LISTING_AND_ALL:
            self.construct_linked_listing_and_view_all_skins_sections(linked_listing)
        elif section_id == StoreSection.SKINS_CORP:
            self.construct_view_all_corp_section()
        elif section_id == StoreSection.SKINS_ALLIANCE:
            self.construct_view_all_alliance_section()
        elif section_id == StoreSection.SKINS_TARGETED_AT_ME:
            self.construct_targeted_at_me_section()
        else:
            self.construct_landing_page()
        self.appear()

    def construct_targeted_at_me_section(self):
        self.Flush()
        StoreViewAllSkinListingsTargetedAtMeSectionContainer(parent=self, align=Align.TOTOP, padTop=32)

    def construct_view_all_for_active_ship_section(self):
        self.Flush()
        ViewAllSkinsActiveShipSectionContainer(parent=self, align=Align.TOTOP, padTop=32)

    def construct_view_all_for_emphasized_ship_section(self):
        self.Flush()
        ViewAllSkinsEmphasizedShipSectionContainer(parent=self, align=Align.TOTOP, padTop=32)

    def construct_view_all_my_listings_sections(self):
        self.Flush()
        ViewAllSkinsListedByMeSectionContainer(parent=self, align=Align.TOTOP, padTop=32)

    def construct_view_all_skins_section(self):
        self.Flush()
        ViewAllSkinsSectionContainer(parent=self, align=Align.TOTOP, padTop=32)

    def construct_linked_listing_and_view_all_skins_sections(self, linked_listing = None):
        self.Flush()
        ViewLinkedListingAndAllSkinsSectionContainer(parent=self, align=Align.TOTOP, padTop=32, linked_listing=linked_listing)

    def construct_view_all_corp_section(self):
        self.Flush()
        ViewAllCorpSkinsSectionContainer(parent=self, align=Align.TOTOP, padTop=32)

    def construct_view_all_alliance_section(self):
        self.Flush()
        ViewAllAllianceSkinsSectionContainer(parent=self, align=Align.TOTOP, padTop=32)

    def construct_landing_page(self):
        self.Flush()
        emphasized_ship_id = storeSettings.emphasized_ship_type_id.get()
        if emphasized_ship_id and emphasized_ship_id != current_skin_design.get_default_ship_type_id():
            EmphasizedShipSectionContainer(parent=self, align=Align.TOTOP, single_row=True, padTop=32)
        ActiveShipSectionContainer(parent=self, align=Align.TOTOP, single_row=True, padTop=32)
        AllSkinsSectionContainer(parent=self, align=Align.TOTOP, single_row=True, padTop=32)
        CorpListingsSectionContainer(parent=self, align=Align.TOTOP, single_row=True, padTop=32)
        if session.allianceid:
            AllianceListingsSectionContainer(parent=self, align=Align.TOTOP, single_row=True, padTop=32)
        StoreSkinListingsTargetedAtMeSectionContainer(parent=self, align=Align.TOTOP, single_row=True, padTop=32)
        if get_ship_skin_trading_svc().get_owned_listings():
            ListedByMeSectionContainer(parent=self, align=Align.TOTOP, single_row=True, padTop=32)

    def appear(self):
        animations.FadeTo(self, 0.0, 1.0, duration=0.3)

    def OnSessionChanged(self, isRemote, session, change):
        if 'corprole' in change or 'corpid' in change or 'allianceid' in change:
            self.LoadPanel()
