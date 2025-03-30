#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\moveMeWindow.py
from eve.client.script.ui.control.entries.button import ButtonEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.eveScroll import Scroll

class MoveMeWnd(Window):
    default_windowID = 'moveMeWnd'
    default_caption = 'Move me'
    default_height = 200

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        solarSystems = attributes.solarSystems
        self.scroll = Scroll(parent=self.sr.main)
        self.LoadScroll(solarSystems)

    def LoadScroll(self, systems):
        scrollList = []
        for eachSystem in systems:
            entry = GetFromClass(ButtonEntry, {'label': eachSystem,
             'caption': 'Move To',
             'OnClick': self.MoveToSystem,
             'args': (eachSystem,)})
            scrollList.append(entry)

        self.scroll.Load(contentList=scrollList)

    def MoveToSystem(self, destinationName, *args):
        sm.GetService('publicQaToolsClient').MoveMeTo(destinationName)
        eve.Message('CustomNotify', {'notify': 'Moving to %s' % destinationName})
        self.Close()
