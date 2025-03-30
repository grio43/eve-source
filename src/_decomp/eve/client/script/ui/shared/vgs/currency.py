#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\currency.py
from carbon.common.script.util.format import FmtAmt
OFFER_CURRENCY_PLEX = 'PLX'
OFFER_CURRENCY_GEM = 'GMS'
OFFER_CURRENCY_YUAN = 'CNY'
OFFER_CURRENCY_JPY = 'JPY'
OFFER_CURRENCY_EURO = 'EUR'
OFFER_CURRENCY_POUND = 'GBP'
OFFER_CURRENCY_DOLLAR = 'USD'
OFFER_CURRENCY_RUBLE = 'RUB'
OFFER_CURRENCY_SORT_ORDER = {OFFER_CURRENCY_YUAN: 1,
 OFFER_CURRENCY_JPY: 2,
 OFFER_CURRENCY_PLEX: 3,
 OFFER_CURRENCY_GEM: 4}
CURRENCY_SYMBOL = {OFFER_CURRENCY_PLEX: '',
 OFFER_CURRENCY_GEM: '',
 OFFER_CURRENCY_YUAN: u'\xa5',
 OFFER_CURRENCY_JPY: u'\xa5',
 OFFER_CURRENCY_EURO: u'\u20ac',
 OFFER_CURRENCY_POUND: u'\xa3',
 OFFER_CURRENCY_DOLLAR: '$',
 OFFER_CURRENCY_RUBLE: u'py\u0431'}
CURRENCY_TO_DISPLAY_FRACTION = {OFFER_CURRENCY_PLEX: 0,
 OFFER_CURRENCY_YUAN: 2,
 OFFER_CURRENCY_GEM: 0,
 OFFER_CURRENCY_JPY: 0,
 OFFER_CURRENCY_EURO: 2,
 OFFER_CURRENCY_POUND: 2,
 OFFER_CURRENCY_DOLLAR: 2,
 OFFER_CURRENCY_RUBLE: 2}

def get_currency_fraction(currency):
    return CURRENCY_TO_DISPLAY_FRACTION.get(currency, 0)


def get_price_text(price, currency, useSpace = True):
    price_amount = get_price_amount(price, currency)
    currency_symbol = CURRENCY_SYMBOL.get(currency, currency)
    space = ' ' if useSpace else ''
    if currency == OFFER_CURRENCY_RUBLE:
        return '%s%s%s' % (price_amount, space, currency_symbol)
    return '%s%s%s' % (currency_symbol, space, price_amount)


def get_price_amount(price, currency):
    return FmtAmt(price, showFraction=get_currency_fraction(currency))
