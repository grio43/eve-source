#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\ledger\genericMiniMap.py
from carbonui.graphs.minimap import MapSlider, MiniMap
from eve.client.script.ui.control.eveLabel import Label
from carbonui.fontconst import EVE_SMALL_FONTSIZE
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from eve.client.script.ui.shared.ledger.ledgerUtil import GetMinDayTimeStamp, GetMaxDayTimeStamp
from signals.signalUtil import ChangeSignalConnect
import carbonui.const as uiconst
RESIZE_COLOR = (0.8, 0.8, 1.0, 0.05)
RESIZE_AREA = 10

class MinimapSliderForStandaloneMinimap(MapSlider):
    default_clipChildren = False
    default_state = uiconst.UI_NORMAL
    resizeColor = (0.8, 0.8, 1.0, 0.1)
    resizeHandleColor = resizeColor[:3] + (0.5,)
    minimumExtraSpace = 10
    default_hoverColor = (1.0, 1.0, 1.0, 0.5)
    showHandle = True

    def ApplyAttributes(self, attributes):
        self.sliderController = attributes.sliderController
        self.sliderLabelRight = None
        MapSlider.ApplyAttributes(self, attributes)
        self.sliderLabel.align = uiconst.TOPLEFT
        self.sliderLabel.SetRGBA(1.0, 1.0, 1.0, 0.75)
        self.InitSliderLabelIfNeeded()

    def InitSliderLabelIfNeeded(self):
        if not self.sliderLabelRight or self.sliderLabelRight.destroyed:
            self.sliderLabelRight = Label(name='sliderLabelRight', parent=self.centerContainer, align=uiconst.BOTTOMRIGHT, fontsize=EVE_SMALL_FONTSIZE)
            self.sliderLabelRight.SetRGBA(1.0, 1.0, 1.0, 0.75)

    def MakeConnections(self):
        self.ChangeSignalConnection()

    def _AxisChanged(self, *args):
        self._ResizeSlider()

    def _ResizeSlider(self, *args):
        self.InitSliderLabelIfNeeded()
        parentWidth, parentHeight = self.parent.GetAbsoluteSize()
        start, end = self.sliderController.GetStartAndEndPoint()
        slierWidth = parentWidth * (end - start)
        sliderPos = parentWidth * start
        self.left = sliderPos
        self.width = slierWidth
        visibleRange0, visibleRange1 = self.sliderController.GetVisibleRange()
        visibleRange0 = GetMinDayTimeStamp(visibleRange0)
        visibleRange1 = GetMaxDayTimeStamp(visibleRange1)
        self.sliderLabel.text = self.sliderController.GetRangeForTimestamp(visibleRange0)
        self.sliderLabelRight.text = self.sliderController.GetRangeForTimestamp(visibleRange1)

    def _GetVisibleRange(self):
        parentWidth, parentHeight = self.parent.GetAbsoluteSize()
        dataRangeStart, dataRangeEnd = self.sliderController.GetDataRange()
        start = float(self.left) / parentWidth
        end = float(self.width) / parentWidth + start
        dataRange = dataRangeEnd - dataRangeStart
        visibleRange0 = start * dataRange + dataRangeStart
        visibleRange1 = end * dataRange + dataRangeStart
        return (long(visibleRange0), long(visibleRange1))

    def _UpdateAxis(self):
        self.sliderController.SetVisibleRange(self._GetVisibleRange())

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.sliderController.on_change, self._AxisChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def Close(self):
        with EatSignalChangingErrors(errorMsg='MinimapSliderForStandaloneMinimap'):
            self.ChangeSignalConnection(connect=False)
        MapSlider.Close(self)


class GenericMiniMap(MiniMap):

    def CreateSlider(self, attributes):
        self.sliderController = attributes.sliderController
        size = self.GetAbsoluteSize()
        self.slider = MinimapSliderForStandaloneMinimap(parent=self, axis=None, sliderController=self.sliderController, height=size[1], width=1, left=0, top=0)

    def OnDblClick(self, *args):
        dataRange = self.sliderController.GetDataRange()
        self.sliderController.SetVisibleRange(dataRange)
