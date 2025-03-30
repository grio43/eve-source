#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\marketOrdersWnd.py
from carbonui.control.window import Window
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from eve.client.script.ui.shared.market import marketOrdersUtil
from eve.client.script.ui.shared.market.corpMarketOrders import CorpMarketOrders
from eve.client.script.ui.shared.market.marketHistory import MarketHistory
from eve.client.script.ui.shared.market.personalMarketOrders import PersonalMarketOrders
from eve.common.lib import appConst
from localization import GetByLabel
TABID_PERSONAL = 1
TABID_CORP = 2

class MarketOrdersWnd(Window):
    default_width = 600
    default_height = 500
    default_windowID = 'marketOrders'
    default_captionLabelPath = 'Tooltips/StationServices/MarketOrders'
    default_descriptionLabelPath = 'Tooltips/StationServices/MarketOrders_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/marketOrders.png'
    default_minSize = (300, 300)

    def ApplyAttributes(self, attributes):
        super(MarketOrdersWnd, self).ApplyAttributes(attributes)
        tabID = attributes.tabID
        self.ConstructLayout(tabID)

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader()

    def ConstructLayout(self, tabID = None):
        self.ConstructPersonalAndCorp(tabID)

    def IsCorpOrdersAccessible(self):
        return session.corprole & appConst.corpRoleAccountant

    def ConstructPersonalAndCorp(self, tabID):
        if self.IsCorpOrdersAccessible():
            self.corpOrders = CorpMarketOrders(parent=self.sr.main, isCorp=True, padding=4)
        else:
            self.corpOrders = None
        self.personalOrders = PersonalMarketOrders(parent=self.sr.main, padding=4)
        self.marketHistory = MarketHistory(parent=self.sr.main, padding=4)
        tabs = [(GetByLabel('UI/Market/Orders/MyOrders'),
          self.personalOrders,
          self.personalOrders,
          1)]
        if self.IsCorpOrdersAccessible():
            (tabs.append((GetByLabel('UI/Market/Orders/CorporationOrders'),
              self.corpOrders,
              self.corpOrders,
              2)),)
            nextIdx = 3
        else:
            nextIdx = 2
        tabs.append((GetByLabel('UI/Market/Orders/MyOrderHistory'),
         self.marketHistory,
         self.marketHistory,
         nextIdx))
        self.tabGroup = self.header.tab_group
        self.tabGroup.Startup(tabs, 'marketTransactions', autoselecttab=tabID is None)
        if tabID:
            self.tabGroup.SelectByID(tabID)

    def GetMenuMoreOptions(self):
        menuData = super(MarketOrdersWnd, self).GetMenuMoreOptions()
        menuData.AddEntry(GetByLabel('Tooltips/Market/MarketMyOrdersExportButton'), self.ExportPersonal)
        if self.IsCorpOrdersAccessible():
            menuData.AddEntry(GetByLabel('Tooltips/Market/MarketCorpOrdersExport'), self.ExportCorp)
        return menuData

    def ExportPersonal(self):
        marketOrdersUtil.ExportToFile(fileName=GetByLabel('UI/Market/Orders/MyOrders'), orders=sm.GetService('marketQuote').GetMyOrders())

    def ExportCorp(self):
        marketOrdersUtil.ExportToFile(fileName=GetByLabel('UI/Market/Orders/CorporationOrders'), orders=sm.GetService('marketQuote').GetCorporationOrders())
