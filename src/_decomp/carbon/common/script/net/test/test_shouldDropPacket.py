#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\test\test_shouldDropPacket.py
from unittest import TestCase
import mock
from carbon.common.lib.const import ADDRESS_TYPE_CLIENT, ADDRESS_TYPE_BROADCAST, ADDRESS_TYPE_NODE
from carbon.common.script.net.packetthreshold import PacketThreshold

class Message(object):

    def __init__(self, destination = 'client', destinationIdType = ''):
        self.destination = mock.Mock(addressType={'client': ADDRESS_TYPE_CLIENT,
         'broadcast': ADDRESS_TYPE_BROADCAST,
         'server': ADDRESS_TYPE_NODE}[destination], idtype=destinationIdType)


class TestShouldDropPacket(TestCase):

    def test_cases(self):
        self.assertTrue(self.ShouldDropPacket('123', 'tcp:packet:machoNet', destination='client', source='server'))
        self.assertTrue(self.ShouldDropPacket('123', 'tcp:packet:client', destination='client', source='proxy'))
        self.assertTrue(self.ShouldDropPacket('123', 'tcp:packet:machoNet', destination='broadcast', source='server'))
        self.assertFalse(self.ShouldDropPacket('123', 'tcp:packet:machoNet', destination='broadcast', source='proxy'))
        self.assertFalse(self.ShouldDropPacket('123', 'tcp:packet:machoNet', destination='broadcast', source='server', idType='nodeID'))
        self.assertTrue(self.ShouldDropPacket('123', 'ip:packet:server', destination='server', source='client'))
        self.assertFalse(self.ShouldDropPacket('1', 'tcp:packet:machoNet', destination='client', source='server'))

    def ShouldDropPacket(self, payload, transportName, destination, source, idType = ''):
        dropSize = 2
        message = Message(destination=destination, destinationIdType=idType)
        return PacketThreshold(transportName, dropSize, source).ShouldDropPacket(payload, message)
