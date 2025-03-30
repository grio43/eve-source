#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\RadioButton.py
from carbonui import uiconst
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.services.setting import UserSettingEnum
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

def OnSettingChanged(value):
    ShowQuickMessage('New Value: {value}'.format(value=value))


class Sample1(Sample):
    name = 'Basic'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, align=uiconst.TOPLEFT, columns=1, cellSpacing=24)
        self.sample_code(grid)

    def sample_code(self, parent):
        from carbonui.control.radioButton import RadioButton
        OPTION_COKE = 'coca_cola'
        OPTION_PEPSI = 'pepsi'
        OPTION_MOUNTAIN_DEW = 'mountain_dew'
        my_radio_setting = UserSettingEnum('my_radio_setting', OPTION_COKE, options=(OPTION_COKE, OPTION_PEPSI, OPTION_MOUNTAIN_DEW))
        my_radio_setting.on_change.connect(OnSettingChanged)
        RadioButton(parent=parent, align=uiconst.TOPLEFT, text='Coca Cola', setting=my_radio_setting, retval=OPTION_COKE)
        RadioButton(parent=parent, align=uiconst.TOPLEFT, text='Pepsi', setting=my_radio_setting, retval=OPTION_PEPSI)
        RadioButton(parent=parent, align=uiconst.TOPLEFT, enabled=False, text='Mountain Dew', setting=my_radio_setting, retval=OPTION_MOUNTAIN_DEW, hint="Yes, it's disabled ...")
