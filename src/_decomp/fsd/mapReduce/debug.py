#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\mapReduce\debug.py


class FakeProcessPool(object):

    def __init__(self):
        pass

    def imap_unordered(self, fn, iterable, batchSize):
        for i in iterable:
            yield fn(i)

    def close(self):
        pass
