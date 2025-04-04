#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\bunch.py


class Bunch(dict):

    def __repr__(self):
        return '%s %s: %s' % (self.get('__doc__', None) or 'Anonymous', self.__class__.__name__, dict.__repr__(self))

    __delattr__ = dict.__delitem__

    def Copy(self):
        return Bunch(self.copy())

    def Set(self, key, val):
        self[key] = val

    __setattr__ = Set

    def Get(self, key, defaultValue = None):
        return self.get(key, defaultValue)

    __getattr__ = Get

    def _JessicaGetMembersAndMethods(self):
        return ([], [])

    def _JessicaAttrPanelIgnore(self):
        return False
