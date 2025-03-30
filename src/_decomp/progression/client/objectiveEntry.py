#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\client\objectiveEntry.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveHeaderLarge, EveLabelSmall
from localization import GetByLabel
from locks import Lock
from progression.client.roomInfoContainer import RoomInfoContainer
from progression.client.widgets.countergreaterthanwidget import CounterGreaterThanWidget
from progression.client.widgets.counterwidget import CounterWidget
from progression.client.widgets.healthwidgets import HealthWidget
from progression.client.widgets.killcounterwidget import KillCounterWidget
from progression.client.widgets.textwidget import TextWidget
from progression.client.widgets.timerwidget import TimerWidget
from progression.client.const import load_icon_grouping_texture, BACKGROUND_COLOR_GRAY, COLOR_GREEN, get_icon_grouping_color
from progression.common.objectives import ObjectiveType, load_objective
from progression.common.tasks import load_task
from progression.common.widgets import load_widget, TaskWidgetType
import blue

class ObjectiveEntry(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(ObjectiveEntry, self).ApplyAttributes(attributes)
        self.progressionSvc = sm.GetService('progressionSvc')
        self.objectiveData = self.progressionSvc.GetObjectiveData()
        self.roomInfoContainer = None
        self.objectiveTitle = None
        self.animationLock = Lock(name='ObjectiveEntryAnimationLock')
        self.objectiveTitleCont = ContainerAutoSize(name='objectiveTitle', parent=self, align=uiconst.TOTOP, bgColor=BACKGROUND_COLOR_GRAY, height=0)
        self.widgetsCont = ContainerAutoSize(name='widgetsCont', parent=self, align=uiconst.TOTOP, padTop=4, state=uiconst.UI_NORMAL)
        animations.MorphScalar(self.objectiveTitleCont, 'height', startVal=0, endVal=28, duration=0.4, callback=self.ConstructTitle)

    def ConstructTitle(self):
        current_room_id = self.progressionSvc.GetCurrentRoomID()
        objectiveStatic = load_objective(self.objectiveData.objective_id)
        if current_room_id not in objectiveStatic.room_ids:
            text = GetByLabel('UI/Progression/GoToNextRoomTitle')
        else:
            text = self.objectiveData.title
        if self.objectiveTitle is None:
            self.objectiveTitle = EveHeaderLarge(parent=self.objectiveTitleCont, align=uiconst.TOTOP, text=text, padding=(5, 5, 5, 5))
            PlaySound('messaging_system_pick_play')
        else:
            self.objectiveTitle.SetText(text)
        animations.BlinkIn(self.objectiveTitle, loops=2, duration=0.2, curveType=uiconst.ANIM_LINEAR, callback=self.ConstructWidgets)

    def ConstructWidgets(self):
        with self.animationLock:
            self._DoConstructWidgets()

    def _DoConstructWidgets(self):
        self.widgetsCont.Flush()
        objectiveStatic = load_objective(self.objectiveData.objective_id)
        current_room_id = self.progressionSvc.GetCurrentRoomID()
        if current_room_id not in objectiveStatic.room_ids:
            if self.roomInfoContainer:
                self.roomInfoContainer.Close()
            self.roomInfoContainer = RoomInfoContainer(name='RoomInfoContainer', parent=self, align=uiconst.TOTOP, connecting_gate_ids=objectiveStatic.connecting_gate_ids, state=uiconst.UI_NORMAL, height=30)
            return
        if self.objectiveData.description:
            self.objectiveDescription = EveLabelSmall(name='objectiveDescription', parent=self.widgetsCont, align=uiconst.TOTOP, text=self.objectiveData.description, padding=(18, 4, 0, 0))
        widgetCont = ContainerAutoSize(name='widgetCont', parent=self.widgetsCont, align=uiconst.TOTOP, padLeft=4, state=uiconst.UI_NORMAL)
        widgetBuffsCont = ContainerAutoSize(name='widgetBuffsCont', parent=self.widgetsCont, align=uiconst.TOTOP, padTop=8, padLeft=4, state=uiconst.UI_NORMAL)
        counter = 0
        for task_widget_data in self.objectiveData.task_widgets:
            if task_widget_data is None:
                continue
            widget_state = self.progressionSvc.get_widget_state(task_widget_data.task_id, task_widget_data.task_widget_id)
            task_widget_static = load_widget(task_widget_data.task_widget_id)
            task_widget_type_id = task_widget_static.task_widget_type_id
            task_widget_icon_grouping_id = task_widget_static.icon_grouping_id
            texturePath = load_icon_grouping_texture(task_widget_icon_grouping_id)
            textureColor = get_icon_grouping_color(task_widget_icon_grouping_id)
            if task_widget_icon_grouping_id < 2:
                parent = widgetCont
            else:
                parent = widgetBuffsCont
            singleWidgetCont = ContainerAutoSize(name='singleWidgetCont', parent=parent, align=uiconst.TOTOP, height=18, mode=uiconst.UI_NORMAL)
            iconCont = Container(parent=singleWidgetCont, align=uiconst.TOLEFT, width=13, height=16, padTop=4)
            if texturePath:
                Sprite(name='iconGrouping', parent=iconCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=6, height=6, top=4, texturePath=texturePath, color=textureColor)
            if task_widget_type_id == TaskWidgetType.TASK_WIDGET_TYPE_TEXT:
                TextWidget(name='textWidget', parent=singleWidgetCont, align=uiconst.TOLEFT, static_data=task_widget_static, padTop=4, width=250, height=100, state=uiconst.UI_NORMAL)
            elif task_widget_type_id in (TaskWidgetType.TASK_WIDGET_TYPE_NPC_KILL_COUNTER, TaskWidgetType.TASK_WIDGET_TYPE_REACTIVE_SPAWNER_POINTS_KILLED):
                KillCounterWidget(name='npcKillCounterWidget', parent=singleWidgetCont, align=uiconst.TOLEFT, widget_state=widget_state, static_data=task_widget_static, padTop=4, padBottom=-4, width=250, height=20, state=uiconst.UI_NORMAL)
            elif task_widget_type_id in (TaskWidgetType.TASK_WIDGET_TYPE_OBJECT_HEALTH_BAR, TaskWidgetType.TASK_WIDGET_TYPE_ENTITY_HEALTH_BAR, TaskWidgetType.TASK_WIDGET_TYPE_REACTIVE_SPAWNER_ENTITY_HEALTH_BAR):
                HealthWidget(name='HealthWidget', parent=singleWidgetCont, align=uiconst.TOLEFT, widget_state=widget_state, static_data=task_widget_static, padTop=4, state=uiconst.UI_NORMAL)
            elif task_widget_type_id == TaskWidgetType.TASK_WIDGET_TYPE_DUNGEON_TIMER:
                TimerWidget(name='TimerWidget', parent=singleWidgetCont, align=uiconst.TOLEFT, widget_state=widget_state, static_data=task_widget_static, width=250, height=100, padTop=4, state=uiconst.UI_NORMAL)
            elif task_widget_type_id == TaskWidgetType.TASK_WIDGET_TYPE_DUNGEON_COUNTER:
                CounterWidget(name='CounterWidget', parent=singleWidgetCont, align=uiconst.TOLEFT, widget_state=widget_state, static_data=task_widget_static, padTop=4, width=250, height=20, state=uiconst.UI_NORMAL)
            elif task_widget_type_id == TaskWidgetType.TASK_WIDGET_TYPE_DUNGEON_COUNTER_GREATER_THAN:
                CounterGreaterThanWidget(name='CounterGreaterThanWidget', parent=singleWidgetCont, align=uiconst.TOLEFT, widget_state=widget_state, static_data=task_widget_static, padTop=4, width=250, height=20, state=uiconst.UI_NORMAL)
            else:
                raise RuntimeError('Unknown task widget type', task_widget_type_id)
            if objectiveStatic.objective_type_id == ObjectiveType.OBJECTIVE_TYPE_CHOICE and counter == 0:
                EveLabelSmall(name='orWidget', parent=parent, align=uiconst.TOTOP, text=GetByLabel('UI/Progression/ChoiceObjectiveSeparator'), padding=(100, 8, 0, 0))
            counter += 1

    def UpdateWidgets(self):
        self.ConstructWidgets()

    def UpdateWidgetsOnRoomJoined(self):
        if self.roomInfoContainer:
            self.widgetsCont.state = uiconst.UI_HIDDEN
            self.roomInfoContainer.Close()
            PlaySound('messaging_system_confirm_play')
            temp = Container(parent=self, align=uiconst.TOTOP, height=30)
            TaskCompletion(name='TaskCompletion', parent=temp, text=GetByLabel('UI/Progression/JumpCompletionLabel'))
            self.objectiveData = self.progressionSvc.GetObjectiveData()
            blue.synchro.SleepWallclock(2000)
            temp.Close()
            self.roomInfoContainer = None
            self.ConstructTitle()
            animations.BlinkIn(self.objectiveTitle, loops=2, duration=0.2, curveType=uiconst.ANIM_LINEAR, callback=self.ConstructWidgetsDelayed)
        self.UpdateWidgets()

    def ConstructWidgetsDelayed(self):
        PlaySound('messaging_system_data_long_play')
        self.ConstructWidgets()
        if self.roomInfoContainer is None:
            self.widgetsCont.state = uiconst.UI_NORMAL

    def CompleteObjective(self, lastTaskCompleted):
        self.widgetsCont.state = uiconst.UI_HIDDEN
        self.objectiveData = self.progressionSvc.GetObjectiveData()
        current_room_id = self.progressionSvc.GetCurrentRoomID()
        objectiveRooms = self.GetCurrentObjectiveRooms()
        previousObjectiveRooms = self.GetPreviousObjectiveRooms()
        completionRooms = objectiveRooms + previousObjectiveRooms
        if current_room_id in completionRooms:
            if self.roomInfoContainer:
                self.roomInfoContainer.Close()
            self.ShowHideCompletion(lastTaskCompleted)
        self.ConstructTitle()
        animations.BlinkIn(self.objectiveTitle, loops=2, duration=0.2, curveType=uiconst.ANIM_LINEAR, callback=self.ConstructWidgetsDelayed)

    def GetCurrentObjectiveRooms(self):
        objectiveStatic = load_objective(self.objectiveData.objective_id)
        objectiveRooms = objectiveStatic.room_ids
        return objectiveRooms

    def GetPreviousObjectiveRooms(self):
        progressionHistory = self.progressionSvc.GetProgressionHistory()
        if len(progressionHistory) < 2:
            return []
        previousObjective = progressionHistory[-2]
        previousObjectiveStatic = load_objective(previousObjective.objective_id)
        previousObjectiveRooms = previousObjectiveStatic.room_ids
        return previousObjectiveRooms

    def ShowHideCompletion(self, lastTaskCompleted):
        with self.animationLock:
            task = load_task(lastTaskCompleted)
            text = task.completion_text
            PlaySound('messaging_system_confirm_play')
            temp = Container(parent=self, align=uiconst.TOTOP, height=30)
            TaskCompletion(name='TaskCompletion', parent=temp, text=text)
            blue.synchro.SleepWallclock(2000)
            temp.Close()


class TaskCompletion(Container):

    def ApplyAttributes(self, attributes):
        super(TaskCompletion, self).ApplyAttributes(attributes)
        self.text = attributes.text
        checkmarkCont = Transform(parent=self, align=uiconst.TOLEFT, width=26, height=18, scalingCenter=(0.5, 0.5), padTop=4)
        Sprite(name='CheckMark', parent=checkmarkCont, state=uiconst.UI_DISABLED, width=26, height=18, texturePath='res:/UI/Texture/Classes/DungeonMessaging/CheckMark2x.png', color=COLOR_GREEN)
        animations.MorphVector2(checkmarkCont, 'scale', startVal=checkmarkCont.scale, endVal=(0.5, 0.5), duration=0.4)
        EveLabelMedium(parent=self, align=uiconst.TOLEFT, text=self.text, color=COLOR_GREEN, padTop=6)
