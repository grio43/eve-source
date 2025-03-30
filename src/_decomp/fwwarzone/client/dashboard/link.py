#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\link.py
from evelink.client import default_with_subtle_color_info
SCHEME_FW_SYSTEM = 'fwSystemLink'

def register_link_handlers(registry):
    registry.register(scheme=SCHEME_FW_SYSTEM, handler=handle_fw_system_link, color_info=default_with_subtle_color_info)


def handle_fw_system_link(url):
    from fwwarzone.client.dashboard.fwWarzoneDashboard import FwWarzoneDashboard
    parts = url.split(':')
    factionIdString = parts[1]
    systemIdString = parts[2]
    wnd = FwWarzoneDashboard.GetIfOpen()
    if wnd and not wnd.destroyed:
        wnd.Maximize()
        wnd.SetFaction(int(factionIdString))
    else:
        wnd = FwWarzoneDashboard.Open(factionID=int(factionIdString))
    wnd.SelectSolarSystem(int(systemIdString), forceExpanded=True)
