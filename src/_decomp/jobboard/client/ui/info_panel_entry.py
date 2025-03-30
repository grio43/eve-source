#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\info_panel_entry.py
import carbonui
from carbonui.button.menu import MenuButtonIcon
import eveui
import eveformat
import localization
from objectives.client.ui.objective_chain import ObjectiveChainEntry
from carbonui.control.buttonIcon import ButtonIcon
from jobboard.client import get_job_board_service
from eve.client.script.ui import eveColor, eveThemeColor
HEADER_BG_COLOR = (0,
 0,
 0,
 0.35)

class JobInfoPanelEntry(eveui.ContainerAutoSize):
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top
    default_clipChildren = True

    def __init__(self, job, on_click, *args, **kwargs):
        kwargs.setdefault('name', job.job_id)
        super(JobInfoPanelEntry, self).__init__(*args, **kwargs)
        self.job = job
        self._on_click = on_click
        self._expanded = False
        self._is_hovered = False
        self._objective_chain_entry = None
        self._options_icon_container = None
        self._layout()
        self.update_state(animate=False)
        self._update_hover_state()
        self._register()
        self._on_job_updated()

    def Close(self):
        self._unregister()
        if self._objective_chain_entry:
            self._objective_chain_entry.Close()
            self._objective_chain_entry = None
        super(JobInfoPanelEntry, self).Close()
        self._on_click = None
        self.callback = None
        self.job = None

    def _register(self):
        self.job.on_job_updated.connect(self.__on_job_updated)

    def _unregister(self):
        self.job.on_job_updated.disconnect(self.__on_job_updated)

    @eveui.skip_if_destroyed
    def __on_job_updated(self):
        if self.job:
            self._on_job_updated()

    def _on_job_updated(self):
        text = self._progress_text
        if text:
            self._progress_label.text = text
            eveui.animate(self._progress_fill, 'width', end_value=self._progress_percentage, duration=1)
            self._update_progress_color()

    @property
    def _current_progress(self):
        return getattr(self.job, 'current_progress', 0)

    @property
    def _target_progress(self):
        return getattr(self.job, 'target_progress', 0)

    @property
    def _progress_percentage(self):
        target = self._target_progress
        if not target:
            return 0
        return float(self._current_progress) / target

    @property
    def _has_progress(self):
        return bool(self._target_progress)

    @property
    def _progress_text(self):
        target_progress = self._target_progress
        if not target_progress:
            return ''
        elif target_progress >= 100:
            return u'{value}%'.format(value=int(self._progress_percentage * 100))
        else:
            return u'{}/{}'.format(eveformat.number(self._current_progress, 0), eveformat.number(self._target_progress, 0))

    def _layout(self):
        self._construct_header()
        self._content_container = eveui.ContainerAutoSize(name='content_container', parent=self, align=eveui.Align.to_top, alignMode=eveui.Align.to_top)

    def _construct_header(self):
        self._header_container = header_container = eveui.ContainerAutoSize(name='header_container', parent=self, state=eveui.State.normal, align=eveui.Align.to_top, alignMode=eveui.Align.to_top_no_push, bgColor=HEADER_BG_COLOR)
        header_container.OnClick = self.OnClick
        header_container.GetMenu = self.GetMenu
        header_container.GetDragData = self.GetDragData
        header_container.OnDragEnter = self.OnDragEnter
        header_container.PrepareDrag = self.PrepareDrag
        header_container.OnEndDrag = self.OnEndDrag
        header_container.isDragObject = True
        header_container.isDropLocation = True
        self._state_info_line = StateInfoLine(parent=header_container)
        wrapper = eveui.ContainerAutoSize(parent=header_container, align=eveui.Align.to_top_no_push, alignMode=eveui.Align.to_top, padding=8)
        icon_container = eveui.ContainerAutoSize(parent=wrapper, align=eveui.Align.to_left, padRight=8, width=16)
        feature_tag = self.job.feature_tag
        view_details_button = ButtonIcon(name='view_details_button', parent=icon_container, align=eveui.Align.center, texturePath=feature_tag.icon, iconSize=16, width=16, height=16, color=carbonui.TextColor.NORMAL, func=self._open_job, hint=localization.GetByLabel('UI/Opportunities/ViewOpportunity'))
        view_details_button.isDragObject = True
        view_details_button.GetDragData = self.job.get_drag_data
        if bool(self.job.has_menu):
            self._options_icon_container = eveui.ContainerAutoSize(parent=wrapper, align=eveui.Align.to_right, padLeft=8, width=16, display=False)
            MenuButtonIcon(name='options_menu_button', parent=self._options_icon_container, align=eveui.Align.center, get_menu_func=self.GetMenu, width=16, hint='')
        progress_text_container = eveui.ContainerAutoSize(parent=wrapper, state=eveui.State.disabled, align=eveui.Align.to_right, clipChildren=True)
        self._progress_label = eveui.EveLabelLarge(parent=progress_text_container, align=eveui.Align.center_right, text=self._progress_text, maxLines=1, padLeft=4)
        title_container = eveui.ContainerAutoSize(parent=wrapper, state=eveui.State.disabled, align=eveui.Align.to_top, clipChildren=True)
        self._title = eveui.EveLabelLarge(parent=title_container, align=eveui.Align.to_top, text=self.job.title, maxLines=1, showEllipsis=True, color=carbonui.TextColor.HIGHLIGHT)
        progress_fill_container = eveui.Container(name='progress_fill_container', parent=header_container, align=eveui.Align.to_all, clipChildren=True, opacity=0.15)
        self._progress_fill = eveui.StretchSpriteHorizontal(parent=progress_fill_container, align=eveui.Align.to_left_prop, texturePath='res:/UI/Texture/classes/InfoPanels/progress_bar_solid.png', color=self._get_progress_color(), leftEdgeSize=2, rightEdgeSize=10, padLeft=-2, padRight=-10, width=self._progress_percentage)

    @eveui.skip_if_destroyed
    def _construct_body(self):
        if self._objective_chain_entry:
            self._objective_chain_entry.Close()
            self._objective_chain_entry = None
        objective_chain = self.job.objective_chain
        if objective_chain:
            self._objective_chain_entry = ObjectiveChainEntry(parent=self._content_container, objective_chain=objective_chain)

    def _reconstruct_body(self):
        self._content_container.Flush()
        self._construct_body()

    def expand(self):
        if self._expanded:
            return
        self._expanded = True
        self._reconstruct_body()
        self._update_hover_state()

    def collapse(self):
        if not self._expanded:
            return
        self._expanded = False
        self._content_container.Flush()
        self._update_hover_state()

    def OnClick(self):
        if self._expanded:
            eveui.Sound.collapse.play()
        else:
            eveui.Sound.expand.play()
        self._on_click(self.job.job_id)

    def GetMenu(self):
        return self.job.get_menu()

    def GetDragData(self):
        self._header_container.bgFill.rgb = eveColor.FOCUS_BLUE[:3]
        return [JobReorderDragData(self)]

    def PrepareDrag(self, dragContainer, dragSource):
        super(JobInfoPanelEntry, self).PrepareDrag(dragContainer, dragSource)
        return (16, 8)

    def OnDragEnter(self, dragSource, dragData):
        data = dragData[0]
        if not isinstance(data, JobReorderDragData) or data.entry == self:
            return
        dragged_job = data.entry.job
        drag_timestamp = dragged_job.get_tracked_timestamp()
        my_timestamp = self.job.get_tracked_timestamp()
        if drag_timestamp > my_timestamp:
            drag_timestamp = my_timestamp - 1
        else:
            drag_timestamp = my_timestamp + 1
        dragged_job.set_tracked_timestamp(drag_timestamp)
        data.entry.SetOrder(self.GetOrder())

    def OnEndDrag(self, *args):
        self._header_container.bgFill.color = HEADER_BG_COLOR

    def OnMouseEnter(self, *args):
        super(JobInfoPanelEntry, self).OnMouseEnter(*args)
        self._is_hovered = True
        self._update_hover_state()

    def OnMouseExit(self, *args):
        super(JobInfoPanelEntry, self).OnMouseEnter(*args)
        self._is_hovered = False
        self._update_hover_state()

    def _update_hover_state(self):
        has_progress = self._has_progress
        self._progress_fill.display = has_progress and not self._expanded
        self._progress_label.display = has_progress and not self._expanded and not self._is_hovered
        if self._expanded or self._is_hovered:
            eveui.fade(self._header_container.bgFill, end_value=0.5, duration=0.2)
            if self._options_icon_container:
                self._options_icon_container.Show()
        else:
            eveui.fade(self._header_container.bgFill, end_value=HEADER_BG_COLOR[3], duration=0.2)
            if self._options_icon_container:
                self._options_icon_container.Hide()

    def _open_job(self):
        get_job_board_service().open_job(self.job.job_id)

    @eveui.skip_if_destroyed
    def update_state(self, animate = True):
        if not self.job:
            return
        if self._expanded and self._objective_chain_entry and self._objective_chain_entry.objective_chain != self.job.objective_chain:
            self.collapse()
            if not self.job.is_removed:
                self.expand()
        self._update_state_info_line(animate=animate)

    def _update_state_info_line(self, animate = True, *args, **kwargs):
        state_info = self.job.get_state_info()
        if not state_info:
            self._state_info_line.Hide()
        else:
            if animate and self._state_info_line.color == state_info['color']:
                animate = False
            self._state_info_line.color = state_info['color']
            self._state_info_line.Show(animate=animate)

    def _get_progress_color(self):
        if self._progress_percentage < 1:
            return eveThemeColor.THEME_FOCUS
        else:
            return eveColor.SUCCESS_GREEN

    def _update_progress_color(self):
        self._progress_fill.color = self._get_progress_color()

    def OnColorThemeChanged(self):
        super(JobInfoPanelEntry, self).OnColorThemeChanged()
        self._update_progress_color()


class StateInfoLine(eveui.Line):
    default_state = eveui.State.hidden
    default_align = eveui.Align.to_left_no_push
    default_outputMode = carbonui.uiconst.OUTPUT_COLOR_AND_GLOW
    default_color = carbonui.TextColor.SUCCESS
    default_opacity = 0.75

    def Close(self):
        eveui.stop_all_animations(self)
        super(StateInfoLine, self).Close()

    def Show(self, animate = False, *args):
        super(StateInfoLine, self).Show(*args)
        if animate:
            eveui.animate(self, 'opacity', duration=1.5, end_value=self.default_opacity * 2, loops=3, curve_type=eveui.CurveType.wave)

    def Hide(self, *args):
        super(StateInfoLine, self).Hide(*args)
        eveui.stop_all_animations(self)
        self.opacity = self.default_opacity


class JobReorderDragData(object):

    def __init__(self, entry):
        self.entry = entry

    def LoadIcon(self, icon, dad, iconSize):
        import eveicon
        icon.LoadIcon(eveicon.caret_up_down)
        icon.width = icon.height = 16
