#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\gameplaymodes\exoplanetstutorial.py
import copy
import logging
import carbonui.const as uiconst
import localization
import projectdiscovery.client.projects.exoplanets.tutorial.const as tutorialconst
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveCaptionMedium
from gametime import GetWallclockTime
from projectdiscovery.client import const
from projectdiscovery.client.projects.exoplanets.ClientLogger import log_tutorial_task_loaded
from projectdiscovery.client.projects.exoplanets.exoplanetssampleloader import ExoPlanetsSampleLoader
from projectdiscovery.client.projects.exoplanets.gameplaymodes.exoplanetsproject import ExoPlanetsProject
from projectdiscovery.client.projects.exoplanets.gameplaymodes.exoplanetsproject import enable_button
from projectdiscovery.client.projects.exoplanets.graphs.exoplanetstutorialgraph import ExoPlanetsTutorialGraph
from projectdiscovery.client.projects.exoplanets.windows.rewardview import RewardView
from projectdiscovery.client.util.dialogue import Dialogue, ResumeTutorialDialogue
from projectdiscovery.common.const import EXOPLANETS_PROJECT_ID
from projectdiscovery.common.exceptions import NoConnectionToAPIError
from projectdiscovery.common.projects.exoplanets.parser import ExoPlanetsDataParser
logger = logging.getLogger(__name__)

class ExoPlanetsTutorial(ExoPlanetsProject):
    __notifyevents__ = ExoPlanetsProject.__notifyevents__ + ['OnProjectDiscoveryStartTutorial',
     'OnProjectDiscoveryStarted',
     'OnProjectDiscoveryTutorialIncrement',
     'OnProjectDiscoveryTutorialFade',
     'OnProjectDiscoveryResetHighlight',
     'OnDisableTransitMarkings',
     'OnProjectDiscoveryTutorialDisplayMessageClosed',
     'OnProjectDiscoveryTutorialDisplayMessage',
     'OnDiscardCurrentMarking',
     'OnExoPlanetsControlsInitialize',
     'OnProjectDiscoveryHideAllTutorialComponents',
     'OnTutorialReset',
     'OnDiscardPreviousMarking']
    exo_planets_graph_type = ExoPlanetsTutorialGraph

    def ApplyAttributes(self, attributes):
        self._waiting = True
        self._number = 0
        self._total = 0
        self._player_statistics = attributes.get('playerStatistics')
        self._player_state = attributes.get('playerState')
        super(ExoPlanetsTutorial, self).ApplyAttributes(attributes)
        self._highlight_info = self._get_highlighted_tutorial_components()
        self.transit_selection_tool.on_selection_change.connect(self._update_tutorials_of_current_marker)
        self.exo_planets_graph.set_current_task(self._service.get_current_task_index())
        if self._service.get_current_task_index() == 0:
            self._show_greeting()
        else:
            self._show_resume_greeting()

    def _get_highlighted_tutorial_components(self):
        return {self.exo_planets_graph.name: {'object': self.exo_planets_graph,
                                       'opacity': self.exo_planets_graph.opacity,
                                       'state': self.exo_planets_graph.state},
         self._category_container.name: {'object': self._category_container,
                                         'opacity': self._category_container.opacity,
                                         'state': self._category_container.state},
         self._bottom_container.name: {'object': self._bottom_container,
                                       'opacity': self._bottom_container.opacity,
                                       'state': self._bottom_container.state},
         self._transit_list.name: {'object': self._transit_list,
                                   'opacity': self._transit_list.opacity,
                                   'state': self._transit_list.state},
         self._control_container.detrending_panel.name: {'object': self._control_container.detrending_panel,
                                                         'opacity': self._control_container.detrending_panel.opacity,
                                                         'state': self._control_container.detrending_panel.state},
         self._tutorial_label.name: {'object': self._tutorial_label,
                                     'opacity': self._tutorial_label.opacity,
                                     'state': self._tutorial_label.state},
         self._control_container.confirm_button_container.name: {'object': self._control_container.confirm_button_container,
                                                                 'opacity': self._control_container.confirm_button_container.opacity,
                                                                 'state': self._control_container.confirm_button_container.state},
         self._control_container.folding_controls.name: {'object': self._control_container.folding_controls,
                                                         'opacity': self._control_container.folding_controls.opacity,
                                                         'state': self._control_container.folding_controls.state}}

    def _setup_reward_view(self):
        RewardView(name='RewardView', parent=self, align=uiconst.CENTER, width=800, height=500, opacity=0, padTop=-10, padBottom=10, state=uiconst.UI_HIDDEN, isTutorial=True)

    def _setup_solar_system_container(self):
        super(ExoPlanetsTutorial, self)._setup_solar_system_container()
        self._tutorial_label = EveCaptionMedium(name='TutorialCaption', parent=self._solar_system_container, text='', align=uiconst.CENTERTOP)

    def _show_bonus_xp_information(self):
        pass

    def _get_service(self):
        return TutorialService(playerState=self._player_state, playerStatistics=self._player_statistics)

    def _update_tutorials_of_current_marker(self):
        current = self.transit_selection_tool.get_current_selection()
        sm.ScatterEvent('OnExoPlanetsMarkerChange', current)

    def Close(self):
        sm.ScatterEvent('OnExoPlanetsTutorialClose')
        super(ExoPlanetsTutorial, self).Close()

    def OnProjectDiscoveryTutorialIncrement(self, number, total):
        self._number = number
        self._total = total
        self._tutorial_label.text = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/RemainingTutorialSamples', number=number, total=total)

    def OnTutorialReset(self):
        self._service.reset_tutorial()
        self.OnProjectDiscoveryResetHighlight()
        self.load_new_task()
        sm.ScatterEvent('OnProjectDiscoveryStartTutorial')

    def load_new_task(self):
        if not self._waiting:
            self._task = self._service.get_new_task()
            if not self._task:
                self._service.skip_tutorial()
                return
            self._task_time = GetWallclockTime()
            self._category_grid.initialize()
            self._category_grid.cascade_in(1, time_offset=1)
            self._control_container.initialize()
            self.transit_selection_tool.reset_tool()
            sm.ScatterEvent('OnTaskLoaded', self._task)

    def OnRewardsViewHidden(self):
        super(ExoPlanetsTutorial, self).OnRewardsViewHidden()
        if not self._task:
            sm.ScatterEvent('OnProjectDiscoveryTutorialFinished')
            return

    def _show_greeting(self):
        self._disable_ui()
        Dialogue(name='greetingDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=340, messageText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/GreetingText'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/GreetingHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/GreetingLabel'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/GreetingButton'), toHide=self._main_container, isTutorial=True)

    def _show_resume_greeting(self):
        self._disable_ui()
        ResumeTutorialDialogue(name='greetingDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=340, label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/GreetingLabel'), toHide=self._main_container, isTutorial=True)

    def OnProjectDiscoveryTutorialDisplayMessage(self, message_text, message_header_text, label, button_label):
        self._disable_ui()
        Dialogue(name='TutorialMessage', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=340, messageText=message_text, messageHeaderText=message_header_text, label=label, buttonLabel=button_label, toHide=self._main_container, onCloseEvent='OnProjectDiscoveryTutorialDisplayMessageClosed')

    def OnDiscardCurrentMarking(self):
        self.transit_selection_tool.remove_selection(self.transit_selection_tool.get_current_selection())

    def OnDiscardPreviousMarking(self):
        self.transit_selection_tool.remove_selection(self.transit_selection_tool.get_confirmed_selections()[-1])

    def OnProjectDiscoveryTutorialDisplayMessageClosed(self):
        self._enable_ui()

    def OnProjectDiscoveryStartTutorial(self):
        self._enable_ui()
        if self._waiting:
            self._waiting = False
            self._task = self._service.get_new_task()
            self.exo_planets_graph.set_current_task(self._service.get_current_task_index())
            if not self._task:
                self._service.skip_tutorial()
                return
            self._task_time = GetWallclockTime()
            self._category_grid.initialize()
            self._category_grid.cascade_in(1, time_offset=1)
            self._control_container.initialize()
            self.transit_selection_tool.reset_tool()
            sm.ScatterEvent('OnTaskLoaded', self._task)

    def OnProjectDiscoveryStarted(self, show_dialog):
        self._service.skip_tutorial()
        sm.ScatterEvent('OnProjectDiscoveryTutorialFinished')

    def OnProjectDiscoveryTutorialFade(self, shown_names):
        shown_objects = [ val for key, val in self._highlight_info.items() if key in shown_names ]
        hidden_objects = [ val for key, val in self._highlight_info.items() if key not in shown_names ]
        for object_info in shown_objects:
            animations.FadeTo(object_info['object'], object_info['object'].opacity, object_info['opacity'])
            object_info['object'].Enable()
            sm.ScatterEvent('OnProjectDiscoveryObjectHighlighted', object_info['object'])

        for object_info in hidden_objects:
            animations.FadeTo(object_info['object'], object_info['object'].opacity, 0.2)
            object_info['object'].Disable()

    def OnProjectDiscoveryResetHighlight(self):
        for key, object_info in self._highlight_info.items():
            animations.FadeTo(object_info['object'], object_info['object'].opacity, object_info['opacity'])
            object_info['object'].Enable()
            object_info['object'].state = object_info['state']
            sm.ScatterEvent('OnProjectDiscoveryObjectHighlighted', object_info['object'])

    def OnProjectDiscoveryHideAllTutorialComponents(self):
        for key, object_info in self._highlight_info.items():
            animations.FadeTo(object_info['object'], object_info['object'].opacity, 0.2)
            object_info['object'].Disable()

    def OnDisableTransitMarkings(self, is_disabled = True):
        self.transit_selection_tool.set_disabled(is_disabled)

    def OnExoPlanetsControlsInitialize(self):
        enable_button(self._submit_button)

    def _continue_to_rewards(self):
        sm.ScatterEvent('OnContinueToRewards', self._result, is_tutorial_show=self._total == self._number)

    def OnTaskLoaded(self, task):
        try:
            self._data = self._service.get_data_from_url(task['url'])
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


class TutorialService(object):

    def __init__(self, playerState, playerStatistics):
        super(TutorialService, self).__init__()
        self._tutorials = []
        self._service = sm.RemoteSvc('ProjectDiscovery')
        self._file_loader = ExoPlanetsSampleLoader('../../packages/projectdiscovery/client/projects/exoplanets/sampledata', ExoPlanetsDataParser())
        self._tutorial_tasks = copy.deepcopy(tutorialconst.tutorial_tasks)
        self._current_task_index = self._service.get_tutorial_level()
        self._current_task = None
        self._player_state = playerState
        self.player_statistics = playerStatistics
        if self._current_task_index == len(self._tutorial_tasks):
            self._service.reset_tutorial()

    def get_new_task(self):
        self._close_current_tutorials()
        self._current_task_index = self._service.get_tutorial_level()
        if self._current_task_index >= len(self._tutorial_tasks):
            return None
        sm.ScatterEvent('OnProjectDiscoveryTutorialIncrement', self._current_task_index + 1, len(self._tutorial_tasks))
        self._current_task = self._tutorial_tasks[self._current_task_index]
        log_tutorial_task_loaded(self._service.get_tutorial_completion_status(), self._current_task_index)
        self._start_tutorials(self._current_task['tutorials'])
        return {'url': self._current_task['fileName'] + '.tab',
         'id': self._current_task['id']}

    def get_data_from_url(self, *args, **kwargs):
        task = self._file_loader.load_sample_via_name(*args, **kwargs)
        return task.data

    def post_classification(self, *args, **kwargs):
        result = {'reliability': 1,
         'task': {'project': EXOPLANETS_PROJECT_ID,
                  'isTrainingSet': True,
                  'solution': self._current_task['solution']},
         'player': {'code': 'tutorialPlayer',
                    'score': self.player_statistics['project']['score'] if self.player_statistics else 0,
                    'scoreChange': 0,
                    'scoredAt': '2017-05-24T21:47:50.935Z'},
         'playerState': self._player_state,
         'XP_Reward': 0,
         'ISK_Reward': 0,
         'loot_crates': 0,
         'bonusSamplesAfterClassification': 0,
         'gotBonusXP': False,
         'tier_reward': False}
        if self._service.get_is_player_entitled_to_tutorial_reward() and self._current_task_index == len(self._tutorial_tasks) - 1:
            if self._service.give_tutorial_rewards():
                self._populate_with_rewards(result)
                result['playerState'] = self._service.get_player_state()
        self._service.increase_tutorial_level()
        return result

    def _populate_with_rewards(self, result_object):
        result_object['XP_Reward'] = 900
        result_object['ISK_Reward'] = 250000
        result_object['loot_crates'] = 1
        result_object['player']['score'] = 0.5

    def get_solution_of_current_task(self):
        if self._current_task:
            return self._current_task['solution']

    def get_current_task_index(self):
        return self._current_task_index

    def _close_current_tutorials(self):
        for tutorial in self._tutorials:
            tutorial.close_tutorial()

        self._tutorials = []

    def _start_tutorials(self, tutorials):
        self._tutorials = []
        for tutorial in tutorials:
            self._tutorials.append(tutorial(self._current_task['solution']))

    def reset_tutorial(self):
        self._service.reset_tutorial()
        self._close_current_tutorials()

    def skip_tutorial(self):
        self._service.skip_tutorial()

    def get_remaining_bonus_samples(self):
        return self._service.get_remaining_bonus_samples()

    def get_maximum_bonus_samples(self):
        return self._service.get_maximum_bonus_samples()
