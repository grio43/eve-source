#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chatutil\channelnames.py
import re
from eve.common.script.sys.idCheckers import IsWormholeSystem, IsNullSecSystem, IsTriglavianSystem, IsZarzakh
from chatutil.const import CATEGORY_LOCAL_SUPPRESSED, CATEGORY_LOCAL, CATEGORY_WORMHOLE, CATEGORY_NULLSEC, CATEGORY_TRIGLAVIAN
from chat.common.util import is_local_chat_suppressed
from eveprefs import prefs
VALID_CHANNELNAME_REGEX = re.compile('^[a-z0-9]+_[a-z0-9_-]+')

def IsValidChannelName(channelName):
    return VALID_CHANNELNAME_REGEX.match(channelName)


def GetIncursionChannelName(taleId):
    return 'incursion_{0}'.format(taleId)


def GetSessionBasedChannelName(prefix, channelId):
    if prefix == CATEGORY_LOCAL:
        if is_local_chat_suppressed(channelId):
            prefix = CATEGORY_LOCAL_SUPPRESSED
        elif IsZarzakh(channelId):
            prefix = CATEGORY_WORMHOLE
        elif IsWormholeSystem(channelId):
            prefix = CATEGORY_WORMHOLE
        elif IsNullSecSystem(channelId) and bool(prefs.GetValue('local_blackout', False)):
            prefix = CATEGORY_NULLSEC
        elif IsTriglavianSystem(channelId):
            prefix = CATEGORY_TRIGLAVIAN
    channelName = '{0}_{1}'.format(prefix, channelId)
    return channelName
