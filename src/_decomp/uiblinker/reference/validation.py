#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\reference\validation.py
import textwrap

class Severity(object):
    warning = 'W'
    error = 'E'


class Validation(object):

    def __init__(self, severity, validation_id, message):
        self._severity = severity
        self._id = validation_id
        self._message = message

    @property
    def severity(self):
        return self._severity

    @property
    def is_error(self):
        return self._severity == Severity.error

    @property
    def is_warning(self):
        return self._severity == Severity.warning

    @property
    def message(self):
        return self._message

    @property
    def code(self):
        return '{}{:0>3}'.format(self.severity, self._id)

    def __str__(self):
        return self.message

    def __eq__(self, other):
        return self is other or isinstance(other, Validation) and self._severity == other._severity and self._id == other._id


class ValidationError(ValueError):

    def __init__(self, path, errors):
        self.path = path
        self.errors = errors
        template = '{count} error(s) for path "{path}":\n\n{errors}'
        error_messages = '\n\n'.join([ textwrap.fill(e.message, width=80) for e in errors ])
        super(ValidationError, self).__init__(template.format(count=len(errors), path=path, errors=error_messages))


SURROUNDING_WHITESPACE = Validation(Severity.warning, 1, 'The path has additional whitespace around it.')
EMPTY_PATH = Validation(Severity.error, 1, 'The path is empty.')
LEADING_SLASH = Validation(Severity.error, 3, "The path should not start with a '/'.")
TRAILING_SLASH = Validation(Severity.error, 4, "The path should not end with a '/'.")
