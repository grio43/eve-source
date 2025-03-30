#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\stringManip.py
from carbonui import uiconst

def PrepareArgs(args):
    dest = {}
    arg = args.split('&')
    for i in arg:
        kv = i.split('=', 1)
        if len(kv) == 2:
            s = kv[1]
            if dest.has_key(kv[0]):
                if type(dest[kv[0]]) != type([]):
                    dest[kv[0]] = [dest[kv[0]]]
                dest[kv[0]].append(s)
            else:
                dest[kv[0]] = s
        else:
            dest[i] = ''

    return dest


def FlattenListText(listText):
    ret = []
    for each in listText:
        if isinstance(each, (tuple, list)):
            ret += FlattenListText(each)
        else:
            ret.append(each)

    return ret


def GetAsUnicode(textOrListText):
    if isinstance(textOrListText, (list, tuple)):
        textOrListText = FlattenListText(textOrListText)
        return ''.join((unicode(each) for each in textOrListText))
    return unicode(textOrListText)


def FindTextBoundaries(text, regexObject = None):
    regexObject = regexObject or uiconst.LINE_BREAK_BOUNDARY_REGEX
    return [ token for token in regexObject.split(text) if token ]


def SanitizeFilename(filename, replacementChar = '_'):
    invalidChars = '\\/:*?"<>|'
    validatedName = filename
    for c in invalidChars:
        validatedName = validatedName.replace(c, replacementChar)

    return validatedName
