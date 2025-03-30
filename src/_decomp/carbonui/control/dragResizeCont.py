#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\dragResizeCont.py
from carbonui import Axis, AxisAlignment, uiconst
from carbonui.decorative.resize_handle import ResizeHandle
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
dividerAlign = {uiconst.TOLEFT: uiconst.TORIGHT,
 uiconst.TORIGHT: uiconst.TOLEFT,
 uiconst.TOTOP: uiconst.TOBOTTOM,
 uiconst.TOBOTTOM: uiconst.TOTOP,
 uiconst.TOLEFT_PROP: uiconst.TORIGHT,
 uiconst.TORIGHT_PROP: uiconst.TOLEFT,
 uiconst.TOTOP_PROP: uiconst.TOBOTTOM,
 uiconst.TOBOTTOM_PROP: uiconst.TOTOP}

class DragResizeCont(Container):
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_maxSize = 200
    default_minSize = 50
    default_defaultSize = 150
    default_settingsID = None
    default_dragAreaSize = 8

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.maxSize = attributes.Get('maxSize', self.default_maxSize)
        self.minSize = attributes.Get('minSize', self.default_minSize)
        self.settingsID = attributes.Get('settingsID', self.default_settingsID)
        self.onResizeCallback = attributes.Get('onResizeCallback', None)
        self.onDragCallback = attributes.Get('onDragCallback', None)
        dragAreaSize = attributes.Get('dragAreaSize', self.default_dragAreaSize)
        defaultSize = attributes.Get('defaultSize', self.default_defaultSize)
        handle_cross_axis_alignment = attributes.get('handle_cross_axis_alignment', AxisAlignment.CENTER)
        if self.align not in dividerAlign:
            raise ValueError('Invalid alignment mode selected. Must be push aligned to LEFT, TOP, RIGHT or BOTTOM')
        self.isHorizontal = self.align in (uiconst.TOLEFT,
         uiconst.TORIGHT,
         uiconst.TOLEFT_PROP,
         uiconst.TORIGHT_PROP)
        self.isProportional = self.align in (uiconst.TOLEFT_PROP,
         uiconst.TOTOP_PROP,
         uiconst.TORIGHT_PROP,
         uiconst.TOBOTTOM_PROP)
        self.isDraggin = False
        self.initialPos = None
        if self.settingsID:
            size = settings.user.ui.Get(self.settingsID, defaultSize)
        else:
            size = defaultSize
        self._SetSize(size)
        self.dragArea = Container(name='dragArea', parent=self, state=uiconst.UI_NORMAL, width=dragAreaSize, height=dragAreaSize)
        self.UpdateDragAreaAlign()
        self.mainCont = Container(parent=self, name='mainCont')
        if self.isHorizontal:
            orientation = Axis.VERTICAL
        else:
            orientation = Axis.HORIZONTAL
        ResizeHandle(parent=self.dragArea, align=uiconst.TOALL, orientation=orientation, cross_axis_alignment=handle_cross_axis_alignment, on_drag_start=self._on_drag_start, on_drag_move=self._on_drag_move, on_drag_end=self._on_drag_end, show_line=attributes.get('show_line', False))

    def UpdateDragAreaAlign(self):
        self.dragArea.align = dividerAlign[self.align]

    def IsInverse(self):
        return self.align in (uiconst.TORIGHT,
         uiconst.TORIGHT_PROP,
         uiconst.TOBOTTOM,
         uiconst.TOBOTTOM_PROP)

    def _GetPos(self):
        if self.isHorizontal:
            return uicore.uilib.x
        return uicore.uilib.y

    def SetAlign(self, align):
        super(DragResizeCont, self).SetAlign(align)
        if not self._constructingBase:
            self.UpdateDragAreaAlign()

    def _on_drag_start(self):
        self.OnDragAreaMouseDown()

    def _on_drag_move(self, delta):
        self.OnDragAreaMouseMove()

    def _on_drag_end(self):
        self.OnDragAreaMouseUp()

    def OnDragAreaMouseDown(self, *args):
        self.isDraggin = True
        self.initialPos = self._GetPos()
        self.parSize = self._GetParSize()

    def DisableDragResize(self):
        self.dragArea.Disable()
        self.dragArea.opacity = 0.0

    def EnableDragResize(self):
        self.dragArea.Enable()
        self.dragArea.opacity = 1.0

    def _GetParSize(self):
        parWidth, parHeight = self.parent.GetAbsoluteSize()
        parSize = parWidth if self.isHorizontal else parHeight
        return parSize

    def OnDragAreaMouseUp(self, *args):
        self.isDraggin = False
        settings.user.ui.Set(self.settingsID, self._GetSize())
        if self.onResizeCallback:
            self.onResizeCallback()

    def OnDragAreaMouseMove(self, *args):
        if not self.isDraggin:
            return
        newPos = self._GetPos()
        if self.IsInverse():
            self._ChangeSize(self.initialPos - newPos)
        else:
            self._ChangeSize(newPos - self.initialPos)
        l, t, w, h = self.GetAbsolute()
        if self.align in (uiconst.TOLEFT, uiconst.TOLEFT_PROP):
            self.initialPos = max(l + self.minSize, min(newPos, l + w))
        elif self.align in (uiconst.TORIGHT, uiconst.TORIGHT_PROP):
            self.initialPos = max(l, min(newPos, l + w - self.minSize))
        elif self.align in (uiconst.TOTOP, uiconst.TOTOP_PROP):
            self.initialPos = max(t + self.minSize, min(newPos, t + h))
        elif self.align in (uiconst.TOBOTTOM, uiconst.TOBOTTOM_PROP):
            self.initialPos = max(t, min(newPos, t + h - self.minSize))
        if self.onDragCallback:
            self.onDragCallback()

    def _GetSize(self):
        if self.isHorizontal:
            return self.width
        else:
            return self.height

    def GetMaxSize(self):
        if self.maxSize is not None:
            return self._ConvertSize(self.maxSize)

    def SetMaxSize(self, maxSize):
        self.maxSize = maxSize
        if self.maxSize is not None and self._GetSize() >= self.maxSize:
            self._SetSize(self.maxSize)

    def GetMinSize(self):
        return self._ConvertSize(self.minSize)

    def SetMinSize(self, minSize):
        self.minSize = minSize
        if self._GetSize() <= self.minSize:
            self._SetSize(self.minSize)

    def _ConvertSize(self, size):
        self.parSize = self._GetParSize()
        if size > 1:
            if self.isProportional:
                return float(size) / self.parSize
            else:
                return size
        else:
            if self.isProportional:
                return size
            return size * self.parSize

    def _OnSizeChange_NoBlock(self, width, height):
        self._UpdateSize(width, height)

    def UpdateSize(self):
        width, height = self.GetAbsoluteSize()
        self._UpdateSize(width, height)

    def _UpdateSize(self, width = None, height = None):
        if not self.pickState:
            return
        if width < 0 or height < 0:
            return
        size = width if self.isHorizontal else height
        size = self._ConvertSize(size)
        minSize = self._ConvertSize(self.minSize)
        if size < minSize:
            self._SetSize(minSize)
        if self.maxSize is not None:
            maxSize = self._ConvertSize(self.maxSize)
            if size > maxSize:
                self._SetSize(maxSize)

    def _SetSize(self, size):
        minSize = self._ConvertSize(self.minSize)
        size = max(minSize, size)
        if self.maxSize is not None:
            maxSize = self._ConvertSize(self.maxSize)
            size = min(size, maxSize)
        if self.isHorizontal:
            self.width = size
        else:
            self.height = size

    def _ChangeSize(self, diff):
        size = self._GetSize()
        if self.isProportional:
            size += float(diff) / self.parSize
        else:
            size += diff
        self._SetSize(size)
