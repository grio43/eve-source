#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evetypes\localizationUtils.py
import logging
from eveprefs import boot
_isBuilt = False
try:
    if not boot:
        raise ImportError()
    import localization
    _isBuilt = True
except ImportError:
    try:
        import localizationcache
    except (ImportError, RuntimeError):
        localizationcache = None
        logging.basicConfig()
        log = logging.getLogger(__name__)
        log.warning('No localization loaders present. Failed to import localizationcache.')

def GetLocalizedTypeName(messageID, languageID = None, important = True):
    if _isBuilt:
        if important:
            return localization.GetImportantByMessageID(messageID, languageID=languageID)
        else:
            return localization.GetByMessageID(messageID, languageID=languageID)
    else:
        if messageID is None:
            return
        if localizationcache:
            return localizationcache.GetMessage(GetTypeLocalizationPath(messageID), messageID, languageID=languageID)
        return ''


def GetTypeLocalizationPath(messageID):
    return 'EVE/Evetypes/Types/Names/{0:02d}'.format(messageID % 100)


def GetLocalizedTypeDescription(messageID, languageID = None):
    if _isBuilt:
        return localization.GetByMessageID(messageID, languageID)
    elif messageID is None:
        return
    elif localizationcache:
        return localizationcache.GetMessage(GetDescriptionLocalizationPath(messageID), messageID, languageID=languageID)
    else:
        return ''


def GetDescriptionLocalizationPath(messageID):
    return 'EVE/Evetypes/Types/Descriptions/{0:02d}'.format(messageID % 100)


def GetLocalizedGroupName(messageID, languageID = None, important = True):
    if _isBuilt:
        if important:
            return localization.GetImportantByMessageID(messageID, languageID=languageID)
        else:
            return localization.GetByMessageID(messageID, languageID=languageID)
    else:
        if localizationcache:
            return localizationcache.GetMessage('EVE/Evetypes/Groups/Names', messageID, languageID=languageID)
        return ''


def GetLocalizedCategoryName(messageID, languageID = None, important = True):
    if _isBuilt:
        if important:
            return localization.GetImportantByMessageID(messageID, languageID=languageID)
        else:
            return localization.GetByMessageID(messageID, languageID=languageID)
    else:
        if localizationcache:
            return localizationcache.GetMessage('EVE/Evetypes/Categories/Names', messageID, languageID=languageID)
        return ''


def GetLocalizedTypeListName(messageID, languageID = None, important = True):
    if _isBuilt:
        if important:
            return localization.GetImportantByMessageID(messageID, languageID=languageID)
        else:
            return localization.GetByMessageID(messageID, languageID=languageID)
    else:
        if localizationcache:
            return localizationcache.GetMessage('EVE/Evetypes/TypeLists/Names', messageID, languageID=languageID)
        return ''
