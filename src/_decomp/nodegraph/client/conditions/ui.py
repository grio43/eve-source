#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\ui.py
from .base import Condition
from eve.client.script.ui.view.viewStateConst import ViewState

class ClientSettings(Condition):
    atom_id = 150

    def __init__(self, settings_section = None, settings_group = None, settings_id = None, settings_value = None, **kwargs):
        super(ClientSettings, self).__init__(**kwargs)
        self.settings_section = self.get_atom_parameter_value('settings_section', settings_section)
        self.settings_group = self.get_atom_parameter_value('settings_group', settings_group)
        self.settings_id = settings_id
        self.settings_value = settings_value

    def validate(self, **kwargs):
        if None in (self.settings_section,
         self.settings_group,
         self.settings_id,
         self.settings_value):
            return False
        try:
            if self.settings_group not in settings[self.settings_section].datastore:
                return False
            return str(settings[self.settings_section].Get(self.settings_group, self.settings_id)) == self.settings_value
        except:
            return False

    @classmethod
    def get_subtitle(cls, settings_section = None, settings_group = None, settings_id = None, settings_value = None, **kwargs):
        return u'{}.{}.{}={}'.format(cls.get_atom_parameter_value('settings_section', settings_section), cls.get_atom_parameter_value('settings_group', settings_group), settings_id or 'MISSING', settings_value or 'MISSING')


class UiElementVisible(Condition):
    atom_id = 152

    def __init__(self, ui_element = None, **kwargs):
        super(UiElementVisible, self).__init__(**kwargs)
        self.ui_element = ui_element

    def validate(self, **kwargs):
        element_key_val = sm.GetService('uipointerSvc').FindElementToPointTo(self.ui_element, shouldExcludeInvisible=True)
        ui_element = element_key_val.pointToElement if element_key_val else None
        return ui_element and ui_element.IsVisible() and ui_element.opacity > 0

    @classmethod
    def get_subtitle(cls, ui_element = '', **kwargs):
        return ui_element


class MenuVisible(Condition):
    atom_id = 353

    def __init__(self, type_id = None, **kwargs):
        super(MenuVisible, self).__init__(**kwargs)
        self.type_id = type_id

    def _is_menu_open(self):
        from carbonui.control.contextMenu.menuUtil import HasContextMenu
        return HasContextMenu()

    def validate(self, **kwargs):
        return self._is_menu_open() and self._is_menu_for_type_id()

    def _is_menu_for_type_id(self):
        if not self.type_id:
            return True
        from carbonui.control.contextMenu.menuUtil import GetContextMenuOwner
        menu_owner = GetContextMenuOwner()
        type_id = getattr(menu_owner, 'typeID', None)
        return type_id == self.type_id


class OverviewTabSelected(Condition):
    atom_id = 357

    def __init__(self, tab_id = None, **kwargs):
        super(OverviewTabSelected, self).__init__(**kwargs)
        self.tab_id = tab_id

    def validate(self, **kwargs):
        tab_id = sm.GetService('overviewPresetSvc').GetActiveOverviewPresetName()
        return self.tab_id == tab_id

    @classmethod
    def get_subtitle(cls, tab_id = '', **kwargs):
        return tab_id or 'MISSING TAB ID'


class InCharacterCreationStep(Condition):
    atom_id = 622

    def __init__(self, step_to_validate = None, **kwargs):
        super(InCharacterCreationStep, self).__init__(**kwargs)
        self.step_to_validate = step_to_validate

    def validate(self, **kwargs):
        from carbonui.uicore import uicore
        if sm.GetService('viewState').IsViewActive(ViewState.CharacterCreation):
            current_step = uicore.layer.charactercreation.controller.stepID
            return self.step_to_validate == current_step
        return False

    @classmethod
    def get_subtitle(cls, step_to_validate = '', **kwargs):
        if step_to_validate:
            return 'Step {}'.format(step_to_validate)
