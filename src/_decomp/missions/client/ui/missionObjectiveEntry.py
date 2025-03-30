#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\missions\client\ui\missionObjectiveEntry.py
import carbonui.const as uiconst
from carbonui import ButtonFrameType, Density, TextColor
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.shared.infoPanels.const.infoPanelUIConst import PANELWIDTH, LEFTPAD, RIGHTPAD
from eve.client.script.ui.util.uix import GetTextHeight
from eve.client.script.ui.control.statefulButton import StatefulButton
ENTRY_WIDTH = PANELWIDTH - LEFTPAD - RIGHTPAD - 12
OBJECTIVE_HEADER_HEIGHT = 20
OBJECTIVE_ICON_OPACITY = 0.7
OBJECTIVE_DIVIDER_CONTAINER_HEIGHT = 2
OBJECTIVE_DIVIDER_WIDTH = 250
OBJECTIVE_DIVIDER_HEIGHT = 1
OBJECTIVE_DIVIDER_OPACITY = 0.4
OBJECTIVE_DIVIDER_WEIGHT = 1
OBJECTIVE_LOCATION_HEIGHT = 36
OBJECTIVE_GUIDANCE_CALL_HEIGHT = 25
PADDING_ICON_TO_TITLE = 4
PADDING_OBJECTIVE_TEXT = 8
PADDING_OBJECTIVE_TO_OBJECTIVE = 2
DEFAULT_PADDING = 6

class MissionObjectiveEntry(ContainerAutoSize):
    default_bgColor = (0, 0, 0, 0.25)

    def ApplyAttributes(self, attributes):
        self.mission = attributes.mission
        self.objectiveIndex = attributes.objectiveIndex
        self.objective = attributes.objective
        OnObjectiveClicked = attributes.OnObjectiveClicked
        super(MissionObjectiveEntry, self).ApplyAttributes(attributes)
        self.isExpanded = False
        self.objectiveContentContainer = None
        self.objectiveButton = None
        self.objectiveLocationContainer = None
        self.wrapper = ContainerAutoSize(name='wrapper', parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=8)
        self._ConstructHeader(OnObjectiveClicked)

    def _GetObjectiveSizes(self):
        hasObjectiveIcon = self.objective.HasIcon()
        objectiveIconSize = self.objective.GetObjectiveIconSize()
        objectiveTextWidth = ENTRY_WIDTH - 2 * PADDING_ICON_TO_TITLE
        objectiveTextLeft = PADDING_ICON_TO_TITLE
        if hasObjectiveIcon:
            objectiveTextWidth -= objectiveIconSize
        objectiveTextHeight = GetTextHeight(strng=self.objective.GetText(), width=objectiveTextWidth, fontsize=EVE_MEDIUM_FONTSIZE) + PADDING_OBJECTIVE_TEXT
        objectiveHeight = max(objectiveIconSize, objectiveTextHeight) if hasObjectiveIcon else objectiveTextHeight
        return (objectiveHeight, objectiveTextWidth, objectiveTextLeft)

    def _ConstructHeader(self, callback):
        objectiveHeaderContainer = ContainerAutoSize(name='missionObjectiveHeader_container_%d_%s' % (self.objectiveIndex, self.mission.GetID()), parent=self.wrapper, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        objectiveHeaderContainer.OnClick = lambda : callback(self.objectiveIndex)
        if not self.objective.IsActive():
            Line(parent=objectiveHeaderContainer, align=uiconst.TOLEFT_NOPUSH, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, color=TextColor.SUCCESS, opacity=0.75, left=-8)
        objectiveHeaderText = self.objective.GetHeaderText() or self.mission.title
        EveLabelLarge(name='missionObjectiveHeader_title_%s' % self.mission.GetID(), parent=objectiveHeaderContainer, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, text=objectiveHeaderText)

    def _AddObjectiveContent(self):
        self.objectiveContentContainer = ContainerAutoSize(name='missionObjective_containerContent_%s' % self.mission.GetID(), parent=self.wrapper, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        if self.objective.HasText():
            objectiveHeight, objectiveTextWidth, objectiveTextLeft = self._GetObjectiveSizes()
            objectiveContainer = Container(name='missionObjective_subcontainer_%s' % self.mission.GetID(), parent=self.objectiveContentContainer, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, width=ENTRY_WIDTH, height=objectiveHeight)
            self._AddObjectiveIcon(parent=objectiveContainer, totalHeight=objectiveHeight)
            self._AddObjectiveText(parent=objectiveContainer, totalHeight=objectiveHeight, textWidth=objectiveTextWidth, leftPos=objectiveTextLeft)
        self._AddObjectiveLocation()

    def _AddObjectiveIcon(self, parent, totalHeight):
        if not self.objective.HasIcon():
            return
        objectiveIconSize = self.objective.GetObjectiveIconSize()
        objectiveIconContainer = Container(name='missionObjective_containerIcon_%s' % self.mission.GetID(), parent=parent, align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN, width=objectiveIconSize, height=totalHeight, left=2, top=2)
        self.objective.BuildIcon(name='missionObjective_icon_%s' % self.mission.GetID(), parent=objectiveIconContainer, align=uiconst.CENTER, state=uiconst.UI_NORMAL, opacity=OBJECTIVE_ICON_OPACITY, width=objectiveIconSize, height=objectiveIconSize)

    def _AddObjectiveText(self, parent, totalHeight, textWidth, leftPos):
        objectiveTitleContainer = Container(name='missionObjective_containerTitle_%s' % self.mission.GetID(), parent=parent, align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN, width=textWidth, height=totalHeight, left=DEFAULT_PADDING, padLeft=2)
        EveLabelMedium(name='missionObjective_title_%s' % self.mission.GetID(), parent=objectiveTitleContainer, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, text=self.objective.GetText(), width=textWidth, linkStyle=uiconst.LINKSTYLE_SUBTLE)

    def _AddObjectiveLocation(self):
        self.objectiveLocationContainer = ContainerAutoSize(name='missionObjective_containerLocation_%s' % self.mission.GetID(), parent=self.objectiveContentContainer, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        self.objectiveButton = StatefulButton(name=self.objective.GetLocationButtonName(), parent=self.objectiveLocationContainer, align=uiconst.TOTOP, controller=self.objective, state=uiconst.UI_HIDDEN, density=Density.COMPACT, frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT, padTop=4)

    def IsExpanded(self):
        return self.isExpanded

    def Expand(self):
        if self.isExpanded:
            return
        self.isExpanded = True
        if not self.objectiveContentContainer or self.objectiveContentContainer.destroyed:
            self._AddObjectiveContent()

    def Collapse(self):
        if not self.isExpanded:
            return
        self.isExpanded = False
        if self.objectiveContentContainer and not self.objectiveContentContainer.destroyed:
            self.objectiveContentContainer.Close()
