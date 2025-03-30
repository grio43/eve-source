#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\draggableShareContainer.py
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import DraggableIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.labelEditable import LabelEditable

class DraggableShareContainer(LayoutGrid):
    default_state = uiconst.UI_PICKCHILDREN
    default_align = uiconst.CENTERRIGHT
    default_name = 'draggableShareContainer'

    def ApplyAttributes(self, attributes):
        self.sharedNameLabel = None
        LayoutGrid.ApplyAttributes(self, attributes)
        self.columns = 2
        maxLength = attributes.get('maxLength', 40)
        currentText = attributes.currentText
        defaultText = attributes.defaultText
        configName = attributes.configName
        hintText = attributes.hintText
        self.getDragDataFunc = attributes.getDragDataFunc
        self.sharedNameLabel = LabelEditable(name='%s_LabelEditable' % configName, parent=self, align=uiconst.CENTERRIGHT, pos=(0, 1, 0, 0), text=currentText, hint=hintText, configName=configName, maxLength=maxLength, minLength=2, defaultText=defaultText)
        self.dragCont = dragCont = Container(parent=self, name='dragCont', pos=(6, 0, 30, 21), align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL)
        Frame(bgParent=dragCont, color=(1, 1, 1, 0.15))
        f = Fill(bgParent=dragCont, color=(1.0, 1.0, 1.0, 0.125))
        f.display = False
        dragSprite = Sprite(parent=dragCont, pos=(3, 0, 15, 15), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Overview/shareableOverview_small.png')
        text = localization.GetByLabel('UI/Overview/ShareOverview')
        shareText = EveLabelMedium(text=text, parent=dragCont, left=20, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        dragCont.width = shareText.textwidth + shareText.left + 9
        dragCont.hint = hintText
        dragCont.cursor = uiconst.UICURSOR_DRAGGABLE

        def ChangeDisplayState(display, *args):
            f.display = display

        dragCont.OnMouseEnter = (ChangeDisplayState, True)
        dragCont.OnMouseExit = (ChangeDisplayState, False)
        for eachObject in (dragCont, self.sharedNameLabel.textLabel):
            eachObject.isDragObject = True
            eachObject.GetDragData = self.GetObjectDragData
            eachObject.PrepareDrag = self.PrepareObjectDrag

    def GetObjectDragData(self):
        return self.getDragDataFunc(self.sharedNameLabel.GetValue())

    def PrepareObjectDrag(self, dragContainer, dragSource):
        icon = DraggableIcon(align=uiconst.TOPLEFT, pos=(0, 0, 64, 64))
        icon.LoadIcon('res:/UI/Texture/classes/Overview/shareableOverview.png')
        dragContainer.children.append(icon)
        return (0, 0)

    def SetMaxWidth(self, width):
        if self.sharedNameLabel is None:
            return
        maxLabelWidth = width - self.dragCont.width - self.dragCont.left
        self.sharedNameLabel.SetMaxWidth(maxLabelWidth)
