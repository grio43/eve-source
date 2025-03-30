#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\schemas\path.py


class FsdDataPathObject(object):

    def __init__(self, name, parent = None):
        self.name = name
        self.parent = parent

    def __str__(self):
        if self.parent is not None:
            return self.parent.__str__() + self.name
        else:
            return self.name
