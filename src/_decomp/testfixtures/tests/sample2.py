#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\testfixtures\tests\sample2.py
from testfixtures.tests.sample1 import X, z
try:
    from guppy import hpy
    guppy = True
except ImportError:
    guppy = False

def dump(path):
    if guppy:
        hpy().heap().stat.dump(path)
