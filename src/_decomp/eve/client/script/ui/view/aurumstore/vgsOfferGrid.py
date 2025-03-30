#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\vgsOfferGrid.py
import math
import signals
from carbonui import uiconst
from carbonui.primitives.flowcontainer import FlowContainer
from eve.client.script.ui.view.aurumstore.vgsOffer import VgsOffer
from eve.client.script.ui.view.aurumstore.vgsShipSkinBanner import ShipSkinBanner
from eve.client.script.ui.view.aurumstore import vgsUiConst

class OfferGrid(FlowContainer):
    default_name = 'OfferGrid'

    def __init__(self, **kwargs):
        FlowContainer.__init__(self, **kwargs)
        self.offers = []
        self.index = 0
        self.visibleColumns = self.GetVisibleColumns()
        self.onUpdate = signals.Signal(signalName='onUpdate2')

    def SetOffers(self, offers, show_skinr_banner = False):
        self.Flush()
        self.FlagAlignmentDirty()
        self.UpdateAlignment()
        self.index = 0
        self.offers = offers
        if show_skinr_banner:
            self.ship_skin_banner = ShipSkinBanner(name='ship_skin_banner', parent=self, align=uiconst.NOALIGN)
        self.onUpdate()

    def RemoveOffer(self, offerID, show_skinr_banner = False):
        self.SetOffers([ offer for offer in self.offers if offer.id != offerID ], show_skinr_banner)

    def GetOffers(self):
        return self.offers

    def _OnResize(self, *args):
        visibleColumns = self.GetVisibleColumns()
        cellWidth = visibleColumns * vgsUiConst.OFFER_IMAGE_SIZE
        padWidth = (visibleColumns - 1) * vgsUiConst.CONTENT_PADDING
        self.width = cellWidth + padWidth
        self.FlagAlignmentDirty()

    def HasAdditionalContent(self):
        if self.destroyed:
            return False
        return len(self.offers) > self.index

    def LoadAdditionalContent(self):
        for i in range(self.GetVisibleColumns()):
            if self.index >= len(self.offers):
                break
            offer = self.offers[self.index]
            VgsOffer(parent=self, width=vgsUiConst.OFFER_IMAGE_SIZE, height=vgsUiConst.OFFER_IMAGE_SIZE, align=uiconst.NOALIGN, offer=offer, image=offer.imageUrl, state=uiconst.UI_NORMAL, upperText=offer.name)
            self.index += 1

        self.FlagAlignmentDirty()

    def GetVisibleColumns(self):
        if self.destroyed:
            return 0
        width, _ = self.GetAbsoluteSize()
        return int(math.floor(width / (vgsUiConst.OFFER_IMAGE_SIZE + vgsUiConst.CONTENT_PADDING)))
