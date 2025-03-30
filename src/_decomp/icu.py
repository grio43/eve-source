#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\icu.py


class ICUError(Exception):
    messages = {}

    def __str__(self):
        return '%s, error code: %d' % (self.args[1], self.args[0])

    def getErrorCode(self):
        return self.args[0]


class InvalidArgsError(Exception):
    pass


from icu_docs import *
