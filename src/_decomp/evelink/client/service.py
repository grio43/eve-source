#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\client\service.py
import eveexceptions
from carbon.common.script.sys.service import Service
from carbonui import TextColor
from carbonui.util.colorblind import CheckReplaceColor
from evelink.client.color import default_link_color_info
from evelink.client.handlers import register_handlers
from evelink.client.registry import Registry

class LinkService(Service):
    __guid__ = 'svc.link'

    def Run(self, *args):
        super(LinkService, self).Run(*args)
        self._registry = Registry()
        register_handlers(self._registry)

    def reload(self):
        self.Stop()
        self.Run()

    def has_handler_for(self, url):
        return self._registry.has_handler_for(url)

    def resolve(self, url, link_text = None):
        try:
            handler = self._registry.get_handler_for(url)
            handler(url, link_text)
        except eveexceptions.UserError:
            raise
        except Exception:
            self.LogException(u'Failed to resolve {}'.format(url))

    def get_hint(self, url):
        try:
            if self.has_handler_for(url):
                handler = self._registry.get_handler_for(url)
                return handler.get_hint(url)
        except Exception:
            self.LogException(u'Failed to get the hint for url {}'.format(url))

    def get_menu(self, url):
        try:
            if self.has_handler_for(url):
                handler = self._registry.get_handler_for(url)
                return handler.get_menu(url)
        except Exception:
            self.LogException(u'Failed to get the menu for url {}'.format(url))

    def get_color(self, url, state, style):
        try:
            if self.has_handler_for(url):
                handler = self._registry.get_handler_for(url)
                color = handler.get_color(url, state, style)
            else:
                color = default_link_color_info.get_color(state, style)
            return CheckReplaceColor(color, maintainBrightness=True)
        except Exception:
            self.LogException(u'Failed to get the link color for url {}'.format(url))
            return TextColor.NORMAL
