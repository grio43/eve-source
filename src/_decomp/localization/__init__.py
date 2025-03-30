#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\__init__.py
import logging
import blue
import eveLocalization
from eveprefs import prefs, boot
from localization import formatters
from localization import uiutil
from localization import util
from localization.const import HIGHLIGHT_IMPORTANT_MARKER
import os
IS_PACKAGED = blue.pyos.packaged
_logger = logging.getLogger(__name__)

def __GetLocalization():
    import localizationBase
    if not hasattr(__GetLocalization, 'cached'):
        __GetLocalization.cached = localizationBase.Localization()
    return __GetLocalization.cached


LOCALIZATION_REF = __GetLocalization()
LOCALIZATION_REF._GetByMessageID = eveLocalization.GetMessageByID
LOCALIZATION_REF._GetMetaData = eveLocalization.GetMetaDataByID
Get = LOCALIZATION_REF.Get
GetByMessageID = LOCALIZATION_REF.GetByMessageID
GetByLabel = LOCALIZATION_REF.GetByLabel
GetImportantByMessageID = LOCALIZATION_REF.GetImportantByMessageID
GetImportantByLabel = LOCALIZATION_REF.GetImportantByLabel
GetPlaceholderLabel = LOCALIZATION_REF.GetPlaceholderLabel
GetMetaData = LOCALIZATION_REF.GetMetaData
GetMessageIDForLabel = LOCALIZATION_REF.GetMessageIDForLabel
IsValidTypeAndProperty = LOCALIZATION_REF.IsValidTypeAndProperty
IsValidLabel = LOCALIZATION_REF.IsValidLabel
IsValidMessageID = LOCALIZATION_REF.IsValidMessageID
LoadLanguageData = LOCALIZATION_REF.LoadLanguageData
LoadPrimaryLanguage = LOCALIZATION_REF.LoadPrimaryLanguage
GetLanguages = LOCALIZATION_REF.GetLanguages
UpdateTextCache = LOCALIZATION_REF.UpdateTextCache
GetHashDataDictionary = LOCALIZATION_REF.GetHashDataDictionary
IsPrimaryLanguage = LOCALIZATION_REF.IsPrimaryLanguage
ClearImportantNameSetting = LOCALIZATION_REF.ClearImportantNameSetting
SetTimeDelta = eveLocalization.SetTimeDelta

def GetTimeDeltaSeconds(*args, **kwargs):
    return eveLocalization.GetTimeDelta(*args, **kwargs)


UsePrimaryLanguageText = LOCALIZATION_REF.UsePrimaryLanguageText
UseImportantTooltip = LOCALIZATION_REF.UseImportantTooltip
HighlightImportant = LOCALIZATION_REF.HighlightImportant
FormatImportantString = LOCALIZATION_REF.FormatImportantString
CleanImportantMarkup = LOCALIZATION_REF.CleanImportantMarkup
_ReadLocalizationMainPickle = LOCALIZATION_REF._ReadLocalizationMainPickle
_ReadLocalizationLanguagePickles = LOCALIZATION_REF._ReadLocalizationLanguagePickles
_GetRawByMessageID = LOCALIZATION_REF._GetRawByMessageID
HIGHLIGHT_IMPORTANT_MARKER = HIGHLIGHT_IMPORTANT_MARKER
SYSTEM_LANGUAGE = ''

def OverrideLocalizationLabel(labelNameAndPath, languageID = None, **kwargs):
    if prefs.languageID != 'EN':
        return LOCALIZATION_REF.GetByLabel(labelNameAndPath, languageID, **kwargs)
    error = None
    try:
        message = labelOverride.GetByLabelFromSource(labelNameAndPath, languageID, **kwargs)
    except Exception as e:
        message = None
        error = '\n' + str(e)

    if message is None:
        _logger.warning('Label override failed for: {}, {} {} \n Falling back to binaries'.format(labelNameAndPath, kwargs, error))
        message = LOCALIZATION_REF.GetByLabel(labelNameAndPath, languageID, **kwargs)
    return message


if not IS_PACKAGED and boot and boot.role == 'client':
    import labelOverride
    if labelOverride.GetConfigValue() and os.path.exists('../../eve/staticData'):
        _logger.info('Localization label live reloading is enabled')
        labelOverride.InitializeLocalizationCache()
        GetByLabel = OverrideLocalizationLabel

def ToggleLabelOverride():
    global GetByLabel
    enabled = labelOverride.GetConfigValue()
    if enabled:
        labelOverride.DisableLabelOverride()
        GetByLabel = LOCALIZATION_REF.GetByLabel
        return False
    else:
        labelOverride.EnableLabelOverride()
        labelOverride.InitializeLocalizationCache()
        GetByLabel = OverrideLocalizationLabel
        return True
