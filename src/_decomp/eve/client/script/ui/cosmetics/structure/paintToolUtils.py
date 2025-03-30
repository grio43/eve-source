#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\paintToolUtils.py
from appConst import corpHeraldry
from eve.client.script.ui.cosmetics.structure import paintToolSelections

def get_evermark_balance():
    everMarks = sm.GetService('loyaltyPointsWalletSvc').GetCorporationEvermarkBalance()
    return everMarks


def get_total_price():
    total_price = 0
    for structure_data in paintToolSelections.SELECTED_STRUCTURES.itervalues():
        price = structure_data.get_price_for_duration(paintToolSelections.SELECTED_DURATION)
        if price is not None:
            total_price += price

    return total_price


def has_sufficient_funds():
    return get_evermark_balance() >= get_total_price()
