#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\builtinmangler.py
import __builtin__
import inspect
import logging
import sys
import stringutil
L = logging.getLogger(__name__)
L.addHandler(logging.NullHandler())

class NamespaceFailedException(ImportError):

    def __init__(self, *args):
        ImportError.__init__(self, *args)

    def __repr__(self):
        return 'NamespaceFailed: The namespace ' + self.args[0] + ' was not found.'


def _SmashConst(constmodule):
    __builtin__.const = constmodule
    sys.modules['const'] = constmodule
    for name, value in constmodule.__dict__.iteritems():
        if not name.startswith('__'):
            if name not in __builtin__.const.__dict__:
                __builtin__.const.__dict__[name] = value
            elif inspect.ismodule(value):
                for moduleKey, moduleValue in value.__dict__.iteritems():
                    if not moduleKey.startswith('__'):
                        setattr(__builtin__.const.__dict__[name], moduleKey, moduleValue)


def add_system_module_extras():
    extras = _get_system_module_extras()
    for module_name, entries in extras.iteritems():
        module = __import__(module_name)
        for name, value in entries.iteritems():
            setattr(module, name, value)


def _get_system_module_extras():
    from eve.common.script.sys.strangeStrings import A, AgentString, AgentUnicode
    from carbon.common.lib.ccp_exceptions import ConnectionError, RoleNotAssignedError, SQLError, UnmarshalError, UserError
    from carbon.common.script.net.GPSExceptions import GPSAddressOccupied, GPSBadAddress, GPSException, GPSRemoteTransportClosed, GPSTransportClosed
    from carbon.common.script.net.machoNetExceptions import MachoException, MachoWrappedException, ProxyRedirect, SessionUnavailable, UberMachoException, UnMachoChannel, UnMachoDestination, WrongMachoNode
    return {'sys': {'A': A,
             'AgentString': AgentString,
             'AgentUnicode': AgentUnicode},
     'exceptions': {'ConnectionError': ConnectionError,
                    'RoleNotAssignedError': RoleNotAssignedError,
                    'SQLError': SQLError,
                    'UnmarshalError': UnmarshalError,
                    'UserError': UserError,
                    'GPSAddressOccupied': GPSAddressOccupied,
                    'GPSBadAddress': GPSBadAddress,
                    'GPSException': GPSException,
                    'GPSRemoteTransportClosed': GPSRemoteTransportClosed,
                    'GPSTransportClosed': GPSTransportClosed,
                    'MachoException': MachoException,
                    'MachoWrappedException': MachoWrappedException,
                    'ProxyRedirect': ProxyRedirect,
                    'SessionUnavailable': SessionUnavailable,
                    'UberMachoException': UberMachoException,
                    'UnMachoChannel': UnMachoChannel,
                    'UnMachoDestination': UnMachoDestination,
                    'WrongMachoNode': WrongMachoNode}}


__CONSTSMANGLED = False

def MangleBuiltins():
    global __CONSTSMANGLED
    if __CONSTSMANGLED:
        return
    import eveexceptions
    __builtin__.UserError = eveexceptions.UserError
    __builtin__.SQLError = eveexceptions.SQLError
    __builtin__.ConnectionError = eveexceptions.ConnectionError
    __builtin__.UnmarshalError = eveexceptions.UnmarshalError
    __builtin__.RoleNotAssignedError = eveexceptions.RoleNotAssignedError
    __builtin__.CreateInstance = CreateInstance
    __builtin__.strx = stringutil.strx
    import eve.common.lib.appConst as appConst
    _SmashConst(appConst)
    __builtin__.SEC = const.SEC
    __builtin__.MIN = const.MIN
    __builtin__.HOUR = const.HOUR
    __builtin__.DAY = const.DAY
    __builtin__.WEEK = const.WEEK
    __builtin__.MONTH = const.MONTH30
    __builtin__.YEAR = const.YEAR360
    __builtin__.DATE = const.UE_DATE
    __builtin__.TIME = const.UE_TIME
    __builtin__.OWNERID = const.UE_OWNERID
    __builtin__.LOCID = const.UE_LOCID
    __builtin__.TYPEID = const.UE_TYPEID
    __builtin__.GROUPID = const.UE_GROUPID
    __builtin__.CATID = const.UE_CATID
    __builtin__.DIST = const.UE_DIST
    __builtin__.ISK = const.UE_ISK
    __builtin__.AUR = const.UE_AUR
    __CONSTSMANGLED = True


def CreateInstance(guid, arguments = ()):
    try:
        namespace, typename = guid.rsplit('.', 1)
    except:
        raise RuntimeError("InvalidClassID (%s), should be like 'ns.Class'" % stringutil.strx(guid))

    module = __import__(namespace, fromlist=[typename])
    ctor = getattr(module, typename)
    ret = ctor(*arguments)
    for each in getattr(ret, '__persistvars__', []):
        if not hasattr(ret, each):
            setattr(ret, each, None)

    for each in getattr(ret, '__nonpersistvars__', []):
        if not hasattr(ret, each):
            setattr(ret, each, None)

    return ret
