#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\gamma.py
from carbonui.control.button import Button
from carbonui import ButtonVariant
from carbonui.primitives.container import Container
from carbonui.button.group import ButtonGroup
from carbonui.control.window import Window
from carbonui.control.slider import Slider
import evegraphics.settings as gfxsettings
import carbonui.const as uiconst
import localization
import trinity
from carbonui.uicore import uicore

class GammaSliderWindow(Window):
    default_isCollapseable = False
    default_isKillable = False
    default_isMinimizable = False
    default_fixedWidth = 400
    default_fixedHeight = 160
    default_windowID = 'GammaSliderWindow'
    default_isLockable = False
    default_isOverlayable = False
    default_isLightBackgroundConfigurable = False
    default_caption = localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Brightness')

    def ConvertValue(self, value):
        return 2.0 - value

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        uicore.layer.systemmenu.suppress(show_ui=False)
        mainCont = Container(name='mainCont', parent=self.sr.main, align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=320, height=70)
        self.savedValue = gfxsettings.Get(gfxsettings.GFX_BRIGHTNESS)
        self.currentValue = self.savedValue
        self.gammaSlider = Slider(name='gammaSlider', parent=mainCont, minValue=0.5, maxValue=1.5, value=self.ConvertValue(self.savedValue), on_dragging=self.OnMySliderMoved, callback=self.OnMySliderMoved)
        ButtonGroup(name='buttonGroup', parent=mainCont, align=uiconst.CENTERBOTTOM, buttons=[Button(label=localization.GetByLabel('UI/Common/Buttons/Save'), func=self.Save, variant=ButtonVariant.PRIMARY), Button(label=localization.GetByLabel('UI/SystemMenu/ResetSettings/Reset'), func=self.Reset), Button(label=localization.GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel)])

    def OnMySliderMoved(self, slider):
        self.currentValue = self.ConvertValue(slider.GetValue())
        trinity.settings.SetValue('eveSpaceSceneGammaBrightness', self.currentValue)

    def Reset(self, *_):
        self.gammaSlider.SetValue(1.0)
        self.OnMySliderMoved(self.gammaSlider)

    def Close(self, *args, **kwds):
        try:
            uicore.layer.systemmenu.unsuppress()
        finally:
            Window.Close(self, *args, **kwds)

    def Save(self, *_):
        self.savedValue = self.currentValue
        gfxsettings.Set(gfxsettings.GFX_BRIGHTNESS, self.savedValue, pending=False)
        self.Close()

    def Cancel(self, *_):
        trinity.settings.SetValue('eveSpaceSceneGammaBrightness', self.savedValue)
        self.Close()


def GammaSlider():
    GammaSliderWindow.CloseIfOpen()
    wnd = GammaSliderWindow.Open()
    wnd.SetParent(uicore.layer.modal)
    return wnd
