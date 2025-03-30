#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\entitlements\corporation\structure\requestMessenger.py
import logging
import uuid
import blue
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from cosmetics.client.structures.license import create_structure_paintwork_license_from_proto_license
from cosmetics.common.structures.priceCatalogue import PriceCatalogue
from google.protobuf.duration_pb2 import Duration
import eveProto.generated.eve_public.cosmetic.structure.paintwork.license.api.api_pb2 as api
import eveProto.generated.eve_public.cosmetic.structure.paintwork.api.admin.admin_pb2 as admin_api
from eveProto.generated.eve_public.cosmetic.structure.paintwork.license.license_pb2 import Identifier as LicenseIdentifier
from eveProto.generated.eve_public.structure.structure_pb2 import Identifier as StructureIdentifier
from eveProto.generated.eve_public.corporation.corporation_pb2 import Identifier as CorporationIdentifier
from eveProto.generated.eve_public.corporation.loyalty_pb2 import Points
from cosmetics.common.structures.fitting import StructurePaintwork
from cosmetics.common.structures.exceptions import InsufficientBalanceError, InsufficientRolesError, InvalidDataError, LicenseNotFoundException, ForbiddenRequestError
from cosmetics.client.structures.fitting import create_proto_slot_config_from_structure_paintwork
import cosmetics.client.messengers.entitlements.corporation.structure.qaconst as qa
from appConst import corpHeraldry
from publicGateway.grpc.exceptions import GenericException
TIMEOUT_SECONDS = 10
logger = logging.getLogger(__name__)

class PublicRequestsMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def issue_request(self, structure_paintwork, duration, structures):
        if session and session.role & ROLE_PROGRAMMER:
            if qa.FORCE_STRUCTURE_ISSUE_LICENSE_DELAY > 0:
                blue.synchro.Sleep(qa.FORCE_STRUCTURE_ISSUE_LICENSE_DELAY * 1000)
            if qa.FORCE_STRUCTURE_ISSUE_LICENSE_ERRORS:
                raise Exception
        request = api.IssueRequest(paintwork=create_proto_slot_config_from_structure_paintwork(structure_paintwork), duration=Duration(seconds=duration), structures=[ StructureIdentifier(sequential=s) for s in structures ])
        response_primitive, response_payload = self.blocking_request(request, api.IssueResponse)
        response_licenses = []
        for proto_license in response_payload.licenses:
            response_licenses.append(create_structure_paintwork_license_from_proto_license(uuid.UUID(bytes=proto_license.id.uuid), proto_license.attributes))

        return response_licenses

    def revoke_request(self, license_id):
        if session and session.role & ROLE_PROGRAMMER:
            if qa.FORCE_STRUCTURE_REVOKE_LICENSE_DELAY > 0:
                blue.synchro.Sleep(qa.FORCE_STRUCTURE_REVOKE_LICENSE_DELAY * 1000)
            if qa.FORCE_STRUCTURE_REVOKE_LICENSE_ERRORS:
                raise Exception
        request = api.RevokeRequest(license=LicenseIdentifier(uuid=license_id.get_bytes()))
        self.blocking_request(request, api.RevokeResponse)

    def get_catalogue_request(self):
        if session and session.role & ROLE_PROGRAMMER:
            if qa.FORCE_STRUCTURE_GET_LICENSE_CATALOGUE_DELAY > 0:
                blue.synchro.Sleep(qa.FORCE_STRUCTURE_GET_LICENSE_CATALOGUE_DELAY * 1000)
            if qa.FORCE_STRUCTURE_GET_LICENSE_CATALOGUE_ERRORS:
                raise Exception
        request = api.GetCatalogueRequest()
        response_primitive, response_payload = self.blocking_request(request, api.GetCatalogueResponse)
        price_catalogue = PriceCatalogue()
        for pricing_info in response_payload.items:
            price_catalogue.define_price(pricing_info.structure_type.sequential, pricing_info.duration.seconds, pricing_info.price.amount)

        return price_catalogue

    def get_request(self, structure_id, license_id):
        if session and session.role & ROLE_PROGRAMMER:
            if qa.FORCE_STRUCTURE_GET_LICENSE_DELAY > 0:
                blue.synchro.Sleep(qa.FORCE_STRUCTURE_GET_LICENSE_DELAY * 1000)
            if qa.FORCE_STRUCTURE_GET_LICENSE_RANDOM_ERRORS:
                import random
                if random.choice([False, True]):
                    raise Exception
            if qa.FORCE_STRUCTURE_GET_LICENSE_ERRORS:
                raise Exception
        request = api.GetRequest(id=LicenseIdentifier(uuid=license_id.get_bytes()))
        response_primitive, response_payload = self.blocking_request(request, api.GetResponse)
        response_license = create_structure_paintwork_license_from_proto_license(license_id, response_payload.attributes)
        return response_license

    def get_for_corporation(self):
        if session and session.role & ROLE_PROGRAMMER:
            if qa.FORCE_STRUCTURE_GET_LICENSE_DELAY > 0:
                blue.synchro.Sleep(qa.FORCE_STRUCTURE_GET_LICENSE_DELAY * 1000)
            if qa.FORCE_STRUCTURE_GET_LICENSE_RANDOM_ERRORS:
                import random
                if random.choice([False, True]):
                    raise Exception
            if qa.FORCE_STRUCTURE_GET_LICENSE_ERRORS:
                raise Exception
        request = api.GetAllOwnedByCorporationRequest()
        response_primitive, response_payload = self.blocking_request(request, api.GetAllOwnedByCorporationResponse)
        response_licenses = {}
        for proto_license in response_payload.licenses:
            structure_id = proto_license.attributes.structure.sequential
            response_licenses[structure_id] = create_structure_paintwork_license_from_proto_license(uuid.UUID(bytes=proto_license.identifier.uuid), proto_license.attributes)

        return response_licenses

    def admin_issue_request(self, structure_paintwork, duration, structures, lp_cost = -1):
        use_catalogue = lp_cost == -1
        if session.role & ROLE_PROGRAMMER:
            if qa.FORCE_STRUCTURE_ISSUE_LICENSE_DELAY > 0:
                blue.synchro.Sleep(qa.FORCE_STRUCTURE_ISSUE_LICENSE_DELAY * 1000)
            if qa.FORCE_STRUCTURE_ISSUE_LICENSE_ERRORS:
                raise Exception
        if use_catalogue:
            request = admin_api.IssueRequest(paintwork=create_proto_slot_config_from_structure_paintwork(structure_paintwork), duration=Duration(seconds=duration), structures=[ StructureIdentifier(sequential=s) for s in structures ], use_catalogue=True)
        else:
            request = admin_api.IssueRequest(paintwork=create_proto_slot_config_from_structure_paintwork(structure_paintwork), duration=Duration(seconds=duration), structures=[ StructureIdentifier(sequential=s) for s in structures ], price=Points(amount=lp_cost, associated_corporation=CorporationIdentifier(sequential=corpHeraldry)))
        response_primitive, response_payload = self.blocking_request(request, admin_api.IssueResponse)
        response_licenses = []
        for proto_license in response_payload.licenses:
            response_licenses.append(create_structure_paintwork_license_from_proto_license(uuid.UUID(bytes=proto_license.id.uuid), proto_license.attributes))

        return response_licenses

    def blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code == 400:
            raise InvalidDataError
        if response_primitive.status_code == 401:
            raise InsufficientRolesError
        if response_primitive.status_code == 402:
            raise InsufficientBalanceError
        if response_primitive.status_code == 403:
            raise ForbiddenRequestError
        if response_primitive.status_code == 404:
            raise LicenseNotFoundException
        elif response_primitive.status_code != 200:
            raise GenericException(request_primitive, response_primitive)
        return (response_primitive, payload)
