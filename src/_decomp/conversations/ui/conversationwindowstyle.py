#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\conversations\ui\conversationwindowstyle.py


def has_background_settings(style):
    return style.style_color and style.background_texture and style.background_corner_size is not None and style.background_blur_color is not None and style.background_glow_texture and style.background_glow_corner_size is not None and style.background_glow_outer_padding is not None and style.header_bar_background_texture and style.header_bar_background_corner_size is not None


class ConversationWindowStyle(object):
    style_color = None
    label_color = None
    background_texture = None
    background_corner_size = None
    background_blur_color = None
    background_glow_texture = None
    background_glow_corner_size = None
    background_glow_outer_padding = None
    header_bar_background_texture = None
    header_bar_background_corner_size = None
    scroll_bar_color = None


class AuraConversationWindowStyle(ConversationWindowStyle):
    style_color = (172 / 255.0,
     213 / 255.0,
     241 / 255.0,
     1.0)
    label_color = (1.0, 1.0, 1.0, 1.0)
    background_texture = 'res:/UI/Texture/classes/ConversationUI/auraWindowBack.png'
    background_corner_size = 32
    background_blur_color = (1.0, 1.0, 1.0, 0.9)
    background_glow_texture = 'res:/UI/Texture/classes/ConversationUI/auraWindowGlow.png'
    background_glow_corner_size = 32
    background_glow_outer_padding = 16
    header_bar_background_texture = 'res:/UI/Texture/classes/ConversationUI/auraWindowTitleBar.png'
    header_bar_background_corner_size = 8
    scroll_bar_color = (0.7, 0.7, 1.0, 0.5)


AGENT_ID_TO_STYLE = {5: AuraConversationWindowStyle}
