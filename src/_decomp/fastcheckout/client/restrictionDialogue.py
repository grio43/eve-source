#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fastcheckout\client\restrictionDialogue.py
import carbonui.const as uiconst
import localization
from carbonui.primitives.container import Container
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelMedium
from eve.client.script.ui.shared.vgs.offerWindowUnderlay import OfferWindowUnderlay
from fastcheckout.client.purchasepanels.purchaseButton import PurchaseButton

class RestrictionDialogue(Container):
    default_width = 500
    default_height = 215
    default_bgColor = (0.2, 0.2, 0.2, 1)
    default_align = uiconst.CENTER
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(RestrictionDialogue, self).ApplyAttributes(attributes)
        self.headerText = attributes.get('headerText', None)
        self.descriptionText = attributes.get('descriptionText', None)
        self.show_button = attributes.get('showButton', True)
        self.construct_layout()
        self.prepare_background_fill()

    def construct_layout(self):
        self.main_container = Container(name='MainContainer', parent=self, align=uiconst.TOALL, clipChildren=True)
        self.header_container = Container(name='HeaderContainer', parent=self.main_container, align=uiconst.TOTOP, height=50)
        self.header_label = EveCaptionLarge(name='HeaderLabel', parent=self.header_container, align=uiconst.CENTER, text=self.headerText)
        self.bottom_container = Container(name='BottomContainer', parent=self.main_container, align=uiconst.TOBOTTOM, height=50, padding=(0, 0, 0, 30))
        self.browser_button = PurchaseButton(parent=self.bottom_container, align=uiconst.CENTER, width=200, height=35, text=localization.GetByLabel('UI/FastCheckout/DisabledButtonLabel'), func=lambda : self.open_online_plex_store(), state=uiconst.UI_NORMAL if self.show_button else uiconst.UI_HIDDEN)
        self.description_label = EveLabelMedium(parent=Container(name='DescriptionContainer', parent=self.main_container, align=uiconst.TOALL, padding=(10, 0, 10, 0)), align=uiconst.TOALL, text=self.descriptionText)

    def prepare_background_fill(self):
        self.sr.underlay = OfferWindowUnderlay(parent=self)

    @staticmethod
    def open_online_plex_store():
        sm.GetService('fastCheckoutClientService').buy_plex_online(log_context='FastCheckout_RestrictionDialogue')
