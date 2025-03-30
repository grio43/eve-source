#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\personalMarketOrders.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label
from eve.client.script.ui.shared.market.orders import MarketOrders
from eve.common.lib import appConst
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel

class PersonalMarketOrders(MarketOrders):

    def GetOrders(self):
        return sm.GetService('marketQuote').GetMyOrders()

    def ConstructBottomCont(self):
        self.bottomCont = Container(name='bottomCont', parent=self, align=uiconst.TOBOTTOM, height=24, idx=0, clipChildren=True)
        self.limits = sm.GetService('marketQuote').GetSkillLimits(None)
        self.leftLimitsLabel = EveLabelMedium(parent=self.bottomCont, align=uiconst.TOLEFT, padding=4, tabs=[175, 500], state=uiconst.UI_NORMAL)
        self.leftLimitsLabel2 = EveLabelMedium(parent=self.bottomCont, align=uiconst.TOLEFT, padding=4, state=uiconst.UI_NORMAL)

    def UpdateOrderTotals(self, orders):
        if orders is None:
            return
        self.totalEscrow = 0.0
        self.totalLeft = 0.0
        self.totalIncome = 0.0
        self.totalExpenses = 0.0
        for order in orders:
            if order.bid:
                self.totalExpenses += order.price * order.volRemaining
                self.totalEscrow += order.escrow
                self.totalLeft += order.volRemaining * order.price - order.escrow
            else:
                self.totalIncome += order.price * order.volRemaining

        self.UpdateCounter(orders)

    def UpdateCounter(self, orders = None):
        current = len(orders)
        maxCount = self.limits['cnt']
        self.leftLimitsLabel.text = GetByLabel('UI/Market/Orders/OrdersRemaining', remaining=maxCount - current, maxCount=maxCount, escrow=FmtISK(self.totalEscrow, showFractionsAlways=False), totalLeft=FmtISK(self.totalLeft, showFractionsAlways=False), feeLimit=self.GetBrokersFeeForOrders(orders), accLimit=round(self.limits['acc'], 4) * 100, income=FmtISK(self.totalIncome, showFractionsAlways=False), expenses=FmtISK(self.totalExpenses, showFractionsAlways=False))
        askLimit = self.limits['ask']
        bidLimit = self.limits['bid']
        modLimit = self.limits['mod']
        visLimit = self.limits['vis']
        if askLimit == -1 and bidLimit == -1 and modLimit == -1 and visLimit == -1:
            self.leftLimitsLabel2.text = GetByLabel('UI/Market/Orders/OrderRangesWithoutRemote')
        else:
            self.leftLimitsLabel2.text = GetByLabel('UI/Market/Orders/OrderRanges', askLimit=self.GetLimitText(askLimit), bidLimit=self.GetLimitText(bidLimit), modLimit=self.GetLimitText(modLimit), visLimit=self.GetLimitText(visLimit))
        self.bottomCont.height = max(20, self.leftLimitsLabel.textheight + 8, self.leftLimitsLabel2.textheight + 8)

    def GetBrokersFeeForOrders(self, orders):
        numValidOrders = 0
        totalFee = 0
        for eachOrder in orders:
            fee = self.limits.GetBrokersFeeForLocation(eachOrder.stationID)
            if fee is None:
                continue
            totalFee += fee * 100
            numValidOrders += 1

        if numValidOrders:
            return round(totalFee / numValidOrders, 2)
        else:
            return appConst.marketCommissionPercentage

    def GetLimitText(self, limit):
        if limit == appConst.rangeStation:
            text = GetByLabel('UI/Market/Orders/LimitedToStations')
        elif limit == appConst.rangeSolarSystem:
            text = GetByLabel('UI/Market/Orders/LimitedToSystem')
        elif limit == appConst.rangeRegion:
            text = GetByLabel('UI/Market/Orders/LimitedToRegions')
        else:
            text = GetByLabel('UI/Market/Orders/LimitedToJumps', jumps=limit)
        return text
