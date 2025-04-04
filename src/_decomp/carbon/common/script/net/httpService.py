#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\httpService.py
import StringIO
import binascii
import cStringIO
import cgi
import logging
import os
import sys
import time
import traceback
import urllib
import uuid
import blue
import bluepy
import carbon.common.script.net.machobase as macho
import carbon.common.script.util.htmlwriter as htmlwriter
import evecrypto.crypto as Crypto
import iocp
import log
import typeutils
import uthread
import utillib
from caching.memoize import Memoize
from carbon.common.script.net import GPSExceptions
from carbon.common.script.net import machoNetExceptions
from carbon.common.script.sys import basesession
from carbon.common.script.sys.service import CoreService, Service
from carbon.common.script.sys.serviceConst import ROLE_ADMIN, ROLE_PROGRAMMER, ROLE_SERVICE, SERVICE_RUNNING, SERVICE_STOPPED, SERVICE_STOP_PENDING
from carbon.common.script.util.timerstuff import ClockThis
from carbon.common.script.util.format import PasswordString
from carbon.common.lib import const
from eveexceptions import SQLError, UserError
from requests import structures
from scriber import httputils
from eveprefs import prefs, boot
from stdlogutils import LineWrap
httplog = logging.getLogger('httplog')
svclog = logging.getLogger('svc.http')
DB_SETTING_CACHE_TIMEOUT = 10
if macho.mode == 'proxy':
    DB_SETTING_CACHE_TIMEOUT = 60

class HeaderDict(structures.CaseInsensitiveDict):

    def has_key(self, key):
        return key in self


class AuthError(RuntimeError):
    pass


class UnknownProtocol(RuntimeError):
    pass


class UnknownVerb(RuntimeError):
    pass


class Request():

    def __init__(self, httpService, ep):
        self.httpService = httpService
        self.ep = ep
        self.buff = ''
        self.start_time = time.time()
        self.header = HeaderDict()
        self.query = {}
        self.form = {}
        self.formfields = None
        self.cookie = {}
        self.totalBytes = 0
        self.path = ''
        self.full_path = ''
        self.paths = []
        self.method = ''
        self.proto = ''
        self.args = ''
        self.raw = ''
        self.tunnelinfo = None
        self.client_ip = ''
        self.uid = ''
        self.host = ''
        self.session = None
        self.node_id = 0
        self.via_node_id = 0
        self.macho_mode = ''

    def ClientCertificate(self, key):
        return None

    def FullPath(self):
        page = self.path + '?'
        for k, v in self.query.iteritems():
            if k:
                page += '%s=%s&' % (k, v)

        return page

    def Cookies(self, cookie):
        return self.cookie[cookie]

    def Form(self, element):
        if not self.form.has_key(element):
            return None
        return htmlwriter.Pythonize(self.form[element])

    def FormItems(self):
        return dict(((k, htmlwriter.Pythonize(v)) for k, v in self.form.items()))

    def FormCheck(self, element):
        if self.Form(element) == 'on':
            return 1
        return 0

    def QueryStrings(self, raw = False):
        ret = {}
        for k, v in self.query.iteritems():
            if raw:
                ret[k] = v
            else:
                ret[k] = htmlwriter.Pythonize(v)

        return ret

    def QueryString(self, variable, caseInsensitive = False, raw = False, default = None):
        if caseInsensitive:
            variable = variable.lower()
            for k, v in self.query.iteritems():
                if k.lower() == variable:
                    if not raw:
                        return htmlwriter.Pythonize(v)
                    return v

        elif self.query.has_key(variable):
            v = self.query[variable]
            if not raw:
                return htmlwriter.Pythonize(v)
            return v
        return default

    def ServerVariables(self, env):
        if env == 'SERVER_SOFTWARE':
            return 'CCP Server Pages 1.0'
        elif env == 'SERVER_PORT':
            return 'Is this being used?'
        elif self.header.has_key(env):
            return self.header[env]
        else:
            return None

    def ReadRequest(self):
        chunks = [self.buff]
        while True:
            end = chunks[-1].find('\r\n\r\n')
            if end >= 0:
                break
            chunks.append(self.ep.Read())

        end += 4
        tail = chunks[-1]
        chunks[-1] = tail[:end]
        tail = tail[end:]
        head = ''.join(chunks)
        lines = head.split('\r\n')
        if macho.mode == 'server' and lines[0].startswith('TUNNEL ') and lines[0].endswith(' TCPTUNNEL/1.0') and self.tunnelinfo is None:
            proto, info, version = lines[0].split(' ')
            self.tunnelinfo = blue.marshal.Load(binascii.a2b_hex(info))
            setattr(self.ep, '_tunnelinfo', self.tunnelinfo)
            lines.pop(0)
        else:
            self.tunnelinfo = getattr(self.ep, '_tunnelinfo', None)
        headers = HeaderDict()
        for line in lines[1:]:
            try:
                key, val = line.split(':', 1)
            except ValueError:
                continue

            headers[key] = val.strip()

        cl = typeutils.int_eval(headers.get('Content-Length', 0), 0)
        if cl:
            got = len(tail)
            chunks = [tail]
            while got < cl:
                missing = cl - got
                ask = min(missing, 4096)
                get = self.ep.Read(ask)
                got += len(get)
                chunks.append(get)

            content = ''.join(chunks)
            tail = content[cl:]
            content = content[:cl]
        else:
            content = ''
        self.host = headers.get('host', '')
        self.node_id = self.httpService.machoNet.GetNodeID()
        self.macho_mode = macho.mode
        if self.tunnelinfo:
            if 'requesterIP' in self.tunnelinfo:
                if 'x-forwarded-for' in headers:
                    headers['x-forwarded-for'] = '%s, %s' % (headers['x-forwarded-for'], self.tunnelinfo['requesterIP'])
                else:
                    headers['x-forwarded-for'] = self.tunnelinfo['requesterIP']
                self.client_ip = self.tunnelinfo['requesterIP']
            if 'nodeID' in self.tunnelinfo:
                self.via_node_id = self.tunnelinfo['nodeID']
        else:
            try:
                self.via_node_id = self.node_id
                self.client_ip = self.ep.socket.getpeername()[0]
            except Exception:
                pass

        self.buff = tail
        return (lines[0],
         headers,
         head,
         content)

    def ParseHeader(self):
        request, self.header, head, body = self.ReadRequest()
        self.raw = ''.join((head, body))
        line = request
        sp = line.find(' ')
        self.method = line[:sp]
        self.proto = line[-9:].strip()
        if self.proto not in ('HTTP/1.0', 'HTTP/1.1'):
            raise UnknownProtocol(self.proto)
        if self.method not in ('GET', 'POST', 'HEAD', 'OPTIONS'):
            raise UnknownVerb(self.method)
        self.full_path = line[sp + 1:-9]
        self.path = self.full_path
        argidx = self.path.find('?')
        if argidx != -1:
            self.args = self.path[argidx + 1:]
            self.path = self.path[:argidx]
            htmlwriter.SplitArgs(self.args, self.query)
        else:
            import urllib
            self.path = urllib.unquote_plus(self.path)
        if self.path.startswith('/'):
            self.paths = self.path[1:].split('/')
        else:
            self.paths = []
        if self.header.has_key('Cookie'):
            cookies = self.header['Cookie']
            for cookie in cookies.split(';'):
                kv = cookie.split('=', 1)
                if len(kv) == 2:
                    self.cookie[kv[0].strip()] = kv[1].strip()

        if self.httpService.httpLog:
            if self.httpService.logChannel.IsOpen(1):
                for y in utillib.strx(self.buff[:-4]).split('\n'):
                    for l in LineWrap(y.replace('\r', ''), maxlines=0, maxlen=80, pfx=''):
                        self.httpService.LogMethodCall('HTTP INPUT: ', l)

        if 'Expect' in self.header and self.header['Expect'].lower().strip().find('100-continue') >= 0:
            self.ep.Write('HTTP/1.1 100 Continue\r\n\r\n')
            if self.httpService.httpLog:
                self.httpService.LogMethodCall('HTTP OUTPUT: HTTP/1.1 100 Continue')
                self.httpService.LogMethodCall('HTTP OUTPUT: ')
        if self.method == 'POST':
            form = body
            if form:
                if self.httpService.httpLog:
                    if self.httpService.logChannel.IsOpen(1):
                        for y in utillib.strx(form).split('\n'):
                            for l in LineWrap(y.replace('\r', ''), maxlines=0, maxlen=80, pfx=''):
                                self.httpService.LogMethodCall('HTTP INPUT: ', l)

                if self.header['Content-Type'].find('multipart/form-data') == -1:
                    htmlwriter.SplitArgs(form, self.form)
                else:
                    hd, body = head, body
                    req, hd = hd.split('\r\n', 1)
                    headers = hd.split('\r\n')
                    headers = [ header.split(': ', 1) for header in headers ]
                    headers = [ header for header in headers if len(header) > 1 ]
                    headers = dict([ (k.lower(), v) for k, v in headers ])
                    method = req.split(' ', 1)[0]
                    self.formfields = cgi.FieldStorage(StringIO.StringIO(body), headers=headers, strict_parsing=1, environ={'REQUEST_METHOD': method})
                    htmlwriter.SplitMIMEArgs(self.formfields, self.form)
                if 'action' in self.form and 'action' not in self.query:
                    action = self.form['action']
                    if action != 'ActionTakenFromQuery':
                        self.query['action'] = action

    def SaveFiles(self, path):
        ret = []
        if self.formfields:
            for field in self.formfields.list:
                fileitem = self.formfields[field.name]
                if fileitem.filename:
                    if path[:1] != '\\':
                        path = '%s\\' % path
                    sourceFileName = fileitem.filename
                    fileName = os.path.basename(sourceFileName)
                    exactFileName = path + fileName
                    ret.append({'size': len(field.value),
                     'filename': fileName,
                     'sourceFileName': sourceFileName,
                     'path': path,
                     'exactFileName': exactFileName})
                    fout = file(exactFileName, 'wb')
                    while 1:
                        chunk = fileitem.file.read(100000)
                        if not chunk:
                            break
                        fout.write(chunk)

                    fout.close()

        return ret

    def GetFiles(self):
        ret = {}
        if self.formfields:
            for field in self.formfields.list:
                fileitem = self.formfields[field.name]
                if fileitem.filename:
                    sourceFileName = fileitem.filename
                    fileName = os.path.basename(sourceFileName)
                    ret[fileitem.filename] = {'size': len(field.value),
                     'filename': fileName,
                     'fileData': fileitem.file.read(len(field.value))}

        return ret

    def DumpRequest(self, withRaw = False):
        print '************** R E Q U E S T ******************'
        print 'my url:', self.path
        print 'my paths:', self.paths
        print 'my method:', self.method
        print 'my proto:', self.proto
        print 'my args', self.args
        print 'my byte count', self.totalBytes
        for q in self.query.iteritems():
            print 'query var %s=%s' % q

        for f in self.form.iteritems():
            print 'form var %s=%s' % f

        print 'server varirables:'
        for i in self.header.iteritems():
            print i[0], ':', i[1]

        if withRaw:
            print '------------------- R A W ---------------------'
            print self.raw
        print '***********************************************'

    def DumpRequestToList(self):
        res = ['request.uid: %s' % self.uid,
         '----------',
         'my url: %s' % self.path,
         'my paths: %s' % self.paths,
         'my method: %s' % self.method,
         'my proto: %s' % self.proto,
         'my args %s' % self.args,
         '----------']
        for q in self.query.iteritems():
            res.append('query var %s=%s' % q)

        res.append('----------')
        res.append('SERVER VARIABLES:')
        for i in self.header.iteritems():
            res.append('%s:%s' % (i[0], i[1]))

        res.append('request.node_id: %s' % self.node_id)
        res.append('request.via_node_id: %s' % self.via_node_id)
        res.append('request.client_ip: %s' % self.client_ip)
        return res

    def Authorization(self):
        if self.header.has_key('Authorization'):
            try:
                uspa = self.header.pop('Authorization')
                i = uspa.rfind(' ')
                uspa = uspa[i + 1:]
                import base64
                uspa = base64.decodestring(uspa)
                try:
                    uspa = unicode(uspa, encoding='utf-8')
                except Exception as ex:
                    try:
                        uspa = unicode(uspa, encoding='iso-8859-1')
                    except Exception as ex:
                        pass

                i = uspa.find(':')
                username = uspa[:i]
                password = uspa[i + 1:]
                return (username, PasswordString(password))
            except:
                pass


def GetSession(parent, request, response, sessionsBySID, sessionsByFlatkaka):
    uspa = request.Authorization()
    if request.cookie.has_key('flatkaka'):
        flatkaka = request.cookie['flatkaka']
        if sessionsByFlatkaka.has_key(flatkaka):
            sess = sessionsByFlatkaka[flatkaka]
            if macho.mode == 'client':
                return sess
            if uspa is not None:
                u = sess.esps.contents['username']
                p = sess.esps.contents['password']
                if uspa[0] != u or uspa[1] != p:
                    svclog.warning("User %s is trying to hijack %s's session, with sessID=%d", uspa[0], u, sess.sid)
                else:
                    return sess
    sess = None
    success = False
    username = None
    password = None
    reason = 'Internal Server Error'
    statusCode = '500 Internal Server Error'
    if macho.mode == 'client':
        sess = basesession.CreateSession(None, const.session.SESSION_TYPE_ESP, None)
        sess.esps = ESPSession(parent, sess.sid)
        success = True
    else:
        usernameAndPassword = uspa
        reason = 'Access denied'
        statusCode = '401 Unauthorized'
        if usernameAndPassword is not None:
            username = usernameAndPassword[0]
            password = usernameAndPassword[1]
            for s in sessionsBySID.itervalues():
                if hasattr(s, 'esps') and s.esps.contents['username'] == username:
                    if s.userid and s.esps.contents['password'] == password:
                        return s
                    break

            if macho.mode == 'server' and ('authentication' not in sm.services or sm.services['authentication'].state != SERVICE_RUNNING):
                blue.pyos.synchro.SleepWallclock(3000)
                raise UserError('AutClusterStarting')
            try:
                if sm.services['http'].session.ConnectToProxyServerService('machoNet').CheckACL(request.ep.address, espCheck=True):
                    blue.pyos.synchro.SleepWallclock(3000)
                    raise UserError('AutClusterStarting')
            except machoNetExceptions.UnMachoDestination:
                blue.pyos.synchro.SleepWallclock(3000)
                raise UserError('AutClusterStarting')

            sessionID = basesession.GetNewSid()
            sess = basesession.CreateSession(sessionID, const.session.SESSION_TYPE_ESP)
            sess.esps = ESPSession(parent, sess.sid)
            auth = basesession.GetServiceSession('httpService').ConnectToAnyService('authentication')
            try:
                sessstuff = None
                try:
                    sessstuff, _, _ = auth.Login(sessionID, username, password, None, const.userConnectTypeServerPages, request.ep.address)
                    sessstuff['role'] |= sess.role
                except UserError as e:
                    if e.msg != 'CharacterInDifferentRegion':
                        raise
                    sys.exc_clear()

                if sessstuff:
                    if 'userid' in sessstuff:
                        for each in basesession.FindSessions('userid', [sessstuff['userid']]):
                            each.LogSessionHistory('Usurped by user %s via HTTP using local authentication' % username)
                            basesession.CloseSession(each)

                    sess.SetAttributes(sessstuff)
                sess.LogSessionHistory('Authenticated user %s via HTTP using local authentication' % username)
                success = True
            except machoNetExceptions.UnMachoDestination:
                reason = 'The proxy server was unable to connect to any Sol Server Node to handle your authentication request.'
                statusCode = '500 No Sol Server available'
                sys.exc_clear()
            except UserError as e:
                if e.msg not in ('LoginAuthFailed', 'LegacyLoginDisabled'):
                    raise
                sys.exc_clear()

            if not success:
                sess.LogSessionHistory('Session closed due to local authentication failure')
                basesession.CloseSession(sess)
    if success:
        sessID = sess.sid
        while sessionsBySID.has_key(sessID):
            svclog.warning('Session %d already exits, adding 1 to it', sessID)
            sessID += 1

        sessionsBySID[sessID] = sess
        sessionsByFlatkaka[sess.esps.GetFlatkaka()] = sess
        parent.OnSessionBegin(sessID)
        sess.cacheList = []
        sess.requestCount = 0
        sess.esps.contents['timeoutTimer'] = None
        if macho.mode != 'client':
            sess.esps.contents['username'] = username
            sess.esps.contents['password'] = password
        if macho.mode in ('proxy', 'server'):
            sm.ChainEvent('ProcessESPSessionCreated', sessionID=sessionID, ipaddress=request.ep.address)
        return sess
    else:
        response.Clear()
        response.status = statusCode
        response.Write(reason)
        response.authenticate = 1
        response.Flush()
        return


class Response():

    def __init__(self, httpService, ep):
        self.httpService = httpService
        self.ep = ep
        self.streamMode = None
        self.buff = cStringIO.StringIO()
        self.cookie = {}
        self.contentType = 'text/HTML; charset=UTF-8'
        self.status = '200 OK'
        self.header = {}
        self.authenticate = 0
        self.done = 0
        self.is_python = False

    def AddHeader(self, name, value):
        self.header[name] = value

    def AppendToLog(self, buff):
        raise RuntimeError('AppendToLog not implemented just yet', buff)

    def WriteBinary(self, buff):
        if self.streamMode == 't':
            raise RuntimeError('You cannot call WriteBinary() after calling Write()')
        self.streamMode = 'b'
        self.buff.write(buffer(buff))

    def Write(self, buff):
        if self.streamMode == 'b':
            raise RuntimeError('You cannot call Write() after calling WriteBinary()')
        self.streamMode = 't'
        self.buff.write(buff.encode('utf-8'))
        self.buff.write('\r\n')

    def Clear(self):
        self.buff.close()
        self.streamMode = None
        self.buff = cStringIO.StringIO()

    def End(self):
        raise RuntimeError('End not implemented just yet')

    def Flush(self):
        if self.done:
            return
        self.done = 1
        self.buff.seek(0, 2)
        self.header['Content-Length'] = self.buff.tell()
        if 'Content-Type' not in self.header:
            self.header['Content-Type'] = self.contentType
        self.header['Server'] = 'CCP-SP/%s' % boot.version
        if 'Keep-Alive' not in self.header:
            self.header['Keep-Alive'] = 'timeout=15, max=98'
        if 'Connection' not in self.header:
            self.header['Connection'] = 'Keep-Alive'
        if self.authenticate:
            self.header['WWW-Authenticate'] = 'Basic realm="CCP SERVER PAGES"'
            for k, v in self.httpService.GetStaticHeader().iteritems():
                if k not in self.header:
                    self.header[k] = v

        if self.cookie:
            s = ''.join([ '%s=%s; ' % (k, v) for k, v in self.cookie.iteritems() ])
            self.header['Set-Cookie'] = s + 'path=/'
        s = cStringIO.StringIO()
        s.write('HTTP/1.1 ')
        s.write(str(self.status))
        s.write('\r\n')
        for k, v in self.header.iteritems():
            s.write(k)
            s.write(': ')
            s.write(str(v))
            s.write('\r\n')

        s.write('\r\n')
        e = self.buff.getvalue()
        s.write(e)
        out = s.getvalue()
        if self.httpService.httpLog:
            if self.httpService.logChannel.IsOpen(1):
                for y in out.split('\n'):
                    for l in LineWrap(y.replace('\r', ''), maxlines=0, maxlen=80, pfx=''):
                        self.httpService.LogMethodCall('HTTP OUTPUT: ', utillib.strx(l))

        self.ep.Write(out)

    def Redirect(self, url, args = None, **kwargs):
        self.status = '302 Object Moved'
        if kwargs:
            if args and isinstance(args, dict):
                args.update(kwargs)
            else:
                args = kwargs
        if args:
            url = '%s?%s' % (url, urllib.urlencode(args))
        self.header['Location'] = url.encode('UTF-8')
        self.Flush()

    def SendNotModified(self, path):
        self.header['Location'] = path.encode('UTF-8')
        self.status = '304 Not Modified'
        self.Flush()

    def SendNotImplemented(self):
        self.status = '501 Not Implemented'
        self.Flush()


class HeadResponse(Response):

    def Write(self, buff):
        pass

    WriteBinary = Write


class ESPSession():

    def __init__(self, owner, sid):
        self.codePage = 0
        self.contents = {}
        self.LCID = 0
        self.sessionID = sid
        self.timeout = 20
        self.authenticated = 0
        self.username = ''
        self.password = ''
        self.owner = owner
        self.flatkokudeig = blue.os.GetWallclockTimeNow()
        self.remappings = {}

    def GetFlatkaka(self):
        return binascii.b2a_hex(Crypto.CryptoHash(self.flatkokudeig, id(self.owner), self.sessionID, sm.services['machoNet'].GetNodeID()))

    def Abandon(self):
        self.owner.OnSessionEnd(self.sessionID)
        self.owner = None


class ConnectionService(Service):
    __startupdependencies__ = ['dataconfig', 'machoNet', 'counter']
    __dependencies__ = ['machoNet']
    __exportedcalls__ = {'GetCacheStatus': [ROLE_SERVICE | ROLE_ADMIN],
     'SetCacheStatus': [ROLE_SERVICE | ROLE_ADMIN],
     'GetCacheSkipList': [ROLE_SERVICE | ROLE_ADMIN],
     'AddToCacheSkipList': [ROLE_SERVICE],
     'GetStaticHeader': [ROLE_SERVICE]}
    __configvalues__ = {'httpLog': 0}
    __guid__ = 'svc.http'
    __notifyevents__ = ['OnSessionEnd']
    __counters__ = {'openConnectionsInHttpService': 'normal'}

    def __init__(self):
        CoreService.__init__(self)
        self.quit = 0
        self.sessionsBySID = {}
        self.sessionsByFlatkaka = {}
        self.connections = []
        self.cacheSkipList = []
        self.caching = 0
        self.acceptingHTTP = 0
        self.codeCache = {}
        self.threads = 0
        self.TimoutOutIntervalInMinutes = 5
        self.staticHeader = None
        self.socket = None
        self.state = SERVICE_STOPPED

    def GetHtmlStateDetails(self, k, v, detailed):
        return None

    def OnSessionBegin(self, sessionID):
        if self.sessionsBySID.has_key(sessionID):
            sess = self.sessionsBySID[sessionID]
            sess.esps = ESPSession(self, sessionID)

    def OnSessionEnd(self, sessionID):
        if self.sessionsBySID.has_key(sessionID):
            sess = self.sessionsBySID[sessionID]
            del self.sessionsBySID[sessionID]
            if getattr(sess, 'esps', None):
                kaka = sess.esps.GetFlatkaka()
                if kaka in self.sessionsByFlatkaka:
                    del self.sessionsByFlatkaka[kaka]
            sess.LogSessionHistory('Session closed during OnSessionEnd')
            basesession.CloseSession(sess)

    def Init(self):
        if boot.role == 'client' and blue.pyos.packaged:
            raise RuntimeError("Http service: can't run")
        self.quit = 0
        self.sessionsBySID = {}
        self.sessionsByFlatkaka = {}
        self.connections = []
        self.cacheSkipList = ['.py', '.htc']
        self.caching = 0
        self.acceptingHTTP = int(prefs.GetValue('http', ['1', '0'][macho.mode == 'client']))
        self.codeCache = {}
        self.threads = 0
        self.TimoutOutIntervalInMinutes = 5
        self.staticHeader = None

    def Run(self, memStream = None):
        self.Init()
        if self.acceptingHTTP == 0:
            svclog.info('Http server not running as no http=1 in prefs.ini')
            return
        if prefs.GetValue('httpServerMode', 'ccp').lower() != 'ccp':
            svclog.info('Http server not running as httpServerMode!=ccp in prefs.ini')
            return
        self.socket = self.machoNet.GetTransport('tcp:raw:http')
        svclog.info('Http server running on address %s', self.socket.address)
        for i in xrange(5):
            self.StartThread()

    def StartThread(self):
        self.threads += 1
        uthread.pool('http::AcceptThread', self.AcceptThread)

    def Stop(self, memStream = None):
        self.quit = 1
        self.state = SERVICE_STOP_PENDING

    def AcceptThread(self):
        try:
            try:
                svclog.debug('Accepting http over transport: %s', self.socket)
                ep = self.socket.Accept()
            except GPSExceptions.GPSTransportClosed:
                if self.quit == 1:
                    svclog.debug('Accept returned because the service is stopping')
                raise

            svclog.debug('Accepted a connection: %s', ep)
            if not self.quit:
                self.StartThread()
            self.HandleConnection(ep)
        finally:
            if hasattr(self, 'threads'):
                self.threads -= 1
                if self.threads == 0:
                    self.state = SERVICE_STOPPED

    def GetCacheStatus(self):
        return self.caching

    def SetCacheStatus(self, status):
        self.caching = status

    def GetCacheSkipList(self):
        result = []
        for s in self.cacheSkipList:
            result.append([s])

        return result

    def AddToCacheSkipList(self, value):
        self.cacheSkipList.append(value)

    def GetStaticHeader(self):
        uthread.Lock('http.GetStaticHeader')
        try:
            if self.staticHeader is None:
                self.staticHeader = {'CCP-codename': boot.codename,
                 'CCP-version': boot.version,
                 'CCP-build': boot.build,
                 'CCP-sync': boot.sync,
                 'CCP-clustermode': prefs.GetValue('clusterMode', 'n/a')}
                if boot.role == 'server':
                    product = sm.GetService('cache').Setting('zsystem', 'Product')
                    ebsVersion = sm.GetService('DB2').CallProc('zsystem.Versions_Select', product)[0].version
                    self.staticHeader['CCP-product'] = product
                    self.staticHeader['CCP-EBS'] = ebsVersion
            if boot.role == 'proxy':
                machoNet = sm.GetService('machoNet')
                onlineCountEve = machoNet.GetClusterSessionCounts('EVE:Online')[0]
                onlineCountDust = machoNet.GetClusterSessionCounts('DUST:Online')[0]
                acl = machoNet.CheckACL(None, espCheck=True)
                self.staticHeader['CCP-onlineCount'] = onlineCountEve + onlineCountDust
                self.staticHeader['CCP-onlineCountEve'] = onlineCountEve
                self.staticHeader['CCP-onlineCountDust'] = onlineCountDust
                self.staticHeader['CCP-ACL'] = acl[1] if acl else None
                self.staticHeader['CCP-VIP'] = machoNet.vipMode
        except Exception:
            self.staticHeader = {'BADHEADER': ''}
            log.LogException()
        finally:
            uthread.UnLock('http.GetStaticHeader')

        return self.staticHeader

    def RemoveFromCacheSkipList(self, value):
        pass

    def HandleConnection(self, ep):
        if not hasattr(self, 'caching'):
            ClockThis('HTTP::Handle::Init', self.Init)
        requestCount = 0
        sess = None
        self.openConnectionsInHttpService.Add()
        try:
            while 1:
                sys.exc_clear()
                request = Request(self, ep)
                if request.method != 'HEAD':
                    response = Response(self, ep)
                else:
                    response = HeadResponse(self, ep)
                errfile = None
                lastRequest = request.path
                try:
                    ClockThis('HTTP::Handle::request.ParseHeader', request.ParseHeader)
                    if request.method == 'OPTION':
                        tmp = request.DumpRequestToList()
                        svclog.error('OPTION REQUEST, sorry not really an error')
                        svclog.error('The client %s made this request', ep.address)
                        for s in tmp:
                            svclog.error(s)

                        response.SendNotImplemented()
                        continue
                    requestCount += 1
                    sess = self.GetSession(request, response)
                    if sess:
                        sess.requestCount += 1
                    else:
                        continue
                    if self.HandleCaching(ep, request, response):
                        continue
                    response.cookie['flatkaka'] = sess.esps.GetFlatkaka()
                    filename, files = self.GetFileFromRequest(request)
                    if not files:
                        errfile = filename
                        raise IOError('file %s not found in www roots' % filename)
                    try:
                        self.HandleRequestFile(request, response, filename, files)
                    finally:
                        for _, f in files:
                            f.Close()

                except GPSExceptions.GPSTransportClosed:
                    svclog.debug('closed retrieving [%s], before that [%s].', request.path, lastRequest)
                    svclog.debug('Total requests served with this connection: %d', requestCount)
                    break
                except UnknownProtocol as e:
                    httplog.warning('%s sent Unknown HTTP protocol "%s" - method=%s, host=%s, path=%s, userid=%s, nodeID=%s/%s via=%s', request.client_ip, request.proto, request.method, request.host, request.full_path, getattr(request.session, 'userid', None), request.node_id, request.macho_mode, request.via_node_id)
                    break
                except UnknownVerb as e:
                    httplog.warning('%s sent Unknown HTTP method "%s" - host=%s, path=%s, userid=%s, nodeID=%s/%s via=%s', request.client_ip, request.method, request.host, request.full_path, getattr(request.session, 'userid', None), request.node_id, request.macho_mode, request.via_node_id)
                    break
                except Exception as ex:
                    self.HandleException(sess, request, response, ex, errfile)

                try:
                    response.Flush()
                    if response.is_python:
                        httplog.info('[%s] Response %s in %s sec. length=%s, type=%s, stream=%s', request.uid, response.status, time.time() - request.start_time, response.header.get('Content-Length', -1), response.header.get('Content-Type', ''), response.streamMode)
                    if request.proto == 'HTTP/1.0':
                        break
                except GPSExceptions.GPSTransportClosed:
                    sys.exc_clear()
                    svclog.warning('Trying to send response for [%s] but the connection was closed, prev: %s', request.path, lastRequest)
                    svclog.warning('Total requests served with this connection: %d', requestCount)
                    if response.is_python:
                        httplog.info('[%s] Failed to send responce - Socket closed after %s sec. length=%s, type=%s, stream=%s', request.uid, time.time() - request.start_time, response.header.get('Content-Length', -1), response.header.get('Content-Type', ''), response.streamMode)
                    break

        finally:
            if not getattr(ep.socket, 'isFake', False):
                ep.Close()
            self.openConnectionsInHttpService.Dec()
            if sess:
                if sess.esps.contents.has_key('timeoutTimer'):
                    if sess.esps.contents['timeoutTimer'] is None:
                        sess.esps.contents['timeoutTimer'] = 1
                        uthread.new(self.CheckSessionTimeout, sess, sess.requestCount)

    def GetSession(self, request, response):
        try:
            if not request.session.userid:
                raise AttributeError
            return request.session
        except AttributeError:
            sess = ClockThis('HTTP::Handle::GetSession', GetSession, self, request, response, self.sessionsBySID, self.sessionsByFlatkaka)
            if sess:
                request.session = sess
            return sess

    def HandleCaching(self, ep, request, response):
        if not self.caching:
            return False
        else:
            r = request.path.rfind('.')
            if r == -1:
                return False
            fileType = request.path[r:]
            for each in self.cacheSkipList:
                if fileType.startswith(each.lower()):
                    return False

            sess = request.session
            if request.path in sess.cacheList:
                response.SendNotModified(request.path)
                response.cookie['flatkaka'] = sess.esps.GetFlatkaka()
                return True
            sess.cacheList.append(request.path)
            svclog.debug('adding %s to cacheList', request.path)
            return False

    def GetFileFromRequest(self, request):
        sess = request.session
        if request.path in sess.esps.remappings:
            filename = sess.esps.remappings[request.path]
            svclog.debug('Remapped %s as %s', request.path, filename)
        else:
            if request.path[:7] == '/cache/':
                filename = 'cache:' + request.path[6:]
            else:
                filename = 'wwwroot:/' + request.path
            if filename[-1:] == '/':
                filename = '%sdefault.py' % filename
        if not sess.role & ROLE_PROGRAMMER:
            refuse = False
            if '..' in request.path:
                svclog.error("Refusing to give %s to %s because he's trying to use .. in the filename to hax0r us :(", filename, sess.userid)
                refuse = True
            else:
                extidx = filename.rfind('.')
                if extidx == -1:
                    svclog.error("Refusing to give %s to %s because he's trying to get a file that has no extension and hax0r us :(", filename, sess.userid)
                    refuse = True
                else:
                    ext = filename[extidx + 1:]
                    if ext.lower() not in self._GetDownloadableFileExtensions():
                        svclog.error("Refusing to give %s to %s because he's trying to get a file that has an extension that only programmers may acquire :(", filename, sess.userid)
                        refuse = True
            if refuse:
                raise AuthError('Only programmers may download arbitrary stuff from servers')
        ret = []
        fullPath = blue.paths.ResolvePath(filename)
        if os.path.exists(fullPath):
            resFile = blue.ResFile()
            resFile.OpenAlways(fullPath, 1)
            ret = [(fullPath, resFile)]
        return (filename, ret)

    def HandleRequestFile(self, request, response, filename, files):
        if filename[-3:] == '.py':
            response.is_python = True
            self.HandlePython(request, response, filename, files)
        else:
            resFile = files[-1][1]
            response.contentType = httputils.get_mimetype(filename)
            response.header['Cache-Control'] = 'max-age=31536000000, public'
            if request.method == 'HEAD':
                svclog.debug('Got a HEAD request, not returning body...')
            else:
                s = resFile.size
                if s > 1048576:
                    data = uthread.CallOnThread(resFile.Read)
                else:
                    data = resFile.Read()
                response.WriteBinary(data)

    def HandlePython(self, request, response, filename, files):
        oldctxt = bluepy.PushTimer('HTTP::Handle::Pages')
        try:
            response.header['Expires'] = '0'
            response.header['Cache-Control'] = 'private, no-cache'
            if request.method == 'HEAD':
                svclog.debug('Got a HEAD request, not executing script...')
            else:
                request.uid = uuid.uuid4()
                httplog.info('%s userID=%s %s %s %s [%s] nodeID=%s/%s via=%s', request.client_ip, getattr(request.session, 'userid', None), request.method, request.full_path, request.host, request.uid, request.node_id, request.macho_mode, request.via_node_id)
                if request.method in ('POST', 'PUT'):
                    httplog.info('[%s] %s data %r', request.uid, request.method, request.form)
                modified = max([ os.stat(fullpath).st_mtime for fullpath, f in files ])
                if filename not in self.codeCache or modified > self.codeCache[filename][0]:
                    with bluepy.Timer('HTTP::Handle::ExecFile::' + filename):
                        import __builtin__
                        glob = {'__builtins__': __builtin__}
                        for fn, f in files:
                            data = f.read().replace('\r\n', '\n')
                            f.close()
                            code = compile(data, fn, 'exec', 0, True)
                            exec code in glob

                        self.codeCache[filename] = (modified, glob)
                else:
                    glob = self.codeCache[filename][1]
                sess = request.session
                masque = sess.Masquerade()
                if not session.userid and macho.mode != 'client':
                    raise RuntimeError('\n                        **********************************************************************\n                        * SESSION IS BROKED, HAS NO USERID. RESTART YOUR SERVER PAGE BROWSER *\n                        **********************************************************************\n                    ')
                try:
                    ClockThis('HTTP::Handle::Pages::' + request.path, glob['Execute'], request, response, sess)
                finally:
                    masque.UnMask()

        finally:
            bluepy.PopTimer(oldctxt)

    def _TrackPage(self, title, session):
        trackID = 1 if prefs.clusterMode == 'LOCAL' else prefs.GetValue('webTrackID', -1)
        trackUrl = prefs.GetValue('trackUrl', 'http://piwik/')
        if not trackUrl.endswith('/'):
            trackUrl += '/'
        if trackID > -1:
            return '\n    <!-- Piwik -->\n    <script type="text/javascript">\n    var pkBaseURL = (("https:" == document.location.protocol) ? "%(trackHttps)s" : "%(trackHttp)s");\n    document.write(unescape("%%3Cscript src=\'" + pkBaseURL + "piwik.js\' type=\'text/javascript\'%%3E%%3C/script%%3E"));\n    </script><script type="text/javascript">\n    try {\n    var user = { \'userID\' : %(userid)s };\n    var piwikTracker = Piwik.getTracker(pkBaseURL + "piwik.php", %(trackID)d);\n    piwikTracker.setCustomData(user);\n    piwikTracker.setDocumentTitle(\'%(documentTitle)s\');\n    piwikTracker.trackPageView();\n    piwikTracker.enableLinkTracking();\n    } catch(err) {}\n    </script><noscript><p><img src="%(trackHttp)spiwik.php?idsite=%(trackID)d" style="border:0" alt="" /></p></noscript>\n    <!-- End Piwik Tracking Tag -->\n            ' % {'userid': session.userid if session and session.userid is not None else 'Not Authorized',
             'documentTitle': 'title',
             'trackID': trackID,
             'trackHttp': trackUrl,
             'trackHttps': trackUrl.replace('http:', 'https:')}

    def HandleException(self, sess, request, response, error, errfile):
        req_session = getattr(request, 'session', None)
        if isinstance(error, UserError):
            log.LogException(toAlertSvc=0, toMsgWindow=0, severity=log.LGWARN)
            if error.msg == 'Unknown protocol' or error.msg == 'Unknown command':
                response.Clear()
                response.Write('<html><head>')
                response.Write('\t<title>Internal Server Error</title>')
                response.Write('\t<link rel="stylesheet" href="/lib/error.css"/>')
                response.status = 501
                response.Write('</head><body>%s</body><img src="/img/header_error.jpg">' % str(error))
            elif error.msg == 'AutClusterStarting':
                response.Clear()
                response.Write('<html><head>')
                response.Write('\t<title>Authentication Failure</title>')
                response.Write('\t<link rel="stylesheet" href="/lib/std.css"/>')
                response.status = '401 Unauthorized'
                response.Write('</head><body><h1>Cluster Startup in Progress</h1>The cluster is not yet accepting incoming connections.</body>')
            else:
                response.Clear()
                response.Write('<html><head>')
                response.Write('\t<title>Exception - UserError</title>')
                response.Write('\t<link rel="stylesheet" href="/lib/error.css"/>')
                response.status = '200 OK'
                response.Write('</head>\n<body><img src="/img/header_error.jpg"><h1>UserError</h1>')
                if hasattr(__builtins__, 'cfg'):
                    response.Write('<font size=4>%s</font><br><br><br>' % cfg.Format(error.msg, error.dict))
                else:
                    response.Write('<font size=4>%s</font><br><br><br>' % utillib.strx((error.msg, error.dict)))
                response.Write('<pre>')
                response.Write(''.join(traceback.format_exc()))
                response.Write('</pre></body></html>')
        elif isinstance(error, machoNetExceptions.WrongMachoNode):
            if not error.payload:
                raise error
            targetNodeID = error.payload
            notFoundMacho = True
            current_host, current_port = ('', '')
            try:
                func = lambda x: (True if x.lower().startswith('host') else False)
                host = filter(func, request.raw.split('\r\n'))[0].split(':')
                current_host, current_port = host[1].strip(), host[2].strip()
            except Exception:
                log.LogException()

            if isinstance(targetNodeID, int):
                if sm.IsServiceRunning('tcpRawProxyService'):
                    tcpproxy = sm.services['tcpRawProxyService']
                else:
                    proxyID = sm.services['machoNet'].GetConnectedProxyNodes()[0]
                    tcpproxy = sm.StartService('debug').session.ConnectToRemoteService('tcpRawProxyService', proxyID)
                host, ports = tcpproxy.GetESPTunnelingAddressByNodeID()
                port = ports.get(targetNodeID)
                if str(host).lower() != str(current_host).lower() or port != int(current_port):
                    notFoundMacho = False
                    protocol = 'https' if iocp.UsingHTTPS() else 'http'
                    url = '%s://%s:%s%s' % (protocol,
                     host,
                     port,
                     request.FullPath())
                    response.Redirect(url)
            if notFoundMacho:
                response.Clear()
                response.Write('<html><head>')
                response.Write('\t<title>Failed macho redirect</title>')
                response.Write('\t<link rel="stylesheet" href="/lib/error.css">')
                response.status = '404 Not Found'
                response.Write('</head>\n<body><img src="/img/header_error.jpg">')
                response.Write("<h1>Don't know how to redirect to node %s</h1>" % (targetNodeID,))
                response.Write('<br>file %r %r' % (errfile, request.path))
                response.Write(' ' * 512)
                response.Write('%s</body></html>' % self._TrackPage('404 Not Found', req_session))
        elif isinstance(error, IOError):
            response.Clear()
            response.Write('<html><head>')
            response.Write('\t<title>404 Not Found</title>')
            response.Write('\t<link rel="stylesheet" href="/lib/error.css">')
            response.status = '404 Not Found'
            response.Write('</head>\n<body><img src="/img/header_error.jpg"><h1>404 Not Found</h1>')
            response.Write('<br>file %r %r' % (errfile, request.path))
            response.Write('<br>error.errno=%s' % error.errno)
            response.Write('<br>error.filename=%s' % error.filename)
            response.Write('<br>error.strerror=%s' % error.strerror)
            response.Write('<br>error.args=%r' % error.args)
            response.Write('<br>error=%r' % error)
            response.Write('<br>request.uid=%s' % request.uid)
            response.Write(' ' * 512)
            response.Write('%s</body></html>' % self._TrackPage('404 Not Found', req_session))
        elif isinstance(error, AuthError):
            response.Clear()
            response.Write('<html><head>')
            response.Write('\t<title>401 Unauthorized</title>')
            response.Write('\t<link rel="stylesheet" href="/lib/std.css"/>')
            response.status = '401 Unauthorized'
            response.Write('</head>\n<body><img src="/img/header_error.jpg"><h1>401 Unauthorized</h1>')
            response.Write('<br>%r<br>%r' % (error, request.path))
            response.Write(' ' * 512)
            response.Write('%s</body></html>' % self._TrackPage('401 Unauthorized', req_session))
        else:
            l = request.DumpRequestToList()
            username = 'N/A'
            if hasattr(sess, 'esps'):
                if 'username' in sess.esps.contents:
                    username = sess.esps.contents['username']
            info = 'Username: %s, address: %s' % (username, request.ep.address)
            response.Clear()
            response.Write('<html><head>')
            response.Write('\t<title>501 Internal Server Error</title>')
            response.Write('\t<link rel="stylesheet" href="/lib/error.css">')
            response.status = '501 Internal Server Error'
            response.Write('</head>\n<body><img src="/img/header_error.jpg"><h1>501 Internal Server Error</h1>')
            logWarning = 0
            sqlerror = isinstance(error, SQLError)
            if sqlerror:
                if error.errorRecords:
                    for er in error.errorRecords:
                        response.Write('<font color=red size=4>%s</font><br><br>' % htmlwriter.Swing(str(er[0])))

                    if error.errorRecords and error.errorRecords[0][2] == 50000 and error.errorRecords[0][4] == 13:
                        log.LogException(severity=log.LGWARN)
                        logWarning = 1
            response.Write('<pre>')
            response.Write(htmlwriter.Swing(''.join(traceback.format_exc())))
            response.Write('</pre><b>The request:</b><hr><pre>')
            for s in l:
                response.Write(htmlwriter.Swing(s))

            response.Write('</pre>%s</body></html>' % self._TrackPage('501 Internal Server Error', req_session))
            if not logWarning:
                log.LogException(info + '\nRequest=\n' + '\n'.join(l))

    def CheckSessionTimeout(self, sess, oldRequestCount):
        blue.pyos.synchro.SleepWallclock(60000 * self.TimoutOutIntervalInMinutes)
        try:
            if sess.requestCount == oldRequestCount:
                svclog.debug("%s's http session timeout, removing session. sid=%s", sess.esps.contents.get('username', '?'), sess.sid)
                if sess.sid != 0:
                    self.OnSessionEnd(sess.sid)
        finally:
            del sess.esps.contents['timeoutTimer']

    @Memoize(DB_SETTING_CACHE_TIMEOUT)
    def _GetDownloadableFileExtensions(self):
        if macho.mode == 'server':
            cacheSvc = self.session.ConnectToService('cache')
        else:
            cacheSvc = self.session.ConnectToAnyService('cache')
        rawString = cacheSvc.Setting('zsystem', 'SP-Allowed-Extensions')
        if not rawString:
            return ['py',
             'gif',
             'jpg',
             'htm',
             'htc',
             'html',
             'txt',
             'mp3',
             'js',
             'xsl',
             'xml',
             'xls',
             'css',
             'png',
             'ico',
             'pickle',
             'lbw',
             'cab',
             '7z',
             'uc',
             'swf',
             'wav',
             'mp3',
             'mid',
             'midi',
             'aif',
             'wma',
             'ogg',
             'woff',
             'ttf',
             'woff2',
             'fon',
             'otf',
             'eot',
             'svg']
        else:
            return [ i.strip() for i in rawString.split(',') ]
