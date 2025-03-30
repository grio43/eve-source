#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\engineinfopanel.py
import localization
import carbonversion
from carbon.common.script.util.format import FmtAmt
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import Label
import blue
import uthread2

def GetMemoryLabel(memory, last, base):
    RED = '0xffff0000'
    GREEN = '0xff00ff00'
    delta = last - memory
    if delta < 0:
        delta = -delta
        deltaColor = RED
    else:
        deltaColor = GREEN
    totalDelta = base - memory
    if totalDelta < 0:
        totalDelta = -totalDelta
        totalDeltaColor = RED
    else:
        totalDeltaColor = GREEN
    memoryStr = FmtAmt(memory / 1024)
    deltaStr = FmtAmt(delta / 1024)
    totalDeltaStr = FmtAmt(totalDelta / 1024)
    text = '%s / <color=%s>%s</color> / <color=%s>%s</color>' % (memoryStr,
     deltaColor,
     deltaStr,
     totalDeltaColor,
     totalDeltaStr)
    return text


class EngineInfoPanel(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.cv = carbonversion.get_carbon_version()
        infoLeft = Container(parent=self, align=uiconst.TOLEFT_PROP, width=0.5)
        infoRight = Container(parent=self, align=uiconst.TOALL)
        self.carbonVersionLabel = Label(parent=infoLeft, align=uiconst.TOTOP, maxLines=1)
        self.fpsLabel = Label(parent=infoLeft, align=uiconst.TOTOP, maxLines=1)
        self.workingSetLabel = Label(parent=infoLeft, align=uiconst.TOTOP, maxLines=1)
        self.commitSizeLabel = Label(parent=infoLeft, align=uiconst.TOTOP, maxLines=1)
        self.resCacheLabel = Label(parent=infoRight, align=uiconst.TOTOP, maxLines=1)
        self.wineVersionLabel = Label(parent=infoRight, align=uiconst.TOTOP, maxLines=1)
        self.rosettaLabel = Label(parent=infoRight, align=uiconst.TOTOP, maxLines=1)
        self.fpsStat = blue.statistics.Find('FPS')
        self.frameTimeStat = blue.statistics.Find('Trinity/SmoothedFrameTime')
        self.workingSetStat = blue.statistics.Find('Blue/Memory/WorkingSet')
        self.lastWorkingSetSize = 0
        self.baseWorkingSetSize = self.workingSetStat.value
        self.commitSizeStat = blue.statistics.Find('Blue/Memory/PageFileUsage')
        self.lastCommitSize = 0
        self.baseCommitSize = self.commitSizeStat.value
        self.wineVersionLabel.text = 'Not running Wine'
        if blue.sysinfo.isWine:
            self.wineVersionLabel.text = 'Wine %s: %s' % (blue.sysinfo.wineVersion, blue.sysinfo.wineHostOs)
        self.rosettaLabel.text = 'Running Rosetta' if blue.sysinfo.isRosetta else 'Not running Rosetta'
        uthread2.StartTasklet(self.Update)

    def Update(self):
        while not self.destroyed:
            self.UpdateInfo()
            uthread2.Sleep(0.5)

    def UpdateInfo(self):
        self.carbonVersionLabel.text = localization.GetByLabel('UI/CarbonInfoWindow/CarbonEngineVersion', engineVersion=self.cv.get_version())
        self.fpsLabel.text = 'Fps: %6.2f (%5.1fms)' % (self.fpsStat.value / 100.0, self.frameTimeStat.value * 1000.0)
        self.workingSetLabel.text = 'Working set: ' + GetMemoryLabel(self.workingSetStat.value, self.lastWorkingSetSize, self.baseWorkingSetSize)
        self.commitSizeLabel.text = 'Commit size: ' + GetMemoryLabel(self.commitSizeStat.value, self.lastCommitSize, self.baseCommitSize)
        self.lastWorkingSetSize = self.workingSetStat.value
        self.lastCommitSize = self.commitSizeStat.value
        inUse = FmtAmt(blue.motherLode.memUsage / 1024)
        total = FmtAmt(blue.motherLode.maxMemUsage / 1024)
        num = blue.motherLode.size()
        self.resCacheLabel.text = 'Resource Cache Usage: %sK / %sK - %s objects' % (inUse, total, num)
