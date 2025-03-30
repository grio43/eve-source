#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\objectivesview.py
from agentinteraction.constUI import HEADER_SIZE_MEDIUM
from agentinteraction.objectivesteps import ObjectiveSteps
import carbonui
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from evemissions.client.objectives import TalkToAgentObjective, CargoObjective, PickUpObjective, DropOffObjective, DungeonObjective
from localization import GetByLabel
GENERAL_OBJECTIVES = [TalkToAgentObjective,
 CargoObjective,
 PickUpObjective,
 DropOffObjective]
EXTRA_OBJECTIVES = [DungeonObjective]
PADDING_BETWEEN_OBJECTIVE_SETS = 24

class ObjectivesView(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        self.general_objectives = None
        self.extra_objectives = None
        super(ObjectivesView, self).ApplyAttributes(attributes)
        self._build_title()
        self._build_objectives_subcontainer()

    def update_objectives(self, objectives, objective_type):
        self._build_objectives_subcontainer(should_clear=True)
        general_objectives = [ objective for objective in objectives if type(objective) in GENERAL_OBJECTIVES ]
        extra_objectives = [ objective for objective in objectives if type(objective) in EXTRA_OBJECTIVES ]
        self.general_objectives.update_objective_steps(general_objectives, objective_type)
        self.extra_objectives.update_objective_steps(extra_objectives, objective_type)
        if general_objectives and extra_objectives:
            self.general_objectives.padBottom = PADDING_BETWEEN_OBJECTIVE_SETS
        else:
            self.general_objectives.padBottom = 0
        if general_objectives:
            self.general_objectives.Show()
        else:
            self.general_objectives.Hide()
        if extra_objectives:
            self.extra_objectives.Show()
        else:
            self.extra_objectives.Hide()
        if not general_objectives and not extra_objectives:
            self.Hide()

    def _clear_container(self, container):
        if isinstance(container, Container) and not getattr(container, 'destroyed', False):
            container.Close()

    def _build_title(self):
        carbonui.TextHeader(name='title', parent=self, align=uiconst.TOTOP, text=GetByLabel('UI/Agents/StandardMission/Objectives'), color=carbonui.TextColor.HIGHLIGHT, padBottom=9)

    def _build_objectives_subcontainer(self, should_clear = False):
        if should_clear:
            self._clear_container(container=self.subcontainer_objectives)
        self.subcontainer_objectives = ContainerAutoSize(name='subcontainer_objectives', parent=self, align=uiconst.TOTOP)
        self.general_objectives = ObjectiveSteps(name='general_objectives', parent=self.subcontainer_objectives, align=uiconst.TOTOP)
        self.extra_objectives = ObjectiveSteps(name='extra_objectives', parent=self.subcontainer_objectives, align=uiconst.TOTOP)
