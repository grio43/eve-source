#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pvpFilaments\client\event_window\character_statistics.py
import eveui
import eveformat
from localization import GetByLabel

class CharacterStatistics(eveui.Container):
    default_height = 72

    def __init__(self, **kwargs):
        super(CharacterStatistics, self).__init__(**kwargs)
        self._layout()

    def update_statistics(self, stats):
        if self.destroyed:
            return
        if not stats:
            return
        if not stats['rank']:
            return
        self._rank.set_value(stats['rank'])
        self._wins.set_value(stats['wins'])
        self._losses.set_value(stats['losses'])
        self._draws.set_value(stats['draws'])

    def _layout(self):
        eveui.CharacterPortrait(parent=self, align=eveui.Align.to_left, padRight=12, size=72, character_id=session.charid)
        character_info = cfg.eveowners.Get(session.charid)
        eveui.EveLabelLarge(parent=self, align=eveui.Align.to_top, text=character_info.name, padBottom=8)
        self._rank = StatisticContainer(parent=self, label=GetByLabel('UI/PVPFilament/EventWindow/Rank'))
        self._wins = StatisticContainer(parent=self, label=GetByLabel('UI/PVPFilament/EventWindow/Wins'), color=(0.13, 0.59, 0.33, 0.25))
        self._losses = StatisticContainer(parent=self, label=GetByLabel('UI/PVPFilament/EventWindow/Losses'), color=(0.87, 0.1, 0.14, 0.25))
        self._draws = StatisticContainer(parent=self, label=GetByLabel('UI/PVPFilament/EventWindow/Draws'), color=(1, 0.7, 0, 0.25))


class StatisticContainer(eveui.Container):
    default_align = eveui.Align.to_left
    default_height = 48
    default_width = 62
    default_padRight = 8

    def __init__(self, label, value = '-', color = (1, 1, 1, 0.25), **kwargs):
        super(StatisticContainer, self).__init__(**kwargs)
        eveui.StretchSpriteVertical(parent=self, align=eveui.Align.to_right_no_push, width=11, bottomEdgeSize=6, opacity=0.2, texturePath='res:/UI/Texture/Shared/DarkStyle/edgeDecoRight.png')
        top_container = eveui.Container(parent=self, align=eveui.Align.to_top, height=16, bgColor=color)
        eveui.EveLabelMedium(parent=top_container, align=eveui.Align.center, text=label)
        bot_container = eveui.Container(parent=self, align=eveui.Align.to_all)
        self._value_label = eveui.EveLabelMedium(parent=bot_container, align=eveui.Align.center, text=value)
        eveui.Frame(bgParent=bot_container, cornerSize=9, opacity=0.05, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png')

    def set_value(self, value):
        self._value_label.text = eveformat.number(value, 0)
