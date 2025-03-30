#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\dragdrop\dragContainer.py
import blue
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore

class DragContainer(Container):
    _dragInited = False
    dragSound = uiconst.SOUND_DRAGDROPLOOP

    def ApplyAttributes(self, attributes):
        super(DragContainer, self).ApplyAttributes(attributes)
        dragData = attributes.dragData
        if not isinstance(dragData, (list, tuple)):
            dragData = (dragData,)
        self.dragData = dragData

    def _OnClose(self, *args):
        uicore.audioHandler.StopSoundLoop(self.dragSound)
        Container._OnClose(self, *args)
        self.dragData = None

    def InitiateDrag(self, mouseOffset):
        if not self or self.destroyed or self._dragInited:
            return
        self._dragInited = True
        uicore.audioHandler.StartSoundLoop(self.dragSound)
        mx, my = mouseOffset
        while uicore.uilib.leftbtn and not self.destroyed and uicore.IsDragging():
            self.state = uiconst.UI_DISABLED
            self.left = uicore.uilib.x - mx
            self.top = uicore.uilib.y - my
            blue.pyos.synchro.Yield()
