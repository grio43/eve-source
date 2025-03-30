#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\conversations\conversationcontroller.py
import localization
from conversations.const import START_CONVERSATION_EVENT, END_CONVERSATION_EVENT, MINIMIZED_CONVERSATION_EVENT, MAXIMIZED_CONVERSATION_EVENT
from conversations.conversation import ConversationAgent, LineHintImage
from conversations.fsdloaders import ConversationAgentsLoader
from conversations.ui.instructionsconversationwindow import InstructionsConversationWindow, InstructionsConversationWindowWithCloseButton
from fsdBuiltData.common.iconIDs import GetIcon
from fsdBuiltData.common.soundIDs import GetSoundEventName
from log import LogWarn, LogException
import uthread2

class ConversationController(object):

    def __init__(self, conversation_manager):
        self._conversation_manager = conversation_manager
        self._conversation_window = None
        self.active_conversation = None
        self._are_air_npe_agents_preloaded = False
        self._agents_preloaded = set()
        self.opening_thread = None
        self.opening_thread_for_convo_id = None
        self._clear_active_conversation_data()

    def show_conversation(self, conversation_id, show_warning_on_first_close_setting = True, show_continue_button = False, should_close_on_continue = False, should_autoprogress = True, variables = None, show_only_once = False):
        if self.opening_thread:
            if self.opening_thread_for_convo_id == conversation_id:
                return
            self.opening_thread.kill()
            self.opening_thread = None
            self.opening_thread_for_convo_id = None
            self.processing_show_conversation_id = None
        self.opening_thread = uthread2.start_tasklet(self._show_conversation, conversation_getter=self._conversation_manager.get_conversation, conversation_id=conversation_id, show_continue_button=show_continue_button, error_message='Failed to display conversation (id: %s)' % conversation_id, show_warning_on_first_close_setting=show_warning_on_first_close_setting, should_close_on_continue=should_close_on_continue, should_autoprogress=should_autoprogress, variables=variables, show_only_once=show_only_once)
        self.opening_thread_for_convo_id = conversation_id

    def _show_conversation(self, conversation_getter, conversation_id, error_message, show_continue_button = False, show_warning_on_first_close_setting = True, should_close_on_continue = False, should_autoprogress = True, variables = None, show_only_once = False):
        uthread2.sleep(0.1)
        is_processing_it = self.processing_show_conversation_id == conversation_id
        is_already_active = self.active_conversation is not None and self.active_conversation.id == conversation_id
        if is_already_active and self._conversation_window and not self._conversation_window.destroyed:
            self._conversation_window.Maximize()
        if is_already_active or is_processing_it:
            self.opening_thread = None
            self.opening_thread_for_convo_id = None
            return
        try:
            conversation = conversation_getter(conversation_id, variables)
            self.processing_show_conversation_id = conversation_id
            self.force_hiding_active_conversation()
            if show_only_once:
                only_once_conversations = settings.char.ui.Get('only_once_conversations', set())
                if conversation_id in only_once_conversations:
                    if show_continue_button:
                        sm.ScatterEvent('OnClientEvent_ConversationContinueButtonClicked', conversation_id)
                    self.opening_thread = None
                    self.opening_thread_for_convo_id = None
                    self.processing_show_conversation_id = None
                    return
                only_once_conversations.add(conversation_id)
                settings.char.ui.Set('only_once_conversations', only_once_conversations)
            self.active_conversation = conversation
            self.active_conversation_lines = list(self.active_conversation)
            self.active_conversation_line_index = None
            self._show_conversation_window(show_continue_button, show_warning_on_first_close_setting, should_close_on_continue, should_autoprogress)
            self.opening_thread = None
            self.opening_thread_for_convo_id = None
        except (ValueError, RuntimeError) as exc:
            self.force_hiding_active_conversation()
            LogException('{error}: {exc}'.format(error=error_message, exc=exc))
            self.opening_thread = None
            self.opening_thread_for_convo_id = None
            raise ValueError(error_message)

    def force_hiding_active_conversation(self):
        if self._conversation_window:
            if not self._conversation_window.destroyed:
                self._conversation_window.close_window()
            self._conversation_window = None
            self._clear_active_conversation_data()

    def hide_conversation(self):
        if not self.is_conversation_window_available():
            return
        self.close_conversation()

    def close_conversation(self):
        self._conversation_window.Close()

    def is_conversation_active(self):
        if self.active_conversation is None:
            return False
        if self.processing_show_conversation_id is not None:
            return False
        return self._conversation_window and not self._conversation_window.destroyed and not self._conversation_window.IsMinimized()

    def is_processing_show_conversation(self):
        return self.processing_show_conversation_id is not None

    def clear_conversation(self, conversation_id):
        active_conversation_id = self.get_active_conversation_id()
        if active_conversation_id is None or active_conversation_id != conversation_id:
            return
        self.clear_active_conversation()

    def clear_active_conversation(self):
        self.processing_show_conversation_id = None
        self._clear_active_conversation_data()

    def _clear_active_conversation_data(self):
        if self.active_conversation is not None:
            self._notify_of_conversation_end()
        self.active_conversation = None
        self.active_conversation_lines = None
        self.active_conversation_line_index = None
        self.processing_show_conversation_id = None

    def get_conversation_window(self):
        return self._conversation_window

    def is_conversation_window_available(self):
        return self._conversation_window and not self._conversation_window.destroyed

    def show_completed_ui(self):
        self._conversation_window.show_completed_ui()

    def notify_of_conversation_start(self, conversation_id):
        active_conversation_id = self.get_active_conversation_id()
        if active_conversation_id is None or active_conversation_id != conversation_id:
            return
        self.processing_show_conversation_id = None
        self._notify_of_conversation_event(START_CONVERSATION_EVENT)

    def _notify_of_conversation_end(self):
        self._notify_of_conversation_event(END_CONVERSATION_EVENT)

    def notify_of_conversation_minimized(self, conversation_id):
        active_conversation_id = self.get_active_conversation_id()
        if active_conversation_id is None or active_conversation_id != conversation_id:
            return
        self._notify_of_conversation_event(MINIMIZED_CONVERSATION_EVENT)

    def notify_of_conversation_maximized(self, conversation_id):
        active_conversation_id = self.get_active_conversation_id()
        if active_conversation_id is None or active_conversation_id != conversation_id:
            return
        self._notify_of_conversation_event(MAXIMIZED_CONVERSATION_EVENT)

    def _notify_of_conversation_event(self, conversation_event):
        if not self.active_conversation:
            return
        conv_event = conversation_event
        conv_id = self.active_conversation.id
        sm.ScatterEvent(conv_event, conv_id)

    def get_active_conversation_id(self):
        if self.active_conversation is None:
            return
        return self.get_conversation_id(self.active_conversation)

    def get_conversation_id(self, conversation):
        return conversation.id

    def _show_conversation_window(self, show_continue_button = False, show_warning_on_first_close_setting = True, should_close_on_continue = False, should_autoprogress = True):
        if self.active_conversation is None or not self.are_any_conversation_lines_left():
            return
        conversation_id = self.get_active_conversation_id()
        if conversation_id is not None:
            if show_continue_button:
                conversation_window_class = InstructionsConversationWindowWithCloseButton
            else:
                conversation_window_class = InstructionsConversationWindow
            window_name = self._get_conversation_window_name(conversation_window_class)
            self._conversation_window = conversation_window = conversation_window_class(conversation_id=conversation_id, is_completed=False, show_warning_on_first_close_setting=show_warning_on_first_close_setting, should_close_on_continue=should_close_on_continue, should_autoprogress=should_autoprogress)
            conversation_window.name = window_name
            if conversation_id != self.processing_show_conversation_id:
                conversation_window.Close()

    def _get_conversation_window_name(self, conversation_window_class):
        if conversation_window_class in [InstructionsConversationWindow, InstructionsConversationWindowWithCloseButton]:
            return 'TaskConversationWindow'
        return 'ConversationWindow'

    def are_any_conversation_lines_left(self):
        if self.active_conversation is None:
            return False
        elif self.active_conversation_line_index is None:
            return len(self.active_conversation) > 0
        else:
            return self.active_conversation_line_index + 1 < len(self.active_conversation_lines)

    def get_next_conversation_line(self):
        self.processing_show_conversation_id = self.active_conversation.id
        if not self.are_any_conversation_lines_left():
            LogException('Failed to find more lines in the active conversation')
            self.force_hiding_active_conversation()
            return
        if self.active_conversation_line_index is None:
            self.active_conversation_line_index = 0
        else:
            self.active_conversation_line_index += 1
        return self.active_conversation_lines[self.active_conversation_line_index]

    def are_any_previous_conversation_lines_available(self):
        return self.active_conversation_line_index is not None and self.active_conversation_line_index > 0

    def get_previous_conversation_line(self):
        self.processing_show_conversation_id = self.active_conversation.id
        if self.active_conversation_line_index is None or self.active_conversation_line_index == 0:
            LogException('The active conversation is already at the beginning')
            return
        self.active_conversation_line_index -= 1
        return self.active_conversation_lines[self.active_conversation_line_index]

    def get_active_conversation_line(self):
        return self.active_conversation_lines[self.active_conversation_line_index]

    def get_agent_name(self, agent_id):
        return self._conversation_manager.get_agent(agent_id).name

    def get_agent(self, agent_id):
        return self._conversation_manager.get_agent(agent_id)

    def get_line_hint_image(self, line_hint_image_id):
        return self._conversation_manager.get_line_hint_image(line_hint_image_id)

    def get_play_event(self, sound_id):
        if not sound_id:
            return ''
        return self._conversation_manager.get_play_event(sound_id)

    def get_stop_event(self, sound_id):
        return self._conversation_manager.get_stop_event(sound_id)

    def get_music_trigger(self, music_trigger_id):
        return self._conversation_manager.get_music_trigger(music_trigger_id)

    def preload_air_npe_agents(self):
        if not self._are_air_npe_agents_preloaded:
            import avatardisplay.avatardisplay as ad
            self._are_air_npe_agents_preloaded = True
            scenes = ['res:/Animation_Gstate/Scenes/AIR_NPE/Aura/AIR_NPE_Aura_2755_1/',
             'res:/Animation_Gstate/Scenes/AIR_NPE/Aura/AIR_NPE_Aura_2783_1/',
             'res:/Animation_Gstate/Scenes/AIR_NPE/Aura/AIR_NPE_Aura_2831_1/',
             'res:/Animation_Gstate/Scenes/AIR_NPE/Aura/AIR_NPE_Aura_2892_1/',
             'res:/Animation_Gstate/Scenes/AIR_NPE/Balin/AIR_NPE_Balin_2753_1/',
             'res:/Animation_Gstate/Scenes/AIR_NPE/Balin/AIR_NPE_Balin_2776_1/',
             'res:/Animation_Gstate/Scenes/AIR_NPE/Elias/AIR_NPE_Elias_2932_1',
             'res:/Animation_Gstate/Scenes/AIR_NPE/Vesper/AIR_NPE_Vesper_2811_2/']
            ad.PreloadScene(scenes, curve_list_yaml='res:/Animation_Gstate/Scenes/AIR_NPE/curve_cache_list.yaml')

    def preload_agent(self, agent_id):
        if agent_id in self._agents_preloaded:
            return
        try:
            self._agents_preloaded.add(agent_id)
            agent_data = self._fetch_agent_data(agent_id)
            if agent_data:
                import avatardisplay.avatardisplay as ad
                ad.PreloadScene(agent_data.scenePath, curve_list_yaml=agent_data.preloadCachePath)
        except Exception as exc:
            LogException('Unable to preload scenes: ', exc)
            if agent_id in self._agents_preloaded:
                self._agents_preloaded.remove(agent_id)

    def _fetch_agent_data(self, agent_id):
        from conversations.fsdloaders import ConversationAgentsLoader
        return ConversationAgentsLoader.GetByID(agent_id)


class BaseConversationManager(object):

    def __init__(self):
        self._conversation_sounds = ConversationSounds()

    def get_localized_video_paths(self, agent):
        loop_video_path = agent.loopVideoPath
        intro_video_path = agent.introVideoPath
        if localization.util.AmOnChineseServer():
            intro_video_path = agent.introVideoPathChinese or intro_video_path
            loop_video_path = agent.loopVideoPathChinese or loop_video_path
        return (loop_video_path, intro_video_path)

    def get_agent(self, agent_id):
        agent = ConversationAgentsLoader.GetByID(agent_id)
        if agent is None:
            raise ValueError('No agent found with id {id}'.format(id=agent_id))
        name = agent.name
        image_path = agent.imagePath
        loop_video_path, intro_video_path = self.get_localized_video_paths(agent)
        scene_path = agent.scenePath
        return ConversationAgent(agent_id, name, image_path, intro_video_path, loop_video_path, scene_path)

    def get_line_hint_image(self, line_hint_image_id):
        line_hint_image = GetIcon(line_hint_image_id)
        if line_hint_image is None:
            raise ValueError('No line hint image found with id {id}'.format(id=line_hint_image_id))
        description = getattr(line_hint_image, 'description', 'default_description')
        image_path = line_hint_image.iconFile
        return LineHintImage(line_hint_image_id, description, image_path)

    def get_play_event(self, sound_id):
        return self._conversation_sounds.get_play_event(sound_id)

    def get_stop_event(self, sound_id):
        return self._conversation_sounds.get_stop_event(sound_id)

    def get_conversation(self, conversation_id):
        raise NotImplementedError('Implement creating the corresponding conversation objects')


class ConversationSounds(object):

    def __init__(self):
        self.sounds = None

    def get_play_event(self, sound_id):
        play_event = GetSoundEventName(sound_id)
        if play_event is not None:
            return play_event

    def get_stop_event(self, sound_id):
        play_event = self.get_play_event(sound_id)
        if play_event is not None:
            return play_event.replace('_play', '_stop')
