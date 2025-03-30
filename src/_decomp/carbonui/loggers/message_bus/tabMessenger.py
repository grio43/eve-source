#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\loggers\message_bus\tabMessenger.py
from eveProto.generated.eve_public.app.eveonline.generic_ui.tab.tab_pb2 import Selected as TabSelected

class TabMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def tab_selected(self, hierarchy_path, tab_id, tab_group_id):
        event = TabSelected()
        event.context.hierarchy_path = hierarchy_path
        event.name = tab_id
        event.group_name = tab_group_id
        self.public_gateway.publish_event_payload(event)
