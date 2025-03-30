#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\packetthreshold.py
from carbon.common.lib import const

class PacketThreshold(object):

    def __init__(self, transportName, packetThreshold, machoMode):
        self._transportName = transportName
        self._packetThreshold = packetThreshold
        self._machoMode = machoMode

    def ShouldDropPacket(self, payload, message):
        if self._IsPacketTooBig(payload) and (self._IsSendingFromTheClient() or self._IsSendingToTheClient(message)):
            return True
        return False

    def _IsPacketTooBig(self, payload):
        return len(payload) > self._packetThreshold

    def _IsSendingToTheClient(self, message):
        if self._IsProxySendingToClient():
            return True
        if self._IsOnServer():
            if self._IsDestinationClient(message):
                return True
            if self._IsClientBroadcast(message):
                return True
        return False

    def _IsClientBroadcast(self, message):
        return message.destination.addressType == const.ADDRESS_TYPE_BROADCAST and message.destination.idtype not in ('nodeID', '+nodeID')

    def _IsOnServer(self):
        return self._machoMode == 'server'

    def _IsDestinationClient(self, message):
        return message.destination.addressType == const.ADDRESS_TYPE_CLIENT

    def _IsProxySendingToClient(self):
        return self._transportName == 'tcp:packet:client'

    def _IsSendingFromTheClient(self):
        return self._transportName == 'ip:packet:server'
