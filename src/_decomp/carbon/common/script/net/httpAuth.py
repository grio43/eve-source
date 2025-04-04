#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\httpAuth.py
import base64
from datetime import datetime
import cherrypy
import blue
from carbon.common.lib import const
from carbon.common.script.sys import basesession
from eveexceptions import UserError
from eveprefs import prefs
from carbon.common.script.net import httpJinja, machoNet
SESSION_KEY = '_cp_username'
AUTH_LOGIN_URL = '/auth/login'
DEFAULT_URL = '/default.py'

def CreateSession(username, password):
    session = basesession.CreateSession()
    session.esps = ESPSession(None, session.sid)
    session.esps.contents['username'] = username
    session.esps.contents['password'] = password
    return session


def EndSession():
    cherrypy.session.delete()
    cherrypy.lib.sessions.expire()


def CheckCredentials(username, password):
    sess = CreateSession(username, password)
    if machoNet.mode == 'client':
        cherrypy.session['machoSession'] = sess
        return
    auth = basesession.GetServiceSession('cherry').ConnectToAnyService('authentication')
    sptype = const.userConnectTypeServerPages
    try:
        sessstuff, _ = auth.Login(sess.sid, username, password, None, sptype, cherrypy.request.remote.ip)
    except UserError:
        return u'Incorrect username or password'
    except Exception:
        return u'Incorrect username or password'

    session = CreateSession(username, password)
    sessstuff['role'] |= sess.role
    for otherSession in basesession.FindSessions('userid', [sessstuff['userid']]):
        otherSession.LogSessionHistory('Usurped by user %s via HTTP using local authentication' % username)
        basesession.CloseSession(otherSession)

    cherrypy.session['machoSession'] = sess
    sess.SetAttributes(sessstuff)


def CheckAuth(*args, **kwargs):
    assets = cherrypy.request.config.get('tools.staticdir.dir')
    cherrypy.request.beginTime = datetime.now()
    if assets not in cherrypy.request.path_info:
        conditions = cherrypy.request.config.get('auth.require', None)
        if conditions is not None:
            pathInfo = cherrypy.request.path_info
            if len(cherrypy.request.query_string):
                pathInfo = '%s?%s' % (pathInfo, cherrypy.request.query_string)
            if pathInfo in [AUTH_LOGIN_URL, DEFAULT_URL]:
                authLogin = AUTH_LOGIN_URL
            else:
                authLogin = '%s?from_page=%s' % (AUTH_LOGIN_URL, base64.urlsafe_b64encode(pathInfo))
            username = cherrypy.session.get(SESSION_KEY)
            if username:
                cherrypy.request.login = username
                for condition in conditions:
                    if not condition():
                        raise cherrypy.HTTPRedirect(authLogin)

            else:
                raise cherrypy.HTTPRedirect(authLogin)


cherrypy.tools.auth = cherrypy.Tool('before_handler', CheckAuth)

def Require(*conditions):

    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f

    return decorate


def MemberOf(groupName):

    def check():
        return cherrypy.request.login == 'joe' and groupName == 'admin'

    return check()


def NameIs(required_username):
    return lambda : required_username == cherrypy.request.login


def AnyOf(*conditions):

    def check():
        for condition in conditions:
            if condition():
                return True

        return False

    return check()


def AllOf(*conditions):

    def check():
        for condition in conditions:
            if not condition():
                return False

        return True

    return check


class ESPSession:

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


class AuthController(object):
    __guid__ = 'httpAuth.AuthController'

    def on_login(self, username):
        pass

    def on_logout(self, username):
        pass

    def get_loginform(self, username, msg = None, from_page = '/'):
        sp = cherrypy.sm.GetService('SP')
        try:
            background_color = sp.Color()
        except Exception:
            background_color = sp.Color()

        return {'msg': msg,
         'style': 'background-color: %s; color: black' % background_color,
         'sp': sp.Title(),
         'server': cherrypy.prefs.clusterName,
         'generate_time': datetime.now() - cherrypy.request.beginTime,
         'username': 'sp' if prefs.clusterMode == 'LOCAL' else ''}

    @cherrypy.expose
    @cherrypy.tools.jinja(template='AuthController_login.html')
    def login(self, username = None, password = None, from_page = '/'):
        if username is None or password is None:
            return self.get_loginform('', from_page=from_page)
        error_msg = CheckCredentials(username, password)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        cherrypy.session.regenerate()
        cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
        self.on_login(username)
        if from_page != '/':
            from_page = base64.urlsafe_b64decode(str(from_page))
        raise cherrypy.HTTPRedirect(from_page or '/')

    @cherrypy.expose
    def logout(self, from_page = '/'):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        if 'machoSession' in cherrypy.session:
            sess = cherrypy.session['machoSession']
            sess.LogSessionHistory('Web session closed by logging out %s' % str(session.userid))
            basesession.CloseSession(sess)
        EndSession()
        raise cherrypy.HTTPRedirect(from_page or '/')
