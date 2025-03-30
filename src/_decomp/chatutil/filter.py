#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chatutil\filter.py
import re
BANNED_PATTERN = None
HIGHLIGHT_PATTERN = None
BANNED_REPLACEMENT = '***'

def UpdateChatFilterVariables(bannedWordList, highlightWordList):
    global BANNED_PATTERN
    global HIGHLIGHT_PATTERN
    bannedWordText = '|'.join((re.escape(word) for word in bannedWordList))
    hightlightdWordText = '|'.join((re.escape(word) for word in highlightWordList))
    if bannedWordText:
        BANNED_PATTERN = re.compile(bannedWordText, re.IGNORECASE)
    else:
        BANNED_PATTERN = None
    if hightlightdWordText:
        HIGHLIGHT_PATTERN = re.compile(hightlightdWordText, re.IGNORECASE)
    else:
        HIGHLIGHT_PATTERN = None


def CleanAndHighlightText(txt):
    txt = CleanText(txt)
    if HIGHLIGHT_PATTERN and HIGHLIGHT_PATTERN.search(txt):
        txt = HIGHLIGHT_PATTERN.sub(GetHighlightedText, txt)
    return txt


def CleanText(txt):
    if BANNED_PATTERN:
        txt = BANNED_PATTERN.sub(BANNED_REPLACEMENT, txt)
    return txt


def GetHighlightedText(matchobj):
    return '<b><color=green>%s</color></b>' % matchobj.group(0)


def ShouldHightlightBlink(txt):
    if not HIGHLIGHT_PATTERN:
        return False
    if HIGHLIGHT_PATTERN.search(txt):
        return True
    return False
