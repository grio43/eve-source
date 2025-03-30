#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\grpc\connectionConfig.py
import os
import uthread2
import certifi
import monolithconfig

class ConnectionConfig(object):

    def __init__(self, logger, grpc_module, tier):
        self.logger = logger
        self.grpc_module = grpc_module
        self.connection = grpc_module.Connection()
        self.tier = tier

    def get_address(self):
        address = os.getenv('EVE_PUBLIC_GATEWAY_ADDRESS')
        if address:
            return (address, False)
        address = self.discover_address()
        return (address, True)

    def get_discovery_address(self):
        domain = 'evetech.net'
        if monolithconfig.get_value('optic', 'boot'):
            domain = 'evepc.163.com'
        return '_{}-public-gateway._tcp.{}'.format(self.tier, domain)

    def discover_address(self):
        domain = 'evetech.net'
        if monolithconfig.get_value('optic', 'boot'):
            domain = 'evepc.163.com'
        return '{}-public-gateway.{}'.format(self.tier, domain)

    def connect(self):
        if self.grpc_module is None:
            return
        address, secure = self.get_address()
        self.logger.info('connecting to (secure: %s): %s', secure, address)
        if secure:
            self.connection.connect(address, root_file=certifi.where())
        else:
            self.connection.connect(address)

    def disconnect(self):
        if self.grpc_module is None:
            return
        self.connection.disconnect()
