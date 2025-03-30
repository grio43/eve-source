#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\character_sheet\home\details.py
import datetimeutils
import eveformat
import localization
import signals
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from eve.client.script.ui.control import eveLabel, infoIcon
from carbonui.control.button import Button
from expertSystems import get_expert_system, MAX_INSTALLED_DURATION_TO_ALLOW_TOP_UP
from expertSystems.client import texture
from expertSystems.client.const import Color
from expertSystems.client.ui.character_sheet.home.controller import ExtendValidationError, TrainSkillsValidationError

class DetailsController(object):
    __notifyevents__ = ['OnSkillsChanged',
     'OnSkillQueueChanged',
     'OnClientEvent_SkillAddedToQueue',
     'OnClientEvent_SkillsRemovedFromQueue']

    def __init__(self, page_controller):
        self._page_controller = page_controller
        self._train_skills_validation_errors = None
        self.on_train_skills_validation_changed = signals.Signal()
        self._page_controller.on_selected_expert_system_changed.connect(self._handle_selected_expert_system_changed)
        ServiceManager.Instance().RegisterNotify(self)

    @property
    def on_selected_expert_system_changed(self):
        return self._page_controller.on_selected_expert_system_changed

    @property
    def selected_expert_system_id(self):
        return self._page_controller.selected_expert_system_id

    @property
    def selected_expert_system(self):
        return self._page_controller.selected_expert_system

    def validate_extend(self):
        return self.selected_expert_system.validate_extend()

    def validate_train_skills(self):
        if self.selected_expert_system is None:
            raise RuntimeError('No Expert System selected')
        if self._train_skills_validation_errors is None:
            self._train_skills_validation_errors = self.selected_expert_system.validate_train_skills()
        return self._train_skills_validation_errors

    def extend_selected_duration(self):
        self._page_controller.extend_selected_duration()

    def remove_selected(self):
        self._page_controller.remove_selected()

    def train_selected_skills(self):
        self._page_controller.train_selected_skills()

    def _handle_selected_expert_system_changed(self):
        self._train_skills_validation_errors = None

    def _update_train_skills_validation(self):
        if self._train_skills_validation_errors is None:
            return
        previous_errors = self._train_skills_validation_errors
        self._train_skills_validation_errors = None
        new_errors = self.validate_train_skills()
        if set(previous_errors) != set(new_errors):
            self.on_train_skills_validation_changed()

    def OnSkillsChanged(self, skill_info):
        self._update_train_skills_validation()

    def OnSkillQueueChanged(self):
        self._update_train_skills_validation()

    def OnClientEvent_SkillAddedToQueue(self, type_id, level):
        self._update_train_skills_validation()

    def OnClientEvent_SkillsRemovedFromQueue(self, skillRequirements):
        self._update_train_skills_validation()


class DetailsSection(ContainerAutoSize):

    def __init__(self, page_controller, **kwargs):
        self.controller = DetailsController(page_controller)
        self.title_label = None
        self.info_icon = None
        self.extend_button = None
        self.remove_button = None
        self.train_button = None
        super(DetailsSection, self).__init__(**kwargs)
        self.layout()
        self.update()
        self.controller.on_selected_expert_system_changed.connect(self.update)
        self.controller.on_train_skills_validation_changed.connect(self._update_train_skills_button)

    def layout(self):
        title_container = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        self.title_label = eveLabel.EveCaptionSmall(parent=title_container, align=uiconst.TOTOP, padRight=20)
        self.info_icon = infoIcon.InfoIcon(parent=title_container, align=uiconst.CENTERLEFT)

        def reposition_info_icon():
            self.info_icon.left = self.title_label.textwidth + 8

        self.title_label.OnSizeChanged = reposition_info_icon
        button_container = FlowContainer(parent=self, align=uiconst.TOTOP, top=8, contentSpacing=(4, 4))
        self.extend_button = IconButton(parent=button_container, align=uiconst.NOALIGN, texture_path=texture.action_extend_duration, func=self._extend_duration, args=())
        self.remove_button = IconButton(parent=button_container, align=uiconst.NOALIGN, texture_path=texture.action_remove, hint=self._get_remove_hint(), func=self._remove, args=())
        self.train_button = Button(parent=button_container, align=uiconst.NOALIGN, fixedheight=32, sidePadding=32, label=localization.GetByLabel('UI/ExpertSystem/TrainSkills'), func=self._train_skills, args=())

    def update(self):
        expert_system = None
        if self.controller.selected_expert_system_id is not None:
            expert_system = get_expert_system(self.controller.selected_expert_system_id)
        self.title_label.color = Color.text_normal if expert_system else Color.text_secondary
        self.title_label.SetText(expert_system.name if expert_system is not None else None)
        self.info_icon.SetTypeID(expert_system.type_id if expert_system is not None else None)
        if self._can_extend_duration():
            self.extend_button.Enable()
        else:
            self.extend_button.Disable()
        self.extend_button.SetHint(self._get_extend_hint())
        self._update_train_skills_button()

    def _update_train_skills_button(self):
        if self._have_skills_to_train():
            self.train_button.Enable()
        else:
            self.train_button.Disable()
        self.train_button.SetHint(self._get_train_skills_hint())

    def _handle_selected_expert_system_changed(self):
        self.update()

    def _can_extend_duration(self):
        expert_system = self.controller.selected_expert_system
        return expert_system is not None and expert_system.can_extend

    def _have_skills_to_train(self):
        expert_system = self.controller.selected_expert_system
        return expert_system is not None and expert_system.can_train_skills

    def _extend_duration(self):
        self.controller.extend_selected_duration()

    def _remove(self):
        self.controller.remove_selected()

    def _train_skills(self):
        self.controller.train_selected_skills()

    def _get_extend_hint(self):
        text = u'{}<br>{}'.format(eveformat.bold(localization.GetByLabel('UI/ExpertSystem/ExtendDuration')), localization.GetByLabel('UI/ExpertSystem/ExtendDurationHint', days=datetimeutils.filetime_delta_to_timedelta(MAX_INSTALLED_DURATION_TO_ALLOW_TOP_UP).days))
        disabled_reason = self._get_extend_disabled_reason()
        if disabled_reason:
            text = u'{}<br><br>{}'.format(text, eveformat.color(disabled_reason, color=Color.error))
        return text

    def _get_extend_disabled_reason(self):
        if self.controller.selected_expert_system is None:
            return
        errors = self.controller.validate_extend()
        not_available_errors = (ExtendValidationError.hidden, ExtendValidationError.hidden)
        if any((error in errors for error in not_available_errors)):
            return localization.GetByLabel('UI/ExpertSystem/ExtendDisabledReasonNotAvailable')
        if ExtendValidationError.duration_limit_reached in errors:
            return localization.GetByLabel('UI/ExpertSystem/ExtendDisabledReasonDurationLimit', days=datetimeutils.filetime_delta_to_timedelta(MAX_INSTALLED_DURATION_TO_ALLOW_TOP_UP).days)

    def _get_remove_hint(self):
        return u'{}<br>{}<br><br>{}'.format(eveformat.bold(localization.GetByLabel('UI/ExpertSystem/Remove')), localization.GetByLabel('UI/ExpertSystem/RemoveHint'), eveformat.color(localization.GetByLabel('UI/ExpertSystem/RemoveWarning'), color=Color.warning))

    def _get_train_skills_hint(self):
        text = localization.GetByLabel('UI/ExpertSystem/TrainSkillsHint')
        disabled_reason = self._get_train_skills_disabled_reason()
        if disabled_reason:
            text = u'{}<br><br>{}'.format(text, eveformat.color(disabled_reason, color=Color.error))
        return text

    def _get_train_skills_disabled_reason(self):
        if self.controller.selected_expert_system is None:
            return
        errors = self.controller.validate_train_skills()
        if TrainSkillsValidationError.no_skills_to_train in errors:
            return localization.GetByLabel('UI/ExpertSystem/TrainSkillsDisabledReasonNoSkills')


class IconButton(Button):

    def __init__(self, texture_path, **kwargs):
        super(IconButton, self).__init__(texturePath=texture_path, iconSize=24, iconPadding=8, **kwargs)
