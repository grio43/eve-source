#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\windows\rewardview.py
import logging
import carbonui.const as uiconst
import localization
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import Label, EveCaptionSmall
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipDescription
from localization import GetByLabel
from projectdiscovery.client.projects.exoplanets.ui.processingcontainer import ProcessingContainer
from projectdiscovery.client.projects.exoplanets.ui.tiertracker import TierTracker
from projectdiscovery.client.ui.agents import get_agent
from projectdiscovery.client.util.util import calculate_rank_band
from projectdiscovery.common.const import ISK_MULTIPLIERS, TIERS
logger = logging.getLogger(__name__)

class RewardView(ProcessingContainer):
    __notifyevents__ = ['OnContinueToRewards',
     'OnContinueFromRewards',
     'OnRewardsViewHidden',
     'OnProjectDiscoveryExperience',
     'OnProjectDiscoveryLevelUp',
     'OnRewardViewVisible']

    def ApplyAttributes(self, attributes):
        super(RewardView, self).ApplyAttributes(attributes)
        self.XP_Reward = 0
        self.ISK_Reward = 0
        self.LOOT_Reward = 0
        self.TIER_Reward = False
        self.BONUS_XP = False
        self.text_container = None
        self.reward_container = None
        self.bonus_samples_left = 0
        self._is_tutorial = attributes.get('isTutorial', False)
        self.agent = get_agent()
        self.projectDiscoverySvc = sm.RemoteSvc('ProjectDiscovery')
        self.playerState = self.projectDiscoverySvc.get_player_state()
        self.experience = self.playerState.experience if self.playerState else 0
        self.player_rank = self.playerState.rank if self.playerState else 1
        self.total_xp_needed_for_current_rank = self.projectDiscoverySvc.get_total_needed_xp(self.player_rank)
        self.total_xp_needed_for_next_rank = self.projectDiscoverySvc.get_total_needed_xp(self.player_rank + 1)
        self.original_rank_band = calculate_rank_band(self.player_rank)
        self.rank_band = self.original_rank_band
        self.score_bar_height = 7
        self._setup_layout()
        sm.RegisterNotify(self)

    def _setup_layout(self):
        self._top_container = Container(name='TopContainer', parent=self._content, align=uiconst.TOTOP, height=250, top=30)
        self.main_container = Container(name='mainContainer', parent=self._top_container, align=uiconst.CENTERTOP, width=550, height=250)
        self.agent_container = Container(name='agentContainer', parent=self.main_container, align=uiconst.TOLEFT, width=200, left=5, top=5)
        self.agent_image = Sprite(name='agentImage', parent=self.agent_container, align=uiconst.TOTOP, height=200, texturePath='res:/UI/Texture/classes/ProjectDiscovery/DrMayor.png')
        self._label_container = Container(name='LabelContainer', parent=self.agent_container, align=uiconst.TOALL)
        self.agent_label = Label(name='agentName', parent=ContainerAutoSize(parent=self._label_container, align=uiconst.TOTOP), align=uiconst.CENTERTOP, text=localization.GetByLabel(self.agent.name), fontsize=14)
        Label(name='concordLabel', parent=ContainerAutoSize(parent=self._label_container, align=uiconst.TOTOP), align=uiconst.CENTERTOP, text=GetByLabel('UI/Chat/ChannelNames/Concord'), fontsize=12)
        self._right_container = Container(name='RightContainer', parent=self.main_container, align=uiconst.TOALL, padLeft=10)
        self._centering_container = ContainerAutoSize(name='CenteringContainer', parent=self._right_container, align=uiconst.CENTERLEFT, width=uicore.ReverseScaleDpi(self._right_container.displayWidth))
        self.header_message = EveCaptionSmall(parent=self._centering_container, align=uiconst.TOTOP)
        self.text_container = ScrollContainer(name='textContainer', parent=self._centering_container, align=uiconst.TOTOP, height=60)
        self.main_message = Label(parent=self.text_container, align=uiconst.TOTOP, fontSize=14, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ThanksMessage'))
        self._setup_reward_container()
        self._setup_tier_tracker()

    def _setup_tier_tracker(self):
        self._bottom_container = Container(name='BottomContainer', parent=self._content, align=uiconst.TOALL)
        self._rank_text_container = Container(name='RankTextContainer', parent=self._bottom_container, align=uiconst.TOTOP, height=50)
        self._rank_caption = EveCaptionSmall(name='RankCaption', parent=self._rank_text_container, align=uiconst.CENTERTOP, text='Rank 1 Novice Analyst')
        self._experience_label = Label(name='ExperienceLabel', parent=self._rank_text_container, align=uiconst.CENTERTOP, top=30, text='93 Total Experience Points - 44 until next rank')
        self._tier_tracker = TierTracker(name='Tiers', parent=self._bottom_container, align=uiconst.TOTOP, height=200, tierInfo=TIERS)

    def UpdateAlignment(self, *args, **kwargs):
        budget = super(RewardView, self).UpdateAlignment(*args, **kwargs)
        if not self.text_container:
            return budget
        if self.reward_container:
            self._centering_container.width = uicore.ReverseScaleDpi(self._right_container.displayWidth)
        return budget

    def _setup_reward_container(self):
        self.reward_container = ContainerAutoSize(name='reward_container', parent=self._centering_container, align=uiconst.TOTOP, height=40, padTop=5)

    def setup_experience_reward_container(self):
        if not self.XP_Reward:
            return
        self.experience_points_container = Container(parent=self.reward_container, width=110, height=40, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        self.experience_points_icon = Sprite(parent=Container(parent=self.experience_points_container, width=40, height=40, align=uiconst.TOLEFT), name='experience_points_Logo', align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/ProjectDiscovery/experiencePointsIcon.png', state=uiconst.UI_DISABLED)
        SetTooltipDescription(targetObject=self.experience_points_container, descriptionText=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ExperiencePointsLabel'))
        self.experience_points = Label(parent=Container(parent=self.experience_points_container, align=uiconst.TOLEFT, width=20, height=50), align=uiconst.CENTERLEFT, fontsize=16, text=self.XP_Reward if not self.BONUS_XP else '%s X 2' % (self.XP_Reward / 2))
        animations.MorphScalar(self, '_xp', 0, self.XP_Reward, duration=1, timeOffset=1)

    def setup_isk_reward_container(self, accuracy):
        if not self.ISK_Reward:
            return
        self.ISK_reward_container = Container(parent=self.reward_container, width=110, height=40, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        self.ISK_reward_icon = Sprite(parent=Container(parent=self.ISK_reward_container, width=40, height=40, align=uiconst.TOLEFT), name='ISK_reward_Logo', align=uiconst.TOALL, texturePath='res:/ui/texture/WindowIcons/wallet.png', state=uiconst.UI_DISABLED)
        SetTooltipDescription(targetObject=self.ISK_reward_container, descriptionText=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/IskLabel', Accuracy=round(accuracy * 100, 2), Multiplier=self.get_isk_mult(accuracy)))
        self.ISK_reward = Label(parent=Container(parent=self.ISK_reward_container, align=uiconst.TOLEFT, width=20, height=50), align=uiconst.CENTERLEFT, fontsize=16, text=0)
        animations.MorphScalar(self, '_isk', 0, self.ISK_Reward, duration=1, timeOffset=1)

    def setup_loot_reward_container(self):
        if not self.LOOT_Reward:
            return
        self.LOOT_reward_container = Container(parent=self.reward_container, width=110, height=40, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        self.LOOT_reward_icon = Sprite(parent=Container(parent=self.LOOT_reward_container, width=40, height=40, align=uiconst.TOLEFT), name='LOOT_reward_Logo', align=uiconst.TOALL, texturePath='res:/ui/texture/WindowIcons/cargocontainer.png', state=uiconst.UI_DISABLED)
        SetTooltipDescription(targetObject=self.LOOT_reward_container, descriptionText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/rewards/LootCrateLabel'))
        self.LOOT_reward = Label(parent=Container(parent=self.LOOT_reward_container, align=uiconst.TOLEFT, width=20, height=50), align=uiconst.CENTERLEFT, fontsize=16, text=self.LOOT_Reward)

    def get_accuracy(self):
        statistics = self.projectDiscoverySvc.get_player_statistics()
        if 'project' in statistics:
            accuracy = statistics['project']['score']
        else:
            accuracy = 50
        return 100 * accuracy

    def get_isk_mult(self, accuracy):
        if accuracy > 90:
            isk_multiplier = ISK_MULTIPLIERS[2]
        elif accuracy > 70:
            isk_multiplier = ISK_MULTIPLIERS[1]
        else:
            isk_multiplier = ISK_MULTIPLIERS[0]
        return isk_multiplier

    def OnContinueToRewards(self, result, is_tutorial_show = False, *args, **kwargs):
        if result:
            if self._is_tutorial and not is_tutorial_show:
                sm.ScatterEvent('OnContinueFromRewards')
                return
            accuracy = result['player']['score']
            self.state = uiconst.UI_NORMAL
            self.playerState = result['playerState']
            self._update_labels()
            self.fade_in_and_expand(callback=lambda : sm.ScatterEvent('OnRewardViewVisible'))
            self.reward_container.Flush()
            self.XP_Reward = result['XP_Reward']
            self.ISK_Reward = result['ISK_Reward']
            self.LOOT_Reward = result['loot_crates']
            self.TIER_Reward = result['tier_reward']
            self.BONUS_XP = result['gotBonusXP']
            self.bonus_samples_left = result['bonusSamplesAfterClassification']
            sm.ScatterEvent('OnBonusSamplesLeft', self.bonus_samples_left)
            self.setup_experience_reward_container()
            self.setup_isk_reward_container(accuracy)
            self.setup_loot_reward_container()
            self._update_main_message()

    def OnContinueFromRewards(self):
        self.fade_out_content_and_retract(callback=lambda : sm.ScatterEvent('OnRewardsViewHidden'))

    def OnRewardViewVisible(self):
        self._tier_tracker.fix_bar_offset_to_current_progression_length()

    def OnRewardsViewHidden(self):
        self.state = uiconst.UI_HIDDEN

    def _update_labels(self):
        try:
            rank = self.player_rank
            rank_title = localization.GetByLabel('UI/ProjectDiscovery/RankTitles/RankTitle' + str(self.rank_band))
            current_exp = self.experience
            remaining_exp = max(self.total_xp_needed_for_next_rank - current_exp, 0)
            self._rank_caption.SetText(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/RankDescription', Rank=rank, RankTitle=rank_title))
            self._experience_label.SetText(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/ExperienceDescription', CurrentExperience=current_exp, RemainingExperience=remaining_exp))
        except AttributeError:
            logger.warning('_update_labels: Attribute error', exc_info=1)

    def OnProjectDiscoveryExperience(self, experience):
        self.experience = experience
        self._update_labels()

    def OnProjectDiscoveryLevelUp(self, new_rank, xp_for_new_rank, xp_for_next_rank):
        self.total_xp_needed_for_current_rank = xp_for_new_rank
        self.total_xp_needed_for_next_rank = xp_for_next_rank
        self.player_rank = new_rank
        self.rank_band = calculate_rank_band(self.player_rank)
        self._update_labels()

    def _update_main_message(self):
        if self._is_tutorial:
            if self.ISK_Reward:
                self.header_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/rewardsScreen/TutorialCompletedLabel'))
                self.main_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/rewardsScreen/TutorialCompletedRewardMessage'))
            else:
                self.header_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/rewardsScreen/TutorialCompletedLabel'))
                self.main_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/rewardsScreen/TutorialCompletedNoRewardMessage'))
        elif self.ISK_Reward <= 0:
            self.header_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/Header'))
            self.main_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ThanksButNoRewardsMessage'))
        elif self.TIER_Reward:
            self.header_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/rewardsScreen/newTier'))
            self.main_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/rewardsScreen/NewTierMessage'))
        elif self.LOOT_Reward:
            self.header_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/NewRankHeader'))
            self.main_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/rewardsScreen/NewRankMessage'))
        elif self.BONUS_XP:
            self.header_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/Header'))
            self.main_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/rewardsScreen/BonusXPMessage'))
        else:
            self.header_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/Header'))
            self.main_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/rewardsScreen/StandardRewards'))
        self.main_message.ResolveAutoSizing()
        self.header_message.ResolveAutoSizing()
        self.reward_container.EnableAutoSize()

    @property
    def _isk(self):
        return self.ISK_Reward

    @_isk.setter
    def _isk(self, value):
        self.ISK_Reward = int(round(value))
        self.ISK_reward.SetText(self.ISK_Reward)

    @property
    def _xp(self):
        return self.XP_Reward

    @_xp.setter
    def _xp(self, value):
        self.XP_Reward = int(round(value))
        self.experience_points.SetText(self.XP_Reward if not self.BONUS_XP else '%s X 2' % (self.XP_Reward / 2))
