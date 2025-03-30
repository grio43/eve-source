#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stargate\client\mockGateLockMessenger.py
from datetime import datetime, timedelta
from eve.common.lib.appConst import solarSystemZarzakh
from stargate.common.lock_details import LockDetails
from carbon.common.lib.const import SEC
GATE_ZARZAKH_TO_ALSAVOINON = 50016567
EXPIRY_DELAY_SECS = 30

class MockClientGateLockMessenger(object):

    def __init__(self, public_gateway):
        self._public_gateway = public_gateway

    def subscribe_to_restricted_systems_notice(self, callback):
        callback([solarSystemZarzakh])

    def subscribe_to_activated_lock_notice(self, callback):
        pass

    def subscribe_to_deactivated_lock_notice(self, callback):
        pass

    def get_restricted_systems_request(self):
        return [solarSystemZarzakh]

    def get_request(self):
        return LockDetails(solarSystemZarzakh, GATE_ZARZAKH_TO_ALSAVOINON, datetime.now() + timedelta(seconds=EXPIRY_DELAY_SECS))
