#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\http.py
import cherrypy
from carbon.common.script.net import machoNet
from eveprefs import prefs

def Referer():
    request = cherrypy.request
    return request.headers.get('Referer', '')


def Host():
    request = cherrypy.request
    host = request.headers.get('X-Forwarded-Host', '')
    if not host:
        host = request.headers.get('Host', '')
    return host


def AddHeader(headerKey, headerValue):
    response = cherrypy.response
    response.headers[headerKey] = headerValue


def ESPUrl(session, polarisID = None):
    if machoNet.mode == 'proxy':
        if polarisID is None:
            polarisID = session.ConnectToSolServerService('DB2').CallProc('zcluster.Nodes_PolarisID')
    elif polarisID is None:
        polarisID = sm.GetService('DB2').CallProc('zcluster.Nodes_PolarisID')
    if cherrypy.request.app is None:
        if sm.IsServiceRunning('tcpRawProxyService'):
            tcpproxy = sm.services['tcpRawProxyService']
        else:
            proxyID = sm.services['machoNet'].GetConnectedProxyNodes()[0]
            tcpproxy = sm.StartService('debug').session.ConnectToRemoteService('tcpRawProxyService', proxyID)
        host, ports = tcpproxy.GetESPTunnelingAddressByNodeID()
        port = ports.get(polarisID)
        return 'http://%s:%s' % (host, port)
    machoNetSvc = session.ConnectToProxyServerService('machoNet', polarisID)
    transport_key = 'tcp:raw:http2' if prefs.GetValue('httpServerMode', 'ccp').lower() == 'ccp' else 'tcp:raw:http'
    host, port = machoNetSvc.GetConnectionProperties()['internaladdress'].split(':')
    refHost = Host().split(':')[0]
    if refHost == 'localhost':
        host = refHost
    sub_number = 1 if cherrypy.request.app else 2
    port = int(port) + machoNet.offsetMap[machoNet.mode][transport_key] - sub_number
    return 'http://%s:%s' % (host, port)
