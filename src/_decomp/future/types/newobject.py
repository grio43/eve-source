#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\types\newobject.py


class newobject(object):

    def next(self):
        if hasattr(self, '__next__'):
            return type(self).__next__(self)
        raise TypeError('newobject is not an iterator')

    def __unicode__(self):
        if hasattr(self, '__str__'):
            s = type(self).__str__(self)
        else:
            s = str(self)
        if isinstance(s, unicode):
            return s
        else:
            return s.decode('utf-8')

    def __nonzero__(self):
        if hasattr(self, '__bool__'):
            return type(self).__bool__(self)
        if hasattr(self, '__len__'):
            return type(self).__len__(self)
        return True

    def __long__(self):
        if not hasattr(self, '__int__'):
            return NotImplemented
        return self.__int__()

    def __native__(self):
        return object(self)

    __slots__ = []


__all__ = ['newobject']
