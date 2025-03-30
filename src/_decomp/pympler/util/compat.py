#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pympler\util\compat.py
import sys
try:
    from StringIO import StringIO
    BytesIO = StringIO
except ImportError:
    from io import StringIO, BytesIO

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    from new import instancemethod
except ImportError:

    def instancemethod(*args):
        return args[0]


try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection

try:
    from urllib2 import Request, urlopen, URLError
except ImportError:
    from urllib.request import Request, urlopen
    from urllib.error import URLError

try:
    from json import dumps
except ImportError:
    try:
        from simplejson import dumps
    except ImportError:
        dumps = lambda s: unicode(s)

try:
    import Tkinter as tkinter
except ImportError:
    try:
        import tkinter
    except ImportError:
        tkinter = None

encode4pipe = lambda s: s
if sys.hexversion >= 50331648:
    encode4pipe = lambda s: s.encode()

def object_in_list(obj, l):
    for o in l:
        if o is obj:
            return True

    return False
