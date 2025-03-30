#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\client\const.py
COLOR_ATTENTION_FOREGROUND = (1.0, 0.549, 0, 1.0)
COLOR_ATTENTION_BACKGROUND = (1.0, 0.549, 0, 0.2)
COLOR_INFO_FOREGROUND = (0.361, 0.796, 0.796, 1.0)
COLOR_INFO_BACKGROUND = (0.361, 0.796, 0.796, 0.2)
COLOR_ALARM_FOREGROUND = (0.875, 0.102, 0.137, 1.0)
COLOR_ALARM_BACKGROUND = (0.875, 0.102, 0.137, 0.2)
WIDGET_TEXT_STANDARD_GREY = (0.753, 0.753, 0.753, 1.0)
WIDGET_TEXT_BOLD_WHITE = (1.0, 1.0, 1.0, 0.75)
BACKGROUND_COLOR_GRAY = (1.0, 1.0, 1.0, 0.1)
COLOR_GREEN = (0.0, 0.8, 0.0, 1.0)
COLOR_UI_HIGHLIGHTING = (0.55, 0.89, 1.0, 1.0)
ICON_GROUPING = {1: 'res:/UI/Texture/Classes/DungeonMessaging/ToDoBulletpoint.png',
 2: None,
 3: 'res:/UI/Texture/Classes/DungeonMessaging/plus.png'}
WIDGET_GROUPING_COLOR = {1: WIDGET_TEXT_BOLD_WHITE,
 2: WIDGET_TEXT_BOLD_WHITE,
 3: WIDGET_TEXT_STANDARD_GREY}

def load_icon_grouping_texture(widget_grouping_id):
    return ICON_GROUPING[widget_grouping_id]


def get_icon_grouping_color(widget_grouping_id):
    return WIDGET_GROUPING_COLOR[widget_grouping_id]
