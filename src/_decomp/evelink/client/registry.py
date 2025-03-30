#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\client\registry.py
import logging
import localization
from evelink.client.color import default_link_color_info
log = logging.getLogger(__name__)

class Registry(object):

    def __init__(self):
        self._handlers = {}

    def has_handler_for(self, url):
        try:
            scheme = parse_scheme(url)
            if scheme is None:
                return False
            return normalize_scheme(scheme) in self._handlers
        except Exception:
            log.exception('Failed to parse url {}'.format(url))
            return False

    def get_handler_for(self, url):
        scheme = parse_scheme(url)
        if scheme is None:
            raise ValueError('No scheme found in the given URL')
        return self._handlers[normalize_scheme(scheme)]

    def register(self, scheme, handler, hint = None, menu = None, color_info = None, accept_link_text = False):
        normalized_scheme = normalize_scheme(scheme)
        if normalized_scheme in self._handlers:
            log.warning('Overriding handler for scheme {}'.format(scheme))
        handler = LinkHandler(scheme, handler, hint, menu, color_info, accept_link_text)
        self._handlers[normalized_scheme] = handler

    def unregister(self, scheme):
        try:
            del self._handlers[normalize_scheme(scheme)]
        except KeyError:
            log.warning('Attempting to unregister nonexisting handler for {}'.format(scheme))


def normalize_scheme(scheme):
    return scheme.lower()


def parse_scheme(url):
    try:
        return url[:url.index(':')]
    except ValueError:
        return None


class LinkHandler(object):

    def __init__(self, scheme, handler, hint = None, menu = None, color_info = None, accept_link_text = False):
        self.scheme = scheme
        self.handler = handler
        self._hint = hint
        self._menu = menu
        self._color_info = color_info
        self._accept_link_text = accept_link_text

    def __call__(self, url, link_text = None):
        if self._accept_link_text:
            self.handler(url, link_text)
        else:
            self.handler(url)

    def get_hint(self, url):
        if callable(self._hint):
            return self._hint(url)
        elif self._hint is not None:
            return localization.GetByLabel(self._hint)
        else:
            return

    def get_menu(self, url):
        if self._menu:
            return self._menu(url)

    def get_color(self, url, state, style):
        if callable(self._color_info):
            color_info = self._color_info(url)
        else:
            color_info = self._color_info
        if color_info is None:
            color_info = default_link_color_info
        return color_info.get_color(state, style)
