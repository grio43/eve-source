#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\tutorial\controllers\secondtutorialsample.py
import uthread2
from projectdiscovery.client.projects.exoplanets.exoplanetsutil import markers
from projectdiscovery.client.projects.exoplanets.tutorial.controllers.basecontroller import TutorialController
from projectdiscovery.client.projects.exoplanets.tutorial.tutorialdescriptioncontainer import TutorialDescriptionContainer
from uihighlighting.const import UiHighlightDirections
import localization

class SecondSampleTutorial(TutorialController):
    __notifyevents__ = TutorialController.__notifyevents__ + ['OnTransitMarkingWithPeriod',
     'OnSolutionSubmit',
     'OnCalibrateToFolded',
     'OnCalibrateToUnFolded',
     'OnTransitMarkingInFoldedMode',
     'OnExoPlanetsGraphDrag',
     'OnExoPlanetsMarkerChange',
     'OnConfirmButtonPressed',
     'OnDetrend',
     'OnDiscardButtonPressed',
     'OnProjectDiscoveryObjectHighlighted',
     'OnFoldButtonPressed',
     'OnTransitMarkingCancelledAfterSettingPeriod',
     'OnResultScreenShown',
     'OnTransitMarkingWithoutPeriod',
     'OnContinueToRewards']
    __highlighted_names__ = ['ExoPlanetsGraph',
     'ExoPlanetsSubmitButton',
     'MiniMapArea',
     'ExoPlanetsFoldButton',
     'ExoPlanetsConfirmButton',
     'DetrendCheck',
     'ExoPlanetsInfoContainer',
     'ExoPlanetsTimeLabels']

    def __init__(self, *args, **kwargs):
        super(SecondSampleTutorial, self).__init__(*args, **kwargs)
        self._is_folding = False
        self._has_detrended = False
        self._is_detrending = False
        self._graph = None
        self._is_explaining_orbital_period_in_folding = False
        self._is_graph_disabled = False
        self._has_marked_the_transit = False
        self._has_player_edited_epoch = False
        self._has_player_click_and_dragged = False
        self._has_displayed_confirm_message = False
        self._marker_change_count = 0
        self._marking_number = 0
        self._drag_count = 0
        self._current_marker = None
        sm.RegisterNotify(self)
        uthread2.StartTasklet(self.start_tutorial)

    def start_tutorial(self):
        self._highlight_service.custom_highlight_ui_element_by_name(ui_element_name='ExoPlanetsGraph', default_direction=UiHighlightDirections.DOWN, offset=-80, highlight_content=TutorialDescriptionContainer(title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/MultipleTransitsLabel'), description=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/MultipleTransitsMessage'), buttonText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ButtonLabel'), width=400, height=110, buttonFunc=self.explain_detrending))
        self._is_graph_disabled = True
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['ExoPlanetsGraph'])

    def explain_detrending(self, *args):
        self._clear_highlights()
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['DetrendingControlPanel'])
        self._highlight_service.highlight_ui_element_by_name(ui_element_name='DetrendCheck', default_direction=UiHighlightDirections.DOWN, title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/DetrendingLabel'), message=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/DetrendingMessage'))

    def OnDetrend(self, is_detrend, *args, **kwargs):
        if not self._has_detrended:
            self._clear_highlights()
            self.explain_click_and_drag_marking()
        self._has_detrended = True

    def explain_click_and_drag_marking(self, *args):
        self._is_graph_disabled = False
        self._graph.Enable()
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['ExoPlanetsGraph'])
        sm.ScatterEvent('OnDisplayTutorialGraph', self._correct_markers[0])
        self._highlight_service.highlight_ui_element_by_name(ui_element_name='ExoPlanetsGraph', default_direction=UiHighlightDirections.RIGHT, title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/MultipleTransitsPerMarkerLabel'), message=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/MultipleTransitsPerMarkerMessage'))

    def OnProjectDiscoveryObjectHighlighted(self, object):
        if object.name == 'ExoPlanetsGraph':
            self._graph = object
            if self._is_graph_disabled:
                self._graph.Disable()
            else:
                self._graph.Enable()

    def OnTransitMarkingWithPeriod(self):
        self._marking_number += 1
        self._clear_highlights()
        if self._marking_number == 1:
            self.explain_unfolded_cancellation()
        elif self._marking_number >= 2 and not self._has_marked_the_transit:
            self.explain_folding()
        sm.ScatterEvent('OnRemoveTutorialGraphs')

    def OnTransitMarkingWithoutPeriod(self):
        sm.ScatterEvent('OnProjectDiscoveryTutorialDisplayMessage', message_text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/MultipleTransitsNotMarked'), message_header_text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/TutorialWarningLabel'), label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/Name'), button_label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ButtonLabel'))
        sm.ScatterEvent('OnExoPlanetsControlsInitialize')
        sm.ScatterEvent('OnDiscardPreviousMarking')

    def explain_unfolded_cancellation(self):
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['ExoPlanetsGraph'])
        self._graph.disable_left_click(False)
        self._graph.disable_right_click(False)
        self._clear_highlights()
        self._highlight_service.highlight_ui_element_by_name('ExoPlanetsGraph', title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/CancelMarkingLabel'), message=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/CancelMarkingMessage'))

    def OnTransitMarkingCancelledAfterSettingPeriod(self):
        if not self._has_marked_the_transit:
            self._clear_highlights()
            self._highlight_service.highlight_ui_element_by_name('ExoPlanetsGraph', message=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/RemarkInstruction'))
            sm.ScatterEvent('OnDisplayTutorialGraph', self._correct_markers[0])

    def explain_folding(self):
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['FoldButtonContainer'])
        self._highlight_service.highlight_ui_element_by_name(ui_element_name='ExoPlanetsFoldButton', default_direction=UiHighlightDirections.DOWN, message=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/FoldInstructionMessage'), title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/FoldingInstructionLabel'))

    def OnFoldButtonPressed(self):
        self._is_graph_disabled = True
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['ExoPlanetsGraph'])

    def OnCalibrateToFolded(self):
        self._is_folding = True
        if not self._has_marked_the_transit:
            sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['ExoPlanetsGraph'])
            self._graph.Disable()
            self._highlight_service.custom_highlight_ui_element_by_name(ui_element_name='ExoPlanetsGraph', default_direction=UiHighlightDirections.DOWN, offset=-80, highlight_content=TutorialDescriptionContainer(title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/FoldedModeLabel'), description=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/FoldedModeMessage'), buttonText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ButtonLabel'), width=400, height=110, buttonFunc=self.explain_x_axis))

    def explain_x_axis(self, *args, **kwargs):
        self._clear_highlights()
        self._highlight_service.custom_highlight_ui_element_by_name(ui_element_name='ExoPlanetsTimeLabels', default_direction=UiHighlightDirections.UP, highlight_content=TutorialDescriptionContainer(title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/XAxisLabel'), description=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/XAxisFoldedMessage'), buttonText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ButtonLabel'), width=300, height=100, buttonFunc=self.explain_info_container))

    def explain_info_container(self, *args, **kwargs):
        self._clear_highlights()
        self._highlight_service.custom_highlight_ui_element_by_name(ui_element_name='ExoPlanetsInfoContainer', default_direction=UiHighlightDirections.LEFT, highlight_content=TutorialDescriptionContainer(title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/MarkingInfoLabel'), description=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/MarkingInfoMessage'), buttonText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ButtonLabel'), width=280, height=70, buttonFunc=self.explain_folded_mode_epoch))

    def explain_folded_mode_epoch(self, *args, **kwargs):
        self._is_graph_disabled = False
        self._clear_highlights()
        self._graph.Enable()
        self._highlight_service.highlight_ui_element_by_name('ExoPlanetsGraph', title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/EpochEditingLabel'), message=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/EpochEditingMessage'))

    def OnTransitMarkingInFoldedMode(self):
        if not self._has_player_edited_epoch:
            self._has_player_edited_epoch = True
            self.explain_folded_mode_orbital_period()

    def explain_folded_mode_orbital_period(self):
        self._clear_highlights()
        self._is_explaining_orbital_period_in_folding = True
        self._highlight_service.highlight_ui_element_by_name('ExoPlanetsGraph', title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/PeriodEditingLabel'), message=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/PeriodEditingMessage'))

    def OnExoPlanetsMarkerChange(self, current_marker):
        self._current_marker = current_marker
        if self._is_folding and self._has_player_edited_epoch and self._marker_change_count > 0 and not self._has_displayed_confirm_message and self.is_marker_roughly_correct():
            self.explain_confirm_button()
        elif self._is_explaining_orbital_period_in_folding:
            self._marker_change_count += 1

    def explain_confirm_button(self):
        self._clear_highlights()
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['ConfirmationContainer', 'ExoPlanetsGraph'])
        self._has_displayed_confirm_message = True
        self._highlight_service.highlight_ui_element_by_name('ExoPlanetsConfirmButton', message=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ExplainConfirmButtonLabel'))

    def OnConfirmButtonPressed(self):
        self._has_marked_the_transit = True
        self._clear_highlights()

    def OnDiscardButtonPressed(self):
        self._clear_highlights()

    def OnCalibrateToUnFolded(self):
        self._is_folding = False
        self._clear_highlights()
        sm.ScatterEvent('OnProjectDiscoveryTutorialFade', ['BottomContainer'])
        self._highlight_service.highlight_ui_element_by_name('ExoPlanetsSubmitButton', message=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/SubmissionInstruction'), default_direction=UiHighlightDirections.UP)

    def is_marker_roughly_correct(self):
        return any([ markers.are_markers_similar(self._current_marker, marker) for marker in self._correct_markers ])

    def OnSolutionSubmit(self):
        self._clear_highlights()
        sm.ScatterEvent('OnRemoveTutorialGraphs')
        sm.ScatterEvent('OnProjectDiscoveryResetHighlight')

    def OnResultScreenShown(self):
        self._highlight_service.highlight_ui_element_by_name('ExoPlanetsGraph', message=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/SecondTutorialResult'), default_direction=UiHighlightDirections.DOWN, offset=-80)

    def OnContinueToRewards(self, *args, **kwargs):
        self._clear_highlights()
