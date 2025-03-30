#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\controls\buyerFee.py
from carbonui import Align, TextBody, TextHeader, TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.common.script.util.eveFormat import FmtAmt
from inventorycommon.const import typeLoyaltyPointsHeraldry
from localization import GetByLabel

class BuyerFee(ContainerAutoSize):
    default_display = False
    default_alignMode = Align.TOTOP

    def __init__(self, *args, **kwargs):
        super(BuyerFee, self).__init__(*args, **kwargs)
        self._amount = None
        self.construct_layout()

    def construct_layout(self):
        self.construct_header()
        self.construct_fee()

    def construct_header(self):
        title_container = Container(name='title_container', parent=self, align=Align.TOTOP, height=26)
        TextHeader(name='title_label', parent=title_container, align=Align.TOLEFT, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/BrandManagerListing'), color=eveColor.SUCCESS_GREEN)
        HeaderInfoIcon(name='info_icon', parent=ContainerAutoSize(parent=title_container, align=Align.TOLEFT, padLeft=4), align=Align.CENTERLEFT)

    def construct_fee(self):
        self.fee_container = ContainerAutoSize(name='fee_container', parent=self, align=Align.TOTOP, alignMode=uiconst.TOTOP)
        self.construct_amount_container()
        TextBody(name='subheader_label', parent=self.fee_container, align=Align.TOTOP, text=self.subheader_label_text, padding=(0, 4, 0, 4))

    def construct_amount_container(self):
        amount_container = ContainerAutoSize(name='amount_container', parent=self.fee_container, align=Align.TOPRIGHT, alignMode=Align.CENTERRIGHT, state=uiconst.UI_NORMAL, hint=GetByLabel('UI/Personalization/ShipSkins/SKINR/BuyersFeeHint'))
        Fill(bgParent=self.fee_container, color=eveColor.SUCCESS_GREEN, opacity=0.2)
        ItemIcon(name='evermark_icon', parent=amount_container, align=uiconst.CENTERLEFT, width=16, height=16, typeID=typeLoyaltyPointsHeraldry)
        self.amount_label = TextBody(name='amount_label', parent=amount_container, align=Align.CENTERRIGHT, color=TextColor.SECONDARY, padding=(20, 4, 0, 4))

    def update(self):
        self.display = self.amount is not None and self.amount > 0
        self.amount_label.text = None if self.amount is None else FmtAmt(self.amount)

    @property
    def subheader_label_text(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/BrandManagerListingDescription')

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = value
        self.update()


class HeaderInfoIcon(InfoIcon):

    def ConstructTooltipPanel(self):
        return HeaderTooltipPanel()


class HeaderTooltipPanel(TooltipPanel):

    def __init__(self, **kw):
        super(HeaderTooltipPanel, self).__init__(**kw)
        self.LoadStandardSpacing()
        self.AddCell(TextBody(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/BrandManagerListingInfo'), width=300), colSpan=2)


class SellSKINBuyerFee(BuyerFee):
    pass


class BuySKINBuyerFee(BuyerFee):
    default_height = 60

    @property
    def subheader_label_text(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/BuyerEverMarkFee')
