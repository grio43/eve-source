#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\goals\common\errors.py


class ContributionMethodTypeNotSupported(RuntimeError):

    def __init__(self, message):
        super(RuntimeError, self).__init__(self)
        self.message = message

    def __str__(self):
        return self.message
