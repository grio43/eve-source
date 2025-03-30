#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\client\rewardIcon.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall, Label
from eve.common.script.sys.eveCfg import IsPreviewable
from eveservices.menu import GetMenuService
from localization.formatters import FormatNumeric
from seasons.client.rewardTooltip import RewardTooltip
TEXTURE_PATH_FOLDER = 'res:/UI/Texture/classes/Seasons/Agency/ContentCard/'
TEXTURE_FRAME_CLAIMABLE_ALPHA = TEXTURE_PATH_FOLDER + 'alpha_ClaimRewardContainer.png'
TEXTURE_FRAME_CLAIMABLE_OMEGA = TEXTURE_PATH_FOLDER + 'omega_ClaimRewardContainer.png'
TEXTURE_FRAME_NOT_CLAIMABLE_ALPHA = TEXTURE_PATH_FOLDER + 'alphaRewardContainer.png'
TEXTURE_FRAME_NOT_CLAIMABLE_OMEGA = TEXTURE_PATH_FOLDER + 'omegaRewardContainer.png'
TEXTURE_FRAME_BACKGROUND_CLAIMABLE = TEXTURE_PATH_FOLDER + 'rewardClaimContainerBG.png'
TEXTURE_FRAME_BACKGROUND_NOT_CLAIMABLE = TEXTURE_PATH_FOLDER + 'rewardContainerBG.png'
TEXTURE_FRAME_BACKGROUND_OMEGA = TEXTURE_PATH_FOLDER + 'omega_rewardMouseOver.png'
TEXTURE_CLAIM_INDICATOR_ARROW = TEXTURE_PATH_FOLDER + 'rewardClaimButton.png'
TEXTURE_CLAIMED_CHECK = TEXTURE_PATH_FOLDER + 'checkmark_claimReward.png'
TEXTURE_OMEGA_ICON = TEXTURE_PATH_FOLDER + 'omegaIcon.png'
HEIGHT_CONTAINER_POINTS_LABEL = 18
WIDTH_FRAME_NOT_CLAIMABLE = 36
HEIGHT_FRAME_NOT_CLAIMABLE = 40
SIZE_ICON_NOT_CLAIMABLE = 28
WIDTH_FRAME_CLAIMABLE = 50
HEIGHT_FRAME_CLAIMABLE = 68
SIZE_ICON_CLAIMABLE = 40
SIZE_ICON_CLAIMED_CHECK = 36
HEIGHT_CLAIM_INDICATOR = 20
PADDING_CLAIM_INDICATOR_H = 1
PADDING_CLAIM_INDICATOR_BOTTOM = 2
SIZE_CLAIM_INDICATOR_ARROW_ICON = 12
HEIGHT_FRAME_POINTER = 4
SIZE_OMEGA_ICON_CLAIMABLE = 36
SIZE_OMEGA_ICON_NOT_CLAIMABLE = 18
WIDTH_BAR_MARKER = 2
COLOR_BAR_MARKER_NOT_ACHIEVED = (0.0, 0.0, 0.0, 1.0)
COLOR_BAR_MARKER_ACHIEVED_ALPHA = (0.0, 0.0, 0.0, 1.0)
COLOR_BAR_MARKER_ACHIEVED_OMEGA = (0.988, 0.761, 0.027, 1.0)
COLOR_POINTS_LABEL_NOT_ACHIEVED = (0.43, 0.43, 0.43, 1.0)
COLOR_POINTS_LABEL_ACHIEVED_ALPHA = (0.259, 0.631, 0.176, 1.0)
COLOR_POINTS_LABEL_ACHIEVED_OMEGA = (0.988, 0.761, 0.027, 1.0)
COLOR_FRAME_BACKGROUND = (0.0, 0.0, 0.0, 1.0)
COLOR_CLAIM = (0.21, 0.45, 0.18, 1.0)
COLOR_CLAIMED_CHECK = (0.38, 0.6, 0.3, 1.0)
COLOR_OMEGA_ICON = (0.988, 0.761, 0.027, 0.0)
OPACITY_FRAME_ALPHA = 0.6
OPACITY_FRAME_OMEGA = 1.0
OPACITY_ICON_OFF = 0.5
OPACITY_ICON_NORMAL = 1.0

class Reward(Container):

    def ApplyAttributes(self, attributes):
        super(Reward, self).ApplyAttributes(attributes)
        self.left -= self.width / 2
        reward = attributes.reward
        self.type_id = reward['reward_type_id']
        self.amount = reward['reward_amount']
        self.points_required = reward['points_required']
        self.reward_index = attributes.rewardIndex
        self.progress_bar_width = attributes.progressBarWidth
        self.progress_bar_height = attributes.progressBarHeight
        self.progress_bar_top = attributes.progressBarTop
        self.progress_bar_left = attributes.progressBarLeft
        self.points_label_top = attributes.pointsLabelTop
        self.seasons_service = attributes.seasonSvc
        self.clone_grade_service = sm.GetService('cloneGradeSvc')
        self.icon = None
        self.add_bar_marker()
        self.add_points_label()
        self.add_icon()
        self.update_reward(reward)

    def add_bar_marker(self):
        bar_marker_container = Container(name='bar_marker_container', parent=self, align=uiconst.TOBOTTOM_NOPUSH, height=self.progress_bar_height, top=self.progress_bar_top)
        self.bar_marker = Fill(name='bar_marker', parent=bar_marker_container, align=uiconst.CENTER, width=WIDTH_BAR_MARKER, height=bar_marker_container.height)

    def add_points_label(self):
        points_label_container = Container(name='points_label_container', parent=self, align=uiconst.TOBOTTOM_NOPUSH, height=HEIGHT_CONTAINER_POINTS_LABEL)
        self.points_label = EveLabelSmall(name='points_label', parent=points_label_container, align=uiconst.CENTER, text=FormatNumeric(int(self.points_required), useGrouping=True), bold=True, top=self.points_label_top)
        self.constraint_points_label_to_bar_width()

    def add_icon(self):
        self.icon = RewardIcon(name='icon_container', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, opacity=0.0, seasonsService=self.seasons_service, typeID=self.type_id, amount=self.amount, pointsRequired=self.points_required, rewardIndex=self.reward_index)

    def constraint_points_label_to_bar_width(self):
        label_left = self.left + self.width / 2 - self.points_label.width / 2
        extra_width_on_left_side = self.progress_bar_left - label_left
        if extra_width_on_left_side > 0:
            self.points_label.left += extra_width_on_left_side
            return
        label_right = self.left + self.width / 2 + self.points_label.width / 2
        extra_width_on_right_side = label_right - self.progress_bar_left - self.progress_bar_width
        if extra_width_on_right_side > 0:
            self.points_label.left -= extra_width_on_right_side

    def update_reward(self, reward_data):
        self.update_reward_data(reward_data)
        self.update_icon()
        self.update_bar_marker_color()
        self.update_points_label_color()

    def update_reward_data(self, reward):
        self.is_omega_only = reward['omega_only']
        self.is_available = not self.is_omega_only or self.clone_grade_service.IsOmega()
        self.is_achieved = reward['points_required'] <= self.seasons_service.get_points()
        self.is_claimed = reward['claimed']

    def update_icon(self):
        self.icon.update(self.is_omega_only, self.is_available, self.is_achieved, self.is_claimed)

    def update_bar_marker_color(self):
        self.bar_marker.color = self._get_bar_marker_color()

    def update_points_label_color(self):
        self.points_label.color = self._get_points_label_color()

    def _get_bar_marker_color(self):
        if self.is_achieved:
            if self.is_omega_only:
                return COLOR_BAR_MARKER_ACHIEVED_OMEGA
            else:
                return COLOR_BAR_MARKER_ACHIEVED_ALPHA
        return COLOR_BAR_MARKER_NOT_ACHIEVED

    def _get_points_label_color(self):
        if self.is_achieved:
            if self.is_omega_only:
                return COLOR_POINTS_LABEL_ACHIEVED_OMEGA
            else:
                return COLOR_POINTS_LABEL_ACHIEVED_ALPHA
        return COLOR_POINTS_LABEL_NOT_ACHIEVED


class RewardIcon(Container):

    def ApplyAttributes(self, attributes):
        super(RewardIcon, self).ApplyAttributes(attributes)
        self.seasons_service = attributes.seasonsService
        self.type_id = attributes.typeID
        self.amount = attributes.amount
        self.points_required = attributes.pointsRequired
        self.reward_index = attributes.rewardIndex
        self.add_tooltip()
        self.add_omega_overlay()
        self.add_claimed_check()
        self.add_icon()
        self.add_claim_indicator()
        self.add_omega_background()
        self.add_frame()

    def add_tooltip(self):
        self.tooltipPanelClassInfo = RewardTooltip(type_id=self.type_id, amount=self.amount, points=self.points_required)

    def add_omega_overlay(self):
        self.omega_icon = Sprite(name='omega_icon', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, texturePath=TEXTURE_OMEGA_ICON, color=COLOR_OMEGA_ICON)

    def add_claimed_check(self):
        self.claimed_check = Sprite(name='claimed_check', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, width=SIZE_ICON_CLAIMED_CHECK, height=SIZE_ICON_CLAIMED_CHECK, texturePath=TEXTURE_CLAIMED_CHECK, padTop=(SIZE_ICON_NOT_CLAIMABLE - SIZE_ICON_CLAIMED_CHECK) / 2, color=COLOR_CLAIMED_CHECK)

    def add_icon(self):
        self.icon = Container(name='type_icon_container', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED)
        quantity_container = ContainerAutoSize(name='quantity_container', parent=self.icon, align=uiconst.BOTTOMRIGHT, bgColor=(0.0, 0.0, 0.0, 0.6), opacity=1.0 if self.amount > 1.0 else 0.0)
        Label(name='quantity_label', parent=quantity_container, text=self.amount, maxLines=1, bold=True, fontsize=9, padding=(4, 1, 4, 1))
        type_icon = Icon(name='type_icon', parent=self.icon, align=uiconst.TOALL)
        type_icon.LoadIconByTypeID(self.type_id)

    def add_claim_indicator(self):
        self.claim_indicator = Container(name='claim_indicator', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, width=WIDTH_FRAME_CLAIMABLE - 2 * PADDING_CLAIM_INDICATOR_H, height=HEIGHT_CLAIM_INDICATOR, bgColor=COLOR_CLAIM, padBottom=PADDING_CLAIM_INDICATOR_BOTTOM)
        Sprite(name='claim_indicator_arrow', parent=self.claim_indicator, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=SIZE_CLAIM_INDICATOR_ARROW_ICON, height=SIZE_CLAIM_INDICATOR_ARROW_ICON, texturePath=TEXTURE_CLAIM_INDICATOR_ARROW)

    def add_omega_background(self):
        self.omega_background = Sprite(name='omega_background', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, width=WIDTH_FRAME_NOT_CLAIMABLE, height=HEIGHT_FRAME_NOT_CLAIMABLE, texturePath=TEXTURE_FRAME_BACKGROUND_OMEGA, opacity=0.0)

    def add_frame(self):
        self.frame = Frame(name='frame', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED)
        self.frame_background = Sprite(name='frame_background', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, color=COLOR_FRAME_BACKGROUND)

    def update(self, is_omega_only, is_available, is_achieved, is_claimed):
        self.opacity = 0.0
        uicore.animations.StopAllAnimations(self.claim_indicator)
        self.update_reward_data(is_omega_only, is_available, is_achieved, is_claimed)
        self.width, self.height = self._get_frame_sizes()
        self.top = self._get_top()
        self.frame.width, self.frame.height = self._get_frame_sizes()
        self.frame.SetTexturePath(self._get_frame_texture())
        self.frame.opacity = self._get_frame_opacity()
        self.frame_background.width, self.frame_background.height = self._get_frame_sizes()
        self.frame_background.SetTexturePath(self._get_frame_background_texture())
        self.icon.width, self.icon.height = self._get_icon_sizes()
        self.icon.top = self._get_icon_padding_v()
        self.icon.opacity = self._get_icon_opacity()
        self.claimed_check.opacity = 1.0 if self.is_claimed else 0.0
        self.claimed_check.top = self.icon.top
        self.claim_indicator.opacity = 1.0 if self.is_claimable else 0.0
        self.claim_indicator.top = self.icon.height + 2 * self.icon.top
        self._animate_claim_indicator()
        self.omega_icon.width, self.omega_icon.height = self._get_omega_icon_sizes()
        self.omega_icon.top = self.icon.top + (self.icon.height - self.omega_icon.height) / 2
        self.tooltipPanelClassInfo.update_reward(self.is_claimed, self.is_achieved, self.is_available)
        self.opacity = 1.0

    def update_reward_data(self, is_omega_only, is_available, is_achieved, is_claimed):
        self.is_omega_only = is_omega_only
        self.is_available = is_available
        self.is_achieved = is_achieved
        self.is_claimed = is_claimed
        self.is_claimable = self.is_achieved and self.is_available and not self.is_claimed

    def _get_top(self):
        if self.is_claimable:
            return 0
        return HEIGHT_FRAME_CLAIMABLE - HEIGHT_FRAME_NOT_CLAIMABLE

    def _get_frame_sizes(self):
        if self.is_claimable:
            return (WIDTH_FRAME_CLAIMABLE, HEIGHT_FRAME_CLAIMABLE)
        return (WIDTH_FRAME_NOT_CLAIMABLE, HEIGHT_FRAME_NOT_CLAIMABLE)

    def _get_icon_sizes(self):
        icon_size = SIZE_ICON_CLAIMABLE if self.is_claimable else SIZE_ICON_NOT_CLAIMABLE
        return (icon_size, icon_size)

    def _get_omega_icon_sizes(self):
        omega_icon_size = SIZE_OMEGA_ICON_CLAIMABLE if self.is_claimable else SIZE_OMEGA_ICON_NOT_CLAIMABLE
        return (omega_icon_size, omega_icon_size)

    def _get_icon_padding_v(self):
        _, frame_height = self._get_frame_sizes()
        _, icon_height = self._get_icon_sizes()
        available_height = frame_height - icon_height - HEIGHT_FRAME_POINTER
        if self.is_claimable:
            available_height -= HEIGHT_CLAIM_INDICATOR + PADDING_CLAIM_INDICATOR_BOTTOM
        return available_height / 2

    def _get_frame_texture(self):
        if self.is_claimable:
            if self.is_omega_only:
                return TEXTURE_FRAME_CLAIMABLE_OMEGA
            else:
                return TEXTURE_FRAME_CLAIMABLE_ALPHA
        else:
            if self.is_omega_only:
                return TEXTURE_FRAME_NOT_CLAIMABLE_OMEGA
            return TEXTURE_FRAME_NOT_CLAIMABLE_ALPHA

    def _get_frame_background_texture(self):
        if self.is_claimable:
            return TEXTURE_FRAME_BACKGROUND_CLAIMABLE
        return TEXTURE_FRAME_BACKGROUND_NOT_CLAIMABLE

    def _get_frame_opacity(self):
        if self.is_omega_only:
            return OPACITY_FRAME_OMEGA
        return OPACITY_FRAME_ALPHA

    def _get_icon_opacity(self):
        if self.is_claimed:
            return OPACITY_ICON_OFF
        return OPACITY_ICON_NORMAL

    def _animate_claim_indicator(self):
        if self.claim_indicator.opacity > 0.1:
            uicore.animations.FadeTo(self.claim_indicator, 0.3, 0.8, duration=1.6, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)

    def GetMenu(self):
        if not session.charid:
            return None
        return GetMenuService().GetMenuFromItemIDTypeID(None, self.type_id, ignoreMarketDetails=0)

    def OnClick(self, *args):
        if not session.charid:
            return
        if self.claim_reward():
            return
        self.show_reward_info()

    def OnMouseEnter(self, *args):
        super(RewardIcon, self).OnMouseEnter(*args)
        self.show_omega_overlay()

    def OnMouseExit(self, *args):
        super(RewardIcon, self).OnMouseExit(*args)
        self.hide_omega_overlay()

    def claim_reward(self):
        if self.is_claimable:
            return self.seasons_service.claim_goal_reward(self.reward_index)
        return False

    def show_reward_info(self):
        if IsPreviewable(self.type_id):
            sm.GetService('preview').PreviewType(self.type_id)
        else:
            sm.GetService('info').ShowInfo(typeID=self.type_id)

    def show_omega_overlay(self):
        if not self.is_omega_only or self.is_available:
            return
        self.icon.opacity = OPACITY_ICON_OFF
        self.omega_icon.opacity = 1.0
        self.omega_background.opacity = 1.0

    def hide_omega_overlay(self):
        self.icon.opacity = self._get_icon_opacity()
        self.omega_icon.opacity = 0.0
        self.omega_background.opacity = 0.0
