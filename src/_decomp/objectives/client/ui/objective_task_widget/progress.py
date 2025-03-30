#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\ui\objective_task_widget\progress.py
import random
import eveui
from eve.client.script.ui import eveColor, eveThemeColor
from carbonui import uiconst, TextColor
from .base import ObjectiveTaskWidget

class ProgressBarTaskWidget(ObjectiveTaskWidget):

    def __init__(self, *args, **kwargs):
        super(ProgressBarTaskWidget, self).__init__(*args, **kwargs)
        self.update()

    @property
    def progress(self):
        return self._objective_task.progress or 0

    @property
    def progress_bar_color(self):
        return getattr(self._objective_task, 'progress_bar_color', eveThemeColor.THEME_FOCUS)

    @property
    def progress_bar_color_completed(self):
        return getattr(self._objective_task, 'progress_bar_color_completed', TextColor.SUCCESS)

    def update(self, **kwargs):
        if not self._objective_task:
            return
        super(ProgressBarTaskWidget, self).update(**kwargs)
        eveui.animate(self._progress_fill, 'width', end_value=self.progress, duration=1)
        if getattr(self._objective_task, 'show_indeterminate_progress', False):
            self.show_indeterminate_progress()
        else:
            self.hide_indeterminate_progress()

    def _on_state_changed(self, **kwargs):
        if not self._objective_task:
            return
        super(ProgressBarTaskWidget, self)._on_state_changed(**kwargs)
        if self._objective_task.completed:
            self._progress_fill.color = self.progress_bar_color_completed
        else:
            self._progress_fill.color = self.progress_bar_color

    def show_indeterminate_progress(self):
        if self._indeterminate_container.display:
            return
        eveui.stop_all_animations(self._indeterminate_fill)
        self._animate_in()
        self._indeterminate_container.Show()
        self._progress_fill.Hide()

    def hide_indeterminate_progress(self):
        if not self._indeterminate_container.display:
            return
        eveui.stop_all_animations(self._indeterminate_fill)
        self._indeterminate_container.Hide()
        self._progress_fill.Show()

    def _layout(self):
        super(ProgressBarTaskWidget, self)._layout()
        progress_line_container = eveui.Container(parent=self.content_container, align=eveui.Align.to_top, height=4, top=2, clipChildren=True, opacity=TextColor.NORMAL.opacity)
        self._indeterminate_container = eveui.Container(parent=progress_line_container, align=eveui.Align.to_all, state=eveui.State.hidden)
        progress_bar_color = self.progress_bar_color
        self._indeterminate_fill = eveui.Line(parent=self._indeterminate_container, align=eveui.Align.to_all, weight=4, color=progress_bar_color)
        self._progress_fill = eveui.Line(parent=progress_line_container, align=eveui.Align.to_left_prop, weight=4, width=self.progress, color=progress_bar_color, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3)
        eveui.Line(parent=progress_line_container, align=eveui.Align.to_all, padTop=1, padBottom=1, color=(1, 1, 1), opacity=0.4)

    def _animate_in(self):
        width = self._indeterminate_container.GetAbsoluteSize()[0]
        self._indeterminate_fill.padRight = width
        self._indeterminate_fill.padLeft = 0
        if width:
            duration = random.uniform(0.8, 1.2)
        else:
            duration = 0.3
        eveui.animate(self._indeterminate_fill, 'padRight', start_value=width, end_value=0, on_complete=self._animate_out, duration=duration)

    def _animate_out(self):
        width = self._indeterminate_container.GetAbsoluteSize()[0]
        duration = random.uniform(0.8, 1.2)
        eveui.animate(self._indeterminate_fill, 'padLeft', start_value=0, end_value=width, on_complete=self._animate_in, duration=duration)

    def OnColorThemeChanged(self):
        super(ProgressBarTaskWidget, self).OnColorThemeChanged()
        progress_bar_color = self.progress_bar_color
        if self.progress < 1:
            self._progress_fill.color = progress_bar_color
        self._indeterminate_fill.color = progress_bar_color
