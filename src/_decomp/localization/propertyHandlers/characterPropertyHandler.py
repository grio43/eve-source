#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\propertyHandlers\characterPropertyHandler.py
import eveLocalization
import log
from eveprefs import boot
from localization import const as locconst
from localization.propertyHandlers.basePropertyHandler import BasePropertyHandler

class CharacterPropertyHandler(BasePropertyHandler):
    PROPERTIES = {locconst.CODE_UNIVERSAL: ('name', 'rawName', 'gender'),
     locconst.LOCALE_SHORT_ENGLISH: ('nameWithPossessive',),
     locconst.LOCALE_SHORT_FRENCH: ('nameWithPossessive',),
     locconst.LOCALE_SHORT_SPANISH: ('nameWithPossessive',),
     locconst.LOCALE_SHORT_GERMAN: ('genitiveName',),
     locconst.LOCALE_SHORT_RUSSIAN: ('genitiveName',)}
    GENDER_NORMALIZATION_MAPPING = {1: locconst.GENDER_MALE,
     0: locconst.GENDER_FEMALE}

    def _GetName(self, charID, languageID, *args, **kwargs):
        try:
            return cfg.eveowners.Get(charID).ownerName
        except KeyError:
            log.LogException()
            return '[no character: %d]' % charID

    def _GetRawName(self, charID, languageID, *args, **kwargs):
        try:
            return cfg.eveowners.Get(charID).GetRawName(languageID)
        except KeyError:
            log.LogException()
            return '[no character: %d]' % charID

    if boot.role != 'client':
        _GetName = _GetRawName

    def _GetGender(self, charID, languageID, *args, **kwargs):
        try:
            return self.GENDER_NORMALIZATION_MAPPING[cfg.eveowners.Get(charID).gender]
        except KeyError:
            log.LogException()
            return self.GENDER_NORMALIZATION_MAPPING[0]

    def _GetNameWithPossessiveEN_US(self, charID, *args, **kwargs):
        characterName = self._GetName(charID, languageID=locconst.LOCALE_SHORT_ENGLISH)
        return self._PrepareLocalizationSafeString(characterName + "'s")

    def _GetNameWithPossessiveFR(self, charID, *args, **kwargs):
        characterName = self._GetName(charID, languageID=locconst.LOCALE_SHORT_FRENCH)
        if characterName and characterName[0].lower() in u'aeiouy':
            poss = u"d'"
        else:
            poss = u'de '
        return self._PrepareLocalizationSafeString(poss + characterName)

    def _GetNameWithPossessiveES(self, charID, *args, **kwargs):
        characterName = self._GetName(charID, languageID=locconst.LOCALE_SHORT_SPANISH)
        return self._PrepareLocalizationSafeString(characterName)

    def _GetGenitiveNameDE(self, charID, *args, **kwargs):
        characterName = self._GetName(charID, languageID=locconst.LOCALE_SHORT_GERMAN)
        if characterName[-1:] not in 'sxz':
            characterName = characterName + 's'
        return self._PrepareLocalizationSafeString(characterName)

    def _GetGenitiveNameRU(self, charID, *args, **kwargs):
        characterName = self._GetName(charID, languageID=locconst.LOCALE_SHORT_RUSSIAN)
        nameWithPossessive = self._PrepareLocalizationSafeString(characterName + '[possessive]')
        return nameWithPossessive

    def Linkify(self, charID, linkText):
        try:
            charInfo = cfg.eveowners.Get(charID)
        except KeyError:
            log.LogException()
            return '[no character: %d]' % charID

        if charInfo.typeID:
            return '<a href=showinfo:%d//%d>%s</a>' % (charInfo.typeID, charID, linkText)
        else:
            return linkText


eveLocalization.RegisterPropertyHandler(eveLocalization.VARIABLE_TYPE.CHARACTER, CharacterPropertyHandler())
