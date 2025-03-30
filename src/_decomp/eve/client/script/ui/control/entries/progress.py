#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\progress.py
import blue
import localization
import uthread
from carbonui import uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall

class Progress(SE_BaseClassCore):
    __guid__ = 'listentry.Progress'
    __params__ = ['header', 'startTime', 'duration']

    def Startup(self, args):
        header = EveLabelMedium(text='', parent=self, left=2, top=2, state=uiconst.UI_DISABLED)
        p = Container(name='gauge', parent=self, width=84, height=14, left=6, top=20, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0)
        t = EveLabelSmall(text='', parent=p, left=6, top=7, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        f = Fill(parent=p, align=uiconst.RELATIVE, width=1, height=10, left=2, top=2, color=(1.0, 1.0, 1.0, 0.25))
        Frame(parent=p, color=(1.0, 1.0, 1.0, 0.5))
        self.sr.progress = p
        self.sr.progressFill = f
        self.sr.progressHeader = header
        self.sr.progressText = t

    def Load(self, node):
        self.sr.node = node
        self.sr.progressHeader.text = node.header
        uthread.new(self.LoadProgress)

    def LoadProgress(self):
        if not hasattr(self, 'sr'):
            return
        startTime = self.sr.node.startTime
        duration = self.sr.node.duration
        maxWidth = self.sr.progress.width - self.sr.progressFill.left * 2
        self.sr.progress.state = uiconst.UI_DISABLED
        while self and not self.destroyed:
            msFromStart = max(0, blue.os.TimeDiffInMs(startTime, blue.os.GetSimTime()))
            portion = 1.0
            if msFromStart:
                portion -= float(msFromStart) / duration
            self.sr.progressFill.width = int(maxWidth * portion)
            diff = max(0, duration - msFromStart)
            self.sr.progressText.text = localization.GetByLabel('UI/Control/Entries/Seconds', seconds=diff / 1000.0)
            if msFromStart > duration:
                break
            blue.pyos.synchro.Yield()

    def GetHeight(self, *args):
        node, width = args
        node.height = 40
        return node.height
