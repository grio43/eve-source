#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipSkinSequencingNoticeMessenger.py
import logging
import uuid
from cosmetics.client.ships.ship_skin_svc_signals import *
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.sequencing.job.api.notices_pb2 import StartedNotice, CompletedNotice, FailedNotice
logger = logging.getLogger(__name__)

class PublicShipSkinSequencingNoticeMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(StartedNotice, self._on_sequencing_started_notice)
        self.public_gateway.subscribe_to_notice(FailedNotice, self._on_sequencing_failed_notice)
        self.public_gateway.subscribe_to_notice(CompletedNotice, self._on_sequencing_completed_notice)

    def _on_sequencing_started_notice(self, notice_payload, _notice_primitive):
        job_id = uuid.UUID(bytes=notice_payload.id.uuid)
        on_sequencing_started_internal(job_id)

    def _on_sequencing_failed_notice(self, notice_payload, _notice_primitive):
        job_id = uuid.UUID(bytes=notice_payload.id.uuid)
        reason = notice_payload.reason
        on_sequencing_failed_internal(job_id, reason)

    def _on_sequencing_completed_notice(self, notice_payload, _notice_primitive):
        job_id = uuid.UUID(bytes=notice_payload.id.uuid)
        on_sequencing_completed_internal(job_id)
