#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\saved_filter_combo.py
import copy
import functools
from carbonui import uiconst
from carbonui.control.comboEntries import ComboEntry
from carbonui.uicore import uicore
from eve.client.script.ui.util.utilWindows import NamePopup
from eveexceptions import UserError
import eveui
import proper
from raffles.client import texture
from raffles.client.localization import Text
from raffles.client.util import deserialize_filter_settings, serialize_filter_settings

def saved_filter_combo(parent, align, filter_controller, settings_key, **kwargs):
    saved_filter_cont = eveui.Container(parent=parent, align=align, height=32, **kwargs)
    controller = SaveFilterController(filter_controller=filter_controller, settings_key=settings_key)
    SaveFilterButton(parent=saved_filter_cont, align=eveui.Align.to_right, padLeft=4, controller=controller, hint=Text.save_filter_hint())
    SavedFilterCombo(parent=saved_filter_cont, align=eveui.Align.to_all, controller=controller)


class SaveFilterController(proper.Observable):
    saved_filter_count_max = 20

    def __init__(self, filter_controller, settings_key, **kwargs):
        self.filter_controller = filter_controller
        self.settings_key = settings_key
        super(SaveFilterController, self).__init__(**kwargs)
        self.filter_controller.on_change.connect(self._on_filter_changed)
        if self.selected_filter_name is not None:
            self.filter_controller.on_change.connect(self._reset_selected_filter)

    @proper.ty
    def selected_filter_name(self):
        pass

    @selected_filter_name.default
    def _selected_filter_name_default(self):
        for name, filter_settings in self.saved_filters.iteritems():
            if filter_settings == self.filter_controller.current_settings:
                return name

    @selected_filter_name.after_change
    def _selected_filter_name_after_change(self, name):
        if name is None:
            self.filter_controller.on_change.disconnect(self._reset_selected_filter)
        else:
            filter_settings = deserialize_filter_settings(self.saved_filters[name])
            self.filter_controller.on_change.disconnect(self._reset_selected_filter)
            self.filter_controller.edit_filter_many(*filter_settings.items())
            self.filter_controller.on_change.connect(self._reset_selected_filter)

    def _reset_selected_filter(self):
        self.selected_filter_name = None

    @proper.alias
    def selected_filter_settings(self):
        if self.selected_filter_name is not None:
            return self.saved_filters[self.selected_filter_name]

    @proper.alias
    def current_filter_settings(self):
        return copy.deepcopy(self.filter_controller.current_settings)

    @proper.ty
    def saved_filters(self):
        pass

    @saved_filters.default
    def _saved_filters_default(self):
        return load_saved_filters(self.settings_key)

    @saved_filters.after_change
    def _persist_saved_filters(self, filters):
        settings.char.ui.Set(self.settings_key, filters)

    @proper.alias
    def is_filter_default(self):
        return self.filter_controller.is_default

    def save_current_filter(self):
        if len(self.saved_filters) >= self.saved_filter_count_max:
            raise UserError('MaxSavedFilterCountReached', {'max_count': self.saved_filter_count_max})
        name = prompt_filter_name()
        if not name:
            return
        if name in self.saved_filters and not prompt_override_filter(name):
            return
        with self.deferred_dispatch():
            self._add_saved_filter(name, self.current_filter_settings)
            self.selected_filter_name = name

    def delete(self, name):
        if name not in self.saved_filters:
            raise ValueError(u'No such filter {}'.format(name))
        if not prompt_delete_filter(name):
            return
        with self.deferred_dispatch():
            self._remove_saved_filter(name)
            if self.selected_filter_name == name:
                self.selected_filter_name = None

    def _add_saved_filter(self, name, filter_settings):
        filters = dict(self.saved_filters)
        filters[name] = serialize_filter_settings(filter_settings)
        self.saved_filters = filters

    def _remove_saved_filter(self, name):
        filters = dict(self.saved_filters)
        del filters[name]
        self.saved_filters = filters

    def _on_filter_changed(self):
        self.dispatch('current_filter_settings')
        if self.is_filter_default != self.filter_controller.is_default:
            self.dispatch('is_filter_default')


class SaveFilterButton(eveui.Button):
    default_name = 'SaveFilterButton'

    def __init__(self, controller, **kwargs):
        self.controller = controller
        super(SaveFilterButton, self).__init__(texturePath=texture.add_icon, func=self.controller.save_current_filter, args=(), **kwargs)
        self.layout()
        self.controller.bind(is_filter_default=self._update_enabled, selected_filter_name=self._update_enabled)

    def layout(self):
        self._update_enabled()

    def Enable(self):
        super(SaveFilterButton, self).Enable()

    def Disable(self):
        super(SaveFilterButton, self).Disable()

    def _update_enabled(self, *args):
        if self.controller.is_filter_default:
            self.Disable()
        else:
            self.Enable()


class SavedFilterCombo(eveui.Combo):
    default_name = 'SavedFilterCombo'
    isTabStop = True

    def __init__(self, controller, **kwargs):
        self.controller = controller
        self._suppress_refresh_options = False
        nothing_selected_text = Text.no_filter_selected()
        super(SavedFilterCombo, self).__init__(callback=self._on_change_handler, select=self.controller.selected_filter_name, options=self._get_options(), nothingSelectedText=nothing_selected_text, **kwargs)
        self._update_enabled()
        self.controller.bind(selected_filter_name=self._on_selected_filter_changed, saved_filters=self._on_saved_filters_changed)

    def _update_enabled(self):
        if len(self.controller.saved_filters) == 0:
            self.Disable()
            self.hint = Text.no_saved_filters_hint()
        else:
            self.Enable()
            self.hint = None

    def _on_selected_filter_changed(self, controller, selected_filter_name):
        if not self._suppress_refresh_options:
            self._refresh_options()

    def _refresh_options(self):
        self.Cleanup()
        self.LoadOptions(self._get_options(), select=self.controller.selected_filter_name)

    def _on_saved_filters_changed(self, controller, saved_filters):
        self._refresh_options()
        self._update_enabled()

    def GetEntryClass(self):
        return Entry

    def GetScrollEntry(self, entryData):
        data = super(SavedFilterCombo, self).GetScrollEntry(entryData)
        data['delete_filter'] = functools.partial(self._delete_saved_filter, name=entryData.label)
        return data

    def _delete_saved_filter(self, name):
        self.controller.delete(name)
        if len(self.controller.saved_filters) > 0:
            self.Expand()

    def _on_change_handler(self, combo, label, value):
        self._suppress_refresh_options = True
        if label == self.nothingSelectedText:
            self.controller.selected_filter_name = None
        else:
            self.controller.selected_filter_name = label
        self._suppress_refresh_options = False

    def _get_options(self):
        options = [ (name, name) for name, filter_settings in self.controller.saved_filters.iteritems() ]
        return sorted(options)


class Entry(ComboEntry):

    def Load(self, node):
        super(Entry, self).Load(node)
        if node.delete_filter:
            self._delete_filter_button._on_click = node.delete_filter

    @eveui.lazy
    def _delete_filter_button(self):
        return eveui.ButtonIcon(parent=self, align=eveui.Align.center_right, left=4, size=12, texture_path=texture.delete_saved_filter_icon, hint=Text.delete_saved_filter())


def prompt_filter_name():
    return NamePopup(caption=Text.filter_name_prompt_caption(), label=Text.filter_name_prompt_hint(), maxLength=100)


def prompt_override_filter(name):
    return _prompt('SavedFilterOverridePrompt', name=name)


def prompt_delete_filter(name):
    return _prompt('SavedFilterDeletePrompt', name=name)


def _prompt(dialog_key, **kwargs):
    result = uicore.Message(dialog_key, params=kwargs, buttons=uiconst.YESNO)
    return result == uiconst.ID_YES


def load_saved_filters(settings_key):
    migrate_old_filters(settings_key)
    saved_filters = settings.char.ui.Get(settings_key)
    if saved_filters is None:
        saved_filters = get_default_saved_filters()
    return saved_filters['filters']


def get_default_saved_filters():
    return {'version': 1,
     'filters': {}}


def migrate_old_filters(settings_key):
    saved_filters = settings.char.ui.Get(settings_key)
    if saved_filters is None:
        return
    if 'version' not in saved_filters:
        saved_filters = migrate_to_v1(saved_filters)
    settings.char.ui.Set(settings_key, saved_filters)


def migrate_to_v1(saved_filters):
    return {'version': 1,
     'filters': saved_filters}
