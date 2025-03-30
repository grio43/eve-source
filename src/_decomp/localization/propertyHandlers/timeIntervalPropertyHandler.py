#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\propertyHandlers\timeIntervalPropertyHandler.py
import eveLocalization
from localization import const as locconst, formatters
from localization.logger import LogError
from localization.propertyHandlers.basePropertyHandler import BasePropertyHandler

class TimeIntervalPropertyHandler(BasePropertyHandler):
    PROPERTIES = {locconst.CODE_UNIVERSAL: ('shortForm', 'shortWrittenForm', 'writtenForm', 'writtenFormTwoPart')}

    def _GetWrittenFormTwoPart(self, value, languageID, *args, **kwargs):
        kwargs = self._GetToFromArgs(kwargs)
        kwargs['languageID'] = languageID
        kwargs['maxParts'] = 2
        try:
            timeIntervalString = formatters.FormatTimeIntervalWritten(value, **kwargs)
            return timeIntervalString
        except ValueError as e:
            LogError(e)

    def _GetShortForm(self, value, languageID, *args, **kwargs):
        kwargs = self._GetToFromArgs(kwargs)
        try:
            timeIntervalString = formatters.FormatTimeIntervalShort(value, **kwargs)
            return timeIntervalString
        except ValueError as e:
            LogError(e)

    def _GetShortWrittenForm(self, value, languageID, *args, **kwargs):
        kwargs = self._GetToFromArgs(kwargs)
        try:
            timeIntervalString = formatters.FormatTimeIntervalShortWritten(value, **kwargs)
            return timeIntervalString
        except ValueError as e:
            LogError(e)

    def _GetWrittenForm(self, value, languageID, *args, **kwargs):
        kwargs = self._GetToFromArgs(kwargs)
        kwargs['languageID'] = languageID
        try:
            timeIntervalString = formatters.FormatTimeIntervalWritten(value, **kwargs)
            return timeIntervalString
        except ValueError as e:
            LogError(e)

    def _GetDefault(self, value, languageID, *args, **kwargs):
        return self._GetShortForm(value, languageID, *args, **kwargs)

    def _GetToFromArgs(self, kwargs):
        fromMark = kwargs.get('from', None)
        toMark = kwargs.get('to', None)
        kwargs = {}
        if fromMark:
            kwargs['showFrom'] = fromMark
        if toMark:
            kwargs['showTo'] = toMark
        return kwargs


eveLocalization.RegisterPropertyHandler(eveLocalization.VARIABLE_TYPE.TIMEINTERVAL, TimeIntervalPropertyHandler())
