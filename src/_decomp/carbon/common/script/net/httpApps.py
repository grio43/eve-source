#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\httpApps.py
import os
import sys
import logging
import blue
import cherrypy
from carbon.common.script.net.httpAuth import Require
from scriber import httputils
from carbon.common.script.net import httpJinja
log = logging.getLogger('scriber')

def Host():
    host = cherrypy.request.headers.get('Host')
    if host:
        return host.split(':')
    else:
        return ('', '')


def Convert(var):
    try:
        return int(var)
    except Exception:
        sys.exc_clear()
        try:
            return long(var)
        except Exception:
            sys.exc_clear()
            try:
                return float(var)
            except Exception:
                sys.exc_clear()
                if var == 'None':
                    return None
                else:
                    return var


def Pythonize(var):
    if type(var) == type([]):
        ret = []
        for i in var:
            ret.append(Convert(i))

        return ret
    return Convert(var)


class ServerPageHandler(object):
    __guid__ = 'httpApps.ServerPageHandler'

    def __init__(self):
        pass

    def Handle(self, *args, **kwargs):
        sess = None
        try:
            sess = cherrypy.session['machoSession']
            if not sess.userid:
                self.EndWebSession()
        except:
            pass

        isSP, files = self.GetFiles(args)
        if not isSP:
            path, fo = files[-1]
            cherrypy.response.headers['Cache-Control'] = 'max-age=3600, public'
            log.info('path=%s' % path)
            log.info('httputils.get_mimetype(path)=%s' % httputils.get_mimetype(path))
            log.info('fo=%s' % fo)
            log.info('fo.size=%s' % fo.size)
            try:
                cherrypy.response.headers['Content-Type'] = httputils.get_mimetype(path)
                return cherrypy.lib.static._serve_fileobj(fo, httputils.get_mimetype(path), fo.size)
            except Exception as ex:
                log.exception('Well SHIT!')
                log.error('path=%s' % path)
                log.error('httputils.get_mimetype(path)=%s' % httputils.get_mimetype(path))
                log.error('fo=%s' % fo)
                log.error('fo.size=%s' % fo.size)

        try:
            glob = self.ExecutePy(files)
        finally:
            for fn, fo in files:
                fo.close()

        request, response = self.PrepareReqResp()
        action = request.params.get('action')
        if action and isinstance(action, list):
            request.params['action'] = action[0]
        try:
            masque = sess.Masquerade()
            request.session = sess
            try:
                glob['Execute'](request, response, sess)
            finally:
                masque.UnMask()
                request.session = None

            if response.contentType is None:
                if response.streamMode == 'b':
                    ct = 'application/octet-stream'
                else:
                    ct = 'text/html;charset=utf-8'
            else:
                ct = response.contentType
            data = response.buff.getvalue()
            if 'charset=utf-8' in ct.lower():
                data = unicode(data).encode('utf-8')
            response.headers['Content-Type'] = ct
            return data
        finally:
            del request
            del response

    def GetFiles(self, args):
        files = []
        filepath, filename = os.path.split(os.path.join(*args))
        isSP = filename.lower().endswith('.py')
        for fn in (filename, 'app' + filename.capitalize()):
            bluepath = 'wwwroot:' + os.path.join(filepath, fn)
            fullPath = blue.paths.ResolvePath(bluepath)
            if os.path.exists(fullPath):
                rf = blue.ResFile()
                rf.OpenAlways(fullPath)
                files.append((fullPath, rf))
            if files and not isSP:
                break

        if not files:
            raise cherrypy.NotFound(bluepath)
        return (isSP, files)

    def ExecutePy(self, files):
        import __builtin__
        glob = {'__builtins__': __builtin__}
        for fn, fo in files:
            data = fo.read()
            code = compile(data, fn, 'exec', 0, True)
            try:
                exec code in glob
            except Exception:
                logging.exception('exec code in glob failed')
                raise

        return glob

    def PrepareReqResp(self):
        request, response = cherrypy.request, cherrypy.response
        request.rawparams = dict(request.params)
        for k, v in request.params.iteritems():
            if type(v) is list:
                v = [ Pythonize(e) for e in v ]
            else:
                v = Pythonize(v)
            if type(v) is list and len(v) == 2:
                if v[0] == v[1]:
                    v = v[0]
                else:
                    try:
                        v.remove('ActionTakeFromQuery')
                        v = v[0]
                    except ValueError:
                        pass

            request.params[k] = v

        def QueryString(variable, caseInsensitive = False, raw = False):
            if variable == 'action':
                action = request.params.get('action')
                if action:
                    if isinstance(action, list):
                        return action[0]
                    else:
                        return action
            params = request.rawparams if raw else request.params
            if caseInsensitive:
                variable = variable.lower()
                for k, v in params.iteritems():
                    if k.lower() == variable:
                        return v

                return None
            else:
                return params.get(variable)

        request.QueryString = QueryString

        def QueryStrings(raw = False):
            if raw:
                return request.rawparams
            return request.params

        request.QueryStrings = QueryStrings
        request.query = request.params
        request.Host = Host
        request.Form = QueryString
        request.FormItems = QueryStrings
        request.form = request.params
        request.path = request.path_info

        def FullPath():
            return request.path_info

        request.FullPath = FullPath
        request.args = request.query_string
        import StringIO
        response.streamMode = None
        response.buff = StringIO.StringIO()

        def Write(buff):
            response.buff.write(buff)
            response.buff.write('\r\n')

        response.Write = Write

        def WriteBinary(buff):
            import cStringIO
            response.buff = cStringIO.StringIO()
            response.streamMode = 'b'
            response.buff.write(buffer(buff))

        response.WriteBinary = WriteBinary

        def Redirect(url, args = None):
            if args:
                url = url + '?'
                for k, v in args.iteritems():
                    url = url + str(k) + '=' + str(v) + '&'

            to = url.encode('UTF-8')
            raise cherrypy.HTTPRedirect([to])

        response.Redirect = Redirect
        response.contentType = None
        return (request, response)


class PolarisController(ServerPageHandler):
    __guid__ = 'httpApps.PolarisController'

    def __init__(self):
        pass

    @cherrypy.expose
    @Require()
    def default(self, *args, **kwargs):
        return self.Handle(*args, **kwargs)


class NodeController(object):
    __guid__ = 'httpApps.NodeController'

    def __init__(self):
        pass

    @cherrypy.expose
    def default(self, *args, **kwargs):
        return 'NodeController: (args) %s and (kwargs) %s' % (args, kwargs)


class MapController(object):
    __guid__ = 'httpApps.MapController'

    def __init__(self):
        pass

    @cherrypy.expose
    def default(self, *args, **kwargs):
        return 'MapController: (args) %s and (kwargs) %s' % (args, kwargs)
