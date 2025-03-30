#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\localizationBase.py
import cPickle as pickle
import hashlib
import logging
import re
import sys
import blue
import eveLocalization
import langutils
import logmodule
from carbon.common.script.sys.serviceConst import ROLEMASK_ELEVATEDPLAYER
from carbon.common.script.util import commonutils
from eveprefs import boot, prefs
from pytelemetry import zoning as telemetry
from localization import const as locconst, internalUtil, logger, parser, uiutil, util
from localization.settings import bilingualSettings, qaSettings
log = logging.getLogger(__name__)
OFFSET_TEXT = 0
OFFSET_METADATA = 1
OFFSET_TOKENS = 2

class Localization(object):
    __guid__ = 'localization.Localization'
    PICKLE_EXT = '.pickle'
    FSD_CLIENT_PREFIX = 'res:/localizationFSD/localization_fsd_'
    FIELD_LABELS = 'labels'
    FIELD_LANGUAGES = 'languages'
    FIELD_TYPES = 'types'

    def __init__(self):
        self._InitializeInternalVariables()
        self._InitializeTextData()
        self._importantNameSetting = None
        self._languageTooltipSetting = None
        self._qaTooltipOverride = None
        self._highlightImportantSetting = None
        message = u'Cerberus localization module loaded on ' + (boot.role if boot else '(Tool Environment)')
        log.info(message)
        print message

    def LoadLanguageData(self):
        import propertyHandlers
        if boot.role == 'client':
            internalUtil.ClearLanguageID()
        picklePrefixes = [(self.FSD_CLIENT_PREFIX, locconst.DATATYPE_FSD)]
        supportedLanguagesByPrefix = {}
        for prefix, dataType in picklePrefixes:
            supportedLanguagesByPrefix[prefix] = self._ReadLocalizationMainPickle(prefix + 'main' + self.PICKLE_EXT, dataType)
            if not supportedLanguagesByPrefix[prefix]:
                message = u'Cerberus localization module failed to load MAIN pickle on %s.  See log server for details.' % boot.role
                log.error(message)
                print message
                return

        self._ValidateAndRepairPrefs()
        for prefix, dataType in picklePrefixes:
            if not self._ReadLocalizationLanguagePickles(prefix, supportedLanguagesByPrefix[prefix], dataType):
                message = u'Cerberus localization module failed to load language pickles on %s. See log server for details.' % boot.role
                log.error(message)
                print message
                return

    def GetLanguageStartupArg(self):
        argKey = '/language='
        for arg in blue.pyos.GetArg()[1:]:
            if arg and arg.startswith(argKey):
                log.info(u'language argument from launcher found: %s', arg)
                return arg[len(argKey):]

    def GetLanguages(self):
        return list(self.languagesDefined)

    @telemetry.ZONE_METHOD
    def LoadPrimaryLanguage(self, prefix, dataType):
        languageID = self._GetPrimaryLanguage()
        self._primaryLanguageID = languageID
        eveLocalization.SetPrimaryLanguage(languageID)
        if self._primaryLanguageID in self.languagesDefined:
            if not self._LoadLanguagePickle(prefix, self._primaryLanguageID, dataType):
                return False
        else:
            log.error(u"Language '%r' is not enabled. Text data was not loaded.", languageID)
            return False
        return True

    def GetImportantByMessageID(self, messageID, **kwargs):
        if boot.region == 'optic':
            if not (session and session.role & ROLEMASK_ELEVATEDPLAYER):
                return self.GetByMessageID(messageID, **kwargs)
        if boot.role == 'proxy':
            return self.GetByMessageID(messageID, **kwargs)
        playerLanguageID = kwargs.pop('languageID', None) or internalUtil.GetLanguageID()
        if playerLanguageID != self._primaryLanguageID or self._QaTooltipOverride():
            if self.UsePrimaryLanguageText():
                textString = self.GetByMessageID(messageID, self._primaryLanguageID, **kwargs)
                hintLang = playerLanguageID
            else:
                textString = self.GetByMessageID(messageID, playerLanguageID, **kwargs)
                hintLang = self._primaryLanguageID
            if self.HighlightImportant():
                textString = '%s%s' % (textString, locconst.HIGHLIGHT_IMPORTANT_MARKER)
            if self.UseImportantTooltip() and not qaSettings.LocWrapSettingsActive():
                if self._QaTooltipOverride() and playerLanguageID == self._primaryLanguageID:
                    hintString = textString[:-1][::-1]
                else:
                    hintString = self.GetByMessageID(messageID, hintLang, **kwargs)
                hintString = hintString.replace('"', "'").replace('<', '[').replace('>', ']')
                textString = '<localized hint="%s">%s</localized>' % (hintString or '', textString)
        else:
            textString = self.GetByMessageID(messageID, **kwargs)
        return textString

    def GetImportantByLabel(self, labelNameAndPath, **kwargs):
        try:
            messageID = self.languageLabels[labelNameAndPath]
        except KeyError:
            logger.LogTraceback(u'No label with name %r', labelNameAndPath)
            return '[no label: %s]' % labelNameAndPath

        return self.GetImportantByMessageID(messageID, **kwargs)

    def FormatImportantString(self, locText, englishText):
        if boot.region == 'optic':
            if not (session and session.role & ROLEMASK_ELEVATEDPLAYER):
                return locText
        playerLanguageID = internalUtil.GetLanguageID()
        if playerLanguageID == self._primaryLanguageID and self._QaTooltipOverride():
            return '<localized hint="%s">%s*</localized>' % (englishText[::-1], englishText)
        if playerLanguageID != self._primaryLanguageID:
            if self.UsePrimaryLanguageText():
                textString = englishText
                hintText = locText
            else:
                textString = locText
                hintText = englishText
            if self.HighlightImportant():
                textString = '%s*' % textString
            if self.UseImportantTooltip() and not qaSettings.LocWrapSettingsActive():
                textString = '<localized hint="%s">%s</localized>' % (hintText, textString)
        else:
            textString = locText
        return textString

    def CleanImportantMarkup(self, textString):
        if self.UseImportantTooltip():
            textString = commonutils.StripTags(textString, stripOnly=['localized'])
        if self.HighlightImportant() and len(textString) > 1 and textString[-1] == '*':
            textString = textString.replace(locconst.HIGHLIGHT_IMPORTANT_MARKER, '')
        return textString

    def Get(self, messageIDorLabel, languageID = None, **kwargs):
        if not messageIDorLabel:
            return
        comfylang = langutils.any_to_comfy_language(languageID or internalUtil.GetLanguageID())
        if session and 'player' not in kwargs:
            kwargs['player'] = session.charid
        if isinstance(messageIDorLabel, (str, unicode)):
            messageID = self.languageLabels.get(messageIDorLabel, None)
            if not messageID:
                logger.LogTraceback(u'No label with name %r' % messageIDorLabel)
                return
        else:
            messageID = messageIDorLabel
        try:
            textString = self._GetByMessageID(messageID, comfylang.cerberus_code(), **kwargs)
            if '<localized' in textString:
                textString = re.sub('^<localized hint="[a-z\\sA-Z]*">', '', textString)
                textString = re.sub('<\\/localized>', '', textString)
            return uiutil.PrepareLocalizationSafeString(textString, messageID=messageID)
        except KeyError:
            return
        except Exception as ex:
            log.warning('_GetByMessageID failed: %r' % ex, exc_info=1, extra={k:v for k, v in sys._getframe(1).f_locals.iteritems() if isinstance(v, basestring) and isinstance(k, basestring) and 'label' in k.lower()})
            try:
                return eveLocalization.GetRawByMessageID(messageID, comfylang.cerberus_code())
            except:
                return

    def GetByMessageID(self, messageID, languageID = None, **kwargs):
        if messageID is None:
            return ''
        val = self.Get(messageID, languageID, **kwargs)
        if val is None:
            return u'[no messageID: %s]' % messageID
        return val

    def GetByLabel(self, labelNameAndPath, languageID = None, **kwargs):
        val = self.Get(labelNameAndPath, languageID, **kwargs)
        if val is None:
            return u'[no label: %s]' % labelNameAndPath
        return val

    def GetMessageIDForLabel(self, labelNameAndPath):
        messageID = self.languageLabels[labelNameAndPath]
        return messageID

    def IsValidMessageID(self, messageID, languageID = None):
        languageID = util.StandardizedLanguageIDOrDefault(languageID)
        return eveLocalization.IsValidMessageID(messageID, languageID)

    def IsValidLabel(self, labelNameAndPath, languageID = None):
        try:
            messageID = self.languageLabels[labelNameAndPath]
            return self.IsValidMessageID(messageID, languageID)
        except KeyError:
            return False

    def IsValidTypeAndProperty(self, typeName, propertyName, languageID = None):
        IS_INVALID_TYPE = 0
        IS_INVALID_PROPERTY = 1
        IS_VALID_TYPE_AND_PROPERTY = 2
        result = None
        languageID = util.StandardizedLanguageIDOrDefault(languageID)
        foundType = self.languageTypesWithProperties.get(typeName, None)
        if foundType is not None:
            foundPropertyList = foundType.get(languageID, None)
            if foundPropertyList is not None:
                if propertyName in foundPropertyList:
                    result = IS_VALID_TYPE_AND_PROPERTY
                else:
                    result = IS_INVALID_PROPERTY
            else:
                result = IS_INVALID_PROPERTY
        else:
            result = IS_INVALID_TYPE
        if result == IS_INVALID_PROPERTY:
            log.error(u"'%s' is not a valid property for '%s' in language '%s'.", propertyName, typeName, languageID)
        elif result == IS_INVALID_TYPE:
            log.error(u"'%s' is not a valid type; cannot retrieve properties for it.", typeName)
        elif result is None:
            log.error(u'IsValidTypeAndProperty wasnt able to determine if type and property were valid: %s, %s', typeName, propertyName)
        return result == IS_VALID_TYPE_AND_PROPERTY

    def GetMetaData(self, messageID, propertyName, languageID = None):
        languageID = util.StandardizedLanguageIDOrDefault(languageID)
        propertyString = self._GetMetaData(messageID, propertyName, languageID)
        if propertyString is not None:
            return uiutil.PrepareLocalizationSafeString(propertyString, messageID=messageID)
        log.error(u'a non existent property was requested. messageID,propertyName,languageID : %s,%s,%s', messageID, propertyName, languageID)
        return u'[no property:%s,%s]' % (messageID, propertyName)

    def GetPlaceholderLabel(self, englishText, **kwargs):
        tags = parser._Tokenize(englishText)
        parsedText = eveLocalization.Parse(englishText, locconst.LOCALE_SHORT_ENGLISH, tags, **kwargs)
        log.warning(u'Placeholder label (%s) needs to be replaced.', englishText)
        return '!_%s_!' % parsedText

    def _DecideLanguage(self):
        prefsValue = prefs.GetValue('languageID', None)
        if prefsValue:
            log.info(u'prefs language=%r', prefsValue)
            comfylang = langutils.any_to_comfy_language(prefsValue)
            if langutils.is_client_valid(comfylang):
                return comfylang
            log.warning(u'prefs language invalid=%r', prefsValue)
        else:
            log.info(u'no language in prefs')
        startupValue = self.GetLanguageStartupArg()
        if startupValue:
            log.info(u'startup args language=%r', startupValue)
            comfylang = langutils.any_to_comfy_language(startupValue)
            if langutils.is_client_valid(comfylang):
                return comfylang
            log.warning(u'startup args language invalid=%r', startupValue)
        else:
            log.info(u'no language in startup args')
        log.info(u'using default language=%r', langutils.DEFAULT_CLIENT_LANGUAGE.mls_language_id())
        return langutils.DEFAULT_CLIENT_LANGUAGE

    def _ValidateAndRepairPrefs(self):
        if boot.role == 'client':
            comfylang = self._DecideLanguage()
            if comfylang.mls_language_id() != prefs.GetValue('languageID', None):
                prefs.languageID = comfylang.mls_language_id()
            blue.os.languageID = comfylang.mls_language_id()

    @telemetry.ZONE_METHOD
    def _ReadMainLocalizationData(self, unPickledObject, dataType):
        if unPickledObject and self.FIELD_LABELS in unPickledObject:
            labelsDict = unPickledObject[self.FIELD_LABELS]
            for aMessageID in labelsDict:
                dataRow = labelsDict[aMessageID]
                pathAndLabelKey = None
                if dataRow[locconst.PICKLE_LABELS_FULLPATH]:
                    aFullPath = dataRow[locconst.PICKLE_LABELS_FULLPATH]
                    pathAndLabelKey = '/'.join([aFullPath, dataRow[locconst.PICKLE_LABELS_LABEL]])
                else:
                    pathAndLabelKey = dataRow[locconst.PICKLE_LABELS_LABEL]
                self.languageLabels[pathAndLabelKey.encode('ascii')] = aMessageID

        else:
            log.error(u"didn't find 'labels' in the unpickled object.")
            return []
        langList = []
        if self.FIELD_LANGUAGES in unPickledObject:
            if isinstance(unPickledObject[self.FIELD_LANGUAGES], dict):
                langList = unPickledObject[self.FIELD_LANGUAGES].keys()
            else:
                langList = unPickledObject[self.FIELD_LANGUAGES]
            langList = filter(self._IsValidLanguage, langList)
            self.languagesDefined.update(langList)
        else:
            log.error(u"didn't find 'languages' in the unpickled object")
            return []
        if self.FIELD_TYPES in unPickledObject:
            self.languageTypesWithProperties.update(unPickledObject[self.FIELD_TYPES])
        else:
            log.error(u"didn't find 'types' in the unpickled object")
            return []
        return langList

    def _IsValidLanguage(self, languageID):
        if boot.role == 'client':
            if boot.region == 'optic' and langutils.is_equal(languageID, langutils.LANG_EN):
                return True
            return langutils.is_client_valid(languageID)
        else:
            return True

    @telemetry.ZONE_METHOD
    def _ReadLanguageLocalizationData(self, aLangCode, unPickledObject, dataType):
        try:
            log.info(u'Loading all message data for language %r', aLangCode)
            eveLocalization.LoadMessageData(*unPickledObject)
        except:
            logmodule.LogException()
            for x, y in unPickledObject[1].iteritems():
                if y[2] is not None and not isinstance(y[2], dict):
                    log.error(u'%s: %r', x, y)

        return True

    @telemetry.ZONE_METHOD
    def UsePrimaryLanguageText(self):
        if self._importantNameSetting is None:
            if internalUtil.GetLanguageID() == self._primaryLanguageID:
                self._importantNameSetting = 0
            else:
                self._importantNameSetting = bilingualSettings.GetValue('localizationImportantNames')
        return self._importantNameSetting == bilingualSettings.IMPORTANT_NAME_ENGLISH

    def HighlightImportant(self):
        if self._highlightImportantSetting is None:
            if internalUtil.GetLanguageID() == self._primaryLanguageID:
                self._highlightImportantSetting = self._QaTooltipOverride()
            else:
                self._highlightImportantSetting = bilingualSettings.GetValue('localizationHighlightImportant')
        return self._highlightImportantSetting

    def UseImportantTooltip(self):
        if self._languageTooltipSetting is None:
            if internalUtil.GetLanguageID() == self._primaryLanguageID:
                self._languageTooltipSetting = self._QaTooltipOverride()
            else:
                self._languageTooltipSetting = bilingualSettings.GetValue('languageTooltip')
        return self._languageTooltipSetting

    def _QaTooltipOverride(self):
        if self._qaTooltipOverride is None:
            if internalUtil.GetLanguageID() == self._primaryLanguageID:
                self._qaTooltipOverride = qaSettings.GetValue('simulateTooltip')
            else:
                self._qaTooltipOverride
        return self._qaTooltipOverride

    def ClearImportantNameSetting(self):
        self._importantNameSetting = None
        self._highlightImportantSetting = None
        self._languageTooltipSetting = None
        self._qaTooltipOverride = None
        cfg.ReloadLocalizedNames()

    def _InitializeInternalVariables(self):
        self.hashDataDictionary = {}

    @telemetry.ZONE_METHOD
    def _InitializeTextData(self):
        self.languagesDefined = set()
        self.languageLabels = {}
        self.importantMessages = {}
        self.languageTypesWithProperties = {}
        self._primaryLanguageID = None
        self._secondaryLanguageID = None

    @telemetry.ZONE_METHOD
    def UpdateTextCache(self, messagePerLanguage, metaDataPerLanguage, labelsDict):
        for language in messagePerLanguage:
            log.info(u'Preparing to update internal text and label cache. The sizes of new data dictionaries are: %s, %s', len(messagePerLanguage.get(language, {})), len(metaDataPerLanguage.get(language, {})))
            if eveLocalization.HasLanguage(language):
                newData = {}
                for messageID, text in messagePerLanguage.get(language, {}).iteritems():
                    try:
                        metaData = None
                        ignore, metaData, ignore = eveLocalization.GetMessageDataByID(messageID, language)
                    except KeyError:
                        sys.exc_clear()

                    try:
                        newData[messageID] = (text, metaData, parser._Tokenize(text))
                    except:
                        logmodule.LogException()
                        continue

                try:
                    eveLocalization.LoadMessageData(language, newData)
                except:
                    logmodule.LogException()
                    continue

        for language in metaDataPerLanguage:
            if eveLocalization.HasLanguage(language):
                newData = {}
                for messageID, metaData in metaDataPerLanguage.get(language, {}).iteritems():
                    try:
                        text, ignore, tokens = eveLocalization.GetMessageDataByID(messageID, language)
                        newData[messageID] = (text, metaData, tokens)
                    except KeyError:
                        sys.exc_clear()

                try:
                    eveLocalization.LoadMessageData(language, newData)
                except:
                    logmodule.LogException()
                    continue

        log.info(u'Updating label cache. New data size is %s', len(labelsDict))
        for label, messageID in labelsDict.iteritems():
            self.languageLabels[label.encode('ascii')] = messageID

    def GetHashDataDictionary(self):
        return self.hashDataDictionary

    @telemetry.ZONE_METHOD
    def _ReadLocalizationMainPickle(self, pickleName, dataType):
        unPickledObject = self._LoadPickleData(pickleName, dataType)
        if unPickledObject is None:
            return []
        supportedLanguages = self._ReadMainLocalizationData(unPickledObject, dataType)
        if not supportedLanguages:
            log.error(u'Error reading main pickle file %s', pickleName)
        del unPickledObject
        return supportedLanguages

    def _GetPrimaryLanguage(self):
        return locconst.LOCALE_SHORT_ENGLISH

    def IsPrimaryLanguage(self, languageID):
        languageID = util.StandardizedLanguageIDOrDefault(languageID)
        return languageID == self._GetPrimaryLanguage()

    @telemetry.ZONE_METHOD
    def _ReadLocalizationLanguagePickles(self, prefix, supportedLanguages, dataType):
        primaryLanguage = self._GetPrimaryLanguage()
        if boot.role == 'client':
            prefsLanguage = util.StandardizedLanguageIDOrDefault(prefs.GetValue('languageID', None))
            if prefsLanguage != primaryLanguage and prefsLanguage in supportedLanguages:
                self._secondaryLanguageID = prefsLanguage
                if not (self.LoadPrimaryLanguage(prefix, dataType) and self._LoadLanguagePickle(prefix, prefsLanguage, dataType)):
                    return False
            else:
                return self.LoadPrimaryLanguage(prefix, dataType)
        elif boot.role == 'server' or boot.role == 'proxy':
            if not self.LoadPrimaryLanguage(prefix, dataType):
                return False
            for aLangCode in supportedLanguages:
                if aLangCode != self._primaryLanguageID and not self._LoadLanguagePickle(prefix, aLangCode, dataType):
                    return False

        return True

    @telemetry.ZONE_METHOD
    def _LoadLanguagePickle(self, prefix, languageID, dataType):
        unPickledObject = self._LoadPickleData(prefix + languageID + self.PICKLE_EXT, dataType)
        if unPickledObject == None:
            return False
        readStatus = self._ReadLanguageLocalizationData(languageID, unPickledObject, dataType)
        del unPickledObject
        return readStatus

    @telemetry.ZONE_METHOD
    def _LoadPickleData(self, pickleName, dataType):
        pickleFile = blue.ResFile()
        if not pickleFile.Open(pickleName):
            log.error(u'Could not load pickle file. %s appears to be missing. The localization module will not be able to access labels or texts.', pickleName)
            return None
        pickledData = pickleFile.Read()
        if not pickledData:
            pickleFile.Close()
            del pickleFile
            log.error(u'Could not read pickle data from file. %s may be corrupt. The localization module will not be able to access labels or texts.', pickleName)
            return None
        blue.statistics.EnterZone('pickle.loads')
        unPickledObject = pickle.loads(pickledData)
        blue.statistics.LeaveZone()

        @telemetry.ZONE_FUNCTION
        def md5ForFile(fin, block_size = 1048576):
            md5 = hashlib.md5()
            while True:
                data = fin.read(block_size)
                if not data:
                    break
                md5.update(data)

            return md5.digest()

        self.hashDataDictionary[pickleName] = md5ForFile(pickleFile)
        pickleFile.Close()
        del pickleFile
        del pickledData
        return unPickledObject

    def _GetRawByMessageID(self, messageID, languageID = None, **kwargs):
        languageID = util.StandardizedLanguageIDOrDefault(languageID)
        try:
            return eveLocalization.GetRawByMessageID(messageID, languageID)
        except:
            return u'[no messageid: %s]' % messageID
