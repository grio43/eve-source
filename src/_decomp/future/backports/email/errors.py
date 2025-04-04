#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\backports\email\errors.py
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future.builtins import super

class MessageError(Exception):
    pass


class MessageParseError(MessageError):
    pass


class HeaderParseError(MessageParseError):
    pass


class BoundaryError(MessageParseError):
    pass


class MultipartConversionError(MessageError, TypeError):
    pass


class CharsetError(MessageError):
    pass


class MessageDefect(ValueError):

    def __init__(self, line = None):
        if line is not None:
            super().__init__(line)
        self.line = line


class NoBoundaryInMultipartDefect(MessageDefect):
    pass


class StartBoundaryNotFoundDefect(MessageDefect):
    pass


class CloseBoundaryNotFoundDefect(MessageDefect):
    pass


class FirstHeaderLineIsContinuationDefect(MessageDefect):
    pass


class MisplacedEnvelopeHeaderDefect(MessageDefect):
    pass


class MissingHeaderBodySeparatorDefect(MessageDefect):
    pass


MalformedHeaderDefect = MissingHeaderBodySeparatorDefect

class MultipartInvariantViolationDefect(MessageDefect):
    pass


class InvalidMultipartContentTransferEncodingDefect(MessageDefect):
    pass


class UndecodableBytesDefect(MessageDefect):
    pass


class InvalidBase64PaddingDefect(MessageDefect):
    pass


class InvalidBase64CharactersDefect(MessageDefect):
    pass


class HeaderDefect(MessageDefect):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)


class InvalidHeaderDefect(HeaderDefect):
    pass


class HeaderMissingRequiredValue(HeaderDefect):
    pass


class NonPrintableDefect(HeaderDefect):

    def __init__(self, non_printables):
        super().__init__(non_printables)
        self.non_printables = non_printables

    def __str__(self):
        return u'the following ASCII non-printables found in header: {}'.format(self.non_printables)


class ObsoleteHeaderDefect(HeaderDefect):
    pass


class NonASCIILocalPartDefect(HeaderDefect):
    pass
