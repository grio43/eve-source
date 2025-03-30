#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\history\banner.py
import eveui
from raffles.client import texture
from raffles.client.localization import Text

class Banner(eveui.Container):
    default_align = eveui.Align.to_top
    default_height = 127

    def __init__(self, stats, **kwargs):
        super(Banner, self).__init__(**kwargs)
        self._stats = stats
        self._layout_done = False
        self._loading_indicator = None
        stats.on_change.connect(self._on_stats_changed)
        self._layout()

    def Close(self):
        super(Banner, self).Close()
        self._stats.on_change.disconnect(self._on_stats_changed)

    def _on_stats_changed(self, stats):
        if not self._layout_done:
            return
        self._update_stat_labels()
        if self._stats.fetch_complete:
            self._hide_loading_indicator()

    def _update_stat_labels(self):
        self.created_label.text = Text.created(amount=self._stats.created)
        self.created_completed_label.text = Text.completed(amount=self._stats.created_completed)
        self.created_active_label.text = Text.active(amount=self._stats.created_active)
        self.joined_label.text = Text.joined(amount=self._stats.joined)
        self.joined_won_label.text = Text.won(amount=self._stats.joined_won)
        self.joined_active_label.text = Text.active(amount=self._stats.joined_active)

    def _layout(self):
        self._construct_portrait()
        self._construct_created_statistics()
        self._construct_joined_statistics()
        self._construct_loading_indicator()
        self._construct_background()
        self._update_stat_labels()
        self._layout_done = True
        if self._stats.fetch_complete:
            self._hide_loading_indicator()

    def _construct_loading_indicator(self):
        if self._stats.fetch_complete:
            return
        self._loading_indicator = eveui.DottedProgress(parent=self, align=eveui.Align.center, dot_size=5, opacity=0.0)
        eveui.fade_in(self._loading_indicator, end_value=0.5, duration=0.5)

    def _hide_loading_indicator(self):
        if self._loading_indicator:
            indicator = self._loading_indicator
            self._loading_indicator = None
            eveui.fade_out(indicator, duration=0.2, on_complete=indicator.Close)
        eveui.fade_in(self._created_statistics_container, duration=0.3)
        eveui.fade_in(self._joined_statistics_container, duration=0.3)

    def _construct_background(self):
        eveui.Sprite(parent=self, align=eveui.Align.center, width=882, height=127, texturePath=texture.banner_frame, color=(0, 0, 0, 0.2))

    def _construct_portrait(self):
        portrait_container = eveui.Container(parent=self, align=eveui.Align.center_left, height=84, width=84, left=150)
        self.portrait = eveui.CharacterPortrait(parent=portrait_container, align=eveui.Align.center, size=84, character_id=session.charid)
        eveui.Frame(parent=portrait_container, padding=-1, opacity=0.25)

    def _construct_created_statistics(self):
        self._created_statistics_container = eveui.Container(parent=self, align=eveui.Align.center_left, height=56, width=250, left=400, opacity=0.0)
        sprite_container = eveui.Container(parent=self._created_statistics_container, align=eveui.Align.to_left, width=24)
        eveui.Sprite(parent=sprite_container, align=eveui.Align.top_left, height=16, width=16, texturePath=texture.created_icon, opacity=0.75)
        text_container = eveui.Container(parent=self._created_statistics_container, align=eveui.Align.to_left, width=200)
        self.created_label = eveui.EveLabelMedium(parent=text_container, align=eveui.Align.to_top)
        self.created_completed_label = eveui.EveLabelMedium(parent=text_container, align=eveui.Align.to_top, top=4)
        self.created_active_label = eveui.EveLabelMedium(parent=text_container, align=eveui.Align.to_top, top=4)

    def _construct_joined_statistics(self):
        self._joined_statistics_container = eveui.Container(parent=self, align=eveui.Align.center_left, height=56, width=250, left=650, opacity=0.0)
        sprite_container = eveui.Container(parent=self._joined_statistics_container, align=eveui.Align.to_left, width=24)
        eveui.Sprite(parent=sprite_container, align=eveui.Align.top_left, height=12, width=12, top=1, texturePath=texture.tickets_icon)
        text_container = eveui.Container(parent=self._joined_statistics_container)
        self.joined_label = eveui.EveLabelMedium(parent=text_container, align=eveui.Align.to_top)
        self.joined_won_label = eveui.EveLabelMedium(parent=text_container, align=eveui.Align.to_top, top=4)
        self.joined_active_label = eveui.EveLabelMedium(parent=text_container, align=eveui.Align.to_top, top=4)
