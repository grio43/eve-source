#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\link\ship_skin_design_link_handler.py
import uuid
from cosmetics.client.ships.link.scheme import LinkScheme
from cosmetics.client.shipSkinDesignSvc import get_ship_skin_design_svc
from cosmetics.client.ships.skins.errors import SkinDesignSharingError
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.shipSKINRWindow import ShipSKINRWindow
from localization import GetByLabel

def register_link_handlers(registry):
    registry.register(scheme=LinkScheme.SHIP_SKIN_DESIGN, handler=handle_link, hint='UI/Personalization/ShipSkins/LinkHint')


def handle_link(url):
    design_data = None
    error = None
    character_id, design_id = _parse_url(url)
    design_data, error = get_ship_skin_design_svc().get_shared_design(character_id, design_id, force_refresh=True)
    if design_data is not None:
        ShipSKINRWindow.open_external_design(character_id, design_id)
    if design_data is None:
        if error == SkinDesignSharingError.DESIGN_NOT_FOUND:
            ShowQuickMessage(GetByLabel('UI/Personalization/ShipSkins/DesignLinkNotFound'))
        else:
            ShowQuickMessage(GetByLabel('UI/Personalization/ShipSkins/DesignLinkFailed'))


def _parse_url(url):
    _, identifiers = url.split(':')
    character_id, design_id = identifiers.split('/')
    character_id = int(character_id)
    try:
        design_id = uuid.UUID(design_id)
    except ValueError:
        return (None, None)

    return (character_id, design_id)
