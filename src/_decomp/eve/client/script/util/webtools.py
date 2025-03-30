#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\util\webtools.py
import os
import sys
from time import strftime, gmtime
import blue
import bluepy
import localization
import log
import uthread
import utillib
from carbon.common.lib.serverInfo import GetServerIP
from carbon.common.script.sys.service import Service
from carbon.common.script.util.format import PasswordString
DEBUGMODE = False
MAX_ICON_RANGE = 200

def Msg(msg):
    eve.Message('CustomNotify', {'notify': msg})
    log.general.Log(msg, log.LGNOTICE)
    print msg


class WebTools(Service):
    __guid__ = 'svc.webtools'
    __exportedcalls__ = {'SetVars': [],
     'GetVars': [],
     'GoSlimLogin': []}
    __dependencies__ = ['settings']

    def __init__(self):
        Service.__init__(self)
        self.Reset()

    def Run(self, memStream = None):
        Service.Run(self, memStream)

    def Stop(self, stream):
        Service.Stop(self)

    def Reset(self):
        self.renderVars = []
        self.events = set()

    def WaitForViewStateIn(self, *views):
        found = False
        while not found:
            blue.pyos.synchro.Yield()
            found = sm.GetService('viewState').IsViewActive(*views)

        sm.GetService('loading').GoBlack()
        s = sm.GetService('sceneManager').GetActiveScene()
        if s is not None:
            s.display = 0

    def SetVars(self, renderVars):
        rv = utillib.KeyVal(username='', password='')
        rv.username = renderVars[0]
        rv.password = renderVars[1]
        rv.routine = 'Apparel'
        self.renderVars = rv

    def GetVars(self):
        return self.renderVars

    def GoSlimLogin(self):
        if blue.pyos.packaged:
            raise RuntimeError('You can not build the IEC package on a packaged client you have to use a perforce client.')
        rv = self.renderVars
        if rv:
            func = getattr(self, '%sRender' % rv.routine.capitalize(), None)
            if func:
                self.GoLogin(rv.username, rv.password)
                self.WaitForViewStateIn('charsel')
                self.GoCharsel()
                self.WaitForViewStateIn('station', 'hangar', 'inflight')
                self.GoRoutine(rv.routine, func)

    def GoLogin(self, username, password):
        sm.GetService('overviewPresetSvc')
        sm.GetService('viewState').ActivateView('login')
        user = username
        pwd = PasswordString(password)
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Login/LoggingIn'), localization.GetByLabel('UI/Login/ConnectingToCluster'), 1, 100)
        blue.pyos.synchro.Yield()
        eve.Message('OnConnecting')
        blue.pyos.synchro.Yield()
        eve.Message('OnConnecting2')
        blue.pyos.synchro.Yield()
        serverName = utillib.GetServerName()
        eve.serverName = serverName
        server = GetServerIP(serverName)
        loginparam = [user,
         pwd,
         server,
         26000,
         0]
        try:
            sm.GetService('connection').Login(loginparam)
        except:
            raise

        sm.GetService('device').PrepareMain()
        blue.pyos.synchro.Yield()
        blue.pyos.synchro.Yield()
        blue.pyos.synchro.Yield()
        blue.pyos.synchro.Yield()
        sm.GetService('viewState').ActivateView('charsel')

    def GoCharsel(self):
        chars = sm.GetService('cc').GetCharactersToSelect()
        characterid = None
        for char in chars:
            characterid = char.characterID
            break

        if characterid:
            sm.GetService('sessionMgr').PerformSessionChange('charsel', sm.RemoteSvc('charUnboundMgr').SelectCharacterID, characterid)

    def GoRoutine(self, routine, func):
        uthread.pool('Webtools :: GoRoutine :: %sRender' % routine.capitalize(), func)

    def GenericQuit(self):
        self.settings.SaveSettings()
        bluepy.Terminate(0, 'User requesting close')

    def GenerateReport(self):
        rootPath = blue.sysinfo.GetUserDocumentsDirectory() + '/EVE/capture/Screenshots/'
        lines = []
        for rootDir, dirs, files in os.walk(rootPath):
            if files:
                numBytes = 0
                for fileName in files:
                    pathName = '%s/%s' % (rootDir, fileName)
                    numBytes += os.path.getsize(pathName)

                lines.append('%s\n\n\t%.3f MB in %d files\n\n' % (rootDir, numBytes / 1024.0 / 1024.0, len(files)))

        fileName = rootPath + 'IEC_report.txt'
        output = open(fileName, 'w')
        output.write(''.join(lines))
        output.close()
        return fileName


class LoggingRoutines:
    __exportedcalls__ = {'CreateLogFile': [],
     'WriteToLogfile': []}

    def __init__(self):
        self.logfile = None

    def CreateLogFile(self, ex = ''):
        logfilepath = blue.sysinfo.GetUserDocumentsDirectory() + '/EVE/logs/RenderLogs/'
        logfilename = '%s_%s_renderlog.txt' % (strftime('%Y.%m.%d-%H.%M', gmtime()), ex)
        dr = DirectoryRoutines()
        dr.GenericCheckCreateDirectory(logfilepath)
        filename = logfilepath + logfilename
        self.logfile = blue.classes.CreateInstance('blue.ResFile')
        if not self.logfile.Open(filename, 0):
            self.logfile.Create(filename)
        self.WriteLogFile('#')
        self.WriteLogFile('# Started at ' + strftime('%Y.%m.%d-%H.%M', gmtime()))
        self.WriteLogFile('#')

    def WriteLogFile(self, line):
        if self.logfile:
            self.logfile.Write(line.encode('utf8') + '\n')

    def CloseLogFile(self):
        if self.logfile:
            self.WriteLogFile('#')
            self.WriteLogFile('# Ended at ' + strftime('%Y.%m.%d-%H.%M', gmtime()))
            self.WriteLogFile('#')
            self.logfile.Close()


class DirectoryRoutines:

    def __init__(self):
        self.createdDirectories = {}

    def DeleteCachedFile(self, itemID, folder = 'Portraits', flush = 0):
        resPath = blue.paths.ResolvePath(u'cache:/Pictures/%s/' % folder)
        for rRoot, dirs, files in os.walk(resPath):
            for rFile in files:
                rFile = str(rFile)
                if flush or rFile.startswith(str(itemID)):
                    try:
                        os.remove(str(rRoot) + str(rFile))
                    except:
                        sys.exc_clear()

    def GenericCheckCreateDirectory(self, name, dry_run = 0):
        if DEBUGMODE:
            self.createdDirectories = {}
        name = os.path.normpath(name)
        created_dirs = []
        if os.path.isdir(name) or name == '':
            return created_dirs
        if self.createdDirectories.get(os.path.abspath(name)):
            return created_dirs
        head, tail = os.path.split(name)
        tails = [tail]
        while head and tail and not os.path.isdir(head):
            head, tail = os.path.split(head)
            tails.insert(0, tail)

        for d in tails:
            head = os.path.join(head, d)
            abs_head = os.path.abspath(head)
            if self.createdDirectories.get(abs_head):
                continue
            if not dry_run:
                try:
                    os.mkdir(head)
                    created_dirs.append(head)
                except OSError as exc:
                    raise "could not create '%s': %s" % (head, exc[-1])

            self.createdDirectories[abs_head] = 1

        return created_dirs
