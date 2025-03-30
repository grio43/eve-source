#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\forms\formValidators.py
from localization import GetByLabel
from localization.util import IsTextInConciseLanguage, IsSessionLanguageConcise
from math import ceil
import re

class BaseValidator(object):
    default_label = None

    def __init__(self, label = None):
        self.label = label

    def _get_invalid_message(self, value):
        return GetByLabel(self.label)

    def get_invalid_reason(self, value):
        raise NotImplementedError


class InputRequired(BaseValidator):

    def __init__(self, label = 'UI/Control/Form/InputRequired'):
        super(InputRequired, self).__init__(label)

    def get_invalid_reason(self, value):
        if not value:
            return self._get_invalid_message(value)


class Length(BaseValidator):

    def __init__(self, minLength = None, maxLength = None, label = None):
        super(Length, self).__init__(label)
        if minLength is None and maxLength is None:
            raise RuntimeError('Either min or max length must be provided')
        self._min_length_standard = minLength
        self._max_length_standard = maxLength
        self._min_length_concise = max(1, int(ceil(float(minLength) / 2))) if minLength else minLength
        self._max_length_concise = maxLength
        if IsSessionLanguageConcise():
            self.min_length = self._min_length_concise
            self.max_length = self._max_length_concise
        else:
            self.min_length = self._min_length_standard
            self.max_length = self._max_length_standard

    def _get_min_length_value(self, value):
        if IsTextInConciseLanguage(languageID=None, textString=value):
            return self._min_length_concise
        else:
            return self._min_length_standard

    def _get_max_length_value(self, value):
        if IsTextInConciseLanguage(languageID=None, textString=value):
            return self._max_length_concise
        else:
            return self._max_length_standard

    def _get_invalid_message(self, value):
        label = self._get_label()
        length = len(value) if value else 0
        kwargs = {'labelNameAndPath': label,
         'length': length}
        min_length_for_message = self._get_min_length_value(value)
        if min_length_for_message is not None:
            kwargs['minLength'] = min_length_for_message
        max_length_for_message = self._get_max_length_value(value)
        if max_length_for_message is not None:
            kwargs['maxLength'] = max_length_for_message
        return GetByLabel(**kwargs)

    def _get_label(self):
        if self.label:
            return self.label
        if self.min_length and self.max_length:
            return 'UI/Control/Form/LengthBetweenRequired'
        if self.min_length:
            return 'UI/Control/Form/LengthAboveRequired'
        if self.max_length:
            return 'UI/Control/Form/LengthBelowRequired'

    def get_invalid_reason(self, value):
        length = len(value) if value else 0
        min_length_for_message = self._get_min_length_value(value)
        if min_length_for_message is not None and length < min_length_for_message:
            return self._get_invalid_message(value)
        max_length_for_message = self._get_max_length_value(value)
        if max_length_for_message is not None and length > max_length_for_message:
            return self._get_invalid_message(value)


class OnlySingleWhitespaces(BaseValidator):

    def __init__(self, label = 'UI/Control/Form/OnlySingleWhitespacesAllowed'):
        super(OnlySingleWhitespaces, self).__init__(label)

    def get_invalid_reason(self, value):
        if re.findall('[\t\n\r\x0c\x0b]+|[ ]{2,}', value):
            return self._get_invalid_message(value)


class IllegalCharacters(BaseValidator):

    def __init__(self, characters = '><', label = None):
        super(IllegalCharacters, self).__init__(label)
        self.characters = characters

    def get_invalid_reason(self, value):
        chars = {c for c in value if c in self.characters}
        if chars:
            return self._get_invalid_message(chars)

    def _get_invalid_message(self, characters):
        charactersTxt = ', '.join([ self._get_char(c) for c in characters ])
        return GetByLabel('UI/Control/Form/IllegalCharacters', characters=charactersTxt)

    def _get_char(self, c):
        c = c.replace('<', '&lt;').replace('>', '&gt;')
        return "'{}'".format(c)
