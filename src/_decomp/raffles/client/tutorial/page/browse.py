#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\tutorial\page\browse.py
from __future__ import division
import random
import eveui
import threadutils
import uthread2
from raffles.client import texture
from raffles.client.localization import Text
from raffles.client.tutorial.page import Page
from raffles.client.tutorial.effects import do_ding

class BrowsePage(Page):

    def __init__(self):
        super(BrowsePage, self).__init__(caption=Text.tutorial_browse_title(), text=Text.tutorial_browse_text(), button_label=Text.tutorial_next(), enter_animation=self._animate_enter, exit_animation=self._animate_exit)
        self.palette = ((0.984313725490196, 0.6901960784313725, 0.23137254901960785), (0.1607843137254902, 0.6705882352941176, 0.8862745098039215))

    def _animate_enter(self, container):
        filter_button = eveui.Frame(parent=container, align=eveui.Align.center, pos=(-72, -60, 16, 9), texturePath=texture.panel_1_corner_3px, cornerSize=3, color=(0.25, 0.25, 0.25), opacity=0.0)
        eveui.animate(filter_button, 'top', end_value=-50, duration=0.2)
        eveui.fade_in(filter_button, duration=0.2)
        refresh_button = eveui.Frame(parent=container, align=eveui.Align.center, pos=(70, -60, 24, 9), texturePath=texture.panel_1_corner_3px, cornerSize=3, color=(0.0, 0.44313725490196076, 0.7372549019607844), opacity=0.0)
        eveui.animate(refresh_button, 'top', end_value=-50, duration=0.2, time_offset=0.1)
        eveui.fade_in(refresh_button, duration=0.2, time_offset=0.1)
        cards = []
        for i in range(12):
            x = i % 4 * 42 - 62
            y = int(i / 4) * 30 - 20
            card = Card(name='card_{}'.format(i), parent=container, align=eveui.Align.center, left=x, top=y + 10, opacity=0.0)
            offset = (i - int(i / 4)) * 0.03 + 0.1
            eveui.animate(card, 'top', end_value=y, duration=0.25, time_offset=offset)
            eveui.fade_in(card, duration=0.25, time_offset=offset)
            cards.append(card)

        uthread2.sleep(1.4)
        self._refresh(container, cards)
        uthread2.sleep(1.4)
        self._filter(container, cards)

    def _refresh(self, container, cards):
        do_ding(parent=container, align=eveui.Align.center, pos=(70, -50, 100, 100))
        do_ding(parent=container, align=eveui.Align.center, pos=(70, -50, 100, 100), offset=0.1)
        uthread2.sleep(0.5)
        for i, card in enumerate(cards):
            new_color = random.choice(self.palette)
            offset = (i - int(i / 4)) * 0.05
            self._refresh_card(card, offset, item_color=new_color)

    def _filter(self, container, cards):
        do_ding(parent=container, align=eveui.Align.center, pos=(-72, -50, 100, 100))
        do_ding(parent=container, align=eveui.Align.center, pos=(-72, -50, 100, 100), offset=0.1)
        uthread2.sleep(0.5)
        new_color = random.choice(self.palette)
        for i, card in enumerate(cards):
            offset = (i - int(i / 4)) * 0.05
            self._refresh_card(card, offset, item_color=new_color)

    def _refresh_card(self, card, offset, item_color = None):

        def the_rest():
            eveui.fade_in(card, duration=0.25, time_offset=0.3)
            eveui.animate(card, 'top', start_value=card.top + 10, end_value=card.top, duration=0.25, time_offset=0.3)

        eveui.fade_out(card, duration=0.25, time_offset=offset, on_complete=the_rest)

    def _animate_exit(self, container):
        card = None
        for child in container.children:
            if child.name == 'card_1':
                card = child
                continue
            eveui.fade_out(child, duration=child.opacity * 0.2, on_complete=child.Close)

        if card is None:
            return
        eveui.fade_in(card, duration=0.1)
        do_ding(parent=container, align=eveui.Align.center, pos=(card.left,
         card.top,
         100,
         100))
        do_ding(parent=container, align=eveui.Align.center, pos=(card.left,
         card.top,
         100,
         100), offset=0.1)
        uthread2.sleep(0.4)
        eveui.fade_out(card, duration=0.3, time_offset=0.3, on_complete=card.Close)


class Card(eveui.Container):
    default_height = 25
    default_width = 36
    default_item_color = (0.8, 0.8, 0.8)

    def __init__(self, item_color = None, **kwargs):
        self._item_color = item_color or self.default_item_color
        super(Card, self).__init__(**kwargs)
        self._layout()

    @property
    def item_color(self):
        return self._item_color

    @item_color.setter
    def item_color(self, color):
        self._item_color = color
        self._item_icon.SetRGBA(*color)

    def _layout(self):
        top_cont = eveui.Container(parent=self, align=eveui.Align.to_top, height=16, bgColor=(0.24, 0.24, 0.24))
        self._item_icon = eveui.Fill(parent=top_cont, align=eveui.Align.top_left, pos=(3, 3, 10, 10), color=self._item_color)
        eveui.Frame(parent=self, align=eveui.Align.to_all, texturePath=texture.panel_1_corner_3px, cornerSize=3, color=(0.06, 0.06, 0.06))
