#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipSkinLicenseNoticeMessenger.py
import logging
from cosmetics.client.ships.ship_skin_svc_signals import *
from cosmetics.client.ships.skins.live_data.skin_license import SkinLicense
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.license.api.notices_pb2 import AddedNotice, UpdatedNotice, DeletedNotice
logger = logging.getLogger(__name__)

class PublicShipSkinLicenseNoticeMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(AddedNotice, self._on_license_added_notice)
        self.public_gateway.subscribe_to_notice(UpdatedNotice, self._on_license_updated_notice)
        self.public_gateway.subscribe_to_notice(DeletedNotice, self._on_license_deleted_notice)

    def _on_license_added_notice(self, notice_payload, _notice_primitive):
        skin_hex = notice_payload.id.skin.hex
        character_id = notice_payload.id.character.sequential
        license_data = SkinLicense.build_from_proto(notice_payload.attributes, skin_hex, character_id)
        on_skin_license_added_internal(skin_hex, license_data)

    def _on_license_updated_notice(self, notice_payload, _notice_primitive):
        skin_hex = notice_payload.id.skin.hex
        character_id = notice_payload.id.character.sequential
        license_data = SkinLicense.build_from_proto(notice_payload.attributes, skin_hex, character_id)
        previous_license_data = SkinLicense.build_from_proto(notice_payload.previous_attributes, skin_hex, character_id)
        on_skin_license_updated_internal(skin_hex, license_data, previous_license_data)

    def _on_license_deleted_notice(self, notice_payload, _notice_primitive):
        skin_hex = notice_payload.id.skin.hex
        character_id = notice_payload.id.character.sequential
        on_skin_license_deleted_internal(skin_hex, character_id)
