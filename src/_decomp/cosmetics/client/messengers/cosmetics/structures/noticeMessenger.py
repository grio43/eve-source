#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\structures\noticeMessenger.py
from signals import Signal
import eveProto.generated.eve_public.cosmetic.structure.paintwork.api.api_pb2 as api
from cosmetics.client.structures.fitting import create_structure_paintwork_from_proto_slot_config

class NoticeMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(api.SetNotice, self._on_set_notice)
        self.public_gateway.subscribe_to_notice(api.SetAllInSolarSystemNotice, self._on_set_all_in_system_notice)
        self.on_structure_cosmetic_state_changed_internal = Signal()
        self.on_structure_cosmetic_state_solar_system_update_internal = Signal()

    def _on_set_notice(self, on_set_notice, _notice_primitive):
        structure_id = on_set_notice.structure.sequential
        paintwork = create_structure_paintwork_from_proto_slot_config(on_set_notice.paintwork)
        self.on_structure_cosmetic_state_changed_internal(structure_id, paintwork)

    def _on_set_all_in_system_notice(self, on_set_all_notice, _notice_primitive):
        paintworks = {each.structure.sequential:create_structure_paintwork_from_proto_slot_config(each.paintwork) for each in on_set_all_notice.paintworks}
        solar_system_id = on_set_all_notice.solar_system.sequential
        self.on_structure_cosmetic_state_solar_system_update_internal(paintworks, solar_system_id)
