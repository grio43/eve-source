#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\profiling.py
import gc
import sys
import weakref
import zlib
import blue
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER, ROLE_SERVICE

def CalcMemoryUsage(what, iterations = 1):
    if session and session.role & (ROLE_PROGRAMMER | ROLE_SERVICE) == 0:
        raise RuntimeError('Requires role programmer')
    iterations = max(1, iterations)
    iterations = min(iterations, 10)
    enabled = gc.isenabled()
    if enabled:
        gc.disable()
    oldWhitelist = blue.marshal.globalsWhitelist.copy()
    blue.marshal.globalsWhitelist.clear()
    oldCollectWhitelist = blue.marshal.collectWhitelist
    blue.marshal.collectWhitelist = True
    try:
        zippedSum = pickleSum = changeSum = 0
        for i in xrange(iterations):
            pickle = blue.marshal.Save(what)
            zipped = zlib.compress(pickle)
            before = sys.getpymalloced()
            unpickled = blue.marshal.Load(pickle)
            after = sys.getpymalloced()
            pickleSum += len(pickle)
            zippedSum += len(zipped)
            changeSum += after - before

        denominator = float(iterations)
        return (pickleSum / denominator, zippedSum / denominator, changeSum / denominator)
    finally:
        if enabled:
            gc.enable()
        blue.marshal.globalsWhitelist.clear()
        blue.marshal.globalsWhitelist.update(oldWhitelist)
        blue.marshal.collectWhitelist = oldCollectWhitelist


class RefTracker(object):

    def __init__(self):
        if not hasattr(self.__class__, 'instanceIndex'):
            self.__class__.instanceIndex = {}
        self.__class__.instanceIndex[id(self)] = weakref.ref(self)

    def __del__(self):
        del self.__class__.instanceIndex[id(self)]


def CheckSM():
    ignorableForROLE_SERVICE = ['genderID',
     'bloodlineID',
     'languageID',
     'rolesAtHQ',
     'wingid',
     'constellationid',
     'regionid',
     'fleetid',
     'rolesAtAll',
     'rolesAtBase',
     'hqID',
     'locationid',
     'shipid',
     'rolesAtOther',
     'squadid',
     'raceID',
     'gangrole',
     'solarsystemid',
     'charid',
     'corprole',
     'corpid',
     'userid',
     'stationid',
     'allianceid',
     'solarsystemid2']
    print '\nChecking sm.services for leaked sessions\n'
    for serviceName, serviceObject in sm.services.iteritems():
        if not hasattr(serviceObject, 'boundObjects'):
            continue
        if 0 == len(serviceObject.boundObjects):
            continue
        print 'Checking: %s' % serviceName
        for boundObject in serviceObject.boundObjects.itervalues():
            print '\n    ', str(boundObject), '\n    ' + '=' * len(str(boundObject))
            print '    Object Connections:'
            for connectionList in [ d.values for d in boundObject.objectConnections.itervalues() ]:
                for obj in connectionList:
                    if obj.__session__:
                        print '        __session__ roles: ', obj.__session__.role
                    print '        ', obj.__dict__

            print '    Session Connections:'
            for sess in boundObject.sessionConnections.itervalues():
                print '        session roles: ', sess.role
                for k, v in sess.__dict__.iteritems():
                    if k == 'connectedObjects':
                        print '        ', k, ':'
                        for someID, connection in v.iteritems():
                            print '            ', someID, ':', connection

                    else:
                        if sess.role & ROLE_SERVICE:
                            if k in ignorableForROLE_SERVICE:
                                continue
                        print '        ', k, ': ', v

        print
