#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\dragdrop.py
import carbonui.const as uiconst
import uthread

class DragDropObject(object):
    dragData = []
    _dragEnabled = False
    _dragging = False
    _lastOverObject = None
    _dragMouseDown = None
    Draggable_blockDrag = False
    isDragObject = False
    isDropLocation = False

    def __init__(self):
        object.__init__(self)
        dragEvents = ['OnExternalDragInitiated', 'OnExternalDragEnded']
        if hasattr(self, '__notifyevents__') and self.__notifyevents__ is not None:
            self.__notifyevents__.extend(dragEvents)
        else:
            self.__notifyevents__ = dragEvents
        sm.RegisterNotify(self)

    def MakeDragObject(self):
        self.isDragObject = True

    def MakeDropLocation(self):
        self.isDropLocation = True

    def EnableDrag(self):
        self.Draggable_blockDrag = False

    def DisableDrag(self):
        self.Draggable_blockDrag = True

    def IsDraggable(self):
        return self.isDragObject and not self.Draggable_blockDrag

    def IsBeingDragged(self):
        return self._dragging

    def GetDragData(self):
        return self.dragData

    def PrepareDrag(self, dragContainer, dragSource):
        from eve.client.script.ui.util.eveOverrides import PrepareDrag_Override
        return PrepareDrag_Override(dragContainer, dragSource)

    def OnDragCanceled(self, dragSource, dragData):
        pass

    def OnEndDrag(self, dragSource, dropLocation, dragData):
        pass

    def VerifyDrag(self, dragDestination, dragData):
        return True

    def OnMouseDownDrag(self, *args):
        from carbonui.uicore import uicore
        if not uicore.IsDragging() and self.isDragObject:
            self._dragMouseDown = (uicore.uilib.x, uicore.uilib.y)
            self._dragEnabled = True
            uicore.dragObject = None

    def OnMouseMoveDrag(self, *args):
        from carbonui.uicore import uicore
        if uicore.IsDragging():
            if uicore.dragObject is not self and self.isDropLocation:
                uthread.new(self.OnDragMove, uicore.dragObject, uicore.dragObject.dragData)
        elif not self.IsBeingDragged() and self._dragEnabled and not self.Draggable_blockDrag and uicore.uilib.mouseTravel >= 6:
            self._dragging = True
            uthread.new(self._BeginDrag).context = 'DragObject::_BeginDrag'

    def _BeginDrag(self):
        dragData = self.GetDragData()
        if not dragData:
            self._dragEnabled = False
            self._dragging = False
            return
        from carbonui.uicore import uicore
        if uicore.uilib.GetMouseCapture() == self:
            uicore.uilib.ReleaseCapture()
        mouseExitArgs, mouseExitHandler = self.FindEventHandler('OnMouseExit')
        if mouseExitHandler:
            mouseExitHandler(*mouseExitArgs)
        from carbonui.control.dragdrop.dragContainer import DragContainer
        dragContainer = DragContainer(name='dragContainer', align=uiconst.ABSOLUTE, idx=0, pos=(0, 0, 32, 32), state=uiconst.UI_DISABLED, parent=uicore.layer.dragging, dragData=dragData)
        self._DoDrag(dragContainer)

    def _DoDrag(self, dragContainer):
        if dragContainer.destroyed:
            return
        dragData = dragContainer.dragData
        mouseOffset = self.PrepareDrag(dragContainer, self)
        if self.destroyed:
            return
        from carbonui.uicore import uicore
        uicore.dragObject = dragContainer
        sm.ScatterEvent('OnExternalDragInitiated', self, dragData)
        try:
            dragContainer.InitiateDrag(mouseOffset)
        finally:
            dropLocation = uicore.uilib.mouseOver
            sm.ScatterEvent('OnExternalDragEnded', self, dropLocation, dragData)
            uicore.dragObject = None

        if self._dragEnabled:
            self._dragEnabled = False
            self._dragging = False
            self.KillDragContainer(dragContainer)
            dropLocation = uicore.uilib.mouseOver
            if dropLocation.isDropLocation and self.VerifyDrag(dropLocation, dragData) and dropLocation.VerifyDrop(self, dragData):
                uthread.new(dropLocation.OnDropData, self, dragData)
            else:
                self.OnDragCanceled(self, dragData)
        self.OnEndDrag(self, dropLocation, dragData)

    def KillDragContainer(self, dragContainer):
        from carbonui.uicore import uicore
        uicore.layer.dragging.Flush()

    def CancelDrag(self):
        from carbonui.uicore import uicore
        self._dragEnabled = False
        self._dragging = None
        uicore.dragObject = None
        uicore.layer.dragging.Flush()

    def OnDragMove(self, dragSource, dragData):
        pass

    def OnDragExit(self, dragSource, dragData):
        pass

    def OnDragEnter(self, dragSource, dragData):
        pass

    def OnDropData(self, dragSource, dragData):
        pass

    def VerifyDrop(self, dragSource, dragData):
        return True

    def OnExternalDragInitiated(self, dragSource, dragData):
        pass

    def OnExternalDragEnded(self, dragSource, dropLocation, dragData):
        pass
