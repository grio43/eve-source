#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmpp\xmppConnection.py
from weakref import WeakSet
import blue
import logging
import socket
from eveprefs import prefs
from stackless_tracing.attributes import SERVICE_NAME, SERVICE_NAME_PREFIX
from xml.sax import SAXParseException
from xml.sax.saxutils import escape, quoteattr
from stackless_tracing.attributes import HOST_NAME
import uthread2
import ssl
import certifi
import monolithmetrics
import monolithhoneycomb_events as mhe
from monolithhoneycomb_events.events import CHAT_CONNECTION_CREATED, CHAT_CONNECTION_DELETED, CHAT_CONNECTION_CONNECTED, CHAT_CONNECTION_DISCONNECTED
from xmpp import XmppHandler
logger = logging.getLogger(__name__)
ca_certs_file = certifi.where()

def channel_timeout_helper(waitingChannel, timeInSecs, msg):
    uthread2.sleep(timeInSecs)
    if waitingChannel.balance < 0:
        logger.warning(msg)
        while waitingChannel.balance < 0:
            waitingChannel.send(None)


def channel_timeout(channel, timeoutInSecs, msg):
    uthread2.start_tasklet(channel_timeout_helper, channel, timeoutInSecs, msg)


CONNECTION_OBJECT_CREATED = 'xmpp.connection_object.created'
CONNECTION_OBJECT_DESTROYED = 'xmpp.connection_object.destroyed'
CONNECTION_ATTEMPTED = 'xmpp.connection.attempted'
CONNECTION_LOGIN_FAILED = 'xmpp.connection.login_failed'
CONNECTION_FAILED = 'xmpp.connection.failed'
CONNECTION_SUCCEEDED = 'xmpp.connection.succeeded'
CONNECTION_DISCONNECTED = 'xmpp.connection.disconnected'
CONNECTION_RECONNECTED = 'xmpp.connection.reconnected'

class XmppConnection(object):

    def __init__(self, hostname = '', ejabberd_address = 'localhost'):
        self.hostname = hostname
        self.ejabberd_address = ejabberd_address
        monolithmetrics.increment(CONNECTION_OBJECT_CREATED, value=1, tags=self._get_tags())
        self.port = 5222
        self.username = None
        self.xmppHandler = None
        self.socket = None
        self.connection_id = 'default'
        self.verbose = False
        self.disconnectRequested = False
        self.hasConnectedOnce = False
        self.myTasklets = WeakSet()
        self.receive_t = None
        self._SetupStatsGathering()
        self.send_honey_event(CHAT_CONNECTION_CREATED)

    def __del__(self):
        monolithmetrics.increment(CONNECTION_OBJECT_DESTROYED, value=1, tags=self._get_tags())
        self.send_honey_event(CHAT_CONNECTION_DELETED)

    def close_socket(self):
        if not self.socket:
            return
        self.socket.close()
        self.socket = None
        monolithmetrics.increment('xmpp.sockets.closed')

    def _SetupStatsGathering(self):
        self.lastSocketActivityTime = blue.os.GetWallclockTime()
        self.bytesReceived = 0
        self.bytesReceivedTotal = 0
        self.bytesReceivedPerSec = 0
        self.bytesReceivedPerSecAvg = 0
        self.bytesSent = 0
        self.bytesSentTotal = 0
        self.bytesSentPerSec = 0
        self.bytesSentPerSecAvg = 0
        self.bytesReceivedStat = blue.statistics.Find('xmpp/bytesReceived')
        if not self.bytesReceivedStat:
            self.bytesReceivedStat = blue.CcpStatisticsEntry()
            self.bytesReceivedStat.name = 'xmpp/bytesReceived'
            self.bytesReceivedStat.type = 1
            self.bytesReceivedStat.resetPerFrame = True
            self.bytesReceivedStat.description = 'Number of bytes received from Xmpp chat'
            blue.statistics.Register(self.bytesReceivedStat)
        self.bytesSentStat = blue.statistics.Find('xmpp/bytesSent')
        if not self.bytesSentStat:
            self.bytesSentStat = blue.CcpStatisticsEntry()
            self.bytesSentStat.name = 'xmpp/bytesSent'
            self.bytesSentStat.type = 1
            self.bytesSentStat.resetPerFrame = True
            self.bytesSentStat.description = 'Number of bytes sent to Xmpp chat'
            blue.statistics.Register(self.bytesSentStat)
        self.bytesReceivedPerSecStat = blue.statistics.Find('xmpp/bytesReceivedPerSec')
        if not self.bytesReceivedPerSecStat:
            self.bytesReceivedPerSecStat = blue.CcpStatisticsEntry()
            self.bytesReceivedPerSecStat.name = 'xmpp/bytesReceivedPerSec'
            self.bytesReceivedPerSecStat.type = 1
            self.bytesReceivedPerSecStat.resetPerFrame = False
            self.bytesReceivedPerSecStat.description = 'Number of bytes received per second from Xmpp chat'
            blue.statistics.Register(self.bytesReceivedStat)
        self.bytesSentPerSecStat = blue.statistics.Find('xmpp/bytesSentPerSec')
        if not self.bytesSentPerSecStat:
            self.bytesSentPerSecStat = blue.CcpStatisticsEntry()
            self.bytesSentPerSecStat.name = 'xmpp/bytesSentPerSec'
            self.bytesSentPerSecStat.type = 1
            self.bytesSentPerSecStat.resetPerFrame = False
            self.bytesSentPerSecStat.description = 'Number of bytes sent per second to Xmpp chat'
            blue.statistics.Register(self.bytesSentPerSecStat)
        self.bytesReceivedPerSecAvgStat = blue.statistics.Find('xmpp/bytesReceivedPerSecAvg')
        if not self.bytesReceivedPerSecAvgStat:
            self.bytesReceivedPerSecAvgStat = blue.CcpStatisticsEntry()
            self.bytesReceivedPerSecAvgStat.name = 'xmpp/bytesReceivedAvgPerSec'
            self.bytesReceivedPerSecAvgStat.type = 1
            self.bytesReceivedPerSecAvgStat.resetPerFrame = False
            self.bytesReceivedPerSecAvgStat.description = 'Number of bytes received per second from Xmpp chat'
            blue.statistics.Register(self.bytesReceivedStat)
        self.bytesSentPerSecAvgStat = blue.statistics.Find('xmpp/bytesSentPerSecAvg')
        if not self.bytesSentPerSecAvgStat:
            self.bytesSentPerSecAvgStat = blue.CcpStatisticsEntry()
            self.bytesSentPerSecAvgStat.name = 'xmpp/bytesSentPerSecAvg'
            self.bytesSentPerSecAvgStat.type = 1
            self.bytesSentPerSecAvgStat.resetPerFrame = False
            self.bytesSentPerSecAvgStat.description = 'Number of bytes sent per second to Xmpp chat'
            blue.statistics.Register(self.bytesSentPerSecAvgStat)
        self.requestsStat = blue.statistics.Find('xmpp/requests')
        if not self.requestsStat:
            self.requestsStat = blue.CcpStatisticsEntry()
            self.requestsStat.name = 'xmpp/requests'
            self.requestsStat.type = 1
            self.requestsStat.resetPerFrame = False
            self.requestsStat.description = 'Number of requests to Xmpp chat'
            blue.statistics.Register(self.requestsStat)
        uthread2.start_tasklet(self._GatherStats)

    def _GatherStats(self):
        bytesReceivedSamples = []
        bytesSentSamples = []
        NUM_SAMPLES_FOR_AVERAGE = 10
        while True:
            uthread2.sleep(1)
            bytesReceivedSamples.append(self.bytesReceived)
            bytesReceivedSamples = bytesReceivedSamples[-NUM_SAMPLES_FOR_AVERAGE:]
            self.bytesReceivedTotal += self.bytesReceived
            self.bytesReceivedPerSec = self.bytesReceived
            self.bytesReceived = 0
            self.bytesReceivedPerSecAvg = sum(bytesReceivedSamples) / len(bytesReceivedSamples)
            self.bytesReceivedPerSecStat.Set(self.bytesReceivedPerSec)
            self.bytesReceivedPerSecAvgStat.Set(self.bytesReceivedPerSecAvg)
            bytesSentSamples.append(self.bytesSent)
            bytesSentSamples = bytesSentSamples[-NUM_SAMPLES_FOR_AVERAGE:]
            self.bytesSentTotal += self.bytesSent
            self.bytesSentPerSec = self.bytesSent
            self.bytesSent = 0
            self.bytesSentPerSecAvg = sum(bytesSentSamples) / len(bytesSentSamples)
            self.bytesSentPerSecStat.Set(self.bytesSentPerSec)
            self.bytesSentPerSecAvgStat.Set(self.bytesSentPerSecAvg)

    def Connect(self, username, connection_id = None):
        self.disconnectRequested = False
        self.username = username
        if connection_id:
            self.connection_id = connection_id
        self._connectToXmppServer()
        self.send_honey_event(CHAT_CONNECTION_CONNECTED, {'connection_id': self.connection_id})

    def Disconnect(self):
        is_connected = self.IsConnected()
        if is_connected:
            self.xmppHandler.send('</stream:stream>')
        self.close_socket()
        self.disconnectRequested = True
        if self.receive_t:
            self.receive_t.kill()
            self.receive_t = None
        tasklets = self.myTasklets.copy()
        self.myTasklets.clear()
        for tasklet in tasklets:
            tasklet.kill()

        self.xmppHandler = None
        self.send_honey_event(CHAT_CONNECTION_DISCONNECTED, {'was_connected': is_connected})

    def IsConnected(self):
        if self.xmppHandler and self.xmppHandler.state == 'ready':
            return True
        return False

    def IssueRequest(self, request, request_type, to = None, method_tag = 'unknown'):
        self.requestsStat.Inc()
        if not self.IsConnected():
            logger.warning("CAN'T HANDLE REQUEST while NOT CONNECTED: iq %s: %s, %s", request_type, request, to)
            return
        TIMEOUT_DELAY_SECS = 30
        startTime = blue.os.GetWallclockTime()
        import stackless
        callback_channel = stackless.channel()

        def callback(response):
            if callback_channel.balance < 0:
                callback_channel.send(response)
            else:
                logger.warning('NO LISTENERS for callback channel!')

        request_id = self.xmppHandler.issue_request(request, request_type, callback, to=to)
        channel_timeout(callback_channel, TIMEOUT_DELAY_SECS, msg='TIMED-OUT awaiting response for request: \n%s' % request)
        result = callback_channel.receive()
        endTime = blue.os.GetWallclockTime()
        duration_ms = blue.os.TimeDiffInMs(startTime, endTime)
        monolithmetrics.histogram('xmpp.issue_request.duration', value=duration_ms, tags=['method:' + method_tag], buckets=(100, 500, 1000))
        if result is None and self.xmppHandler is not None:
            self.xmppHandler.notify_of_timeout(request_id, duration_ms, request_type, request, to)
        if duration_ms > 3000:
            logger.warning('SLOW RESPONSE time of %d ms, type:%s, request:%s, to:%s, result:%s', duration_ms, request_type, request, to, result)
        return result

    def Message(self, receiver, text):
        return self.xmppHandler.message(receiver, text)

    def GroupChat(self, receiver, text):
        return self.xmppHandler.groupchat(receiver, text)

    def SendXmppSubject(self, receiver, text):
        self.xmppHandler.send_xmpp_subject(receiver, text)

    def JoinRoom(self, room, password = '', historySeconds = 0):
        return self.xmppHandler.join_room(room, password=password, historySeconds=historySeconds)

    def LeaveRoom(self, room):
        return self.xmppHandler.leave_room(room)

    def SetRole(self, room, user, role, reason):
        template = "<query xmlns='http://jabber.org/protocol/muc#admin'><item nick='{0}' role='{1}'>{2}</item></query>"
        if reason is not None:
            reason_element = '<reason>{0}</reason>'.format(self.xmppHandler.sanitize_text(reason))
        else:
            reason_element = ''
        query = template.format(user, role, reason_element)
        response = self.IssueRequest(query, 'set', to=room, method_tag='set_role')
        if not response.attributes.getValue('type') == 'result':
            logger.warning('set_role: Incorrect response')

    def RegisterTemporaryRestriction(self, category, room, user, durationInSecs):
        template = "<query xmlns='urn:xmpp:expiring_record' jid='{0}' room='{1}' duration='{2}' action='set' category='{3}'/>"
        query = template.format(user, room, durationInSecs, category)
        self.IssueRequest(query, 'set', to=self.hostname, method_tag='register_temporary_restriction')

    def UnregisterTemporaryRestriction(self, category, room, user):
        template = "<query xmlns='urn:xmpp:expiring_record' jid='{0}' room='{1}' action='delete' category='{2}'/>"
        query = template.format(user, room, category)
        self.IssueRequest(query, 'set', to=self.hostname, method_tag='unregister_temporary_restriction')

    def SetEveUserData(self, user, data):
        attrs = ''
        for k, v in data.iteritems():
            try:
                attribute = quoteattr(escape(v).encode('utf-8'))
            except Exception:
                attribute = "'{0}'".format(v)

            attrs += '{0}={1} '.format(k, attribute)

        template = "<query xmlns='urn:xmpp:eve_user_data' jid='{0}'><eve_user_data {1}/></query>"
        query = template.format(user, attrs)
        self.IssueRequest(query, 'set', to=self.hostname, method_tag='set_eve_user_data')

    def GetEveUserData(self, user):
        template = "<query xmlns='urn:xmpp:eve_user_data' jid='{0}'/>"
        query = template.format(user)
        result = self.IssueRequest(query, 'get', to=self.hostname, method_tag='get_eve_user_data')
        logger.debug(result)
        return result

    def Invite(self, user, roomName, reason):
        template = "<message from='{sender}' to='{room}'><x xmlns='http://jabber.org/protocol/muc#user'><invite to='{to}'><reason>{reason}</reason></invite></x></message>"
        package = template.format(sender=self.username, room=roomName, reason=reason, to=user)
        self.Send(package)

    def RejectInvite(self, user, roomName, reason):
        template = "<message from='{sender}' to='{room}'><x xmlns='http://jabber.org/protocol/muc#user'><decline to='{to}'><reason>{reason}</reason></decline></x></message>"
        package = template.format(sender=self.username, room=roomName, reason=reason, to=user)
        self.Send(package)

    def Send(self, package):
        return self.xmppHandler.send(package)

    def GetFullUsername(self, user):
        return '{0}@{1}'.format(user, self.hostname)

    def _receive_t(self):
        while not self.disconnectRequested and self.socket:
            wasConnected = self.IsConnected()
            try:
                startTime = blue.os.GetWallclockTime()
                response = self.socket.recv(4096)
                endTime = blue.os.GetWallclockTime()
                self.lastSocketActivityTime = endTime
                duration = blue.os.TimeDiffInMs(startTime, endTime)
                monolithmetrics.histogram('xmpp.bytes.rx.duration', value=duration, buckets=(100, 500, 1000))
            except socket.error:
                idleTime = self.GetIdleTimeInSeconds()
                logger.warning('Socket error in receive tasklet after %ds idle time', idleTime)
                response = ''

            bytesReceived = len(response)
            if bytesReceived == 0:
                self.close_socket()
                self.xmppHandler = None
                if self.disconnectRequested:
                    monolithmetrics.increment(CONNECTION_DISCONNECTED, value=1, tags=self._get_tags())
                else:
                    uthread2.start_tasklet(self._handleXmppConnectionLost, wasConnected)
                break
            monolithmetrics.increment('xmpp.bytes.rx', value=bytesReceived)
            self.bytesReceivedStat.Add(bytesReceived)
            self.bytesReceived += bytesReceived
            try:
                self.xmppHandler.feed_parser(response)
                while self.xmppHandler and not self.xmppHandler.is_queue_empty():
                    element = self.xmppHandler.pop_queue()
                    if self.disconnectRequested and self.xmppHandler:
                        self.xmppHandler.flush_queue()
                    elif self.IsConnected():
                        self.myTasklets.add(uthread2.start_tasklet(self.xmppHandler.process_single_queue_item, element))
                        monolithmetrics.gauge('xmpp.connection.tasklets', value=len(self.myTasklets))
                    else:
                        self.xmppHandler.process_single_queue_item(element)

            except SAXParseException:
                logger.exception('Error parsing XMPP stream')
                self.close_socket()
                self.xmppHandler = None
                uthread2.start_tasklet(self._handleXmppConnectionLost, wasConnected)
                break
            except Exception:
                logger.exception('Exception in receive tasklet')

        if self.disconnectRequested:
            self.close_socket()
            self.disconnectRequested = False

    def GetIdleTimeInSeconds(self):
        idleTime = blue.os.TimeDiffInMs(self.lastSocketActivityTime, blue.os.GetWallclockTime()) / 1000
        return idleTime

    def _send(self, data):
        if self.verbose:
            logger.info('Send: %s', data)
        try:
            startTime = blue.os.GetWallclockTime()
            self.socket.sendall(data)
            endTime = blue.os.GetWallclockTime()
            duration = blue.os.TimeDiffInMs(startTime, endTime)
            bytesSent = len(data)
            if duration > 300:
                logger.warning('Slow: Sending %d bytes took %d ms', bytesSent, duration)
            monolithmetrics.increment('xmpp.bytes.tx', value=bytesSent)
            monolithmetrics.histogram('xmpp.bytes.tx.duration', value=duration, buckets=(100, 500, 1000))
            self.bytesSentStat.Add(bytesSent)
            self.bytesSent += bytesSent
            self.lastSocketActivityTime = startTime
        except socket.error:
            idleTime = self.GetIdleTimeInSeconds()
            logger.warning('Socket error when sending after %ds idle time', idleTime)
            logger.exception('Socket error in send')

    def _connectToXmppServer(self):
        self.xmppHandler = XmppHandler(self, self.connection_id)
        self.xmppHandler.handle_message = self.handle_message
        self.xmppHandler.handle_presence = self.handle_presence
        self.xmppHandler.handle_logged_in = self.handle_logged_in
        self.xmppHandler.handle_login_failed = self._handleXmppLoginFailed
        self.xmppHandler.handle_closed = self._handleXmppConnectionLost
        self.xmppHandler.handle_stream_error = self.handle_stream_error
        self.xmppHandler.send = self._send
        self.xmppHandler.verbose = self.verbose
        s = socket.socket()
        monolithmetrics.increment('xmpp.sockets.opened')
        try:
            monolithmetrics.increment(CONNECTION_ATTEMPTED, value=1, tags=self._get_tags())
            s.connect((self.ejabberd_address, self.port))
            if not prefs.GetValue('chatserver_disable_tls', False):
                s = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED, ca_certs=ca_certs_file)
            self.socket = s
            monolithmetrics.increment(CONNECTION_SUCCEEDED, value=1, tags=self._get_tags())
        except Exception as e:
            monolithmetrics.increment(CONNECTION_FAILED, value=1, tags=self._get_tags())
            raise e

        self.receive_t = uthread2.start_tasklet(self._receive_t)
        self.xmppHandler.connect(self.hostname, self.username, self.get_password())

    def _reconnectToXmppServer(self):
        isFirst = True
        while True:
            try:
                self._connectToXmppServer()
                monolithmetrics.increment(CONNECTION_RECONNECTED, value=1, tags=self._get_tags())
                break
            except socket.error:
                if isFirst:
                    logger.exception('Socket error when reconnecting to chat server')
                    isFirst = False
                else:
                    logger.warning('Error reconnecting to chat server')
            except ssl.SSLError:
                if isFirst:
                    logger.exception('TLS error when reconnecting to chat server')
                    isFirst = False
                else:
                    logger.warning('Error reconnecting to chat server')

            uthread2.sleep(5)

    def _handleXmppConnectionLost(self, wasConnected):
        self.xmppHandler = None
        if wasConnected:
            monolithmetrics.increment(CONNECTION_DISCONNECTED, value=1, tags=self._get_tags())
            logger.warning('Connection to chat server lost')
            uthread2.sleep(5)
            try:
                self.handle_connection_lost()
            except Exception:
                logger.exception('Exception when handling lost connection')

        else:
            logger.warning("Couldn't connect to %s", self.ejabberd_address)
            uthread2.sleep(5)
        uthread2.start_tasklet(self._reconnectToXmppServer)

    def _handleXmppLoginFailed(self):
        self.close_socket()
        self.xmppHandler = None
        monolithmetrics.increment(CONNECTION_LOGIN_FAILED, value=1, tags=self._get_tags())
        logger.warning('Failed to login to chat server')
        try:
            self.handle_login_failed()
        except Exception:
            logger.exception('Exception when handling failed login')

        uthread2.sleep(5)
        uthread2.start_tasklet(self._reconnectToXmppServer)

    def handle_logged_in(self):
        if self.verbose:
            logger.info('Logged in to xmpp server')
        self.hasConnectedOnce = True

    def _get_tags(self):
        return ['address:{}'.format(self.ejabberd_address), 'host:{}'.format(self.hostname)]

    def handle_login_failed(self):
        pass

    def handle_message(self, response):
        pass

    def handle_presence(self, response):
        pass

    def handle_connection_lost(self):
        pass

    def handle_stream_error(self, state, response):
        pass

    def get_password(self):
        pass

    def send_honey_event(self, event_name, extra = None):
        fields = {'eve.xmpp.connection.id': id(self),
         HOST_NAME: self.hostname,
         'eve.xmpp.connection.address': self.ejabberd_address,
         'eve.xmpp.connection.has_connected': self.hasConnectedOnce,
         SERVICE_NAME: SERVICE_NAME_PREFIX + 'xmppConnection'}
        if extra is not None:
            fields.update(extra)
        try:
            mhe.send(event_name, fields)
        except StandardError as e:
            logger.warning('Failed to send honey event: %s' % e)
