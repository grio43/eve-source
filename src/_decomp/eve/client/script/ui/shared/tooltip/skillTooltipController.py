#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\tooltip\skillTooltipController.py
import characterskills.client
import clonegrade
import evetypes
import localization
from carbonui.uicore import uicore
from eve.client.script.ui.control import primaryButton
from eve.client.script.ui.shared.cloneGrade import ORIGIN_SKILLREQUIREMENTSTOOLTIP
from eve.client.script.ui.shared.info import infoConst
from eve.client.script.ui.shared.neocom import skillConst
from inventorycommon import typeHelpers

def service_dependency(name, injected = None):
    if injected is not None:
        return injected
    return sm.GetService(name)


class SkillTooltipController(object):

    def __init__(self, type_id, clone_grade_service = None, info_service = None, market_utils_service = None, queue_service = None, skill_service = None):
        self.type_id = type_id
        self._clone_grade_service = service_dependency('cloneGradeSvc', clone_grade_service)
        self._info_service = service_dependency('info', info_service)
        self._market_utils_service = service_dependency('marketutils', market_utils_service)
        self._queue_service = service_dependency('skillqueue', queue_service)
        self._skill_service = service_dependency('skills', skill_service)

    @property
    def description(self):
        return evetypes.GetDescription(self.type_id)

    @property
    def estimated_market_price(self):
        return typeHelpers.GetAveragePrice(self.type_id)

    @property
    def has_rare_missing_requirements(self):
        return any((not skill.is_available_for_purchase for skill in self.missing_requirements))

    @property
    def is_available_for_purchase(self):
        return characterskills.client.is_available_for_purchase(self.type_id)

    @property
    def is_grandfathered(self):
        return self.points > 0 and self.untrained_requirements

    @property
    def is_injected(self):
        return self._skill_service.IsSkillInjected(self.type_id)

    @property
    def is_next_level_omega_restricted(self):
        if self._clone_grade_service.IsOmega():
            return False
        if self.points == 0 and self.is_omega_restricted_by_requirements:
            return True
        if self.level_including_queued == 5:
            return False
        next_level = self.level_including_queued + 1
        return self._clone_grade_service.IsSkillLevelRestricted(self.type_id, next_level)

    @property
    def is_rare(self):
        return not self.is_available_for_purchase

    @property
    def is_omega_restricted(self):
        return self.level_max == 0 or self.level_max < self.level or self.is_next_level_omega_restricted

    @property
    def is_omega_restricted_by_requirements(self):
        if self._clone_grade_service.IsOmega():
            return False
        return self._clone_grade_service.IsRequirementsRestricted(self.type_id)

    @property
    def is_trainable(self):
        if not self.is_injected:
            return False
        if self.level == 5:
            return False
        if self.is_next_level_omega_restricted:
            return False
        if self.is_grandfathered:
            return True
        if self.missing_requirements:
            return False
        return True

    @property
    def is_queued(self):
        return self._queue_service.IsSkillInQueue(self.type_id)

    def could_be_trained(self, skillLevel):
        if self.level == 5:
            return False
        if self.level >= skillLevel:
            return False
        if self.is_next_level_omega_restricted:
            return False
        return True

    @property
    def level(self):
        skill = self._get_skill_including_lapsed()
        if skill:
            return skill.trainedSkillLevel or 0
        return 0

    @property
    def effective_level(self):
        skill = self._get_skill_including_lapsed()
        if skill:
            return skill.effectiveSkillLevel or 0
        return 0

    @property
    def trained_level(self):
        skill = self._get_skill_including_lapsed()
        if skill:
            return skill.trainedSkillLevel or 0
        return 0

    @property
    def virtual_level(self):
        skill = self._get_skill_including_lapsed()
        if skill:
            return skill.virtualSkillLevel or 0
        return 0

    @property
    def level_including_queued(self):
        return self._skill_service.MySkillLevelIncludingQueued(self.type_id)

    @property
    def level_max(self):
        return self._clone_grade_service.GetMaxSkillLevel(self.type_id)

    @property
    def missing_requirements(self):
        return filter(lambda skill: not skill.is_injected, self.untrained_requirements)

    @property
    def points(self):
        skill = self._get_skill_including_lapsed()
        if skill:
            return skill.trainedSkillPoints or 0
        return 0

    @property
    def price(self):
        if not self.is_available_for_purchase:
            return None
        return characterskills.client.get_direct_purchase_price(self.type_id)

    @property
    def rank(self):
        return self._skill_service.GetSkillRank(self.type_id)

    @property
    def requirements_training_time(self):
        return self._skill_service.GetSkillTrainingTimeLeftToUseType(self.type_id, includeBoosters=False)

    @property
    def training_rate(self):
        return self._skill_service.GetSkillpointsPerMinute(self.type_id)

    @property
    def untrained_requirements(self):
        return [ RequiredSkillTooltipController(type_id, level) for type_id, level in self._get_untrained_required_skills() ]

    def buy(self):
        return self._skill_service.PurchaseSkills([self.type_id])

    def buy_with_requirements(self):
        type_ids = []
        if not self.is_grandfathered:
            type_ids.extend((skill.type_id for skill in self.missing_requirements))
        if not self.is_injected:
            type_ids.append(self.type_id)
        if not type_ids:
            return
        return self._skill_service.PurchaseSkills(type_ids)

    def get_time_until_trained(self, level = None):
        if not self.is_queued:
            return
        if level is None:
            level = self.level_including_queued
        training_time, _, _ = self._queue_service.GetTrainingLengthOfSkill(self.type_id, self.level_including_queued)
        return training_time

    def get_training_time_to_level(self, level):
        return long(sm.GetService('skills').GetTrainingTimeLeftForSkillLevels({self.type_id: level}, includeBoosters=True))

    def train(self, skillLevel = None):
        self._queue_service.AddSkillAndRequirementsToQueue(self.type_id)

    def train_to_level(self, skillLevel):
        self._queue_service.AddSkillAndRequirementsToQueue(self.type_id, skillLevel)

    def view_market_details(self):
        self._market_utils_service.ShowMarketDetails(self.type_id, None)

    def view_requirements(self):
        self._info_service.ShowInfo(typeID=self.type_id, selectTabType=infoConst.TAB_REQUIREMENTS)

    def _get_skill(self):
        return self._skill_service.GetSkill(self.type_id)

    def _get_skill_including_lapsed(self):
        return self._skill_service.GetSkillIncludingLapsed(self.type_id)

    def _get_untrained_required_skills(self):
        return self._skill_service.GetSkillsMissingToUseItemRecursiveList(self.type_id)


class RequiredSkillTooltipController(SkillTooltipController):

    def __init__(self, type_id, required_level):
        super(RequiredSkillTooltipController, self).__init__(type_id)
        self.required_level = required_level


class SkillPrimaryActionController(primaryButton.PrimaryButtonController):

    def __init__(self, skill, skillLevel = None):
        self.skill = skill
        self.skillLevel = skillLevel
        self.skill_service = service_dependency('skills')
        super(SkillPrimaryActionController, self).__init__()

    @property
    def default_is_enabled(self):
        if self.need_omega_upgrade:
            return True
        if self.skill.is_grandfathered:
            return True
        if not self.skill.is_injected and self.skill.is_rare:
            return False
        if self.skill.has_rare_missing_requirements:
            return False
        return True

    @property
    def default_label(self):
        if self.need_omega_upgrade:
            return localization.GetByLabel('UI/CloneState/Upgrade')
        if self.need_to_buy_skills:
            return localization.GetByLabel('UI/Skills/BuyAndTrain')
        if self.skill.is_trainable:
            skillLevel = self.skillLevel or self.skill.level_including_queued + 1
            return localization.GetByLabel('UI/Skills/TrainLevel', level=skillLevel)

    @property
    def default_style(self):
        if not self.default_is_enabled:
            color = (1.0, 1.0, 1.0, 0.5)
        elif self.need_omega_upgrade:
            color = clonegrade.COLOR_OMEGA_BG
        else:
            color = skillConst.COLOR_SKILL_2
        return primaryButton.FixedColorStyle(base_color=color)

    @property
    def error_message(self):
        are_requirements_available = all((skill.is_available_for_purchase for skill in self.skill.missing_requirements))
        need_rare_requirements = self.skill.missing_requirements and not are_requirements_available
        is_skill_available = self.skill.is_available_for_purchase
        need_rare_skill = not self.skill.is_injected and not is_skill_available
        if need_rare_skill and need_rare_requirements:
            return localization.GetByLabel('UI/Skills/ErrorRareSkillAndRequirements')
        elif need_rare_skill:
            return localization.GetByLabel('UI/Skills/ErrorRareSkill')
        elif need_rare_requirements:
            return localization.GetByLabel('UI/Skills/ErrorRareRequirements')
        else:
            return None

    @property
    def need_to_buy_skills(self):
        return not self.skill.is_injected or not self.skill.is_grandfathered and self.skill.missing_requirements

    @property
    def need_omega_upgrade(self):
        return self.skill.is_omega_restricted

    def buy_and_train(self, skillLevel = None):
        with self.arrow_animated():
            if self.need_to_buy_skills:
                missing_skills = []
                missing_skills.extend((skill.type_id for skill in self.skill.missing_requirements))
                missing_skills.append(self.skill.type_id)
                bought_skills = self.skill.buy_with_requirements()
                if not bought_skills:
                    return
                self.skill_service.WaitUntilSkillsAreAvailable(missing_skills)
            if skillLevel:
                self.skill.train_to_level(skillLevel)
            else:
                self.skill.train()

    def on_clicked(self):
        if self.need_omega_upgrade:
            self.upgrade()
        else:
            self.buy_and_train(self.skillLevel)

    def upgrade(self):
        uicore.cmd.OpenCloneUpgradeWindow(origin=ORIGIN_SKILLREQUIREMENTSTOOLTIP, reason=self.skill.type_id)
