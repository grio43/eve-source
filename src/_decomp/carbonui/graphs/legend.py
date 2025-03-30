#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\legend.py
import carbonui.fontconst
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import Label

class Legend(FlowContainer):
    default_name = 'Legend'

    def ApplyAttributes(self, attributes):
        FlowContainer.ApplyAttributes(self, attributes)

    def AddItem(self, item, text):
        container = ContainerAutoSize(parent=self, align=uiconst.NOALIGN, padding=(10, 0, 0, 5), height=14)
        item.height = 10
        item.width = 10
        item.align = uiconst.TOLEFT
        item.padding = (1, 1, 2, 3)
        item.SetParent(container)
        Label(parent=container, align=uiconst.TOLEFT, text=text, color=(1.0, 1.0, 1.0, 0.5), fontsize=carbonui.fontconst.EVE_SMALL_FONTSIZE)
