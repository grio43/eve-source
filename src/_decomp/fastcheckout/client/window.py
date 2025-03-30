#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fastcheckout\client\window.py
import carbonui.const as uiconst
import localization
from carbonui.primitives.container import Container
from carbonui.control.window import Window
from eve.client.script.ui.plex.textures import PLEX_WINDOW_ICON
from eve.client.script.ui.shared.vgs.offerWindowHeader import OfferWindowHeader
from eve.client.script.ui.shared.vgs.offerWindowUnderlay import OfferWindowUnderlay
from fastcheckout.client.fastCheckoutStoreView import FastCheckoutStoreView
from fastcheckout.client.restrictionDialogue import RestrictionDialogue
from fastcheckout.const import FULL_WINDOW_WIDTH, FULL_WINDOW_HEIGHT

class FastCheckoutWindow(Window):
    __guid__ = 'FastCheckoutWindow'
    default_windowID = 'FastCheckoutWindow'
    default_iconNum = PLEX_WINDOW_ICON
    default_captionLabelPath = 'UI/FastCheckout/Name'
    default_isCollapseable = False
    default_isStackable = False
    default_height = FULL_WINDOW_HEIGHT
    default_width = FULL_WINDOW_WIDTH

    def ApplyAttributes(self, attributes):
        super(FastCheckoutWindow, self).ApplyAttributes(attributes)
        self.closeFunc = attributes.get('closeFunc', None)
        self.logContext = attributes.get('logContext', 'Not Specified')
        self.offerId = attributes.get('offerId', None)
        self.main = self.GetMainArea()
        self.fastCheckoutService = sm.RemoteSvc('FastCheckoutService')
        self.HideHeader()
        self.MakeUnResizeable()
        self.construct_layout()
        self.construct_store_view()

    def Close(self, *args, **kwds):
        super(FastCheckoutWindow, self).Close(*args, **kwds)
        sm.GetService('fastCheckoutClientService').stop_purchase_flow()

    def construct_layout(self):
        OfferWindowHeader(parent=self.main, align=uiconst.TOTOP, onExit=self.CloseByUser)
        self.main_container = Container(name='MainContainer', parent=self.main)

    def construct_store_view(self):
        self.storeView = FastCheckoutStoreView(name='FastCheckoutStoreView', parent=self.main_container, closeFunc=self.closeFunc, logContext=self.logContext, offerId=self.offerId)

    def MakeUnResizeable(self):
        self._resizeable = False
        self.Prepare_ScaleAreas_()
        self.MakeUnstackable()

    def Prepare_Background_(self):
        self.sr.underlay = OfferWindowUnderlay(parent=self)

    def display_elements(self):
        self.main_container.SetOpacity(1)
        self.main_container.SetState(uiconst.UI_NORMAL)

    def hide_elements(self):
        self.main_container.SetOpacity(0.3)
        self.main_container.SetState(uiconst.UI_DISABLED)

    def restrict_ui_and_show_popup(self):
        RestrictionDialogue(parent=self, headerText=localization.GetByLabel('UI/FastCheckout/ServiceUnavailableHeader'), descriptionText='<center>%s</center>' % localization.GetByLabel('UI/FastCheckout/ServiceUnavailableDescription'), idx=0)
