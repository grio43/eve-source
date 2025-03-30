#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipSkinDataRequestMessenger.py
import logging
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException
from cosmetics.client.ships.skins.live_data.skin_design import SkinDesign
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.thirdparty_pb2 import Identifier as SkinIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.api.requests_pb2 import GetRequest, GetResponse
_TIMEOUT_SECONDS = 10
logger = logging.getLogger(__name__)

class PublicShipSkinDataRequestMessenger(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get_skin_data_request(self, design_hex):
        request = GetRequest(skin=SkinIdentifier(hex=design_hex))
        info_log = 'SKIN DATA - Get design data {design_hex} requested. '.format(design_hex=design_hex)
        try:
            response_primitive, response_payload = self._blocking_request(request, GetResponse)
            if response_payload is None:
                info_log += 'Response: no design found'
                return
            design = SkinDesign.build_from_proto(response_payload.skin)
            info_log += 'Response: design data fetched (design={design})'.format(design=str(design))
            return design
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get design data %s: %s', design_hex, exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get design data %s: %s', design_hex, exc)
            raise
        finally:
            logger.info(info_log)

    def _blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, _TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code != 200:
            raise GenericException(request_primitive, response_primitive)
        return (response_primitive, payload)
