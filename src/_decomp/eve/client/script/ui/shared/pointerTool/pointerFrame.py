#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\pointerFrame.py
from carbonui.primitives.frame import Frame
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.pointerTool.pointerToolFraming import ChangePickStateOfAllFrames
from eve.client.script.ui.shared.pointerTool.pointerToolFunctions import GetInfoOnElementUnderMouse
from utillib import KeyVal
from carbonui.uicore import uicore
BLUE_COLOR = (0.2, 0.6, 1)

class PointerFrame(Frame):
    default_frameConst = uiconst.FRAME_BORDER1_CORNER9

    @apply
    def frameWidth():

        def fset(self, value):
            self.width = int(value - self.left)

        return property(**locals())

    @apply
    def frameHeight():

        def fset(self, value):
            self.height = int(value - self.top)

        return property(**locals())


class PointerFill(Container):
    default_state = uiconst.UI_DISABLED
    isDragObject = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.uiElementName = attributes.uiElementName
        self.name = 'pointerFill_%s' % self.uiElementName
        color = attributes.get('colorRGB', BLUE_COLOR)
        self.pointerFrame = Frame(parent=self, color=color + (0.4,), frameConst=uiconst.FRAME_BORDER1_CORNER9)
        self.pointerFill = Frame(parent=self, color=color + (0.2,), frameConst=uiconst.FRAME_FILLED_CORNER9)

    def OnMouseMoveDrag(self, *args):
        if not uicore.IsDragging() and not self.IsBeingDragged() and self._dragEnabled and not self.Draggable_blockDrag and uicore.uilib.mouseTravel >= 6:
            self._ChangePickStateOfAllFrames(isEnabled=False)
        Container.OnMouseMoveDrag(self)

    def GetDragData(self):
        try:
            x, y = self._dragMouseDown
            _, mouseOver = uicore.uilib.PickScreenPosition(uicore.ScaleDpi(x), uicore.ScaleDpi(y))
            pointerObj = GetInfoOnElementUnderMouse(mouseOver, x, y)
            if not pointerObj:
                return
            fakeNode = KeyVal(__guid__='listentry.PointerWndEntry', pointerObjects=[pointerObj])
            return [fakeNode]
        finally:
            self._ChangePickStateOfAllFrames(isEnabled=True)

    def PrepareDrag(self, dragContainer, dragSource):
        mx, my = Container.PrepareDrag(self, dragContainer, dragSource)
        if dragContainer.dragData:
            dragData = dragContainer.dragData[0]
            text = dragData.pointerObjects[0].label
            label = EveLabelMedium(parent=dragContainer, align=uiconst.TOPLEFT, text=text)
            if dragContainer.children:
                dragContainer.children[0].top = label.textheight + 4
        return (mx, my)

    def _ChangePickStateOfAllFrames(self, isEnabled):
        pointerOverlay = sm.GetService('helpPointer').GetPointerOverlay()
        ChangePickStateOfAllFrames(pointerOverlay.fillDict, isEnabled)
