#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fastcheckout\client\fastCheckoutStoreView.py
from operator import attrgetter
import carbonui.const as uiconst
import localization
import uthread2
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.linkLabel import LinkLabel
from eveexceptions import UserError
from fastcheckout.client.eventlogging.eventLoggers import event_logger
from fastcheckout.client.offerEntry import OfferEntry
from fastcheckout.client.purchaseView import PlexPurchaseView
from fastcheckout.client.restrictionDialogue import RestrictionDialogue
from fastcheckout.common.errors import FastCheckoutDisabled
from fastcheckout.const import WINDOW_COLOR, OFFER_ENTRY_PADDING, FULL_WINDOW_WIDTH, BACKGROUND_IMAGE_PATH

class FastCheckoutStoreView(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(FastCheckoutStoreView, self).ApplyAttributes(attributes)
        self.is_ready = False
        self.close_func = attributes.get('closeFunc', None)
        self.plex_needed = attributes.get('plexNeeded', False)
        self.log_context = attributes.get('logContext', 'Not specified')
        self.offer_id = attributes.get('offerId', None)
        self.opened_from_nes = attributes.get('openedFromNES', False)
        self.purchaseView = None
        self.service = sm.GetService('fastCheckoutClientService')
        self.construct_layout()
        self.set_labels()
        uthread2.StartTasklet(self.construct_offer_view)
        event_logger.log_fast_checkout_window_opened(self.log_context)

    def construct_offer_view(self):
        try:
            self.offers = self.get_offers()
        except KeyError:
            self.restrict_ui_and_show_popup(header_text=localization.GetByLabel('UI/FastCheckout/MaximumTransactionsExceededHeader'), description_text='<center>%s</center>' % localization.GetByLabel('UI/FastCheckout/MaximumTransactionsExceededDescription'))
        except FastCheckoutDisabled:
            self.service.buy_plex_online(log_context='NewEdenStore_FastCheckout')
            self.close_view()
            return
        except (RuntimeError, UserError):
            self.restrict_ui_and_show_popup(header_text=localization.GetByLabel('UI/FastCheckout/ServiceUnavailableHeader'), description_text='<center>%s</center>' % localization.GetByLabel('UI/FastCheckout/ServiceUnavailableDescription'))
        else:
            self.reset_highlight()
            if self.plex_needed:
                self.add_highlight_to_offer()
            self.get_offer_base_value()
            self.populate_offer_list()
            if self.offer_id:
                self.select_offer_by_id(self.offer_id)
        finally:
            self.loading_wheel.Close()
            self.is_ready = True

    def construct_layout(self):
        self.background_container = Sprite(name='BackgroundImage', bgParent=self, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, useSizeFromTexture=True, texturePath=BACKGROUND_IMAGE_PATH)
        self.main_container = Container(name='MainContainer', parent=self, state=uiconst.UI_NORMAL)
        self.loading_wheel = LoadingWheel(parent=self.main_container, align=uiconst.CENTER, opacity=1, idx=0)
        self.top_container = Container(name='TopContainer', parent=self.main_container, align=uiconst.TOTOP, height=60)
        self.description_label = Label(name='DescriptionLabel', parent=self.top_container, align=uiconst.TOPLEFT, fontsize=12, bold=True, color=Color.WHITE, left=10, top=10)
        self.info_button = InfoIcon(name='PlexInfoButton', parent=self.top_container, align=uiconst.TOPLEFT, typeID=const.typePlex, iconOpacity=1.0, top=8, state=uiconst.UI_HIDDEN if self.opened_from_nes else uiconst.UI_NORMAL)
        self.bottom_container = Container(name='BottomContainer', parent=self.main_container, align=uiconst.TOBOTTOM, height=60)
        more_information_label_container = ContainerAutoSize(name='MoreInformationLabelContainer', parent=self.bottom_container, align=uiconst.BOTTOMLEFT, height=15, left=10, top=10)
        self.more_information_label = Label(name='MoreInformationLabel', parent=more_information_label_container, align=uiconst.TOLEFT, fontsize=12, bold=True, color=Color.WHITE)
        self.online_store_link_label = LinkLabel(name='MoreInformationLinkLabel', parent=more_information_label_container, align=uiconst.TOLEFT, left=5, function=lambda : self.service.buy_plex_online(log_context='NewEdenStore_FastCheckout'), bold=True)
        offers_container = Container(name='OffersContainer', parent=self.main_container, align=uiconst.TOALL)
        self.offers_scroll_container = ScrollContainer(name='OffersScrollContainer', parent=offers_container, align=uiconst.CENTER, padLeft=15, width=FULL_WINDOW_WIDTH, height=260)

    @staticmethod
    def get_animation_width():
        return FULL_WINDOW_WIDTH

    def populate_offer_list(self):
        for i in range(len(self.offers)):
            OfferEntry(name=self.offers[i]['name'], parent=self.offers_scroll_container, offer=self.offers[i], left=OFFER_ENTRY_PADDING if i > 0 else 0, basePrice=self.base_price, baseQuantity=self.base_quantity, func=self.select_offer)

    def get_offers(self):
        offers = self.service.get_plex_offers(self.log_context)
        if not offers:
            raise KeyError()
        return sorted(offers, key=lambda k: k['quantity'])

    def add_highlight_to_offer(self):
        try:
            next((offer for offer in self.offers if offer['quantity'] >= self.plex_needed))['highlight'] = True
        except StopIteration:
            max(self.offers, key=attrgetter('quantity'))['highlight'] = True

    def get_offer_base_value(self):
        self.base_price, self.base_quantity = self.service.get_plex_offers_base_price_and_quantity()

    def select_offer_by_id(self, offerId):
        selected_offer = None
        for offer in self.offers:
            if offer['id'] == offerId:
                selected_offer = offer

        if selected_offer is None:
            raise RuntimeError('OfferNotFound')
        self.select_offer(selected_offer)

    def select_offer(self, offer):
        offer_id = offer['id']
        offer_quantity = offer['quantity']
        event_logger.log_plex_offer_selected(self.log_context, offer_id, offer_quantity)
        if self.service.is_fast_checkout_enabled():
            self.hide_elements()
            self.purchaseView = PlexPurchaseView(name='purchase_view', parent=self, align=uiconst.TOALL, idx=0, state=uiconst.UI_NORMAL, opacity=0, offer=offer, close_function=self.close_func, opened_from_nes=self.opened_from_nes, log_context=self.log_context)
            animations.FadeIn(self.purchaseView, duration=0.5)
        else:
            self.service.buy_plex_online(log_context=self.log_context)

    def un_select_offer(self):
        if self.purchaseView:
            self.purchaseView.Close()

    def set_labels(self):
        self.more_information_label.SetText(localization.GetByLabel('UI/FastCheckout/DetailedOfferLabel'))
        self.online_store_link_label.SetText(localization.GetByLabel('UI/FastCheckout/accountManagement'))
        self.description_label.SetText(localization.GetByLabel('UI/FastCheckout/PlexStoreInstruction'))
        self.info_button.SetHint(localization.GetByLabel('UI/FastCheckout/PlexHint'))
        self.info_button.left = self.description_label.width + 15

    def display_elements(self):
        self.backFill.Close()
        self.main_container.SetOpacity(1)
        self.main_container.SetState(uiconst.UI_NORMAL)

    def hide_elements(self):
        self.backFill = Fill(parent=self, opacity=0.85, color=WINDOW_COLOR, idx=0, state=uiconst.UI_NORMAL)
        self.backFill.OnClick = self.un_select_offer
        self.main_container.SetOpacity(0.5)
        self.main_container.SetState(uiconst.UI_DISABLED)

    def restrict_ui_and_show_popup(self, header_text, description_text, show_button = True):
        self.hide_elements()
        RestrictionDialogue(parent=self, headerText=header_text, descriptionText=description_text, idx=0, showButton=show_button)

    def reset_highlight(self):
        for offer in self.offers:
            offer['highlight'] = False

    def close_view(self):
        uthread2.StartTasklet(sm.GetService('vgsService').GetUiController().CloseOffer)
