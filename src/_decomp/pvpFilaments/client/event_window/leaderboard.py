#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pvpFilaments\client\event_window\leaderboard.py
import threadutils
import eveui
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from localization import GetByLabel
from raffles.client.widget.virtual_list import VirtualList

class Leaderboard(eveui.Container):

    def __init__(self, **kwargs):
        super(Leaderboard, self).__init__(**kwargs)
        self._loading_wheel = None
        self._layout()

    def update_entries(self, entries):
        if self.destroyed:
            return
        if entries is None:
            self._show_loading()
            return
        self._hide_loading()
        self.list.data = entries

    def _layout(self):
        self.list = VirtualList(parent=self, align=eveui.Align.to_all, pushContent=True, render_item=self._render_list_item)

    def _render_list_item(self):
        return LeaderboardListItem()

    def _show_loading(self):
        if self._loading_wheel:
            return
        self._loading_wheel = LoadingWheel(parent=self, align=eveui.Align.center)

    def _hide_loading(self):
        if not self._loading_wheel:
            return
        self._loading_wheel.Hide()
        self._loading_wheel = None


class LeaderboardListItem(eveui.Container):
    default_align = eveui.Align.to_top
    default_state = eveui.State.hidden
    default_height = 48
    default_padBottom = 6

    def __init__(self, **kwargs):
        super(LeaderboardListItem, self).__init__(**kwargs)
        self._score_info = None
        self._layout()

    def update_item(self, score_info):
        if self._score_info is score_info:
            return
        self._score_info = score_info
        self._update_item()

    @threadutils.threaded
    def _update_item(self):
        if self._score_info is None:
            self.state = eveui.State.hidden
            return
        rank = self._score_info['rank']
        if rank < 4:
            self._frame.color = (0.83, 0.69, 0.22, 0.2)
        else:
            self._frame.color = (1, 1, 1, 0.07)
        self.state = eveui.State.normal
        eveui.fade_out(self._hover_fill, duration=0)
        character_id = self._score_info['character_id']
        character_info = cfg.eveowners.Get(character_id)
        self._character_name.text = character_info.name
        self._portrait.character_id = character_id
        self._score.text = GetByLabel('UI/PVPFilament/EventWindow/NumWins', wins=self._score_info['wins'])
        self._rank.text = rank
        self.OnClick = self._portrait.OnClick
        self.GetMenu = self._portrait.GetMenu

    def OnMouseEnter(self, *args):
        eveui.Sound.button_click.play()
        eveui.fade(self._hover_fill, end_value=0.1, duration=0.1)

    def OnMouseExit(self):
        eveui.fade_out(self._hover_fill, duration=0.3)

    def _layout(self):
        eveui.Sprite(bgParent=self, texturePath='res:/UI/Texture/classes/ProvingGrounds/leaderboard_card_border.png')
        self._hover_fill = eveui.Frame(bgParent=self, opacity=0, cornerSize=9, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png')
        self._frame = eveui.Frame(bgParent=self, cornerSize=9, opacity=0.07, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png')
        container = eveui.Container(parent=self, padding=8)
        self._portrait = eveui.CharacterPortrait(parent=container, align=eveui.Align.to_left, size=32)
        text_container = eveui.Container(parent=container, align=eveui.Align.to_all, padding=8)
        self._character_name = eveui.EveLabelMedium(parent=text_container, align=eveui.Align.center_left)
        self._rank = eveui.EveLabelMedium(parent=text_container, align=eveui.Align.center, left=133)
        self._score = eveui.EveLabelMedium(parent=text_container, align=eveui.Align.center_right, left=60)
