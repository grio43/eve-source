#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\raffle_card\card.py
import functools
import math
import eveformat.client
import eveui
import eveui.compatibility
import threadutils
import trinity
import uthread2
from carbonui import fontconst, TextColor
from eve.client.script.ui.control.infoIcon import InfoIcon
from utillib import KeyVal
from raffles.client import sound, texture
from raffles.client.localization import Text
from raffles.client.util import get_market_estimate_text, character_name
from raffles.client.widget.item_icon import ItemIcon
from raffles.client.widget.linear_progress import LinearProgress
from raffles.client.widget.sweep_effect import SweepEffect
from raffles.client.widget.quick_buy_button import QuickBuyButton
PADDING = 6

class RaffleCard(eveui.compatibility.CarbonEventHandler, eveui.Container):
    default_name = 'RaffleCard'
    default_state = eveui.State.disabled
    default_opacity = 0.0
    isDragObject = True

    def __init__(self, navigation, on_filter = None, **kwargs):
        super(RaffleCard, self).__init__(**kwargs)
        self._navigation = navigation
        self._on_filter = on_filter
        self._raffle = None
        self._sweep_effect = None
        self._ticket_anim = False
        self._few_tickets_remaining = None
        self._layout()

    def Close(self):
        super(RaffleCard, self).Close()
        self._unsubscribe()

    def GetDragData(self):
        return [self._raffle.get_drag_data()]

    def GetMenu(self):
        menu = sm.GetService('menu').GetMenuFromItemIDTypeID(self._raffle.item_id, self._raffle.type_id, includeMarketDetails=True, abstractInfo=KeyVal(bpData=self.item_icon.bpData))
        if self._on_filter:
            menu.append(None)
            menu.append((Text.filter_type_context_menu(), self._filter_type))
            menu.append((Text.filter_group_context_menu(), self._filter_group))
            menu.append((Text.filter_solar_system_context_menu(), self._filter_solar_system))
        return menu

    def _filter_type(self):
        self._on_filter(type_id=self._raffle.type_id)

    def _filter_group(self):
        self._on_filter(group_id=self._raffle.group_id)

    def _filter_solar_system(self):
        self._on_filter(solar_system_id=self._raffle.solar_system_id)

    def OnClick(self, *args, **kwargs):
        sound.play(sound.card_click)
        self._navigation.open_details_page(self._raffle.raffle_id)

    def OnMouseEnter(self, *args):
        t = self._raffle.time_remaining
        sound.play(sound.card_hover)
        duration = 0.1
        eveui.fade(self.corner, end_value=1.0, duration=duration)
        eveui.fade(self.background_frame, end_value=0.8, duration=duration)
        eveui.fade_in(self.info_icon, duration=duration)
        self.buy_button.card_enter()

    def OnMouseExit(self, *args):
        duration = 0.3
        eveui.fade(self.corner, end_value=0.5, duration=duration)
        eveui.fade(self.background_frame, end_value=0.3, duration=duration)
        eveui.fade_out(self.info_icon, duration=0.1)
        self.buy_button.card_exit()

    def turn_on(self, raffle, time_offset = 0):
        self._raffle = raffle
        if not self._raffle:
            self.Disable()
            return
        self.item_icon.SetTypeIDandItemID(self._raffle.type_id, self._raffle.item_id, isCopy=self._raffle.is_blueprint_copy)
        self.info_icon.UpdateInfoLink(self._raffle.type_id, self._raffle.item_id)
        self.title_label.text = self._raffle.item_name
        self.market_estimate_label.text = get_market_estimate_text(self._raffle.type_id, self._raffle.item_id)
        self.location_label.text = eveformat.solar_system_with_security_and_jumps(self._raffle.solar_system_id)
        self.buy_button.set_raffle(self._raffle)
        eveui.fade_in(self, duration=0.3, time_offset=time_offset, on_complete=self.Enable)
        self._update_state()
        self._raffle.on_tickets_sold.connect(self._on_tickets_sold)
        self._raffle.on_status_changed.connect(self._on_status_changed)
        self.Enable()

    def turn_off(self, time_offset = 0):
        self._unsubscribe()
        self.Disable()
        self._raffle = None
        self.buy_button.set_raffle(self._raffle)
        if self._few_tickets_remaining:
            self._few_tickets_remaining.kill()
            self._few_tickets_remaining = None
        eveui.fade_out(self, duration=0.3, time_offset=time_offset)

    def _unsubscribe(self):
        if self._raffle:
            self._raffle.on_tickets_sold.disconnect(self._on_tickets_sold)
            self._raffle.on_status_changed.disconnect(self._on_status_changed)

    def _on_status_changed(self, *args, **kwargs):
        if self._raffle.is_finished:
            sound.play(sound.card_finished)
        self._update_state()

    def _update_state(self):
        self.state_container.Flush()
        if self._sweep_effect:
            self._sweep_effect.Close()
            self._sweep_effect = None
        if self._raffle.is_finished:
            self.location_label.opacity = 0
            self._construct_finished_bottom()
        else:
            self.location_label.opacity = 1
            self._construct_active_bottom()
            self._update_tickets()
        self.buy_button.update_state()

    def _update_tickets(self):
        if self._raffle.is_finished:
            return
        self.tickets_label.text = Text.remaining_tickets(remaining_ticket_count=self._raffle.tickets_remaining_count, ticket_count=self._raffle.ticket_count)
        self.progress_bar.value = 1 - self._raffle.tickets_remaining_ratio
        if self._raffle.few_tickets_remaining and not self._few_tickets_remaining:
            self._few_tickets_remaining = uthread2.start_tasklet(self._few_tickets_routine)

    def _on_tickets_sold(self, *args, **kwargs):
        self.buy_button.tickets_sold()
        self._anim_ticket_sold()

    @threadutils.threaded
    def _anim_ticket_sold(self):
        if self._ticket_anim or self._raffle is None or self._raffle.tickets_remaining_count == 0:
            return
        raffle = self._raffle
        if raffle.few_tickets_remaining:
            sound.play(sound.card_ticket_update_urgent, time_offset=0.8)
        else:
            sound.play(sound.card_ticket_update, time_offset=0.8)
        self._ticket_anim = True
        try:
            self.ticket_sweep.sweep()
            uthread2.sleep(1.2)
            if self._raffle != raffle:
                return
            ticket_corner_size = 550 if raffle.few_tickets_remaining else 250
            eveui.animate(self.ticket_corner_effect, 'width', start_value=0, end_value=ticket_corner_size, duration=0.75)
            eveui.animate(self.ticket_corner_effect, 'height', start_value=0, end_value=ticket_corner_size, duration=0.75)
            eveui.fade(self.ticket_corner_effect, start_value=1, end_value=0, duration=0.75)
        finally:
            self._ticket_anim = False

        uthread2.sleep(0.3)
        if self._raffle != raffle:
            return
        eveui.fade(self.tickets_label, start_value=1.0, end_value=TextColor.NORMAL.opacity, duration=2)
        self._update_tickets()

    def _few_tickets_routine(self):
        pulse_duration = 3
        fade_duration = pulse_duration * 0.5
        while not self.destroyed:
            self.progress_bar.pulse(pulse_duration)
            eveui.fade(self.tickets_label, start_value=self.tickets_label.opacity, end_value=1.0, duration=fade_duration)
            uthread2.sleep(fade_duration)
            eveui.fade(self.tickets_label, start_value=self.tickets_label.opacity, end_value=TextColor.NORMAL.opacity, duration=fade_duration)
            uthread2.sleep(fade_duration)
            uthread2.sleep(0.5)

    def _layout(self):
        self._construct_effects()
        self._construct_background()
        self.buy_button = QuickBuyButton(parent=self, align=eveui.Align.bottom_right, top=8, left=8)
        self.content_container = eveui.Container(name='contentContainer', parent=self, padding=PADDING)
        self.state_container = eveui.Container(name='stateContainer', parent=self.content_container)
        self._construct_top()

    def _construct_effects(self):
        self.effects_container = eveui.Container(name='effectsContainer', parent=self, clipChildren=True)
        self.ticket_sweep = SweepEffect(parent=self.effects_container, align=eveui.Align.to_all, texturePath=texture.card_sweep_frame, duration=2, opacity=1, rotation=math.pi * 0.25, color=(0.6, 0.8, 1))

    @eveui.lazy
    def ticket_corner_effect(self):
        container = eveui.Container(parent=self.effects_container, align=eveui.Align.bottom_left, height=1, width=1)
        effect = eveui.GradientSprite(name='cornerEffect', parent=container, align=eveui.Align.center, rgbData=((1.0, (0.6, 0.8, 1)),), alphaData=((0.0, 1.0), (1.0, 0.0)), radial=True, opacity=0, height=0, width=0)
        return effect

    def _construct_background(self):
        self.background_frame = eveui.Frame(bgParent=self, texturePath=texture.panel_2_corner, cornerSize=9, color=(0.15, 0.15, 0.15), opacity=0.3)
        self.corner = eveui.Sprite(parent=self, align=eveui.Align.top_left, texturePath=texture.corner_triangle_small, useSizeFromTexture=True, opacity=0.5)

    def _construct_top(self):
        top_container = eveui.Container(name='topContainer', parent=self.content_container, align=eveui.Align.to_top, height=68, padBottom=PADDING)
        item_icon_container = eveui.Container(parent=top_container, align=eveui.Align.to_left, padRight=8, width=64)
        self._construct_item_icon(item_icon_container)
        label_cont = eveui.ContainerAutoSize(parent=top_container, align=eveui.Align.center_right, width=150, top=-3)
        self.title_label = eveui.EveLabelLarge(parent=label_cont, align=eveui.Align.to_top, maxLines=2, padRight=16)
        self.market_estimate_label = eveui.EveLabelMedium(parent=label_cont, align=eveui.Align.to_top, maxLines=1, color=TextColor.SECONDARY)
        self.location_label = eveui.EveLabelMedium(parent=label_cont, align=eveui.Align.to_top, maxLines=1)
        self.info_icon = InfoIcon(parent=top_container, align=eveui.Align.top_right, opacity=0.0)

    def _construct_item_icon(self, item_icon_container):
        self.item_icon = ItemIcon(parent=item_icon_container, align=eveui.Align.center_top)
        self.item_icon.OnClick = self.OnClick
        self.item_icon.GetDragData = self.GetDragData
        self.item_icon.GetMenu = self.GetMenu

    def _construct_active_bottom(self):
        container = eveui.Container(name='activeContainer', parent=self.state_container, align=eveui.Align.to_bottom, height=36)
        eveui.Frame(bgParent=container, texturePath=texture.panel_1_corner, cornerSize=9, padding=-PADDING, color=(0.0, 0.0, 0.0))
        self.progress_bar = LinearProgress(parent=container, align=eveui.Align.to_top_no_push, padding=(-PADDING,
         -PADDING,
         -PADDING,
         0), value=0.5, color=(1.0, 1.0, 1.0), background_color=(0.3, 0.3, 0.3))
        ticket_price_label = eveui.EveLabelLarge(name='TicketPriceLabel', parent=container, state=eveui.State.normal, align=eveui.Align.to_top, maxLines=1, text=eveformat.isk_readable(self._raffle.ticket_price))
        ticket_price_label.OnClick = self.OnClick
        ticket_price_label.GetMenu = self.GetMenu
        ticket_price_label.PrepareDrag = self.PrepareDrag
        ticket_price_label.GetDragData = self.GetDragData
        ticket_price = eveformat.isk(self._raffle.ticket_price)
        if self._raffle.good_value:
            ticket_price_label.SetTextColor(TextColor.SUCCESS)
            ticket_price_label.SetHint(u'{}\n{}'.format(ticket_price, Text.good_value_hint()))
        elif self._raffle.bad_value:
            ticket_price_label.SetTextColor(TextColor.WARNING)
            ticket_price_label.SetHint(u'{}\n{}'.format(ticket_price, Text.bad_value_hint()))
        else:
            ticket_price_label.SetHint(ticket_price)
        self.tickets_label = eveui.EveLabelMedium(name='TicketsLabel', parent=container, align=eveui.Align.to_top, maxLines=1)

    def _construct_finished_bottom(self):
        if self._raffle.is_expired:
            self._construct_expired()
        else:
            self._construct_finished()

    def _construct_expired(self):
        container = eveui.Container(name='expiredContainer', parent=self.state_container, align=eveui.Align.to_bottom, height=32, padTop=PADDING)
        eveui.Frame(bgParent=container, texturePath=texture.panel_1_corner, cornerSize=9, padding=-PADDING, color=(0.05, 0.05, 0.05))
        eveui.EveLabelMediumBold(parent=container, align=eveui.Align.center_left, text=Text.card_expired())
        eveui.fade(self, end_value=0.5, duration=0.1)

    def _construct_finished(self):
        portrait_container = eveui.Container(name='portraitContainer', parent=self.state_container, align=eveui.Align.bottom_right, height=64, width=64)
        container = eveui.Container(name='finishedContainer', parent=self.state_container, align=eveui.Align.to_bottom, height=32, padTop=PADDING)
        eveui.GradientSprite(bgParent=container, align=eveui.Align.to_all, alphaData=[(0, 1.0), (1, 0)], rgbData=[(0, (0.9, 0.9, 0.9)), (1, (0.7, 0.7, 0.7))], rotation=-math.pi * 0.5, padding=-PADDING)
        eveui.Frame(bgParent=container, texturePath=texture.panel_1_corner, cornerSize=9, color=(0.7, 0.7, 0.7), padding=-PADDING)
        top_label = eveui.EveLabelMedium(parent=container, align=eveui.Align.to_top, color=(0.2, 0.2, 0.2))
        bottom_label_container = eveui.Container(parent=container, align=eveui.Align.to_bottom, height=18)
        bottom_label = self.winner_label = eveui.EveLabelLargeBold(parent=bottom_label_container, maxLines=1, color=(0, 0, 0))
        if self._raffle.is_winner_unseen:
            top_label.text = Text.card_completed()
            bottom_label.text = Text.card_show_winner()
            self._sweep_effect = SweepEffect(parent=self.effects_container, align=eveui.Align.to_all, on_start=functools.partial(sound.play, sound.card_sweep))
            self._sweep_effect.sweep(loop=True)
        else:
            eveui.CharacterPortrait(parent=portrait_container, textureSecondaryPath=texture.portrait_mask, spriteEffect=trinity.TR2_SFX_MASK, blendMode=trinity.TR2_SBM_BLEND, character_id=self._raffle.winner_id)
            eveui.Frame(parent=portrait_container, align=eveui.Align.to_all, texturePath=texture.frame_1_corner, cornerSize=9, padding=-1, color=(0.5, 0.5, 0.5))
            top_label.text = Text.card_winner()
            bottom_label.text = character_name(self._raffle.winner_id)
            bottom_label.SetRightAlphaFade(160, 10)
            bottom_label.state = eveui.State.normal
