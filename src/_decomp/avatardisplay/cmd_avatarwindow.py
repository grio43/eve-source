#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\avatardisplay\cmd_avatarwindow.py
from carbonui.control.window import Window
from carbonui.primitives.container import Container

class MyWindow(Window):
    default_caption = 'Test Character Window'
    default_windowID = 'myWindowUniqueID'
    default_width = 300
    default_height = 300
    default_someValue = 10
    default_otherValue = 20

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        someValue = attributes.Get('someValue', self.default_someValue)
        otherValue = attributes.Get('otherValue', self.default_otherValue)
        self.sr.sceneContainer = Container(name='sceneContainer', parent=self.sr.main)
