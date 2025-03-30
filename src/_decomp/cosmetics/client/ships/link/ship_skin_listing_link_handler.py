#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\link\ship_skin_listing_link_handler.py
import uuid
from cosmetics.client.ships.link.scheme import LinkScheme
from cosmetics.client.shipSkinTradingSvc import get_ship_skin_trading_svc
from eve.client.script.ui.cosmetics.ship.shipSKINRWindow import ShipSKINRWindow
from eve.client.script.ui.control.message import ShowQuickMessage
from cosmetics.client.ships.skins.errors import get_listing_error_text
from localization import GetByLabel

def register_link_handlers(registry):
    registry.register(scheme=LinkScheme.SHIP_SKIN_LISTING, handler=handle_link, hint='UI/Personalization/ShipSkins/ShipSkinListingLinkHint')


def handle_link(url):
    listing_id = _parse_url(url)
    listing, error = get_ship_skin_trading_svc().get_listing(listing_id)
    if error is not None:
        ShowQuickMessage(GetByLabel(get_listing_error_text(error)))
    ShipSKINRWindow.open_external_skin_listing(listing)


def _parse_url(url):
    _, listing_id = url.split(':')
    try:
        listing_id = uuid.UUID(listing_id)
    except ValueError:
        return None

    return listing_id
