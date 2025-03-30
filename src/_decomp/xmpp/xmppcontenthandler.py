#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmpp\xmppcontenthandler.py
import logging
import monolithmetrics
from xml.sax import ContentHandler
from xmpp.xmppelement import XmppElement
logger = logging.getLogger(__name__)

class XmppContentHandler(ContentHandler):

    def __init__(self):
        ContentHandler.__init__(self)
        self.queue = []
        self.current_element = None
        self.element_stack = []

    def startElement(self, name, attrs):
        element = XmppElement()
        element.tag = name
        element.attributes = attrs
        if name == 'stream:stream':
            self.queue.append(element)
            monolithmetrics.gauge('xmpp.content_handler.queue', value=len(self.queue))
            return
        self.element_stack.append(self.current_element)
        self.current_element = element

    def endElement(self, name):
        if not self.current_element:
            if name == 'stream:stream':
                element = XmppElement()
                element.tag = 'stream:closed'
                return
            raise RuntimeError('No current element')
        if name != self.current_element.tag:
            raise RuntimeError('Mismatched tag')
        parent = self.element_stack.pop()
        if parent:
            parent.children.append(self.current_element)
        else:
            self.queue.insert(0, self.current_element)
            monolithmetrics.gauge('xmpp.content_handler.queue', value=len(self.queue))
        self.current_element = parent

    def characters(self, content):
        if self.current_element.text:
            self.current_element.text += content
        else:
            self.current_element.text = content
