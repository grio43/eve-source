#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\market.py
from nodegraph.client.util import get_item_name
from .base import Condition

class BuyOrder(Condition):
    atom_id = 565

    def __init__(self, type_id = None, station_id = None, min_quantity = None, max_price = None, **kwargs):
        super(BuyOrder, self).__init__(**kwargs)
        self.type_id = type_id
        self.station_id = station_id
        self.min_quantity = min_quantity
        self.max_price = max_price

    def validate(self, **kwargs):
        from eve.client.script.ui.shared.market.buyThisTypeWindow import MarketActionWindow
        window = MarketActionWindow.GetIfOpen()
        if not window:
            return False
        try:
            buy_info = window.GetBuyInfo()
        except:
            return False

        if self.type_id and buy_info['typeID'] != self.type_id:
            return False
        if self.station_id and buy_info['stationID'] != self.station_id:
            return False
        if self.min_quantity and buy_info['quantity'] < self.min_quantity:
            return False
        if self.max_price and buy_info['bidPrice'] > self.max_price:
            return False
        return True

    @classmethod
    def get_subtitle(cls, type_id = None, station_id = None, min_quantity = None, max_price = None, **kwargs):
        result = []
        if min_quantity:
            result.append(u'q\u2265{}'.format(min_quantity))
        if max_price:
            result.append(u'isk\u2264{}'.format(max_price))
        if type_id:
            result.append('type')
        if station_id:
            result.append('station')
        return ' '.join(result)


class ViewingMarket(Condition):
    atom_id = 566

    def __init__(self, type_id = None, **kwargs):
        super(ViewingMarket, self).__init__(**kwargs)
        self.type_id = type_id

    def validate(self, **kwargs):
        from eve.client.script.ui.shared.market.marketbase import RegionalMarket
        window = RegionalMarket.GetIfOpen()
        if not window:
            return False
        selected_type = window.sr.market.GetTypeIDFromDetails()
        if self.type_id and selected_type != self.type_id:
            return False
        return True

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        if type_id:
            return get_item_name(type_id=type_id)
        return ''


class InSellWindow(Condition):
    atom_id = 611

    def __init__(self, type_id = None, **kwargs):
        super(InSellWindow, self).__init__(**kwargs)
        self.type_id = type_id

    def validate(self, **kwargs):
        from eve.client.script.ui.shared.market.sellMulti import SellItems
        window = SellItems.GetIfOpen()
        if not window:
            return False
        if not self.type_id:
            return True
        for item in window.itemDict.values():
            if item.typeID == self.type_id:
                return True

        return False

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        if type_id:
            return get_item_name(type_id=type_id)
        return ''
