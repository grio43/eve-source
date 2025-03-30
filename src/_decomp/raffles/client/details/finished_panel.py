#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\finished_panel.py
import logging
import math
import eveformat.client
import eveui
import threadutils
from carbonui import TextColor
import raffles
from raffles.client import texture
from raffles.client.details.fanfare import FanfarePanel
from raffles.client.details.info_panel import InfoPanel
from raffles.client.details.ticket_owners import TicketOwners
from raffles.client.localization import Text
from raffles.client.raffle_card.card import RaffleCard
from raffles.client.util import character_name, station_name
log = logging.getLogger(__name__)

class FinishedPanel(eveui.Container):
    default_name = 'FinishedPanel'

    def __init__(self, raffle, controller, navigation, **kwargs):
        super(FinishedPanel, self).__init__(**kwargs)
        self._raffle = raffle
        self._controller = controller
        self._navigation = navigation
        self._view_same_type = False
        self.result_container = eveui.Container(parent=self, align=eveui.Align.to_all, opacity=0)
        if self._raffle.is_winner_unseen:
            self._show_fanfare()
        else:
            self._show_winner()

    def _handle_view_more(self, *args):
        if self._view_same_type:
            type_id = self._raffle.type_id
        else:
            type_id = -1
        self._navigation.open_browse_page(type_id)

    def _handle_claim_reward(self, *args):
        self._construct_claim_prize_progress()
        try:
            self._controller.claim_reward(self._raffle)
        except Exception:
            log.exception('Failed to claim raffle reward')
            self._construct_claim_prize_failed()
        else:
            self._construct_prize_claimed()
            eveui.fade_in(self.claim_prize_container, duration=0.3)

    def _show_fanfare(self):
        FanfarePanel(parent=self, raffle=self._raffle, on_finish=self._fanfare_finished)

    def _fanfare_finished(self):
        self._show_winner()

    @threadutils.threaded
    def _show_winner(self):
        self._construct_result()
        eveui.fade_in(self.result_container, duration=1)
        eveui.fade_in(self.winner_container, duration=0.5)
        eveui.fade_in(self.winner_label_container, duration=1)
        eveui.fade_in(self.winner_frame, duration=0.3)
        if self._raffle.is_raffle_winner:
            eveui.fade_in(self.claim_prize_container, duration=1)
        eveui.fade_in(self.similar_raffles_container, duration=1)

    @eveui.lazy
    def main_container(self):
        return eveui.Container(parent=self.result_container)

    @eveui.lazy
    def content_container(self):
        return eveui.Container(parent=self.main_container, padding=16)

    def _construct_result(self):
        InfoPanel(parent=self.result_container, raffle=self._raffle)
        TicketOwners(parent=self.main_container, raffle=self._raffle)
        self._construct_winner()
        if self._raffle.is_raffle_winner:
            if self._raffle.is_unclaimed:
                self._construct_claim_prize()
            else:
                self._construct_prize_claimed()
        self._construct_similar_raffles(self.content_container)
        self._construct_frame(self.main_container)

    def _construct_frame(self, parent):
        eveui.StretchSpriteVertical(parent=parent, state=eveui.State.disabled, align=eveui.Align.to_all, texturePath=texture.banner_frame, topEdgeSize=20, bottomEdgeSize=20, color=(0, 0, 0, 0.5), padding=(0, 4, 0, 4))
        top_container = eveui.Container(parent=parent, state=eveui.State.disabled, align=eveui.Align.to_top_no_push, height=5, pacity=1.5)
        eveui.StretchSpriteHorizontal(parent=top_container, align=eveui.Align.to_all, texturePath=texture.content_frame, rightEdgeSize=5, leftEdgeSize=5)
        eveui.StretchSpriteHorizontal(parent=top_container, align=eveui.Align.center_bottom, texturePath=texture.content_frame_middle, width=252, height=4, rightEdgeSize=5, leftEdgeSize=5)
        bot_container = eveui.Transform(parent=parent, state=eveui.State.disabled, align=eveui.Align.to_bottom_no_push, height=5, rotation=math.pi, pacity=1.5, top=1)
        eveui.StretchSpriteHorizontal(parent=bot_container, align=eveui.Align.to_all, texturePath=texture.content_frame, rightEdgeSize=5, leftEdgeSize=5)
        eveui.StretchSpriteHorizontal(parent=bot_container, align=eveui.Align.center_bottom, texturePath=texture.content_frame_middle, width=252, height=4, rightEdgeSize=5, leftEdgeSize=5)

    def _construct_winner(self):
        container = eveui.Container(parent=self.content_container, align=eveui.Align.center, width=698, height=127, top=-100)
        self._construct_player(container)
        self._construct_winning_ticket(container)
        self.winner_frame = eveui.Container(parent=container, state=eveui.State.disabled, align=eveui.Align.to_all)
        if self._raffle.is_raffle_winner:
            stroke_color = (0.83, 0.69, 0.22, 0.7)
            frame_color = (0.83, 0.69, 0.22, 0.05)
        else:
            stroke_color = (0.5, 0.5, 0.5, 0.8)
            frame_color = (0.2, 0.2, 0.2, 0.1)
        eveui.Sprite(parent=self.winner_frame, align=eveui.Align.to_all, texturePath=texture.banner_frame_stroke, color=stroke_color)
        eveui.Sprite(parent=self.winner_frame, align=eveui.Align.to_all, texturePath=texture.banner_frame, color=frame_color)

    def _construct_player(self, parent):
        winner_id = self._raffle.winner_id
        self.winner_container = container = eveui.Container(parent=parent, align=eveui.Align.center_left, width=350, height=84, left=70, opacity=0)
        portrait_container = eveui.Container(parent=container, align=eveui.Align.to_left, width=84)
        eveui.Frame(parent=portrait_container, padding=-1, color=(1, 1, 1, 0.25))
        eveui.CharacterPortrait(parent=portrait_container, size=84, character_id=winner_id)
        self.winner_label_container = label_container = eveui.Container(parent=container, left=30, opacity=0, clipChildren=True)
        eveui.EveCaptionMedium(parent=label_container, align=eveui.Align.center_left, top=-10, state=eveui.State.normal, text=character_name(winner_id, linkify=True), opacity=0.75, autoFadeSides=10)
        owned_tickets_container = eveui.Container(parent=label_container, align=eveui.Align.center_left, top=14, height=14, width=200)
        eveui.Sprite(parent=owned_tickets_container, align=eveui.Align.center_left, height=10, width=10, texturePath=texture.tickets_icon)
        eveui.EveLabelMedium(parent=owned_tickets_container, align=eveui.Align.center_left, left=12, color=TextColor.SECONDARY, text=Text.owned_tickets(owned_ticket_count=self._raffle.ticket_count_owned_by(winner_id)))

    def _construct_winning_ticket(self, parent):
        self.winning_ticket = container = eveui.Container(parent=parent, align=eveui.Align.center_right, left=100, width=160, height=39)
        if self._raffle.is_raffle_winner:
            frame_color = (0.5, 0.4, 0.13, 0.8)
        else:
            frame_color = (0.2, 0.2, 0.2, 0.8)
        eveui.Frame(bgParent=container, texturePath=texture.panel_2_corner, cornerSize=9, color=frame_color)
        hash_container = eveui.Container(parent=container, padding=2)
        winning_hash = self._raffle.get_ticket_display_hash(self._raffle.winning_ticket.number)
        for i in range(4):
            character = eveui.Container(parent=hash_container, align=eveui.Align.to_left, width=35, padding=2)
            eveui.Frame(bgParent=character, texturePath=texture.panel_2_corner, cornerSize=9, color=(0.9, 0.9, 0.9, 0.1))
            eveui.Label(parent=character, align=eveui.Align.center, fontsize=24, fontStyle=eveui.FontStyle.condensed, opacity=1, text=winning_hash[i])

    @eveui.lazy
    def claim_prize_container(self):
        return eveui.Container(parent=self.content_container, align=eveui.Align.center, height=56, width=720, opacity=0)

    def _construct_claim_prize(self):
        self.claim_prize_container.Flush()
        arrow = eveui.Sprite(parent=self.claim_prize_container, align=eveui.Align.center_top, height=14, width=25, texturePath=texture.fanfare_arrow, color=(0.5, 0.4, 0.13, 0.8))
        eveui.fade(arrow, start_value=0.6, end_value=1, duration=1, loops=-1, curve_type=eveui.CurveType.wave)
        eveui.Button(parent=self.claim_prize_container, align=eveui.Align.center_bottom, label=Text.claim_reward(), func=self._handle_claim_reward)

    def _construct_claim_prize_progress(self):
        self.claim_prize_container.Flush()
        eveui.Sprite(parent=self.claim_prize_container, align=eveui.Align.center_top, height=14, width=25, texturePath=texture.fanfare_arrow, color=(0.5, 0.4, 0.13, 0.8))
        eveui.DottedProgress(parent=self.claim_prize_container, align=eveui.Align.center, top=12, dot_size=5, opacity=0.5)

    def _construct_prize_claimed(self):
        self.claim_prize_container.Flush()
        eveui.Sprite(parent=self.claim_prize_container, align=eveui.Align.center_top, height=14, width=25, texturePath=texture.fanfare_arrow, color=(0.5, 0.4, 0.13, 0.8))
        eveui.EveLabelMedium(parent=self.claim_prize_container, align=eveui.Align.to_bottom, state=eveui.State.normal, text=eveformat.center(station_name(self._raffle.location_id, linkify=True)), maxWidth=720)
        eveui.EveLabelMedium(parent=self.claim_prize_container, align=eveui.Align.to_bottom, text=eveformat.center(Text.reward_claimed(item_name=self._raffle.item_name)), maxWidth=720)

    def _construct_claim_prize_failed(self):
        self.claim_prize_container.Flush()
        eveui.EveLabelMedium(parent=self.claim_prize_container, align=eveui.Align.center, text=eveformat.center(Text.reward_claim_failed()), color=TextColor.WARNING, width=720)

    def _construct_similar_raffles(self, parent):
        self.similar_raffles_container = container = eveui.Container(name='similarRafflesContainer', parent=parent, align=eveui.Align.center_bottom, height=172, width=753, opacity=0)
        eveui.EveLabelMediumBold(parent=container, align=eveui.Align.top_left, width=200, top=8, left=8, text=Text.similar_raffles())
        eveui.Button(parent=container, align=eveui.Align.top_right, left=8, label=Text.view_more(), func=self._handle_view_more)
        raffle_count = 3
        try:
            similar_raffles = self._controller.get_similar_raffles(self._raffle, raffle_count)
        except raffles.RafflesError:
            similar_raffles = []

        cards_container = eveui.GridContainer(parent=container, align=eveui.Align.center_bottom, height=140, width=753)
        for i in range(raffle_count):
            if i < len(similar_raffles):
                card = RaffleCard(navigation=self._navigation, parent=cards_container, padding=8)
                card.turn_on(similar_raffles[i])
            else:
                eveui.Frame(parent=cards_container, texturePath=texture.panel_1_corner, cornerSize=9, padding=8, color=(0, 0, 0, 0.35))

        self._view_same_type = len(similar_raffles) > 0 and similar_raffles[0].type_id == self._raffle.type_id
