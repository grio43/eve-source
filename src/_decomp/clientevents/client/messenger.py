#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\clientevents\client\messenger.py
import logging
import socket
import struct
from eveProto.generated.eve_public.app.eveonline.network.api.events_pb2 import ConnectionLost
logger = logging.getLogger('clientevents.messenger')

class ClientEventsMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def connection_lost(self, user_id, reason_str, country_code, asn, ip_address):
        event = ConnectionLost()
        if user_id:
            event.user.sequential = user_id
        if reason_str:
            event.reason = reason_str
        if country_code:
            event.country_code = country_code
        if asn:
            event.asn = asn
        if ip_address:
            event.ip_address.v4 = struct.unpack('!I', socket.inet_aton(ip_address))[0]
        self.public_gateway.publish_event_payload(event)
        logger.info('Client Events: ConnectionLost event emitted for user %s with reason %s. country_code = %s, asn = %s, ipv4 = %s' % (user_id,
         reason_str,
         country_code,
         asn,
         ip_address))
