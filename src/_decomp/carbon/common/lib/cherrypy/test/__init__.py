#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\cherrypy\test\__init__.py
import sys

def newexit():
    raise SystemExit('Exit called')


def setup():
    newexit._old = sys.exit
    sys.exit = newexit


def teardown():
    try:
        sys.exit = sys.exit._old
    except AttributeError:
        sys.exit = sys._exit
