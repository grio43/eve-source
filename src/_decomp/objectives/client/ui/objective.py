#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\ui\objective.py
import eveui
import eveicon
from carbonui import uiconst, TextColor
from eve.client.script.ui.control.infoIcon import MoreInfoIcon

class ObjectiveEntry(eveui.ContainerAutoSize):
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top
    default_state = eveui.State.normal
    default_bgColor = (0, 0, 0, 0.25)

    def __init__(self, objective, *args, **kwargs):
        kwargs.setdefault('name', 'objective_{}'.format(objective.objective_id))
        super(ObjectiveEntry, self).__init__(*args, **kwargs)
        self.objective = objective
        self._task_containers = {}
        self._task_widgets = {}
        self._task_button_widgets = {}
        self._layout()
        self._tasks_changed()
        self._state_changed(objective_id=self.objective.objective_id)
        self._register()

    def Close(self):
        self._unregister()
        super(ObjectiveEntry, self).Close()
        self.objective = None

    def _register(self):
        if self.objective:
            self.objective.on_tasks_changed.connect(self._tasks_changed)
            self.objective.on_state_changed.connect(self._state_changed)

    def _unregister(self):
        if self.objective:
            self.objective.on_tasks_changed.disconnect(self._tasks_changed)
            self.objective.on_state_changed.disconnect(self._state_changed)

    def close(self):
        self._unregister()
        if self.state == eveui.State.normal:
            self.state = eveui.State.disabled
        if self.opacity < 1 or self.state == eveui.State.hidden:
            self.Close()
        else:
            eveui.fade_out(self, duration=1, on_complete=self.Close)

    @eveui.skip_if_destroyed
    def _tasks_changed(self, **kwargs):
        if not self.objective:
            return
        tasks = self.objective.get_visible_tasks()
        current_tasks = set(self._task_widgets.keys())
        current_tasks.update(self._task_button_widgets.keys())
        for task in tasks:
            task_id = task.task_id
            if task_id in current_tasks:
                current_tasks.remove(task_id)
            else:
                task_widget = task.construct_widget(align=eveui.Align.to_top)
                if task_widget:
                    task_widget.SetParent(self._task_containers[task_id])
                    self._task_widgets[task_id] = task_widget
                button_widget = task.construct_button_widget(align=eveui.Align.to_top, padTop=4)
                if button_widget:
                    self._task_button_widgets[task_id] = button_widget
                    button_widget.SetParent(self._buttons_container)

        for task_id in current_tasks:
            if task_id in self._task_widgets:
                self._task_widgets[task_id].close()
                del self._task_widgets[task_id]
            if task_id in self._task_button_widgets:
                self._task_button_widgets[task_id].close()
                del self._task_button_widgets[task_id]

    @eveui.skip_if_destroyed
    def _state_changed(self, reason = None, **kwargs):
        if not self.objective:
            return
        if self.objective.completed:
            self._completed_line.Show(bool(reason == 'on_complete'))
        else:
            self._completed_line.Hide()
        if self.objective.hidden:
            self.state = eveui.State.hidden
        else:
            self.state = eveui.State.normal

    def _layout(self):
        container = eveui.ContainerAutoSize(name='wrapper', parent=self, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padding=(8, 4, 8, 4))
        header_container = eveui.ContainerAutoSize(name='header', parent=container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padding=(0, 4, 0, 4))
        self._completed_line = CompletedLine(parent=header_container, left=-8)
        if self.objective.tooltip:
            tooltip_container = eveui.ContainerAutoSize(name='tooltip_container', parent=header_container, align=eveui.Align.to_right, padLeft=4)
            tooltip_icon = MoreInfoIcon(parent=tooltip_container, align=eveui.Align.center_right, hint=self.objective.tooltip, texturePath=eveicon.info, color=TextColor.NORMAL)
            tooltip_icon.tooltipPointer = uiconst.POINT_LEFT_2
        eveui.EveLabelLarge(name='title', parent=header_container, align=eveui.Align.to_top, text=self.objective.title, maxLines=2)
        if not self.objective.title:
            header_container.display = False
        if self.objective.description:
            eveui.EveLabelMedium(name='description', parent=container, align=eveui.Align.to_top, text=self.objective.description, padding=(0, 4, 0, 4))
        self._task_container = eveui.ContainerAutoSize(name='task_container', parent=container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padding=(0, 4, 0, 4))
        for task in self.objective.get_all_tasks():
            task_id = task.task_id
            self._task_containers[task_id] = eveui.ContainerAutoSize(name='task_container_{}'.format(task_id), parent=self._task_container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top)

        self._buttons_container = eveui.ContainerAutoSize(name='buttons_container', parent=self._task_container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top)

    def GetMenu(self):
        from objectives.client.qa_tools import get_objective_context_menu
        return get_objective_context_menu(self.objective)


class CompletedLine(eveui.Line):
    default_align = eveui.Align.to_left_no_push
    default_outputMode = uiconst.OUTPUT_COLOR_AND_GLOW
    default_color = TextColor.SUCCESS
    default_opacity = 0.75

    def Show(self, animate = False, *args):
        super(CompletedLine, self).Show(*args)
        if animate:
            eveui.animate(self, 'opacity', duration=1.5, end_value=self.default_opacity * 2, loops=3, curve_type=eveui.CurveType.wave)

    def Hide(self, *args):
        super(CompletedLine, self).Hide(*args)
        eveui.stop_all_animations(self)
        self.opacity = self.default_opacity
