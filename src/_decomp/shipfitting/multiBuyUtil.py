#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipfitting\multiBuyUtil.py
from collections import defaultdict
from localization import GetByLabel

def AddBuyButton(parent, fittingMgmtWnd):
    from carbonui.control.button import Button

    def CallBuyFit():
        fitting = fittingMgmtWnd.fitting
        BuyFit(fitting.shipTypeID, fitting.fitData)

    Button(parent=parent, label=GetByLabel('UI/Market/MarketQuote/CommandBuy'), func=lambda *args: CallBuyFit())


def BuyFit(shipTypeID, fitData, *args):
    buyDict = defaultdict(int)
    for typeID, flag, qty in fitData:
        buyDict[typeID] += qty

    buyDict[shipTypeID] = 1
    BuyMultipleTypesWithQty(buyDict)


def BuyMultipleTypes(items, *args):
    buyDict = {}
    for item in items:
        buyDict[item.typeID] = 1

    BuyMultipleTypesWithQty(buyDict)


def BuyMultipleTypesWithQty(buyDict, fitting = None):
    if session.stationid and not sm.GetService('cmd').HasServiceAccess('market', True):
        return
    from eve.client.script.ui.shared.market.buyMultiFromBase import MultiBuy
    wnd = MultiBuy.GetIfOpen()
    if wnd and not wnd.destroyed:
        wnd.AddToOrder(wantToBuy=buyDict, fitting=fitting)
    else:
        wnd = MultiBuy(wantToBuy=buyDict, fitting=fitting)
    wnd.Maximize()
    return wnd
