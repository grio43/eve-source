#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihighlighting\uihighlights.py
import logging
from uihighlighting.const import SPACE_OBJECT_STRING_TO_TYPE, DEFAULT_AUDIO_ON, DEFAULT_AUDIO_OFF, DIRECTION_STRING_TO_ID
logger = logging.getLogger(__name__)

def get_space_object_type(space_object_string):
    if space_object_string in SPACE_OBJECT_STRING_TO_TYPE:
        return SPACE_OBJECT_STRING_TO_TYPE[space_object_string]
    raise KeyError('Unrecognized space object type: %s' % space_object_string)


class Highlight(object):

    def __init__(self, id, name, message_path, seconds_til_fadeout, audio_setting):
        self.id = id
        self.name = name
        self.message_path = message_path
        self.seconds_til_fadeout = seconds_til_fadeout
        self.audio_setting = DEFAULT_AUDIO_ON if audio_setting is None else audio_setting


class UiHighlight(Highlight):

    def __init__(self, id, name, ui_element_name, title_path, message_path, seconds_til_fadeout = None, audio_setting = DEFAULT_AUDIO_ON, additional_effects = None, default_direction = None, offset = None, texturePath = None, iconID = None, iconSize = None, iconColor = None, uiClass = None):
        self.ui_element_name = ui_element_name
        self.title_path = title_path
        self.additional_effects = additional_effects if additional_effects is not None else []
        self.default_direction = DIRECTION_STRING_TO_ID.get(default_direction, None)
        self.offset = offset
        self.texturePath = texturePath
        self.iconID = iconID
        self.iconSize = iconSize
        self.iconColor = iconColor
        self.ui_class = uiClass
        Highlight.__init__(self, id, name, message_path, seconds_til_fadeout, audio_setting)


class SpaceObjectHighlight(Highlight):

    def __init__(self, id, name, space_object_type, space_object_id, message_path, hint_path, seconds_til_fadeout = None, audio_setting = DEFAULT_AUDIO_OFF, disable_bracket_highlight = False, disable_box = False):
        self.space_object_type = self._read_space_object_type(space_object_type)
        self.space_object_id = space_object_id
        self.hint_path = hint_path
        self.disable_bracket_highlight = disable_bracket_highlight
        self.disable_box = disable_box
        Highlight.__init__(self, id, name, message_path, seconds_til_fadeout, audio_setting)

    def _read_space_object_type(self, space_object_type):
        try:
            return get_space_object_type(space_object_type)
        except KeyError:
            logger.exception('No space object type found for %s' % space_object_type)
            return None


class MenuHighlight(Highlight):

    def __init__(self, id, name, menu_name, type_ids):
        self.menu_name = menu_name
        self.type_ids = type_ids
        Highlight.__init__(self, id, name, message_path=None, seconds_til_fadeout=None, audio_setting=DEFAULT_AUDIO_OFF)
