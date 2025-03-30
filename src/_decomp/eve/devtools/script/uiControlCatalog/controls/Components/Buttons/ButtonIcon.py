#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\Buttons\ButtonIcon.py
import eveicon
from carbonui import AxisAlignment, uiconst
from carbonui.primitives.flowcontainer import FlowContainer
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):

    def sample_code(self, parent):
        from carbonui.control.buttonIcon import ButtonIcon
        flow = FlowContainer(parent=parent, align=uiconst.TOPLEFT, width=200, contentSpacing=(4, 4), contentAlignment=AxisAlignment.CENTER)
        ButtonIcon(parent=flow, align=uiconst.NOALIGN, width=24, height=24, iconSize=16, texturePath=eveicon.navigate_back, func=lambda : ShowQuickMessage('Going back'))
        ButtonIcon(parent=flow, align=uiconst.NOALIGN, width=24, height=24, iconSize=16, texturePath=eveicon.navigate_forward, func=lambda : ShowQuickMessage('Going forward'))
        ButtonIcon(parent=flow, align=uiconst.NOALIGN, width=24, height=24, iconSize=16, texturePath=eveicon.close, func=lambda : ShowQuickMessage('Getting out of here'), enabled=False, hint="There's no escape from this place")
