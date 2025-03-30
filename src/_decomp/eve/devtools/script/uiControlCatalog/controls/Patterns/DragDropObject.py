#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Patterns\DragDropObject.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Types'
    description = "If you want a UI object to provide drag data, assign it an 'isDragData=True', define a GetDragData method that returns a list of DragData objects and make sure the item is pickable. You can also dragyour draggables to any text edit, such as the chat to create links."

    def construct_sample(self, parent):
        cont = Container(name='cont', parent=parent, align=uiconst.TOPLEFT, width=300, height=100)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.control.dragdrop.dragdata import BaseDragData, TypeDragData, OwnerDragData, SkillLevelDragData

        class DragContainer(Container):
            isDragObject = True
            default_state = uiconst.UI_NORMAL

            def GetDragData(self):
                item1 = TypeDragData(typeID=2203)
                item2 = OwnerDragData(owner_id=session.charid)
                item3 = SkillLevelDragData(typeID=3327, level=3)
                return [item1, item2, item3]

        class DropContainer(Container):
            default_state = uiconst.UI_NORMAL

            def OnDropData(self, dragSource, dragData):
                if dragData and isinstance(dragData[0], BaseDragData):
                    txt = 'Items dropped:\n'
                    txt += '\n'.join((d.get_link() for d in dragData))
                    ShowQuickMessage(txt)
                self.opacity = 1.0

            def OnDragEnter(self, dragSource, dragData):
                self.opacity = 0.5

            def OnDragExit(self, dragSource, dragData):
                self.opacity = 1.0

        dragCont = DragContainer(parent=parent, name='dragCont', align=uiconst.TOLEFT, width=100, bgColor=eveColor.MATTE_BLACK)
        Label(parent=dragCont, text='DRAG', align=uiconst.CENTER, shadowOffset=(0, 0))
        dropCont = DropContainer(parent=parent, name='dropCont', align=uiconst.TORIGHT, width=100, bgColor=eveColor.SMOKE_BLUE)
        Label(parent=dropCont, text='DROP', align=uiconst.CENTER, shadowOffset=(0, 0))
