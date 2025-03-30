#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\client\handlers\show_info\handler.py
import evetypes
import localization
from inventorycommon.const import categorySkill
from evelink.client.color import default_with_subtle_color_info
from evelink.client.handlers.show_info.parse import parse_show_info_url
from evelink.format.show_info import SCHEME

def register_show_info_handler(registry):
    registry.register(SCHEME, handle_show_info_link, hint=get_link_hint, menu=get_link_menu, color_info=default_with_subtle_color_info)


def handle_show_info_link(url):
    parsed = parse_show_info_url(url)
    sm.GetService('info').ShowInfo(parsed.type_id, parsed.item_id, abstractinfo=parsed.abstract_info)


def get_link_hint(url):
    try:
        parsed = parse_show_info_url(url)
    except Exception:
        return localization.GetByLabel('UI/Commands/ShowInfo')

    if not evetypes.Exists(parsed.type_id):
        return localization.GetByLabel('UI/Common/ShowInfo')
    elif evetypes.GetCategoryID(parsed.type_id) == categorySkill:
        return localization.GetByLabel('UI/Common/ShowTypeInfo', groupName=evetypes.GetCategoryName(parsed.type_id))
    else:
        return localization.GetByLabel('UI/Common/ShowTypeInfo', groupName=evetypes.GetGroupName(parsed.type_id))


def get_link_menu(url):
    parsed = parse_show_info_url(url)
    if parsed.bookmark_info:
        return sm.GetService('menu').BookmarkMenu(parsed.bookmark_info)
    else:
        return sm.GetService('menu').GetMenuFromItemIDTypeID(parsed.item_id, parsed.type_id, abstractInfo=parsed.abstract_info, includeMarketDetails=True)
