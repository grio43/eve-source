#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\rewardcont.py
import gametime
import mathext
import trinity
from agentinteraction.constUI import PADDING_SMALLER, HEADER_SIZE_MEDIUM, PADDING_SMALL
from agentinteraction.reward import RewardType
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.timerstuff import AutoTimer
import carbonui
from carbonui import uiconst, TextAlign
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from clonegrade.const import CLONE_STATE_ALPHA, CLONE_STATE_OMEGA
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveIcon import GetOwnerLogo
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.control.infoIcon import MoreInfoIconBeta
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.shared.tooltip.blueprints import AddBlueprintInfo
from eve.common.lib.vgsConst import CATEGORYTAG_GAMETIME
from eve.common.script.sys.idCheckers import IsOwner
from evetypes import GetName
from localization import GetByLabel
TITLE_HEIGHT = 29
REWARD_ICON_SIZE = 64
REWARD_ICON_CONT_SIZE = 84
REWARD_TEXT_HEIGHT = 35
REWARD_TEXT_TOP_PADDING = 6
GAUGE_WIDTH = 16
REWARD_CONTAINER_HEIGHT = TITLE_HEIGHT + PADDING_SMALLER + REWARD_ICON_CONT_SIZE + REWARD_TEXT_TOP_PADDING + REWARD_TEXT_HEIGHT
REWARD_TITLE_BY_TYPE = {RewardType.NORMAL: 'UI/Agents/StandardMission/RewardsTitle',
 RewardType.BONUS: 'UI/Agents/StandardMission/BonusRewardsTitle'}
CLONE_STATE_BADGE_SIZE = 24
OMEGA_UPSELL_LEFT = 32
OMEGA_UPSELL_INFO_WIDTH = 186
OMEGA_UPSELL_INFO_PADDING_H = 13

class RewardTypeCont(ContainerAutoSize):
    default_name = 'RewardTypeCont'
    default_height = REWARD_CONTAINER_HEIGHT
    default_alignMode = uiconst.TOLEFT
    default_title_color = carbonui.TextColor.HIGHLIGHT

    def ApplyAttributes(self, attributes):
        super(RewardTypeCont, self).ApplyAttributes(attributes)
        hint_text = attributes.hint_text
        reward_type = attributes.reward_type
        title_color = attributes.title_color if attributes.title_color else self.default_title_color
        self.current_rewards = set()
        self.title_cont = Container(name='title_container_%s_rewards' % reward_type, parent=self, align=uiconst.TOTOP, padBottom=PADDING_SMALLER)
        self._build_title_text(reward_type, title_color)
        self._build_hint(hint_text)
        self.title_cont.height = self.title_label.height
        self.minWidth = self.title_label.width
        self.tile_cont = ContainerAutoSize(name='tile_cont', parent=self, align=uiconst.TOLEFT)
        self._update_sizes()

    def add_rewards(self, rewards, reward_type):
        for reward in rewards:
            if reward.quantity > 0:
                self._add_reward(reward, reward_type)

        self.update_info(rewards)
        if self.get_amount_of_rewards() > 0:
            self.Show()
        else:
            self.Hide()

    def get_amount_of_rewards(self):
        return len(self.current_rewards)

    def _build_title_text(self, reward_type, title_color):
        self.title_text_cont = ContainerAutoSize(name='self.title_text_cont', parent=self.title_cont, align=uiconst.TOLEFT, alignMode=uiconst.CENTERLEFT)
        self.title_label = carbonui.TextHeader(name='title_%s_rewards' % reward_type, parent=self.title_text_cont, align=uiconst.CENTERLEFT, text=GetByLabel(REWARD_TITLE_BY_TYPE[reward_type]), color=title_color)

    def _build_hint(self, hint_text):
        self.hint_cont = Container(name='hint_cont', parent=self.title_cont, align=uiconst.TOLEFT)
        self.hint_icon = MoreInfoIconBeta(parent=self.hint_cont, align=uiconst.CENTERLEFT, left=4)
        self.hint_cont.width = self.hint_icon.width
        self._set_hint_text(hint_text)

    def _set_hint_text(self, hint_text):
        self.hint_icon.hint = hint_text
        self.hint_cont.display = bool(self.hint_icon.hint)

    def flush_content(self):
        self.tile_cont.Flush()

    def _add_reward(self, reward, reward_type):
        type_id = reward.type_id
        self.current_rewards.add((type_id, reward_type))
        RewardCont(name='container_%s_reward_%s' % (reward_type, type_id), parent=self.tile_cont, align=uiconst.TOLEFT, padRight=PADDING_SMALL, state=uiconst.UI_NORMAL, reward=reward, reward_type=reward_type)

    def get_current_rewards(self):
        return self.current_rewards

    def clear_current_rewards(self):
        self.current_rewards = set()

    def update_info(self, rewards):
        pass

    def _update_sizes(self):
        self.minWidth = self.title_label.width + self._get_hint_width()

    def _get_hint_width(self):
        if self.hint_cont.display:
            return self.hint_cont.width + self.hint_cont.left
        return 0


class BonusRewardTypeCont(RewardTypeCont):
    default_name = 'BonusRewardTypeCont'
    default_height = REWARD_CONTAINER_HEIGHT
    default_alignMode = uiconst.TOLEFT

    def ApplyAttributes(self, attributes):
        self.timer_cont = None
        super(BonusRewardTypeCont, self).ApplyAttributes(attributes)
        self._build_timer_cont()

    def _build_timer_cont(self):
        if self.timer_cont and not self.timer_cont.destroyed:
            return self.timer_cont
        self.timer_cont = TimerCont(parent=self.title_cont)
        return self.timer_cont

    def update_info(self, rewards):
        self.update_expiry_time(rewards)
        self._update_sizes()

    def update_expiry_time(self, rewards):
        reward_with_earliest_expiry = None
        expiry_times = [ x for x in rewards if x.get_bonus_expiry_time() ]
        if expiry_times:
            expiry_times = sorted(expiry_times, key=lambda x: x.get_bonus_expiry_time() is not None)
            reward_with_earliest_expiry = expiry_times[0]
        hint = self._get_hint_text(rewards)
        if not reward_with_earliest_expiry:
            self.timer_cont.display = False
            self._set_hint_text(hint)
            return
        self._set_hint_text('')
        self.timer_cont.hint = hint
        self.timer_cont.display = True
        self.timer_cont.update_expiry_time(reward_with_earliest_expiry)
        self._update_sizes()

    def _get_hint_text(self, rewards):
        hint = ''
        bonus_times = filter(None, [ x.get_time_bonus() for x in rewards ])
        if bonus_times:
            bonus_time = min(bonus_times)
            hint = GetByLabel('UI/Agents/StandardMission/BonusRewardsHeader2', timeRemaining=bonus_time)
        return hint

    def _update_sizes(self):
        self.minWidth = self.title_label.width + self._get_timer_width() + self._get_hint_width()

    def _get_timer_width(self):
        if not self.timer_cont:
            return 0
        return self.timer_cont.get_counter_width()


class RewardCont(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(RewardCont, self).ApplyAttributes(attributes)
        self.reward = attributes.reward
        self.reward_type = attributes.reward_type
        self.reward_type_id = self.reward.type_id
        self.icon_parent_cont = Container(name='icon_parent_cont', parent=self, width=REWARD_ICON_CONT_SIZE, height=REWARD_ICON_CONT_SIZE, align=uiconst.TOPLEFT)
        self._add_icon(self.icon_parent_cont, self.reward_type_id)
        self._add_label(parent=self)
        self._add_clone_state_ui()

    def _add_icon(self, parent, type_id, size = REWARD_ICON_SIZE):
        self.icon_cont = Container(name='icon_cont', parent=parent, width=REWARD_ICON_CONT_SIZE, height=REWARD_ICON_CONT_SIZE, align=uiconst.CENTERTOP)
        icon_name = 'icon_{type_id}'.format(type_id=type_id)
        if IsOwner(type_id):
            GetOwnerLogo(ownerID=type_id, name=icon_name, parent=self.icon_cont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, size=size)
        else:
            if self.reward.is_blueprint_copy():
                bpData = sm.GetService('blueprintSvc').GetBlueprintTypeCopy(self.reward.type_id, original=False, runsRemaining=self.reward.get_runs_remaining(), materialEfficiency=self.reward.get_material_level(), timeEfficiency=self.reward.get_productivity_level())
            else:
                bpData = None
            self.reward_icon = ItemIcon(name=icon_name, parent=self.icon_cont, align=uiconst.CENTER, width=size, height=size, showOmegaOverlay=False, typeID=type_id, bpData=bpData)
            self.reward_icon.icon.spriteEffect = trinity.TR2_SFX_MODULATE
            self.reward_icon.icon.SetSecondaryTexturePath('res:/UI/Texture/Classes/AgentInteraction/panel1Corner_Solid_64.png')
            self.reward_icon.LoadTooltipPanel = self._reward_tooltip_panel
            if not self.reward.is_normal_type():
                self.reward_icon.state = uiconst.UI_DISABLED
        background_name = 'background_reward_%s_%s' % (self.reward_type, self.reward_type_id)
        self._add_background(parent=self.icon_cont, name=background_name, color=(1.0, 1.0, 1.0, 0.1))

    def _reward_tooltip_panel(self, tooltip_panel, *args):
        tooltip_panel.LoadGeneric2ColumnTemplate()
        tooltip_panel.margin = (12, 8, 12, 8)
        tooltip_panel.AddLabelMedium(text=GetName(self.reward.type_id), colSpan=2, bold=True, wrapWidth=200)
        if self.reward_icon.bpData:
            AddBlueprintInfo(tooltip_panel, typeID=self.reward.type_id, bpData=self.reward_icon.bpData)

    def _add_background(self, parent, name, color):
        background_container = Container(name='container_%s' % name, parent=parent, state=uiconst.UI_DISABLED)
        Frame(name='stroke_frame_%s' % name, parent=background_container, color=color, cornerSize=9, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Stroke.png')
        Frame(name='solid_frame_%s' % name, parent=background_container, color=color, cornerSize=9, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png')

    def _add_label(self, parent, use_omega_quantity = False):
        label_cont = Container(name='label_cont', parent=parent, align=uiconst.TOPLEFT, width=REWARD_ICON_CONT_SIZE, height=REWARD_TEXT_HEIGHT + REWARD_TEXT_TOP_PADDING, clipChildren=True, top=REWARD_ICON_CONT_SIZE, padTop=REWARD_TEXT_TOP_PADDING, hint=self.reward.get_hint(use_omega_quantity), state=uiconst.UI_NORMAL)
        carbonui.TextBody(name='label_%s_reward_%s' % (self.reward_type, self.reward_type_id), parent=label_cont, align=uiconst.TOTOP, text=self.reward.get_text(use_omega_quantity), color=carbonui.TextColor.HIGHLIGHT, textAlign=TextAlign.LEFT)

    def _add_clone_state_ui(self):
        alpha_quantity = self.reward.alpha_quantity or self.reward.quantity
        omega_quantity = self.reward.omega_quantity or self.reward.quantity
        if alpha_quantity == omega_quantity:
            return
        clone_state = sm.GetService('cloneGradeSvc').GetCloneGrade()
        self._add_clone_state_badge(clone_state, parent=self.icon_parent_cont)
        self._add_omega_upsell(clone_state)

    def _add_clone_state_badge(self, clone_state, parent):
        texture_path = None
        if clone_state == CLONE_STATE_ALPHA:
            texture_path = 'res:/UI/Texture/Classes/CloneGrade/Alpha_32.png'
        elif clone_state == CLONE_STATE_OMEGA:
            texture_path = 'res:/UI/Texture/Classes/CloneGrade/Omega_24.png'
        if not texture_path:
            return
        offset = -CLONE_STATE_BADGE_SIZE / 2
        Sprite(name='clone_state_badge', parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=CLONE_STATE_BADGE_SIZE, height=CLONE_STATE_BADGE_SIZE, texturePath=texture_path, top=offset, left=parent.width + offset, idx=0)

    def _add_omega_upsell(self, clone_state):
        if clone_state != CLONE_STATE_ALPHA:
            return
        omega_vs_alpha_ratio = self.reward.get_omega_vs_alpha_ratio()
        if not omega_vs_alpha_ratio:
            return
        omega_upsell_container = Container(name='omega_upsell_container', parent=self, width=REWARD_ICON_CONT_SIZE + OMEGA_UPSELL_INFO_WIDTH, height=REWARD_ICON_CONT_SIZE + REWARD_TEXT_HEIGHT + REWARD_TEXT_TOP_PADDING, align=uiconst.TOPLEFT, left=REWARD_ICON_CONT_SIZE + OMEGA_UPSELL_LEFT)
        omega_upsell_top_container = Container(name='omega_upsell_top_container', parent=omega_upsell_container, width=REWARD_ICON_CONT_SIZE + OMEGA_UPSELL_INFO_WIDTH, height=REWARD_ICON_CONT_SIZE, align=uiconst.TOPLEFT)
        omega_upsell_icon_parent_container = Container(name='omega_upsell_icon_parent_container', parent=omega_upsell_top_container, width=REWARD_ICON_CONT_SIZE, height=REWARD_ICON_CONT_SIZE, align=uiconst.TOPLEFT)
        self._add_icon(omega_upsell_icon_parent_container, self.reward_type_id)
        self._add_upsell_info(omega_upsell_container, omega_vs_alpha_ratio)
        self._add_label(parent=omega_upsell_container, use_omega_quantity=True)
        background_color = Color(*eveColor.SAND_YELLOW).SetOpacity(0.1).GetRGBA()
        self._add_background(parent=omega_upsell_top_container, name='omega_upsell_background', color=background_color)

    def _add_upsell_info(self, parent, omega_vs_alpha_ratio):
        upsell_info_container = Container(name='upsell_info_container', parent=parent, width=OMEGA_UPSELL_INFO_WIDTH, height=REWARD_ICON_CONT_SIZE, align=uiconst.TOPLEFT, left=REWARD_ICON_CONT_SIZE, state=uiconst.UI_NORMAL)
        upsell_info_label_container = Container(name='upsell_info_label_container', parent=upsell_info_container, align=uiconst.CENTER, width=OMEGA_UPSELL_INFO_WIDTH, height=REWARD_ICON_CONT_SIZE, clipChildren=True, padding=(OMEGA_UPSELL_INFO_PADDING_H,
         0,
         OMEGA_UPSELL_INFO_PADDING_H,
         0))
        omega_vs_alpha_ratio = round(omega_vs_alpha_ratio, ndigits=2)
        if float(omega_vs_alpha_ratio).is_integer():
            omega_vs_alpha_ratio = int(omega_vs_alpha_ratio)
        text = GetByLabel('UI/Agents/StandardMission/OmegaUpsell', omegaVsAlphaRatio=omega_vs_alpha_ratio, typeName=GetName(self.reward_type_id))
        carbonui.TextBody(name='upsell_info_label', parent=upsell_info_label_container, align=uiconst.CENTER, text=text, color=carbonui.TextColor.HIGHLIGHT, textAlign=TextAlign.LEFT, maxWidth=upsell_info_label_container.width - 2 * OMEGA_UPSELL_INFO_PADDING_H)
        self._add_clone_state_badge(clone_state=CLONE_STATE_OMEGA, parent=upsell_info_container)
        upsell_info_container.OnClick = self._see_omega_in_new_eden_store
        self.icon_cont.OnClick = self._see_omega_in_new_eden_store

    def _see_omega_in_new_eden_store(self, *args, **kwargs):
        sm.GetService('vgsService').OpenStore(categoryTag=CATEGORYTAG_GAMETIME)


class TimerCont(ContainerAutoSize):
    default_name = 'timer_cont'
    default_align = uiconst.TOLEFT
    default_alignMode = uiconst.TOLEFT
    default_padLeft = 12
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        self.reward_with_timer_info = None
        self.expiry_thread = None
        super(TimerCont, self).ApplyAttributes(attributes)
        gauge_size = GAUGE_WIDTH
        self.gauge_cont = Container(name='gauge_cont', parent=self, align=uiconst.TOLEFT, width=GAUGE_WIDTH)
        self.gauge_circular = GaugeCircular(parent=self.gauge_cont, showMarker=False, align=uiconst.CENTER, colorStart=eveColor.CRYO_BLUE, colorEnd=eveColor.CRYO_BLUE, radius=GAUGE_WIDTH / 2, state=uiconst.UI_DISABLED)
        self.text_cont = ContainerAutoSize(name='text_cont', parent=self, align=uiconst.TOLEFT, height=gauge_size + 4)
        self.timer_label = carbonui.TextBody(name='timer_label', parent=self.text_cont, align=uiconst.CENTERLEFT, maxLines=1, color=carbonui.TextColor.HIGHLIGHT, text=' ', left=8)

    def update_expiry_time(self, reward):
        self.reward_with_timer_info = reward
        self.update_expiry_elements_thread(animate=False)
        self.expiry_thread = AutoTimer(500, self.update_expiry_elements_thread)

    def update_expiry_elements_thread(self, animate = True):
        if self.destroyed:
            self.expiry_thread = None
            return
        if self.reward_with_timer_info is None:
            return
        reward_expiry_time = self.reward_with_timer_info.get_bonus_expiry_time()
        diff = reward_expiry_time - gametime.GetWallclockTime()
        is_expired = diff < 0
        if is_expired:
            self.set_as_expired(animate)
            return
        diff = max(0, diff)
        self.timer_label.text = FmtDate(diff, 'ss')
        bonus_progress = self.reward_with_timer_info.get_bonus_progress()
        progress = mathext.clamp(bonus_progress, 0, 1.0)
        self.gauge_circular.SetValue(1 - progress, animate=animate)

    def set_as_expired(self, animate):
        self.expiry_thread = None
        self.timer_label.text = GetByLabel('UI/Agents/StandardMission/BonusRewardsAreExpired')
        self.timer_label.SetAlpha(0.5)
        self.gauge_circular.SetValue(0.0, animate=animate)

    def get_counter_width(self):
        if not self.display:
            return 0
        return self.gauge_cont.width + self.timer_label.width + self.timer_label.left
