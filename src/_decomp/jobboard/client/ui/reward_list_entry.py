#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\reward_list_entry.py
import carbonui
import eveformat
import eveicon
import eveui
from carbonui import Align, uiconst, Density, TextColor
from eve.client.script.ui import eveColor
from eveicon import IconData
from jobboard.client.ui.base_list_entry import BaseJobListEntry
from jobboard.client.ui.claim_button import JobRewardClaimButton
from localization import GetByLabel
from jobboard.client.ui.util import select_redeem_location

class JobRewardListEntry(BaseJobListEntry):
    _has_error = False

    def __init__(self, controller, show_feature = False, *args, **kwargs):
        self.reward_icons = []
        self.reward_labels = []
        super(JobRewardListEntry, self).__init__(controller, show_feature, *args, **kwargs)

    def _on_job_updated(self):
        self._update_state()

    def _update_claimable_assets(self):
        if not self.job.has_claimable_rewards:
            self._update_reward_icon_and_label()
            return
        self.right_content_container.Flush()
        self._construct_claimable_assets()

    def _construct_left_side(self):
        self._construct_solar_system_chip()
        self._construct_left_content(self.left_container)
        self._construct_title_icons(self.left_container)
        title_container = eveui.Container(parent=self.left_container, align=Align.TOALL, clipChildren=True)
        carbonui.TextBody(parent=title_container, align=Align.CENTERLEFT, maxLines=1, text=self.job.title, bold=True, autoFadeSides=16)

    def _construct_right_side(self):
        self._error_indicator = eveui.Sprite(name='error_indicator', color=TextColor.DANGER, align=uiconst.TOPRIGHT, parent=self.right_container, texturePath=eveicon.difficulty, state=uiconst.UI_NORMAL if self._has_error else uiconst.UI_HIDDEN, padTop=1, width=16, height=17, hint=GetByLabel('UI/Corporations/Goals/ErrorWhileClaiming'))
        self._construct_cta_button()
        self.right_content_container = eveui.Container(name='right_content_container', parent=self.right_container, align=Align.TOALL, clipChildren=True)
        self._construct_right_content(self.right_content_container)

    def _construct_cta_button(self):
        if self.job.has_claimable_rewards:
            cta_cont = eveui.ContainerAutoSize(name='cta_cont', parent=self.right_container, align=uiconst.TORIGHT, padLeft=4)
            self._claim_button = self._construct_claim_button(cta_cont)

    def _construct_claim_button(self, parent):
        return JobRewardClaimButton(name='claim_button', parent=parent, align=Align.CENTERLEFT, density=Density.COMPACT, job=self.job, func=self.OnClaimButton)

    def _construct_right_content(self, parent):
        self._construct_claimable_assets()

    def _construct_claimable_assets(self):
        rewards = self.job.claimable_rewards
        self.reward_icons = []
        self.reward_labels = []
        for reward in rewards:
            self._construct_reward_icon_and_label(reward.icon, reward.amount_text)

    def _construct_reward_icon_and_label(self, icon, value_text):
        cont = eveui.ContainerAutoSize(parent=self.right_content_container, align=Align.TOLEFT, padRight=8)
        self.reward_icons.append(eveui.Sprite(parent=cont, align=eveui.Align.center_left, pos=(0, 0, 16, 16), texturePath=icon, color=TextColor.SECONDARY if isinstance(icon, IconData) else eveColor.WHITE))
        self.reward_labels.append(carbonui.TextBody(parent=cont, align=eveui.Align.center_left, left=20, maxLines=1, autoFadeSides=16, text=value_text, color=TextColor.NORMAL))

    def _update_reward_icon_and_label(self):
        for icon in self.reward_icons:
            eveui.animate(icon, 'color', end_value=TextColor.SUCCESS, duration=0.2, time_offset=0.2)

        for label in self.reward_labels:
            eveui.animate(label, 'color', end_value=TextColor.SUCCESS, duration=0.2, time_offset=0.2)

        self._claim_button.set_claimed()

    def start_claim_sequence(self):
        self._claim_button.start_claim_sequence()
        self.job.claim_rewards()

    def OnClaimButton(self, *args):
        if self._claim_button.busy:
            return
        if self.job.has_claimable_item_reward:
            should_claim = select_redeem_location([self.job])
            if not should_claim:
                return
        self.start_claim_sequence()

    def claim_reward(self):
        self.job.claim_rewards()

    def _flag_error(self):
        self._has_error = True
        self._error_indicator.Show()

    def _on_payment_complete(self, goal_id, *args, **kwargs):
        if goal_id != self.job.goal_id:
            return
        self._update_claimable_assets()

    def _on_payment_earned(self, goal_id, *args, **kwargs):
        if goal_id != self.job.goal_id:
            return
        self._update_claimable_assets()

    def _on_payment_failed(self, goal_id, *args, **kwargs):
        if goal_id != self.job.goal_id:
            return
        self._flag_error()
