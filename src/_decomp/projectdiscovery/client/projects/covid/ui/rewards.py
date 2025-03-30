#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\rewards.py
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelMediumBold, Label
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from evetypes import GetName, GetCategoryID
from inventorycommon.const import categoryBlueprint, categoryShipSkin
from localization import GetByLabel
from projectdiscovery.client.projects.covid.ui.results import BIG_GAUGE_LINE_WIDTH, BIG_GAUGE_SIZE, COLOR_BACKGROUND_GAUGE, COLOR_BACKGROUND_PROGRESS_LABEL, COLOR_TEXT, GAUGE_ANIMATION_DURATION, PADDING_CONTAINER_TO_LABEL
from carbonui.fontconst import STYLE_HEADER
from projectdiscovery.client import const
from projectdiscovery.client.projects.covid.sounds import Sounds
from projectdiscovery.client.projects.covid.ui.containerwithcorners import ContainerWithCorners
from projectdiscovery.client.util.util import calculate_rank_band
from projectdiscovery.common.const import TIERS, NEEDED_LEVEL_FOR_SUPERIOR_CRATES, LOOT_CRATE_TYPE_ID, SUPERIOR_LOOT_CRATE_TYPE_ID
import trinity
from uthread2 import StartTasklet
from utillib import KeyVal
LINE_COLOR = (1.0,
 1.0,
 1.0,
 1.0)
SECTION_HEADER_BACKGROUND_COLOR = (1.0,
 1.0,
 1.0,
 0.97)
SECTION_HEADER_LABEL_COLOR = (0.0,
 0.0,
 0.0,
 1.0)
SCROLL_COLOR = (0.063,
 0.69,
 0.937,
 0.2)
COLOR_BACKGROUND_BLUE = COLOR_BACKGROUND_PROGRESS_LABEL
ARROW_SIZE = 48
LINE_HEIGHT = 5
FONTSIZE_BIG_GAUGE_DESCRIPTION = 18
FONTSIZE_BIG_GAUGE_EXPERIENCE = 32
FONTSIZE_BIG_GAUGE_NEW_RANK = 24
FONTSIZE_TEXT_RANK = 36
MILESTONE_REWARD_ICON_SIZE = 128
NEXT_REWARD_SIZE = 128
RANK_ICON_SIZE = 64
SPACE_BETWEEN_ARROW_AND_REWARD = 15
SECTION_HEADER_HEIGHT = 19
UPCOMING_REWARD_SIZE = 75
PADDING_BETWEEN_LABELS_LEVEL = 5
PADDING_BIG_GAUGE_NEW_RANK_TOP = 50
PADDING_INNER = 10
PADDING_LABELS_BIG_GAUGE_TOP = -5
PADDING_LABELS_CURRENT_REWARD_TOP = -20
PADDING_MILESTONE_LABELS = 25
PADDING_OUTER = 20
PADDING_SECTION_LABEL = 7
PADDING_SECTION_TOP = 40
CRATE_REWARD_ICON_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/reward.png'
ARROW_BETWEEN_REWARDS_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/icon_arrow.png'
SECTION_HEADER_LABEL_END_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/icon_label_end_2.png'
LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Rewards/'
LABELS_FOLDER_RANK_TITLES = 'UI/ProjectDiscovery/Covid/RankTitles/'
LABEL_PATH_CLAIM_IN_REDEEM = LABELS_FOLDER + 'ClaimInRedeem'
LABEL_PATH_EXPERIENCE = LABELS_FOLDER + 'Experience'
LABEL_PATH_LEVEL = LABELS_FOLDER + 'Level'
LABEL_PATH_MILESTONE_SKIN_ICON = 'res:/UI/Texture/classes/skins/icons/2531_128.png'
LABEL_PATH_NEW_RANK_REACHED = LABELS_FOLDER + 'NewRankReached'
LABEL_PATH_RANK = LABELS_FOLDER + 'Rank'
LABEL_PATH_RANK_PROGRESS = LABELS_FOLDER + 'RankProgress'
LABEL_PATH_RANK_TITLES = LABELS_FOLDER_RANK_TITLES + 'RankTitle'
LABEL_PATH_REDEEM_ITEMS = 'UI/RedeemWindow/RedeemItem'
LABEL_PATH_REWARD = LABELS_FOLDER + 'Reward'
LABEL_PATH_UNLOCKED_REWARD = LABELS_FOLDER + 'UnlockedReward'
LABEL_PATH_UNLOCKED_REWARD_COOL = LABELS_FOLDER + 'UnlockedRewardCool'
LABEL_PATH_UNLOCK_REWARD_IN_REDEEM = LABELS_FOLDER + 'UnlockRewardInRedeem'
LABEL_PATH_UPCOMING_REWARDS = LABELS_FOLDER + 'UpcomingRewards'
REDEEM_WINDOW_URL = '<url=localsvc:method=ShowRedeemUI><b><color=%(color)s>%(redeem)s</b></color></url>' % {'color': Color(*COLOR_TEXT).GetHex(),
 'redeem': GetByLabel(LABEL_PATH_REDEEM_ITEMS)}

def show_info(type_id):
    sm.GetService('info').ShowInfo(typeID=type_id, abstractinfo=get_abstract_info(type_id))


def get_abstract_info(type_id):
    if GetCategoryID(type_id) != categoryBlueprint:
        return None
    blueprint_service = sm.GetService('blueprintSvc')
    blueprint_data = blueprint_service.GetBlueprintTypeCopy(type_id, original=False, runsRemaining=1)
    return KeyVal(bpData=blueprint_data)


class Rewards(Container):
    __notifyevents__ = ['OnPlayerStateUpdated']

    def ApplyAttributes(self, attributes):
        super(Rewards, self).ApplyAttributes(attributes)
        self.audio = sm.GetService('audio')
        self._project_discovery_service = sm.RemoteSvc('ProjectDiscovery')
        self._tiers = sorted(TIERS, key=lambda tier: tier['level'])
        self._rank = None
        self._current_tier = None
        self._next_tier = None
        self._tier = self._get_player_current_tier_level()
        self._upcoming_rewards = []
        self._is_visible = False
        player_state = self._project_discovery_service.get_player_state()
        self.update_state(player_state)
        self.add_rank_container()
        self.add_reward_container()
        self.add_upcoming_rewards_container()
        sm.RegisterNotify(self)

    def Close(self):
        self.audio.SendUIEvent(Sounds.REWARDS_BACKGROUND_STOP)
        super(Rewards, self).Close()

    def Show(self, *args):
        super(Rewards, self).Show(*args)
        sm.ScatterEvent('OnRewardViewVisible')

    def add_rank_container(self):
        self.rank_container = Container(name='rank_container', parent=self, align=uiconst.TOPLEFT, width=self.width / 4 * 3 - PADDING_OUTER * 2, height=self.height / 3 * 2, padding=(0,
         0,
         0,
         PADDING_INNER))
        self._set_section_header(self.rank_container, LABEL_PATH_RANK)
        self._build_rank_info()
        self._build_rank_milestone()
        self._build_big_gauge()
        self._build_level_container()

    def _build_rank_info(self):
        self.rank_info = ContainerWithCorners(name='rank_info', parent=self.rank_container, align=uiconst.TOTOP, height=self.rank_container.height * 0.75, shouldShowTopCorners=False, padTop=PADDING_SECTION_TOP, state=uiconst.UI_HIDDEN)

    def _build_rank_milestone(self):
        self.rank_milestone = ContainerWithCorners(name='rank_milestone', parent=self.rank_container, align=uiconst.TOTOP, height=self.rank_container.height * 0.75, width=self.rank_container.width, padTop=PADDING_SECTION_TOP, shouldShowTopCorners=False, bgColor=COLOR_BACKGROUND_BLUE, state=uiconst.UI_HIDDEN)
        self.milestone_reward_label_container = Container(name='milestone_label_container', parent=self.rank_milestone, align=uiconst.TOLEFT, width=self.rank_milestone.width / 2, height=self.rank_milestone.height)
        self.milestone_reward_icon_container = Container(name='milestone_icon_container', parent=self.rank_milestone, align=uiconst.TOLEFT, width=self.rank_milestone.width - self.milestone_reward_label_container.width)
        self.reward_name_container = Container(name='milestone_reward_name_container', parent=self.milestone_reward_label_container, align=uiconst.TOTOP, height=self.milestone_reward_label_container.height / 2, width=self.milestone_reward_label_container.width)
        self.milestone_reward_name = Label(name='milestone_reward_name', parent=self.reward_name_container, align=uiconst.CENTERLEFT, fontsize=30, padding=(PADDING_MILESTONE_LABELS,
         15,
         0,
         0), maxWidth=self.reward_name_container.width - PADDING_MILESTONE_LABELS)
        self.milestone_reward_description = Label(name='milestone_reward_description', parent=self.milestone_reward_label_container, align=uiconst.TOTOP, fontsize=16, padding=(PADDING_MILESTONE_LABELS,
         20,
         0,
         0))
        self.claim_in_redeem_label = EveLabelMedium(name='claim_in_redeem_label', parent=self.milestone_reward_label_container, align=uiconst.TOBOTTOM, state=uiconst.UI_NORMAL, text=GetByLabel(LABEL_PATH_CLAIM_IN_REDEEM, link_to_redeem=REDEEM_WINDOW_URL), padding=(PADDING_MILESTONE_LABELS,
         0,
         0,
         PADDING_MILESTONE_LABELS))
        self._milestone_reward_icon = Icon(name='milestone_reward_icon', parent=self.milestone_reward_icon_container, align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=MILESTONE_REWARD_ICON_SIZE, height=MILESTONE_REWARD_ICON_SIZE)

    def _build_big_gauge(self):
        self.big_gauge_container = Container(name='big_gauge_container', parent=self.rank_info, align=uiconst.CENTERLEFT, width=BIG_GAUGE_SIZE, height=BIG_GAUGE_SIZE, shouldShowLeftCorners=False)
        self.big_gauge = GaugeCircular(name='big_gauge', parent=self.big_gauge_container, align=uiconst.TOLEFT, height=BIG_GAUGE_SIZE, radius=BIG_GAUGE_SIZE / 2, showMarker=False, lineWidth=BIG_GAUGE_LINE_WIDTH, state=uiconst.UI_HIDDEN, colorBg=COLOR_BACKGROUND_GAUGE)
        self.big_gauge_label_container = Container(name='big_gauge_label_container', parent=self.big_gauge_container, align=uiconst.CENTER, height=BIG_GAUGE_SIZE / 3, width=BIG_GAUGE_SIZE, padTop=PADDING_LABELS_BIG_GAUGE_TOP, state=uiconst.UI_HIDDEN)
        self.big_gauge_experience_label = Label(name='big_gauge_experience', parent=self.big_gauge_label_container, align=uiconst.TOTOP, fontsize=FONTSIZE_BIG_GAUGE_EXPERIENCE, fontStyle=STYLE_HEADER)
        self.big_gauge_description = Label(name='big_gauge_description', parent=self.big_gauge_label_container, align=uiconst.TOTOP, fontsize=FONTSIZE_BIG_GAUGE_DESCRIPTION, color=COLOR_TEXT)
        self.big_gauge_new_rank_label = Label(name='big_gauge_new_rank', parent=self.big_gauge_container, align=uiconst.CENTERTOP, fontsize=FONTSIZE_BIG_GAUGE_NEW_RANK, height=BIG_GAUGE_SIZE - PADDING_BIG_GAUGE_NEW_RANK_TOP, width=11.0 / 20.0 * BIG_GAUGE_SIZE, color=COLOR_TEXT, padTop=PADDING_BIG_GAUGE_NEW_RANK_TOP, state=uiconst.UI_HIDDEN)

    def _build_level_container(self):
        self.level_container = Container(name='level', parent=self.rank_info, align=uiconst.CENTERRIGHT, width=self.rank_container.width - BIG_GAUGE_SIZE, height=BIG_GAUGE_SIZE)
        self.level_label = EveLabelMedium(name='level', parent=self.level_container, align=uiconst.TOTOP, padLeft=PADDING_CONTAINER_TO_LABEL)
        max_rank_name_width = self.level_container.width - RANK_ICON_SIZE - 20 - PADDING_CONTAINER_TO_LABEL
        self.rank_name_label = Label(name='rank_name', parent=self.level_container, align=uiconst.TOPLEFT, width=max_rank_name_width, maxWidth=max_rank_name_width, fontsize=FONTSIZE_TEXT_RANK, padLeft=PADDING_CONTAINER_TO_LABEL, padTop=PADDING_BETWEEN_LABELS_LEVEL)
        self.rank_progress_label = EveLabelMedium(name='rank_progress', parent=self.level_container, align=uiconst.TOTOP, padLeft=PADDING_CONTAINER_TO_LABEL, padTop=PADDING_BETWEEN_LABELS_LEVEL)
        self._rank_icon = Sprite(name='rankIcon', parent=self.level_container, texturePath=self._get_rank_icon_path(self._rank), idx=0, top=8, left=20, height=RANK_ICON_SIZE, width=RANK_ICON_SIZE, align=uiconst.TOPRIGHT, opacity=1.0, state=uiconst.UI_DISABLED)
        self._set_rank_labels()
        self.rank_name_label.padTop += self.level_label.height
        self.rank_progress_label.padTop += self.rank_name_label.height + PADDING_BETWEEN_LABELS_LEVEL

    def add_reward_container(self):
        self.reward_container = Container(name='reward_container', parent=self, align=uiconst.TOPLEFT, width=self.width / 4 - PADDING_INNER, height=self.height / 3 * 2)
        self.reward_container.left = self.rank_container.width + PADDING_OUTER
        self._set_section_header(self.reward_container, LABEL_PATH_REWARD)
        self.current_rank_reward_container = Container(name='current_level_reward_container', parent=self.reward_container, align=uiconst.TOTOP, height=self.rank_container.height * 0.75, width=self.reward_container.width, bgColor=COLOR_BACKGROUND_BLUE, padTop=PADDING_SECTION_TOP)
        self.current_rank_icon_container = Container(name='reward_icon', parent=self.current_rank_reward_container, align=uiconst.TOTOP, height=self.current_rank_reward_container.height * 0.6)
        reward_type_id = self.get_loot_crate_type()
        self._reward_sprite = Sprite(name='reward_icon', parent=self.current_rank_icon_container, state=uiconst.UI_NORMAL, align=uiconst.CENTER, width=NEXT_REWARD_SIZE, height=NEXT_REWARD_SIZE, texturePath=CRATE_REWARD_ICON_PATH)
        self._reward_sprite.OnClick = lambda *args: show_info(reward_type_id)
        self.reward_label_container = Container(name='reward_label_container', parent=self.current_rank_reward_container, align=uiconst.TOTOP, height=self.current_rank_reward_container.height - self.current_rank_icon_container.height, width=self.current_rank_reward_container.width)
        self.reward_name = Label(name='reward_name', parent=self.reward_label_container, align=uiconst.CENTER, text=GetName(reward_type_id), fontsize=20, padTop=PADDING_LABELS_CURRENT_REWARD_TOP, maxWidth=self.reward_label_container.width)

    def add_upcoming_rewards_container(self):
        self.upcoming_rewards_container = Container(name='upcoming_rewards_container', parent=self, align=uiconst.TOBOTTOM, height=self.height / 3 - PADDING_INNER, padRight=PADDING_OUTER + PADDING_INNER)
        self._set_section_header(self.upcoming_rewards_container, LABEL_PATH_UPCOMING_REWARDS)
        self._build_upcoming_rewards()

    def _build_upcoming_rewards(self):
        self.upcoming_rewards_scroll = ScrollContainer(name='upcoming_rewards_scroll', parent=self.upcoming_rewards_container, align=uiconst.TOTOP, height=155, state=uiconst.UI_PICKCHILDREN, scrollBarColor=SCROLL_COLOR)
        next_tier = None
        for tier in self._tiers:
            tier_container = Container(name='tier_container', parent=self.upcoming_rewards_scroll, align=uiconst.TOLEFT, height=self.upcoming_rewards_scroll.height, width=ARROW_SIZE + SPACE_BETWEEN_ARROW_AND_REWARD * 2 + UPCOMING_REWARD_SIZE)
            if next_tier is None and tier['level'] > self._rank:
                next_tier = tier_container
            arrow_container = Container(name='arrow_container', parent=tier_container, align=uiconst.TOLEFT, width=ARROW_SIZE + SPACE_BETWEEN_ARROW_AND_REWARD)
            Sprite(name='arrow', parent=arrow_container, align=uiconst.CENTERLEFT, width=ARROW_SIZE, height=ARROW_SIZE, texturePath=ARROW_BETWEEN_REWARDS_TEXTURE_PATH, state=uiconst.UI_DISABLED)
            reward = Reward(name='tier_reward', parent=tier_container, align=uiconst.TOLEFT, width=UPCOMING_REWARD_SIZE, height=tier_container.height, tier=tier)
            if tier == self._tiers[-1]:
                tier_container.width += ARROW_SIZE
                arrow_container = Container(name='arrow_container', parent=tier_container, align=uiconst.TOLEFT, width=ARROW_SIZE, left=SPACE_BETWEEN_ARROW_AND_REWARD)
                Sprite(name='arrow', parent=arrow_container, align=uiconst.CENTER, width=ARROW_SIZE, height=ARROW_SIZE, texturePath=ARROW_BETWEEN_REWARDS_TEXTURE_PATH, state=uiconst.UI_DISABLED)
            self._upcoming_rewards.append(reward)

        StartTasklet(self.scroll_to_reward, next_tier)

    def scroll_to_reward(self, next_tier):
        if not next_tier:
            return
        self.upcoming_rewards_scroll.ScrollToRevealChildHorizontal(next_tier)

    def _set_section_header(self, section, label_path):
        if section:
            self._add_top_label(section, label_path)
            self._add_top_line(section)

    def _add_top_line(self, container_area):
        if container_area:
            container_area.top_line = Line(name='top_line', parent=container_area, align=uiconst.TOTOP, height=LINE_HEIGHT, color=LINE_COLOR)

    def _add_top_label(self, container_area, label_path):
        if container_area:
            top_label_container = Container(name='header_container', parent=container_area, align=uiconst.TOTOP, height=SECTION_HEADER_HEIGHT)
            section_header_label = ContainerAutoSize(name='section_header', parent=top_label_container, align=uiconst.TOLEFT, bgColor=SECTION_HEADER_BACKGROUND_COLOR)
            top_label = EveLabelMediumBold(name='top_label', parent=section_header_label, align=uiconst.CENTERLEFT, color=SECTION_HEADER_LABEL_COLOR, padLeft=PADDING_SECTION_LABEL, padRight=PADDING_SECTION_LABEL * 2)
            Sprite(name='label_end', parent=top_label_container, texturePath=SECTION_HEADER_LABEL_END_TEXTURE_PATH, opacity=1.0, state=uiconst.UI_DISABLED, align=uiconst.TOLEFT, color=SECTION_HEADER_BACKGROUND_COLOR, width=19)
            top_label.SetText(GetByLabel(label_path))

    def show_rewards(self):
        self._is_visible = True
        self.SetState(uiconst.UI_PICKCHILDREN)
        old_value = self.big_gauge.value
        new_value = self._get_value_for_big_gauge()
        if old_value > new_value:
            self.big_gauge.SetValue(0, animate=False)
        self.big_gauge.SetValueAndMarkerTimed(self._get_value_for_big_gauge(), GAUGE_ANIMATION_DURATION)
        self.play_background_audio()

    def hide_rewards(self):
        self._is_visible = False
        self.Hide()
        self.stop_background_audio()

    def start_audio_on_maximize(self):
        if self._is_visible:
            self.play_background_audio()

    def stop_audio_on_minimize(self):
        if self._is_visible:
            self.stop_background_audio()

    def _load_big_gauge(self, is_rank_up):
        if is_rank_up:
            self.big_gauge_label_container.Hide()
            self.big_gauge_new_rank_label.Show()
            self._load_big_gauge_text_rank_up(GetByLabel(LABEL_PATH_NEW_RANK_REACHED))
        else:
            self.big_gauge_new_rank_label.Hide()
            self.big_gauge_label_container.Show()
            self._load_big_gauge_text(self._get_current_level_progress(), GetByLabel(LABEL_PATH_EXPERIENCE))
        self.big_gauge_container.height = BIG_GAUGE_SIZE
        self.big_gauge.Show()
        self.big_gauge_container.Show()

    def _load_milestone_reward_view(self):
        try:
            type_id = self.get_current_milestone_reward_type_id(self._current_tier)
        except IndexError:
            return

        self.milestone_reward_name.SetText('<color=%(color)s>%(item_name)s</color>' % {'color': Color(*COLOR_TEXT).GetHex(),
         'item_name': GetName(type_id)})
        self.milestone_reward_description.SetText(GetByLabel(LABEL_PATH_UNLOCKED_REWARD_COOL, item_name=GetName(type_id)))
        self._milestone_reward_icon.OnClick = lambda *args: show_info(type_id)
        if GetCategoryID(type_id) == categoryShipSkin:
            self._milestone_reward_icon.SetTexturePath(LABEL_PATH_MILESTONE_SKIN_ICON)
        else:
            self._milestone_reward_icon.LoadIconByTypeID(typeID=type_id)

    def _get_current_level_progress(self):
        return self._experience - self.total_xp_needed_for_current_rank

    def _get_value_for_big_gauge(self):
        max_level_progress = self.total_xp_needed_for_next_rank - self.total_xp_needed_for_current_rank
        if max_level_progress < 1:
            return 0
        return float(self._get_current_level_progress()) / max_level_progress

    def get_loot_crate_type(self):
        if self._rank < NEEDED_LEVEL_FOR_SUPERIOR_CRATES:
            return LOOT_CRATE_TYPE_ID
        else:
            return SUPERIOR_LOOT_CRATE_TYPE_ID

    def get_current_milestone_reward_type_id(self, current_tier):
        return [ self._get_single_reward_type_id(tier) for tier in self._tiers if tier['level'] == current_tier ][0]

    def _get_single_reward_type_id(self, tier):
        if len(tier['types']) == 1:
            return tier['types'][0]
        return tier['types'][session.genderID]

    def _load_big_gauge_text(self, text, description_text):
        self.big_gauge_experience_label.SetText(self._center_text(text))
        self.big_gauge_description.SetText(self._center_text(description_text))

    def _load_big_gauge_text_rank_up(self, text):
        self.big_gauge_new_rank_label.SetText(self._center_text(text))

    def _center_text(self, text):
        return '<center>%s</center>' % text

    def _get_player_current_tier_level(self):
        current_rank = self._rank
        tiers_reached = [ tier['level'] for tier in self._tiers if tier['level'] <= current_rank ]
        if tiers_reached:
            return max(tiers_reached)
        return 0

    def _is_tier_level(self):
        tier_levels = [ tier['level'] for tier in self._tiers ]
        return self._rank in tier_levels

    def OnPlayerStateUpdated(self, player_state):
        previous_rank = self._rank
        self.update_state(player_state)
        is_rank_up = previous_rank is not None and self._rank > previous_rank
        is_milestone_rank_up = is_rank_up and self._is_tier_level()
        self._load_big_gauge(is_rank_up)
        self._load_milestone_reward_view()
        self._set_rank_labels()
        if is_milestone_rank_up:
            self.rank_info.Hide()
            self.rank_milestone.Show()
            self.audio.SendUIEvent(Sounds.REWARDS_MILESTONE_REWARD)
        elif is_rank_up:
            self.rank_milestone.Hide()
            self.rank_info.Show()
            self.audio.SendUIEvent(Sounds.REWARDS_LEVEL_UP)
        else:
            self.rank_milestone.Hide()
            self.rank_info.Show()

    def update_state(self, player_state):
        self._player_state = player_state
        self._rank = self._player_state.rank
        self._experience = self._player_state.experience
        self.total_xp_needed_for_current_rank = self._project_discovery_service.get_total_needed_xp(self._rank)
        self.total_xp_needed_for_next_rank = self._project_discovery_service.get_total_needed_xp(self._rank + 1)
        self._current_tier = self._get_player_current_tier_level()
        self._update_milestone_collect_state()
        self._next_tier = self._get_next_tier_level()

    def _update_milestone_collect_state(self):
        for reward in self._upcoming_rewards:
            if reward.get_tier_level() <= self._current_tier:
                reward.show_achieved_overlay()

    def _get_player_current_rank_level(self):
        current_rank = self._rank
        tiers_reached = [ tier['level'] for tier in self._tiers if tier['level'] <= current_rank ]
        if tiers_reached:
            return max(tiers_reached)
        return 0

    def _get_next_tier_level(self):
        current_tier_level = self._get_player_current_tier_level()
        tiers_left = [ tier['level'] for tier in self._tiers if tier['level'] > current_tier_level ]
        if tiers_left:
            return min(tiers_left)
        return current_tier_level

    def _get_rank_icon_path(self, rank):
        return const.rank_paths[calculate_rank_band(rank)]

    def increment(self):
        self._current_tier = [ self._tiers[i]['level'] for i in xrange(len(self._tiers)) if self._tiers[i]['level'] > self._current_tier ][0] if self._current_tier < self._tiers[-1]['level'] else self._tiers[-1]['level']

    def _set_rank_labels(self):
        self.level_label.SetText(GetByLabel(LABEL_PATH_LEVEL, level=str(self._rank)))
        text = u'<color=%s>' % Color(*COLOR_TEXT).GetHex()
        text += GetByLabel(LABEL_PATH_RANK_TITLES + str(calculate_rank_band(self._rank)))
        text += '</color>'
        self.rank_name_label.SetText(text)
        current_exp = self._experience
        remaining_exp = max(self.total_xp_needed_for_next_rank - current_exp, 0)
        self.rank_progress_label.SetText(GetByLabel(LABEL_PATH_RANK_PROGRESS, experience_gained=current_exp, experience_until_next=remaining_exp))

    def play_background_audio(self):
        self.audio.SendUIEvent(Sounds.REWARDS_BACKGROUND_PLAY)

    def stop_background_audio(self):
        self.audio.SendUIEvent(Sounds.REWARDS_BACKGROUND_STOP)


class Reward(Container):
    UPCOMING_REWARD_ICON_SIZE = 64
    default_clipChildren = False
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(Reward, self).ApplyAttributes(attributes)
        self._tier = attributes.get('tier')
        self._is_achieved = False
        self._setup_layout()

    def _setup_layout(self):
        reward_type_id = self.get_type_id()
        self.rewardCircle = RewardCircle(name='reward_icon', parent=self, align=uiconst.TOTOP, height=self.height / 2, padTop=5, typeID=reward_type_id, iconSize=self.UPCOMING_REWARD_ICON_SIZE)
        self.reward_rank_conatiner = Container(name='reward_rank_container', parent=self, align=uiconst.TOTOP, height=self.height / 2)
        self.rewardCircle.load_icon()
        self._rank_icon_container = Container(name='reward_rank_container', parent=self.reward_rank_conatiner, align=uiconst.TOTOP, height=self.reward_rank_conatiner.height / 2)
        self._rank_icon = Sprite(name='rankIcon', parent=self._rank_icon_container, texturePath=self._get_rank_icon_path(self._tier['level']), height=36, width=36, align=uiconst.CENTER, opacity=0.9)
        self._level_label = EveLabelMedium(name='LevelLabel', parent=self.reward_rank_conatiner, align=uiconst.TOTOP, text='<center>%s</center>' % GetByLabel(LABEL_PATH_LEVEL, level=str(self._tier['level'])), opacity=0.9)

    def show_achieved_overlay(self):
        if not self._is_achieved:
            self._is_achieved = True
            self.rewardCircle.show_achieved_overlay()
            animations.FadeIn(self._level_label, curveType=uiconst.ANIM_OVERSHOT2)
            animations.FadeIn(self._rank_icon, curveType=uiconst.ANIM_OVERSHOT2)

    def get_type_id(self):
        if len(self._tier['types']) == 1:
            return self._tier['types'][0]
        return self._tier['types'][session.genderID]

    def _get_rank_icon_path(self, rank):
        return const.rank_paths[calculate_rank_band(rank)]

    def get_tier_level(self):
        return self._tier['level']


class RewardCircle(Container):
    COLOR_ACHIEVED_GLOW = (0.2, 0.74, 0.95, 0.9)
    COLOR_ACHIEVED_CHECK_BASE = (0.2, 0.74, 0.95, 0.5)
    COLOR_SELECTED = (0.0, 0.0, 0.05, 1.0)
    COLOR_ACHIEVED_SELECTED = (0.2, 0.74, 0.95, 1.0)
    UPCOMING_REWARD_ICON_SIZE = 64
    default_clipChildren = False
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(RewardCircle, self).ApplyAttributes(attributes)
        self.typeID = attributes.get('typeID')
        self.icon_size = attributes.get('iconSize')
        self._is_achieved = False
        self._setup_layout()

    def _setup_layout(self):
        self._check_mark = Sprite(name='checkMark', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/checkmark.png', opacity=0, idx=0, state=uiconst.UI_DISABLED, align=uiconst.CENTER, height=self.icon_size, width=self.icon_size, color=self.COLOR_ACHIEVED_GLOW)
        self._check_base = Sprite(name='checkBase', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/checkBase.png', opacity=0, state=uiconst.UI_DISABLED, align=uiconst.CENTER, height=self.icon_size, width=self.icon_size, color=self.COLOR_ACHIEVED_CHECK_BASE)
        self._selected = Sprite(name='selected', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/select.png', state=uiconst.UI_DISABLED, align=uiconst.CENTER, height=self.icon_size, width=self.icon_size, color=self.COLOR_SELECTED)
        self._done_glow = Sprite(name='doneGlow', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/doneGlow.png', opacity=0, state=uiconst.UI_DISABLED, align=uiconst.CENTER, height=self.icon_size, width=self.icon_size, color=self.COLOR_ACHIEVED_GLOW)
        self._reward_overlay_base = Sprite(name='rewardOverlayBase', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/rewardBase.png', opacity=0, state=uiconst.UI_DISABLED, align=uiconst.CENTER, height=self.icon_size, width=self.icon_size, color=(0, 0, 0, 0.7))
        self._reward_sprite = Icon(name='reward_sprite', parent=self, state=uiconst.UI_NORMAL, align=uiconst.CENTER, spriteEffect=trinity.TR2_SFX_MASK, textureSecondaryPath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/rewardBase.png', height=self.icon_size, width=self.icon_size)
        self._base = Sprite(name='base', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/rewardBase.png', state=uiconst.UI_DISABLED, align=uiconst.CENTER, height=self.icon_size, width=self.icon_size, color=(0, 0, 0, 1))

    def set_type_id(self, typeID):
        self.typeID = typeID

    def load_icon(self):
        self._reward_sprite.OnClick = lambda *args: show_info(self.typeID)
        self._reward_sprite.LoadIconByTypeID(typeID=self.typeID, isCopy=True)

    def show_achieved_overlay(self):
        if not self._is_achieved:
            self._is_achieved = True
            animations.FadeIn(self._check_mark, curveType=uiconst.ANIM_OVERSHOT2)
            animations.FadeTo(self._check_base, 0, 0.11, curveType=uiconst.ANIM_OVERSHOT2)
            animations.FadeIn(self._done_glow, curveType=uiconst.ANIM_OVERSHOT2)
            animations.FadeTo(self._reward_overlay_base, 0, 0.7, curveType=uiconst.ANIM_OVERSHOT2)
            self._selected.color = self.COLOR_ACHIEVED_SELECTED
            animations.FadeTo(self._selected, 0, 1, curveType=uiconst.ANIM_OVERSHOT2)

    def OnMouseEnter(self, *args):
        animations.SpGlowFadeIn(self._selected, duration=0.25)
        animations.SpGlowFadeTo(self._selected, self.COLOR_SELECTED, self.COLOR_ACHIEVED_SELECTED, duration=0.25)

    def OnMouseExit(self, *args):
        animations.SpGlowFadeOut(self._selected, duration=0.25)
