#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipSkinSequencingRequestMessenger.py
import logging
import uuid
from cosmetics.client.ships.skins.live_data.component_license import ComponentLicense
from cosmetics.client.ships.skins.live_data.sequencing_job import SequencingJob
from cosmetics.client.ships.skins.errors import SequencingJobError, GenericError, STATUS_CODE_TO_INITIATE_SEQUENCING_ERROR, STATUS_CODE_TO_EXPEDITE_SEQUENCING_ERROR
from cosmetics.client.ships.skins.live_data.skin_design import SkinDesign
from cosmetics.client.ships.skins.live_data.slot_layout import SlotLayout
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.sequencing.job.job_pb2 import Identifier as JobIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.license_pb2 import Kind as LicenseKind
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.sequencing.job.api.requests_pb2 import GetRequest, GetResponse, GetAllActiveRequest, GetAllActiveResponse, InitiateRequest, InitiateResponse, CompleteEarlyRequest, CompleteEarlyResponse
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.sequencing.api.requests_pb2 import GetTierDurationsRequest, GetTierDurationsResponse, GetTierPricingRequest, GetTierPricingResponse, GetEarlyCompletionPricingRequest, GetEarlyCompletionPricingResponse
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException
_TIMEOUT_SECONDS = 3
logger = logging.getLogger(__name__)

class PublicShipSkinSequencingRequestMessenger(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def initiate_sequencing_request(self, skin_design, component_quantity_by_id_and_license_type, component_category_by_id, nb_runs):
        info_log = None
        try:
            component_license_protos = []
            for key, quantity in component_quantity_by_id_and_license_type.iteritems():
                component_id, license_type = key
                component_license_proto = LicenseKind(component=ComponentLicense.build_component_id_proto_from_component_id(component_id=component_id, component_type=component_category_by_id[component_id]))
                if license_type == ComponentLicenseType.LIMITED:
                    component_license_proto.finite = quantity
                elif license_type == ComponentLicenseType.UNLIMITED:
                    component_license_proto.infinite = True
                component_license_protos.append(component_license_proto)

            request = InitiateRequest(name=skin_design.name.encode('utf-8'), line_name=skin_design.line_name.encode('utf-8'), layout=SlotLayout.build_proto_from_layout(skin_design.ship_type_id, skin_design.slot_layout), component_licenses=component_license_protos, licenses=nb_runs)
            info_log = 'SKIN SEQUENCING - InitiateRequest {nb_copies} x {name} for {type_id}. \nComponent licenses: {component_license_protos}'.format(nb_copies=nb_runs, name=skin_design.name.encode('utf-8'), type_id=skin_design.ship_type_id, component_license_protos=component_license_protos)
            response_primitive, response_payload = self._blocking_request(request, InitiateResponse)
            job = SequencingJob.build_from_proto(uuid.UUID(bytes=response_payload.id.uuid), response_payload.attributes)
            info_log += 'Response: job_id={job_id}, skin_hex={skin_hex}.'.format(job_id=job.job_id, skin_hex=job.skin_hex)
            return (job, None)
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            sequencing_job_error = STATUS_CODE_TO_INITIATE_SEQUENCING_ERROR.get(status_code, None)
            info_log += '\nERROR (status_code={status_code}, error={error}).'.format(status_code=status_code, error=sequencing_job_error)
            if sequencing_job_error:
                return (None, sequencing_job_error)
            else:
                logger.exception('Unexpected exception when requesting to initiate sequencing: %s', exc)
                return (None, GenericError.UNKNOWN)
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to initiate sequencing: %s', exc)
            return (None, GenericError.TIMEOUT)
        finally:
            if info_log:
                logger.info(info_log)

    def expedite_sequencing(self, job_id):
        request = CompleteEarlyRequest(job=JobIdentifier(uuid=job_id.bytes))
        info_log = 'SKIN SEQUENCING - Expedite sequencing for job {job_id}: '.format(job_id=job_id)
        try:
            self._blocking_request(request, CompleteEarlyResponse)
            info_log += 'SUCCESS'
            return
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            sequencing_job_error = STATUS_CODE_TO_EXPEDITE_SEQUENCING_ERROR.get(status_code, None)
            info_log += 'ERROR (status_code={status_code}, error={error})'.format(status_code=status_code, error=sequencing_job_error)
            if sequencing_job_error:
                return sequencing_job_error
            else:
                logger.exception('Unexpected exception when requesting to expedite sequencing, job %s: %s', job_id, exc)
                return GenericError.UNKNOWN
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to expedite sequencing, job: %s: %s', job_id, exc)
            return GenericError.TIMEOUT
        finally:
            logger.info(info_log)

    def get_all_active_sequencing_jobs_request(self):
        request = GetAllActiveRequest()
        info_log = 'SKIN SEQUENCING - Get all active jobs requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetAllActiveResponse)
            if response_payload is None:
                info_log += 'Response: no active jobs found'
                return {}
            jobs = response_payload.jobs
            info_log += 'Response: {amount} active jobs found'.format(amount=len(jobs) if jobs else 0)
            return {uuid.UUID(bytes=x.id.uuid):SequencingJob.build_from_proto(uuid.UUID(bytes=x.id.uuid), x.attributes) for x in jobs}
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get all active jobs: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get all active jobs: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def get_sequencing_job_request(self, job_id):
        request = GetRequest(job=JobIdentifier(uuid=job_id.bytes))
        info_log = 'SKIN SEQUENCING - Get job {job_id} requested. '.format(job_id=job_id)
        try:
            response_primitive, response_payload = self._blocking_request(request, GetResponse)
            if response_payload is None:
                info_log += 'Response: no job found'
                return
            job = SequencingJob.build_from_proto(job_id, response_payload.job)
            info_log += 'Response: job fetched (job_id={job_id}, skin_hex={skin_hex})'.format(job_id=job.job_id, skin_hex=job.skin_hex)
            return job
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get job %s: %s', job_id, exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get job %s: %s', job_id, exc)
            raise
        finally:
            logger.info(info_log)

    def get_tier_durations_request(self):
        request = GetTierDurationsRequest()
        info_log = 'SKIN SEQUENCING - Get tier durations requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetTierDurationsResponse)
            if response_payload is None:
                info_log += 'Response: empty tier durations'
                return {}
            seconds_by_tier_level = {}
            for duration in response_payload.durations:
                tier_level = duration.tier.level
                seconds = duration.duration.ToSeconds()
                seconds_by_tier_level[tier_level] = seconds

            info_log += 'Response: {durations} '.format(durations=seconds_by_tier_level)
            return seconds_by_tier_level
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting tier durations: %s.\nResponse primitive: %s.\nResponse payload: %s', exc, exc.response_primitive, exc.response_primitive)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting tier durations: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def get_tier_pricing_request(self):
        request = GetTierPricingRequest()
        info_log = 'SKIN SEQUENCING - Get tier pricing requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetTierPricingResponse)
            if response_payload is None:
                info_log += 'Response: empty tier pricing'
                return ({}, 0)
            discount_applied = response_payload.discount_percentage_applied
            plex_by_tier_level = {}
            for price in response_payload.prices:
                tier_level = price.tier.level
                plex = price.plex.total_in_cents / 100
                plex_by_tier_level[tier_level] = plex

            return (plex_by_tier_level, discount_applied)
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting tier pricing: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting tier pricing: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def get_early_completion_pricing_request(self):
        request = GetEarlyCompletionPricingRequest()
        info_log = 'SKIN SEQUENCING - Get early completion pricing requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetEarlyCompletionPricingResponse)
            if response_payload is None:
                info_log += 'Response: empty early completion pricing'
                return []
            time_limits_and_prices = []
            for price in response_payload.prices:
                remaining_greater = price.remaining_greater.ToSeconds()
                remaining_lesser_or_equal = price.remaining_lesser_or_equal.ToSeconds()
                plex = price.plex.total_in_cents / 100
                time_limits_and_prices.append((remaining_greater, remaining_lesser_or_equal, plex))

            return time_limits_and_prices
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting early completion pricing: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting early completion pricing: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def _blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, _TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code == 404:
            return (response_primitive, None)
        if response_primitive.status_code != 200:
            raise GenericException(request_primitive, response_primitive)
        return (response_primitive, payload)
