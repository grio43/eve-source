#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\graph.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.graphs.axis import AxisOrientation
from carbonui.uicore import uicore

def _UnlockGraphs(locked):
    for each in locked:
        each.UnlockGraphUpdates()


class GraphArea(Container):
    default_state = uiconst.UI_ACTIVE
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self._horizontalAxis = attributes.get('horizontalAxis', [])
        self._verticalAxis = attributes.get('verticalAxis', [])
        self._zoomAxis = []
        self._panAxis = []
        self._isPanning = None
        self._prevPanPosition = (0, 0)

    def _OnResize(self, *args):
        Container._OnResize(self)
        width, height = self.GetAbsoluteSize()
        locked = self._LockGraphs()
        for each in self._horizontalAxis:
            each[0].SetViewportRange((each[1] * width, each[2] * width))

        for each in self._verticalAxis:
            each[0].SetViewportRange((each[1] * height, each[2] * height))

        _UnlockGraphs(locked)

    def AddAxis(self, orientation, axis, minFactor = 0.0, maxFactor = 1.0):
        width, height = self.GetAbsoluteSize()
        if orientation == AxisOrientation.HORIZONTAL:
            self._horizontalAxis.append((axis,
             minFactor,
             maxFactor,
             AxisOrientation.HORIZONTAL))
            axis.SetViewportRange((minFactor * width, maxFactor * width))
        else:
            self._verticalAxis.append((axis,
             minFactor,
             maxFactor,
             AxisOrientation.VERTICAL))
            axis.SetViewportRange((minFactor * height, maxFactor * height))

    def AddZoomAxis(self, axis):
        self._zoomAxis.append(self._FindAxis(axis))

    def AddPanAxis(self, axis):
        self._panAxis.append(self._FindAxis(axis))

    def _FindAxis(self, axis):
        result = None
        for each in self._horizontalAxis:
            if each[0] == axis:
                result = each
                break

        if result is None:
            for each in self._verticalAxis:
                if each[0] == axis:
                    result = each
                    break

        if result is None:
            raise ValueError('axis needs to be added first with AddAxis')
        return result

    def OnMouseDown(self, *args):
        if not uicore.uilib.leftbtn:
            return
        self._isPanning = True
        self._prevPanPosition = (uicore.uilib.x, uicore.uilib.y)

    def OnMouseUp(self, *args):
        self._isPanning = False

    def OnMouseMove(self, *args):
        if not self._isPanning or not self._panAxis:
            return
        newPos = (uicore.uilib.x, uicore.uilib.y)
        if newPos != self._prevPanPosition:
            width, height = self.GetAbsoluteSize()
            locked = self._LockGraphs()
            for axis, minv, maxv, orientation in self._panAxis:
                if orientation == AxisOrientation.HORIZONTAL:
                    delta = float(newPos[0] - self._prevPanPosition[0]) / width
                    axis.Pan(-delta * (maxv - minv))
                else:
                    delta = float(newPos[1] - self._prevPanPosition[1]) / height
                    axis.Pan(-delta * (maxv - minv))

            _UnlockGraphs(locked)
            self._prevPanPosition = newPos

    def OnMouseWheel(self, event, *args):
        if not self._zoomAxis:
            return
        locked = self._LockGraphs()
        l, t = self.GetAbsolutePosition()
        x, y = uicore.uilib.x - l, uicore.uilib.y - t
        size = self.GetAbsoluteSize()
        rx = min(max(x / float(size[0]), 0.0), 1.0)
        ry = min(max(y / float(size[1]), 0.0), 1.0)
        change = 0.1
        if event < 0:
            change = -change
        for axis, minv, maxv, orientation in self._zoomAxis:
            if orientation == AxisOrientation.HORIZONTAL:
                axis.Zoom(change, minv * (1 - rx) + maxv * rx)
            else:
                axis.Zoom(change, minv * (1 - ry) + maxv * ry)

        _UnlockGraphs(locked)

    def _LockGraphs(self):
        locked = []
        for each in self.children:
            cb = getattr(each, 'LockGraphUpdates', None)
            if cb:
                cb()
                locked.append(each)

        return locked
