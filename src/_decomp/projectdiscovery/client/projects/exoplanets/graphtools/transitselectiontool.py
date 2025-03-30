#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphtools\transitselectiontool.py
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import Label
from projectdiscovery.client.projects.exoplanets.exoplanetsmultiplicationcontrols import ExoPlanetsMultiplicationControls
from projectdiscovery.client.projects.exoplanets.exoplanetsutil import markers
from projectdiscovery.client.projects.exoplanets.selection.transitselection import TransitSelection
from projectdiscovery.client.projects.exoplanets.graphtools.basetool import BaseTool
from signals import Signal
from carbonui.uicore import uicore
from carbonui.uianimations import animations
import carbonui.const as uiconst
import trinity
import localization

class TransitSelectionTool(BaseTool):
    __notifyevents__ = ['OnDataLoaded', 'OnTransitMarkingWithPeriod']
    _scroll_reset_time = 0.5
    _scroll_period_delta = 1e-07
    _scroll_start_multiplier = 1
    _mouse_move_period_delta = 0.001
    _mouse_down_to_period_edit_threshold = 0.15

    def __init__(self, *args, **kwargs):
        super(TransitSelectionTool, self).__init__(*args, **kwargs)
        self._data = []
        self.on_phantom_selection_change = Signal(signalName='on_phantom_selection_change')
        self.on_selection_change = Signal(signalName='on_selection_change')
        self.on_period_edit = Signal(signalName='on_period_edit')
        self.on_fold_edit_start = Signal(signalName='on_fold_edit_start')
        self.on_fold_edit_stopped = Signal(signalName='on_fold_edit_stopped')
        self._transit_selections = []
        self._confirmed_selections = []
        self._color_pallet = markers.MARKER_COLORS
        self._patterns = markers.MARKER_PATTERNS
        self._max_number_of_selections = len(self._color_pallet)
        self._phantom_selection = TransitSelection(0, None, [], self._color_pallet[0], self._patterns[0])
        self._current_selection = None
        self._is_mouse_down = False
        self._is_editing_period = False
        self._is_disabled = False
        self._is_canceling = False
        self._mouse_down_origin = None
        self._prev_horizontal_value = None
        self._is_moved = False
        self._is_scrolling = False
        self._tooltip = None
        self._minimum_period = markers.MINIMUM_PERIOD
        self._maximum_period = None
        self._last_scroll_time = trinity.device.animationTime
        self._scroll_multiplier = self._scroll_start_multiplier
        self._mouse_down_time = 0
        self._tooltip = self.get_tool_tip_object()
        self.create_new_selection()
        sm.RegisterNotify(self)

    def OnDataLoaded(self, data):
        time_values = zip(*data)[0]
        self._maximum_period = max(time_values) - min(time_values)
        self._data = data
        self.reset_tool()

    def reset_tool(self):
        self._is_editing_period = False
        self._transit_selections = []
        self._confirmed_selections = []
        self._phantom_selection = TransitSelection(0, None, self._data, self._color_pallet[0], self._patterns[0])
        self.create_new_selection()

    def on_mouse_move(self, horizontal_mouse_value, vertical_mouse_value):
        if self._is_disabled:
            return
        if self._is_folded:
            self._on_folded_mouse_move(horizontal_mouse_value, vertical_mouse_value)
        else:
            self._on_unfolded_mouse_move(horizontal_mouse_value, vertical_mouse_value)

    def _on_folded_mouse_move(self, horizontal_mouse_value, vertical_mouse_value):
        if self._is_mouse_down and self._is_moved:
            added = -self._mouse_move_period_delta if horizontal_mouse_value < self._prev_horizontal_value else self._mouse_move_period_delta
            new_period = max(self._minimum_period, min(self._maximum_period, self._current_selection.get_period_length() + added))
            self.set_orbital_period_of_current_selection(new_period)
            self._prev_horizontal_value = horizontal_mouse_value
            self._tooltip.update('')
        elif not self._is_moved:
            self._is_moved = False
            value = horizontal_mouse_value - self._current_selection.get_center()
            self.set_epoch_tooltip(value)
        self._tooltip.update_info(self._current_selection)

    def _on_unfolded_mouse_move(self, horizontal_mouse_value, vertical_mouse_value):
        current_time_value = horizontal_mouse_value
        if not self._is_editing_period:
            self._phantom_selection.set_center(current_time_value, False)
            self.on_phantom_selection_change()
            self.set_epoch_tooltip(self._phantom_selection.get_epoch())
            return
        self._current_selection.set_period_end_value(current_time_value)
        self.set_orbital_period_tooltip(self._current_selection.get_period_length())
        self.set_orbital_period_of_current_selection(self._current_selection.get_period_length())

    def on_mouse_down(self, horizontal_mouse_value, vertical_mouse_value):
        if self._is_disabled:
            return
        if self._is_folded:
            self._on_folded_mouse_down(horizontal_mouse_value, vertical_mouse_value)
        else:
            self._on_unfolded_mouse_down(horizontal_mouse_value, vertical_mouse_value)
        self._is_mouse_down = True

    def _on_folded_mouse_down(self, horizontal_mouse_value, vertical_mouse_value):
        self._is_moved = False
        self._mouse_down_origin = horizontal_mouse_value
        self._prev_horizontal_value = horizontal_mouse_value
        self._mouse_down_time = trinity.device.animationTime

    def _on_unfolded_mouse_down(self, horizontal_mouse_value, vertical_mouse_value):
        if uicore.uilib.rightbtn:
            if self._is_editing_period:
                self._is_editing_period = False
                self.remove_selection(self._current_selection)
                self._is_canceling = True
                sm.ScatterEvent('OnTransitMarkingCancelled')
            else:
                self._is_canceling = True
                self.remove_selection(self._current_selection)
                sm.ScatterEvent('OnTransitMarkingCancelledAfterSettingPeriod')
            sm.ScatterEvent('OnProjectDiscoveryMarkerDim', self.get_selections_with_phantom_selections())
        elif not self._is_editing_period and self._current_selection.get_period_length():
            self.remove_selection(self._current_selection)
            sm.ScatterEvent('OnTransitMarkingCancelledAfterSettingPeriod')
            sm.ScatterEvent('OnProjectDiscoveryMarkerDim', self.get_selections_with_phantom_selections())

    def on_mouse_up(self, horizontal_mouse_value, vertical_mouse_value):
        if self._is_disabled:
            return
        if self._is_folded:
            self._on_folded_mouse_up(horizontal_mouse_value, vertical_mouse_value)
        else:
            self._on_unfolded_mouse_up(horizontal_mouse_value, vertical_mouse_value)
        self._is_mouse_down = False

    def _on_folded_mouse_up(self, horizontal_mouse_value, vertical_mouse_value):
        current_time_value = horizontal_mouse_value
        if not self._is_moved and self._is_mouse_down:
            self._current_selection.set_center(current_time_value)
            sm.ScatterEvent('OnTransitMarkingInFoldedMode')
            self.on_selection_change()
        self._is_moved = False
        uicore.uilib.SetCursor(uiconst.UICURSOR_DEFAULT)
        self.on_fold_edit_stopped()
        self._tooltip.update_info(self._current_selection)

    def _on_unfolded_mouse_up(self, horizontal_mouse_value, vertical_mouse_value):
        if self._is_canceling:
            self._is_canceling = False
            return
        self._is_editing_period = not self._is_editing_period
        current_time_value = horizontal_mouse_value
        if not self._is_editing_period:
            marking_event = 'OnTransitMarkingWithPeriod' if self._current_selection.get_period_length() else 'OnTransitMarkingWithoutPeriod'
            sm.ScatterEvent(marking_event)
            if marking_event == 'OnTransitMarkingWithoutPeriod':
                sm.ScatterEvent('OnProjectDiscoveryMarkerDim', self.get_selections())
        elif self._is_editing_period:
            sm.ScatterEvent('OnProjectDiscoveryMarkerDim', [self.get_current_selection()])
            if self._current_selection and self._current_selection not in self._transit_selections:
                self._transit_selections.append(self._current_selection)
            self._current_selection.set_center(current_time_value)
            self.set_orbital_period_tooltip(self._current_selection.get_period_length())
            self.on_selection_change()

    def on_mouse_exit(self, *args, **kwargs):
        self._tooltip.update('')
        if self._is_folded:
            self._on_folded_mouse_exit()
        else:
            self._on_unfolded_mouse_exit()

    def _on_unfolded_mouse_exit(self):
        if not self._current_selection:
            return
        if self._is_editing_period:
            self._current_selection.set_period_end_value(None)
            self.on_selection_change()
        else:
            self.on_phantom_selection_change(False)

    def _on_folded_mouse_exit(self):
        if self._is_moved:
            uicore.uilib.SetCursor(uiconst.UICURSOR_DEFAULT)
            self._is_moved = False
            self._is_mouse_down = False
            self.on_fold_edit_stopped()
            self._tooltip.update_info(self._current_selection)

    def on_scroll(self, scroll_amount):
        if self._current_selection.get_period_length() and not self._is_editing_period:
            current_time = trinity.device.animationTime
            if current_time > self._last_scroll_time + self._scroll_reset_time:
                self._scroll_multiplier = self._scroll_start_multiplier
            else:
                self._scroll_multiplier += 1
            self._last_scroll_time = current_time
            added = self._scroll_multiplier * self._scroll_period_delta * scroll_amount
            new_period = max(self._minimum_period, min(self._maximum_period, self._current_selection.get_period_length() + added))
            self.set_orbital_period_of_current_selection(new_period)
            self.on_period_edit()
            self._tooltip.update_info(self._current_selection)

    def on_mouse_hover(self, horizontal_mouse_value, vertical_mouse_value):
        if self._is_folded and self._is_mouse_down:
            if trinity.device.animationTime > self._mouse_down_time + self._mouse_down_to_period_edit_threshold:
                if not self._is_moved:
                    self.on_fold_edit_start()
                self._is_moved = True
                uicore.uilib.SetCursor(uiconst.UICURSOR_LEFT_RIGHT_DRAG)
            else:
                self._is_moved = False
                uicore.uilib.SetCursor(uiconst.UICURSOR_DEFAULT)

    def get_unhidden_selections(self):
        return [ selection for selection in self._transit_selections if not selection.is_hidden() ]

    def get_selections(self):
        return self._transit_selections

    def get_selections_with_phantom_selections(self):
        return self.get_unhidden_selections() + [self._phantom_selection]

    def get_phantom_selection(self):
        return self._phantom_selection

    def get_number_of_selections(self):
        return len(self._transit_selections)

    def get_max_number_of_selections(self):
        return self._max_number_of_selections

    def get_current_selection(self):
        return self._current_selection

    def create_new_selection(self):
        if self.is_full():
            self.set_disabled(True)
            return
        self._is_disabled = False
        self._current_selection = TransitSelection(0, None, self._data, self._get_unused_color(), self._get_unused_pattern())
        self._phantom_selection.set_period_length(None)
        self._phantom_selection.set_color(self._current_selection.get_color())
        self._phantom_selection.pattern_path = self._current_selection.pattern_path
        if self._tooltip:
            self._tooltip.show_info(False, transit_selection=self._current_selection)
        self.on_selection_change()

    def remove_selection(self, selection):
        if self.is_selection_known_to_tool(selection):
            was_full = self.is_full()
            self._transit_selections.remove(selection)
            if selection in self._confirmed_selections:
                self._confirmed_selections.remove(selection)
            if not self._is_editing_period and self._current_selection not in self._transit_selections or was_full and self._current_selection in self._confirmed_selections:
                self.create_new_selection()
            else:
                self.on_selection_change()

    def remove_all_selections(self):
        if self._transit_selections or self._confirmed_selections:
            self._transit_selections = []
            self._confirmed_selections = []
            self._current_selection = None
            self.create_new_selection()

    def hide_selection(self, selection, is_hidden):
        if selection in self._transit_selections:
            selection.set_hidden(is_hidden)
            self.on_selection_change()

    def is_selection_known_to_tool(self, selection):
        return selection in self._transit_selections

    def _get_unused_color(self):
        used_colors = [ selection.get_color() for selection in self._transit_selections ]
        return [ color for color in self._color_pallet if color not in used_colors ][0]

    def _get_unused_pattern(self):
        used_patterns = [ selection.pattern_path for selection in self._transit_selections ]
        return [ pattern for pattern in self._patterns if pattern not in used_patterns ][0]

    def set_disabled(self, is_disabled):
        if not is_disabled and self.is_full():
            is_disabled = True
        self._tooltip.update('')
        self._is_disabled = is_disabled

    def confirm_current_selection(self):
        if self._current_selection and self._current_selection not in self._confirmed_selections:
            self._confirmed_selections.append(self._current_selection)
            self.create_new_selection()
            confirm_event = 'OnTransitMarkingConfirmedInFoldedMode' if self._is_folded else 'OnTransitMarkingConfirmed'
            sm.ScatterEvent(confirm_event)
            sm.ScatterEvent('OnTransitConfirmed')
        self.on_selection_change()

    def is_full(self):
        return len(self._transit_selections) == self._max_number_of_selections

    def get_confirmed_selections(self):
        return self._confirmed_selections

    def _construct_tooltip(self):
        self._tooltip = TransitSelectionTooltip(name='TransitSelectionTooltip', padLeft=10, transitSelectionTool=self, maximumPeriod=self._maximum_period)

    def get_tool_tip_object(self):
        if not self._tooltip or self._tooltip.destroyed:
            self._construct_tooltip()
        return self._tooltip

    def set_epoch_tooltip(self, epoch):
        self._tooltip.update('%s' % round(epoch, 4))

    def set_orbital_period_tooltip(self, period):
        if period:
            self._tooltip.update(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/OrbitalPeriodTooltip', numberofdays=round(period, 4)))
        else:
            self._tooltip.update(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/UnknownOrbitalPeriodTooltip'))

    def set_orbital_period_of_current_selection(self, orbital_period):
        self._current_selection.set_period_length(orbital_period)
        if self._is_folded:
            self._phantom_selection.set_period_length(orbital_period)
        else:
            self._phantom_selection.set_period_length(None)
        self._tooltip.update_info(self._current_selection)
        self.on_selection_change()
        self.on_period_edit()

    def OnTransitMarkingWithPeriod(self):
        if self._tooltip:
            self._tooltip.show_info(True, transit_selection=self._current_selection)
        self._phantom_selection.set_period_length(None)

    def is_confirmed_selection(self, selection):
        return selection in self._confirmed_selections

    def on_tool_set(self):
        if self._is_folded or self._current_selection.get_period_length() and not self._is_editing_period:
            self._tooltip.show_info(transit_selection=self._current_selection)

    def on_tool_unset(self):
        self.on_selection_change()
        self.on_mouse_exit()


class TransitSelectionTooltip(Container):

    def ApplyAttributes(self, attributes):
        super(TransitSelectionTooltip, self).ApplyAttributes(attributes)
        self._multiplier_controls = None
        self._transit_selection_tool = attributes.get('transitSelectionTool')
        self._is_left = False
        self._is_show_info = False
        self._max_period = attributes.get('maximumPeriod', None)
        self._setup_layout()

    def _setup_layout(self):
        self._info_container = ContainerAutoSize(name='ExoPlanetsInfoContainer', parent=self, align=uiconst.TOPRIGHT, width=200, bgColor=(0, 0, 0, 0.5), opacity=0)
        self._epoch_label = Label(name='Epoch', parent=self._info_container, align=uiconst.TOTOP, text='Epoch: 2.074', padLeft=10, padRight=10, padTop=10)
        self._orbital_period_container = ContainerAutoSize(name='OrbitalPeriodContainer', parent=self._info_container, align=uiconst.TOTOP, height=40)
        self._orbital_period_label = Label(name='OrbitalPeriod', parent=self._orbital_period_container, align=uiconst.TOTOP, text='Orbital Period: 2.074 days', padLeft=10, padRight=10)
        self._multiplier_controls = ExoPlanetsMultiplicationControls(parent=self._orbital_period_container, align=uiconst.TOTOP, transitSelectionTool=self._transit_selection_tool, maximumPeriod=self._max_period, padRight=5, height=20, padLeft=10)
        self._tooltip_label = Label(name='TooltipLabel', parent=self, align=uiconst.BOTTOMLEFT)

    def show_info(self, is_show = True, transit_selection = None):
        if is_show and not self._is_show_info:
            self._info_container.SetState(uiconst.UI_PICKCHILDREN)
            animations.BlinkIn(self._info_container)
        elif self._is_show_info:
            self._info_container.SetState(uiconst.UI_DISABLED)
            animations.BlinkOut(self._info_container)
        self._is_show_info = is_show
        self.update_info(transit_selection)

    def update_info(self, transit_selection):
        if isinstance(transit_selection, TransitSelection):
            unknown_label = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/UnknownValue')
            epoch = round(transit_selection.get_epoch(), 4) if transit_selection.get_epoch() else unknown_label
            period = round(transit_selection.get_period_length(), 4) if transit_selection.get_period_length() else unknown_label
            self._epoch_label.SetText(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/EpochInfo', epoch=epoch))
            self._orbital_period_label.SetText(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/PeriodInfo', period=period))
            if self._multiplier_controls:
                self._multiplier_controls.update_state()

    def update(self, text):

        def set_text():
            self._tooltip_label.text = text

        if not self._tooltip_label.text and text:
            animations.BlinkIn(self._tooltip_label)
        if not text and self._tooltip_label.text:
            animations.BlinkOut(self._tooltip_label, callback=set_text)
        else:
            set_text()
        self._update_position()

    def _update_position(self):
        if not self.parent:
            return
        dpi = uicore.dpiScaling
        mouse_x, mouse_y = uicore.uilib.x, uicore.uilib.y
        parent_left, parent_top = self.parent.GetAbsolutePosition()
        self._tooltip_label.left = mouse_x - parent_left
        is_collision = self._tooltip_label.left * dpi + self._tooltip_label.displayWidth + self.padLeft * dpi > self.parent.displayWidth
        if is_collision:
            if not self._is_left:
                self._is_left = True
                animations.BlinkIn(self._tooltip_label)
            self._tooltip_label.left -= self._tooltip_label.displayWidth + self.padLeft * 2 * dpi
        else:
            if self._is_left:
                animations.BlinkIn(self._tooltip_label)
            self._is_left = False
