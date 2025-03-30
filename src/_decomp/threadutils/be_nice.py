#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\threadutils\be_nice.py
try:
    import blue
    _be_nice_impl = blue.pyos.BeNice
except ImportError:
    _be_nice_impl = None

def be_nice(interval_ms = 15):
    if _be_nice_impl:
        _be_nice_impl(interval_ms)


def be_nice_iter(interval_ms, sequence):
    for item in sequence:
        yield item
        be_nice(interval_ms)
