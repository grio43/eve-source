#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\tutorial\controllers\firsttutorialsample.py
from carbonui.uianimations import animations
from projectdiscovery.client.projects.exoplanets.tutorial.controllers.basecontroller import TutorialController
from projectdiscovery.client.projects.exoplanets.tutorial.tutorialdescriptioncontainer import TutorialDescriptionContainer
from uihighlighting.const import UiHighlightDirections
import localization
import uthread2

class FirstSampleTutorial(TutorialController):
    __notifyevents__ = TutorialController.__notifyevents__ + ['OnTransitConfirmed',
     'OnSolutionSubmit',
     'OnProjectDiscoveryZoom',
     'OnExoPlanetsColorToggle',
     'OnResultScreenShown',
     'OnProjectDiscoveryStartTutorial',
     'OnContinueToRewards',
     'OnProjectDiscoveryObjectHighlighted',
     'OnTransitMarkingWithPeriod',
     'OnProjectDiscoveryTutorialDisplayMessageClosed']
    __highlighted_names__ = ['ExoPlanetsGraph',
     'ExoPlanetsSubmitButton',
     'ExoPlanetsZoomSlider',
     'ExoPlanetsToggleButton',
     'HighlightSprite',
     'CategoryContainer',
     'ExoPlanetsTimeLabels',
     'ExoPlanetsFluxLabels',
     'ExoPlanetsSolarSystem']

    def __init__(self, *args, **kwargs):
        super(FirstSampleTutorial, self).__init__(*args, **kwargs)
        self._is_graph_tutorial_closed = False
        self._transit_message = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/DoubleClickMessage')
        self._is_transit_confirmed = False
        self._is_zoom_completed = False
        self._is_toggle_off_completed = False
        self._graph = None
        self._is_graph_disabled = False
        sm.RegisterNotify(self)
        uthread2.StartTasklet(self.start_tutorial)

    def start_tutorial(self):
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['ExoPlanetsGraph'])
        self._highlight_service.custom_highlight_ui_element_by_name(ui_element_name='ExoPlanetsGraph', default_direction=UiHighlightDirections.DOWN, offset=-80, highlight_content=TutorialDescriptionContainer(title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/GraphLabel'), description=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/TutorialGraphDescription'), buttonText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ButtonLabel'), width=400, height=110, buttonFunc=lambda args: self.explain_x_axis()))

    def explain_x_axis(self):
        self._clear_highlights()
        self._highlight_service.remove_highlight_from_ui_element_by_name('ExoPlanetsGraph')
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['ExoPlanetsGraph'])
        self._highlight_service.custom_highlight_ui_element_by_name(ui_element_name='ExoPlanetsTimeLabels', default_direction=UiHighlightDirections.UP, highlight_content=TutorialDescriptionContainer(title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/XAxisLabel'), description=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/XAxisDescription'), buttonText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ButtonLabel'), width=200, height=100, buttonFunc=lambda args: self.explain_y_axis()))

    def explain_y_axis(self):
        self._clear_highlights()
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['ExoPlanetsGraph'])
        self._highlight_service.custom_highlight_ui_element_by_name(ui_element_name='ExoPlanetsFluxLabels', default_direction=UiHighlightDirections.RIGHT, highlight_content=TutorialDescriptionContainer(title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/YAxisLabel'), description=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/YAxisDescription'), buttonText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ButtonLabel'), width=400, height=110, buttonFunc=lambda args: self.explain_secondary_classifications()))

    def explain_solar_system(self):
        self._clear_highlights()
        sm.ScatterEvent('OnProjectDiscoveryHideAllTutorialComponents')
        self._highlight_service.custom_highlight_ui_element_by_name(ui_element_name='ExoPlanetsSolarSystem', default_direction=UiHighlightDirections.UP, offset=-100, highlight_content=TutorialDescriptionContainer(title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/SolarSystemLabel'), description=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/SolarSystemDescription'), buttonText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ButtonLabel'), width=400, height=120, buttonFunc=lambda args: self.explain_submit()))

    def OnProjectDiscoveryObjectHighlighted(self, highlighted_object):
        if highlighted_object.name == 'ExoPlanetsGraph':
            if self._graph is None:
                sm.ScatterEvent('OnDisableTransitMarkings')
                highlighted_object.hide_mini_map_zoom()
            if self._is_graph_disabled:
                highlighted_object.Disable()
            self._graph = highlighted_object

    def OnTransitMarkingWithPeriod(self):
        self._highlight_service.remove_highlight_from_ui_element_by_name('HighlightSprite')
        sm.ScatterEvent('OnProjectDiscoveryTutorialDisplayMessage', message_text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/NoTransitsYet'), message_header_text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/TutorialWarningLabel'), label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/Name'), button_label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ButtonLabel'))
        sm.ScatterEvent('OnExoPlanetsControlsInitialize')
        sm.ScatterEvent('OnDiscardCurrentMarking')

    def OnProjectDiscoveryTutorialDisplayMessageClosed(self):
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['ExoPlanetsGraph'])
        self._highlight_transit_location('HighlightSprite', self._transit_message)

    def OnTransitConfirmed(self):
        if self._is_zoom_completed and not self._is_transit_confirmed:
            self._is_transit_confirmed = True
            self._remove_highlight_for_transit_location('HighlightSprite')
            self._is_graph_disabled = True
            sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['TransitMarkerList', 'ExoPlanetsGraph'])
            self._highlight_service.highlight_ui_element_by_name('ExoPlanetsToggleButton', localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ToggleVisibilityLabel'), default_direction=UiHighlightDirections.DOWN)
            self._graph.hide_mini_map_zoom(True)
            sm.ScatterEvent('OnProjectDiscoveryDeleteHide')
            sm.ScatterEvent('OnRemoveTutorialGraphs')

    def OnProjectDiscoveryZoom(self, visibility_range):
        correct_epoch = self._correct_markers[0].get_centers()[0]
        is_centered = 0.48 < (correct_epoch - visibility_range[0]) / (visibility_range[1] - visibility_range[0]) < 0.52
        if self._is_graph_tutorial_closed and is_centered and not self._is_zoom_completed:
            sm.ScatterEvent('OnDisableTransitMarkings', False)
            animations.FadeTo(self._graph.graph_area, self._graph.graph_area.opacity, 1.0)
            self._clear_highlights()
            self._is_zoom_completed = True
            self._highlight_transit_location('HighlightSprite', self._transit_message)

    def OnExoPlanetsColorToggle(self, is_on):
        if self._is_transit_confirmed and not self._is_toggle_off_completed and is_on:
            self._is_graph_disabled = False
            self._graph.Enable()
            self._highlight_service.remove_highlight_from_ui_element_by_name('ExoPlanetsToggleButton')
            self._is_toggle_off_completed = True
            self.explain_solar_system()

    def explain_submit(self):
        self._clear_highlights()
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['BottomContainer'])
        self._highlight_service.highlight_ui_element_by_name('ExoPlanetsSubmitButton', localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/SubmitButtonHighlight'), default_direction=UiHighlightDirections.UP)

    def explain_secondary_classifications(self):
        self._clear_highlights()
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['CategoryContainer'])
        self._highlight_service.remove_highlight_from_ui_element_by_name('ExoPlanetsGraph')
        self._highlight_service.custom_highlight_ui_element_by_name(ui_element_name='CategoryContainer', default_direction=UiHighlightDirections.LEFT, highlight_content=TutorialDescriptionContainer(title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/SecondaryClassificationLabel'), description=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/SecondaryClassificationMessage'), buttonText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ButtonLabel'), width=400, height=130, buttonFunc=lambda args: self.explain_zoom()))

    def explain_zoom(self):
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['ExoPlanetsGraph'])
        self._graph.graph_area.opacity = 0.3
        self._highlight_service.remove_highlight_from_ui_element_by_name('CategoryContainer')
        self._graph.show_mini_map_zoom(is_animate=True)
        self._is_graph_tutorial_closed = True
        sm.ScatterEvent('OnDisplayTutorialGraph', self._correct_markers[0])
        self._highlight_service.highlight_ui_element_by_name('ExoPlanetsZoomSlider', localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ZoomSliderMessage'), default_direction=UiHighlightDirections.DOWN)

    def OnSolutionSubmit(self):
        sm.ScatterEvent('OnProjectDiscoveryResetHighlight')
        self._clear_highlights()

    def OnContinueToRewards(self, *args, **kwargs):
        self.close_tutorial()

    def OnResultScreenShown(self, *args, **kwargs):
        self._transit_message = self._get_result_message()
        sm.ScatterEvent('OnDisplayTutorialGraph', self._correct_markers[0], hide_graphs=True)
        self._highlight_transit_location('HighlightSprite', self._transit_message)

    def _get_result_message(self):
        return localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/FirstTutorialSolution')

    def close_tutorial(self):
        super(FirstSampleTutorial, self).close_tutorial()
        sm.ScatterEvent('OnDisableTransitMarkings', False)
