#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipSkinComponentLicenseNoticeMessenger.py
import logging
import uuid
from cosmetics.client.ships.ship_skin_svc_signals import *
from cosmetics.client.ships.skins.live_data.component_license import ComponentLicense
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.api.notices_pb2 import GrantedNotice
logger = logging.getLogger(__name__)

class PublicShipComponentLicenseNoticeMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(GrantedNotice, self._on_component_license_granted_notice)

    def _on_component_license_granted_notice(self, notice_payload, _notice_primitive):
        component_id = ComponentLicense.get_component_id_from_proto(notice_payload.kind.component)
        quantity = notice_payload.kind.finite if notice_payload.kind.HasField('finite') else None
        on_component_license_granted_internal(component_id, quantity)
