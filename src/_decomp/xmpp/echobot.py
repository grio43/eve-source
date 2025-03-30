#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmpp\echobot.py
import logging
from xmpp import XmppConnection
logger = logging.getLogger(__name__)

class EchoBot(object):

    def __init__(self, host, username, password, servername = None):
        self.host = host
        self.username = '{0}@{1}'.format(username, host)
        self.xmppConnection = XmppConnection(host)
        self.xmppConnection.handle_message = self.handle_xmpp_message
        self.xmppConnection.handle_presence = self.handle_xmpp_presence
        self.xmppConnection.handle_closed = self.handle_closed

    def connect(self):
        self.xmppConnection.Connect(self.username)

    def handle_xmpp_message(self, response):
        sender = response.attributes.getValue('from').split('/')[0]
        logger.debug(sender)
        text = ''
        for child in response.children:
            if child.tag == 'body':
                text = child.text

        logger.debug(text)
        self.xmppConnection.Message(sender, text)

    def handle_xmpp_presence(self, response):
        try:
            type = response.attributes.getValue('type')
            requester = response.attributes.getValue('from')
            if type == 'subscribe':
                package = "<presence to='{0}' type='subscribed'/>".format(requester)
                self.xmppConnection.Send(package)
        except KeyError:
            pass

    def handle_closed(self):
        logger.debug('Stream closed')
