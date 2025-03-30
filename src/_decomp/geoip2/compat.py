#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\geoip2\compat.py
import sys
import ipaddress
if sys.version_info[0] == 2:

    def compat_ip_address(address):
        if isinstance(address, bytes):
            address = address.decode()
        return ipaddress.ip_address(address)


else:

    def compat_ip_address(address):
        return ipaddress.ip_address(address)
