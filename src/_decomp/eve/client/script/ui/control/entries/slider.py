#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\slider.py
import carbonui.control.slider
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.eveLabel import EveLabelSmall

class SliderEntry(Generic):
    __guid__ = 'listentry.Slider'
    __params__ = ['cfgname', 'retval']
    __update_on_reload__ = 1

    def Startup(self, *args):
        super(SliderEntry, self).Startup(*args)
        mainpar = Container(name='listentry_slider', align=uiconst.TOTOP, width=0, height=10, left=0, top=14, state=uiconst.UI_NORMAL, parent=self)
        slider = carbonui.control.slider.Slider(parent=mainpar, align=uiconst.TOPLEFT, top=20, state=uiconst.UI_NORMAL)
        lbl = EveLabelSmall(text='', parent=mainpar, width=200, left=5, top=-12)
        lbl.name = 'label'
        self.sr.lbl = lbl
        slider.GetSliderHint = lambda idname, dname, value: localization.formatters.FormatNumeric(int(value))
        self.sr.slider = slider

    def Load(self, args):
        super(SliderEntry, self).Load(args)
        data = self.sr.node
        slider = self.sr.slider
        lbl = self.sr.lbl
        if data.Get('hint', None) is not None:
            lbl.hint = data.hint
        if data.Get('endsetslidervalue', None) is not None:
            slider.EndSetSliderValue = data.endsetslidervalue
        slider.Startup(data.Get('sliderID', 'slider'), data.Get('minValue', 0), data.Get('maxValue', 10), data.Get('config', None), data.Get('displayName', None), data.Get('increments', None), data.Get('usePrefs', 0), data.Get('startVal', None))

    def GetHeight(self, *args):
        node, width = args
        node.height = node.Get('height', 0) or 32
        return node.height
