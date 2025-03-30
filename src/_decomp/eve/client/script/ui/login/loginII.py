#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\loginII.py
import sys
import types
import blue
import carbon.common.script.util.format as fmtutil
import evecamera
import localization
import locks
import log
import pytelemetry.zoning as telemetry
import trinity
import uthread
import utillib
from carbon.common.lib.serverInfo import GetServerInfo, GetServerIP, GetServerName, LIVE_SERVER, TEST_SERVER1, TEST_SERVER2, TEST_SERVER3
from carbonui import uiconst
from carbonui.control.layer import LayerCore
from carbonui.control.singlelineedits.singleLineEditPassword import SingleLineEditPassword
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.environment import nodemanager
from eve.client.script.ui.control import eveLabel
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.common.lib import appConst as const
from eveexceptions import UserError
from eveprefs import prefs, boot

def GetVersion():
    buildno = 'Undefined'
    try:
        buildno = '%s.%s' % (boot.keyval['version'].split('=', 1)[1], boot.build)
    except Exception:
        log.LogException()

    return buildno


try:
    if not GetServerInfo().isLive:
        if prefs.GetValue('nominidump', 0):
            log.general.Log('Running against a test server. Crash minidump is NOT active because of nominidump=1 in prefs.ini', log.LGNOTICE)
        else:
            log.general.Log('Running against a test server. Crash minidump is active. You can disable this with nominidump=1 in prefs.ini', log.LGNOTICE)
            blue.os.miniDump = True
except Exception:
    log.LogException()

class Login(LayerCore):
    __guid__ = 'form.LoginII'
    __notifyevents__ = ['OnEndChangeDevice', 'OnGraphicSettingsChanged', 'ProcessUIRefresh']
    isTopLevelWindow = True

    def OnCloseView(self):
        if uicore.layer.systemmenu.isopen:
            uthread.new(uicore.layer.systemmenu.CloseMenu)
        self.Reset()
        sm.GetService('sceneManager').SetActiveScene(None)
        sm.UnregisterNotify(self)
        del self.scene.curveSets[:]
        self.scene = None
        self.ship = None
        self.Flush()

    def ProcessUIRefresh(self):
        if self.isopen:
            if self.reloading:
                self.pendingReload = 1
                return
            currentUsername = self.usernameEditCtrl.GetValue()
            currentPassword = self.passwordEditCtrl.GetValue()
            self.reloading = 1
            self.Layout(False, None, currentUsername, currentPassword)
            self.reloading = 0
            if self.pendingReload:
                self.pendingReload = 0

    def OnEndChangeDevice(self, *args):
        if self.isopen:
            if self.reloading:
                self.pendingReload = 1
                return
            currentUsername = self.usernameEditCtrl.GetValue()
            currentPassword = self.passwordEditCtrl.GetValue()
            self.reloading = 1
            self.Layout(1, True, currentUsername, currentPassword)
            self.reloading = 0
            if self.pendingReload:
                self.pendingReload = 0
                self.OnEndChangeDevice()

    @telemetry.ZONE_METHOD
    def Reset(self):
        self.serverStatus = {}
        self.serverStatusTextControl = None
        self.serverStatusTextFunc = None
        self.serverNameTextControl = None
        self.serverVersionTextControl = None
        self.mainBrowserParent = None
        self.mainBrowser = None
        self.usernameEditCtrl = None
        self.passwordEditCtrl = None
        self.connecting = False
        self.acceptbtns = None
        self.scrollText = None
        self.reloading = 0
        self.pendingReload = 0
        self.maintabs = None
        self.isShowingUpdateDialog = False

    @telemetry.ZONE_METHOD
    def OnOpenView(self, **kwargs):
        self.Reset()
        uthread.worker('login::StatusTextWorker', self.__StatusTextWorker)
        blue.resMan.Wait()
        self.serverName = utillib.GetServerName()
        self.serverIP = GetServerIP(self.serverName)
        self.serverName = GetServerName(self.serverIP)
        self.serverPort = utillib.GetServerPort()
        self.firstCheck = True
        self.isShowingUpdateDialog = False
        self.Layout()
        sm.ScatterEvent('OnClientReady', 'login')
        self.isopen = 1
        uthread.new(self.UpdateServerStatus)

    def ClickExit(self):
        uicore.cmd.GetCommandAndExecute('CmdQuitGame')

    @telemetry.ZONE_METHOD
    def Layout(self, reloading = 0, pushBtnArgs = None, setUsername = None, setPassword = None):
        if not reloading:
            self.sceneLoadedEvent = locks.Event('loginScene')
            uthread.new(self.LoadScene)
        self.Flush()
        bar_height = uicore.desktop.height / 6
        top_bar = Container(name='underlayContainer', parent=self, align=uiconst.TOTOP, height=bar_height)
        FillThemeColored(bgParent=top_bar, colorType=uiconst.COLORTYPE_UIBASE, opacity=0.5)
        eveLabel.EveLabelSmall(parent=top_bar, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, left=16, top=16, text=localization.GetByLabel('UI/Login/Version', versionNumber=GetVersion()))
        if trinity.mainWindow.GetWindowState().windowMode != trinity.Tr2WindowMode.WINDOWED:
            ButtonIcon(parent=top_bar, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL, top=16, left=16, texturePath='res:/UI/Texture/Shared/DarkStyle/windowClose.png', hint=localization.GetByLabel('UI/Login/QuitGame'), func=self.ClickExit, args=())
        bottom_bar = Container(name='underlayContainer_Bottom', parent=self, align=uiconst.TOBOTTOM, height=bar_height)
        FillThemeColored(bgParent=bottom_bar, colorType=uiconst.COLORTYPE_UIBASE, opacity=0.5)
        bottomArea = Container(name='bottomArea', parent=bottom_bar, idx=0)
        bottomSub = Container(name='bottomSub', parent=bottomArea, align=uiconst.CENTER, idx=0, height=bottom_bar.height, width=800)
        Button(parent=bottom_bar, align=uiconst.TOPLEFT, top=16, left=16, label=localization.GetByLabel('UI/Login/Settings'), func=self.OpenSettings, args=())
        login_container = ContainerAutoSize(parent=bottom_bar, align=uiconst.CENTERTOP, top=16, width=160, alignMode=uiconst.TOTOP)
        is_sso_login = sm.GetService('gameui').UsingSingleSignOn()
        if not is_sso_login:
            selected_username = setUsername or settings.public.ui.Get('username', '')
            self.usernameEditCtrl = SingleLineEditText(name='username', parent=login_container, align=uiconst.TOTOP, maxLength=64, hintText=localization.GetByLabel('UI/Login/Username'), OnReturn=self.Connect, setvalue=selected_username)
            self.usernameEditCtrl.SetHistoryVisibility(0)
            knownUserNames = settings.public.ui.Get('usernames', [])
            if knownUserNames:
                self.usernameEditCtrl.LoadCombo(id='usernamecombo', options=[ (name, name) for name in knownUserNames ], callback=self.OnComboChange, setvalue=selected_username, comboIsTabStop=0)
            self.passwordEditCtrl = SingleLineEditPassword(name='password', parent=login_container, align=uiconst.TOTOP, top=8, maxLength=64, setvalue=setPassword, hintText=localization.GetByLabel('UI/Login/Password'), OnReturn=self.Connect)
            if trinity.app.IsActive():
                if selected_username:
                    uicore.registry.SetFocus(self.passwordEditCtrl)
                else:
                    uicore.registry.SetFocus(self.usernameEditCtrl)
        Button(parent=login_container, align=uiconst.TOTOP, top=8 if not is_sso_login else 0, label=localization.GetByLabel('UI/Login/Connect'), func=self.Connect, btn_default=1)
        status_container = LayoutGrid(parent=login_container, align=uiconst.TOPLEFT, left=login_container.width + 16, columns=1, cellSpacing=(0, 4))
        self.serverNameTextControl = eveLabel.EveLabelSmall(parent=status_container, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, text=localization.GetByLabel('UI/Login/CheckingStatus'))
        self.serverStatusTextControl = eveLabel.EveLabelSmall(parent=status_container, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        self.serverVersionTextControl = eveLabel.EveLabelSmall(parent=status_container, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        if not self.IsChina():
            esrbNoticeHeight = 70
            esrbNoticeWidth = 200
            allowedSizes = [1.0, 0.9, 0.8]
            desktopWidth = uicore.desktop.width
            useHeight = int(esrbNoticeHeight * 0.7)
            useWidth = int(esrbNoticeWidth * 0.7)
            for multiplier in allowedSizes:
                tempWidth = esrbNoticeWidth * multiplier
                if tempWidth <= desktopWidth * 0.11:
                    useWidth = int(tempWidth)
                    useHeight = int(esrbNoticeHeight * multiplier)
                    break

            cont = Container(name='esrbParent', parent=top_bar, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, left=16, width=useWidth, height=useHeight)
            sprite = Sprite(name='ESRB', parent=cont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/ESRBnotice.dds', color=(1.0, 1.0, 1.0, 1.0))
            sprite.rectWidth = esrbNoticeWidth
            sprite.rectHeight = esrbNoticeHeight
            animations.FadeOut(cont, duration=0.5, timeOffset=6.0)

    def OnGraphicSettingsChanged(self, changes):
        if self.isopen and 'shaderQuality' in changes and getattr(self, 'scene', None):
            self.CheckHeightMaps()

    @telemetry.ZONE_METHOD
    def CheckHeightMaps(self):
        if 'LO' in trinity.GetShaderModel():
            heightMapParams = nodemanager.FindNodes(self.scene, 'HeightMap', 'trinity.TriTextureParameter')
            for param in heightMapParams:
                param.resourcePath = param.resourcePath.replace('_hi.dds', '_lo.dds')

        else:
            heightMapParams = nodemanager.FindNodes(self.scene, 'HeightMap', 'trinity.TriTextureParameter')
            for param in heightMapParams:
                param.resourcePath = param.resourcePath.replace('_lo.dds', '_hi.dds')

    @telemetry.ZONE_METHOD
    def LoadScene(self):
        self.scene = trinity.Load('res:/dx9/scene/login_screen.red')
        blue.resMan.Wait()
        self.CheckHeightMaps()
        stations = self.scene.Find('trinity.EveStation2')
        for station in stations:
            station.PlayAnimationEx('NormalLoop', 0, 0, 0.2)

        sceneMan = sm.GetService('sceneManager')
        sceneMan.SetActiveScene(self.scene)
        sceneMan.SetPrimaryCamera(evecamera.CAM_LOGIN)
        self.sceneLoadedEvent.set()
        blue.pyos.synchro.Yield()

    def OnEsc(self):
        if uicore.layer.systemmenu.isopen:
            uthread.new(uicore.layer.systemmenu.CloseMenu)
        else:
            uthread.new(uicore.layer.systemmenu.OpenView)

    def OpenSettings(self):
        if not uicore.layer.systemmenu.isopen:
            uthread.new(uicore.layer.systemmenu.OpenView)

    def OnComboChange(self, combo, header, value, *args):
        self.usernameEditCtrl.SetValue(value)
        self.passwordEditCtrl.SetValue('')
        uthread.new(uicore.registry.SetFocus, self.passwordEditCtrl)

    @telemetry.ZONE_METHOD
    def __StatusTextWorker(self):
        while not eve.session.userid:
            blue.pyos.synchro.SleepWallclock(750)
            try:
                if getattr(self, 'serverStatusTextFunc', None) is not None:
                    if not getattr(self, 'connecting', 0):
                        self.__SetServerStatusText(refreshOnNone=True)
            except:
                log.LogException('Exception in status text worker')
                sys.exc_clear()

    @telemetry.ZONE_METHOD
    def __SetServerStatusText(self, refreshOnNone = False):
        if self.serverStatusTextFunc is None:
            self.ClearServerStatus()
            return
        statusText = apply(self.serverStatusTextFunc[0])
        if statusText is None:
            self.ClearServerStatus()
            if refreshOnNone:
                uthread.new(self.UpdateServerStatus, False)
            return
        serverversion, serverbuild = self.serverStatusTextFunc[1:]
        self.SetNameText(localization.GetByLabel('UI/Login/ServerStatus/Server', serverName=self.serverName))
        label, parameters = statusText
        self.SetStatusText(localization.GetByLabel('UI/Login/ServerStatus/Status', statusText=localization.GetByLabel(label, **parameters)))
        eve.serverVersion = serverversion
        eve.serverBuild = serverbuild
        if serverversion and serverbuild:
            if '%.2f' % serverversion != '%.2f' % boot.version or serverbuild > boot.build:
                self.SetVersionText(localization.GetByLabel('UI/Login/ServerStatus/VersionIncompatible', serverVersion=serverversion, serverBuild=serverbuild))
        if label == '/Carbon/MachoNet/ServerStatus/OK':
            sm.GetService('connection').TryAutomaticLogin()

    def IsChina(self):
        return boot.region == 'optic'

    def GetIsAutoPatch(self, allowPatch):
        isAutoPatch = self.serverIP == LIVE_SERVER or self.serverIP in [TEST_SERVER1, TEST_SERVER2, TEST_SERVER3] or prefs.GetValue('forceAutopatch', 0) == 1
        if not allowPatch:
            isAutoPatch = False
        return isAutoPatch

    def IsServerPortValid(self):
        try:
            int(self.serverPort)
        except Exception as e:
            log.LogError(e)
            sys.exc_clear()
            self.SetStatusText(localization.GetByLabel('UI/Login/InvalidPortNumber', port=self.serverPort))
            self.serverStatusTextFunc = None
            return False

        return True

    def UpdateServerStatus(self, allowPatch = True):
        self.InternalUpdateServerStatus(allowPatch=allowPatch, bootbuild=boot.build, bootversion=boot.version)

    def DisplayOutOfDateMessageAndQuitGame(self, reason = None):
        self.isShowingUpdateDialog = True
        uicore.Message('LoginUpdateAvailable', {'info': 'Client is out of date'})
        uicore.cmd.DoQuitGame()

    def CompareVersionsAndAct(self, bootbuild, bootversion, isAutoPatch, serverbuild, serverversion, statusMessage):
        if statusMessage is not None and 'Incompatible' in statusMessage[0] or '%.2f' % serverversion != '%.2f' % bootversion or serverbuild > bootbuild:
            if serverbuild > bootbuild and isAutoPatch:
                self.DisplayOutOfDateMessageAndQuitGame('OutOfDate')

    def GetActualStatusMessage(self, serverbuild, serverversion, statusMessage):
        self.serverStatusTextFunc = None
        if type(statusMessage) in (types.LambdaType, types.FunctionType, types.MethodType):
            self.serverStatusTextFunc = (statusMessage, serverversion, serverbuild)
        else:
            self.serverStatusTextFunc = (lambda : statusMessage, serverversion, serverbuild)
        self.__SetServerStatusText()
        resolvedStatusMessage = apply(self.serverStatusTextFunc[0])
        messagePart = resolvedStatusMessage[0]
        return messagePart

    @telemetry.ZONE_METHOD
    def InternalUpdateServerStatus(self, allowPatch, bootbuild, bootversion):
        self.SetStatusText(localization.GetByLabel('UI/Login/CheckingStatus'))
        self.serverStatusTextFunc = None
        blue.pyos.synchro.Yield()
        if self.isShowingUpdateDialog:
            return
        if not self.IsServerPortValid():
            return
        serverversion = serverbuild = servercodename = None
        isAutoPatch = self.GetIsAutoPatch(allowPatch)
        try:
            log.LogInfo('checking status of %s' % self.serverIP)
            try:
                if self.firstCheck:
                    forceQueueCheck = True
                    self.firstCheck = False
                else:
                    forceQueueCheck = False
                statusMessage, serverStatus = sm.GetService('machoNet').GetServerStatus('%s:%s' % (self.serverIP, self.serverPort), forceQueueCheck=forceQueueCheck)
            except UserError as e:
                if e.msg == 'AlreadyConnecting':
                    sys.exc_clear()
                    return
                raise

            if not self.isopen:
                return
            self.serverStatus[self.serverIP] = (serverStatus.get('boot_version', None),
             serverStatus.get('boot_build', None),
             str(serverStatus.get('boot_codename', const.responseUnknown)),
             serverStatus.get('update_info', const.responseUnknown))
            serverversion, serverbuild, servercodename, updateinfo = self.serverStatus[self.serverIP]
            actualStatusMsg = self.GetActualStatusMessage(serverbuild, serverversion, statusMessage)
            if serverversion and serverbuild:
                self.CompareVersionsAndAct(bootbuild, bootversion, isAutoPatch, serverbuild, serverversion, actualStatusMsg)
            elif actualStatusMsg is not None and 'IncompatibleProtocol' in actualStatusMsg:
                self.DisplayOutOfDateMessageAndQuitGame('Incompatable protocol')
            else:
                raise Exception('Invalid answer from server GetServerStatus')
        except Exception as e:
            log.LogException(e)
            sys.exc_clear()
            self.SetStatusText(localization.GetByLabel('UI/Login/UnableToConnect', IP=self.serverIP, port=self.serverPort))
            self.serverStatusTextFunc = None

    def SetNameText(self, text):
        if self.serverNameTextControl and not self.serverNameTextControl.destroyed:
            self.serverNameTextControl.text = text

    def SetStatusText(self, text):
        if self.serverStatusTextControl and not self.serverStatusTextControl.destroyed:
            self.serverStatusTextControl.text = text

    def SetVersionText(self, text):
        if self.serverVersionTextControl and not self.serverVersionTextControl.destroyed:
            self.serverVersionTextControl.text = text

    def ClearServerStatus(self, *args):
        self.SetStatusText('')
        self.serverStatusTextFunc = None
        return True

    def Connect(self, *args):
        uthread.new(self._Connect)

    @telemetry.ZONE_METHOD
    def _Connect(self):
        if self.connecting:
            return
        self.connecting = True
        giveFocus = None
        try:
            if sm.GetService('gameui').UsingSingleSignOn():
                for arg in blue.pyos.GetArg()[1:]:
                    if arg.startswith('/ssoToken'):
                        try:
                            argName, token = arg.split('=')
                        except:
                            raise RuntimeError('Invalid format of SSO token, should be /ssoToken=<token>')

                sm.GetService('gameui').DoLogin(token)
                return
            user = self.usernameEditCtrl.GetValue()
            password = fmtutil.PasswordString(self.passwordEditCtrl.GetValue(raw=1))
            giveFocus = None
            if user is None or len(user) == 0:
                giveFocus = 'username'
            if password is None or len(password) == 0:
                giveFocus = 'password' if giveFocus is None else giveFocus
            if giveFocus is not None:
                eve.Message('LoginAuthFailed')
                self.CancelLogin()
                self.SetFocus(giveFocus)
                return
            log.LogInfo('server: %s selected' % self.serverIP)
            blue.pyos.synchro.Yield()
            if self.serverPort == sm.StartService('machoNet').defaultProxyPortOffset:
                if self.serverIP not in self.serverStatus:
                    self.UpdateServerStatus()
                try:
                    serverversion, serverbuild, servercodename, updateinfo = self.serverStatus[self.serverIP]
                    if serverbuild > boot.build:
                        if self.serverIP == LIVE_SERVER:
                            response = eve.Message('PatchLiveServerConnectWrongVersion', {'serverVersion': serverbuild,
                             'clientVersion': boot.build}, uiconst.YESNO)
                            if response == uiconst.ID_YES:
                                self.UpdateServerStatus()
                        else:
                            eve.Message('PatchTestServerWarning', {'serverVersion': serverbuild,
                             'clientVersion': boot.build})
                        self.CancelLogin()
                        return
                except:
                    log.LogInfo('No serverStatus found for server %s' % self.serverIP)
                    sys.exc_clear()
                    eve.Message('UnableToConnectToServer')
                    self.CancelLogin()
                    return

            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Login/LoggingIn'), localization.GetByLabel('UI/Login/ConnectingToCluster'), 1, 100)
            blue.pyos.synchro.Yield()
            eve.Message('OnConnecting')
            blue.pyos.synchro.Yield()
            eve.Message('OnConnecting2')
            blue.pyos.synchro.Yield()
            try:
                sm.GetService('connection').Login([user,
                 password,
                 self.serverIP,
                 self.serverPort,
                 0])
            except Exception:
                self.CancelLogin()
                raise

            settings.public.ui.Set('username', user or '-')
            prefs.newbie = 0
            knownUserNames = settings.public.ui.Get('usernames', [])[:]
            if user and user not in knownUserNames:
                knownUserNames.append(user)
                settings.public.ui.Set('usernames', knownUserNames)
        except UserError as e:
            if e.msg.startswith('LoginAuthFailed'):
                giveFocus = 'password'
            eve.Message(e.msg, e.dict)
            self.CancelLogin()
            self.SetFocus(giveFocus)
        finally:
            if not self.destroyed:
                self.connecting = 0

    def CancelLogin(self):
        sm.GetService('loading').CleanUp()

    def SetFocus(self, where = None):
        if where is None:
            return
        if where == 'username':
            uicore.registry.SetFocus(self.usernameEditCtrl)
        elif where == 'password':
            self.passwordEditCtrl.SetValue('')
            uicore.registry.SetFocus(self.passwordEditCtrl)
