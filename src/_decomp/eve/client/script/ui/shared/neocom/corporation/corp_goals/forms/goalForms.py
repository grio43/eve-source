#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_goals\forms\goalForms.py
import eveicon
from carbon.common.script.sys.serviceConst import ROLE_QA
from carbonui import TextColor
from carbonui.control.comboEntryData import ComboEntryData
from carbonui.control.forms import formComponent, formValidators
from carbonui.control.forms.form import Form, FormActionSubmit, FormActionCancel
from carbonui.control.forms.formWindow import FormWindow
from characterdata import careerpathconst, careerpath
from corporation.client.goals import goalsSettings
from corporation.client.goals.errors import AtGoalCapacity, BadRequestToReserveAsset, WalletAccessForbidden, InsufficientFunds
from corporation.client.goals.featureFlag import are_corporation_goal_payments_enabled
from corporation.client.goals.goalConst import ALLOWED_CONTRIBUTION_METHOD_TYPES
from corporation.client.goals.goalConst import ContributionMethodTypes
from corporation.client.goals.goalFormsMessenger import GoalFormsMessenger
from corporation.client.goals.goalsController import CorpGoalsController
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.shared.careerPortal.careerConst import CAREERS_16_SIZES
from eve.client.script.ui.shared.neocom.corporation.corp_goals.forms.goalFormComponents import ParticipationLimitComponent, MaxRewardPerContributorComponent
from eve.client.script.ui.shared.neocom.corporation.corp_goals.forms.goalFormWindow import GoalFormWindow
from eve.client.script.ui.shared.neocom.wallet import walletUtil
from eve.common.lib import appConst
from goals.client import contributionMethods
from localization import GetByLabel
from localization import GetByMessageID

def _SetProgress(form, goal):
    data = form.get_form_data()
    try:
        CorpGoalsController.get_instance().set_current_progress(goal.get_id(), data['current_progress'])
    except:
        ShowQuickMessage(GetByLabel('UI/Corporations/Goals/FailedToConnect'))
        raise


def OpenSetGoalProgressFormWindow(goal):
    form = Form(name=GetByLabel('UI/Corporations/Goals/SetProjectProgress'), icon='res:/ui/Texture/WindowIcons/corporation.png', components=[formComponent.Label('goal_name', GetByLabel('UI/Corporations/Goals/SetProgressLabel', name=goal.get_name(), progress=goal.get_current_progress(), target=goal.get_desired_progress())), formComponent.Integer('current_progress', GetByLabel('UI/Corporations/Goals/ProgressValue'), value=goal.get_current_progress() + 1, min_value=goal.get_current_progress() + 1, max_value=goal.get_desired_progress())], actions=(FormActionSubmit(GetByLabel('UI/Common/Buttons/Apply'), lambda f: _SetProgress(f, goal)),))
    FormWindow.Open(form=form)


def _CreateGoal(form):
    if session.role & ROLE_QA:
        _CreateGoalGM(form)
    else:
        payment_per_contribution_component = None
        if are_corporation_goal_payments_enabled():
            payment_per_contribution_component = form.get_component('amount_paid_per_unit').get_value()
        contribution_method = form.get_component('contribution_method').get_value()
        coverage_limit = None
        coverage_ratio = None
        if contribution_method == ContributionMethodTypes.SHIP_INSURANCE:
            coverage_limit = form.get_component('coverage_limit').get_value()
            coverage_ratio = form.get_component('coverage_ratio').get_value() * 0.01
            participation_limit = form.get_component('coverage_limit_per_member').get_value()
        else:
            participation_limit = form.get_component('participation_limit').get_value()
        CorpGoalsController.get_instance().create_goal(name=form.get_component('name').get_value(), description=form.get_component('description').get_value(), desired_progress=form.get_component('desired_progress').get_value(), method_type=form.get_component('contribution_method').get_value(), contribution_fields=form.get_component('contribution_parameters').get_value(), career_path=form.get_component('career_path').get_value(), payment_per_contribution=payment_per_contribution_component, end_time=form.get_component('expiration_time').get_value() if form.get_component('has_expiry').get_value() else None, participation_limit=participation_limit, coverage_limit=coverage_limit, multiplier=coverage_ratio)


def _CreateGoalGM(form):
    multipler = goalsSettings.gm_create_multiple_goals_setting.get()
    for i in range(multipler or 1):
        name = form.get_component('name').get_value()
        if multipler:
            name = u'{}_{}'.format(name, i)
        payment_per_contribution_component = None
        if are_corporation_goal_payments_enabled():
            payment_per_contribution_component = form.get_component('amount_paid_per_unit').get_value()
        contribution_method = form.get_component('contribution_method').get_value()
        coverage_limit = None
        coverage_ratio = None
        if contribution_method == ContributionMethodTypes.SHIP_INSURANCE:
            coverage_limit = form.get_component('coverage_limit').get_value()
            coverage_ratio = form.get_component('coverage_ratio').get_value() * 0.01
            participation_limit = form.get_component('coverage_limit_per_member').get_value()
        else:
            participation_limit = form.get_component('participation_limit').get_value()
        CorpGoalsController.get_instance().create_goal(name=name, description=form.get_component('description').get_value(), desired_progress=form.get_component('desired_progress').get_value(), method_type=form.get_component('contribution_method').get_value(), contribution_fields=form.get_component('contribution_parameters').get_value(), career_path=form.get_component('career_path').get_value(), payment_per_contribution=payment_per_contribution_component, end_time=form.get_component('expiration_time').get_value() if form.get_component('has_expiry').get_value() else None, participation_limit=participation_limit, coverage_limit=coverage_limit, multiplier=coverage_ratio)


class CreateGoalSubmit(FormActionSubmit):

    def execute(self, form):
        if form.is_valid():
            try:
                self.func(form)
                form.on_submitted(self)
            except (AtGoalCapacity,
             BadRequestToReserveAsset,
             WalletAccessForbidden,
             InsufficientFunds):
                return
            except Exception:
                raise

        else:
            form.on_submit_failed(self)


class ContributionParametersForm(Form):

    def __init__(self, components = None, actions = None, name = None, label = None, description = None, icon = None, hint = None, field_cls = None, cancel_dialog = None, parameters = None):
        Form.__init__(self, components, actions, name, label, description, icon, hint, field_cls, cancel_dialog)
        self._reconstruct_components(parameters)

    def _reconstruct_components(self, parameters):
        if parameters is None:
            return
        components = []
        for parameter in parameters:
            c = parameter.get_form_component()
            c.indent_level = 1
            components.append(c)

        self.set_components(components)


def OpenDuplicateGoalFormWindow(original):
    GoalFormsMessenger(sm.GetService('publicGatewaySvc')).clone_form_opened(original.goal_id)
    OpenCreateGoalFormWindow(method_type=original.contribution_method.method_id, desired_progress=original.get_desired_progress(), career_path=original.career_path, name=original.get_name(), description=original.get_description(), parameters=original.contribution_method.parameters, payment_per_unit=original.get_isk_per_contribution(), participation_limit=original.get_participation_limit(), pre_set_duration=original.get_cloned_project_duration(), coverage_limit=original.get_coverage_limit(), multiplier=original.get_multiplier_percentage())


def OpenCreateGoalFormWindow(method_type = None, desired_progress = 1, career_path = None, name = None, description = None, parameters = None, payment_per_unit = 0, participation_limit = None, pre_set_duration = None, coverage_limit = None, multiplier = None):
    project_definition_sub_form = ProjectDefinitionSubForm(method_type, parameters, desired_progress, name='contribution_method_sub_form', label=GetByLabel('UI/Corporations/Goals/ProjectDefinition'), pre_set_duration=pre_set_duration, participation_limit=participation_limit, coverage_limit=coverage_limit, multiplier=multiplier)
    description_sub_form = _get_description_sub_form(career_path, description, name)
    form_components = [project_definition_sub_form, description_sub_form]
    if are_corporation_goal_payments_enabled():
        payment_sub_form = _get_payment_sub_form(payment_per_unit, participation_limit)
        form_components.append(payment_sub_form)
    form = Form(name=GetByLabel('UI/Corporations/Goals/NewProject'), icon='res:/ui/Texture/WindowIcons/corporation.png', components=form_components, actions=(CreateGoalSubmit(GetByLabel('UI/Corporations/Goals/CreateNew'), _CreateGoal), FormActionCancel()), cancel_dialog='CancelProjectCreation')
    for component in form.components:
        form.on_submit_failed.connect(component.on_submit_failed)

    form.get_component('contribution_method').on_value_set_by_user.connect(form.get_component('career_path').on_contribution_method_changed)
    if are_corporation_goal_payments_enabled():
        form.get_component('contribution_method').on_value_set_by_user.connect(form.get_component('amount_paid_per_unit').on_contribution_method_changed)
        reward_per_contributor_component = form.get_component('max_reward_per_contributor')
        form.get_component('amount_paid_per_unit').on_value_set_by_user.connect(reward_per_contributor_component.reward_changed)
        form.get_component('amount_paid_per_unit').on_value_set.connect(reward_per_contributor_component.set_reward)
        project_definition_sub_form.add_max_reward_listeners(reward_per_contributor_component)
    GoalFormWindow.Open(form=form)


def _get_description_sub_form(career_path, description, name):
    options = [ ComboEntryData(GetByMessageID(c.nameID), c_id, icon=CAREERS_16_SIZES.get(c_id), iconColor=TextColor.SECONDARY, hint=GetByMessageID(c.nameID) + '\n\n' + GetByMessageID(c.descriptionID)) for c_id, c in careerpath.get_career_paths().iteritems() ]
    options.insert(0, ComboEntryData(GetByLabel('Character/CareerPaths/Unclassified'), careerpathconst.career_path_none, icon=eveicon.unclassified, iconColor=TextColor.SECONDARY, hint=GetByLabel('Character/CareerPaths/Unclassified')))
    career_path_component = GoalCareerPathComponent('career_path', GetByLabel('Character/CareerPaths/CareerPath'), options, value=career_path)
    return Form(name='description_sub_form', label=GetByLabel('UI/Common/Description'), components=[formComponent.Text('name', GetByLabel('UI/Common/Name'), validators=[formValidators.Length(5, 60), formValidators.OnlySingleWhitespaces(), formValidators.IllegalCharacters()], value=name), formComponent.TextMultiLine('description', GetByLabel('UI/Common/Description'), num_lines=4, show_formatting_panel=True, validators=[formValidators.Length(maxLength=1000)], value=description), career_path_component])


class ProjectDefinitionComponentsSubForm(Form):

    def __init__(self, method_type, parameters, desired_progress, pre_set_duration = None, participation_limit = None, coverage_limit = None, multiplier = None, *args, **kwargs):
        super(ProjectDefinitionComponentsSubForm, self).__init__(*args, **kwargs)
        self.desired_progress_component = DesiredProgressComponent('desired_progress', self._get_target_value_description(method_type), min_value=1, max_value=2 * appConst.maxBigint, value=desired_progress, is_visible=bool(method_type), icon=eveicon.number, indent_level=1)
        self.coverage_limit = None
        self.coverage_ratio = None
        self.coverage_limit_per_member = None
        self.optional_expiry = None
        self.expiration_component = None
        self.max_reward_component = None
        self.participation_limit_component = None
        self._reconstruct_components(method_type, parameters, participation_limit, pre_set_duration, coverage_limit, multiplier)

    def _reconstruct_components(self, method_type, parameters, participation_limit = None, pre_set_duration = None, coverage_limit = None, multiplier = None):
        self.contribution_parameters = self._create_parameters_component(method_type, parameters)
        if method_type is None:
            components = [self.desired_progress_component]
        elif method_type == ContributionMethodTypes.SHIP_INSURANCE:
            self.contribution_parameters.get_component('ship').on_value_set_by_user.connect(self._on_srp_ship_value_changed)
            self.coverage_limit = formComponent.Integer(name='coverage_limit', label=GetByLabel('UI/Corporations/Goals/CoverageLimitPerLoss'), hint=GetByLabel('UI/Corporations/Goals/ShipInsuranceLimitPerContributionTooltip'), min_value=1, max_value=self.desired_progress_component.get_value(), value=coverage_limit, icon=eveicon.isk, placeholder=GetByLabel('UI/Corporations/Goals/TypeInIskOptional'), indent_level=1)
            self.coverage_ratio = formComponent.Integer(name='coverage_ratio', label=GetByLabel('UI/Corporations/Goals/CoverageRatioParamName', min_value=10, max_value=200), hint=GetByLabel('UI/Corporations/Goals/ShipInsuranceCoverageRatio'), value=int(multiplier) if multiplier else 100, min_value=10, max_value=200, icon=eveicon.ratio, indent_level=1)
            self.coverage_limit_per_member = formComponent.Integer(name='coverage_limit_per_member', label=GetByLabel('UI/Corporations/Goals/CoverageLimitPerMemberTitle'), hint=GetByLabel('UI/Corporations/Goals/ShipInsuranceLimitPerContributorTooltip'), min_value=1, max_value=self.desired_progress_component.get_value(), value=participation_limit if participation_limit else None, is_visible=method_type == ContributionMethodTypes.SHIP_INSURANCE, icon=eveicon.isk, placeholder=GetByLabel('UI/Corporations/Goals/TypeInIskOptional'), indent_level=1)
            components = [self.desired_progress_component,
             self.coverage_limit_per_member,
             self.coverage_limit,
             self.coverage_ratio,
             self.contribution_parameters]
        else:
            self.participation_limit_component = ParticipationLimitComponent(name='participation_limit', value=participation_limit if participation_limit else None, label=GetByLabel('UI/Corporations/Goals/LimitPerContributor'), hint=GetByLabel('UI/Corporations/Goals/LimitPerContributorHint'), min_value=1, max_value=self.desired_progress_component.get_value(), icon=eveicon.user, placeholder=GetByLabel('UI/Corporations/Goals/TypeInOptionalContributionAmount'), indent_level=1)
            components = [self.contribution_parameters, self.desired_progress_component, self.participation_limit_component]
        expiry_components = self._create_expiration_component(method_type, pre_set_duration)
        if expiry_components is not None:
            components.extend(expiry_components)
        self.set_components(components)
        self.desired_progress_component.on_value_set_by_user.connect(self.on_desired_progress_changed)
        if self.optional_expiry:
            self.optional_expiry.on_value_set_by_user.connect(self.on_optional_expiry_toggled)
        self._set_max_reward_listeners()

    def _on_srp_ship_value_changed(self, component):
        if component.get_value():
            self.get_component('cover_implants').set_hidden()
            self.get_component('cover_implants').set_value(False)
        else:
            self.get_component('cover_implants').set_visible()
            self.get_component('cover_implants').set_value(True)

    def _get_target_value_description(self, method_type):
        if not method_type:
            return GetByLabel('UI/Corporations/Goals/TargetValue')
        return contributionMethods.get_contribution_method(method_type).target_value_description

    def _create_parameters_component(self, method_type, parameters):
        if method_type is None:
            return
        return ContributionParametersForm(name='contribution_parameters', parameters=parameters)

    def _create_expiration_component(self, method_type, pre_set_duration):
        if method_type is None:
            return []
        self.optional_expiry = formComponent.Boolean(name='has_expiry', value=True if pre_set_duration else False, label=GetByLabel('UI/Corporations/Goals/SetEndDate'), hint=GetByLabel('UI/Corporations/Goals/ExpiredFieldInfo'), indent_level=1)
        expiration_visible = True if pre_set_duration else False
        self.expiration_component = ExpirationComponent(name='expiration_time', time_options=['7d',
         '2w',
         '1m',
         '3m',
         '6m'], year_range=2, indent_level=1, is_visible=expiration_visible, is_included=expiration_visible, duration_datetime=pre_set_duration)
        return [self.optional_expiry, self.expiration_component]

    def get_contribution_method(self, method_type):
        if method_type is None:
            return
        data = self.contribution_parameters.get_value()
        return contributionMethods.get_contribution_method(method_type, data)

    def on_desired_progress_changed(self, component):
        new_max = component.get_value()
        if new_max is None:
            return
        if self.participation_limit_component:
            self.participation_limit_component.max_values_changed(new_max)
        if self.coverage_limit is not None:
            self.coverage_limit.max_values_changed(new_max)
        if self.coverage_limit_per_member is not None:
            self.coverage_limit_per_member.max_values_changed(new_max)

    def on_optional_expiry_toggled(self, component):
        self.expiration_component.set_is_included(bool(component.get_value()))

    def on_contribution_method_changed(self, component):
        method_type = component.get_value()
        if not method_type:
            return
        parameters = contributionMethods.get_contribution_method(method_type).parameters
        self._reconstruct_components(method_type, parameters)
        self.desired_progress_component.on_contribution_method_changed(component)

    def add_max_reward_listeners(self, max_reward_component):
        self.max_reward_component = max_reward_component
        self._set_max_reward_listeners()

    def _set_max_reward_listeners(self):
        if self.max_reward_component is None:
            return
        if are_corporation_goal_payments_enabled():
            if self.participation_limit_component:
                self.participation_limit_component.on_value_set_by_user.connect(self.max_reward_component.limit_changed)
            if self.participation_limit_component:
                self.participation_limit_component.on_value_set_by_user.connect(self.max_reward_component.set_is_included)


class ProjectDefinitionSubForm(Form):

    def __init__(self, method_type, parameters, desired_progress, pre_set_duration = None, participation_limit = None, coverage_limit = None, multiplier = None, *args, **kwargs):
        super(ProjectDefinitionSubForm, self).__init__(*args, **kwargs)
        methods = [ contributionMethods.get_contribution_method(contribution_method_type) for contribution_method_type in ALLOWED_CONTRIBUTION_METHOD_TYPES ]
        methods = sorted(methods, key=lambda m: m.title)
        options = [ ComboEntryData(method.title, method.method_id, hint=method.info, icon=method.icon, iconColor=TextColor.SECONDARY) for method in methods ]
        self.contribution_method_component = ContributionMethodComponent('contribution_method', GetByLabel('UI/Corporations/Goals/ContributionMethod'), options=options, value=method_type, placeholder=GetByLabel('UI/Corporations/Goals/SelectContributionMethod'), validators=[formValidators.InputRequired()])
        self.contribution_component_sub_form = ProjectDefinitionComponentsSubForm(name='contribution_parameters_sub_form', method_type=method_type, parameters=parameters, desired_progress=desired_progress, pre_set_duration=pre_set_duration, participation_limit=participation_limit, coverage_limit=coverage_limit, multiplier=multiplier)
        self.set_components([self.contribution_method_component, self.contribution_component_sub_form])
        self.contribution_method_component.on_value_set_by_user.connect(self.on_contribution_method_changed)

    def on_contribution_method_changed(self, component):
        self.contribution_component_sub_form.on_contribution_method_changed(component)

    def get_contribution_method(self, include_data = False):
        method_type = self.contribution_method_component.get_value()
        if method_type is None:
            return
        return self.contribution_component_sub_form.get_contribution_method(method_type)

    def add_max_reward_listeners(self, max_reward_component):
        self.contribution_component_sub_form.add_max_reward_listeners(max_reward_component)


def _get_payment_sub_form(payment_per_unit = 0, participation_limit = None):
    wallet_division_text = walletUtil.GetDivisionName(session.corpAccountKey)
    amount_component = AmountPaidPerUnitComponent(name='amount_paid_per_unit', label=GetByLabel('UI/Corporations/Goals/ISKPerUnitOfProgress'), hint=GetByLabel('UI/Corporations/Goals/ISKPerUnitOfProgressHint', divisionName=wallet_division_text), icon=eveicon.isk, value=payment_per_unit)
    amount_per_contributor_component = MaxRewardPerContributorComponent(name='max_reward_per_contributor', reward=payment_per_unit, limit=participation_limit if participation_limit else 0, is_visible=True if participation_limit else False)
    return Form(name='payment_sub_form', label=GetByLabel('UI/Corporations/Goals/PaymentOptional'), components=[amount_component, amount_per_contributor_component])


class DesiredProgressComponent(formComponent.Integer):

    def on_contribution_method_changed(self, component):
        if component.get_value() == ContributionMethodTypes.SHIP_INSURANCE:
            self.set_icon(eveicon.isk)
            self.set_hint(GetByLabel('UI/Corporations/Goals/ShipInsuranceTargetValueDescription'))
        else:
            self.set_hint(None)
            self.set_icon(eveicon.number)
        label = component.get_target_value_description()
        if label:
            self.set_label(label)
        self.set_value(1)
        if component.is_valid():
            self.set_visible()
        else:
            self.set_hidden()


class ExpirationComponent(formComponent.DateTime):

    def __init__(self, is_included = False, *args, **kwargs):
        super(ExpirationComponent, self).__init__(*args, **kwargs)
        self.is_included = is_included

    def set_is_included(self, value):
        if value == self.is_included:
            return
        self.is_included = value
        if value:
            self.set_visible()
        else:
            self.set_hidden()


class GoalCareerPathComponent(formComponent.Enum):

    def on_contribution_method_changed(self, component):
        method_type = component.get_value()
        if method_type is None:
            return
        method = contributionMethods.get_contribution_method(method_type)
        self.set_value(method.career_path or careerpathconst.career_path_none)


class AmountPaidPerUnitComponent(formComponent.Float):

    def on_contribution_method_changed(self, component):
        method_type = component.get_value()
        if method_type is None:
            return
        if method_type == ContributionMethodTypes.SHIP_INSURANCE:
            self.set_value(1.0)
        else:
            self.set_value(0)
        method = contributionMethods.get_contribution_method(method_type)
        self.set_label(method.rewarding_description)


class ContributionMethodComponent(formComponent.Enum):

    def get_target_value_description(self):
        method = self.get_contribution_method()
        if method:
            return method.target_value_description

    def get_contribution_method(self):
        method_type = self.get_value()
        if method_type is None:
            return
        return contributionMethods.get_contribution_method(method_type)

    def get_full_description(self):
        method = self.get_contribution_method()
        if method:
            return method.full_description
