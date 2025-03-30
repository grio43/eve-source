#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\ui\objective_task_widget\base.py
from carbonui import uiconst, TextColor
import eveui
import eveicon
import uthread2
NORMAL_ICON_SIZE = 16
TYPE_ICON_SIZE = 24
TYPE_ICON_OPACITY = TextColor.HIGHLIGHT.opacity

class ObjectiveTaskWidget(eveui.ContainerAutoSize):
    default_name = 'ObjectiveWidget'
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top
    default_clipChildren = True
    default_opacity = 0

    def __init__(self, objective_task, *args, **kwargs):
        kwargs.setdefault('name', 'objective_task_{}'.format(objective_task.task_id))
        super(ObjectiveTaskWidget, self).__init__(*args, **kwargs)
        self._objective_task = objective_task
        self._layout()
        self._register()
        self._on_state_changed()
        self.update()

    @property
    def task_id(self):
        return self._objective_task.task_id

    def Close(self):
        self._unregister()
        if self._objective_task:
            self._objective_task.disable_highlight()
        super(ObjectiveTaskWidget, self).Close()
        self._objective_task = None

    def _register(self):
        if self._objective_task:
            self._objective_task.on_update.connect(self.update)
            self._objective_task.on_state_changed.connect(self._on_state_changed)

    def _unregister(self):
        if self._objective_task:
            self._objective_task.on_update.disconnect(self.update)
            self._objective_task.on_state_changed.disconnect(self._on_state_changed)

    def close(self):
        self._unregister()
        self.state = eveui.State.disabled
        if self.opacity < 1:
            self.Close()
        else:
            eveui.fade_out(self, duration=1)
            eveui.animate(self, 'padBottom', time_offset=0.5, duration=1, end_value=-self.GetAbsoluteSize()[1], on_complete=self.Close)

    def update(self, **kwargs):
        if not self._objective_task:
            return
        self._text_label.text = self._objective_task.title or ' '
        self._value_label.text = unicode(self._objective_task.value)
        self._update_icon()

    def hide(self):
        if not self.display:
            return
        if self.opacity == 0:
            self.padBottom = -self.GetAbsoluteSize()[1]
            self.Hide()
        else:
            eveui.fade_out(self, time_offset=0.5, duration=1)
            eveui.animate(self, 'padBottom', time_offset=1.5, duration=1, end_value=-self.GetAbsoluteSize()[1], on_complete=self.Hide)

    def show(self):
        eveui.fade_in(self, duration=0.5)
        eveui.animate(self, 'padBottom', duration=0, end_value=0)
        self.Show()

    def _on_state_changed(self, reason = None, **kwargs):
        if not self._objective_task:
            return
        self._update_icon(reason)
        if self._objective_task.hidden:
            self.hide()
        else:
            self.show()

    def _update_icon(self, reason = None):
        if self._objective_task.completed:
            self._icon_sprite.state = eveui.State.hidden
            self._checkmark.Show()
        else:
            self._checkmark.Hide()
            if self._objective_task.USE_TYPE_ICON and self._objective_task.type_id:
                sm.GetService('photo').GetIconByType(sprite=self._icon_sprite, typeID=self._objective_task.type_id, size=self._icon_sprite.width, isCopy=getattr(self._objective_task, 'is_blueprint_copy', False))
                self._icon_sprite.SetSize(TYPE_ICON_SIZE, TYPE_ICON_SIZE)
                self._icon_sprite.opacity = TYPE_ICON_OPACITY
                self._icon_sprite.state = eveui.State.disabled
            elif self._objective_task.icon:
                self._icon_sprite.SetSize(NORMAL_ICON_SIZE, NORMAL_ICON_SIZE)
                self._icon_sprite.color = self._objective_task.icon_color
                self._icon_sprite.texturePath = self._objective_task.icon
                self._icon_sprite.state = eveui.State.disabled
            else:
                self._icon_sprite.state = eveui.State.hidden

    def _layout(self):
        self._bg_frame = eveui.Container(parent=self, align=eveui.Align.to_all, bgColor=(1, 1, 1), opacity=0)
        self.content_container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padding=4)
        icon_container = eveui.Container(parent=self.content_container, align=eveui.Align.to_left, width=24, padRight=4)
        self._icon_sprite = eveui.Sprite(parent=icon_container, state=eveui.State.hidden, align=eveui.Align.center, height=NORMAL_ICON_SIZE, width=NORMAL_ICON_SIZE, color=self._objective_task.icon_color)
        self._checkmark = CompletedCheckmark(parent=icon_container, state=eveui.State.hidden, align=eveui.Align.center)
        self.main_container = eveui.ContainerAutoSize(parent=self.content_container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, height=16)
        value_container = eveui.ContainerAutoSize(parent=self.main_container, align=eveui.Align.to_right, padLeft=4)
        self._value_label = eveui.EveLabelMedium(parent=value_container, maxLines=1)
        self._text_label = eveui.EveLabelMedium(parent=self.main_container, align=eveui.Align.to_top, maxLines=1, showEllipsis=True)

    def OnMouseEnter(self, *args):
        eveui.fade(self._bg_frame, end_value=0.05, duration=0.1)
        self._objective_task.enable_highlight()

    def OnMouseExit(self, *args):
        eveui.fade(self._bg_frame, end_value=0, duration=0.2)
        self._objective_task.disable_highlight()

    def OnMouseDown(self, *args):
        uthread2.start_tasklet(self._objective_task.mouse_down, self)

    def OnClick(self, *args):
        uthread2.start_tasklet(self._objective_task.click)

    def OnDblClick(self, *args):
        uthread2.start_tasklet(self._objective_task.double_click)

    def GetMenu(self, *args):
        return self._objective_task.get_context_menu()

    def GetHint(self):
        return self._objective_task.tooltip


class ObjectiveTaskGroupWidget(eveui.ContainerAutoSize):
    default_name = 'ObjectiveTaskGroupWidget'
    default_state = eveui.State.pick_children
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top

    def __init__(self, objective_task, *args, **kwargs):
        super(ObjectiveTaskGroupWidget, self).__init__(*args, **kwargs)
        self._task_widgets = dict()
        self._objective_task = objective_task
        self._register()
        self._on_group_changed()

    def Close(self):
        self._unregister()
        super(ObjectiveTaskGroupWidget, self).Close()
        self._objective_task = None

    def _register(self):
        self._objective_task.on_group_changed.connect(self._on_group_changed)

    def _unregister(self):
        if self._objective_task:
            self._objective_task.on_group_changed.disconnect(self._on_group_changed)

    def _on_group_changed(self):
        task_ids = self._objective_task.get_task_ids()
        for task_id in self._task_widgets.keys():
            if task_id not in task_ids:
                task_widget = self._task_widgets.pop(task_id)
                task_widget.close()

        for task_id in task_ids:
            if task_id in self._task_widgets:
                continue
            widget = self._objective_task.construct_task_widget(task_id, align=eveui.Align.to_top)
            if widget:
                widget.SetParent(self)
                self._task_widgets[task_id] = widget

    def close(self):
        self._unregister()
        self.state = eveui.State.disabled
        if self.opacity < 1:
            self.Close()
        else:
            eveui.fade_out(self, duration=1, on_complete=self.Close)


class CompletedCheckmark(eveui.Container):
    default_width = 16
    default_height = 16
    default_opacity = 0.75

    def __init__(self, *args, **kwargs):
        super(CompletedCheckmark, self).__init__(*args, **kwargs)
        self._sprite = eveui.Sprite(parent=self, align=eveui.Align.center, width=16, height=16, texturePath=eveicon.checkmark, color=TextColor.SUCCESS, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3)

    def Show(self, animate = False, *args):
        super(CompletedCheckmark, self).Show(*args)
        if animate:
            eveui.animate(self._sprite, 'opacity', duration=1.5, end_value=1.5, loops=3, curve_type=eveui.CurveType.wave)

    def Hide(self, *args):
        super(CompletedCheckmark, self).Hide(*args)
        eveui.stop_all_animations(self._sprite)
        self._sprite.opacity = 1
