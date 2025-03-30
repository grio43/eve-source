#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pvpFilaments\client\event_window\window.py
import math
import threadutils
from carbon.common.script.util.format import FmtDate
import eveui
from carbonui.control.button import Button
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from carbonui.control.section import Section, SectionAutoSize
from localization import GetByLabel
from .controller import PVPFilamentEventInfoController
from .leaderboard import Leaderboard
from .character_statistics import CharacterStatistics
from .reward_icon import RewardIcon

class PVPFilamentEventWindow(eveui.Window):
    default_name = 'PVPFilamentEventWindow'
    default_windowID = 'PVPFilamentEventWindow'
    default_fixedWidth = 912
    default_fixedHeight = 544
    default_isStackable = False
    default_captionLabelPath = 'UI/PVPFilament/EventWindow/WindowTitle'
    default_descriptionLabelPath = 'UI/PVPFilament/EventWindow/WindowDescription'
    default_iconNum = 'res:/ui/Texture/WindowIcons/provingGrounds.png'

    @classmethod
    def Open(cls, *args, **kwargs):
        window = cls.GetIfOpen()
        if not window:
            return cls(**kwargs)
        filament_type_id = kwargs.get('filament_type_id', None)
        if not filament_type_id or filament_type_id == window._controller.filament_type_id:
            window.Maximize()
            return window
        window.CloseByUser()
        return cls(**kwargs)

    def Close(self, *args, **kwds):
        super(PVPFilamentEventWindow, self).Close(*args, **kwds)
        self._unsubscribe()

    def ApplyAttributes(self, attributes):
        super(PVPFilamentEventWindow, self).ApplyAttributes(attributes)
        self._controller = PVPFilamentEventInfoController(attributes.get('filament_type_id', None))
        if self._controller.is_any_event_active or self._controller.is_qa_filament:
            self._layout()
            self._init_data()
        elif self._controller.data_valid:
            self._past_event_window()
            self._init_data()
        else:
            self._inactive_window()
        self._subscribe()

    @threadutils.threaded
    def _init_data(self):
        self._on_character_statistics_changed()
        self._on_leaderboard_changed()

    def _subscribe(self):
        sm.GetService('pvpFilamentSvc').onCharacterStatisticsChanged.connect(self._on_character_statistics_changed)
        sm.GetService('pvpFilamentSvc').onLeaderboardChanged.connect(self._on_leaderboard_changed)

    def _unsubscribe(self):
        sm.GetService('pvpFilamentSvc').onCharacterStatisticsChanged.disconnect(self._on_character_statistics_changed)
        sm.GetService('pvpFilamentSvc').onLeaderboardChanged.disconnect(self._on_leaderboard_changed)

    def _on_character_statistics_changed(self):
        self._character_statistics.update_statistics(self._controller.character_statistics)

    def _on_leaderboard_changed(self):
        self._leaderboard.update_entries(self._controller.leaderboard)

    def _layout(self):
        container = eveui.Container(parent=self.GetMainArea(), align=eveui.Align.to_all)
        self._construct_left_side(container)
        self._construct_right_side(container)

    def _construct_right_side(self, parent):
        container = eveui.Container(parent=parent, align=eveui.Align.to_left, width=376)
        stats_container = SectionAutoSize(parent=container, align=eveui.Align.to_top, padBottom=8, headerText=GetByLabel('UI/PVPFilament/EventWindow/YourStatistics'))
        self._character_statistics = CharacterStatistics(parent=stats_container, align=eveui.Align.to_top)
        leaderboard_container = Section(parent=container, align=eveui.Align.to_all, headerText=GetByLabel('UI/PVPFilament/EventWindow/Leaderboard'))
        self._leaderboard = Leaderboard(parent=leaderboard_container, align=eveui.Align.to_all)

    def _construct_left_side(self, parent):
        wrapper = eveui.Container(parent=parent, align=eveui.Align.to_left, width=504)
        eveui.GradientSprite(bgParent=wrapper, rotation=-math.pi / 2, rgbData=((0, (0.0, 0.0, 0.0)), (1.0, (0.0, 0.0, 0.0))), alphaData=((0.0, 0.8), (0.5, 0)))
        eveui.Sprite(bgParent=wrapper, opacity=0.8, texturePath='res:/UI/Texture/classes/ProvingGrounds/event_window_bg.png')
        container = eveui.Container(parent=wrapper, align=eveui.Align.to_all, padding=8)
        self._construct_rewards(container)
        self._construct_filament(container)
        self._construct_event_info(container)

    def _construct_event_info(self, parent):
        container = eveui.Container(parent=parent, align=eveui.Align.to_all)
        eveui.Sprite(state=eveui.State.normal, parent=container, align=eveui.Align.top_left, height=64, width=64, texturePath=self.default_iconNum)
        eveui.EveCaptionMedium(parent=container, align=eveui.Align.to_top, top=4, left=76, text=self._controller.event_title, color=(1, 1, 1, 1))
        eveui.EveLabelLarge(parent=container, align=eveui.Align.to_top, left=76, padTop=4, text=u'{} - {}'.format(FmtDate(self._controller.event_start_date, 'ln'), FmtDate(self._controller.event_end_date, 'ln')))
        descriptionContainer = eveui.ScrollContainer(parent=container, align=eveui.Align.to_all, padTop=12)
        eveui.EveLabelLarge(parent=descriptionContainer, align=eveui.Align.to_top, text=self._controller.event_description)

    def _construct_filament(self, parent):
        wrapper = eveui.Container(parent=parent, align=eveui.Align.to_bottom, height=80, bgColor=(0, 0, 0, 0.6))
        container = eveui.Container(parent=wrapper, align=eveui.Align.to_all, padding=8)
        eveui.EveLabelLargeBold(parent=parent, align=eveui.Align.to_bottom, padBottom=4, padTop=8, text=GetByLabel('UI/PVPFilament/EventWindow/Filament'))
        ItemIcon(parent=container, align=eveui.Align.to_left, width=64, padRight=12, typeID=self._controller.filament_type_id)
        filamentName = eveui.EveLabelLarge(parent=container, align=eveui.Align.to_top, top=4, text=self._controller.filament_name, singleline=True)
        filamentName.SetRightAlphaFade(fadeEnd=320, maxFadeWidth=100)
        Button(parent=container, align=eveui.Align.center_left, left=76, top=12, label=GetByLabel('UI/PVPFilament/EventWindow/OpenMarket'), func=self._controller.open_market)
        DescriptionIconLabel(parent=container, align=eveui.Align.top_right, alignText=eveui.Align.to_right, text=GetByLabel('UI/PVPFilament/EventWindow/Rules'), hint=self._controller.rules_hint)
        DescriptionIconLabel(parent=container, align=eveui.Align.bottom_right, alignText=eveui.Align.to_right, text=GetByLabel('UI/PVPFilament/EventWindow/ShipRestrictions'), hint=self._controller.ship_restrictions_hint)

    def _construct_rewards(self, parent):
        rewards = self._controller.event_rewards
        wrapper = eveui.Container(parent=parent, align=eveui.Align.to_bottom, height=168, bgColor=(0, 0, 0, 0.6))
        container = eveui.Container(parent=wrapper, align=eveui.Align.to_all, padding=8)
        eveui.EveLabelLargeBold(parent=parent, align=eveui.Align.to_bottom, padBottom=4, padTop=8, text=GetByLabel('UI/PVPFilament/EventWindow/Rewards'))
        if not len(rewards):
            rows = 1
        else:
            rows = math.ceil(len(rewards) / 5.0)
        columns = math.ceil(len(rewards) / float(rows))
        rewards_container = eveui.FlowContainer(parent=container, align=eveui.Align.center, height=52 * rows + 24 * (rows - 1), width=52 * columns + 30 * (columns - 1) + 2, contentSpacing=(30, 24))
        for reward in rewards:
            RewardIcon(parent=rewards_container, align=eveui.Align.no_align, padRight=6, reward=reward)

        DescriptionIconLabel(parent=container, align=eveui.Align.bottom_right, left=-7, hint=self._controller.rewards_hint)

    def _past_event_window(self):
        container = eveui.Container(parent=self.GetMainArea(), align=eveui.Align.to_all, padding=(12, 12, 12, 20))
        self._construct_past_event_left_side(container)
        self._construct_right_side(container)

    def _construct_past_event_left_side(self, parent):
        wrapper = eveui.Container(parent=parent, align=eveui.Align.to_left, width=504)
        container = eveui.ContainerAutoSize(parent=wrapper, align=eveui.Align.center, width=450)
        eveui.Sprite(parent=eveui.Container(parent=container, align=eveui.Align.to_top, height=64, width=64), align=eveui.Align.center, height=64, width=64, texturePath=self.default_iconNum)
        eveui.EveCaptionLarge(parent=container, align=eveui.Align.to_top, text=u'<center>{}</center>'.format(GetByLabel('UI/PVPFilament/EventWindow/FinalResults')))
        eveui.EveCaptionLarge(parent=container, align=eveui.Align.to_top, text=u'<center>{}</center>'.format(self._controller.event_title))
        eveui.EveCaptionLarge(parent=container, align=eveui.Align.to_top, padTop=20, text=u'<center>{}</center>'.format(GetByLabel('UI/PVPFilament/EventWindow/InactiveWindowWithDate')))
        eveui.EveCaptionLarge(parent=container, align=eveui.Align.to_top, text=u'<center>{}</center>'.format(self._controller.next_event_date))

    def _inactive_window(self):
        eveui.EveCaptionLarge(parent=self.GetMainArea(), align=eveui.Align.center, text=GetByLabel('UI/PVPFilament/EventWindow/InactiveWindow'))
        eveui.Sprite(parent=self.GetMainArea(), align=eveui.Align.center, top=-60, height=64, width=64, texturePath=self.default_iconNum)
