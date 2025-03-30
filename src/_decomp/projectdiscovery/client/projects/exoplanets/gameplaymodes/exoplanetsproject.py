#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\gameplaymodes\exoplanetsproject.py
import logging
import math
import blue
import carbonui.const as uiconst
import localization
import projectdiscovery.client.projects.exoplanets.graphs.axis as exo_axis
import requests
import trinity
import uthread
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.common.lib.appConst import MSEC
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveCaptionSmall, Label
from eveexceptions import UserError
from gametime import GetWallclockTime, GetTimeDiff
from projectdiscovery.client import const
from projectdiscovery.client.projects.exoplanets.exoplanetscontrolscontainer import ExoPlanetsControlsContainer
from projectdiscovery.client.projects.exoplanets.exoplanetssampleloader import ExoPlanetsSampleLoader
from projectdiscovery.client.projects.exoplanets.exoplanetsutil import markers, consensus, result
from projectdiscovery.client.projects.exoplanets.graphs.exoplanetsgraph import ExoPlanetsGraph
from projectdiscovery.client.projects.exoplanets.graphtoolmanager import GraphToolManager
from projectdiscovery.client.projects.exoplanets.graphtools.magnifyingglasstool import MagnifyingGlassTool, MagnifyingGlassPosition
from projectdiscovery.client.projects.exoplanets.graphtools.transitselectiontool import TransitSelectionTool
from projectdiscovery.client.projects.exoplanets.map.solarsystemscene import SolarSystemScene
from projectdiscovery.client.projects.exoplanets.normalizing import Normalizer
from projectdiscovery.client.projects.exoplanets.processingindicator import ProcessingIndicator
from projectdiscovery.client.projects.exoplanets.selection.transitselectionlist import TransitMarkerList
from projectdiscovery.client.projects.exoplanets.ui.category import CategoryGrid
from projectdiscovery.client.projects.exoplanets.windows.rewardview import RewardView
from projectdiscovery.client.ui.projectcontainer import BaseProjectContainer
from projectdiscovery.client.util.dialogue import Dialogue
from projectdiscovery.common.const import NEEDED_LEVEL_FOR_SUPERIOR_CRATES, TASK_ALLOWANCE_MET_MSG, TASK_ALLOWANCE_PER_MINUTE_MSG, IS_API_MOCKED
from projectdiscovery.common.exceptions import NoConnectionToAPIError, MissingKeyError
from projectdiscovery.common.projects.exoplanets.classes import CLASSES
from projectdiscovery.common.projects.exoplanets.parser import ExoPlanetsDataParser
logger = logging.getLogger(__name__)

class ExoPlanetsProject(BaseProjectContainer):
    __notifyevents__ = BaseProjectContainer.__notifyevents__ + ['OnTaskLoaded',
     'OnDetrend',
     'OnFoldButtonPressed',
     'OnTransitMarkingWithPeriod',
     'OnTransitMarkingWithoutPeriod',
     'OnTransitMarkingInFoldedMode',
     'OnTransitMarkingCancelled',
     'OnTransitMarkingCancelledAfterSettingPeriod',
     'OnContinueToRewards',
     'OnCalibrateToUnFolded',
     'OnContinueFromRewards',
     'OnConfirmButtonPressed',
     'OnDiscardButtonPressed',
     'OnRewardViewVisible',
     'OnRewardsViewHidden',
     'OnProjectDiscoveryResetAndGetNewTask',
     'OnBonusSamplesLeft',
     'OnUIColorsChanged',
     'OnDisplayTransitMarkers',
     'OnProjectDiscoveryLevelUp']
    exo_planets_graph_type = ExoPlanetsGraph
    GRAPH_INITIAL_SIZE = 300

    def ApplyAttributes(self, attributes):
        super(ExoPlanetsProject, self).ApplyAttributes(attributes)
        self._audio_service = sm.GetService('audio')
        self._service = self._get_service()
        self._bottom_container = attributes.get('bottomContainer')
        self.__bonus_xp_notifier = None
        self._task = None
        self._task_id = None
        self._task_time = None
        self._result = None
        self._classification = None
        self._data = None
        self._tool_manager = None
        self._is_data_changed = False
        self.exo_planets_graph = None
        self._is_animating_to_result = False
        self._scene_container = None
        self._analysis_message = None
        self.main_button_container = None
        self._categories = []
        self.should_display_upgraded_loot_dialogue = False
        self._submit_button = None
        self.mmos_gateway = get_mmos_gateway_class()()
        self.transit_selection_tool = TransitSelectionTool()
        self.transit_selection_tool.on_selection_change.connect(self._actual_transit_selection_pipe)
        self.transit_selection_tool.on_phantom_selection_change.connect(self._phantom_transit_selection_pipe)
        self.transit_selection_tool.on_period_edit.connect(self._current_selection_period_edit)
        self._bonus_samples_left = self._service.get_remaining_bonus_samples()
        self._total_bonus_samples = self._service.get_maximum_bonus_samples()
        self.setup_layout()
        self.OnProjectDiscoveryRescaled(scale=self.scale)
        self.exo_planets_graph.set_tool(self.transit_selection_tool)
        self.transit_selection_tool.on_fold_edit_start.connect(self.exo_planets_graph.disable_point_graph)
        self.transit_selection_tool.on_fold_edit_stopped.connect(self.exo_planets_graph.enable_point_graph)
        self._tool_manager = GraphToolManager(self.exo_planets_graph, self.transit_selection_tool, MagnifyingGlassTool(max_time_ratio=0.1, min_time_ratio=0.1, position=MagnifyingGlassPosition.BELOW))
        self.load_new_task()
        self._tool_manager.register_key_listeners()
        uthread.new(self._time_line_player)

    def _disable_ui(self):
        self._main_container.Disable()
        self._bottom_container.Disable()

    def _enable_ui(self):
        self._main_container.Enable()
        self._bottom_container.Enable()

    def Close(self):
        sm.UnregisterNotify(self)
        if self._tool_manager:
            self._tool_manager.unregister_key_listeners()
        if self._audio_service:
            self._audio_service.SendUIEvent(const.Sounds.ProcessingStop)
            self._audio_service.SendUIEvent(const.Sounds.MainImageLoadStop)
        if self.exo_planets_graph:
            self.transit_selection_tool.on_fold_edit_start.disconnect(self.exo_planets_graph.disable_point_graph)
            self.transit_selection_tool.on_fold_edit_stopped.disconnect(self.exo_planets_graph.enable_point_graph)
        if self.transit_selection_tool:
            self.transit_selection_tool.on_selection_change.disconnect(self._actual_transit_selection_pipe)
            self.transit_selection_tool.on_phantom_selection_change.disconnect(self._phantom_transit_selection_pipe)
            self.transit_selection_tool.on_period_edit.disconnect(self._current_selection_period_edit)
        super(ExoPlanetsProject, self).Close()

    def setup_layout(self):
        self.dialogue_container = Container(name='DialogContainer', parent=self, idx=0)
        self._main_container = Container(name='MainContainer', parent=self, align=uiconst.TOALL, padLeft=15, padRight=15, pad=0, clipChildren=False)
        self._notify_parent = Container(name='NotifyParent', parent=self._main_container, align=uiconst.TOTOP, height=20)
        self._setup_reward_view()
        self._show_bonus_xp_information()
        self._setup_graph_container()
        self._setup_middle_container()
        self._setup_solar_system_container()
        self._setup_primary_button_container()
        self.OnUIColorsChanged()

    def _show_bonus_xp_information(self):
        if self._bonus_samples_left > 0:
            self._bonus_xp_notifier = Container(name='BonusXpNotifier', parent=self._notify_parent, align=uiconst.TOALL, bgColor=const.BgColors.BLUE)
            Frame(bgParent=self._bonus_xp_notifier, color=const.Colors.BLUE, opacity=0.3)
            self._bonus_examples_left = Label(parent=self._bonus_xp_notifier, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/RemainingDoubleXPSamples', used=self._total_bonus_samples - self._bonus_samples_left, dailymaximum=self._total_bonus_samples), color=const.Colors.BLUE, padLeft=10)
            self._bonus_description = Label(parent=ContainerAutoSize(parent=self._bonus_xp_notifier, align=uiconst.CENTERRIGHT, padRight=10), align=uiconst.CENTERRIGHT, text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/GettingDoubleXPMessage'), color=const.Colors.BLUE)

    def _setup_reward_view(self):
        RewardView(name='RewardView', parent=self, align=uiconst.CENTER, width=800, height=500, opacity=0, padTop=-10, padBottom=10, state=uiconst.UI_HIDDEN)

    def _setup_graph_container(self):
        self._graph_container = Container(name='GraphContainer', parent=self._main_container, align=uiconst.TOTOP, height=self.GRAPH_INITIAL_SIZE, clipChildren=True)
        self.exo_planets_graph = self.exo_planets_graph_type(name='ExoPlanetsGraph', parent=self._graph_container, align=uiconst.TOALL, data=[], categoryAxisType=exo_axis.ExoPlanetsDayTimeAxis)
        self._graph_processing_indicator = ProcessingIndicator(name='GraphProcessingIndicator', parent=self._graph_container, align=uiconst.TOALL, padLeft=10, padRight=10, opacity=0, idx=0)
        self._submission_processing_indicator = ProcessingIndicator(name='GraphProcessingIndicator', parent=self._graph_container, align=uiconst.TOALL, padLeft=10, padRight=10, opacity=0, idx=0)

    def _setup_middle_container(self):
        self._middle_container = Container(name='MiddleContainer', parent=self._main_container, align=uiconst.TOTOP, height=32)
        self._control_container = ExoPlanetsControlsContainer(name='ControlsContainer', parent=self._middle_container, align=uiconst.TOALL, transitSelectionTool=self.transit_selection_tool)

    def _setup_solar_system_container(self):
        self._solar_system_container = Container(name='SolarSystemPanel', parent=self._main_container, clipChildren=True, align=uiconst.TOALL, padBottom=20)
        self._solar_system_ui_container = Container(name='SolarSystemUI', parent=self._solar_system_container, align=uiconst.TOALL)
        self._categories = CLASSES
        self._category_container = ContainerAutoSize(name='CategoryContainer', parent=self._solar_system_ui_container, align=uiconst.CENTERRIGHT, width=170)
        self._category_label = EveLabelLarge(name='CategoryLabel', parent=self._category_container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/SolarActivityLabel'), padBottom=10)
        self._category_grid_parent = ContainerAutoSize(name='CategoryGridParent', parent=self._category_container, align=uiconst.TOTOP)
        self._category_grid = CategoryGrid(categories=self._categories, parent=self._category_grid_parent, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, rowOffset=0, padRight=10, categoryLayout=[[True, True], [True, True]], cellWidth=56, cellHeight=56)
        self._category_grid.cascade_in(1)
        self._transit_list = TransitMarkerList(name='TransitMarkerList', parent=self._solar_system_ui_container, align=uiconst.TOLEFT, width=400, transitSelectionTool=self.transit_selection_tool)
        self._setup_solar_system_scene()

    def _setup_solar_system_scene(self):
        self._scene_container = SolarSystemScene(name='ExoPlanetsSolarSystem', parent=self._solar_system_container, align=uiconst.TOALL, transitSelectionTool=self.transit_selection_tool)

    def _setup_primary_button_container(self):
        self.main_button_container = Container(name='main_button_container', parent=self._bottom_container, align=uiconst.CENTERBOTTOM, width=355, height=53, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/footerBG.png')
        self.main_button_container.pickState = uiconst.TR2_SPS_CHILDREN
        self.submit_button_container = Container(name='submitButtonContainer', parent=self.main_button_container, width=250, align=uiconst.CENTER, height=40, top=5)
        self._submit_button = Button(name='ExoPlanetsSubmitButton', parent=self.submit_button_container, align=uiconst.CENTER, label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/NoTransitsButtonLabel'), fontsize=18, fixedwidth=170, fixedheight=30, func=lambda args: self._on_solution_submit() or enable_button(self._submit_button, False))
        enable_button(self._submit_button, False)
        self._result_continue_button = Button(name='ExoPlanetsResultContinueButton', parent=self.submit_button_container, align=uiconst.CENTER, label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/FinishButtonLabel'), fontsize=18, fixedwidth=170, fixedheight=30, func=lambda args: self._continue_to_rewards() or enable_button(self._result_continue_button, False))
        self._reward_continue_button = Button(name='ExoPlanetsRewardContinueButton', parent=self.submit_button_container, align=uiconst.CENTER, label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/NextButtonLabel'), fontsize=18, fixedwidth=170, fixedheight=30, func=lambda args: sm.ScatterEvent('OnContinueFromRewards') or enable_button(self._reward_continue_button, False))
        self._left_arrow = Sprite(parent=self.submit_button_container, align=uiconst.CENTERLEFT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        self._right_arrow = Sprite(parent=Transform(parent=self.submit_button_container, align=uiconst.CENTERRIGHT, width=34, height=20, rotation=math.pi), align=uiconst.CENTERRIGHT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        self._primary_buttons = [self._submit_button, self._result_continue_button, self._reward_continue_button]
        self._display_primary_button(self._submit_button)

    def OnProjectDiscoveryLevelUp(self, new_rank, xp_for_new_rank, xp_for_next_rank):
        if new_rank == NEEDED_LEVEL_FOR_SUPERIOR_CRATES:
            self.should_display_upgraded_loot_dialogue = True

    def OnProjectDiscoveryRescaled(self, scale):
        super(ExoPlanetsProject, self).OnProjectDiscoveryRescaled(scale)
        try:
            self._graph_container.height = self.GRAPH_INITIAL_SIZE * self.scale
        except AttributeError:
            logger.warn('OnProjectDiscoveryRescaled Attribute Error', exc_info=1)

    def OnUIColorsChanged(self):
        if self.main_button_container is None:
            return
        color = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIBASE)
        color = Color(*color).SetBrightness(1).GetRGBA()
        self.main_button_container.background_color = color

    def OnTaskLoaded(self, task):
        try:
            self._data = self.mmos_gateway.get_data_from_url(task['url'])
        except NoConnectionToAPIError:
            self.open_task_retrieval_error_dialogue()
            logger.error('Could not get data from task url', exc_info=1)
            return

        self._is_data_changed = True
        enable_button(self._submit_button)
        enable_button(self._result_continue_button)
        enable_button(self._reward_continue_button)
        self._display_primary_button(self._submit_button)
        self._close_analysis_message()
        self._audio_service.SendUIEvent(const.Sounds.MainImageOpenPlay)
        sm.ScatterEvent('OnDataLoaded', self._data)

    def OnDetrend(self, is_detrend, detrend_window_size, number_of_iterations = 15):
        normalizer = Normalizer()
        normalizer.windowSize = detrend_window_size
        normalizer.nbiter = number_of_iterations
        data = normalizer.DetrendCurve(curve=self._data) if is_detrend else self._data
        self.exo_planets_graph.update_animated(data)
        sm.ScatterEvent('OnDataUpdate', data)

    def OnTransitMarkingWithPeriod(self, *args, **kwargs):
        enable_button(self._submit_button, False)

    def OnTransitMarkingCancelledAfterSettingPeriod(self, *args, **kwargs):
        enable_button(self._submit_button)

    def OnTransitMarkingWithoutPeriod(self):
        self.transit_selection_tool.confirm_current_selection()

    def OnTransitMarkingInFoldedMode(self):
        self.exo_planets_graph.fold_animated(self.transit_selection_tool.get_current_selection().get_center(), self.transit_selection_tool.get_current_selection().get_period_length())

    def OnConfirmButtonPressed(self):
        self._calibrate_to_unfolded_mode(callback=lambda : self.transit_selection_tool.confirm_current_selection())

    def OnDiscardButtonPressed(self):
        self.transit_selection_tool.remove_selection(self.transit_selection_tool.get_current_selection())
        self.exo_planets_graph.display_transit_markers([])
        self._calibrate_to_unfolded_mode(is_transit_marker_displayed=False)

    def _on_solution_submit(self):
        sm.ScatterEvent('OnSolutionSubmit')
        self._category_grid.Disable()
        self.main_button_container.Disable()
        self.exo_planets_graph.Disable()
        animations.FadeOut(self.main_button_container, duration=0.5)
        animations.FadeOut(self._middle_container, duration=0.5)
        self.exo_planets_graph.hide_mini_map_zoom(is_animate=True)
        self._reset_to_initial_game_state()
        self._is_animating_to_result = True
        self._submission_processing_indicator.process(duration=1.5, prefix=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/TransmittingMessage'), expand=False, callback=self._on_solution_transmission_completed)
        self._submit_classification()

    def _on_solution_transmission_completed(self):

        def move_callback():

            def set_animation_flag_to_false():
                self._is_animating_to_result = False

            self._submission_processing_indicator.expand_screen(duration=0.5, callback=self._submission_processing_indicator.fade_out)
            self.main_button_container.Enable()
            self.exo_planets_graph.Enable()
            animations.FadeIn(self.main_button_container, duration=0.5, callback=set_animation_flag_to_false)
            animations.FadeIn(self._middle_container, duration=0.5)
            animations.FadeIn(self._solar_system_container, duration=0.5, callback=lambda : self.exo_planets_graph.show_mini_map_zoom(is_animate=True, callback=self._show_results))
            sm.ScatterEvent('OnResultScreenShown')

        move_callback()
        self._display_primary_button(self._result_continue_button)

    def OnContinueToRewards(self, *args, **kwargs):
        self._scene_container.state = uiconst.UI_HIDDEN
        self._fade_out_project()

    def OnRewardViewVisible(self, *args, **kwargs):
        self._display_primary_button(self._reward_continue_button)

    def OnContinueFromRewards(self):
        self._category_grid.Enable()
        self._close_analysis_message()

    def _close_analysis_message(self):
        if self._analysis_message:
            self._analysis_message.Close()
            self._analysis_message = None

    def OnRewardsViewHidden(self):
        sm.ScatterEvent('OnDisableDetrend')
        self.exo_planets_graph.set_data(None)
        self.load_new_task()
        self._display_primary_button(self._submit_button)
        self._fade_in_project()
        self._scene_container.state = uiconst.UI_NORMAL
        if self.should_display_upgraded_loot_dialogue:
            self.show_superior_crate_unlocked_dialogue()

    def show_superior_crate_unlocked_dialogue(self):
        self.should_display_upgraded_loot_dialogue = False
        self.dialogue = Dialogue(name='EntitledToSuperiorBoxesDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=215, messageText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/UpgradedLootMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/UpgradedLootTitle'), label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/UpgradedLootWindowTitle'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/ErrorButton'), toHide=self._main_container)

    def OnFoldButtonPressed(self):
        selection = self.transit_selection_tool.get_current_selection()
        if selection and selection.get_period_length():
            self._calibrate_to_folding_mode()

    def OnCalibrateToUnFolded(self):
        self._actual_transit_selection_pipe()

    def OnProjectDiscoveryResetAndGetNewTask(self):
        self._enable_ui()
        self._reset_to_initial_game_state()
        self.load_new_task()

    def OnBonusSamplesLeft(self, samples_left):
        self._bonus_samples_left = samples_left
        self._notify_parent.Flush()
        self._show_bonus_xp_information()

    def OnDisplayTransitMarkers(self):
        self._actual_transit_selection_pipe()

    def _phantom_transit_selection_pipe(self, is_phantom_selection = True):
        if not self.exo_planets_graph.is_folding():
            if is_phantom_selection:
                transit_selections = self.transit_selection_tool.get_selections_with_phantom_selections()
            else:
                transit_selections = self.transit_selection_tool.get_unhidden_selections()
            self._transit_selection_pipe(transit_selections)

    def _actual_transit_selection_pipe(self, *args, **kwargs):
        if self.exo_planets_graph:
            self._update_submit_button_text()
            if self.exo_planets_graph.is_folding():
                transit_selections = [self.transit_selection_tool.get_current_selection()]
            else:
                transit_selections = self.transit_selection_tool.get_unhidden_selections()
            self._transit_selection_pipe(transit_selections)

    def _transit_selection_pipe(self, transit_selections):
        mini_map_markers = []
        current_marker = self.transit_selection_tool.get_current_selection()
        if current_marker.get_center() and self.transit_selection_tool.is_selection_known_to_tool(current_marker) and not self.transit_selection_tool.is_confirmed_selection(current_marker):
            mini_map_markers = [self.transit_selection_tool.get_current_selection()]
        if self.exo_planets_graph:
            self.exo_planets_graph.display_transit_markers(transit_selections, mini_map_transit_markers=mini_map_markers)

    def _update_submit_button_text(self):
        if self._submit_button:
            text = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/SubmitButtonLabel') if len(self.transit_selection_tool.get_confirmed_selections()) > 0 else localization.GetByLabel('UI/ProjectDiscovery/exoplanets/NoTransitsButtonLabel')
            self._submit_button.SetLabel(text)

    def _current_selection_period_edit(self):
        if self.exo_planets_graph.is_folding():
            current_selection = self.transit_selection_tool.get_current_selection()
            center = current_selection.get_center()
            period = current_selection.get_period_length()
            self.exo_planets_graph.fold(center, period)

    def load_new_task(self):
        try:
            self._task = self._service.get_new_task()
        except UserError as error:
            if error.msg == TASK_ALLOWANCE_PER_MINUTE_MSG:
                self.open_spam_warning_dialogue()
            return
        except (MissingKeyError, NoConnectionToAPIError):
            self.open_task_retrieval_error_dialogue()
            return

        if self._task:
            self._task_id = self._task['id']
        self._task_time = GetWallclockTime()
        sm.ScatterEvent('OnTaskLoaded', self._task)
        self.transit_selection_tool.reset_tool()
        self._control_container.initialize()
        self._category_grid.initialize()
        self._category_grid.cascade_in(1, time_offset=1)

    def _display_primary_button(self, button):
        for _button in self._primary_buttons:
            if _button == button:
                _button.state = uiconst.UI_NORMAL
            else:
                _button.state = uiconst.UI_HIDDEN

    def _get_animate_in_translation_y(self):
        return self.parent.height / 2.0 - self._graph_container.height / 2.0 - 60

    def _reset_to_initial_game_state(self):

        def graph_fadeout_callback():
            self.exo_planets_graph.unfold()
            self._actual_transit_selection_pipe()
            animations.FadeIn(self.exo_planets_graph)

        if self.exo_planets_graph.is_folding():
            animations.FadeOut(self.exo_planets_graph, callback=graph_fadeout_callback)
            self.transit_selection_tool.remove_selection(self.transit_selection_tool.get_current_selection())
        if self.exo_planets_graph.is_zoom():
            self.exo_planets_graph.reset_zoom()
        if not self.transit_selection_tool.is_confirmed_selection(self.transit_selection_tool.get_current_selection()):
            self.transit_selection_tool.remove_selection(self.transit_selection_tool.get_current_selection())
            sm.ScatterEvent('OnProjectDiscoveryMarkerDim', self.transit_selection_tool.get_confirmed_selections())
        self._control_container.initialize()

    def _calibrate_to_folding_mode(self, duration = 1.5):

        def after_calibration():
            self._actual_transit_selection_pipe()
            sm.ScatterEvent('OnCalibrateToFolded')

        self._submit_button.Disable()
        if self.exo_planets_graph.is_zoom():
            self._graph_processing_indicator.show(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/CalibratingMessage', duration=0), 0)
            self.exo_planets_graph.reset_zoom(callback=self._calibrate_to_folding_mode)
            return
        current_selection = self.transit_selection_tool.get_current_selection()
        folding_center = current_selection.get_center()
        folding_period = current_selection.get_period_length()
        self.exo_planets_graph.hide_mini_map_zoom(is_animate=True, duration=duration / 2.0)
        self.exo_planets_graph.calibrate_to_folded_mode(folding_center, folding_period, transit_selection=current_selection, duration=duration, callback=after_calibration)
        self._graph_processing_indicator.process(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/CalibratingMessage'), duration=duration)

    def _calibrate_to_unfolded_mode(self, duration = 1.5, is_transit_marker_displayed = True, callback = None):

        def after_calibration():
            self._submit_button.Enable()
            self.exo_planets_graph.show_mini_map_zoom(is_animate=True, duration=duration / 2.0)
            invoke_callback(callback)
            enable_button(self._submit_button)
            sm.ScatterEvent('OnCalibrateToUnFolded')

        self._submit_button.Disable()
        current_selection = self.transit_selection_tool.get_current_selection() if is_transit_marker_displayed else None
        self.exo_planets_graph.calibrate_to_unfolded_mode(transit_selection=current_selection, duration=duration, callback=after_calibration)
        self._graph_processing_indicator.process(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/UnfoldingMessage'), duration=duration)

    def _fade_out_project(self, callback = None):
        self._main_container.Disable()
        animations.FadeOut(self._main_container, callback=callback)

    def _fade_in_project(self):
        self._main_container.Enable()
        animations.FadeIn(self._main_container)

    def _get_main_container_height(self):
        return self.parent.height - 20

    def _submit_classification(self):
        self._classification = markers.convert_transit_markers_to_classification_object(self.transit_selection_tool.get_confirmed_selections())
        self._classification['stellarActivity'] = [ category['id'] for category in self._categories if category['selected'] ]
        try:
            self._result = self._service.post_classification(self._task, self._classification, self.get_duration(), remark=False)
        except UserError as error:
            if error.msg == TASK_ALLOWANCE_MET_MSG:
                self.open_task_allowance_met_dialogue()
            elif error.msg == TASK_ALLOWANCE_PER_MINUTE_MSG:
                self.open_spam_warning_dialogue()
            else:
                self.open_classification_error_dialogue()

    def _show_results(self):
        sm.ScatterEvent('OnShowProjectDiscoveryId', self._task_id)
        if self._result and 'task' in self._result:
            if self._result['task']['isTrainingSet']:
                correct, missed, incorrect, mapping = result.get_solution_data(self._result, self._data, self.transit_selection_tool.get_confirmed_selections())
                self.exo_planets_graph.setup_result_graph(correct, missed, incorrect, mapping)
                self._show_analysis_result_message(missed, incorrect)
            else:
                self.exo_planets_graph.setup_consensus_graph(consensus.convert_consensus_response_to_consensus_data(self._result), self.transit_selection_tool.get_confirmed_selections())
                self._notify_categories_of_voting()
                self._show_analysis_result_message(is_consensus=True)

    def _notify_categories_of_voting(self):
        voting_dictionary = {category['id']:0 for category in self._categories}
        try:
            stellar_activity_voting = self._result['task']['votes']['stellarActivity']
            for voting_info in stellar_activity_voting:
                voting_dictionary[voting_info['r']] = float(voting_info['vc']) / float(self._result['task']['classificationCount']) * 100

        except KeyError:
            pass

        sm.ScatterEvent('OnCategoryVoteResult', voting_dictionary)

    def _show_analysis_result_message(self, missed_intervals = None, incorrect_intervals = None, is_consensus = False):
        if is_consensus:
            self._analysis_message = self._create_consensus_message_container()
        else:
            self._analysis_message = self._create_unsuccessful_message_container() if missed_intervals or incorrect_intervals else self._create_successful_message_container()
        self._analysis_message.fade_in()

    def _create_unsuccessful_message_container(self):
        return AnalysisResultMessageContainer(name='UnsuccessfulMessage', parent=self._graph_container, align=uiconst.TOTOP_NOPUSH, height=60, text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/AnalysisFailureText').upper(), textColor=const.Colors.RED, bgColor=const.BgColors.RED, opacity=0, idx=0)

    def _create_successful_message_container(self):
        return AnalysisResultMessageContainer(name='SuccessfulMessage', parent=self._graph_container, align=uiconst.TOTOP_NOPUSH, height=60, text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/AnalysisSuccessText').upper(), textColor=const.Colors.GREEN, bgColor=const.BgColors.GREEN, opacity=0, idx=0)

    def _create_consensus_message_container(self):
        transits, total = consensus.get_vote_stats(self._result)
        if total:
            text = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/ConsensusResultsBanner', PercentageMarked=round(float(transits) / float(total) * 100, 1))
        else:
            text = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/NoConsensusYet')
        return AnalysisResultMessageContainer(name='ConsensusMessage', parent=self._graph_container, align=uiconst.TOTOP_NOPUSH, height=60, text=text, textColor=const.Colors.GREEN, bgColor=const.BgColors.GREEN, opacity=0, idx=0)

    def get_duration(self):
        return max(GetTimeDiff(self._task_time, GetWallclockTime()) / MSEC, 0)

    def _continue_to_rewards(self):
        sm.ScatterEvent('OnContinueToRewards', self._result)

    def open_classification_error_dialogue(self):
        self._disable_ui()
        self.dialogue = Dialogue(name='ErrorDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=215, messageText=localization.GetByLabel('UI/ProjectDiscovery/ClassificationErrorMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/ClassificationErrorHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/ErrorButton'), toHide=self._main_container, onCloseEvent='OnRestartWindow')

    def open_task_allowance_met_dialogue(self):
        self._disable_ui()
        self.dialogue = Dialogue(name='ErrorDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=215, messageText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/TaskAllowanceMetErrorBody'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/TaskAllowanceMetErrorLabel'), label=localization.GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/CloseProjectDiscoveryButtonLabel'), toHide=self._main_container, onCloseEvent='OnProjectDiscoveryClosed')

    def open_spam_warning_dialogue(self):
        self._disable_ui()
        self.dialogue = Dialogue(name='ErrorDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=215, messageText=localization.GetByLabel('UI/ProjectDiscovery/SpammingErrorBody'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/SpammingErrorLabel'), label=localization.GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/CloseProjectDiscoveryButtonLabel'), toHide=self._main_container, onCloseEvent='OnProjectDiscoveryClosed')

    def open_task_retrieval_error_dialogue(self):
        self._disable_ui()
        self.dialogue = Dialogue(name='ErrorDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=215, messageText=localization.GetByLabel('UI/ProjectDiscovery/TaskRetrievalErrorMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/TaskRetrievalErrorHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/ErrorButton'), toHide=self._main_container, onCloseEvent='OnProjectDiscoveryResetAndGetNewTask')

    def _time_line_player(self):
        while not self.destroyed:
            current_time = trinity.device.animationTime
            start = current_time
            end = current_time
            if self._data:
                min_time = self._data[0][0]
                max_time = self._data[-1][0]
                total_time = (max_time - min_time) * 5
                end = start + total_time
            else:
                blue.synchro.Yield()
                continue
            while self._data and current_time < end:
                if self._is_data_changed:
                    self._is_data_changed = False
                    break
                if self._data:
                    current_time = trinity.device.animationTime
                    t = float((current_time - start) / (end - start))
                    data_time = (1.0 - t) * min_time + t * max_time
                    self._scene_container.update_time(data_time)
                blue.synchro.Yield()
                if self.destroyed:
                    return


def invoke_callback(callback, *args, **kwargs):
    if callable(callback):
        callback(*args, **kwargs)


def enable_button(button, is_enabled = True):
    button.Enable() if is_enabled else button.Disable()


class AnalysisResultMessageContainer(Container):
    default_align = uiconst.TOTOP_NOPUSH

    def ApplyAttributes(self, attributes):
        super(AnalysisResultMessageContainer, self).ApplyAttributes(attributes)
        self._text = attributes.get('text', '')
        self._text_color = attributes.get('textColor', Color.WHITE)
        self._setup_layout()

    def _setup_layout(self):
        self._caption = EveCaptionSmall(name='Caption', parent=self, align=uiconst.CENTER, text=self._text, color=self._text_color)

    def fade_in(self, time_offset = 0, callback = None):
        animations.FadeTo(self, 0, 1, timeOffset=time_offset, curveType=uiconst.ANIM_OVERSHOT2)
        animations.BlinkIn(self._caption, timeOffset=0.5 + time_offset, callback=callback)

    def fade_out(self, time_offset = 0, callback = None):
        animations.FadeTo(self, 1, 0, timeOffset=0.5 + time_offset, curveType=uiconst.ANIM_OVERSHOT2, callback=callback)
        animations.BlinkOut(self._caption, timeOffset=time_offset)


def get_mmos_gateway_class():
    if IS_API_MOCKED:
        return FakeMMOSGateway
    return MMOSGateway


class BaseMMOSGateway(object):

    def get_data_from_url(self, url):
        raise NotImplementedError('get_data_from_url must be implemented in derived class')


class MMOSGateway(BaseMMOSGateway):

    def __init__(self):
        self._data_parser = ExoPlanetsDataParser()

    def get_data_from_url(self, url):
        try:
            response = requests.get(url)
            return self._data_parser.parse(response.content)
        except Exception as exception:
            raise NoConnectionToAPIError('Project Discovery could not retrieve data for url: %s' % exception)


class FakeMMOSGateway(BaseMMOSGateway):
    SAMPLE_DATA_PATH = '../../packages/projectdiscovery/client/projects/exoplanets/sampledata'
    SAMPLE_TASK_FILENAME = 'NHbD32ISL19D2vPk0BkLN92AiYimmeMU.tab'

    def __init__(self):
        self._file_loader = ExoPlanetsSampleLoader(self.SAMPLE_DATA_PATH, ExoPlanetsDataParser())

    def get_data_from_url(self, url):
        task = self._file_loader.load_sample_via_name(self.SAMPLE_TASK_FILENAME)
        return task.data
