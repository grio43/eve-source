#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\kiring\common\errors.py


class KiringRedeemingCodeException(Exception):

    def __init__(self, retcode = 0, message = None):
        self.message = message
        self.retcode = retcode
        Exception.__init__(self, message)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'Redeeming failed with error %s - %s' % (str(self.retcode), self.message)


class KiringRedeemingCodeNotValidException(KiringRedeemingCodeException):

    def __repr__(self):
        return 'Redeeming code is not valid, error is %s - %s' % (str(self.retcode), self.message)


class KiringRedeemingCodeUsedException(KiringRedeemingCodeException):

    def __repr__(self):
        return 'Code has already been used, error is %s - %s' % (str(self.retcode), self.message)


class KiringRedeemingCodeTypeUsedException(KiringRedeemingCodeException):

    def __repr__(self):
        return 'Offer type has already been claimed by user, error is %s - %s' % (str(self.retcode), self.message)
