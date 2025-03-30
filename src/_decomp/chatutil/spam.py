#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chatutil\spam.py
import re
from itertools import izip, imap
from caching.memoize import Memoize
_tfrom = u'1370,-_*+=^~@\u263b\u3002\u03bc\u03bf\u043c\u043e\u0441'
_tto = u'leto...........momoc'
_spamTrans = dict(izip(imap(ord, _tfrom), _tto))
for ordinal in [u' ',
 u'\\',
 u'|',
 u'/',
 u'!',
 u'(',
 u')',
 u'[',
 u']',
 u'{',
 u'}',
 u'<',
 u'>',
 u'"',
 u"'",
 u'`',
 u'\xb4']:
    _spamTrans[ord(ordinal)] = None

_dotsubst = re.compile('\\.{2,}')

def NormalizeForSpam(s):
    return _dotsubst.sub('.', unicode(s).lower().translate(_spamTrans).replace('dot', '.'))


@Memoize
def GetTaboos():
    bannedPhrasesInChat = sm.GetService('sites').GetBannedInChatList()
    return map(NormalizeForSpam, bannedPhrasesInChat)


def IsSpam(text):
    normtext = NormalizeForSpam(text)
    for taboo in GetTaboos():
        if taboo in normtext:
            foundSpam = True
            idx = text.find(taboo)
            if idx > 0:
                foundSpam = False
                while idx > 0:
                    if text[idx - 1].isalnum():
                        idx = text.find(taboo, idx + 1)
                    else:
                        foundSpam = True
                        break

                return foundSpam
            return True
    else:
        return False
