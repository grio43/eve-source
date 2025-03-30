#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\common\const.py
from itertoolsext.Enum import Enum

@Enum

class MemberClassification(object):
    UNSPECIFIED = 0
    INVISIBLE = 1
    DEVELOPER = 2
    ADMINISTRATOR = 3
    GAME_MASTER = 4
    VOLUNTEER = 5
    NPC = 6


CLASSIFACTION_TO_COLOR = {MemberClassification.NPC: '0xb2ffff20',
 MemberClassification.GAME_MASTER: '0xb2ee6666',
 MemberClassification.DEVELOPER: '0xb20099ff',
 MemberClassification.VOLUNTEER: '0xb200ffcc'}

class ChatCategory(object):
    PRIVATE = 'private'
    PLAYER = 'player'
    SYSTEM = 'system'
    FLEET = 'fleet'
    CORP = 'corp'
    ALLIANCE = 'alliance'
    FACTION = 'faction'
    RW = 'resourcewars'
    INCURSION = 'incursion'
    LOCAL = 'local'
    LOCAL_SUPPRESSED = 'nolocal'
    WORMHOLE = 'wormhole'
    TRIGLAVIAN = 'triglavian'
    NULLSEC = 'nullsec'


MIGRATED_CHAT_CATEGORIES = [ChatCategory.LOCAL,
 ChatCategory.LOCAL_SUPPRESSED,
 ChatCategory.WORMHOLE,
 ChatCategory.TRIGLAVIAN,
 ChatCategory.NULLSEC]
LOCAL_CHAT_CATEGORIES = (ChatCategory.LOCAL,
 ChatCategory.LOCAL_SUPPRESSED,
 ChatCategory.WORMHOLE,
 ChatCategory.TRIGLAVIAN,
 ChatCategory.NULLSEC)
CATEGORY_LABEL_PATH = {ChatCategory.LOCAL: 'UI/Chat/Local',
 ChatCategory.CORP: 'UI/Common/Corp',
 ChatCategory.ALLIANCE: 'UI/Common/Alliance',
 ChatCategory.FACTION: 'UI/Common/Militia',
 ChatCategory.FLEET: 'UI/Fleet/Fleet',
 ChatCategory.PRIVATE: 'UI/Chat/CategoryPrivate',
 ChatCategory.SYSTEM: 'UI/Chat/CategoryCustom',
 ChatCategory.PLAYER: 'UI/Chat/CategoryCustomPlayer',
 ChatCategory.INCURSION: 'UI/Chat/CategoryIncursion'}
LOCAL_CHAT_XMPP_FEATURE_FLAG_KEY = 'xmpp_local_chat_migrated'
LOCAL_CHAT_FEATURE_FLAG_KEY = 'eve-local-chat-authority'
LOCAL_CHAT_FEATURE_FLAG_FALLBACK = False
