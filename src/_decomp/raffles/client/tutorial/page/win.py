#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\tutorial\page\win.py
from __future__ import division
import eveui
import uthread2
from raffles.client import texture
from raffles.client.localization import Text
from raffles.client.tutorial.effects import do_ding
from raffles.client.tutorial.page import Page
from raffles.client.tutorial.page.buy import Ticket

class WinPage(Page):

    def __init__(self):
        super(WinPage, self).__init__(caption=Text.tutorial_win_title(), text=Text.tutorial_win_text(), button_label=Text.tutorial_got_it(), enter_animation=self._animate_enter)

    def _animate_enter(self, container):
        tickets = []
        for i in range(10):
            ticket = container.FindChild('ticket_{}'.format(i))
            left = (i - 2) * 43
            if not ticket:
                ticket = Ticket(name='ticket_{}'.format(i), parent=container, align=eveui.Align.center, left=left, top=20, opacity=0.0)
            if i == 6:
                ticket.owned = True
            offset = (i - int(i / 4)) * 0.05
            if i < 6:
                eveui.fade_in(ticket, duration=0.3, time_offset=offset)
            else:
                eveui.fade_out(ticket, duration=0.2, time_offset=offset / 2)
            eveui.animate(ticket, 'top', end_value=20, duration=0.3, time_offset=offset)
            eveui.animate(ticket, 'left', end_value=left, duration=0.3, time_offset=offset)
            tickets.append(ticket)

        for child in container.children:
            if child not in tickets:
                eveui.fade_out(child, duration=0.2, on_complete=child.Close)

        cube_inner = eveui.Sprite(parent=container, align=eveui.Align.center, pos=(-72, -44, 39, 45), texturePath=texture.hyper_cube_inner, color=(0.4, 0.4, 0.4), opacity=0.0)
        cube_outer = eveui.Sprite(parent=container, align=eveui.Align.center, pos=(0, -30, 39, 45), texturePath=texture.hyper_cube_outer, color=(0.2, 0.2, 0.2), opacity=0.0)
        eveui.animate(cube_inner, 'scale', start_value=(10.0, 10.0), end_value=(1.0, 1.0), duration=0.3)
        eveui.fade_in(cube_inner, duration=0.3, sleep=True)
        eveui.animate(cube_inner, 'left', end_value=0, duration=0.5)
        eveui.animate(cube_inner, 'top', end_value=-30, duration=0.5)
        eveui.fade_in(cube_outer, duration=0.3, time_offset=0.3)
        uthread2.sleep(0.4)
        for step in range(4):
            delay = 0.3 + step * 0.2
            uthread2.sleep(delay)
            for i, ticket in enumerate(tickets):
                eveui.animate(ticket, 'left', end_value=ticket.left - 43, duration=0.3)
                if i <= step:
                    eveui.fade_out(ticket, duration=0.3)
                elif i <= step + 2:
                    opacity = (i - step + 2) / 3 * 0.1
                    eveui.fade(ticket, end_value=opacity, duration=0.3)
                elif i < step + 6:
                    eveui.fade_in(ticket, duration=0.3)

        uthread2.sleep(0.5)
        eveui.animate(cube_outer, 'color', end_value=(0.1607843137254902, 0.6705882352941176, 0.8862745098039215), duration=0.3)
        eveui.animate(cube_inner, 'color', end_value=(1.0, 1.0, 1.0), duration=0.3)
        do_ding(parent=container, align=eveui.Align.center, index=-1, pos=(0, -30, 140, 140))
        do_ding(parent=container, align=eveui.Align.center, index=-1, pos=(0, -30, 140, 140), offset=0.2)
        do_ding(parent=container, align=eveui.Align.center, index=-1, pos=(0, -30, 140, 140), offset=0.5)
        for ticket in tickets:
            if ticket.name != 'ticket_6':
                eveui.fade_out(ticket, duration=0.3)
