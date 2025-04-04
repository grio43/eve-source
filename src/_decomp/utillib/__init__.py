#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\utillib\__init__.py
import collections
import os
import sys
from collections import defaultdict
import blue

class KeyVal:
    __passbyvalue__ = 1

    def __init__(self, dictLikeObject = None, **kw):
        self.__dict__ = kw
        if dictLikeObject is not None:
            if isinstance(dictLikeObject, dict):
                self.__dict__.update(dictLikeObject)
            elif isinstance(dictLikeObject, blue.DBRow):
                for k in dictLikeObject.__keys__:
                    self.__dict__[k] = getattr(dictLikeObject, k)

            elif isinstance(dictLikeObject, KeyVal):
                self.__dict__.update(dictLikeObject.__dict__)
            else:
                raise TypeError("KeyVal can only be initialized with dictionaries, key/value pairs or blue.DBRow's. %s isn't one of them." % type(dictLikeObject))

    def _get_class_name(self):
        return self.__class__.__name__

    def __str__(self):
        members = dict(filter(lambda (k, v): not k.startswith('__'), self.__dict__.items()))
        return '%s: %s' % (self._get_class_name(), members)

    def __repr__(self):
        return '<%s>' % str(self)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __delitem__(self, key):
        del self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def update(self, other):
        self.__dict__.update(other)

    def copy(self):
        ret = KeyVal()
        ret.__dict__.update(self.__dict__)
        return ret

    def get(self, key, defval = None):
        return self.__dict__.get(key, defval)

    def Get(self, key, defval = None):
        return self.__dict__.get(key, defval)

    def Set(self, key, value):
        self.__dict__[key] = value


class keydefaultdict(defaultdict):

    def __missing__(self, key):
        ret = self[key] = self.default_factory(key)
        return ret


def strx(o):
    try:
        return str(o)
    except UnicodeEncodeError:
        sys.exc_clear()
        return unicode(o).encode('ascii', 'replace')


def GetClientUniqueFolderName():
    path = os.path.normpath(blue.paths.ResolvePath(u'app:/').lower())
    path = path.replace('/', '_').replace('\\', '_').replace(':', '').replace(' ', '_')
    path += u'_' + GetServerNameForSettingsFolder()
    return path


def GetServerNameForSettingsFolder():
    name = GetServerName().lower().replace(' ', '_')
    if name.endswith('.servers.eveonline.com'):
        name = name.split('.')[0]
    return name


def GetServerName():
    from eveprefs import prefs, boot
    serverName = boot.GetValue('server', '')
    if prefs:
        serverName = prefs.GetValue('server', serverName)
    for arg in blue.pyos.GetArg():
        if arg.startswith('/server:'):
            serverName = arg.split(':')[1]

    return serverName


def GetServerPort():
    from eveprefs import prefs, boot
    serverPort = boot.GetValue('port', '')
    if prefs:
        serverPort = prefs.GetValue('port', serverPort)
    for arg in blue.pyos.GetArg():
        if arg.startswith('/port:'):
            serverPort = arg.split(':')[1]

    return int(serverPort)


def GetLoginCredentials():
    for arg in blue.pyos.GetArg()[1:]:
        if arg.startswith('/login:'):
            argParts = arg.split(':')[1:]
            if len(argParts) != 2:
                raise RuntimeError('Format of login parameter incorrect, should be /login:<user>:<password>')
            return argParts


class DAG(object):

    def __init__(self):
        self.graph = collections.defaultdict(lambda : (set(), set()))

    def AddNode(self, node):
        self.graph[node]

    def InsertEdge(self, A, B):
        self.graph[A][0].add(B)
        self.graph[B][1].add(A)

    def RemoveEdge(self, A, B):
        self.graph[A][0].remove(B)
        self.graph[B][1].remove(A)

    def RemoveNode(self, N, stitch = True):
        connections = self.graph[N]
        del self.graph[N]
        for out in connections[0]:
            self.graph[out][1].remove(N)

        for inc in connections[1]:
            self.graph[inc][0].remove(N)

        if stitch:
            for out in connections[0]:
                self.graph[out][1].update(connections[1])

            for inc in connections[1]:
                self.graph[inc][0].update(connections[0])

    def Invert(self):
        for k, v in self.graph.items():
            self.graph[k] = (v[1], v[0])

    def Leaves(self):
        return [ k for k, v in self.graph.iteritems() if not v[0] ]

    def __str__(self):
        return self.graph.__str__()

    def ToDot(self):
        retStr = 'digraph graphname {\n'
        for k, v in self.graph.iteritems():
            for dep in v[0]:
                retStr += '%s -> %s\n' % (k, dep)

        retStr += '}'
        return retStr

    def _ListAllCyclesRec(self, k, v, doneStack, currentStack, detectedCycles):
        if k in doneStack:
            return
        if k in currentStack:
            t = currentStack[currentStack.index(k):]
            t.append(k)
            detectedCycles.append(t)
            return
        currentStack.append(k)
        for each in v[0]:
            self._ListAllCyclesRec(each, self.graph[each], doneStack, currentStack, detectedCycles)

        currentStack.pop()
        doneStack.append(k)

    def ListAllCycles(self):
        doneStack = []
        currentStack = []
        detectedCycles = []
        for k, v in self.graph.iteritems():
            if k not in doneStack:
                self._ListAllCyclesRec(k, v, doneStack, currentStack, detectedCycles)

        return detectedCycles
