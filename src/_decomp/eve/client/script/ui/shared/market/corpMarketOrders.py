#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\corpMarketOrders.py
from eve.client.script.ui.shared.market.orders import MarketOrders
from localization import GetByLabel

class CorpMarketOrders(MarketOrders):

    def GetOrders(self):
        return sm.GetService('marketQuote').GetCorporationOrders()

    def GetBuyHeaders(self):
        bheaders = super(CorpMarketOrders, self).GetBuyHeaders()
        bheaders.extend((GetByLabel('UI/Market/MarketQuote/headerIssuedBy'), GetByLabel('UI/Market/MarketQuote/headerWalletDivision')))
        return bheaders

    def GetSellHeaders(self):
        sheaders = super(CorpMarketOrders, self).GetSellHeaders()
        sheaders.extend((GetByLabel('UI/Market/MarketQuote/headerIssuedBy'), GetByLabel('UI/Market/MarketQuote/headerWalletDivision')))
        return sheaders
