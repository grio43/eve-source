#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\selection\transitselectionlist.py
import carbonui.const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.uianimations import animations
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from projectdiscovery.client.projects.exoplanets.selection.transitselection import TransitSelection
from projectdiscovery.client.projects.exoplanets.ui.colorfilterbutton import ColorFilterButton
import localization

class TransitMarkerList(Container):
    __notifyevents__ = ['OnTaskLoaded', 'OnProjectDiscoveryRescaled', 'OnSolutionSubmit']

    def ApplyAttributes(self, attributes):
        super(TransitMarkerList, self).ApplyAttributes(attributes)
        self._active_delete_button = None
        self._transit_selection_tool = attributes.get('transitSelectionTool')
        self._transit_selection_tool.on_selection_change.connect(self.update)
        self._elements = []
        self._current_selections = []
        self.setup_layout()
        self._scrollContainer.OnMouseEnter = self.OnMouseEnter
        self._scrollContainer.OnMouseExit = self.OnMouseExit
        sm.RegisterNotify(self)

    def setup_layout(self):
        self._scrollContainer = ScrollContainer(name='ScrollContainer', parent=self, align=uiconst.TOALL)
        self._auto_size_container = ContainerAutoSize(name='AutoSizeContainer', parent=self._scrollContainer, align=uiconst.CENTER, width=self.width - 5)

    def OnProjectDiscoveryRescaled(self, *args, **kwargs):
        self._fix_auto_size_position()

    def _fix_auto_size_position(self):
        if self._auto_size_container.displayHeight > self.displayHeight:
            self._auto_size_container.top = max(self._auto_size_container.displayHeight - self.displayHeight - 40, 16)
        else:
            self._auto_size_container.top = 0

    def _add_element(self, selection):
        element = TransitMarkerListElement(name='TransitMarkerListElement_%s' % len(self._elements), parent=self._auto_size_container, align=uiconst.TOTOP, height=24, transitMarker=selection, hideFunc=self._hide_toggle_func, deleteFunc=self._transit_selection_tool.remove_selection, opacity=0)
        self._elements.append(element)
        animations.FadeIn(element)

    def update(self, *args, **kwargs):
        self._current_selections = self._transit_selection_tool.get_confirmed_selections()
        self._remove_deleted_elements()
        self._add_missing_elements()
        self._fix_auto_size_position()

    def _remove_deleted_elements(self):
        for element in self._elements:
            if element.get_marker() not in self._current_selections:
                element.Close()
                self._elements.remove(element)

    def _add_missing_elements(self):
        selections_in_elements = [ element.get_marker() for element in self._elements ]
        missing_selections = [ selection for selection in self._current_selections if selection not in selections_in_elements ]
        for selection in missing_selections:
            self._add_element(selection)

    def _hide_toggle_func(self, selection):
        self._transit_selection_tool.hide_selection(selection, not selection.is_hidden())

    def Close(self):
        self._transit_selection_tool.on_selection_change.disconnect(self.update)
        super(TransitMarkerList, self).Close()

    def OnTaskLoaded(self, *args, **kwargs):
        self._auto_size_container.Flush()


class TransitMarkerListElement(Container):
    __notifyevents__ = ['OnSolutionSubmit', 'OnProjectDiscoveryDeleteHide']

    def ApplyAttributes(self, attributes):
        super(TransitMarkerListElement, self).ApplyAttributes(attributes)
        self._transit_marker = attributes.get('transitMarker')
        self._hide_func = attributes.get('hideFunc')
        self._delete_func = attributes.get('deleteFunc')
        self.setup_layout()
        sm.RegisterNotify(self)

    def setup_layout(self):
        epoch = self._transit_marker.get_epoch()
        epoch = 0 if epoch is None else epoch
        epoch = round(epoch, 3)
        period = self._transit_marker.get_period_length()
        self._parent_container = ContainerAutoSize(parent=self, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        self._parent_container.OnClick = self._on_parent_container_click
        self._toggle_container = Container(name='ToggleContainer', parent=self._parent_container, align=uiconst.TOLEFT, width=16)
        self._button = ColorFilterButton(name='ExoPlanetsToggleButton', parent=self._toggle_container, align=uiconst.CENTER, width=16, height=16, color=self._transit_marker.get_color(), args=self._transit_marker, func=lambda marker: self._hide_func(marker) or self._on_hide())
        SetTooltipHeaderAndDescription(targetObject=self._button, headerText='', descriptionText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/VisibilityToggleTooltip'))
        self._epoch_container = ContainerAutoSize(name='EpochContainer', parent=self._parent_container, align=uiconst.TOLEFT, padLeft=5, padRight=5)
        self._epoch = Label(name='EpochLabel', parent=self._epoch_container, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/EpochInfo', epoch=epoch))
        self._orbital_period_container = ContainerAutoSize(name='OrbitalPeriodContainer', parent=self._parent_container, align=uiconst.TOLEFT, padLeft=5, padRight=5)
        self._orbital_period = Label(name='OrbitalPeriodLabel', parent=self._orbital_period_container, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/PeriodListing', period=round(period, 3) if period else localization.GetByLabel('UI/ProjectDiscovery/exoplanets/NotApplicable')))
        self._delete_button = ButtonIcon(name='DeleteButton', parent=Container(parent=self._parent_container, align=uiconst.TOLEFT, width=24, height=24), align=uiconst.TOLEFT, iconSize=32, width=32, height=32, texturePath='res:/UI/Texture/icons/105_32_12.png', iconColor=(1, 0, 0, 1), args=self._transit_marker, func=self._delete_func)
        SetTooltipHeaderAndDescription(targetObject=self._delete_button, headerText='', descriptionText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/DeleteButtonTooltip'))

    def get_marker(self):
        return self._transit_marker

    def OnSolutionSubmit(self):
        self._delete_button.SetState(uiconst.UI_HIDDEN)

    def OnProjectDiscoveryDeleteHide(self):
        self._delete_button.SetState(uiconst.UI_HIDDEN)

    def _on_hide(self):
        self._orbital_period.opacity = 0.3 if not self._button.toggled else 1
        self._epoch.opacity = 0.3 if not self._button.toggled else 1

    @property
    def delete_button(self):
        return self._delete_button

    def _on_parent_container_click(self, *args):
        self._button.OnClick()
