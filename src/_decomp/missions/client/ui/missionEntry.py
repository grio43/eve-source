#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\missions\client\ui\missionEntry.py
import carbonui.const as uiconst
from carbonui import TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.utilMenu import UtilMenu
from missions.client.ui.missionObjectiveEntry import MissionObjectiveEntry
from objectives.client.ui.objective_chain import ObjectiveChainEntry
from jobboard.client.ui.info_panel_entry import StateInfoLine
import eveicon
HELP_ICON_SIZE = 16

class MissionEntry(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        self.missionIndex = attributes.missionIndex
        self.mission = attributes.mission
        self.objectives = attributes.objectives
        self.objectiveChain = getattr(self.mission, 'objectiveChain', None)
        self.HasOptionsMenu = attributes.HasOptionsMenu
        self.GetOptionsMenu = attributes.GetOptionsMenu
        self.UpdateExpandedStateForMission = attributes.UpdateExpandedStateForMission
        self.isCollapsable = attributes.get('isCollapsable', True)
        self.missionObjectivesContainer = None
        self.missionObjectiveContainers = {}
        self.objectiveIndexShown = None
        super(MissionEntry, self).ApplyAttributes(attributes)
        self._ConstructHeader()

    def _ConstructHeader(self):
        missionHeaderContainer = ContainerAutoSize(name='mission_containerHeader_%s' % self.mission.GetID(), parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_NORMAL, bgColor=(0, 0, 0, 0.45))
        self._ConstructMissionStateLine(parent=missionHeaderContainer)
        wrapperContainer = ContainerAutoSize(parent=missionHeaderContainer, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=8)
        if self.isCollapsable:
            missionHeaderContainer.OnClick = lambda : self.UpdateExpandedStateForMission(self.missionIndex)
        missionHeaderContainer.GetMenu = self.GetMenu
        missionHeaderContainer.hint = self.mission.hint
        self._AddOptionsMenu(parent=wrapperContainer)
        self._AddTitle(parent=wrapperContainer)

    def _ConstructMissionStateLine(self, parent):
        stateColor = self.mission.GetStateColor()
        if not stateColor:
            return
        StateInfoLine(parent=parent, color=stateColor)

    def _AddTitle(self, parent):
        titleContainer = ContainerAutoSize(name='titleContainer', parent=parent, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, clipChildren=True)
        EveLabelLarge(name='missionHeader_title_%s' % self.mission.GetID(), parent=titleContainer, align=uiconst.TOTOP, maxLines=1, showEllipsis=True, color=TextColor.HIGHLIGHT, text=self.mission.title)

    def _AddOptionsMenu(self, parent):
        if not self.HasOptionsMenu():
            return
        optionsMenuIconContainer = Container(name='missionHeader_containerIconOptionsMenu_%s' % self.mission.GetID(), parent=parent, align=uiconst.TORIGHT, state=uiconst.UI_PICKCHILDREN, width=HELP_ICON_SIZE, padLeft=4)
        UtilMenu(name='missionHeader_iconOptionsMenu_%s' % self.mission.GetID(), parent=optionsMenuIconContainer, align=uiconst.CENTER, menuAlign=uiconst.BOTTOMLEFT, GetUtilMenu=(self.GetOptionsMenu, self.mission), texturePath=eveicon.more_vertical, width=HELP_ICON_SIZE, height=HELP_ICON_SIZE, iconSize=HELP_ICON_SIZE, bgOpacityExpandedIcon=0.0, opacityExpandedLines=0.0)

    def _AddObjectives(self):
        self.missionObjectiveContainers = {}
        self.missionObjectivesContainer = ContainerAutoSize(name='mission_containerObjectives_%s' % self.mission.GetID(), parent=self, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, width=self.width, clipChildren=True)
        if self.objectiveChain:
            ObjectiveChainEntry(parent=self.missionObjectivesContainer, objective_chain=self.objectiveChain)
        else:
            objectiveIndex = 0
            for objectiveIndex, objective in enumerate(self.objectives):
                objectiveContainer = MissionObjectiveEntry(name='missionObjective_container_%d_%s' % (objectiveIndex, self.mission.GetID()), parent=self.missionObjectivesContainer, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, width=self.width, top=4, mission=self.mission, objectiveIndex=objectiveIndex, objective=objective, OnObjectiveClicked=self.OnObjectiveClicked)
                self.missionObjectiveContainers[objectiveIndex] = objectiveContainer

            self.objectiveIndexShown = objectiveIndex
            self.UpdateExpandedStatesForObjectives()

    def ShowObjectives(self):
        if not self.missionObjectivesContainer or self.missionObjectivesContainer.destroyed:
            self._AddObjectives()

    def HideObjectives(self):
        if self.missionObjectivesContainer and not self.missionObjectivesContainer.destroyed:
            self.missionObjectivesContainer.Close()

    def OnObjectiveClicked(self, objectiveIndex):
        if objectiveIndex in self.missionObjectiveContainers:
            container = self.missionObjectiveContainers[objectiveIndex]
            if container.IsExpanded():
                self.objectiveIndexShown = None
            else:
                self.objectiveIndexShown = objectiveIndex
        self.UpdateExpandedStatesForObjectives()

    def UpdateExpandedStatesForObjectives(self):
        for index, container in self.missionObjectiveContainers.items():
            if self.objectiveIndexShown is not None and index == self.objectiveIndexShown:
                container.Expand()
            else:
                if not self.isCollapsable:
                    return
                container.Collapse()

    def GetMenu(self):
        return self.mission.GetContextMenu()
