#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\resourcewars\client\rewardsfeedback.py
import carbonui.const as uiconst
from carbon.common.script.util.format import FmtAmt
from carbonui.control.window import Window
from carbonui.fontconst import STYLE_DEFAULT
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.window.header.small import SmallWindowHeader
from eve.client.script.ui.control.buttons import TextButtonWithBackgrounds, ButtonTextBoldness
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
from eve.common.lib.appConst import factionAmarrEmpire, factionCaldariState, factionGallenteFederation, factionMinmatarRepublic
from gametime import SEC
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShort
from resourcewars.client.iconlabelview import IconLabelView, LpIconView
from resourcewars.common.const import FACTION_TO_RW_LP_CORP
WINDOW_MARGIN = 2
ACTION_HEIGHT = 28
ACTION_TOP = 2
INFO_WIDTH = 294
TITLE_WIDTH = INFO_WIDTH
TITLE_HEIGHT = 34
TITLE_PADDING_H = 11
TITLE_PADDING_V = 4
TITLE_MARGIN_BETWEEN_ICONS = 5
TITLE_MARGIN_FROM_ICON_TO_TEXT = 7
TITLE_FONTSIZE = 10
TIER_FONTSIZE = 10
TITLE_OPACITY = 0.75
TIER_OPACITY = 0.75
FACTION_ICON_SIZE = {factionAmarrEmpire: (21, 17),
 factionCaldariState: (20, 19),
 factionGallenteFederation: (20, 20),
 factionMinmatarRepublic: (20, 20)}
FACTION_ICON_SIZE_DEFAULT = (20, 20)
ICON_MISSION_TYPE_WIDTH = 26
ICON_MISSION_TYPE_HEIGHT = 26
REWARD_LEVEL_ICON_BASE_WIDTH = 17
REWARD_LEVEL_ICON_BASE_HEIGHT = 18
REWARD_LEVEL_ICON_EXTRA_WIDTH = 30
REWARD_LEVEL_ICON_EXTRA_HEIGHT = 30
RESULTS_HEIGHT_ROW_1 = 13
RESULTS_HEIGHT_ROW_2 = 47
RESULTS_HEIGHT_ROW_3 = max(REWARD_LEVEL_ICON_BASE_HEIGHT, REWARD_LEVEL_ICON_EXTRA_HEIGHT)
RESULTS_PADDING_L = TITLE_PADDING_H + ICON_MISSION_TYPE_WIDTH + TITLE_MARGIN_BETWEEN_ICONS + TITLE_MARGIN_FROM_ICON_TO_TEXT
RESULTS_PADDING_T = 11
RESULTS_PADDING_B = 10
RESULTS_MARGIN_1_2 = 0
RESULTS_MARGIN_2_3 = 5
RESULTS_WIDTH = INFO_WIDTH
RESULTS_HEIGHT = RESULTS_PADDING_T + RESULTS_HEIGHT_ROW_1 + RESULTS_MARGIN_1_2 + RESULTS_HEIGHT_ROW_2 + RESULTS_MARGIN_2_3 + RESULTS_HEIGHT_ROW_3 + RESULTS_PADDING_B
RESULTS_ROW_3_MARGIN_BASE = 11
RESULTS_ROW_3_MARGIN_EXTRAS = 2
RESULTS_ROW_3_MARGIN_TIME = 21
TOTAL_ISK_FONTSIZE = 11
ISK_FONTSIZE = 38
TIME_FONTSIZE = 11
TOTAL_ISK_OPACITY = 0.75
ISK_OPACITY = 0.9
TIME_OPACITY = 0.75
REWARDS_WIDTH = INFO_WIDTH
REWARDS_HEIGHT = 28
REWARDS_PADDING_L = RESULTS_PADDING_L
REWARDS_PADDING_V = 3
REWARDS_INTERNAL_MARGIN = 15
REWARDS_MARGIN_ICON = 2
REWARD_LP_ICON_SIZE = 26
REWARD_STANDINGS_ICON_SIZE = 26
REWARD_ISK_ICON_SIZE = 26
REWARDS_TEXT_FONTSIZE = 12
REWARDS_TEXT_OPACITY = 0.75
REWARD_FRAME_COLOR = (0.0,
 0.0,
 0.0,
 0.5)
INFO_HEIGHT = TITLE_HEIGHT + RESULTS_HEIGHT + REWARDS_HEIGHT
ICON_WIDTH = 99
ICON_HEIGHT = INFO_HEIGHT
ICON_OPACITY = 0.7
VIEW_WIDTH = ICON_WIDTH + INFO_WIDTH
VIEW_HEIGHT = INFO_HEIGHT + ACTION_HEIGHT
SMALL_SCREEN_HEIGHT = 768
ACTION_FONTSIZE = 14
TITLE = 'UI/ResourceWars/IncomingTransmission/MainTitle'
SUBTITLE = 'UI/ResourceWars/IncomingTransmission/SubTitle'
TOTAL_ISK = 'UI/ResourceWars/ISKRewarded'
REWARDS_ICON = 'res:/ui/Texture/Classes/ResourceWars/resourceWars_rewardBanner.png'
FACTION_ICON = {factionAmarrEmpire: 'res:/UI/Texture/Classes/ResourceWars/resourceWars_empireAmarr.png',
 factionCaldariState: 'res:/UI/Texture/Classes/ResourceWars/resourceWars_empireCaldari.png',
 factionGallenteFederation: 'res:/UI/Texture/Classes/ResourceWars/resourceWars_empireGallente.png',
 factionMinmatarRepublic: 'res:/UI/Texture/Classes/ResourceWars/resourceWars_empireMinmatar.png'}
MISSION_TYPE_ICON = 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/resourceWars.png'
REWARD_LEVEL_BASE_ICON = 'res:/UI/Texture/Classes/ResourceWars/resourceWars_participationTier.png'
REWARD_LEVEL_BRONZE_ICON = 'res:/UI/Texture/Classes/ResourceWars/resourceWars_Site_Success_Tier_Bronze.png'
REWARD_LEVEL_SILVER_ICON = 'res:/UI/Texture/Classes/ResourceWars/resourceWars_Site_Success_Tier_Silver.png'
REWARD_LEVEL_GOLD_ICON = 'res:/UI/Texture/Classes/ResourceWars/resourceWars_Site_Success_Tier_Gold.png'
REWARD_LEVEL_ACHIEVED_ICONS = {2: REWARD_LEVEL_BRONZE_ICON,
 3: REWARD_LEVEL_SILVER_ICON,
 4: REWARD_LEVEL_GOLD_ICON}
REWARD_LEVEL_FAILED_ICON = 'res:/UI/Texture/classes/ResourceWars/resourceWars_emptyRewardTier.png'
ISK_ICON = 'res:/UI/Texture/WindowIcons/wallet.png'
LP_ICON = 'res:/UI/Texture/WindowIcons/lpstore.png'
STANDINGS_ICON = 'res:/UI/Texture/WindowIcons/factionalwarfare.png'
REWARD_LEVEL_FAILED_ICON_COLOR = (0.598,
 0.598,
 0.598,
 0.2)

def get_scale():
    if uicore.desktop:
        return float(uicore.desktop.height) / float(SMALL_SCREEN_HEIGHT)
    return 1


class RewardsFeedbackWindow(Window):
    default_fixedWidth = VIEW_WIDTH * get_scale()
    default_fixedHeight = VIEW_HEIGHT * get_scale()
    default_top = '__center__'
    default_name = 'rwRewardsFeedbackWindow'
    default_isLightBackgroundConfigurable = False
    default_isMinimizable = False
    default_isStackable = False
    default_isCollapseable = False
    default_isLockable = False
    default_isOverlayable = False
    default_extend_content_into_header = True

    def ApplyAttributes(self, attributes):
        func = attributes.get('func', None)
        data = attributes.get('data', None)
        Window.ApplyAttributes(self, attributes)
        self.update_size()
        self.rewardsFeedbackContainer = RewardsFeedbackContainer(name='rewardsFeedbackContainer', parent=self.sr.main, align=uiconst.TOTOP_NOPUSH, width=self.get_width(), height=self.get_height(), func=func, data=data, padding=WINDOW_MARGIN)

    def update_size(self):
        width = self.get_width()
        height = self.get_height()
        width, height = self.GetWindowSizeForContentSize(width, height)
        self.LockWidth(width)
        self.LockHeight(height)

    def get_width(self):
        return VIEW_WIDTH * get_scale() + 2 * WINDOW_MARGIN

    def get_height(self):
        return VIEW_HEIGHT * get_scale() + 2 * WINDOW_MARGIN

    def OnResizeUpdate(self, *args):
        Window.OnResizeUpdate(self, *args)
        self.update_size()
        self.rewardsFeedbackContainer.update_size()

    def Prepare_Header_(self):
        self._SetHeader(SmallWindowHeader())


class RewardsFeedbackContainer(Container):
    ACTION_LABEL = 'UI/ResourceWars/AcceptRewards'

    def ApplyAttributes(self, attributes):
        self.is_ready = False
        self.data = attributes.data
        self.func = attributes.get('func', None)
        self.rwSvc = sm.GetService('rwService')
        Container.ApplyAttributes(self, attributes)
        self.scale = get_scale()
        self.build_base()
        self.build_icon()
        self.build_info()
        self.build_action()
        self.is_ready = True

    def Close(self):
        Container.Close(self)

    def build_base(self):
        self.base = Container(name='rewardsFeedback_baseContainer', parent=self, align=uiconst.CENTERTOP, width=VIEW_WIDTH * self.scale, height=VIEW_HEIGHT * self.scale, state=uiconst.UI_PICKCHILDREN)

    def build_icon(self):
        icon_width, icon_height = self.get_icon_size()
        self.icon_container = Container(name='rewardsFeedback_iconContainer', parent=self.base, align=uiconst.TOPLEFT, width=icon_width, height=icon_height, state=uiconst.UI_DISABLED)
        self.icon = Sprite(name='rewardsFeedback_icon', parent=self.icon_container, align=uiconst.TOALL, texturePath=REWARDS_ICON, opacity=ICON_OPACITY)

    def build_info(self):
        panel_width, panel_height = self.get_info_size()
        self.info_container = Container(name='rewardsFeedback_infoContainer', parent=self.base, align=uiconst.TOPRIGHT, width=panel_width, height=panel_height)
        self.build_title()
        self.build_results()
        self.build_rewards()

    def build_title(self):
        row_width, row_height, row_padding_h, row_padding_v, row_margin_icons, row_margin_to_text = self.get_title_size()
        self.title_container = Container(name='rewardsFeedback_titleContainer', parent=self.info_container, align=uiconst.TOTOP, width=row_width, height=row_height, state=uiconst.UI_DISABLED, padding=(row_padding_h,
         row_padding_v,
         row_padding_h,
         0))
        self.build_faction_icon()
        self.build_mission_type_icon(row_margin_icons)
        self.build_title_labels(row_margin_to_text)

    def build_faction_icon(self):
        faction = self.data.get('faction', None)
        faction_icon_width, faction_icon_height = self.get_faction_icon_size()
        self.faction_icon_container = Container(name='rewardsFeedback_title_factionIconContainer', parent=self.title_container, align=uiconst.TOLEFT, width=faction_icon_width, height=faction_icon_height)
        self.faction_icon = Sprite(name='rewardsFeedback_title_factionIcon', parent=self.faction_icon_container, align=uiconst.CENTER, texturePath=FACTION_ICON[faction] if faction else None, width=faction_icon_width, height=faction_icon_height)

    def build_mission_type_icon(self, row_margin_internal):
        mission_type_icon_width, mission_type_icon_height = self.get_mission_type_icon_size()
        self.mission_icon_container = Container(name='rewardsFeedback_title_missionTypeIconContainer', parent=self.title_container, align=uiconst.TOLEFT, width=mission_type_icon_width, height=mission_type_icon_height, left=row_margin_internal)
        self.mission_type_icon = Sprite(name='rewardsFeedback_title_missionTypeIcon', parent=self.mission_icon_container, align=uiconst.CENTER, texturePath=MISSION_TYPE_ICON, width=mission_type_icon_width, height=mission_type_icon_height)

    def build_title_labels(self, row_margin_internal):
        title_fontsize = self.get_title_fontsize()
        self.title = Label(name='rewardsFeedback_title_titleLabel', parent=self.title_container, align=uiconst.TOTOP, text=self.rwSvc.get_site_name(), fontsize=title_fontsize, fontstyle=STYLE_DEFAULT, left=row_margin_internal, opacity=TITLE_OPACITY)
        tier_fontsize = self.get_tier_fontsize()
        tier = self.data.get('tier', '')
        self.tier = Label(name='rewardsFeedback_title_tierLabel', parent=self.title_container, align=uiconst.TOTOP, text=GetByLabel(SUBTITLE, level=tier), fontsize=tier_fontsize, fontstyle=STYLE_DEFAULT, left=row_margin_internal, opacity=TIER_OPACITY)

    def build_results(self):
        row_width, row_height, row_padding_l, row_padding_t, row_padding_b = self.get_results_size()
        self.results_container = Container(name='rewardsFeedback_resultsContainer', parent=self.info_container, align=uiconst.TOTOP, width=row_width, height=row_height, state=uiconst.UI_PICKCHILDREN, padding=(row_padding_l,
         row_padding_t,
         0,
         row_padding_b))
        row_1_height, row_1_2_margin, row_2_height, row_2_3_margin, row_3_height, row_3_margin_base, row_3_margin_extras, row_3_margin_time = self.get_result_rows_size()
        total_isk_fontsize, isk_fontsize, time_fontsize = self.get_results_fontsize()
        self.build_results_row_1(row_1_height, total_isk_fontsize)
        self.build_results_row_2(row_2_height, row_1_2_margin, isk_fontsize)
        self.build_results_row_3(row_3_height, row_2_3_margin, row_3_margin_base, row_3_margin_extras, row_3_margin_time, time_fontsize)

    def build_results_row_1(self, row_1_height, total_isk_fontsize):
        self.results_row_1 = Container(name='rewardsFeedback_results_row1', parent=self.results_container, align=uiconst.TOTOP, height=row_1_height, state=uiconst.UI_DISABLED)
        self.total_isk = Label(name='rewardsFeedback_results_row1_totalIskLabel', parent=self.results_row_1, align=uiconst.CENTERLEFT, text=GetByLabel(TOTAL_ISK).upper(), fontsize=total_isk_fontsize, fontstyle=STYLE_DEFAULT, opacity=TOTAL_ISK_OPACITY, bold=True)

    def build_results_row_2(self, row_2_height, row_1_2_margin, isk_fontsize):
        self.results_row_2 = Container(name='rewardsFeedback_results_row2', parent=self.results_container, align=uiconst.TOTOP, height=row_2_height, state=uiconst.UI_DISABLED, top=row_1_2_margin)
        isk_amount = self.data.get('iskReward', 0)
        self.isk = Label(name='rewardsFeedback_results_iskAmountLabel', parent=self.results_row_2, align=uiconst.CENTERLEFT, text=FmtAmt(amount=isk_amount), fontsize=isk_fontsize, fontstyle=STYLE_DEFAULT, bold=True, opacity=ISK_OPACITY)

    def build_results_row_3(self, row_3_height, row_2_3_margin, row_3_margin_base, row_3_margin_extras, row_3_margin_time, time_fontsize):
        self.results_row_3 = Container(name='rewardsFeedback_results_row3', parent=self.results_container, align=uiconst.TOTOP, height=row_3_height, top=row_2_3_margin)
        icon_base_width, icon_base_height, icon_extra_width, icon_extra_height = self.get_reward_level_icon_size()
        self.reward_level_icon_base = Sprite(name='rewardsFeedback_results_row3_rewardLevelIconBase', parent=self.results_row_3, align=uiconst.CENTERLEFT, texturePath=REWARD_LEVEL_BASE_ICON, width=icon_base_width, height=icon_base_height)
        self.reward_level_icons_extras = []
        reward_level_reached = self.data.get('rewardLevel', 1)
        reward_level_icon_left = icon_base_width + row_3_margin_base
        for reward_level, icon in REWARD_LEVEL_ACHIEVED_ICONS.items():
            is_reached = reward_level_reached >= reward_level
            reward_level_icon = Sprite(name='rewardsFeedback_results_row3_rewardLevelIconExtra', parent=self.results_row_3, align=uiconst.CENTERLEFT, texturePath=icon if is_reached else REWARD_LEVEL_FAILED_ICON, width=icon_extra_width, height=icon_extra_height, left=reward_level_icon_left, color=None if is_reached else REWARD_LEVEL_FAILED_ICON_COLOR, state=uiconst.UI_NORMAL)
            reward_level_icon.hint = GetByLabel('UI/ResourceWars/AdditionalRewardsHint')
            self.reward_level_icons_extras.append(reward_level_icon)
            reward_level_icon_left += icon_extra_width + row_3_margin_extras

        completion_time_left = self.get_completion_time_left(icon_base_width, icon_extra_width, row_3_margin_base, row_3_margin_extras, row_3_margin_time)
        completion_time = self.data.get('completionTimeSeconds', 0) * SEC
        time_limit = self.data.get('timeLimitSeconds', 0) * SEC
        time_remaining = max(time_limit - completion_time, 0)
        time_remaining_string = FormatTimeIntervalShort(time_remaining, showFrom='hour', showTo='second')
        self.time = Label(name='rewardsFeedback_results_row3_timeLabel', parent=self.results_row_3, align=uiconst.CENTERLEFT, text=time_remaining_string, fontsize=time_fontsize, fontstyle=STYLE_DEFAULT, left=completion_time_left, opacity=TIME_OPACITY, state=uiconst.UI_NORMAL)
        self.time.hint = GetByLabel('UI/ResourceWars/TimeRemaining')

    def build_rewards(self):
        scale = get_scale()
        row_width, row_height, row_padding_l, row_padding_v, row_margin_internal, row_margin_icon = self.get_rewards_size()
        self.rewards_container = Container(name='rewardsFeedback_rewardsContainer', parent=self.info_container, align=uiconst.TOTOP, width=row_width, height=row_height + 2 * row_padding_v, padding=(row_padding_l,
         row_padding_v,
         0,
         row_padding_v))
        self.build_reward_lp(row_height, row_margin_icon, 0, scale)
        self.build_reward_standings(row_height, row_margin_icon, row_margin_internal, scale)
        self.build_reward_isk(row_height, row_margin_icon, row_margin_internal, scale)
        self.build_reward_frame()

    def build_reward_lp(self, row_height, row_margin_icon, row_margin_internal, scale):
        faction_id = self.data.get('faction', None)
        rw_corp_id = FACTION_TO_RW_LP_CORP.get(faction_id, None)
        lp_text = FmtAmt(self.data.get('lpReward', 0))
        self.lp_container = LpIconView(name='rewardsFeedback_rewardView_lp', parent=self.rewards_container, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, text=lp_text, icon_texture=LP_ICON, font_size=REWARDS_TEXT_FONTSIZE, icon_size=REWARD_LP_ICON_SIZE, row_height=row_height, row_margin_icon=row_margin_icon, row_margin_internal=row_margin_internal, scale=scale, rw_corp_id=rw_corp_id)

    def build_reward_standings(self, row_height, row_margin_icon, row_margin_internal, scale):
        standings_increase = self.data.get('standingsIncrease', 0)
        standings_sign = '+' if standings_increase >= 0 else '-'
        standings_text = standings_sign + FmtAmt(standings_increase, showFraction=2)
        self.standings_container = IconLabelView(name='rewardsFeedback_rewardView_standings', parent=self.rewards_container, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, hint=GetByLabel('UI/ResourceWars/StandingsGain'), text=standings_text, icon_texture=STANDINGS_ICON, font_size=REWARDS_TEXT_FONTSIZE, icon_size=REWARD_STANDINGS_ICON_SIZE, row_height=row_height, row_margin_icon=row_margin_icon, row_margin_internal=row_margin_internal, scale=scale)
        self.standings_container.OnClick = CharacterSheetWindow.OpenStandings

    def build_reward_isk(self, row_height, row_margin_icon, row_margin_internal, scale):
        isk_text = FmtAmt(self.data.get('iskReward', 0))
        self.isk_container = IconLabelView(name='rewardsFeedback_rewardView_isk', parent=self.rewards_container, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, hint=GetByLabel('UI/ResourceWars/ISKRewarded'), text=isk_text, icon_texture=ISK_ICON, font_size=REWARDS_TEXT_FONTSIZE, icon_size=REWARD_ISK_ICON_SIZE, row_height=row_height, row_margin_icon=row_margin_icon, row_margin_internal=row_margin_internal, scale=scale)
        self.isk_container.OnClick = uicore.cmd.OpenWallet

    def build_reward_frame(self):
        row_width, row_height, row_padding_l, row_padding_v, row_margin_internal, row_margin_icon = self.get_rewards_size()

    def build_action(self):
        action_width, action_height = self.get_action_size()
        self.action_container = Container(name='rewardsFeedback_actionContainer', parent=self.base, align=uiconst.TOBOTTOM, width=action_width, height=action_height, state=uiconst.UI_PICKCHILDREN)
        self.action = None
        self.rebuild_action_button()

    def rebuild_action_button(self):
        if self.action and not self.action.destroyed:
            self.action.Close()
        button_text = GetByLabel(self.ACTION_LABEL).upper()
        button_fontsize = self.get_action_fontsize()
        action_width, action_height = self.get_action_size()
        self.action = ActionButton(name='rewardsFeedback_action', parent=self.action_container, align=uiconst.CENTERBOTTOM, width=action_width, height=action_height, func=self.func, text=button_text, fontsize=button_fontsize, padTop=8)

    def update_size(self):
        if self.is_ready:
            new_scale = get_scale()
            if new_scale != self.scale:
                self.scale = new_scale
                self.resize()
                self.resize_base()
                self.resize_icon()
                self.resize_info()
                self.resize_action()

    def resize(self):
        self.width = VIEW_WIDTH * self.scale
        self.height = VIEW_HEIGHT * self.scale

    def resize_base(self):
        self.base.width = VIEW_WIDTH * self.scale
        self.base.height = VIEW_HEIGHT * self.scale

    def resize_icon(self):
        icon_width, icon_height = self.get_icon_size()
        self.icon_container.width = icon_width
        self.icon_container.height = icon_height

    def resize_info(self):
        panel_width, panel_height = self.get_info_size()
        self.info_container.width = panel_width
        self.info_container.height = panel_height
        self.resize_title()
        self.resize_results()
        self.resize_rewards()

    def resize_title(self):
        row_width, row_height, row_padding_h, row_padding_v, row_margin_icons, row_margin_to_text = self.get_title_size()
        self.title_container.width = row_width
        self.title_container.height = row_height
        self.title_container.padding = (row_padding_h,
         row_padding_v,
         row_padding_h,
         row_padding_v)
        self.resize_faction_icon()
        self.resize_mission_type_icon(row_margin_icons)
        self.resize_title_labels(row_margin_to_text)

    def resize_faction_icon(self):
        faction_icon_width, faction_icon_height = self.get_faction_icon_size()
        self.faction_icon_container.width = faction_icon_width
        self.faction_icon_container.height = faction_icon_height
        self.faction_icon.width = faction_icon_width
        self.faction_icon.height = faction_icon_height

    def resize_mission_type_icon(self, row_margin_internal):
        mission_type_icon_width, mission_type_icon_height = self.get_mission_type_icon_size()
        self.mission_icon_container.width = mission_type_icon_width
        self.mission_icon_container.height = mission_type_icon_height
        self.mission_icon_container.left = row_margin_internal
        self.mission_type_icon.width = mission_type_icon_width
        self.mission_type_icon.height = mission_type_icon_height

    def resize_title_labels(self, row_margin_internal):
        title_fontsize = self.get_title_fontsize()
        self.title.fontsize = title_fontsize
        self.title.left = row_margin_internal
        tier_fontsize = self.get_tier_fontsize()
        self.tier.fontsize = tier_fontsize
        self.tier.left = row_margin_internal

    def resize_results(self):
        row_width, row_height, row_padding_l, row_padding_t, row_padding_b = self.get_results_size()
        self.results_container.width = row_width
        self.results_container.height = row_height
        self.results_container.padding = (row_padding_l,
         row_padding_t,
         0,
         row_padding_b)
        row_1_height, row_1_2_margin, row_2_height, row_2_3_margin, row_3_height, row_3_margin_base, row_3_margin_extras, row_3_margin_time = self.get_result_rows_size()
        self.results_row_1.height = row_1_height
        self.results_row_2.height = row_2_height
        self.results_row_2.top = row_1_2_margin
        self.results_row_3.height = row_3_height
        self.results_row_3.top = row_2_3_margin
        total_isk_fontsize, isk_fontsize, time_fontsize = self.get_results_fontsize()
        self.total_isk.fontsize = total_isk_fontsize
        self.isk.fontsize = isk_fontsize
        self.time.fontsize = time_fontsize
        icon_base_width, icon_base_height, icon_extra_width, icon_extra_height = self.get_reward_level_icon_size()
        self.reward_level_icon_base.width = icon_base_width
        self.reward_level_icon_base.height = icon_base_height
        reward_level_icon_left = icon_base_width + row_3_margin_base
        for icon in self.reward_level_icons_extras:
            icon.width = icon_extra_width
            icon.height = icon_extra_height
            icon.left = reward_level_icon_left
            reward_level_icon_left += icon_extra_width + row_3_margin_extras

        completion_time_left = self.get_completion_time_left(icon_base_width, icon_extra_width, row_3_margin_base, row_3_margin_extras, row_3_margin_time)
        self.time.left = completion_time_left

    def resize_rewards(self):
        scale = get_scale()
        row_width, row_height, row_padding_l, row_padding_v, row_margin_internal, row_margin_icon = self.get_rewards_size()
        self.rewards_container.width = row_width
        self.rewards_container.height = row_height + 2 * row_padding_v
        self.rewards_container.padding = (row_padding_l,
         row_padding_v,
         0,
         row_padding_v)
        self.lp_container.update_size(row_height, row_margin_icon, 0, scale)
        self.standings_container.update_size(row_height, row_margin_icon, row_margin_internal, scale)
        self.isk_container.update_size(row_height, row_margin_icon, row_margin_internal, scale)

    def resize_action(self):
        action_width, action_height = self.get_action_size()
        self.action_container.width = action_width
        self.action_container.height = action_height
        self.rebuild_action_button()

    def get_action_size(self):
        return (VIEW_WIDTH * self.scale, ACTION_HEIGHT * self.scale)

    def get_action_fontsize(self):
        return ACTION_FONTSIZE * self.scale

    def get_icon_size(self):
        return (ICON_WIDTH * self.scale, ICON_HEIGHT * self.scale)

    def get_info_size(self):
        return (INFO_WIDTH * self.scale, INFO_HEIGHT * self.scale)

    def get_title_size(self):
        padding_h = TITLE_PADDING_H * self.scale
        padding_v = TITLE_PADDING_V * self.scale
        width = TITLE_WIDTH * self.scale
        height = TITLE_HEIGHT * self.scale - 2 * padding_v
        margin_between_icons = TITLE_MARGIN_BETWEEN_ICONS * self.scale
        margin_to_text = TITLE_MARGIN_FROM_ICON_TO_TEXT * self.scale
        return (width,
         height,
         padding_h,
         padding_v,
         margin_between_icons,
         margin_to_text)

    def get_faction_icon_size(self):
        faction = self.data.get('faction', None)
        icon_width, icon_height = FACTION_ICON_SIZE[faction] if faction else FACTION_ICON_SIZE_DEFAULT
        return (icon_width * self.scale, icon_height * self.scale)

    def get_mission_type_icon_size(self):
        return (ICON_MISSION_TYPE_WIDTH * self.scale, ICON_MISSION_TYPE_HEIGHT * self.scale)

    def get_results_size(self):
        faction_icon_width, _ = self.get_faction_icon_size()
        padding_l = RESULTS_PADDING_L * self.scale + faction_icon_width
        padding_t = RESULTS_PADDING_T * self.scale
        padding_b = RESULTS_PADDING_B * self.scale
        width = RESULTS_WIDTH * self.scale
        height = RESULTS_HEIGHT * self.scale - padding_t - padding_b
        return (width,
         height,
         padding_l,
         padding_t,
         padding_b)

    def get_result_rows_size(self):
        row_1_height = RESULTS_HEIGHT_ROW_1 * self.scale
        row_2_height = RESULTS_HEIGHT_ROW_2 * self.scale
        row_3_height = RESULTS_HEIGHT_ROW_3 * self.scale
        row_1_2_margin = RESULTS_MARGIN_1_2 * self.scale
        row_2_3_margin = RESULTS_MARGIN_2_3 * self.scale
        row_3_margin_base = RESULTS_ROW_3_MARGIN_BASE * self.scale
        row_3_margin_extras = RESULTS_ROW_3_MARGIN_EXTRAS * self.scale
        row_3_margin_time = RESULTS_ROW_3_MARGIN_TIME * self.scale
        return (row_1_height,
         row_1_2_margin,
         row_2_height,
         row_2_3_margin,
         row_3_height,
         row_3_margin_base,
         row_3_margin_extras,
         row_3_margin_time)

    def get_reward_level_icon_size(self):
        return (REWARD_LEVEL_ICON_BASE_WIDTH * self.scale,
         REWARD_LEVEL_ICON_BASE_HEIGHT * self.scale,
         REWARD_LEVEL_ICON_EXTRA_WIDTH * self.scale,
         REWARD_LEVEL_ICON_EXTRA_HEIGHT * self.scale)

    def get_completion_time_left(self, icon_base_width, icon_extra_width, row_3_margin_base, row_3_margin_extras, row_3_margin_time):
        num_of_extra_icons = len(self.reward_level_icons_extras)
        width_base = icon_base_width + row_3_margin_base
        width_extras = icon_extra_width * num_of_extra_icons + row_3_margin_extras * max(0, num_of_extra_icons - 1)
        left = width_base + width_extras + row_3_margin_time
        return left

    def get_rewards_size(self):
        padding_l = REWARDS_PADDING_L * self.scale
        padding_v = REWARDS_PADDING_V * self.scale
        width = REWARDS_WIDTH * self.scale
        height = REWARDS_HEIGHT * self.scale - 2 * padding_v
        internal_margin = REWARDS_INTERNAL_MARGIN * self.scale
        icon_margin = REWARDS_MARGIN_ICON * self.scale
        return (width,
         height,
         padding_l,
         padding_v,
         internal_margin,
         icon_margin)

    def get_reward_lp_icon_size(self):
        return REWARD_LP_ICON_SIZE * self.scale

    def get_reward_standings_icon_size(self):
        return REWARD_STANDINGS_ICON_SIZE * self.scale

    def get_reward_isk_icon_size(self):
        return REWARD_ISK_ICON_SIZE * self.scale

    def get_title_fontsize(self):
        return TITLE_FONTSIZE * self.scale

    def get_tier_fontsize(self):
        return TIER_FONTSIZE * self.scale

    def get_results_fontsize(self):
        return (TOTAL_ISK_FONTSIZE * self.scale, ISK_FONTSIZE * self.scale, TIME_FONTSIZE * self.scale)

    def get_rewards_text_fontsize(self):
        return REWARDS_TEXT_FONTSIZE * self.scale


class ActionButton(TextButtonWithBackgrounds):
    default_mouseUpBGTexture = None
    default_mouseEnterBGTexture = 'res:/UI/Texture/Classes/ResourceWars/resourceWars_Accept_Button_Highlight.png'
    default_mouseDownBGTexture = 'res:/UI/Texture/Classes/ResourceWars/resourceWars_Accept_Button_Highlight.png'
    default_mouseUpBGColor = (0.0, 0.0, 0.0, 0.7)
    default_mouseUpBGOpacity = 1.0
    default_mouseEnterBGOpacity = 0.75
    default_mouseDownBGOpacity = 0.9
    default_frameCornerSize = 7
    default_hoverSound = None
    default_selectSound = None
    default_mouseUpTextColor = (1.0, 1.0, 1.0, 0.9)
    default_mouseEnterTextColor = (0.0, 0.0, 0.0, 0.8)
    default_mouseDownTextColor = (0.0, 0.0, 0.0, 1.0)
    default_boldText = ButtonTextBoldness.ALWAYS_BOLD
