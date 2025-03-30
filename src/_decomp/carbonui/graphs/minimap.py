#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\minimap.py
import carbonui.fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.various_unsorted import IsUnder
from eve.client.script.ui.control.eveLabel import Label
from carbonui.graphs import graph
from carbonui.uicore import uicore
from signals import Signal

class MapSlider(Container):
    default_name = 'mapslider'
    default_color = (1.0, 1.0, 1.0, 0.2)
    default_hoverColor = (1.0, 1.0, 1.0, 0.25)
    default_align = uiconst.TOPLEFT
    default_clipChildren = True
    resizeColor = (0.8, 0.8, 1.0, 0.1)
    resizeHandleColor = resizeColor
    resizeAreaSize = 10
    minimumExtraSpace = 0
    showHandle = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.beforeAxisUpdate = Signal(signalName='beforeAxisUpdate')
        self.onSliderStart = Signal(signalName='onSliderStart')
        self.onSliderReleased = Signal(signalName='onSliderReleased')
        self.onSliderWheel = Signal(signalName='onSliderWheel')
        self._axis = attributes['axis']
        self.MakeConnections()
        self.cursor = uiconst.UICURSOR_LEFT_RIGHT_DRAG
        self.drag = False
        self.dragOffset = 0
        self.color = attributes.get('color', self.default_color)
        self.hoverColor = attributes.get('hoverColor', self.default_hoverColor)
        self.frame = Frame(bgParent=self, texturePath='res:/UI/Texture/classes/Graph/MiniMap/zoomFrame.png', cornerSize=8, color=self.color)
        resizeAreaSize = self.resizeAreaSize
        self.minimumWidth = resizeAreaSize * 2 + self.minimumExtraSpace
        self.leftResize = Container(name='leftResize', parent=self, state=uiconst.UI_NORMAL, align=uiconst.TOLEFT, width=resizeAreaSize, height=resizeAreaSize, bgColor=self.resizeColor, opacity=0)
        self.leftHandle = Sprite(name='leftHandle', parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, pos=(-6, 0, 12, 12), color=self.resizeHandleColor, texturePath='res:/UI/Texture/classes/graph/sliderHandle.png')
        self.rightHandle = Sprite(name='rightHandle', parent=self, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, pos=(-6, 0, 12, 12), color=self.resizeHandleColor, texturePath='res:/UI/Texture/classes/graph/sliderHandle.png')
        self.leftHandle.display = False
        self.rightHandle.display = False
        self.leftResize.cursor = uiconst.UICORSOR_HORIZONTAL_RESIZE
        self.leftResize.OnMouseDown = self.OnLeftResizeMouseDown
        self.leftResize.OnMouseUp = self.OnLeftResizeMouseUp
        self.leftResize.OnMouseMove = self.OnResizeMouseMove
        self.rightResize = Container(name='rightResize', parent=self, state=uiconst.UI_NORMAL, align=uiconst.TORIGHT, width=resizeAreaSize, height=resizeAreaSize, bgColor=self.resizeColor, opacity=0)
        self.rightResize.cursor = uiconst.UICORSOR_HORIZONTAL_RESIZE
        self.rightResize.OnMouseDown = self.OnRightResizeMouseDown
        self.rightResize.OnMouseUp = self.OnRightResizeMouseUp
        self.rightResize.OnMouseMove = self.OnResizeMouseMove
        self.leftResize.OnMouseEnter = lambda *args, **kwargs: self.OnMouserEnterResizer(self.leftResize)
        self.leftResize.OnMouseExit = lambda *args, **kwargs: self.OnMouseExitResizer(self.leftResize)
        self.rightResize.OnMouseEnter = lambda *args, **kwargs: self.OnMouserEnterResizer(self.rightResize)
        self.rightResize.OnMouseExit = lambda *args, **kwargs: self.OnMouseExitResizer(self.rightResize)
        self.centerContainer = Container(parent=self)
        self.sliderLabel = Label(parent=self.centerContainer, align=uiconst.BOTTOMLEFT, fontsize=carbonui.fontconst.EVE_SMALL_FONTSIZE)
        self.sliderLabel.SetRGBA(1.0, 1.0, 1.0, 0.3)
        self.leftResizing = False
        self.rightResizing = False
        self.initialResize = (0, 0)
        self._AxisChanged(self._axis)

    def OnMouserEnterResizer(self, resizer):
        animations.FadeIn(resizer, duration=0.25)
        self.OnMouseEnter()

    def OnMouseExitResizer(self, resizer):
        animations.FadeOut(resizer, duration=0.25)
        if not IsUnder(uicore.uilib.mouseOver, self):
            self.OnMouseExit()

    def MakeConnections(self):
        self._axis.onChange.connect(self._AxisChanged)

    def _AxisChanged(self, _):
        self._ResizeSlider()

    def UpdateAlignment(self, *args, **kwargs):
        budget = super(MapSlider, self).UpdateAlignment(*args, **kwargs)
        self._ResizeSlider()
        return budget

    def _ResizeSlider(self):
        size = self.parent.GetAbsoluteSize()
        visibleRange = self._axis.GetVisibleRange()
        dataRange = self._axis.GetDataRange()
        start = (visibleRange[0] - dataRange[0]) / (dataRange[1] - dataRange[0])
        end = (visibleRange[1] - dataRange[0]) / (dataRange[1] - dataRange[0])
        sliderWidth = size[0] * (end - start)
        sliderPos = size[0] * start
        if sliderWidth < self.minimumWidth:
            sliderPos -= (self.minimumWidth - sliderWidth) * 0.5
        self.left = sliderPos
        self.width = max(sliderWidth, self.minimumWidth)
        self.sliderLabel.text = self._axis.GetRangeText(*visibleRange)

    def OnLeftResizeMouseDown(self, *_):
        self.onSliderStart()
        if not uicore.uilib.leftbtn:
            return
        self.resizeStart = uicore.uilib.x
        self.leftResizing = True

    def OnLeftResizeMouseUp(self, *_):
        self.onSliderReleased()
        self.leftResizing = False
        self._UpdateAxis()

    def OnResizeMouseMove(self, *args):
        parentWidth = float(self.parent.GetAbsoluteSize()[0])
        mouseX = uicore.uilib.x
        if self.leftResizing:
            resizeDelta = mouseX - self.resizeStart
            if resizeDelta > 50000:
                return
            self.resizeStart = mouseX
            if self.left + resizeDelta < 0:
                self.left = 0
                self.width -= self.left
            else:
                self.left += resizeDelta
                self.width -= resizeDelta
            if self.width < self.minimumWidth:
                self.left += self.width - self.minimumWidth
                self.width = self.minimumWidth
            self._UpdateAxis()
        elif self.rightResizing:
            resizeDelta = mouseX - self.resizeStart
            self.resizeStart = mouseX
            self.width += resizeDelta
            if self.width < self.minimumWidth:
                self.width = self.minimumWidth
            self.width = min(parentWidth - self.left, self.width)
            self._UpdateAxis()

    def OnMouseWheel(self, amount, *args):
        parentWidth = float(self.parent.GetAbsoluteSize()[0])
        x = uicore.uilib.x - self.GetAbsoluteLeft()
        t = x / float(self.width)
        added = amount / 10.0
        newWidth = max(self.width + added, self.minimumWidth)
        if self.width != newWidth:
            self.width = newWidth
            left_change = added * t if self.left + self.width <= parentWidth else added
            self.left -= left_change
            self.left = max(0, self.left)
            self.width = min(self.width, parentWidth)
            self.onSliderWheel(amount)
            self._UpdateAxis()

    def OnRightResizeMouseDown(self, *args):
        self.onSliderStart()
        if not uicore.uilib.leftbtn:
            return
        self.resizeStart = uicore.uilib.x
        self.rightResizing = True

    def OnRightResizeMouseUp(self, *args):
        self.rightResizing = False
        self._UpdateAxis()
        self.onSliderReleased()

    def OnMouseDown(self, *args):
        self.onSliderStart()
        if not uicore.uilib.leftbtn:
            return
        self.drag = True
        self.dragOffset = self.left - uicore.uilib.x
        self.OnMouseMove(*args)

    def OnMouseEnter(self, *args):
        if self.hoverColor:
            self.frame.color = self.hoverColor
        if self.showHandle:
            self.leftHandle.display = True
            self.rightHandle.display = True

    def OnMouseExit(self, *args):
        if IsUnder(uicore.uilib.mouseOver, self):
            return
        if self.color:
            self.frame.color = self.color
        if self.showHandle:
            self.leftHandle.display = False
            self.rightHandle.display = False

    def OnMouseUp(self, *args):
        self.onSliderReleased()
        self.drag = False

    def OnMouseMove(self, *args):
        if self.drag:
            pos = uicore.uilib.x + self.dragOffset
            pos = max(0, pos)
            parentWidth = float(self.parent.GetAbsoluteSize()[0])
            pos = min(pos, parentWidth - self.width)
            self.left = pos
            self._UpdateAxis()

    def UpdatePosition(self, pos):
        pos = max(0, pos)
        parentWidth = float(self.parent.GetAbsoluteSize()[0])
        pos = min(pos, parentWidth - self.width)
        self.left = pos

    def JumpToAndStartDrag(self, position):
        self.drag = True
        self.dragOffset = position

    def _GetVisibleRange(self):
        size = self.parent.GetAbsoluteSize()
        dataRange = self._axis.GetDataRange()
        start = float(self.left) / size[0]
        end = float(self.width) / size[0] + start
        visibleRange0 = start * (dataRange[1] - dataRange[0]) + dataRange[0]
        visibleRange1 = end * (dataRange[1] - dataRange[0]) + dataRange[0]
        return (visibleRange0, visibleRange1)

    def _UpdateAxis(self):
        self.beforeAxisUpdate()
        self._axis.SetVisibleRange(self._GetVisibleRange())


class MiniMap(graph.GraphArea):

    def ApplyAttributes(self, attributes):
        graph.GraphArea.ApplyAttributes(self, attributes)
        self.CreateSlider(attributes)

    def CreateSlider(self, attributes):
        controlAxis = attributes['controlAxis']
        size = self.GetAbsoluteSize()
        self.slider = MapSlider(parent=self, axis=controlAxis, height=size[1], width=1, left=0, top=0)

    def OnMouseDown(self, *args):
        if not uicore.uilib.leftbtn:
            return
        offset = uicore.uilib.x - self.GetAbsoluteLeft() - self.slider.width / 2.0
        self.slider.UpdatePosition(offset)
        self.slider.OnMouseDown(*args)

    def OnMouseMove(self, *args):
        self.slider.OnMouseMove(*args)

    def OnMouseUp(self, *args):
        self.slider.OnMouseUp()
