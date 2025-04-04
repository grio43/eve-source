#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dateutil\_common.py


class weekday(object):
    __slots__ = ['weekday', 'n']

    def __init__(self, weekday, n = None):
        self.weekday = weekday
        self.n = n

    def __call__(self, n):
        if n == self.n:
            return self
        else:
            return self.__class__(self.weekday, n)

    def __eq__(self, other):
        try:
            if self.weekday != other.weekday or self.n != other.n:
                return False
        except AttributeError:
            return False

        return True

    __hash__ = None

    def __repr__(self):
        s = ('MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU')[self.weekday]
        if not self.n:
            return s
        else:
            return '%s(%+d)' % (s, self.n)
