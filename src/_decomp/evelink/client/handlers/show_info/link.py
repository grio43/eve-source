#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\client\handlers\show_info\link.py
from eve.client.script.ui.util import uix
from eve.common.script.sys.idCheckers import IsCharacter, IsEvePlayerCharacter, IsCorporation, IsAlliance, IsFaction
import evetypes
import inventorycommon.const as invconst
import localization
from evelink.link import Link
from evelink.format.show_info import format_show_info_url, format_blueprint_show_info_url, format_ship_show_info_url

def item_link(item, link_text = None, hint = None):
    if link_text is None:
        link_text = uix.GetItemName(item)
    item_id = None
    if not isinstance(item.itemID, tuple):
        item_id = item.itemID
    return Link(url=format_show_info_url(item.typeID, item_id), text=link_text, alt=hint)


def type_link(type_id, item_id = None, link_text = None, hint = None):
    if link_text is None:
        link_text = evetypes.GetName(type_id)
    return Link(url=format_show_info_url(type_id, item_id), text=link_text, alt=hint)


def ship_link(type_id, item_id = None, owner_id = None, item_name = None, hint = None):
    if owner_id is not None and not IsEvePlayerCharacter(owner_id):
        owner_id = None
    type_name = evetypes.GetName(type_id, important=False)
    if owner_id:
        if item_name is not None:
            if type_name not in item_name:
                link_text = u'{} ({})'.format(item_name, type_name)
            else:
                link_text = item_name
        else:
            link_text = u'{} ({})'.format(cfg.eveowners.Get(owner_id).name, type_name)
    else:
        link_text = type_name
    return Link(url=format_ship_show_info_url(type_id, item_id, owner_id), text=link_text, alt=hint)


def blueprint_link(type_id, item_id = None, link_text = None, hint = None, runs = None, isCopy = 0, te = None, me = None):
    if link_text is None:
        link_text = evetypes.GetName(type_id)
    url = format_blueprint_show_info_url(type_id, item_id, runs, int(isCopy), te, me)
    return Link(url, text=link_text, alt=hint)


def owner_link(owner_id, link_text = None, hint = None):
    if IsCharacter(owner_id):
        return character_link(owner_id, link_text, hint)
    if IsCorporation(owner_id):
        return corporation_link(owner_id, link_text, hint)
    if IsAlliance(owner_id):
        return alliance_link(owner_id, link_text, hint)
    if IsFaction(owner_id):
        return faction_link(owner_id, link_text, hint)
    raise ValueError('Unknown owner', owner_id)


def character_link(character_id, link_text = None, hint = None):
    character_info = cfg.eveowners.Get(character_id)
    if link_text is None:
        link_text = character_info.name
    return Link(url=format_show_info_url(character_info.typeID, character_id), text=link_text, alt=hint)


def corporation_link(corporation_id, link_text = None, hint = None):
    if link_text is None:
        link_text = cfg.eveowners.Get(corporation_id).name
    return Link(url=format_show_info_url(invconst.typeCorporation, corporation_id), text=link_text, alt=hint)


def alliance_link(alliance_id, link_text = None, hint = None):
    if link_text is None:
        link_text = cfg.eveowners.Get(alliance_id).name
    return Link(url=format_show_info_url(invconst.typeAlliance, alliance_id), text=link_text, alt=hint)


def faction_link(faction_id, link_text = None, hint = None):
    if link_text is None:
        link_text = cfg.eveowners.Get(faction_id).name
    return Link(url=format_show_info_url(invconst.typeFaction, faction_id), text=link_text, alt=hint)


def location_link(location_id, link_text = None, hint = None):
    location_info = sm.GetService('map').GetItem(location_id)
    if location_info is None:
        raise ValueError('Unknown location', location_id)
    if link_text is None:
        link_text = location_info.itemName
    return Link(url=format_show_info_url(location_info.typeID, location_id), text=link_text, alt=hint)
