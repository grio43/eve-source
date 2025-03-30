#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\client\color.py
from carbonui import Color, TextColor
from evelink.client.const import LinkState, LinkStyle

class LinkColorInfo(object):

    def __init__(self, normal, hover, subtle = None, subtle_hover = None):
        self.normal = Color.from_any(normal)
        self.hover = Color.from_any(hover)
        self.subtle = Color.from_any(subtle or normal)
        self.subtle_hover = Color.from_any(subtle_hover or hover)

    def get_color(self, state, style):
        if state in (LinkState.active, LinkState.hover):
            if style == LinkStyle.subtle:
                return self.subtle_hover
            return self.hover
        if style == LinkStyle.subtle:
            return self.subtle
        return self.normal


default_link_color_info = LinkColorInfo(normal='#d98d00', hover='#ffb732')
default_with_subtle_color_info = LinkColorInfo(normal=default_link_color_info.normal, hover=default_link_color_info.hover, subtle=TextColor.NORMAL, subtle_hover='#ffff00')
external_link_color_info = LinkColorInfo(normal='#ffe400', hover=TextColor.HIGHLIGHT)
settings_link_color_info = LinkColorInfo(normal='#00a99d', hover='#65fff5')
invite_link_color_info = LinkColorInfo(normal='#6868e1', hover='#8e8eff')
help_link_color_info = LinkColorInfo(normal='#94ccff', hover='#aed9ff')
