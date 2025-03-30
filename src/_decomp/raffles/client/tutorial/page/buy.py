#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\tutorial\page\buy.py
from __future__ import division
import eveui
import proper
import uthread2
from raffles.client import texture
from raffles.client.localization import Text
from raffles.client.tutorial.page import Page
from raffles.client.tutorial.effects import do_ding

class BuyPage(Page):

    def __init__(self):
        super(BuyPage, self).__init__(caption=Text.tutorial_buy_title(), text=Text.tutorial_buy_text(), button_label=Text.tutorial_next(), enter_animation=self._animate_enter, exit_animation=self._animate_exit)

    def _animate_enter(self, container):
        header = Header(name='header', parent=container, align=eveui.Align.center, left=-30, top=-25)
        header.anim_show_icon()
        uthread2.sleep(0.3)
        eveui.animate(header, 'left', end_value=-73, duration=0.4)
        eveui.animate(header, 'top', end_value=-42, duration=0.4)
        uthread2.sleep(0.3)
        header.anim_show_text()
        uthread2.sleep(0.3)
        owned_ticket = None
        for i in range(16):
            x = i % 4 * 42 - 62
            y = int(i / 4) * 18 - 20
            ticket = Ticket(name='ticket_{}'.format(i), parent=container, align=eveui.Align.center, left=x, top=y, opacity=0.0)
            if i == 6:
                owned_ticket = ticket
            offset = (i - int(i / 4)) * 0.03
            eveui.animate(ticket, 'top', start_value=ticket.top - 10, end_value=ticket.top, duration=0.2, time_offset=offset)
            eveui.animate(ticket, 'left', start_value=ticket.left - i % 4 * 20, end_value=ticket.left, duration=0.2, time_offset=offset)
            eveui.fade_in(ticket, duration=0.2, time_offset=offset)

        uthread2.sleep(0.8)
        do_ding(parent=container, align=eveui.Align.center, pos=(owned_ticket.left,
         owned_ticket.top,
         80,
         80))
        do_ding(parent=container, align=eveui.Align.center, pos=(owned_ticket.left,
         owned_ticket.top,
         80,
         80), offset=0.1)
        owned_ticket.owned = True

    def _animate_exit(self, container):
        for child in container.children:
            if child.name == 'header' or 'ticket_' in child.name:
                continue
            else:
                eveui.fade_out(child, duration=child.opacity * 0.2, on_complete=child.Close)
                eveui.animate(child, 'left', end_value=child.left - 10, duration=0.2)


class Header(eveui.Container):
    default_width = 10
    default_height = 10

    def __init__(self, **kwargs):
        super(Header, self).__init__(**kwargs)
        self._layout()

    def anim_show_icon(self, offset = 0.0):
        eveui.fade(self._item_icon, start_value=0.0, end_value=1.0, duration=0.3, time_offset=offset)

    def anim_show_text(self, offset = 0.0):
        eveui.fade(self._text, start_value=0.0, end_value=1.0, duration=0.3, time_offset=offset)
        eveui.fade(self._sub_text, start_value=0.0, end_value=1.0, duration=0.3, time_offset=0.05 + offset)

    def _layout(self):
        self._item_icon = eveui.Fill(parent=self, align=eveui.Align.top_left, width=10, height=10, color=(0.8, 0.8, 0.8), opacity=0.0)
        self._text = eveui.Fill(parent=self, align=eveui.Align.top_left, pos=(14, 2, 24, 2), color=(0.8, 0.8, 0.8), opacity=0.0)
        self._sub_text = eveui.Fill(parent=self, align=eveui.Align.top_left, pos=(14, 6, 16, 2), color=(0.4, 0.4, 0.4), opacity=0.0)


class Ticket(proper.Observable, eveui.Container):
    default_width = 35
    default_height = 11

    def __init__(self, **kwargs):
        self._boxes = []
        super(Ticket, self).__init__(**kwargs)
        self._layout()

    @proper.ty(default=False)
    def owned(self):
        pass

    def on_owned(self, owned):
        eveui.animate(self._underlay, 'color', end_value=self._get_underlay_color(), duration=0.3)
        color = self._get_box_color()
        for box in self._boxes:
            eveui.animate(box, 'color', end_value=color, duration=0.3)

    def blink(self):
        eveui.animate(self._underlay, 'color', end_value=(0.5, 0.5, 0.5), duration=1.0, loops=4, curve_type=eveui.CurveType.bounce)

    def _layout(self):
        color = self._get_box_color()
        for i in range(4):
            left = 2 + i * 8
            box = eveui.Frame(parent=self, align=eveui.Align.top_left, pos=(left,
             2,
             7,
             7), texturePath=texture.panel_1_corner_2px, cornerSize=2, color=color)
            self._boxes.append(box)

        self._underlay = eveui.Frame(parent=self, align=eveui.Align.to_all, texturePath=texture.panel_1_corner_3px, cornerSize=3, color=self._get_underlay_color())

    def _get_box_color(self):
        if self.owned:
            return (0.1607843137254902, 0.6705882352941176, 0.8862745098039215)
        else:
            return (0.34, 0.34, 0.34)

    def _get_underlay_color(self):
        if self.owned:
            return (0.0, 0.44313725490196076, 0.7372549019607844)
        else:
            return (0.2, 0.2, 0.2)
