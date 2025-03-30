#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\theme\storage.py
import carbonui
import contextlib
from carbonui.services.setting import _BaseSetting, _UserSettingMixin
from eve.client.script.ui.shared.colorThemes import ColorTheme
from eve.client.script.ui.shared.systemMenu.theme.model import focus_dark_from_focus

class CustomColorThemeCollection(object):
    VERSION = 1

    def __init__(self, themes):
        self.themes_by_id = {theme.id:theme for theme in themes}

    @property
    def themes(self):
        return self.themes_by_id.values()

    def add_or_update(self, theme):
        self.themes_by_id[theme.id] = theme

    def remove(self, theme):
        del self.themes_by_id[theme.id]

    @classmethod
    def deserialize(cls, data):
        version = int(data['version'])
        return cls(themes=[ deserialize_theme(theme_data) for theme_data in data['themes'] ])

    def serialize(self):
        return {'version': self.VERSION,
         'themes': [ serialize_theme(theme) for theme in self.themes_by_id.values() ]}

    def __eq__(self, other):
        if not isinstance(other, CustomColorThemeCollection):
            return False
        keys = set(self.themes_by_id.keys())
        if keys != set(other.themes_by_id.keys()):
            return False
        for key in keys:
            if self.themes_by_id[key] != other.themes_by_id[key]:
                return False

        return True


def serialize_theme(theme):
    return {'id': theme.id,
     'name': theme.name,
     'focus': theme.focus.hex_argb,
     'accent': theme.accent.hex_argb,
     'alert': theme.alert.hex_argb,
     'tint': theme.tint.hex_argb}


def deserialize_theme(data):
    focus = carbonui.Color.from_hex(data['focus'])
    return ColorTheme(theme_id=data['id'], name=data['name'], focus=focus, focus_dark=focus_dark_from_focus(focus), accent=carbonui.Color.from_hex(data['accent']), alert=carbonui.Color.from_hex(data['alert']), tint=carbonui.Color.from_hex(data['tint']))


class CustomColorThemesSetting(_BaseSetting, _UserSettingMixin):

    def __init__(self):
        super(CustomColorThemesSetting, self).__init__(settings_key='custom_color_themes', default_value=lambda : CustomColorThemeCollection(themes=[]))

    def get(self):
        data = super(CustomColorThemesSetting, self).get()
        if isinstance(data, CustomColorThemeCollection):
            return data
        else:
            result = CustomColorThemeCollection.deserialize(data)
            return result

    @contextlib.contextmanager
    def modify(self):
        custom_themes_data = self.get()
        try:
            yield custom_themes_data
        except Exception:
            raise
        else:
            self.set(custom_themes_data)

    def is_equal(self, value):
        return False

    def _set(self, value):
        super(CustomColorThemesSetting, self)._set(value.serialize())

    def _validate(self, value):
        return isinstance(value, CustomColorThemeCollection)


custom_color_themes = CustomColorThemesSetting()
