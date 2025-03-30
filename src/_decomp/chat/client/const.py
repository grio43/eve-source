#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\client\const.py


class ChatMessageMode(object):
    TEXT_ONLY = 0
    SMALL_PORTRAIT = 1
    LARGE_PORTRAIT = 2


AVAILABLE_FONT_SIZES = list(range(9, 28))
CHAT_MESSAGE_MODE_LABEL_PATH = {ChatMessageMode.TEXT_ONLY: 'UI/Chat/NoPortrait',
 ChatMessageMode.SMALL_PORTRAIT: 'UI/Chat/SmallPortrait',
 ChatMessageMode.LARGE_PORTRAIT: 'UI/Chat/LargePortrait'}
MAX_MESSAGE_LENGTH = 1024
MAX_MESSAGE_SAFEGUARD_LENGTH = 2048
MAX_MESSAGES_IN_HISTORY = 100
MAX_PENDING_MESSAGES = 4
MAX_MESSAGES_PER_SEC = 3
IDLE_MEMBER_REMOVAL_TIME = 900
SLASH_EMOTE_STRING = '/emote'
SLASH_ME_STRING = '/me'
CHATLOG_TEMPLATE = '\r\n\r\n\n\n        ---------------------------------------------------------------\n\n          Channel ID:      %s\n          Channel Name:    %s\n          Listener:        %s\n          Session started: %s\n        ---------------------------------------------------------------\n\n'
