#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\shared\offerpricing.py


def get_offer_price_in_currency(offer, currency):
    for pricing in offer.offerPricings:
        if pricing.currency == currency:
            return pricing.price


def get_min_offer_price_in_currency(offers, currency):
    prices = [ get_offer_price_in_currency(o, currency) for o in offers ]
    prices = [ price for price in prices if price is not None ]
    return min(prices) or 0


def get_offer_price_and_base_price_in_currency(offer, currency):
    for pricing in offer.offerPricings:
        if pricing.currency == currency:
            return (pricing.price, pricing.basePrice)

    return (None, None)


def offer_is_available_in_currency(offer, currency):
    return get_offer_price_in_currency(offer, currency) is not None


def get_available_currencies(offer):
    return [ pricing.currency for pricing in offer.offerPricings ]


def get_number_of_available_currencies(offer):
    return len(get_available_currencies(offer))


def iter_currencies(offer):
    for pricing in offer.offerPricings:
        yield (pricing.currency, pricing.price, pricing.basePrice)
