#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveicon\iterate.py
from eveicon import icons

def iter_icons():
    for name in icons.__all__:
        yield getattr(icons, name)
