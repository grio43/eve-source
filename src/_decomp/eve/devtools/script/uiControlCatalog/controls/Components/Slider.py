#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\Slider.py
from carbonui import uiconst
from carbonui.services.setting import UserSettingNumeric
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

def OnSettingChanged(value):
    ShowQuickMessage('New Value: {value}'.format(value=value))


class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from carbonui.control.slider import Slider
        my_setting = UserSettingNumeric('my_slider_setting', default_value=5.0, min_value=0.0, max_value=10.0)
        my_setting.on_change.connect(OnSettingChanged)
        Slider(parent=parent, align=uiconst.TOPLEFT, setting=my_setting, width=120)


class Sample2(Sample):
    name = 'Increments'

    def sample_code(self, parent):
        from carbonui.control.slider import Slider
        my_other_setting = UserSettingNumeric('my_other_slider_setting', default_value=5, min_value=0, max_value=8)
        my_other_setting.on_change.connect(OnSettingChanged)
        Slider(parent=parent, align=uiconst.TOPLEFT, setting=my_other_setting, width=120, increments=range(my_other_setting.max_value + 1))


def on_slider_callback(slider):
    ShowQuickMessage("Slider released, clicked or mouse-wheel'd, currently at %s" % round(slider.GetValue(), 2))


def on_slider_dragging(slider):
    ShowQuickMessage('Slider being dragged around, currently at %s' % round(slider.GetValue(), 2))


class Sample3(Sample):
    name = 'Callbacks'

    def sample_code(self, parent):
        from carbonui.control.slider import Slider
        Slider(parent=parent, align=uiconst.TOTOP, width=120, minValue=0.0, maxValue=256.0, value=100.0, callback=on_slider_callback, on_dragging=on_slider_dragging)


class Sample4(Sample):
    name = 'With tooltip'

    def sample_code(self, parent):
        from carbonui.control.slider import Slider

        def GetSliderHint(slider):
            return 'The value is %s' % round(slider.GetValue(), 1)

        Slider(name='mySlider', parent=parent, minValue=0, maxValue=10, getHintFunc=GetSliderHint)


class Sample5(Sample):
    name = 'With Labels'

    def sample_code(self, parent):
        from carbonui.control.slider import Slider
        Slider(name='mySlider', parent=parent, minValue=0, maxValue=10, minLabel="L'l", maxLabel='Lotz')
