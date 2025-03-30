#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\market.py
from .base import Event

class BuyOrderWindowPriceChanged(Event):
    atom_id = 564
    __notifyevents__ = ['OnBuyOrderWindowPriceChanged']

    def OnBuyOrderWindowPriceChanged(self):
        self.invoke()


class MarketTypeSelectionChanged(Event):
    atom_id = 567
    __notifyevents__ = ['OnMarketTypeSelectionChanged']

    def OnMarketTypeSelectionChanged(self, type_id):
        self.invoke()
