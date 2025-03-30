#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\machoNetExceptions.py
from stringutil import strx

class MachoException(StandardError):
    __guid__ = 'exceptions.MachoException'

    def __init__(self, payload = None):
        self.payload = payload

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '<%s: payload=%s>' % (self.__class__.__name__, self.payload)


class UberMachoException(MachoException):
    __guid__ = 'exceptions.UberMachoException'

    def __init__(self, payload = None):
        MachoException.__init__(self, payload)

    def __repr__(self):
        payload = []
        for each in self.payload:
            try:
                if each[0]:
                    payload.append('%d: %s' % (each[1], strx(each[2]) + strx(getattr(each[2], '__dict__', ''))))
            except:
                payload.append(repr(each))

        return '<%s: payload=%s>' % (self.__class__.__name__, strx(payload))


class MachoWrappedException(MachoException):
    __guid__ = 'exceptions.MachoWrappedException'

    def __init__(self, payload = None):
        MachoException.__init__(self, payload)


class UnMachoDestination(MachoException):
    __guid__ = 'exceptions.UnMachoDestination'

    def __init__(self, payload = None):
        MachoException.__init__(self, payload)


class UnMachoChannel(MachoException):
    __guid__ = 'exceptions.UnMachoChannel'

    def __init__(self, payload = None):
        MachoException.__init__(self, payload)


class WrongMachoNode(MachoException):
    __guid__ = 'exceptions.WrongMachoNode'
    __passbyvalue__ = 1

    def __init__(self, payload = None):
        MachoException.__init__(self, payload)


class ProxyRedirect(MachoException):
    __guid__ = 'exceptions.ProxyRedirect'
    __passbyvalue__ = 1

    def __init__(self, payload = None, **keywords):
        MachoException.__init__(self, payload)
        self.extra = keywords


class SessionUnavailable(MachoException):
    __guid__ = 'exceptions.SessionUnavailable'
    __passbyvalue__ = 1

    def __init__(self, payload = None):
        MachoException.__init__(self, payload)


class UserRejectedByVIP(MachoException):
    __guid__ = 'exceptions.UserRejectedByVIP'
