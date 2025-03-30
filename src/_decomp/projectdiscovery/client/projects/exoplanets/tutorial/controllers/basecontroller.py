#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\tutorial\controllers\basecontroller.py
from abc import abstractmethod
from projectdiscovery.client.projects.exoplanets.selection.transitselection import TransitSelection
from uihighlighting.const import UiHighlightDirections
import blue
import trinity

class TutorialController(object):
    __notifyevents__ = ['OnExoPlanetsTutorialClose', 'OnDataLoaded', 'OnTutorialGraphSpriteLeftOutOfRange']
    __highlighted_names__ = []

    def __init__(self, solution):
        super(TutorialController, self).__init__()
        self._correct_markers = []
        self._task_data = []
        self._transit_message = ''
        self._transit_title = None
        self._solution = solution
        self._highlight_service = sm.GetService('uiHighlightingService')
        self._highlighted_sprites = set()

    @abstractmethod
    def start_tutorial(self):
        pass

    def close_tutorial(self):
        sm.UnregisterNotify(self)
        self._clear_highlights()

    def _clear_highlights(self):
        for name in self.__highlighted_names__:
            self._highlight_service.remove_highlight_from_ui_element_by_name(name)

        self._highlighted_sprites = set()

    def OnExoPlanetsTutorialClose(self, *args, **kwargs):
        self.close_tutorial()

    def OnDataLoaded(self, data):
        self._task_data = data
        self._correct_markers = []
        if self._solution and 'transits' in self._solution:
            for sol in self._solution['transits']:
                marker = TransitSelection(sol['epoch'], sol['period'], self._task_data, listen_to_data_change=True)
                marker.set_period_length(sol['period'])
                self._correct_markers.append(marker)

    def OnTutorialGraphSpriteLeftOutOfRange(self, is_left_out_of_range, sprite):
        if sprite.name not in self._highlighted_sprites:
            return
        self._highlight_service.remove_highlight_from_ui_element_by_name(sprite.name)
        if is_left_out_of_range:
            self._highlight_transit_location(sprite.name, self._transit_message, title=self._transit_title, is_audio=False, default_direction=UiHighlightDirections.RIGHT)
        else:
            self._highlight_transit_location(sprite.name, self._transit_message, title=self._transit_title, is_audio=False)

    def _highlight_transit_location(self, sprite_name, message, title = None, is_audio = True, default_direction = UiHighlightDirections.LEFT):
        self._highlighted_sprites.add(sprite_name)
        self._highlight_service.highlight_ui_element_by_name(sprite_name, message, title=title, default_direction=default_direction, audio_setting=is_audio)

    def _remove_highlight_for_transit_location(self, sprite_name):
        if sprite_name in self._highlighted_sprites:
            self._highlighted_sprites.remove(sprite_name)
            self._highlight_service.remove_highlight_from_ui_element_by_name(sprite_name)

    def _wait(self, seconds):
        end_time = trinity.device.animationTime + seconds
        while trinity.device.animationTime < end_time:
            blue.synchro.Yield()
