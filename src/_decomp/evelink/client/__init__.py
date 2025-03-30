#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\client\__init__.py
from evelink import *
from .const import LinkState, LinkStyle
from .color import LinkColorInfo, default_link_color_info, default_with_subtle_color_info, external_link_color_info, help_link_color_info, invite_link_color_info, settings_link_color_info
from .handlers.show_info.link import alliance_link, character_link, corporation_link, faction_link, item_link, location_link, owner_link, type_link, blueprint_link, ship_link
from .handlers.show_info.parse import parse_show_info_url
from .service import LinkService
