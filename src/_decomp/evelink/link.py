#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\link.py


class Link(unicode):

    def __new__(cls, url, text, alt = None):
        return unicode.__new__(cls, _format_link(url, text, alt))

    def __init__(self, url, text, alt = None):
        self._url = url
        self._text = text
        self._alt = alt
        super(Link, self).__init__()

    @property
    def url(self):
        return self._url

    @property
    def text(self):
        return self._text

    @property
    def alt(self):
        return self._alt

    def __reduce__(self):
        return (Link, (self.url, self.text, self.alt))


def _format_link(url, text, alt = None):
    return u'<a href="{href}"{alt}>{text}</a>'.format(href=url, alt=u'' if not alt else u' alt="{}"'.format(alt), text=text)
