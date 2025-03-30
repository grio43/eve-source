#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\loyaltyPointStore\selectQuantityWnd.py
from carbonui import uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelMedium

class SelectQuantityWnd(Window):
    __guid__ = 'form.LPStore.ConfirmAmount'
    default_windowID = 'lpstore.ConfirmAmount'
    default_captionLabelPath = 'UI/LPStore/selectAmount'
    default_width = 300
    default_height = 230

    def ApplyAttributes(self, attributes):
        super(SelectQuantityWnd, self).ApplyAttributes(attributes)
        self.main = None

    @classmethod
    def ConfirmPurchaseQuantity(cls, offerString, maxAmount, purchaseCallback):
        wnd = SelectQuantityWnd.GetIfOpen()
        if wnd is None:
            wnd = SelectQuantityWnd.Open()
        wnd._Construct(offerString, maxAmount, purchaseCallback)
        wnd.Maximize()

    def _Confirm(self, amount, purchaseCallback):
        purchaseCallback(amount)
        self.Close()

    def _Construct(self, offerString, maxAmount, purchaseCallback):
        if self.main:
            self.main.Flush()
        self.main = Container(parent=self.sr.main)
        amountRow = Container(parent=self.main, align=uiconst.TOTOP, height=32, padBottom=24, padTop=24)
        labelCont = ContainerAutoSize(parent=amountRow, width=170, align=uiconst.TOLEFT, alignMode=uiconst.TOTOP)
        EveLabelMedium(parent=labelCont, name='OfferText', align=uiconst.TOTOP, text=offerString)
        amountEdit = SingleLineEditInteger(name='offerString', parent=amountRow, align=uiconst.TORIGHT, maxValue=maxAmount, minValue=1, width=100)
        amountEdit.SetValue(1)
        group = ButtonGroup(parent=self.main, align=uiconst.TOBOTTOM)
        Button(parent=group, label='Purchase', func=lambda *args: self._Confirm(amountEdit.GetValue(), purchaseCallback))
        Button(parent=group, label='Cancel', func=self.Close)
