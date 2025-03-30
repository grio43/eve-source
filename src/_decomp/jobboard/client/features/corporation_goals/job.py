#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\corporation_goals\job.py
import caching
import eveicon
import localization
import logging
from assetholding.client.qa import get_entitlement_qa_menu_entries
from corporation.client.goals import goalSignals
from corporation.client.goals import goalsUtil
from corporation.client.goals.goalsController import CorpGoalsController
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.neocom.corporation.corpPanelConst import CorpPanel
from eve.client.script.ui.shared.neocom.corporation.corp_goals.forms import goalForms
from eveformat import currency
from jobboard.client.job import BaseJob
from jobboard.client.features.corporation_goals.claimable_reward_button import ClaimableRewardButton, ClaimableRewardControllerStub
from jobboard.client.util import add_track_job_menu_option, add_open_job_menu_option
from jobboard.client.qa_tools import is_qa
from utillib import KeyVal
from .card import CorporationGoalCard, CorporationGoalListEntry, CorporationGoalRewardListEntry
from .tooltips import GoalRewardToolTip
from .info_panel_entry import CorporationJobInfoPanelEntry
from .page import CorporationGoalPage
logger = logging.getLogger('corporation_goals')
CORP_JOB_OBJECTIVE_CHAIN_ID = 46
LIMITED_CORP_JOB_OBJECTIVE_CHAIN_ID = 82
MANUAL_OBJECTIVE_CHAIN_ID = 50

class CorporationGoalJob(BaseJob):
    PAGE_CLASS = CorporationGoalPage
    CARD_CLASS = CorporationGoalCard
    LIST_ENTRY_CLASS = CorporationGoalListEntry
    REWARD_LIST_ENTRY_CLASS = CorporationGoalRewardListEntry
    INFO_PANEL_ENTRY_CLASS = CorporationJobInfoPanelEntry

    def __init__(self, job_id, provider, corporation_goal):
        self._corporation_goal = corporation_goal
        self._objectives_context = None
        content_id = self.goal_id
        super(CorporationGoalJob, self).__init__(job_id, content_id, provider)

    def update(self, goal = None, *args, **kwargs):
        if goal:
            self._corporation_goal = goal
        self._update_context()
        super(CorporationGoalJob, self).update(*args, **kwargs)

    @property
    def id(self):
        return self._job_id

    @property
    def goal_id(self):
        return self._corporation_goal.goal_id

    @property
    def goal(self):
        return self._corporation_goal

    @property
    def title(self):
        return self._corporation_goal.name

    @property
    def feature_title(self):
        return self._corporation_goal.contribution_method.title

    @property
    def description(self):
        return self._corporation_goal.description

    @property
    def current_progress(self):
        return self._corporation_goal.current_progress

    @property
    def desired_progress(self):
        return self._corporation_goal.desired_progress

    @property
    def target_progress(self):
        return self._corporation_goal.desired_progress

    @property
    def progress_percentage(self):
        return self._corporation_goal.get_progress_ratio()

    @property
    def personal_progress(self):
        return self._corporation_goal.get_my_progress()

    @property
    def personal_progress_limit(self):
        if self.participation_limit:
            return self.participation_limit
        return self.desired_progress

    @property
    def personal_progress_percentage(self):
        if self.personal_progress is 0:
            return 0
        if self.participation_limit:
            return self.personal_progress / float(self.participation_limit)
        return self.personal_progress / float(self.desired_progress)

    @property
    def progress_title(self):
        return self._corporation_goal.contribution_method.title

    @property
    def contribution_method(self):
        return self._corporation_goal.contribution_method

    @property
    def goal_state(self):
        return self._corporation_goal.state

    @property
    def creator_id(self):
        return self._corporation_goal.creator

    @property
    def creator_name(self):
        creator_info = cfg.eveowners.GetIfExists(self.creator_id)
        if creator_info:
            return creator_info.name
        return ''

    @property
    def corporation_id(self):
        return session.corpid

    @property
    def corporation_name(self):
        corporation_info = cfg.eveowners.GetIfExists(self.corporation_id)
        if corporation_info:
            return corporation_info.name
        return ''

    @property
    def creation_date(self):
        return self._corporation_goal.created

    @property
    def is_available_in_browse(self):
        if not super(CorporationGoalJob, self).is_available_in_browse:
            return False
        return self.can_contribute_to()

    @property
    def is_available_in_active(self):
        if not self.is_active:
            return False
        if self.is_tracked:
            return True
        return self.personal_progress and self.can_contribute_to()

    @property
    def is_trackable(self):
        return self.is_active

    @property
    def is_linkable(self):
        return not self.is_removed

    @property
    def is_active(self):
        return self._corporation_goal.is_active() and not self.is_removed

    @property
    def is_completed(self):
        return self._corporation_goal.is_completed()

    @property
    def is_closed(self):
        return self._corporation_goal.is_closed()

    @property
    def is_expired(self):
        return self._corporation_goal.is_expired()

    @property
    def has_rewards(self):
        return self.goal.has_rewards()

    @property
    def reward_amount_per_contribution(self):
        return self.goal.get_isk_per_contribution()

    @property
    def earned_amount(self):
        return self.goal.get_earned_amount()

    @property
    def claimed_amount(self):
        return self.goal.get_claimed_amount()

    @property
    def unclaimed_amount(self):
        return self.goal.get_unclaimed_amount()

    @property
    def has_claimable_rewards(self):
        return self.goal.has_unclaimed_reward()

    @property
    def has_available_rewards(self):
        return self.goal.has_available_rewards()

    @property
    def claimable_rewards(self):
        reward = self.goal.get_claimable_reward()
        if reward:
            return [reward]
        return []

    @property
    def expiration_time(self):
        return self.goal.expiration_time

    @property
    def end_time(self):
        return self.goal.get_end_time()

    @property
    def participation_limit(self):
        return self._corporation_goal.get_participation_limit()

    def can_contribute_to(self):
        return self.is_active and self.get_my_remaining_progress() > 0

    def get_isk_payout_remaining(self):
        return self.goal.get_total_remaining_isk()

    def get_my_isk_payout_remaining(self):
        return self.get_my_remaining_progress() * self.reward_amount_per_contribution

    def get_my_progress(self):
        return self.goal.get_my_progress()

    def get_my_remaining_progress(self):
        return self.goal.get_my_remaining_progress()

    def get_my_total_progress(self):
        return self.goal.get_my_total_progress()

    def get_total_rewards(self):
        return self.goal.get_desired_progress() * self.reward_amount_per_contribution

    def get_allocated_payment(self):
        return self.goal.get_current_progress() * self.reward_amount_per_contribution

    def claim_rewards(self):
        CorpGoalsController.get_instance().redeem_reward(self.goal_id)

    def is_ship_insurance(self):
        return self.goal.is_ship_insurance()

    def get_formatted_coverage_ratio(self):
        return u'{}%'.format(self.goal.get_multiplier_percentage())

    def get_coverage_per_loss(self):
        return self.goal.get_coverage_limit()

    @caching.lazy_property
    def objective_chain(self):
        from objectives.client.objective_chain import ObjectiveChain
        from objectives.common.objective_context import ObjectivesContext
        if self._corporation_goal.has_personal_progress():
            if self.participation_limit:
                objective_chain_id = LIMITED_CORP_JOB_OBJECTIVE_CHAIN_ID
            else:
                objective_chain_id = CORP_JOB_OBJECTIVE_CHAIN_ID
        else:
            objective_chain_id = MANUAL_OBJECTIVE_CHAIN_ID
        self._objectives_context = ObjectivesContext()
        self._update_context()
        objective_chain = ObjectiveChain(content_id=objective_chain_id, context=self._objectives_context, overrides={'progress': KeyVal(title=self.contribution_method.title_id)})
        objective_chain.start()
        return objective_chain

    def get_cta_buttons(self):
        return [ClaimableRewardButton(job=self, controller=ClaimableRewardControllerStub(), tooltipCls=GoalRewardToolTip, label=localization.GetByLabel('UI/Corporations/Goals/ClaimValue', rewardValue=currency.isk(self.unclaimed_amount)))]

    def get_buttons(self):
        buttons = super(CorporationGoalJob, self).get_buttons()
        if goalsUtil.CanAuthorGoals():
            buttons.append({'icon': eveicon.copy,
             'on_click': self._open_clone_view,
             'hint': localization.GetByLabel('UI/Corporations/Goals/CloneProject')})
            if self.is_active:
                buttons.append({'icon': eveicon.edit,
                 'on_click': self._open_edit_view,
                 'hint': localization.GetByLabel('UI/Corporations/Goals/ViewAdminDetails')})
        buttons.append({'icon': eveicon.open_window,
         'on_click': self._open_corporation_goal_window,
         'hint': localization.GetByLabel('UI/Opportunities/OpenCorporationProjects')})
        return buttons

    def get_menu(self):
        if self.is_removed:
            return []
        menu = goalsUtil.get_menu_for_corp_job(self.goal)
        menu.AddSeparator()
        add_open_job_menu_option(menu, self.job_id)
        menu.AddSeparator()
        add_track_job_menu_option(menu, self)
        if is_qa() and self._corporation_goal:
            asset_ids = [ reward.asset_id for reward in self.claimable_rewards ]
            if len(asset_ids) > 0:
                qa_entries = get_entitlement_qa_menu_entries(asset_ids, self.goal_id)
                menu.extend(qa_entries)
        return menu

    def get_state_info(self):
        if self.is_closed:
            return {'text': localization.GetByLabel('UI/Generic/Closed'),
             'color': eveColor.WARNING_ORANGE,
             'icon': eveicon.close}
        return super(CorporationGoalJob, self).get_state_info()

    def get_detailed_state_info(self):
        ret = {}
        if self.is_completed:
            ret = {'text': localization.GetByLabel('UI/Generic/Completed'),
             'color': eveColor.SUCCESS_GREEN,
             'icon_color': eveColor.PLATINUM_GREY,
             'icon': 'res:/ui/Texture/classes/Menu/Icons/checkmark.png'}
        elif self.is_expired:
            ret = {'text': localization.GetByLabel('UI/Generic/Expired'),
             'color': eveColor.DANGER_RED,
             'icon_color': eveColor.DANGER_RED,
             'icon': eveicon.hourglass,
             'inner_display': False}
        elif self.is_removed:
            ret = {'text': localization.GetByLabel('UI/Opportunities/RemovedState'),
             'color': eveColor.WARNING_ORANGE,
             'icon_color': eveColor.WARNING_ORANGE,
             'icon': eveicon.close,
             'inner_display': False}
        if self.is_closed:
            ret = {'text': localization.GetByLabel('UI/Generic/Closed'),
             'color': eveColor.WARNING_ORANGE,
             'icon_color': eveColor.WARNING_ORANGE,
             'icon': eveicon.close,
             'inner_display': False}
        if self.participation_limit:
            if self.get_my_remaining_progress() <= 0:
                ret['icon'] = 'res:/ui/Texture/classes/Menu/Icons/checkmark.png'
                ret['icon_color'] = eveColor.PLATINUM_GREY
                ret['inner_color'] = eveColor.SUCCESS_GREEN
        if len(ret):
            return ret

    def _get_content_tag_ids(self):
        return goalsUtil.get_content_tags_for_corp_goal(self._corporation_goal)

    def _open_corporation_goal_window(self):
        sm.GetService('corpui').Show(CorpPanel.PROJECTS)

    def _open_edit_view(self):
        goalSignals.on_view_details(self.job_id)

    def _open_clone_view(self):
        goalForms.OpenDuplicateGoalFormWindow(self.goal)

    def _update_context(self):
        if not self._objectives_context:
            return
        self._objectives_context.update_value(key='target_progress', value=self.target_progress)
        self._objectives_context.update_value(key='current_progress', value=self.current_progress)
        self._objectives_context.update_value(key='personal_progress', value=self.personal_progress)
        if self.participation_limit:
            self._objectives_context.update_value(key='personal_target_progress', value=self.participation_limit)

    @property
    def solar_system_id(self):
        return self._corporation_goal.get_closest_solar_system_id()

    @property
    def location_ids(self):
        return self._corporation_goal.get_location_ids()
