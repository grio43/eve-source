#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\util\linkUtil.py
from carbonui.util.stringManip import GetAsUnicode
import evelink.client
from eve.common.lib import appConst

def IsLink(text):
    textAsUnicode = GetAsUnicode(text)
    if textAsUnicode.find('<url') != -1:
        return True
    if textAsUnicode.find('<a href') != -1:
        return True
    return False


def GetCharIDFromTextLink(node):
    validTypeIDs = appConst.characterTypes
    return GetItemIDFromTextLink(node, validTypeIDs)


def GetTextLinkUrl(node):
    if getattr(node, '__guid__', None) != 'TextLink':
        return
    return getattr(node, 'url', None)


def GetItemIDFromTextLink(node, validTypeIDs = None):
    url = GetTextLinkUrl(node)
    if url is None:
        return
    try:
        parsed = evelink.parse_show_info_url(url)
    except Exception:
        return

    if validTypeIDs and parsed.type_id not in validTypeIDs:
        return
    return parsed.item_id


def GetTypeIDFromTextLink(node):
    url = GetTextLinkUrl(node)
    if url is None:
        return
    try:
        parsed = evelink.parse_show_info_url(url)
    except Exception:
        return

    return parsed.type_id
