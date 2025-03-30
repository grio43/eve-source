#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\textImporting\__init__.py
import evetypes
from carbon.common.script.util.commonutils import StripTags
from eveprefs import boot
TAGS_TO_STRIP = ['localized']
SUBLEVEL_FOLDER = '+'
SUBLEVEL_TYPE = '-'
EXTRA_TEXT_SYMBOL_OPEN = '['
EXTRA_TEXT_SYMBOL_CLOSE = ']'

def GetValidNamesAndTypesDict(validCategoryIDs, localized = False):
    nameFunc = GetNameFunc(localized=localized)
    return {CleanText(nameFunc(typeID)).lower():typeID for typeID in evetypes.GetTypeIDsByCategories(validCategoryIDs)}


def GetValidNamesAndTypesDictForGroups(validGroupIDs, localized = False):
    nameFunc = GetNameFunc(localized=localized)
    return {CleanText(nameFunc(typeID)).lower():typeID for typeID in evetypes.GetTypeIDsByGroups(validGroupIDs)}


def GetLines(text, wordsToRemove = None):
    textWithBr = text.replace('\n', '<br>').replace('\r\n', '<br>')
    if wordsToRemove:
        for word in wordsToRemove:
            textWithBr = textWithBr.replace(word, '')

    lines = SplitAndStrip(textWithBr, '<br>')
    return lines


def SplitAndStrip(text, splitOn):
    parts = text.split(splitOn)
    parts = [ x.strip() for x in parts if x.strip() ]
    return parts


def StripImportantSymbol(text):
    return text.replace('*', '')


def GetNameFunc(localized = False):
    try:
        region = boot.region
    except AttributeError:
        region = 'ccp'

    if region == 'optic':
        return evetypes.GetName
    elif localized:
        return __GetNameFunctNotImportant
    else:
        return evetypes.GetEnglishName


def __GetNameFunctNotImportant(typeID):
    return evetypes.GetName(typeID, important=False)


def CleanText(text):
    txt = StripTags(text, stripOnly=TAGS_TO_STRIP)
    txt = StripImportantSymbol(txt)
    return txt


def CleanAndStripText(text):
    txt = CleanText(text)
    txt = txt.strip()
    return txt


def IsUsingDefaultLanguage(playerSession):
    try:
        region = boot.region
    except AttributeError:
        region = 'ccp'

    if region == 'optic':
        return True
    return playerSession.languageID == 'EN'
