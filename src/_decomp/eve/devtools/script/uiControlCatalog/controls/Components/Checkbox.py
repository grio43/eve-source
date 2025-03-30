#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\Checkbox.py
from carbonui import uiconst
from carbonui.services.setting import CharSettingBool
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

def OnSettingChanged(value):
    ShowQuickMessage('my_binary_setting is now set to {value}'.format(value=value))


class Sample1(Sample):
    name = 'With setting'
    description = 'Passing a setting into a checkbox will take care of persisting checkbox state and is generally preferred as most checkboxes correspond to a setting'

    def sample_code(self, parent):
        from carbonui.control.checkbox import Checkbox
        my_binary_setting = CharSettingBool('my_binary_setting', True)
        my_binary_setting.on_change.connect(OnSettingChanged)
        Checkbox(parent=parent, align=uiconst.TOPLEFT, text='Simple checkbox using settings', setting=my_binary_setting)


class Sample2(Sample):
    name = 'Without setting'

    def sample_code(self, parent):
        from carbonui.control.checkbox import Checkbox

        def OnChecked(checkbox):
            parts = ['Checkbox checked', 'settingsKey = %s' % checkbox.GetSettingsKey(), 'current value = %s' % checkbox.GetValue()]
            ShowQuickMessage('\n'.join(parts))

        Checkbox(parent=parent, align=uiconst.TOPLEFT, text='Simple checkbox', checked=True, callback=OnChecked, hint="I'm a very basic checkbox")


class Sample3(Sample):
    name = 'Disabled'

    def sample_code(self, parent):
        from carbonui.control.checkbox import Checkbox

        def OnChecked(checkbox):
            parts = ['Checkbox checked', 'settingsKey = %s' % checkbox.GetSettingsKey(), 'current value = %s' % checkbox.GetValue()]
            ShowQuickMessage('\n'.join(parts))

        Checkbox(parent=parent, align=uiconst.TOPLEFT, enabled=False, text='Disabled checkbox', checked=False, callback=OnChecked, hint="I'm a disabled checkbox")
