#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\outstandingmonitor.py
import blue
import uthread2
from carbon.common.script.sys import basesession
from carbon.common.script.util.format import FmtDate, FmtTime
from carbonui import uiconst
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window

class OutstandingMonitor(Window):
    default_caption = 'Outstanding Calls'
    default_windowID = 'outstandingcalls'
    default_minSize = (400, 300)
    refreshDelay = 0.5

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.scroll = Scroll(parent=self.sr.main, id='outstandingscroll', align=uiconst.TOALL)
        uthread2.StartTasklet(self.Refresh)

    def Refresh(self):
        while not self.destroyed:
            uthread2.Sleep(self.refreshDelay)
            self.PopulateScroll()

    def PopulateScroll(self, *args):
        scrolllist = []
        for ct in basesession.outstandingCallTimers:
            method = ct[0].replace('<', '&lt;').replace('>', '&gt;')
            t = ct[1]
            label = '%s<t>%s<t>%s' % (method, FmtDate(t, 'nl'), FmtTime(blue.os.GetWallclockTimeNow() - t))
            scrolllist.append(ScrollEntryNode(decoClass=SE_GenericCore, label=label))

        self.scroll.Load(contentList=scrolllist, headers=['method', 'time', 'dt'])
