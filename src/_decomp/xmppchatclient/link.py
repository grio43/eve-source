#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmppchatclient\link.py
import evelink.client
import localization
from carbonui.uicore import uicore
from eveservices.xmppchat import GetChatService
from xmppchatclient.const import CATEGORY_PLAYER, SYSTEM_CHANNEL_MAX_CHANNELID
SCHEME = 'joinChannel'

def register_link_handlers(registry):
    registry.register(SCHEME, handle_join_channel_link, hint='UI/Chat/ChannelWindow/JoinChannel', color_info=evelink.invite_link_color_info)


def handle_join_channel_link(url):
    channel = parse_channel_url(url)
    channel.join()


def channel_link(channel_id, channel_name):
    return evelink.Link(url=format_channel_url(channel_id), text=channel_name)


def parse_channel_url(url):
    content = url[url.index(':') + 1:]
    parts = content.split('//')
    return ChannelReference.from_raw_channel_id(parts[0])


def format_channel_url(channel_id):
    return '{scheme}:{channel_id}'.format(scheme=SCHEME, channel_id=channel_id)


class ChannelReference(object):

    def __init__(self, channel_id, is_old_channel_id = False, is_system_channel = False):
        self.channel_id = channel_id
        self.is_old_channel_id = is_old_channel_id
        self.is_system_channel = is_system_channel

    @classmethod
    def from_raw_channel_id(cls, raw_channel_id):
        try:
            numeric_channel_id = int(raw_channel_id)
        except ValueError:
            return cls(raw_channel_id)

        is_system_channel = 0 <= numeric_channel_id <= SYSTEM_CHANNEL_MAX_CHANNELID
        channel_id = '{}_{}'.format(CATEGORY_PLAYER, numeric_channel_id)
        return cls(channel_id, is_old_channel_id=True, is_system_channel=is_system_channel)

    @property
    def is_joined(self):
        return GetChatService().IsJoined(self.channel_id)

    def join(self):
        if self.is_system_channel:
            self._show_outdated_link_message()
            return
        did_join = GetChatService().JoinChannel(self.channel_id)
        if not did_join and self.is_old_channel_id:
            self._show_outdated_link_message()

    def _show_outdated_link_message(self):
        uicore.Message('CustomInfo', {'info': localization.GetByLabel('UI/Chat/ChatSvc/OutdatedLink')})
