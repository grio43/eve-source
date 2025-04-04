#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\behaviortools\blackboardwindow.py
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.window import Window
import carbonui.const as uiconst

class BlackboardDebugWindow(Window):
    default_windowID = 'BehaviorDebugWindow'
    default_caption = 'Behavior Debug Tool'
    default_width = 600
    default_height = 500

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.taskMap = {}
        self.nodeCount = 0
        self.controller = None
        self.mainScroll = ScrollContainer(name='myScrollCont', parent=self.sr.main, align=uiconst.TOALL, padding=(4, 4, 4, 4))
