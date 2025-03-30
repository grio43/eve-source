#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\live_data\slot_layout.py
from cosmetics.client.ships.skins.live_data.component_instance import create_component_instance, build_config_proto_from_component_instance
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from cosmetics.common.ships.skins.live_data.slot_layout import BaseSlotLayout
from eve.client.script.ui.control.message import ShowQuickMessage
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.slot.slot_pb2 import Identifier as SlotIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.thirdparty_pb2 import Layout
from eveProto.generated.eve_public.ship.ship_type_pb2 import Identifier as ShipTypeIdentifier
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException

class SlotLayout(BaseSlotLayout):
    LAYOUT_PROTO = Layout
    SLOT_IDENTIFIER_PROTO = SlotIdentifier
    SHIP_TYPE_PROTO = ShipTypeIdentifier

    def create_component_instance(self, component_id, **kwargs):
        return create_component_instance(component_id, **kwargs)

    @classmethod
    def build_config_proto_from_component_instance(cls, component_instance):
        return build_config_proto_from_component_instance(component_instance)

    def get_component_license(self, component_id, component_type):
        try:
            return get_ship_skin_component_svc().get_default_license_to_use(component_id, component_type)
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            return None

    def get_component_license_of_type(self, component_id, component_type, license_type):
        try:
            return get_ship_skin_component_svc().get_license(component_id, component_type, license_type)
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            return None
