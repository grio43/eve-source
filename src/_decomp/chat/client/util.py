#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\client\util.py
import re
import trinity
import carbonui
from carbon.common.script.util.commonutils import StripTags
from eveexceptions import UserError
from eve.common.script.sys.idCheckers import IsNewbieSystem, IsCareerAgentSystem, IsStarterNPCCorporation
from chatutil import StripBreaks
from chat.common.const import ChatCategory, LOCAL_CHAT_CATEGORIES
from chat.client.const import MAX_MESSAGE_SAFEGUARD_LENGTH
from chat.client.hide_messages import get_hide_message_pattern
_NEW_PLAYER_CHAT_BANNED_PATTERN = re.compile('|'.join((re.escape(word) for word in ['/signup?invc='])), re.IGNORECASE)

def get_chat_default_width():
    device_width = trinity.device.width
    if device_width >= carbonui.IdealSize.SIZE_1680:
        return 450
    if device_width >= carbonui.IdealSize.SIZE_1200:
        return 360
    return 260


def get_chat_default_height():
    device_height = trinity.device.height
    if device_height >= carbonui.IdealSize.SIZE_1200:
        return 350
    if device_height >= carbonui.IdealSize.SIZE_960:
        return 320
    return 260


def parse_pasted_text(text):
    text = text.replace('<t>', '  ')
    ignoredTags = ['b', 'i', 'u']
    ignoredTags += sm.GetService('helpPointer').FindTagToIgnore(text)
    text = StripTags(text, ignoredTags=ignoredTags)
    return text


def parse_chat_message(text, truncate = True):
    text = StripBreaks(text)
    ignoredTags = ['b',
     'i',
     'u',
     'url',
     'br']
    text = StripTags(text, ignoredTags=ignoredTags)
    if truncate:
        text = truncate_chat_message(text)
    return text


def truncate_chat_message(text):
    if len(text) > MAX_MESSAGE_SAFEGUARD_LENGTH:
        return text[:MAX_MESSAGE_SAFEGUARD_LENGTH - 5] + ' ...'
    return text


def should_hide_message(channel_id, category_id, text):
    if _is_new_player_channel(category_id) and bool(_NEW_PLAYER_CHAT_BANNED_PATTERN.search(text)):
        return True
    if category_id in LOCAL_CHAT_CATEGORIES:
        category_id = ChatCategory.LOCAL
    hide_message_pattern = get_hide_message_pattern(channel_id, category_id)
    return hide_message_pattern and hide_message_pattern.search(text)


def check_banned_message_in_new_player_channel(category_id, text):
    if _is_new_player_channel(category_id) and _NEW_PLAYER_CHAT_BANNED_PATTERN.search(text):
        raise UserError('ChatReferralLinkBanned')


def _is_new_player_channel(category_id):
    if category_id == ChatCategory.LOCAL:
        return IsNewbieSystem(session.solarsystemid2) or IsCareerAgentSystem(session.solarsystemid2)
    elif category_id == ChatCategory.CORP:
        return IsStarterNPCCorporation(session.corpid)
    elif category_id == ChatCategory.SYSTEM:
        return True
    else:
        return False
