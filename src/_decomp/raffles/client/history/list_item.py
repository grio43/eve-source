#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\history\list_item.py
import functools
import math
import random
import eveformat.client
import eveui
import trinity
import uthread2
from carbon.common.script.util.format import FmtDate
from carbonui import TextColor
from carbonui.uianimations import animations
from datetimeutils import datetime_to_filetime
from utillib import KeyVal
from raffles.client import sound, texture
from raffles.client.localization import Text
from raffles.client.util import get_market_estimate_text, character_name, station_name
from raffles.client.widget.item_icon import ItemIcon
from raffles.client.widget.quick_buy_button import QuickBuyButton
PADRIGHT = 10

class ListItemUninitialized(RuntimeError):
    pass


def swallow_uninitialized_error(f):

    @functools.wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ListItemUninitialized:
            return

    return inner


def singleton_threaded_method(f):

    def kill_thread_maybe(self):
        thread_map = getattr(self, '_singleton_threads', {})
        if f in thread_map:
            thread_map[f].kill()
            del thread_map[f]
            return True
        return False

    f.kill_thread_maybe = kill_thread_maybe

    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        f.kill_thread_maybe(self)
        thread = uthread2.start_tasklet(f, self, *args, **kwargs)
        if not hasattr(self, '_singleton_threads'):
            self._singleton_threads = {}
        self._singleton_threads[f] = thread

    return wrapper


class RaffleListItem(eveui.Container):
    default_align = eveui.Align.to_top
    default_state = eveui.State.hidden
    default_height = 90
    default_padBottom = 6
    default_clipChildren = True
    isDragObject = True

    def __init__(self, navigation, **kwargs):
        super(RaffleListItem, self).__init__(**kwargs)
        self._navigation = navigation
        self._raffle = None
        self._time_remaining_thread = None
        self._layout()

    @property
    def raffle(self):
        if self._raffle is None:
            raise ListItemUninitialized()
        return self._raffle

    @raffle.setter
    def raffle(self, raffle):
        if self.is_initialized:
            self._unsubscribe(self._raffle)
        self._raffle = raffle

    @property
    def is_initialized(self):
        return self._raffle is not None

    def update_item(self, raffle):
        if self._raffle is raffle:
            return
        self.raffle = raffle
        self._update_item()

    @singleton_threaded_method
    @swallow_uninitialized_error
    def _update_item(self):
        if not self.is_initialized:
            self.state = eveui.State.hidden
            return
        self.state = eveui.State.normal
        self.owner_badge.update(self.raffle.is_raffle_owner)
        self.private_badge.update(self.raffle.is_private)
        self.item_label.text = self.raffle.item_name
        self.item_group_label.text = self.raffle.item_group_name
        self.market_estimate_label.text = get_market_estimate_text(self.raffle.type_id, self.raffle.item_id)
        self.location_label.text = u'{}\n{}'.format(eveformat.solar_system_with_security_and_jumps(self.raffle.solar_system_id), station_name(self.raffle.location_id, linkify=False))
        self.item_icon.SetTypeIDandItemID(self.raffle.type_id, self.raffle.item_id, isCopy=self.raffle.is_blueprint_copy)
        self.ticket_price_label.text = eveformat.isk(self.raffle.ticket_price)
        self.ticket_price_label.hint = eveformat.isk_readable(self.raffle.ticket_price)
        self._on_status_changed()
        self._on_tickets_sold()
        self._subscribe(self.raffle)
        if not self.raffle.is_finished and not self._time_remaining_thread:
            self._time_remaining_thread = uthread2.start_tasklet(self._time_remaining_routine)

    def _subscribe(self, raffle):
        raffle.on_tickets_sold.connect(self._on_tickets_sold)
        raffle.on_status_changed.connect(self._on_status_changed)

    def _unsubscribe(self, raffle):
        raffle.on_tickets_sold.disconnect(self._on_tickets_sold)
        raffle.on_status_changed.disconnect(self._on_status_changed)

    def _on_tickets_sold(self, *args, **kwargs):
        if self.raffle.is_finished:
            self.tickets_label.text = self.raffle.ticket_count
        else:
            self.quick_buy_button.tickets_sold()
            self.tickets_label.text = Text.remaining_tickets(remaining_ticket_count=self.raffle.tickets_remaining_count, ticket_count=self.raffle.ticket_count)

    def _on_status_changed(self, *args, **kwargs):
        self._shimmer.stop()
        if self.raffle.is_finished:
            self.active_container.state = eveui.State.hidden
            self.finished_container.state = eveui.State.pick_children
            self._update_finished()
        else:
            self.finished_container.state = eveui.State.hidden
            self.active_container.state = eveui.State.pick_children
            self._update_active()

    def _update_finished(self):
        self.end_time_label.text = FmtDate(datetime_to_filetime(self.raffle.end_time), 'ln')
        if self.raffle.requires_interaction:
            self.expired_container.state = eveui.State.hidden
            self.winner_container.state = eveui.State.hidden
            self.interaction_container.state = eveui.State.pick_children
            self._shimmer.start()
            if self.raffle.is_winner_unseen:
                reason = Text.card_show_winner()
                self.finished_separator.color = (0.2, 0.6, 1.0)
                self._shimmer.color = (0.2, 0.6, 1.0)
            else:
                reason = Text.card_claim_prize()
                self.finished_separator.color = (1.0, 0.9, 0.6)
                self._shimmer.color = (1.0, 0.9, 0.6)
            self.interaction_label.text = reason
        elif self.raffle.winner_id:
            self.expired_container.state = eveui.State.hidden
            self.interaction_container.state = eveui.State.hidden
            self.winner_container.state = eveui.State.pick_children
            if self.raffle.is_raffle_winner:
                self.finished_separator.color = (1.0, 0.9, 0.6, 0.5)
            else:
                self.finished_separator.color = (1.0, 1.0, 1.0, 0.25)
            self.winner_portrait.character_id = self.raffle.winner_id
            self.winner_name.text = character_name(self.raffle.winner_id, linkify=True)
        else:
            self.interaction_container.state = eveui.State.hidden
            self.winner_container.state = eveui.State.hidden
            self.expired_container.state = eveui.State.disabled
            self.finished_separator.color = (1.0, 1.0, 1.0, 0.25)

    def _update_active(self):
        self.quick_buy_button.set_raffle(self.raffle)

    def Close(self):
        super(RaffleListItem, self).Close()
        if self.is_initialized:
            self._unsubscribe(self.raffle)

    @swallow_uninitialized_error
    def OnClick(self, *args, **kwargs):
        eveui.play_sound(sound.card_click)
        self._navigation.open_details_page(self.raffle.raffle_id)

    @swallow_uninitialized_error
    def OnMouseEnter(self, *args):
        eveui.play_sound(sound.card_hover)
        eveui.fade(self.bg, end_value=0.8, duration=0.1)
        if not self.raffle.is_finished:
            self.quick_buy_button.card_enter()

    @swallow_uninitialized_error
    def OnMouseExit(self):
        eveui.fade(self.bg, end_value=0.3, duration=0.3)
        if not self.raffle.is_finished:
            self.quick_buy_button.card_exit()

    @swallow_uninitialized_error
    def GetDragData(self):
        return [self.raffle.get_drag_data()]

    @swallow_uninitialized_error
    def GetMenu(self):
        menu = sm.GetService('menu').GetMenuFromItemIDTypeID(self.raffle.item_id, self.raffle.type_id, includeMarketDetails=True, abstractInfo=KeyVal(bpData=self.item_icon.bpData))
        menu.append(None)
        menu.append((Text.browse_type_context_menu(), self._browse_type, (self.raffle.type_id,)))
        if self.raffle.is_winner_unseen:
            menu.append((Text.show_winner_context_menu(), self._show_winner))
        return menu

    def _browse_type(self, type_id):
        self._navigation.open_browse_page(type_id)

    @swallow_uninitialized_error
    def _show_winner(self):
        self.raffle.update_winner_seen(True)
        self._on_status_changed()

    def _time_remaining_routine(self):
        try:
            while not self.destroyed and not self.raffle.is_finished:
                self.expiration_label.text = self.raffle.time_remaining_text
                uthread2.sleep(1)

        except ListItemUninitialized:
            pass
        finally:
            self._time_remaining_thread = None

    def _layout(self):
        self._construct_owner_icon()
        self._construct_content()
        self.end_group = eveui.Container(parent=self.content_container)
        self._construct_active()
        self._construct_finished()
        self._construct_background()

    def _construct_owner_icon(self):
        badge_container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.top_right, left=16, height=32)
        self.owner_badge = Badge(parent=badge_container, icon=texture.created_icon, icon_opacity=0.75, hint=Text.created_by_player_hint())
        self.private_badge = Badge(parent=badge_container, icon=texture.hyperlink_icon, icon_opacity=1.5, hint=Text.private_raffle_hint())

    def _construct_background(self):
        self.bg = eveui.Frame(name='bg', bgParent=self, texturePath=texture.panel_1_corner, cornerSize=9, color=(0.15, 0.15, 0.15), opacity=0.3)
        self._shimmer = Shimmer(parent=self, align=eveui.Align.center_left)

    def _construct_content(self):
        self.content_container = eveui.Container(name='content', parent=self, padding=10)
        self._construct_icon()
        group_0 = eveui.Container(name='Group0', parent=self.content_container, align=eveui.Align.to_left, width=225, padRight=PADRIGHT)
        self.item_group_label = eveui.EveLabelSmall(parent=group_0, align=eveui.Align.center_left, maxWidth=225, maxLines=1, top=-22, color=TextColor.SECONDARY)
        self.item_label = eveui.EveLabelLarge(parent=group_0, align=eveui.Align.center_left, maxWidth=225, maxLines=1, top=-6)
        self.market_estimate_label = eveui.EveLabelMedium(parent=group_0, align=eveui.Align.center_left, top=16, color=TextColor.SECONDARY)
        group_1 = eveui.Container(name='Group1', parent=self.content_container, align=eveui.Align.to_left, width=140, padRight=PADRIGHT)
        tickets = LabelValue(parent=group_1, align=eveui.Align.to_top, label=Text.tickets())
        self.tickets_label = tickets.value
        ticket_price = LabelValue(parent=group_1, align=eveui.Align.to_bottom, label=Text.ticket_price())
        self.ticket_price_label = ticket_price.value
        self.ticket_price_label.state = eveui.State.normal
        self.ticket_price_label.OnClick = self.OnClick
        self.ticket_price_label.GetDragData = self.GetDragData
        self.ticket_price_label.PrepareDrag = self.PrepareDrag
        self.ticket_price_label.GetMenu = self.GetMenu
        group_2 = eveui.Container(name='Group2', parent=self.content_container, align=eveui.Align.to_left, width=225, padRight=PADRIGHT)
        location = LabelValue(parent=group_2, align=eveui.Align.to_top, label=Text.location(), height=62, max_lines=3)
        self.location_label = location.value

    def _construct_icon(self):
        container = eveui.Container(name='iconContainer', parent=self.content_container, align=eveui.Align.to_left, width=76, padRight=12)
        self.item_icon = ItemIcon(parent=container, width=56, height=56)
        self.item_icon.OnClick = self.OnClick
        self.item_icon.GetDragData = self.GetDragData
        self.item_icon.GetMenu = self.GetMenu

    def _construct_active(self):
        self.active_container = container = eveui.Container(parent=self.content_container)
        expire = LabelValue(parent=container, align=eveui.Align.to_top, label=Text.expires_in())
        self.expiration_label = expire.value
        self.quick_buy_button = QuickBuyButton(parent=container, align=eveui.Align.bottom_right)

    def _construct_finished(self):
        self.finished_container = container = eveui.Container(parent=self.content_container)
        self.finished_separator = eveui.Line(parent=container, align=eveui.Align.to_left, padding=(-12, -2, 12, -2))
        self.end_time_label = eveui.EveLabelSmall(parent=container, align=eveui.Align.bottom_right, height=13, color=TextColor.SECONDARY)
        self.interaction_container = eveui.Container(name='interactionContainer', parent=container)
        eveui.EveLabelSmall(parent=self.interaction_container, align=eveui.Align.to_top, top=16, text=Text.card_completed(), color=TextColor.SECONDARY)
        self.interaction_label = eveui.EveLabelMediumBold(parent=self.interaction_container, align=eveui.Align.to_top)
        self.winner_container = eveui.Container(name='winnerContainer', parent=container)
        portrait_container = eveui.Container(parent=self.winner_container, align=eveui.Align.to_left, width=56, padRight=6)
        self.winner_portrait = eveui.CharacterPortrait(parent=portrait_container, align=eveui.Align.center_left, size=56)
        eveui.EveLabelSmall(parent=self.winner_container, align=eveui.Align.to_top, text=Text.card_winner(), color=TextColor.SECONDARY, top=8)
        name_container = eveui.Container(parent=self.winner_container, align=eveui.Align.to_top, height=16, clipChildren=True)
        self.winner_name = eveui.EveLabelMedium(parent=name_container, state=eveui.State.normal, opacity=0.75)
        self.expired_container = eveui.Container(name='expiredContainer', parent=container)
        eveui.EveLabelMediumBold(parent=self.expired_container, align=eveui.Align.to_top, top=20, text=Text.card_expired(), color=TextColor.SECONDARY)


class Badge(eveui.Container):
    default_align = eveui.Align.to_right
    default_state = eveui.State.normal
    default_width = 22
    default_padLeft = 8
    default_bgTexturePath = texture.flag

    def __init__(self, icon, icon_opacity = 1.0, **kwargs):
        super(Badge, self).__init__(**kwargs)
        eveui.Sprite(parent=self, align=eveui.Align.center, top=-3, width=16, height=16, texturePath=icon, opacity=icon_opacity)

    def update(self, active):
        if active:
            self.Show()
        else:
            self.Hide()


class Shimmer(eveui.Container):
    default_state = eveui.State.disabled
    default_height = 90
    default_width = 340

    def __init__(self, color = None, **kwargs):
        if color is None:
            color = (1.0, 1.0, 1.0)
        self._color = color
        self._shimmer_thread = None
        super(Shimmer, self).__init__(**kwargs)
        self._layout()
        self.start()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        self._shine.SetRGBA(*eveui.Color(*color).SetAlpha(self._shine.opacity).GetRGBA())

    def start(self):
        if not self._shimmer_thread:
            self._shimmer_thread = uthread2.start_tasklet(self._animate_shimmer)

    def stop(self):
        if self._shimmer_thread:
            self._shimmer_thread.kill()
            self._shimmer_thread = None
        eveui.fade(self.underlay, end_value=0.2, duration=0.1)
        eveui.fade(self._shine, end_value=0.0, duration=0.0)

    def Close(self):
        self.stop()
        for child in self.children:
            eveui.stop_all_animations(child)

        super(Shimmer, self).Close()

    def _animate_shimmer(self):
        uthread2.sleep(random.random() * 2.0)
        eveui.fade_in(self._shine, end_value=0.2, duration=0.1)
        while not self.destroyed:
            animations.SpSwoopBlink(self._shine, rotation=math.pi, duration=1.5)
            eveui.fade(self.underlay, end_value=0.4, duration=0.25, sleep=True)
            uthread2.sleep(0.3)
            eveui.fade(self.underlay, end_value=0.2, duration=0.75, sleep=True)
            uthread2.sleep(random.random() * 1.5 + 0.5)

    def _layout(self):
        self.underlay = eveui.Sprite(parent=self, align=eveui.Align.to_all, texturePath=texture.list_item_shimmer_underlay, blendMode=trinity.TR2_SBM_ADD, opacity=0.2)
        self._shine = eveui.Sprite(parent=self, align=eveui.Align.to_all, texturePath=texture.list_item_shimmer_effect, blendMode=trinity.TR2_SBM_ADDX2, color=self._color, opacity=0.0)


class LabelValue(eveui.Container):
    default_height = 29

    def __init__(self, label = '', value = '', max_lines = 1, **kwargs):
        super(LabelValue, self).__init__(**kwargs)
        self.label = eveui.EveLabelSmall(parent=self, align=eveui.Align.to_top, text=label, color=TextColor.SECONDARY)
        self.value = eveui.EveLabelMedium(parent=self, align=eveui.Align.to_top, text=value, maxLines=max_lines)
