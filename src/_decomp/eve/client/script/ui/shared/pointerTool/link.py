#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\link.py
import evelink.client
from carbon.common.script.sys.serviceManager import ServiceManager
from eve.client.script.ui.shared.pointerTool.pointerToolConst import SOURCE_LOCATION_LINK
from globalConfig.getFunctions import ArePointerLinksActive
SCHEME_HELP_POINTER = 'helpPointer'

def get_help_pointer_link(ui_element, name):
    return evelink.Link(url=format_help_pointer_url(ui_element), text=name)


def register_link_handlers(registry):
    registry.register(SCHEME_HELP_POINTER, handle_link, hint='UI/Help/HelpPointersTooltip', color_info=evelink.help_link_color_info)


def handle_link(url):
    if not are_pointer_links_enabled():
        return
    ui_element = parse_help_pointer_url(url)
    help_pointer_service = get_service('helpPointer')
    help_pointer_service.ActivateHelperPointer(ui_element, SOURCE_LOCATION_LINK)


def are_pointer_links_enabled():
    macho_net = get_service('machoNet')
    return ArePointerLinksActive(macho_net)


def get_service(service_name):
    service_manager = ServiceManager.Instance()
    return service_manager.GetService(service_name)


def parse_help_pointer_url(url):
    return url[url.index(':') + 1:]


def format_help_pointer_url(ui_element):
    return '{}:{}'.format(SCHEME_HELP_POINTER, ui_element)
