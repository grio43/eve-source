#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\ui.py
from .base import Event

class ClientSettingsChanged(Event):
    atom_id = 151
    __notifyevents__ = ['OnClientSettingsChanged']

    def __init__(self, settings_section = None, settings_group = None, settings_id = None, *args, **kwargs):
        super(ClientSettingsChanged, self).__init__(*args, **kwargs)
        self.settings_section = self.get_atom_parameter_value('settings_section', settings_section)
        self.settings_group = self.get_atom_parameter_value('settings_group', settings_group)
        self.settings_id = settings_id

    def _register(self):
        if self.settings_section and self.settings_group and self.settings_id:
            settings[self.settings_section].Subscribe(self.settings_group, self.settings_id, self._setting_changed)
        else:
            super(ClientSettingsChanged, self)._register()

    def _unregister(self):
        if self.settings_section and self.settings_group and self.settings_id:
            settings[self.settings_section].Unsubscribe(self.settings_group, self.settings_id, self._setting_changed)
        else:
            super(ClientSettingsChanged, self)._unregister()

    def OnClientSettingsChanged(self, settings_section, settings_group, settings_id):
        if self.settings_section and self.settings_section != settings_section:
            return
        if self.settings_group and self.settings_group != settings_group:
            return
        if self.settings_id and self.settings_id != settings_id:
            return
        self.invoke(settings_section=settings_section, settings_group=settings_group, settings_id=settings_id)

    def _setting_changed(self):
        self.invoke(settings_section=self.settings_section, settings_group=self.settings_group, settings_id=self.settings_id)

    @classmethod
    def get_subtitle(cls, settings_section = None, settings_group = None, settings_id = None, **kwargs):
        return u'{}.{}.{}'.format(cls.get_atom_parameter_value('settings_section', settings_section), cls.get_atom_parameter_value('settings_group', settings_group), settings_id or '')


class DialogMessageShown(Event):
    atom_id = 160
    __notifyevents__ = ['OnEveMessage']

    def OnEveMessage(self, message_key, message_values):
        self.invoke(message_key=message_key)


class MenuShown(Event):
    atom_id = 352
    __notifyevents__ = ['OnMenuShown']

    def OnMenuShown(self):
        self.invoke()


class MenuClosed(Event):
    atom_id = 493
    __notifyevents__ = ['OnMenuClosed']

    def OnMenuClosed(self):
        self.invoke()


class OverviewTabSelected(Event):
    atom_id = 358
    __notifyevents__ = ['OnOverviewPresetLoaded']

    def OnOverviewPresetLoaded(self, tab_id, *args, **kwargs):
        self.invoke(tab_id=tab_id)


class InventoryItemMouseEntered(Event):
    atom_id = 359
    __notifyevents__ = ['OnInventoryItemMouseEntered']

    def OnInventoryItemMouseEntered(self, type_id, item_id):
        self.invoke(type_id=type_id, item_id=item_id)


class InventoryItemMouseExited(Event):
    atom_id = 360
    __notifyevents__ = ['OnInventoryItemMouseExited']

    def OnInventoryItemMouseExited(self, type_id, item_id):
        self.invoke(type_id=type_id, item_id=item_id)


class UtilMenuOpened(Event):
    atom_id = 422
    __notifyevents__ = ['OnUtilMenuOpened']

    def OnUtilMenuOpened(self):
        self.invoke()


class CapacitorContainerTooltipShown(Event):
    atom_id = 497
    __notifyevents__ = ['OnCapacitorContainerTooltipShown']

    def OnCapacitorContainerTooltipShown(self, *args, **kwargs):
        self.invoke()


class CapacitorContainerTooltipClosed(Event):
    atom_id = 498
    __notifyevents__ = ['OnCapacitorContainerTooltipClosed']

    def OnCapacitorContainerTooltipClosed(self, *args, **kwargs):
        self.invoke()


class SelectedItemButtonClicked(Event):
    atom_id = 609
    __notifyevents__ = ['OnSelectedItemButtonClicked']

    def OnSelectedItemButtonClicked(self, ui_name):
        if not ui_name.startswith('selectedItem'):
            return
        command_name = ui_name[len('selectedItem'):]
        self.invoke(command_name=command_name)


class CharacterCreationStepChanged(Event):
    atom_id = 621
    __notifyevents__ = ['OnCharacterCreationStep']

    def OnCharacterCreationStep(self, fromStep, toStep):
        self.invoke(to_step=toStep)
