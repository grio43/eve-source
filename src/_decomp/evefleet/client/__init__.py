#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evefleet\client\__init__.py
try:
    from evefleet.client.dragdata import FleetDragData
    from evefleet.client.link import register_link_handlers, format_fleet_url, get_fleet_link
    from evefleet.client.menu import MemberMenu
    from evefleet.client.ui.color_picker import FleetColorPickerCont
except ImportError:
    from monolithconfig import on_client
    if on_client():
        raise
