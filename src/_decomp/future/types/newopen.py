#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\types\newopen.py
_builtin_open = open

class newopen(object):

    def __init__(self, fname, mode = 'r', encoding = 'utf-8'):
        self.f = _builtin_open(fname, mode)
        self.enc = encoding

    def write(self, s):
        return self.f.write(s.encode(self.enc))

    def read(self, size = -1):
        return self.f.read(size).decode(self.enc)

    def close(self):
        return self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, etype, value, traceback):
        self.f.close()
