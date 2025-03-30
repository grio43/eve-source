#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmpp\xmppelement.py


class XmppElement(object):

    def __init__(self):
        self.tag = None
        self.attributes = []
        self.text = None
        self.children = []

    def __str__(self):
        return self.toXml()

    def find_child_with_tag(self, tag):
        for c in self.children:
            if c.tag == tag:
                return c

    def toXml(self, indent = 0):
        spaces = ' ' * indent
        attributes = ''
        for a in self.attributes.getNames():
            attributes += '{0}={1} '.format(a, self.attributes.getValue(a).encode('utf-8'))

        result = spaces + '<{0} {1}'.format(self.tag, attributes).strip()
        if self.children or self.text:
            result += '>\n'
            for child in self.children:
                result += child.toXml(indent=indent + 4)

            if self.text:
                result += ' ' * (indent + 4) + self.text.encode('utf-8') + '\n'
            result += spaces + '</{0}>\n'.format(self.tag)
        else:
            result += '/>\n'
        return result
