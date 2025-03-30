#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\controls\incursionStateCont.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control.eveLabel import EveHeaderMedium
from eve.client.script.ui.shared.incursions.incursionConst import INACTIVE_STATE, INCURSION_STATES, COLOR_BY_INCURSION_STATE, NAME_BY_INCURSION_STATE

class IncursionStateCont(Container):
    default_height = 8

    def ApplyAttributes(self, attributes):
        super(IncursionStateCont, self).ApplyAttributes(attributes)
        self.activeState = attributes.activeState
        self.indicators = []
        self.ConstructLayout()

    def ConstructLayout(self):
        statesContainer = ContainerAutoSize(name='statesContainer', parent=self, align=uiconst.TOPLEFT, height=self.height)
        for i, state in enumerate(INCURSION_STATES):
            isActive = state == self.activeState
            self.indicators.append(IncursionStateIndicator(parent=statesContainer, align=uiconst.TOLEFT, width=17, padRight=3, indicatorState=state, active=isActive, state=uiconst.UI_NORMAL, hint=NAME_BY_INCURSION_STATE[state]))

        EveHeaderMedium(parent=self, align=uiconst.CENTERLEFT, text=NAME_BY_INCURSION_STATE[self.activeState], color=COLOR_BY_INCURSION_STATE[self.activeState], left=65)


class IncursionStateIndicator(Fill):

    def ApplyAttributes(self, attributes):
        super(IncursionStateIndicator, self).ApplyAttributes(attributes)
        self.indicatorState = attributes.indicatorState
        if attributes.active:
            self.Enable()
        else:
            self.Disable()

    def Enable(self, *args):
        self.SetRGBA(*COLOR_BY_INCURSION_STATE[self.indicatorState])

    def Disable(self, *args):
        self.SetRGBA(*COLOR_BY_INCURSION_STATE[INACTIVE_STATE])
