#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\internalUtil.py
from eveprefs import prefs, boot
defaultLanguage = 'en-us'
if getattr(boot, 'region', None) == 'optic':
    defaultLanguage = 'zh'

def GetStandardizedLanguageID(languageID):
    if not hasattr(GetStandardizedLanguageID, 'cachedLanguages'):
        GetStandardizedLanguageID.cachedLanguages = {'en': 'en-us',
         'en-us': 'en-us',
         'es': 'es',
         'fr': 'fr',
         'it': 'it',
         'ko': 'ko',
         'ja': 'ja',
         'ru': 'ru',
         'de': 'de',
         'zh': 'zh'}
    return GetStandardizedLanguageID.cachedLanguages.get(languageID.lower(), 'en-us')


_cachedLanguageId = None

def GetLanguageIDClient():
    global _cachedLanguageId
    if _cachedLanguageId:
        return _cachedLanguageId
    try:
        _cachedLanguageId = GetStandardizedLanguageID(prefs.languageID)
        return _cachedLanguageId
    except (KeyError, AttributeError):
        return defaultLanguage


def GetLanguageID():
    try:
        ret = None
        try:
            import localstorage
            ls = localstorage.GetLocalStorage()
            ret = ls['languageID']
        except KeyError:
            pass

        if ret is None:
            ret = GetStandardizedLanguageID(session.languageID)
        return ret
    except (KeyError, AttributeError):
        return defaultLanguage


def ClearLanguageID():
    global _cachedLanguageId
    _cachedLanguageId = None


if getattr(boot, 'role', None) == 'client':
    GetLanguageID = GetLanguageIDClient
