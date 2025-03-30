#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmpp\xmpphandler.py
import base64
import logging
from xml.sax import make_parser
from xml.sax.saxutils import escape
import unicodedata
from xmppcontenthandler import XmppContentHandler
import monolithmetrics
logger = logging.getLogger(__name__)

def remove_control_characters(unicode_str):
    return u''.join((ch for ch in unicode_str if unicodedata.category(ch)[0] != 'C'))


class XmppHandler(object):

    def __init__(self, owner_xmpp_connection, connection_id):
        self.xmppConnection = owner_xmpp_connection
        self.id = connection_id
        self.state = 'initial'
        self.parser = make_parser()
        self.contentHandler = None
        self.host = None
        self.jid = None
        self.nick = None
        self.username = None
        self.password = None
        self.requests = {}
        self.next_request_id = 1
        self.timed_out_requests_ids = set()
        self.handle_response = self.handle_response_state_not_ready
        self.stream_element = None
        self.stream_features_element = None
        self.verbose = False

    def connect(self, host, username, password):
        self.host = host
        self.username = username
        self.nick = username.split('@')[0]
        self.jid = self.username
        self.password = password
        self.state = 'waiting_for_stream'
        self.start_stream()

    def start_stream(self):
        self.parser.reset()
        self.contentHandler = XmppContentHandler()
        self.parser.setContentHandler(self.contentHandler)
        template = "<?xml version='1.0'?><stream:stream to='{0}' version='1.0' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams'>"
        self.send(template.format(self.host))
        monolithmetrics.increment('xmpp.handler.send', tags=['type:start_stream'])

    def authenticate(self):
        key = base64.b64encode('\x00{0}\x00{1}'.format(self.nick, self.password).encode('ascii')).decode()
        if self.verbose:
            logger.info('Auth Key: %s', key)
        package = "<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='PLAIN'>{0}</auth>".format(key)
        self.state = 'authenticating'
        self.send(package)
        monolithmetrics.increment('xmpp.handler.send', tags=['type:authenticate'])

    def bind(self):
        request = "<bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'><resource>{0}</resource></bind>".format(self.id)
        self.issue_request(request, 'set', self.handle_bind)

    def handle_bind(self, response):
        if self.verbose:
            logger.info('Got response to bind')
        if response.children[0].tag == 'bind':
            bind = response.children[0]
            if bind.children[0].tag == 'jid':
                self.jid = bind.children[0].text
                if self.verbose:
                    logger.info('JID is %s', self.jid)
        self.start_session()

    def start_session(self):
        request = "<session xmlns='urn:ietf:params:xml:ns:xmpp-session'/>".format(self.host)
        self.issue_request(request, 'set', self.handle_session)

    def handle_session(self, _response):
        self.send_initial_presence()
        self.state = 'ready'

    def send_initial_presence(self):
        package = '<presence><show/></presence>'
        self.send(package)
        monolithmetrics.increment('xmpp.handler.send', tags=['type:send_initial_presence'])

    def message(self, receiver, text):
        template = '<message from="{0}" to="{1}" xml:lang="en"><body>{2}</body></message>'
        package = template.format(self.username, receiver, self.sanitize_text(text))
        self.send(package)
        monolithmetrics.increment('xmpp.handler.send', tags=['type:message'])

    def groupchat(self, receiver, text):
        msg_id = self.get_request_id()
        template = "<message from='{0}' to='{1}' type='groupchat' xml:lang='en' id='{2}'><body>{3}</body></message>"
        package = template.format(self.username, receiver, msg_id, self.sanitize_text(text))
        self.send(package)
        monolithmetrics.increment('xmpp.handler.send', tags=['type:groupchat'])
        return msg_id

    def sanitize_text(self, text):
        sanitized = escape(remove_control_characters(text)).encode('utf8')
        return sanitized

    def send_xmpp_subject(self, receiver, text):
        template = '<message from="{0}" to="{1}" type="groupchat" xml:lang="en"><subject>{2}</subject></message>'
        package = template.format(self.username, receiver, self.sanitize_text(text))
        self.send(package)
        monolithmetrics.increment('xmpp.handler.send', tags=['type:send_xmpp_subject'])

    def feed_parser(self, response):
        if self.verbose:
            logger.info('Recv: %s', response)
        self.parser.feed(response)

    def is_queue_empty(self):
        return len(self.contentHandler.queue) == 0

    def pop_queue(self):
        item = self.contentHandler.queue.pop()
        monolithmetrics.gauge('xmpp.content_handler.queue', value=len(self.contentHandler.queue))
        return item

    def flush_queue(self):
        if self.contentHandler and self.contentHandler.queue:
            self.contentHandler.queue = []

    def process_single_queue_item(self, element):
        if self.verbose:
            logger.info('XmppHandler:processing State: %s Username: %s - Received element:\n%s', self.state, self.username, element.toXml())
        if self.xmppConnection.disconnectRequested:
            return
        if element.tag == 'iq':
            iq_type = element.attributes.getValue('type')
            if iq_type == 'get' and element.children[0].tag == 'ping':
                self._handle_ping(element)
            else:
                self._handle_iq_result(element)
        else:
            result = self.handle_response(element)
            if not result:
                if element.tag == 'stream:error':
                    result = self.handle_stream_error(self.state, element)
                if not result:
                    logger.warning('Unhandled response - state %s\n%s', self.state, element.toXml())
        return True

    def _handle_ping(self, element):
        request_id = element.attributes.getValue('id')
        ping_to = element.attributes['to']
        ping_from = element.attributes['from']
        package = "<iq id='{0}' type='result' from='{1}' to='{2}'/>".format(request_id, ping_to, ping_from)
        self.send(package)
        monolithmetrics.increment('xmpp.handler.send', tags=['type:handle_ping'])

    def _handle_iq_result(self, element):
        request_id = element.attributes.getValue('id')
        try:
            callback = self.requests.pop(request_id)
            if callback:
                callback(element)
            monolithmetrics.gauge('xmpp.handler.requests', value=len(self.requests))
        except KeyError:
            try:
                self.timed_out_requests_ids.remove(request_id)
                logger.warning('LATE RESPONSE to timed-out request_id=%s with response=%s', request_id, element)
            except KeyError:
                logger.error('NO CALLBACK FOUND found for RESPONSE to request %s with response=%s', request_id, element)

    def notify_of_timeout(self, request_id, duration_ms, request_type, request, to):
        try:
            _callback = self.requests.pop(request_id)
            monolithmetrics.gauge('xmpp.handler.requests', value=len(self.requests))
            monolithmetrics.increment('xmpp.handler.timeouts')
            logger.warning('TIME-OUT NOTIFIED for request_id=%s after duration_ms=%s, type=%s, request=%s', request_id, duration_ms, request_type, request)
            self.timed_out_requests_ids.add(request_id)
        except KeyError:
            logger.error('NO CALLBACK FOUND for TIMED-OUT request %s', request_id)

    def handle_response_state_not_ready(self, response):
        if self.state == 'waiting_for_stream':
            if response.tag == 'stream:stream':
                self.stream_element = response
                self.state = 'waiting_for_features'
                return True
            else:
                logger.warning('Expected stream:stream tag')
                return True
        elif self.state == 'waiting_for_features':
            if response.tag == 'stream:features':
                self.stream_features_element = response
                self.authenticate()
                return True
        elif self.state == 'authenticating':
            if response.tag == 'success':
                self.start_stream()
                self.state = 'authenticated_waiting_for_stream'
                return True
            if response.tag == 'failure':
                self.handle_login_failed()
                return True
        elif self.state == 'authenticated_waiting_for_stream':
            if response.tag == 'stream:stream':
                self.stream_element = response
                if self.verbose:
                    logger.info('Logged in with id: %s', response.attributes.getValue('id'))
                self.state = 'authenticated_waiting_for_features'
                return True
        elif self.state == 'authenticated_waiting_for_features':
            if response.tag == 'stream:features':
                self.stream_features_element = response
                self.bind()
                return True
        elif self.state == 'ready':
            self.handle_response = self.handle_response_state_ready
            self.handle_logged_in()
            return self.handle_response_state_ready(response)

    def handle_response_state_ready(self, response):
        if response.tag == 'message':
            self.handle_message(response)
            return True
        if response.tag == 'presence':
            self.handle_presence(response)
            return True
        if response.tag == 'stream:closed':
            self.state = 'closed'
            self.handle_response = self.handle_response_state_not_ready
            self.handle_closed()
            return True

    def handle_logged_in(self):
        pass

    def handle_login_failed(self):
        pass

    def handle_message(self, response):
        pass

    def handle_presence(self, response):
        pass

    def handle_closed(self):
        pass

    def handle_stream_error(self, state, response):
        return None

    def send(self, package):
        pass

    def issue_request(self, request, request_type, callback, to = None):
        request_id = self.get_request_id()
        if to is not None:
            to_clause = "to='{0}'".format(to)
        else:
            to_clause = ''
        package = "<iq id='{0}' type='{1}' from='{2}' {3}>{4}</iq>".format(request_id, request_type, self.jid, to_clause, request)
        self.requests[request_id] = callback
        monolithmetrics.gauge('xmpp.handler.requests', value=len(self.requests))
        self.send(package)
        monolithmetrics.increment('xmpp.handler.send', tags=['type:issue_request'])
        return request_id

    def join_room(self, room, password = '', historySeconds = 0):
        request_id = self.get_request_id()
        if password:
            password_element = '<password>{0}</password>'.format(self.sanitize_text(password))
        else:
            password_element = ''
        if historySeconds > 0:
            history_element = "<history seconds='{0}'/>".format(int(historySeconds))
        else:
            history_element = ''
        template = "<presence from='{0}' id='{1}' to='{2}/{3}'><x xmlns='http://jabber.org/protocol/muc'>{4}{5}</x></presence>"
        package = template.format(self.jid, request_id, room, self.nick, password_element, history_element)
        self.send(package)
        monolithmetrics.increment('xmpp.handler.send', tags=['type:join_room'])
        return request_id

    def leave_room(self, room):
        request_id = self.get_request_id()
        template = "<presence from='{0}' id='{1}' to='{2}/{3}' type='unavailable'/>"
        package = template.format(self.jid, request_id, room, self.nick)
        self.send(package)
        monolithmetrics.increment('xmpp.handler.send', tags=['type:leave_room'])
        return request_id

    def get_request_id(self):
        request_id = 'id{0}'.format(self.next_request_id)
        self.next_request_id += 1
        return request_id

    def create_room(self, room):
        request_id = self.get_request_id()
        template = "<presence from='{0}' id='{1}' to='{2}/{3}'><x xmlns='http://jabber.org/protocol/muc'/></presence>"
        package = template.format(self.jid, request_id, room, self.nick)
        self.send(package)
        monolithmetrics.increment('xmpp.handler.send', tags=['type:create_room'])
        return request_id
