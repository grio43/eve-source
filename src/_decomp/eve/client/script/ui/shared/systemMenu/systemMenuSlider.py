#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\systemMenuSlider.py
from carbonui import uiconst
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.shared.systemMenu import systemMenuConst
from localization import GetByLabel

class SystemMenuSlider(ContainerAutoSize):
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_padding = (0, 4, 0, 8)
    default_alignMode = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        callback = attributes.pop('callback', None)
        super(SystemMenuSlider, self).ApplyAttributes(attributes)
        label = attributes.pop('label')
        labelWidth = attributes.pop('labelWidth', 120)
        attributes.pop('parent')
        labelParent = Container(name='labelparent', parent=self, align=uiconst.TOLEFT, width=systemMenuConst.LABEL_WIDTH)
        eveLabel.EveLabelSmall(text=GetByLabel(label), parent=labelParent, state=uiconst.UI_PICKCHILDREN, align=uiconst.VERTICALLY_CENTERED, lineSpacing=-0.1)
        Slider(parent=self, callback=callback, mouseWheelEnabled=False, **attributes)
