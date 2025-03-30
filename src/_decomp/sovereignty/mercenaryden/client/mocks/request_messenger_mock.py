#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\mocks\request_messenger_mock.py
import uuid
import datetime
from collections import namedtuple
from eveProto.generated.eve_public.sovereignty.mercenaryden.api.requests_pb2 import GetAsOwnerRequest
from eveProto.generated.eve_public.sovereignty.mercenaryden.mercenaryden_pb2 import Identifier as MercenaryDenIdentifier
from httplib import OK, NOT_FOUND
from logging import getLogger
from sovereignty.mercenaryden.client.mocks.data import create_mercenary_den_mock
from sovereignty.mercenaryden.client.data.activity import MercenaryDenActivity
from sovereignty.mercenaryden.common.errors import GenericError, UnknownMercenaryDen
logger = getLogger('mercenary_den')

class MockMercenaryDenRequestMessenger(object):

    def get_mercenary_den_request(self, item_id):
        response = OK
        request = GetAsOwnerRequest(id=MercenaryDenIdentifier(sequential=item_id))
        info_log = 'Request: Get Mercenary Den {item_id}: {request}\n'.format(item_id=item_id, request=request)
        try:
            if response == OK:
                info_log += 'Response (MOCKED): Get Mercenary Den {item_id}: ({status_code}) {response}'.format(item_id=item_id, status_code=OK, response=response)
                return create_mercenary_den_mock(item_id, session.charid, session.solarsystemid2, session.corpid)
            if response == NOT_FOUND:
                raise UnknownMercenaryDen('(MOCKED) Mercenary Den does not exist or caller is not owner and therefore has no visibility')
            else:
                raise GenericError('(MOCKED) Unspecified error when fetching data for Mercenary Den: {code}'.format(code=response))
        finally:
            logger.info(info_log)

    def get_all_activities_for_den_request(self, item_id):
        activities = [MercenaryDenActivity(activity_id=uuid.uuid4(), den_id=item_id, dungeon_id=12355, name_id=871696, description_id=871697, started=False, expiry=datetime.datetime.utcnow() + datetime.timedelta(minutes=60), solar_system_id=30000208, development_impact=10, anarchy_impact=-10, infomorph_bonus=100)]
        next_generation = datetime.datetime.utcnow() + datetime.timedelta(days=1, hours=1, minutes=15)
        return (activities, next_generation)

    def _get_all_activities_request(self):
        if not hasattr(self, '_activities'):
            self._activities = [MercenaryDenActivity(activity_id=uuid.uuid4(), den_id=1000000013115L, dungeon_id=12355, name_id=871696, description_id=871697, started=False, expiry=datetime.datetime.utcnow() + datetime.timedelta(minutes=60), solar_system_id=30000208, development_impact=10, anarchy_impact=-10, infomorph_bonus=100)]
        return self._activities

    def get_all_activities_request_without_retries(self):
        return self._get_all_activities_request()

    def get_all_activities_request_with_retries(self):
        return self._get_all_activities_request()

    def start_activity_request(self, activity_id):
        logger.info('(Mocked) start_activity_request')
        result = namedtuple('Result', ['is_started'])
        return result(is_started=True)

    def get_activity_capacity_request(self):
        pass

    def get_all_owned_mercenary_dens_request(self):
        return [1000000270300L]

    def get_maximum_dens_info_dens_request(self):
        current_maximum = 5
        absolute_maximum = 5
        return (current_maximum, absolute_maximum)
