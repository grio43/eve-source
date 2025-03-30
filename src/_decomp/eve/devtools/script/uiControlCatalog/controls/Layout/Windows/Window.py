#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\Windows\Window.py
from carbonui import IdealSize
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import Label
import carbonui.const as uiconst
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = "Windows are practically our 'App' class. They commonly correspond to feature, and will be represented in the Neocom."

    def sample_code(self, parent):
        from carbonui.control.window import Window

        class MyWindow(Window):
            default_caption = 'My Window Caption'
            default_windowID = 'myWindowUniqueID'
            default_width = IdealSize.SIZE_480
            default_height = IdealSize.SIZE_480
            default_minSize = (IdealSize.SIZE_240, IdealSize.SIZE_240)
            default_someValue = 10
            default_otherValue = 20

            def ApplyAttributes(self, attributes):
                Window.ApplyAttributes(self, attributes)
                someValue = attributes.Get('someValue', self.default_someValue)
                otherValue = attributes.Get('otherValue', self.default_otherValue)
                Label(name='someValueLabel', parent=self.content, align=uiconst.CENTER, text='Some value is %s' % someValue)
                Label(name='otherValueLabel', parent=self.content, align=uiconst.CENTER, top=16, text='Other value is %s' % otherValue)

        def OnWindowButton(btn):
            MyWindow.ToggleOpenClose(someValue=5)

        Button(name='windowButton', parent=parent, label='Open my window', func=OnWindowButton)
