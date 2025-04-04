#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\SocketGPS.py
import errno
import iocp
import logging
import socket
import sys
import log
import blue
import stackless
import uthread
import bluepy
import locks
import localization
from carbon.common.script.net import GPS, machobase, machoRunTimeStats
from carbon.common.script.net.GPSExceptions import GPSAddressOccupied, GPSBadAddress, GPSException, GPSRemoteTransportClosed, GPSTransportClosed
from eveprefs import prefs
import monolithconfig
if sys.platform == 'darwin':
    ADDRESS_OCCUPIED_ERRORCODES = (errno.EADDRINUSE,)
    SOFT_CONNECTION_ERRORS = (errno.ECONNRESET, errno.ENOBUFS)
    NOBUF_ERRORS = (errno.ENOBUFS,)
    CLOSE_SOCKET_ERRNOS = (errno.ECONNABORTED, errno.ECONNREFUSED, errno.ECONNRESET)
elif sys.platform == 'win32':
    ADDRESS_OCCUPIED_ERRORCODES = (errno.EADDRINUSE, errno.WSAEADDRINUSE)
    SOFT_CONNECTION_ERRORS = (errno.ECONNRESET,
     errno.ENOBUFS,
     errno.WSAECONNRESET,
     errno.WSAENOBUFS)
    NOBUF_ERRORS = (errno.ENOBUFS, errno.WSAENOBUFS)
    CLOSE_SOCKET_ERRNOS = (errno.ECONNABORTED,
     errno.ECONNREFUSED,
     errno.ECONNRESET,
     errno.WSAECONNABORTED,
     errno.WSAECONNREFUSED,
     errno.WSAECONNRESET)
stdlog = logging.getLogger(__name__)
mylog = log.Channel('GPS', 'socket')
gai = socket.getaddrinfo

@locks.SingletonCall
def mygai(*args):
    return gai(*args)


socket.getaddrinfo = mygai
usingIOCP = iocp.UsingIOCP()
if not usingIOCP:
    import stacklessio
    usesmartwakeup = bool(prefs.GetValue('useSmartWakeup', 0))
    usependingcalls = bool(prefs.GetValue('usePendingCalls', 0))
    usethreaddispatch = bool(prefs.GetValue('useThreadDispatch', 0))
    stacklessio.ApplySettings({'useSmartWakeup': usesmartwakeup,
     'usePendingCalls': usependingcalls,
     'useThreadDispatch': usethreaddispatch})
blue.os.CarbonIoFastWakeup(prefs.GetValue('carbonIoFastWakeup', 0))
stacklessioVersion = prefs.GetValue('stacklessioVersion', 0)
stacklessioNobufProb = prefs.GetValue('stacklessioNobufProb', 0.0)
stacklessioUseNoblock = prefs.GetValue('stacklessioUseNoblock', 1)
stacklessioAllocChunkSize = prefs.GetValue('stacklessioAllocChunkSize', 1048576)
socket.apply_settings({'version': stacklessioVersion,
 'nobufProb': stacklessioNobufProb,
 'useNoblock': stacklessioUseNoblock,
 'allocChunkSize': stacklessioAllocChunkSize})
GPSSTATS_TIME_SAMPLING_PERIODS = [1,
 5,
 60,
 600]
GPSSTATS_PACKETSREAD_PERIODS = GPSSTATS_TIME_SAMPLING_PERIODS
GPSSTATS_BYTESREAD_PERIODS = GPSSTATS_TIME_SAMPLING_PERIODS
GPSSTATS_PACKETSWRITTEN_PERIODS = GPSSTATS_TIME_SAMPLING_PERIODS
GPSSTATS_BYTESWRITTEN_PERIODS = GPSSTATS_TIME_SAMPLING_PERIODS
GPSSTATS_COUNT_SAMPLING_PERIODS = [1,
 5,
 50,
 500]
GPSSTATS_BYTESREADPERPACKET_PERIODS = GPSSTATS_COUNT_SAMPLING_PERIODS
GPSSTATS_BYTESWRITTENPERPACKET_PERIODS = GPSSTATS_COUNT_SAMPLING_PERIODS

class SocketTransportFactory(GPS.GPSTransportFactory):
    __guid__ = 'gps.SocketTransportFactory'
    reuseAddress = False

    def __init__(self, *args, **kwds):
        super(SocketTransportFactory, self).__init__(*args, **kwds)
        self.MaxPacketSize = None
        self.MaxPacketSize = 10485760

    @staticmethod
    def Transport():
        return SocketTransport

    @staticmethod
    def Acceptor():
        return SocketTransportAcceptor

    def _PreSocketConnectOperations(self, socket):
        pass

    def Listen(self, port, address = ''):
        s = socket.socket()
        self._PreSocketConnectOperations(s)
        if self.reuseAddress:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            port = int(port)
        except Exception as e:
            raise GPSBadAddress(localization.GetByLabel('/Carbon/MachoNet/SpecifiedAddressBogus'), e)

        if port < 1 or port > 65535:
            raise GPSBadAddress(localization.GetByLabel('/Carbon/MachoNet/SpecifiedPortNotvalid'))
        try:
            s.bind((address, port))
            s.listen(socket.SOMAXCONN)
        except socket.error as e:
            if e[0] in ADDRESS_OCCUPIED_ERRORCODES:
                raise GPSAddressOccupied('Cannot listen', e)
            raise

        result = self.Acceptor()(self.useACL, s)
        result.MaxPacketSize = self.MaxPacketSize
        return result

    def Connect(self, address):
        if stackless.getcurrent().is_main:
            raise RuntimeError("Can't do a Connect() on the main thread")
        s = socket.socket()
        self._PreSocketConnectOperations(s)
        address = address.encode('ascii')
        try:
            host, port = address.split(':')
            port = int(port)
            if port < 1 or port > 65535:
                raise GPSBadAddress(localization.GetByLabel('/Carbon/MachoNet/SpecifiedPortNotvalid'))
        except ValueError as e:
            raise GPSBadAddress(localization.GetByLabel('/Carbon/MachoNet/SpecifiedPortNotValidNotInt'), e)
        except Exception as e:
            raise GPSBadAddress(localization.GetByLabel('/Carbon/MachoNet/SpecifiedAddressBogus'), e)

        try:
            s.connect((host, port))
        except socket.gaierror as e:
            raise GPSBadAddress(localization.GetByLabel('/Carbon/MachoNet/CouldNotConnectToAddress'), e)
        except socket.error as e:
            raise GPSTransportClosed(localization.GetByLabel('/Carbon/MachoNet/CouldNotConnectToAddress'), exception=e)

        if self.MaxPacketSize:
            s.setmaxpacketsize(self.MaxPacketSize)
        return self.Transport()(s)


class SocketTransportAcceptor(GPS.GPSTransportAcceptor):
    __guid__ = 'gps.SocketTransportAcceptor'

    def __init__(self, *args, **kwds):
        super(SocketTransportAcceptor, self).__init__(*args, **kwds)
        self.MaxPacketSize = None

    @staticmethod
    def Transport():
        return SocketTransport

    @property
    def address(self):
        return self._address

    def __repr__(self):
        if self.socket:
            return '<%s at addr %s:%s>' % ((self.__guid__,) + self.socket.getsockname())
        else:
            return '<%s (closed)>' % self.__guid__

    def __init__(self, useACL, sock):
        super(SocketTransportAcceptor, self).__init__(useACL)
        self.socket = sock
        self._address = '%s:%s' % (socket.gethostname(), sock.getsockname()[1])

    def Accept(self):
        if self.socket is None:
            raise GPSTransportClosed('Listen socket closed.')
        if stackless.getcurrent().is_main:
            raise RuntimeError("Can't do an Accept() on the main thread")
        while True:
            try:
                s, address = self.socket.accept()
                if self.MaxPacketSize:
                    s.setmaxpacketsize(self.MaxPacketSize)
                t = self.Transport()(s)
                acl = self.CheckACL('%s:%d' % address)
                if acl is not None:
                    t.Close(*acl)
                    continue
                return t
            except socket.error as e:
                if e[0] in SOFT_CONNECTION_ERRORS:
                    sys.exc_clear()
                else:
                    raise GPSException('accept failed: ', e)

    def close(self, reason = None):
        try:
            self.socket.close()
        except socket.error as e:
            sys.exc_clear()

        self.socket = None


class SocketTransport(GPS.GPSTransport):
    __guid__ = 'gps.SocketTransport'

    def __init__(self, socket):
        super(SocketTransport, self).__init__()
        self.address = '%s:%s' % socket.getpeername()
        self.localaddress = '%s:%s' % socket.getsockname()
        self.socket = socket
        self.closeReason = None
        self.socketStatsEnabled = prefs.GetValue('socketStatsEnabled', False)
        self.statsBytesReadPerPacket = machoRunTimeStats.EWMA.FromSampleCounts(GPSSTATS_BYTESREADPERPACKET_PERIODS)
        self.statsBytesWrittenPerPacket = machoRunTimeStats.EWMA.FromSampleCounts(GPSSTATS_BYTESWRITTENPERPACKET_PERIODS)
        self.statsBytesRead = machoRunTimeStats.EWMA.FromSampleCounts(GPSSTATS_BYTESREAD_PERIODS)
        self.statsBytesWritten = machoRunTimeStats.EWMA.FromSampleCounts(GPSSTATS_BYTESWRITTEN_PERIODS)
        self.statsPacketsRead = machoRunTimeStats.EWMA.FromSampleCounts(GPSSTATS_PACKETSREAD_PERIODS)
        self.statsPacketsWritten = machoRunTimeStats.EWMA.FromSampleCounts(GPSSTATS_PACKETSWRITTEN_PERIODS)
        self.lastSocketActivityTimestamp = blue.os.GetWallclockTime()

    def StatsRepr(self):
        if self.socketStatsEnabled:
            return '([bs][pkts][bpp] RD [%s][%s][%s] WR [%s][%s][%s])' % (self.statsBytesRead,
             self.statsPacketsRead,
             self.statsBytesReadPerPacket,
             self.statsBytesWritten,
             self.statsPacketsWritten,
             self.statsBytesWrittenPerPacket)
        else:
            return '[Socket Stats Disabled]'

    def __repr__(self):
        if self.socket:
            return '<%s at addr %s:%s %s:%s, %s>' % ((self.__guid__,) + self.socket.getsockname() + self.socket.getpeername() + (self.StatsRepr(),))
        else:
            return '<%s (closed)>' % self.__guid__

    def GetSocket(self):
        return self.socket.getSocket()

    def GetIdleTime(self):
        return blue.os.TimeDiffInMs(self.lastSocketActivityTimestamp, blue.os.GetWallclockTime()) / 1000

    def Write(self, packet):
        if stackless.getcurrent().is_main:
            raise RuntimeError("You can't Write to a socket in a synchronous manner without blocking, dude.")
        try:
            self.socket.send(packet)
            self.lastSocketActivityTimestamp = blue.os.GetWallclockTime()
        except socket.error as e:
            idleTime = self.GetIdleTime()
            log.LogWarn('Write: Socket closed, idle time is %d seconds' % idleTime)
            self.Close(localization.GetByLabel('/Carbon/MachoNet/ConnectionWasClosed'), exception=e)
            raise GPSTransportClosed(**self.closeReason)
        except Exception as e:
            self.Close(localization.GetByLabel('/Carbon/MachoNet/SocketWasClosed'), exception=e)
            log.LogTraceback()
            raise GPSTransportClosed(**self.closeReason)

        if self.socketStatsEnabled:
            self.statsBytesWrittenPerPacket.AddSample(len(packet))
            self.statsBytesWritten.Add(len(packet))
            self.statsPacketsWritten.Add()

    def Read(self, bufsize = 4096, flags = 0):
        if stackless.getcurrent().is_main:
            raise RuntimeError("You can't Read from a socket in a synchronous manner without blocking, dude.")
        try:
            r = self.socket.recv(bufsize, flags)
            self.lastSocketActivityTimestamp = blue.os.GetWallclockTime()
        except socket.error as e:
            idleTime = self.GetIdleTime()
            log.LogWarn('Read: Socket closed, idle time is %d seconds' % idleTime)
            if e[0] in (10053, 10054, 995):
                self.Close(localization.GetByLabel('/Carbon/MachoNet/SocketWasClosed'), exception=e)
            else:
                log.LogException()
                self.Close(localization.GetByLabel('/Carbon/MachoNet/SomethingHappenedSocketWasClosed'), exception=e)
            raise GPSTransportClosed(**self.closeReason)
        except Exception as e:
            self.Close(localization.GetByLabel('/Carbon/MachoNet/SomethingHappenedSocketWasClosed'), exception=e)
            raise

        if not r:
            self.Close(localization.GetByLabel('/Carbon/MachoNet/ConnectionWasClosed'))
            raise GPSTransportClosed(**self.closeReason)
        if self.socketStatsEnabled:
            self.statsBytesReadPerPacket.AddSample(len(r))
            self.statsBytesRead.Add(len(r))
            self.statsPacketsRead.Add()
        return r

    def Close(self, reason = None, reasonCode = None, reasonArgs = {}, exception = None, noSend = False):
        with bluepy.Timer('Socket::GPS::Close'):
            if exception and monolithconfig.on_client():
                stdlog.error('Socket closed with Exception', exc_info=1)
            if not self.closeReason and reason is not None:
                self.closeReason = {'reason': reason,
                 'reasonCode': reasonCode,
                 'reasonArgs': reasonArgs,
                 'exception': exception}
            s, self.socket = self.socket, None
            if s:
                self.Nerf()
                self._Close(s, noSend)

    def _Close(self, s, noSend):
        try:
            s.shutdown(socket.SHUT_WR)
            s.close()
        except socket.error:
            log.LogException()

    def IsClosed(self):
        return self.socket is None

    def Nerf(self):
        self.Read = self.Write = self.NerfFunc(self.closeReason)

    @staticmethod
    def NerfFunc(reason):

        def Helper(*args):
            raise GPSTransportClosed(reason)

        return Helper

    def SetKeepalive(self, timeout, interval = None):
        if interval is None:
            interval = timeout
        try:
            self.socket.ioctl(socket.SIO_KEEPALIVE_VALS, (timeout > 0, int(timeout * 1000), int(interval * 1000)))
        except AttributeError:
            mylog.Log("socket doesn't support ioctl() ", log.LGWARN)
        except socket.error:
            log.LogException('socket.ioctl')


class SocketPacketTransportFactory(SocketTransportFactory):
    __guid__ = 'gps.SocketPacketTransportFactory'

    @staticmethod
    def Transport():
        return SocketPacketTransport

    @staticmethod
    def Acceptor():
        return SocketPacketTransportAcceptor


class SocketPacketTransportAcceptor(SocketTransportAcceptor):
    __guid__ = 'gps.SocketPacketTransportAcceptor'

    @staticmethod
    def Transport():
        return SocketPacketTransport


class SocketPacketTransport(SocketTransport):
    __guid__ = 'gps.SocketPacketTransport'

    def __init__(self, sock):
        SocketTransport.__init__(self, sock)
        sock.setblockingsend(False)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.packetQueue = {}
        self.packetNumber = -1
        self.numReorderedPackets = 0

    def Write(self, packet, header = None):
        global usingIOCP
        try:
            if header and usingIOCP:
                self.socket.sendpacket(packet, header)
            else:
                self.socket.sendpacket(packet)
            self.lastSocketActivityTimestamp = blue.os.GetWallclockTime()
        except socket.error as e:
            idleTime = self.GetIdleTime()
            log.LogInfo('Socket closed, idle time is %d seconds' % idleTime)
            if e[0] in NOBUF_ERRORS:
                log.LogException()
            self.Close(localization.GetByLabel('/Carbon/MachoNet/ConnectionWasClosed'), exception=e)
            raise GPSTransportClosed(**self.closeReason)
        except Exception as e:
            self.Close(localization.GetByLabel('/Carbon/MachoNet/SocketWasClosed'), exception=e)
            raise

        if self.socketStatsEnabled:
            self.statsBytesWrittenPerPacket.AddSample(len(packet))
            self.statsBytesWritten.Add(len(packet))
            self.statsPacketsWritten.Add()

    def Read(self, *args, **keywords):
        with bluepy.Timer('Socket::GPS::Read'):
            if stackless.getcurrent().is_main:
                raise RuntimeError("You can't Read from a socket in a synchronous manner without blocking, dude.")
            try:
                while True:
                    if self.packetNumber in self.packetQueue:
                        r = self.packetQueue[self.packetNumber]
                        serial = self.packetNumber
                        del self.packetQueue[self.packetNumber]
                        log.LogInfo('[Packet Order] address:', self.address, 'removed packet', self.packetNumber, 'from reordering map (queue:', len(self.packetQueue), 'elems)')
                        break
                    else:
                        value = self.socket.recvpacketoob()
                        self.lastSocketActivityTimestamp = blue.os.GetWallclockTime()
                    if value is not None:
                        r, oob, serial = value
                        if r is None and oob is None and serial == 0:
                            break
                        if self.packetNumber == -1:
                            self.packetNumber = serial
                        if self.packetNumber < serial:
                            log.LogInfo('[Packet Order] address:', self.address, 'got', serial, 'expected', self.packetNumber, ', adding to map (queue:', len(self.packetQueue), ' elems)')
                            self.packetQueue[serial] = r
                            self.numReorderedPackets += 1
                            if len(self.packetQueue) > 1024:
                                raise RuntimeError('We seem to be indefinitely waiting for a packet.')
                            continue
                        elif self.packetNumber > serial:
                            log.LogError('[Packet Order] address:', self.address, 'got', serial, 'expected', self.packetNumber, ', dropping old packet (queue:', len(self.packetQueue), ' elems)')
                            continue
                        break
                    else:
                        r = None
                        break

                self.packetNumber += 1
            except socket.error as e:
                idleTime = self.GetIdleTime()
                log.LogInfo('Socket closed, idle time is %d seconds' % idleTime)
                if e[0] in NOBUF_ERRORS:
                    log.LogException()
                self.Close(localization.GetByLabel('/Carbon/MachoNet/SocketWasClosed'), exception=e)
                raise GPSTransportClosed(**self.closeReason)
            except Exception as e:
                if isinstance(e, RuntimeError) and e.args and 'too large a packet' in e.args[0]:
                    self.Close(localization.GetByLabel('/Carbon/MachoNet/ConnectionWasClosed'), exception=e)
                    raise GPSTransportClosed(**self.closeReason)
                self.Close(localization.GetByLabel('/Carbon/MachoNet/SomethingHappenedSocketWasClosed'), exception=e)
                log.LogTraceback()
                raise

            if r is None:
                self.Close(localization.GetByLabel('/Carbon/MachoNet/ConnectionWasClosed'))
                raise GPSTransportClosed(**self.closeReason)
            if self.socketStatsEnabled:
                self.statsBytesReadPerPacket.AddSample(len(r))
                self.statsBytesRead.Add(len(r))
                self.statsPacketsRead.Add()
            return r

    def _Close(self, s, noSend):
        flag = log.LGWARN
        exception = self.closeReason.get('exception', None)
        if self.closeReason and exception is None:
            flag = log.LGINFO
        mylog.Log('Closing connection to ' + self.address + ': ' + repr(self.closeReason), flag)
        if noSend or exception and exception[0] in CLOSE_SOCKET_ERRNOS:
            SocketTransport._Close(self, s, noSend)
        else:
            uthread.worker('Socket::DelayedClose', self._DelayedClose, s)

    def _DelayedClose(self, s):
        with bluepy.Timer('Socket::GPS::__DelayedClose'):
            try:
                s.setblockingsend(True)
                s.sendpacket(self.CreateClosedPacket(**self.closeReason))
            except socket.error as e:
                mylog.Log("Couldn't send close packet, rhe socket is probably already closed. " + str(e), log.LGINFO)
            except AttributeError:
                pass
            finally:
                SocketTransport._Close(self, s, False)


class SecureSocketPacketTransportFactory(SocketPacketTransportFactory):
    __guid__ = 'gps.SecureSocketPacketTransportFactory'

    @staticmethod
    def Transport():
        return SecureSocketPacketTransport

    @staticmethod
    def Acceptor():
        return SecureSocketPacketTransportAcceptor


class SecureSocketPacketTransportAcceptor(SocketPacketTransportAcceptor):
    __guid__ = 'gps.SecureSocketPacketTransportAcceptor'

    @staticmethod
    def Transport():
        return SecureSocketPacketTransport


class SecureSocketPacketTransport(SocketPacketTransport):
    __guid__ = 'gps.SecureSocketPacketTransport'
    __mandatory_fields__ = ['macho_version',
     'boot_version',
     'boot_build',
     'boot_codename',
     'boot_region',
     'user_name',
     'user_password',
     'user_password_hash',
     'user_languageid',
     'user_affiliateid']

    def __init__(self, *args, **keywords):
        SocketPacketTransport.__init__(self, *args, **keywords)

    UnEncryptedRead = SocketPacketTransport.Read
    UnEncryptedWrite = SocketPacketTransport.Write
    Read = SocketPacketTransport.EncryptedRead
    Write = SocketPacketTransport.EncryptedWrite


class SSLSocketTransportFactory(SocketTransportFactory):
    __guid__ = 'gps.SSLSocketTransportFactory'

    def _PreSocketConnectOperations(self, socket):
        socket._sock.enableSSL()


class SSLSocketPacketTransportFactory(SocketPacketTransportFactory):
    __guid__ = 'gps.SSLSocketPacketTransportFactory'

    def _PreSocketConnectOperations(self, socket):
        socket._sock.enableSSL()

    @staticmethod
    def Transport():
        return SSLSocketPacketTransport

    @staticmethod
    def Acceptor():
        return SSLSocketPacketTransportAcceptor


class SSLSocketPacketTransportAcceptor(SocketPacketTransportAcceptor):
    __guid__ = 'gps.SSLSocketPacketTransportAcceptor'

    @staticmethod
    def Transport():
        return SSLSocketPacketTransport


class SSLSocketPacketTransport(SocketPacketTransport):
    __guid__ = 'gps.SSLSocketPacketTransport'
    EncryptedRead = SocketPacketTransport.Read
    EncryptedWrite = SocketPacketTransport.Write
    UnEncryptedRead = SocketPacketTransport.Read
    UnEncryptedWrite = SocketPacketTransport.Write

    def CreateClosedPacket(self, reason, reasonCode = None, reasonArgs = {}, exception = None):
        msg = 'Creating Closed Packet: ' + reason
        if exception:
            msg += ' exception:' + repr(exception)
        log.general.Log(msg, log.LGINFO)
        etype = GPSRemoteTransportClosed
        etype = GPSTransportClosed
        exception = None
        packet = machobase.Dumps(etype(reason, reasonCode, reasonArgs, exception=exception))
        return packet
