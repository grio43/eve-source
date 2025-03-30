#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\commonutils.py
import re
import blue
from carbon.common.script.sys.serviceConst import ROLEMASK_ELEVATEDPLAYER
from eveprefs import boot

def IsFullLogging():
    return boot.role != 'client' or not blue.pyos.packaged or session.role & ROLEMASK_ELEVATEDPLAYER


def GetAttrs(obj, *names):
    for name in names:
        obj = getattr(obj, name, None)
        if obj is None:
            return

    return obj


def StripTags(s, ignoredTags = tuple(), stripOnly = tuple()):
    if not s or not isinstance(s, basestring):
        return s
    regex = '|'.join([ '</%s>|<%s>|<%s .*?>|<%s *=.*?>|<%s/>' % (tag,
     tag,
     tag,
     tag,
     tag) for tag in stripOnly or ignoredTags ])
    if stripOnly:
        return ''.join(re.split(regex, s))
    elif ignoredTags:
        for matchingTag in [ tag for tag in re.findall('<.*?>', s) if tag not in re.findall(regex, s) ]:
            s = s.replace(matchingTag, '')

        return s
    else:
        return ''.join(re.split('<.*?>', s))
