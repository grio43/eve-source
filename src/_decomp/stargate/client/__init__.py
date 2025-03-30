#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stargate\client\__init__.py
from stargate.client.mockGateLockMessenger import MockClientGateLockMessenger
from stargate.client.gateLockMessenger import ClientGateLockMessenger

def get_gate_lock_messenger(public_gateway, mock = False):
    if mock:
        return MockClientGateLockMessenger(public_gateway)
    return ClientGateLockMessenger(public_gateway)
