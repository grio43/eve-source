#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\browser\empireFactionToggleButtonGroup.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from eve.client.script.ui.control.toggleButtonGroupCircular import ToggleButtonGroupButtonCircular
BG_SIZE = 48

class EmpireFactionToggleButtonGroupButton(ToggleButtonGroupButtonCircular):

    def ApplyAttributes(self, attributes):
        super(EmpireFactionToggleButtonGroupButton, self).ApplyAttributes(attributes)
        leftCont = Container(name='leftCont', parent=self, align=uiconst.TOLEFT_PROP, width=0.5, padRight=BG_SIZE / 2)
        Line(name='leftLine', parent=leftCont, align=uiconst.TOPLEFT_PROP, pos=(0, 0.5, 0.999, 2), opacity=0.1)
        rightCont = Container(name='rightCont', parent=self, align=uiconst.TORIGHT_PROP, width=0.5, padLeft=BG_SIZE / 2)
        Line(name='leftLine', parent=rightCont, align=uiconst.TOPLEFT_PROP, pos=(0, 0.5, 0.999, 2), opacity=0.1)
