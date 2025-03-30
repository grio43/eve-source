#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\util.py
import langutils
import pytelemetry.zoning as telemetry
from carbon.common.script.util.commonutils import StripTags
from eveprefs import boot
from localization import internalUtil

def ConvertLanguageIDFromMLS(mlsLanguageID):
    if mlsLanguageID.lower() == 'en':
        return 'en-us'
    else:
        return mlsLanguageID.lower()


def ConvertLanguageIDToMLS(languageID):
    if languageID.lower() == 'en-us':
        return 'EN'
    else:
        return languageID.upper()


def GetLanguageID():
    return internalUtil.GetLanguageID()


def GetDefaultServerLanguageID():
    import localization.const as locconst
    if AmOnChineseServer():
        return locconst.LOCALE_SHORT_CHINESE
    else:
        return locconst.LOCALE_SHORT_ENGLISH


def AmOnChineseServer():
    return boot.region == 'optic'


def StandardizedLanguageIDOrDefault(fromLanguageID = None):
    if not fromLanguageID:
        return internalUtil.GetLanguageID()
    else:
        fromLanguageID = fromLanguageID.lower()
        if fromLanguageID == 'en':
            return 'en-us'
        return fromLanguageID


def GetSortFunc(languageID):
    languageID = StandardizedLanguageIDOrDefault(languageID)
    import eveLocalization
    collator = eveLocalization.Collator()
    collator.locale = str(languageID)

    def SortFunc(left, right):
        res = collator.Compare(unicode(left.lower()), unicode(right.lower()))
        if res == 0:
            return collator.Compare(unicode(right), unicode(left))
        return res

    return SortFunc


@telemetry.ZONE_FUNCTION
def Sort(iterable, cmp = None, key = lambda x: x, reverse = False, languageID = None):
    import localization
    if cmp:
        raise ValueError("Passing a compare function into Sort defeats the purpose of using a language-aware sort.  You probably want to use the 'key' parameter instead.")
    cmpFunc = GetSortFunc(languageID)
    if all([ isinstance(key(each), (int, type(None))) for each in iterable ]):

        def getPronunciation(messageID):
            if not messageID:
                return ''
            ret = ''
            try:
                ret = localization.GetMetaData(messageID, 'pronounciation', languageID=languageID)
            except KeyError:
                ret = localization.GetByMessageID(messageID, languageID)

            return ret

        return sorted(iterable, cmp=cmpFunc, key=lambda x: StripTags(getPronunciation(key(x))), reverse=reverse)
    return sorted(iterable, cmp=cmpFunc, key=lambda x: StripTags(key(x)), reverse=reverse)


def IsTextInConciseLanguage(languageID, textString):
    languageID = langutils.any_to_comfy_language(languageID, default=langutils.get_session_language())
    if IsConciseLanguage(languageID):
        try:
            textString.encode('ascii')
        except UnicodeEncodeError:
            return True

    return False


def IsConciseLanguage(languageID):
    return IsIdeographic(languageID) or IsSyllabic(languageID)


def IsSessionLanguageConcise():
    languageID = langutils.get_session_language()
    return IsConciseLanguage(languageID)


def IsIdeographic(languageID):
    return languageID in [langutils.LANG_JA, langutils.LANG_ZH]


def IsSyllabic(languageID):
    return languageID in [langutils.LANG_JA, langutils.LANG_KO]


def UpperCase(string):
    if langutils.get_session_language() == langutils.LANG_RU:
        return string
    if string is None:
        return ''
    string = string.upper()
    return string
