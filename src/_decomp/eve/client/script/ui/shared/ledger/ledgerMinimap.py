#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\ledger\ledgerMinimap.py
import signals
import uthread
from carbon.common.script.util.format import FmtDate
from carbonui.graphs import axis
from carbonui.graphs.areagraph import AreaGraph
from carbonui.graphs.axis import FixupRange
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.ledger.ledgerUtil import GetDataForMinimap, GetDataForPersonaMinimap
from eve.client.script.ui.shared.ledger.genericMiniMap import GenericMiniMap
from localization import GetByLabel

class LedgerMinimap(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sliderController = attributes.sliderController
        self.miniMap = GenericMiniMap(name='MiniMap', parent=self, align=uiconst.TOALL, sliderController=self.sliderController)
        self.noContentLabel = EveLabelMedium(parent=self, text='%s' % GetByLabel('UI/Ledger/NoDataToDisplay'), idx=0, align=uiconst.CENTER)
        self.noContentLabel.display = False
        self.areaGraph = None
        self.horizontalAxis = axis.MonthlyTimeAxis([])
        self.miniMap.AddAxis(axis.AxisOrientation.HORIZONTAL, self.horizontalAxis)
        minValue = 0
        maxValue = 1
        self.verticalAxis = axis.AutoTicksAxis((minValue, maxValue), behavior=axis.AXIS_FROM_ZERO)
        self.miniMap.AddAxis(axis.AxisOrientation.VERTICAL, self.verticalAxis, 1.0, 0.0)

    def LoadMiniMap(self, summaryData):
        data = [ x[1] for x in summaryData ]
        timestamps = [ x[0] for x in summaryData ]
        if self.areaGraph:
            self.areaGraph.Close()
        self.horizontalAxis.SetDataPoints(timestamps, True)
        minValue = min(data) if data else 0
        maxValue = max(data) if data else 1
        self.verticalAxis.SetDataRange(FixupRange((minValue, maxValue)))
        self.areaGraph = AreaGraph(parent=self.miniMap, categoryAxis=self.horizontalAxis, valueAxis=self.verticalAxis, values=data, graphColor=(1.0,
         1.0,
         1.0,
         0.09), state=uiconst.UI_DISABLED)
        if data and any(data):
            self.noContentLabel.display = False
        else:
            self.noContentLabel.display = True


class MiniMapSliderController(object):

    def __init__(self, minRange, maxRange):
        self.on_change = signals.Signal(signalName='on_change')
        self._dataRange = (minRange, maxRange)
        storedRange = _GetSetting('dateRange', 30 * const.DAY)
        visibleMin = max(minRange, maxRange - storedRange)
        self._visibleRange = (visibleMin, maxRange)

    def GetVisibleRange(self):
        return self._visibleRange

    def GetDataRange(self):
        return self._dataRange

    def GetRangeText(self, start, end):
        return '%s - %s' % (self.GetRangeForTimestamp(start), self.GetRangeForTimestamp(end))

    def GetRangeForTimestamp(self, timestamp):
        return FmtDate(timestamp, 'ln')

    def SetVisibleRange(self, visibleRange):
        self._visibleRange = visibleRange
        self.SetSettings()
        self._OnChange()

    def _OnChange(self):
        self.on_change()

    def GetStartAndEndPoint(self):
        visibleStart, visibleEnd = self.GetVisibleRange()
        dataStart, dataEnd = self.GetDataRange()
        dataRange = dataEnd - dataStart
        start = float(visibleStart - dataStart) / dataRange
        end = float(visibleEnd - dataStart) / dataRange
        return (start, end)

    def SetSettings(self):
        _SetSetting('dateRange', int(self._visibleRange[1] - self._visibleRange[0]))


def _GetSetting(name, default):
    return settings.user.ui.Get('ledger_setting_%s' % name, default)


def _SetSetting(name, value):
    settings.user.ui.Set('ledger_setting_%s' % name, value)
