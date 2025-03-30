#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\menuSvcExtras\marketMenu.py
import structures
from eve.client.script.ui.shared.market.sellMulti import SellItems as SellItemsWnd
from eve.common.script.sys import idCheckers

def SellItems(invItems):
    sm.GetService('marketutils').StartupCheck()
    wnd = SellItemsWnd.GetIfOpen()
    if wnd is not None:
        wnd.AddPreItems(invItems)
        wnd.Maximize()
    else:
        itemLocationID = sm.GetService('invCache').GetStationIDOfItem(invItems[0])
        if not idCheckers.IsStation(itemLocationID):
            sm.RemoteSvc('structureSettings').CharacterCheckService(itemLocationID, structures.SERVICE_MARKET)
        SellItemsWnd.Open(preItems=invItems)
