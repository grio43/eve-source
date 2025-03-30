#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\conversations\conversation.py
import localization

class ConversationAgent(object):

    def __init__(self, agent_id, name, image_path, intro_video_path = None, loop_video_path = None, scene_path = None):
        self.agent_id = agent_id
        self.name = name
        self.image_path = image_path
        self.use_video = loop_video_path is not None
        self.use_intro_video = intro_video_path is not None
        self.intro_video_path = intro_video_path
        self.loop_video_path = loop_video_path
        self.scene_path = scene_path


class LineOfDialogueHint(object):

    def __init__(self, text, iconID, imageSize, imageColor):
        self.text = text
        self.iconID = iconID
        self.image_size = imageSize
        self.image_color = imageColor


class LineOfDialogue(object):

    def __init__(self, agent_id, text_message_id, sound_id, hints, music_trigger, scene_path = None, variables = None):
        self.agent_id = agent_id
        self.text_message_id = text_message_id
        self.sound_id = sound_id
        self.music_trigger = music_trigger
        self.scene_path = scene_path
        self.variables = variables or {}
        self.hints = [ LineOfDialogueHint(hint.text, getattr(hint, 'iconID', None), getattr(hint, 'imageSize', None), getattr(hint, 'imageColor', None)) for hint in hints ]

    def get_text(self):
        return localization.GetByMessageID(self.text_message_id, **self.variables)


class Conversation(object):

    def __init__(self, id, name, lines, variables = None):
        self.id = id
        self.name = name
        self._lines = lines
        self._line_iterator = iter(lines)
        self.variables = variables

    def __len__(self):
        return len(self._lines)

    def reset(self):
        self._line_iterator = iter(self._lines)

    def next(self):
        raise NotImplementedError('Implement creating the corresponding conversation LineOfDialogue object')

    def __iter__(self):
        return self


class LineHintImage(object):
    ALL_RACES = 0

    def __init__(self, line_hint_image_id, description, image_path):
        self.line_hint_image_id = line_hint_image_id
        self.name = description
        self.image_path = image_path
