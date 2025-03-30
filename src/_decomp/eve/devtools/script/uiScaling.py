#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiScaling.py
import trinity
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from carbonui.control.window import Window

class UIScaling(Window):
    __guid__ = 'form.UIScaling'
    default_windowID = 'UIScaling'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetCaption('UI Scaling')
        self.SetMinSize([200, 150])
        self.Layout()

    def Layout(self):
        floats = (0.5, 2.0, 2)
        eveLabel.Label(text='use values from 0.5 to 2.0', parent=self.content, align=uiconst.TOTOP)
        apply_cont = Container(parent=self.content, align=uiconst.TOTOP, height=Button.default_height, padBottom=4)
        self.scaleEdit = SingleLineEditText(parent=apply_cont, name='scaleEdit', align=uiconst.TOLEFT, floats=floats, setvalue=uicore.desktop.dpiScaling, padRight=4)
        Button(parent=apply_cont, name='apply', align=uiconst.TOLEFT, label='Apply', func=self.ScaleUI)
        Button(parent=ContainerAutoSize(parent=self.content, align=uiconst.TOTOP), name='reset', align=uiconst.TOPLEFT, label='Reset', func=self.ResetUI)

    def LayoutOld(self):
        mainCont = Container(name='params', parent=self.sr.main, align=uiconst.TOALL, padding=const.defaultPadding)
        floats = (0.5, 2.0, 2)
        eveLabel.Label(text='use values from 0.5 to 2.0', parent=mainCont, align=uiconst.TOPLEFT)
        self.scaleEdit = SingleLineEditText(parent=mainCont, name='scaleEdit', align=uiconst.TOPLEFT, floats=floats, setvalue=uicore.desktop.dpiScaling, width=50, top=18)
        applyBtn = Button(parent=mainCont, name='apply', align=uiconst.TOPLEFT, label='Apply', left=54, top=18, func=self.ScaleUI)
        resetBtn = Button(parent=mainCont, name='reset', align=uiconst.TOPLEFT, label='Reset', left=0, top=40, func=self.ResetUI)

    def GetChange(self):
        scaleValue = self.scaleEdit.GetValue()
        oldHeight = int(trinity.device.height / uicore.desktop.dpiScaling)
        oldWidth = int(trinity.device.width / uicore.desktop.dpiScaling)
        newHeight = int(trinity.device.height / scaleValue)
        newWidth = int(trinity.device.width / scaleValue)
        changeDict = {}
        changeDict['ScalingWidth'] = (oldWidth, newWidth)
        changeDict['ScalingHeight'] = (oldHeight, newHeight)
        return (changeDict, True)

    def ResetUI(self, *args):
        self.scaleEdit.SetValue(1.0)
        change, canResize = self.GetChange()
        uicore.desktop.dpiScaling = 1.0
        sm.ScatterEvent('OnScalingChange', change)

    def ScaleUI(self, *args):
        scaleValue = self.scaleEdit.GetValue()
        change, canResize = self.GetChange()
        if not canResize:
            return
        uicore.desktop.dpiScaling = scaleValue
        sm.ScatterEvent('OnScalingChange', change)
