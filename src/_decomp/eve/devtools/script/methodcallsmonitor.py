#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\methodcallsmonitor.py
import carbonui
import eveicon
import uthread2
from carbon.common.script.sys import basesession
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst, Align
from carbonui.control.button import Button
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.common.lib import appConst as const

class MethodCallsMonitor(Window):
    default_caption = 'Monolith Remote Method Calls'
    default_windowID = 'methodcalls'
    default_minSize = (400, 300)
    refreshDelay = 0.5

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.is_paused = False
        self.settingsContainer = Container(parent=self.sr.main, align=uiconst.TOTOP, height=32, padTop=16)
        self.ConstructSettings()
        self.scroll = Scroll(parent=self.sr.main, id='methodcallsscroll', align=uiconst.TOALL, padTop=8)
        self.Update()
        self._ready = True
        uthread2.StartTasklet(self.Refresh)

    def ConstructSettings(self):
        self.filterEdit = QuickFilterEdit(parent=self.settingsContainer, align=uiconst.TOLEFT, width=150, callback=self.PopulateScroll)
        self.pauseButton = Button(parent=self.settingsContainer, texturePath=eveicon.pause, align=uiconst.TOLEFT, func=self.TogglePause, hint='Pause/Resume list updates (history will still be collected)', padLeft=8)
        Button(parent=self.settingsContainer, label='Clear History', align=uiconst.TORIGHT, func=self.ClearHistory)
        self.numEntriesText = carbonui.TextBody(parent=ContainerAutoSize(parent=self.settingsContainer, align=uiconst.TORIGHT, padRight=8), align=Align.CENTERLEFT)

    def ClearHistory(self, *args):
        basesession.methodCallHistory.clear()
        self.Update()

    def Update(self):
        self.PopulateScroll()
        self.numEntriesText.text = u'{}/{}'.format(len(basesession.methodCallHistory), basesession.methodCallHistory.maxlen)

    def TogglePause(self, *args):
        self.is_paused = not self.is_paused
        self.pauseButton.texturePath = eveicon.play if self.is_paused else eveicon.pause

    def Refresh(self):
        while not self.destroyed:
            uthread2.Sleep(self.refreshDelay)
            if not self.is_paused:
                self.Update()

    def PopulateScroll(self, *args):
        contentList = []
        history = list(basesession.methodCallHistory)
        history.reverse()
        filter = self.filterEdit.text.lower()
        count = 0
        for ct in history:
            method = ct[0].replace('<', '&lt;').replace('>', '&gt;')
            if filter and filter not in method.lower():
                continue
            t = ct[1]
            label = '%s<t>%s<t>%s' % (method, FmtDate(t, 'nl'), ct[2] / const.MSEC)
            contentList.append(ScrollEntryNode(decoClass=SE_GenericCore, label=label))
            count += 1
            if count == 100:
                break

        self.scroll.Load(contentList=contentList, noContentHint='No calls found', headers=['method', 'time', 'ms'])
