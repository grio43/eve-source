#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\dogstatsd\route.py
import socket
import struct

class UnresolvableDefaultRoute(Exception):
    pass


def get_default_route():
    try:
        with open('/proc/net/route') as f:
            for line in f.readlines():
                fields = line.strip().split()
                if fields[1] == '00000000':
                    return socket.inet_ntoa(struct.pack('<L', int(fields[2], 16)))

    except IOError:
        raise NotImplementedError(u'Unable to open `/proc/net/route`. `use_default_route` option is available on Linux only.')

    raise UnresolvableDefaultRoute(u"Unable to resolve the system default's route.")
