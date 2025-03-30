#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\gameui.py
import datetime
import sys
import blue
import datetimeutils
import gametime
import telemetry
import bluepy
import carbon.client.script.sys.appUtils as appUtils
import carbon.common.script.util.logUtil as log
import eve.common.script.net.eveMoniker as moniker
import evegraphics.settings as gfxsettings
import everesourceprefetch
import langutils
import localization
import logmodule
import paperdoll
import trinity
import uthread
from carbon.common.lib import const, serverInfo
from carbon.common.script.sys.service import Service, SERVICE_RUNNING, SERVICE_START_PENDING, ROLEMASK_ELEVATEDPLAYER
from carbonui import uiconst
from carbonui.control.contextMenu.menuUtil import ClearMenuLayer
from carbonui.text.settings import get_default_font_size_setting, get_font_size_setting, set_font_size_setting, update_font_size_factor
from carbonui.uicore import uicore, GetWindowName
from eve.client.script.parklife.messagebus.uiMessenger import UIMessenger
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.control.resourceLoadingIndicator import ResourceLoadingIndicator
from eve.client.script.ui.inflight.shipHud.safeLogoffTimer import SafeLogoffTimer, SafeLogoffTimer2
from eve.client.script.ui.mouseInputHandler import MouseInputHandler
from eve.client.script.ui.podGuide.megaMenuManager import MegaMenuManager
from eve.client.script.ui.services import sessionChangeWindowOpener
from eve.client.script.ui.shared.canNotStartTrainingWindow import CanNotStartTrainingClass
from eve.client.script.ui.shared.logOffWnd import LogOffWnd
from eve.client.script.ui.shared.messagebox import MessageBox
from eve.client.script.ui.shared.radioButtonMessageBox import RadioButtonMessageBox
from eve.client.script.ui.shared.sov.sovHub.changesWarning import ConfirmSovHubChanges
from eve.client.script.ui.shared.systemMenu.systemmenu import SystemMenu
from eve.client.script.ui.structure.structureBrowser.controllers.reinforceTimersBundle import ReinforcementBundle
from eve.client.script.ui.structure.structureHackingResult import StructureHackingResultWnd
from eve.client.script.ui.util.disconnectNotice import DisconnectNotice
from eve.client.script.ui.view.viewStateConfig import SetupViewStates
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.lib import appConst
from eve.common.script.sys import eveCfg
from eveexceptions import ExceptionEater
from evegraphics.environments.environmentManager import EnvironmentManager
from eveprefs import prefs
from evespacescene.playerdeath import PlayerDeathHandler
from evespacescene.routevisualizer import RouteVisualizer
from evetypes import GetVolume
from globalConfig import AllowCharacterLogoff
from inventoryutil.client.cargo_utils import get_cargo_volume_available
from kiring.client.apigateway import get_kiring_api_gateway
from kiring.common.const import ANTI_ADDICTION_CHECK_FAIL_JUVENILES_BLOCK_AFTER_22_AND_BEFORE_8, ANTI_ADDICTION_CHECK_FAIL_JUVENILES_PLAY_TIME_OVERFLOW, ANTI_ADDICTION_CHECK_FAIL_JUVENILES_PLAY_TIME_OVERFLOW_HOLIDAY
from newFeatures import newFeatureNotify
from operations.client.operationscontroller import ReleaseOperationsController
from operations.client.tutorialOperationsController import ReleaseTutorialOperationsController
from regionalui import manager
from sceneManagerConsts import SCENE_TYPE_SPACE
from sovereignty.mercenaryden.client.qa.settings.should_mock_data import ShouldMockSetting
from sovereignty.mercenaryden.client.repository import setup_singleton
from spacecomponents.client.components.mercenaryDen import extract_infomorphs_to_ship
CUSTOM_MESSAGE_BOXES = {'UserAlreadyHasSkillInTraining': CanNotStartTrainingClass,
 'ConfirmSovHubUpgradeChanges': ConfirmSovHubChanges}
CUSTOM_MESSAGE_BOX_CLASSES = {'AskQuitGame': LogOffWnd}
AFK_THRESHOLD = datetime.timedelta(minutes=5)
DEFAULT_RESOURCE_LOADING_WHEEL_ALIGN = uiconst.BOTTOMLEFT
DEFAULT_RESOURCE_LOADING_WHEEL_SIZE = 32
DEFAULT_RESOURCE_LOADING_WHEEL_LEFT = 12
DEFAULT_RESOURCE_LOADING_WHEEL_TOP = 12

class GameUI(Service):
    __guid__ = 'svc.gameui'
    __exportedcalls__ = {'StartupUI': [],
     'MessageBox': [],
     'GetShipAccess': []}
    __startupdependencies__ = ['device',
     'settings',
     'viewState',
     'publicGatewaySvc',
     'ui_blinker',
     'station',
     'seasonService']
    __dependencies__ = ['michelle',
     'machoNet',
     'inv',
     'neocom',
     'infoPanel',
     'shipTreeUI',
     'agencyNew',
     'redeem',
     'sov',
     'epicArc']
    __notifyevents__ = ['OnConnectionRefused',
     'OnDisconnect',
     'OnServerMessage',
     'OnRemoteMessage',
     'DoSessionChanging',
     'ProcessSessionChange',
     'OnSessionChanged',
     'DoBallsAdded',
     'OnNewState',
     'OnClusterShutdownInitiated',
     'OnClusterShutdownCancelled',
     'OnJumpQueueMessage',
     'OnViewStateChanged',
     'OnSetDevice',
     'OnCreateNewMailWindow',
     'OnStructureHacked',
     'OnPodKilled',
     'DoBallClear',
     'OnAntiAddictionOnlineTimeWarning',
     'OnAntiAddictionOnlineTimeBlockWarning',
     'OnSafeLogoffTimerStarted',
     'OnSafeLogoffActivated',
     'OnSafeLogoffAborted',
     'OnSafeLogoffFailed']

    def __init__(self):
        self.state = SERVICE_START_PENDING
        super(GameUI, self).__init__()
        self.wannaBeEgo = -1
        self.languages = None
        self.shutdownTime = None
        self.podKillPodID = None
        self.sceneManager = None
        self.playerDeathHandler = None
        self.routeVisualizer = None
        self.uiLayerList = None
        self.shipAccess = None
        self.regionalUiManager = manager.RegionalUserInterfaceManager(self)
        self.logoffTimer = None
        self._is_afk = False
        self._last_ui_interaction_timestamp = None
        self.ui_messenger = None

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        self.ui_messenger = UIMessenger(self.publicGatewaySvc)
        self.sceneManager = sm.GetService('sceneManager')
        self.playerDeathHandler = PlayerDeathHandler(self.sceneManager)
        self.routeVisualizer = RouteVisualizer()
        update_font_size_factor()
        defaults = {'debug': 0,
         'port': sm.services['machoNet'].defaultProxyPortOffset,
         'newbie': 1,
         'inputhost': 'localhost',
         'digit': ',',
         'decimal': '.',
         'eulaagreed': 0,
         'host': 0}
        for k, v in defaults.items():
            if not prefs.HasKey(k):
                prefs.SetValue(k, v)

        self.uiLayerList = [('l_hint', None, None),
         ('l_dragging', None, None),
         ('l_menu', None, None),
         ('l_mloading', None, None),
         ('l_modal', None, [('l_loadingFill', None, None), ('l_systemmenu', SystemMenu, None)]),
         ('l_utilmenu', None, None),
         ('l_alwaysvisible', None, None),
         ('l_abovemain', None, None),
         ('l_loading', None, None),
         ('l_videoOverlay', None, None),
         ('l_infoBubble', None, None),
         ('l_main', None, None),
         ('l_viewstate', None, None)]
        self.shipAccess = None
        self.state = SERVICE_RUNNING
        uthread.worker('gameui::ShutdownTimer', self.__ShutdownTimer)
        uthread.worker('gameui::SessionTimeoutTimer', self.__SessionTimeoutTimer)
        uthread.new(self._UpdateCrashKeyValues).context = 'gameui::_UpdateCrashKeyValues'

    def _UpdateCrashKeyValues(self):
        self.LogInfo('UpdateCrashKeyValues loop starting')
        stats = []
        try:
            info = serverInfo.GetServerInfo()
            blue.SetCrashKeyValues('serverName', info.name)
            blue.SetCrashKeyValues('serverIP', info.IP)
        except:
            log.LogException()

        statNames = ['Blue/Memory/Malloc',
         'Blue/Memory/Python',
         'Blue/Memory/PageFileUsage',
         'Blue/Memory/WorkingSet']
        for each in statNames:
            s = blue.statistics.Find(each)
            if s:
                stats.append(s)

        while self.state == SERVICE_RUNNING:
            for each in stats:
                blue.SetCrashKeyValues(each.name, str(each.value))

            blue.SetCrashKeyValues('Trinity_shader_model', trinity.GetShaderModel())
            blue.synchro.SleepWallclock(5000)

    def GetShipAccess(self):
        if self.shipAccess is not None:
            shipAccess, locationID, shipID, charID = self.shipAccess
            if locationID != eve.session.solarsystemid or eve.session.stationid:
                self.shipAccess = None
            elif shipID != eve.session.shipid:
                self.shipAccess = None
            elif charID != eve.session.charid:
                self.shipAccess = None
        if self.shipAccess is None:
            self.shipAccess = [moniker.GetShipAccess(),
             eve.session.solarsystemid or eve.session.stationid,
             eve.session.shipid,
             eve.session.charid]
        return self.shipAccess[0]

    def OnDisconnect(self, reason = 0, msg = ''):
        if self.HasDisconnectionNotice():
            return
        disconnectNotice = DisconnectNotice(logProvider=self)
        disconnectNotice.OnDisconnect(reason, msg)

    @staticmethod
    def OnConnectionRefused():
        sm.GetService('loading').CleanUp()

    def OnServerMessage(self, msg):
        uthread.new(self.OnServerMessage_thread, msg).context = 'gameui.ServerMessage'

    @staticmethod
    def OnServerMessage_thread(msg):
        if isinstance(msg, tuple) and len(msg) == 2:
            label, kwargs = msg
            msg = localization.GetByLabel(label, **kwargs)
        eve.Message('ServerMessage', {'msg': msg})

    def OnClusterShutdownInitiated(self, explanationLabel, when, duration):
        self.shutdownTime = when

    def OnJumpQueueMessage(self, msg, ready):
        ShowQuickMessage(msg)

    def OnClusterShutdownCancelled(self, explanationLabel):
        self.shutdownTime = None

    def __ShutdownTimer(self):
        while self.state == SERVICE_RUNNING:
            try:
                if self.shutdownTime and self.shutdownTime - blue.os.GetWallclockTime() < 5 * const.MIN:
                    timeLeft = max(0L, self.shutdownTime - blue.os.GetWallclockTime())
                    ShowQuickMessage(localization.GetByLabel('UI/Shared/ClusterShutdownInSeconds', timeLeft=timeLeft))
            except StandardError:
                log.LogException()
                sys.exc_clear()

            blue.pyos.synchro.SleepWallclock(5000)

    def __SessionTimeoutTimer(self):
        while self.state == SERVICE_RUNNING:
            try:
                if eve.session.maxSessionTime and eve.session.maxSessionTime - blue.os.GetWallclockTime() < 15 * const.MIN:
                    ShowQuickMessage(localization.GetByLabel('UI/Shared/MaxSessionTimeExpiring', timeLeft=eve.session.maxSessionTime - blue.os.GetWallclockTime()))
            except StandardError:
                log.LogException()
                sys.exc_clear()

            blue.pyos.synchro.SleepWallclock(5000)

    def _start_afk_monitor(self):
        uicore.uilib.RegisterForTriuiEvents([uiconst.UI_MOUSEDOWN,
         uiconst.UI_MOUSEUP,
         uiconst.UI_MOUSEWHEEL,
         uiconst.UI_KEYDOWN], self._handle_global_ui_event)
        uthread.worker('gameui._afk_timer_loop', self._afk_timer_loop)

    def _handle_global_ui_event(self, *args, **kwargs):
        self._last_ui_interaction_timestamp = gametime.now()
        return self.state == SERVICE_RUNNING

    def _afk_timer_loop(self):
        last_observed_active_timestamp = self._last_ui_interaction_timestamp
        while self.state == SERVICE_RUNNING:
            blue.pyos.synchro.SleepWallclock(1000)
            try:
                if session.charid is None:
                    continue
                if self._last_ui_interaction_timestamp is None:
                    continue
                dt_since_active = gametime.now() - self._last_ui_interaction_timestamp
                if not self._is_afk and dt_since_active > AFK_THRESHOLD:
                    self._is_afk = True
                    self.LogNotice('I am now AFK after being idle for {dt} seconds.'.format(dt=dt_since_active.total_seconds()))
                    self.ui_messenger.idle_threshold_reached(AFK_THRESHOLD)
                    sm.RemoteSvc('charMgr').SetActivityStatus(status=appConst.PLAYER_STATUS_AFK, extraInfo=datetimeutils.datetime_to_filetime(self._last_ui_interaction_timestamp))
                elif self._is_afk and dt_since_active < AFK_THRESHOLD:
                    self._is_afk = False
                    self.LogNotice('I am no longer AFK after being idle for {dt} seconds.'.format(dt=(gametime.now() - last_observed_active_timestamp).total_seconds()))
                    self.ui_messenger.activity_resumed()
                    sm.RemoteSvc('charMgr').SetActivityStatus(status=appConst.PLAYER_STATUS_ACTIVE, extraInfo=datetimeutils.datetime_to_filetime(last_observed_active_timestamp))
                last_observed_active_timestamp = self._last_ui_interaction_timestamp
            except Exception:
                log.LogException()
                sys.exc_clear()

    @staticmethod
    def OnRemoteMessage(msgID, dict = None, kw = None):
        if kw is None:
            kw = {}
        remoteNotifyMessages = ('SelfDestructInitiatedOther', 'SelfDestructImmediateOther', 'SelfDestructAbortedOther2')
        if msgID in remoteNotifyMessages and not settings.user.ui.Get('notifyMessagesEnabled', 1):
            return
        uthread.new(eve.Message, msgID, dict, **kw).context = 'gameui.ServerMessage'

    @staticmethod
    def TransitionCleanup(change):
        ClearMenuLayer()
        uicore.layer.utilmenu.Flush()
        for each in uicore.registry.GetWindows()[:]:
            if each.name.startswith('infowindow') and 'shipid' in change and each.sr.itemID in change['shipid']:
                each.Close()

    def ClearCacheFiles(self):
        if eve.Message('AskClearCacheReboot', {}, uiconst.YESNO) == uiconst.ID_YES:
            prefs.clearcache = 1
            appUtils.Reboot('clear cache')

    def ClearSettings(self):
        if eve.Message('AskClearSettingsReboot', {}, uiconst.YESNO) == uiconst.ID_YES:
            prefs.resetsettings = 1
            appUtils.Reboot('clear settings')

    @telemetry.ZONE_METHOD
    def ProcessSessionChange(self, isRemote, session, change, cheat = 0):
        self.settings.SaveSettings()
        self.LogInfo('ProcessSessionChange: ', change, ',', session)

    def DoSessionChanging(self, isRemote, session, change):
        wasPodded, movedToStructure, movedToStation = self._ParseStateChange(change)
        if wasPodded:
            view = ViewState.Hangar
            viewState = sm.GetService('viewState')
            viewState.SetTransitionReason(viewState.GetCurrentViewInfo().name, view, 'clone')
        self.TransitionCleanup(change)
        if 'charid' in change and change['charid'][0] or 'userid' in change and change['userid'][0]:
            self.shipAccess = None

    def _ParseStateChange(self, change):
        movedFromDestroyedPod = 'shipid' in change and self.podKillPodID and self.podKillPodID == change['shipid'][0]
        movedToStation = 'stationid' in change and change['stationid'][1] is not None
        movedToStructure = 'structureid' in change and change['structureid'][1] is not None
        wasPodded = movedFromDestroyedPod and (movedToStation or movedToStructure)
        return (wasPodded, movedToStructure, movedToStation)

    @staticmethod
    def OnSetDevice(*args):
        uicore.layer.utilmenu.Flush()

    @staticmethod
    def OnViewStateChanged(oldView, newView):
        uicore.layer.utilmenu.Flush()
        if oldView == ViewState.CharacterSelector:
            newFeatureNotify.CheckOpenNewFeatureNotifyWindow()
        if oldView == ViewState.CharacterSelector or oldView == ViewState.CharacterCreation and newView == ViewState.Hangar:
            sm.GetService('activities').CheckIfLoginOpenWindowEnabled()
        if newView == ViewState.CharacterSelector:
            sm.GetService('activities').AfterLogout()

    @staticmethod
    def AnythingImportantInChange(change):
        ignoreKeys = ('fleetid', 'wingid', 'squadid', 'fleetrole', 'languageID')
        ck = change.keys()
        for k in ignoreKeys:
            try:
                ck.remove(k)
            except ValueError:
                pass

        return bool(ck)

    @telemetry.ZONE_METHOD
    def OnSessionChanged(self, isRemote, session, change):
        if not self.AnythingImportantInChange(change):
            return
        relevantSessionAttributes = ('userid', 'charid', 'solarsystemid', 'stationid', 'structureid', 'shipid')
        changeIsRelevant = False
        for attribute in relevantSessionAttributes:
            if attribute in change:
                changeIsRelevant = True
                break

        if not changeIsRelevant:
            return
        if 'userid' in change:
            sm.GetService('tactical')
            sm.GetService('cloneGradeSvc').PrimeCloneState()
            uicore.mouseInputHandler = MouseInputHandler()
        if 'charid' in change:
            self.OnCharacterSelected()
        if 'userid' in change or 'charid' in change:
            self.settings.LoadSettings()
            gfx = gfxsettings.GraphicsSettings.GetGlobal()
            gfx.InitializeSettingsGroup(gfxsettings.SETTINGS_GROUP_UI, settings.user.ui)
            self.device.ApplyTrinityUserSettings()
        if 'shipid' in change and session.sessionChangeReason == 'selfdestruct':
            session.sessionChangeReason = 'board'
        if session.charid is None:
            self._HandleUserLogonSessionChange(isRemote, session, change, self.viewState)
        elif session.stationid is not None:
            self._HandleSessionChangeInStation(isRemote, session, change, self.viewState)
        elif session.structureid is not None:
            self._HandleSessionChangeInStructure(isRemote, session, change, self.viewState)
        elif session.solarsystemid is not None:
            self._HandleSessionChangeInSpace(isRemote, session, change, self.viewState)
        else:
            self.LogWarn('GameUI::OnSessionChanged, Lame Teardown of the client, it should get propper OnDisconnect event', isRemote, session, change)

    def DoCharacterLogoff(self):
        sm.GetService('cc').ClearCharacterSelectionData()
        sm.GetService('jumpQueue').PrepareQueueForCharID(None)
        self.LogInfo('ChainEvent ProcessSessionReset with current session', session)
        sm.ChainEvent('ProcessSessionReset')
        self.LogInfo('Closing game windows')
        sessionChangeWindowOpener.CloseOutOfScopeWindows(uiconst.SCOPE_NONE)
        viewStateSvc = sm.GetService('viewState')
        viewStateSvc.CloseSecondaryView()
        self.LogInfo('ScatterEvent OnSessionReset with current session', session)
        sm.ScatterEvent('OnSessionReset')
        ReleaseOperationsController()
        ReleaseTutorialOperationsController()
        self.LogInfo('Switching to character selection', session)
        viewStateSvc.ActivateView('charsel')
        trinity.app.title = GetWindowName()
        self.LogNotice('Character logoff complete')

    def LogOffCharacter(self):
        self.LogNotice('Logging out character %s' % cfg.eveowners.Get(session.charid).name)
        with ExceptionEater('Failed to persist achievements'):
            achievementsUpdated = sm.GetService('achievementSvc').CheckAchievementStatus()
            if not achievementsUpdated:
                sm.GetService('achievementSvc').UpdateClientAchievementsAndCountersOnServer()
        if sm.GetService('sessionMgr').PerformSessionChange('logoff', sm.RemoteSvc('userSvc').UserLogOffCharacter):
            return self.DoCharacterLogoff()
        self.LogNotice('Character logoff denied')

    def OnCharacterSelected(self):
        sm.ScatterEvent('OnCharacterSelected')
        self.DoWindowIdentification()

    @staticmethod
    def _CheckSessionLanguage(userSession):
        prefsLang = langutils.any_to_comfy_language(prefs.GetValue('languageID', None))
        sessionLang = langutils.any_to_comfy_language(userSession.languageID)
        if prefsLang != sessionLang:
            userSession.__dict__['languageID'] = prefsLang.mls_language_id()

    def AlertAntiAddictionDialogBoxAndQuit(self, message):
        if eve.Message(message, {}, uiconst.OK) in (uiconst.ID_OK, uiconst.ID_CLOSE, uiconst.ID_CANCEL):
            uicore.cmd.DoQuitGame()

    def CheckAntiAddiction(self):
        if not localization.util.AmOnChineseServer():
            return
        kiringApiGateway = get_kiring_api_gateway()
        code = kiringApiGateway.check_anti_addiction()
        log.LogInfo('anti-addiction login check code: %s' % code)
        if code == ANTI_ADDICTION_CHECK_FAIL_JUVENILES_BLOCK_AFTER_22_AND_BEFORE_8:
            self.AlertAntiAddictionDialogBoxAndQuit('AntiAddictionLoginTimeBlock')
        elif code == ANTI_ADDICTION_CHECK_FAIL_JUVENILES_PLAY_TIME_OVERFLOW:
            self.AlertAntiAddictionDialogBoxAndQuit('AntiAddictionLoginBlock')
        elif code == ANTI_ADDICTION_CHECK_FAIL_JUVENILES_PLAY_TIME_OVERFLOW_HOLIDAY:
            self.AlertAntiAddictionDialogBoxAndQuit('AntiAddictionLoginBlockHoliday')

    def _HandleUserLogonSessionChange(self, isRemote, session, change, viewSvc):
        self._CheckSessionLanguage(session)
        self.regionalUiManager.on_login(session)
        self.CheckAntiAddiction()
        self.LogNotice('GameUI::OnSessionChanged, Heading for character selection', isRemote, session, change)
        self.regionalUiManager.on_splash_screen(session)
        characters = sm.GetService('cc').GetCharactersToSelect(False)
        if characters:
            uthread.pool('GameUI::ActivateView::charsel', viewSvc.ActivateView, 'charsel')
        else:
            uthread.pool('GameUI::GoCharacterCreation', self.GoCharacterCreation)

    def _GetStationView(self):
        view = settings.user.ui.Get('defaultDockingView', ViewState.Hangar)
        if view == 'station':
            view = ViewState.Hangar
        return view

    def _GetStructureView(self):
        return settings.user.ui.Get('defaultStructureView', ViewState.Hangar)

    def _GetActivateViewFunction(self, viewSvc):
        if viewSvc.IsViewActive('charactercreation'):
            activateViewFunc = viewSvc.ActivateView
        else:
            activateViewFunc = viewSvc.ChangePrimaryView
        return activateViewFunc

    def _HandleSessionChangeInStation(self, isRemote, session, change, viewSvc):
        if 'stationid' in change:
            self.LogNotice('GameUI::OnSessionChanged, Heading for station', isRemote, session, change)
            activateViewFunc = self._GetActivateViewFunction(viewSvc)
            view = self._GetStationView()
            uthread.pool('GameUI::ActivateView::station', activateViewFunc, view, change=change)

    def _HandleSessionChangeInStructure(self, isRemote, session, change, viewSvc):
        if not ('shipid' in change or 'structureid' in change):
            return
        structureView = None
        wasPodded, movedToStructure, _ = self._ParseStateChange(change)
        if movedToStructure:
            if 'shipid' in change and session.shipid == session.structureid:
                uicore.layer.shipui.CloseView(recreate=False)
                structureView = ViewState.Space
            elif wasPodded:
                structureView = ViewState.Hangar
                settings.user.ui.Set('defaultStructureView', structureView)
            else:
                structureView = self._GetStructureView()
        elif 'shipid' in change and session.structureid:
            if session.shipid == session.structureid:
                structureView = ViewState.Space
            elif not self.viewState.IsViewActive('structure', 'hangar'):
                structureView = self._GetStructureView()
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark and session.structureid in ballpark.balls:
            ballpark.ego = session.structureid
            self.wannaBeEgo = -1
            self.OnNewState(ballpark)
        else:
            self.LogNotice('_HandleSessionChangeInStructure:  Postponing ego assignment to', session.structureid, 'until ballpark is ready')
            self.wannaBeEgo = session.structureid
        if structureView:
            uthread.pool('GameUI::ActivateView::structure', self._GetActivateViewFunction(viewSvc), structureView, change=change)

    def _HandleSessionChangeInSpace(self, isRemote, session, change, viewSvc):
        bp = sm.GetService('michelle').GetBallpark()
        if 'solarsystemid' in change:
            oldSolarSystemID, newSolarSystemID = change['solarsystemid']
            if oldSolarSystemID:
                sm.GetService('FxSequencer').ClearAll()
                self.LogInfo('Cleared effects')
            if bp and session.shipid in bp.balls:
                self.LogNotice('GameUI::OnSessionChanged, Heading for inflight with a valid ego', isRemote, session, change)
                bp.ego = session.shipid
                self.wannaBeEgo = -1
            else:
                self.LogNotice('GameUI::OnSessionChanged:%s - Activating space view without a ego ball properly inserted into a proper ballpark.' % (change,))
                self.wannaBeEgo = session.shipid
            uthread.pool('GameUI::ChangePrimaryView::inflight', self._GetActivateViewFunction(viewSvc), 'inflight', change=change)
        else:
            if 'shipid' in change and change['shipid'][1] is not None and bp is not None:
                uthread.new(sm.GetService('target').ClearTargets)
                if session.shipid in bp.balls:
                    self.LogNotice('Changing ego:', bp.ego, '->', session.shipid)
                    bp.ego = session.shipid
                    self.wannaBeEgo = -1
                    self.OnNewState(bp)
                else:
                    self.LogNotice('Postponing ego:', bp.ego, '->', session.shipid)
                    self.wannaBeEgo = session.shipid
            if 'structureid' in change:
                self.LogNotice('GameUI::OnSessionChanged, Heading for inflight', isRemote, session, change)
                uthread.pool('GameUI::ChangePrimaryView::inflight', self._GetActivateViewFunction(viewSvc), 'inflight', change=change)
                if bp and session.shipid in bp.balls:
                    bp.ego = session.shipid
                    self.wannaBeEgo = -1
                    self.OnNewState(bp)
                else:
                    self.wannaBeEgo = session.shipid
            if 'shipid' in change and 'structureid' in change:
                uicore.layer.shipui.CloseView(recreate=False)

    def StartupUI(self, *args):
        uthread.new(_ScheduleBackgroundDownloads)
        self.usingSingleSignOn = False
        uicore.SetAudioHandler(sm.StartService('audio'))
        uicore.Startup(self.uiLayerList)
        desktopIndex = uicore.desktop.children.index(uicore.layer.hint)
        self.resourceLoadingIndicator = ResourceLoadingIndicator(parent=uicore.desktop, align=DEFAULT_RESOURCE_LOADING_WHEEL_ALIGN, width=DEFAULT_RESOURCE_LOADING_WHEEL_SIZE, height=DEFAULT_RESOURCE_LOADING_WHEEL_SIZE, left=DEFAULT_RESOURCE_LOADING_WHEEL_LEFT, top=DEFAULT_RESOURCE_LOADING_WHEEL_TOP, isGlobal=True, idx=desktopIndex)
        uicore.SetCommandHandler(sm.StartService('cmd'))
        import eve.client.script.ui.control.tooltips as tooltipHandler
        uicore.SetTooltipHandler(tooltipHandler)
        uicore.Message = eve.Message
        logmodule.SetUiMessageFunc(uicore.Message)
        SetupViewStates(self.viewState, uicore.layer.viewstate)
        sm.GetService('device').SetupUIScaling()
        sceneManager = sm.StartService('sceneManager')
        sceneManager.SetSceneType(SCENE_TYPE_SPACE)
        sceneManager.Initialize(trinity.EveSpaceScene())
        self.RegisterBlueResources()
        sm.StartService('connection')
        sm.StartService('logger')
        sm.StartService('ownerprimer')
        sm.StartService('petition')
        sm.StartService('ui')
        sm.StartService('window')
        sm.StartService('log')
        sm.StartService('consider')
        sm.StartService('incursion')
        sm.StartService('moonScan')
        sm.StartService('preview')
        sm.StartService('crimewatchSvc')
        sm.StartService('flightControls')
        sm.StartService('flightPredictionSvc')
        sm.StartService('sensorSuite')
        sm.StartService('hackingUI')
        sm.StartService('radialmenu')
        sm.StartService('tourneyUISvc')
        sm.StartService('achievementSvc')
        sm.StartService('contextualOfferSvc')
        sm.StartService('tacticalNavigation')
        sm.StartService('subway')
        sm.StartService('paperDollClient')
        setup_singleton(self.publicGatewaySvc, GetVolume, get_cargo_volume_available, extract_infomorphs_to_ship, ShouldMockSetting())
        uicore.megaMenuManager = MegaMenuManager()
        token = None
        for arg in blue.pyos.GetArg()[1:]:
            if arg.startswith('/ssoToken'):
                try:
                    argName, token = arg.split('=')
                except:
                    raise RuntimeError('Invalid format of SSO token, should be /ssoToken=<token>')

        if token is not None:
            self.usingSingleSignOn = True
            self.DoLogin(token)
        else:
            self.viewState.ActivateView('login')
        self._start_afk_monitor()

    def RegisterBlueResources(self):
        from carbon.client.script.graphics.resourceConstructors.gradients import Gradient, GradientRadial, Gradient2D
        blue.resMan.RegisterResourceConstructor('gradient', Gradient)
        blue.resMan.RegisterResourceConstructor('gradient_radial', GradientRadial)
        blue.resMan.RegisterResourceConstructor('gradient2d', Gradient2D)

    def _IsResourceLoadingIndicatorAvailable(self):
        return self.resourceLoadingIndicator and not self.resourceLoadingIndicator.destroyed

    def EnableResourceLoadingIndicator(self):
        if self._IsResourceLoadingIndicatorAvailable():
            self.resourceLoadingIndicator.Enable()

    def DisableResourceLoadingIndicator(self):
        if self._IsResourceLoadingIndicatorAvailable():
            self.resourceLoadingIndicator.Disable()

    def MoveResourceLoadingIndicator(self, newAlignment, newLeft, newTop):
        if self._IsResourceLoadingIndicatorAvailable():
            self.resourceLoadingIndicator.align = newAlignment
            self.resourceLoadingIndicator.left = newLeft
            self.resourceLoadingIndicator.top = newTop

    def ResetResourceLoadingIndicatorPosition(self):
        self.MoveResourceLoadingIndicator(newAlignment=DEFAULT_RESOURCE_LOADING_WHEEL_ALIGN, newLeft=DEFAULT_RESOURCE_LOADING_WHEEL_LEFT, newTop=DEFAULT_RESOURCE_LOADING_WHEEL_TOP)

    def DoLogin(self, token):
        sm.ScatterEvent('OnClientReady', 'login')
        try:
            sm.GetService('connection').LoginSso(token)
        except:
            sm.GetService('loading').CleanUp()
            self.viewState.ActivateView('login')
            raise

    def SetLanguage(self, key, doReload = False):
        is_cool = bool(session.role & ROLEMASK_ELEVATEDPLAYER)
        if is_cool:
            comfylang = langutils.any_to_comfy_language(key)
        else:
            comfylang = langutils.client_valid_or_default(key)
        if comfylang != prefs.GetValue('languageID', None):
            if session.userid is not None:
                sm.RemoteSvc('authentication').SetLanguageID(comfylang.mls_language_id())
            session.__dict__['languageID'] = comfylang.mls_language_id()
            prefs.languageID = comfylang.mls_language_id()
            blue.os.languageID = comfylang.mls_language_id()
            if doReload:
                localization.LoadLanguageData()
                setting = get_default_font_size_setting(comfylang.mls_language_id())
                if setting > get_font_size_setting():
                    set_font_size_setting(setting)
            sm.ChainEvent('ProcessUIRefresh')
            sm.ScatterEvent('OnUIRefresh')
            sm.ScatterEvent('OnLanguageChanged', comfylang.code)

    def GoCharacterCreationCurrentCharacter(self, *args):
        if None in (session.charid, session.genderID, session.bloodlineID):
            return
        if self.viewState.IsViewActive('charactercreation'):
            return
        if sm.GetService('undocking').IsExiting():
            return
        stationSvc = sm.GetService('station')
        dollState = stationSvc.GetPaperdollStateCache()
        msg = None
        if dollState == paperdoll.State.resculpting:
            msg = 'AskRecustomizeCharacter'
        elif dollState == paperdoll.State.full_recustomizing:
            msg = 'AskRecustomizeCharacterChangeBloodline'
        message = uiconst.ID_NO
        if msg is not None:
            message = eve.Message(msg, {'charName': cfg.eveowners.Get(session.charid).ownerName}, uiconst.YESNO, default=uiconst.ID_NO, suppress=uiconst.ID_NO)
        if message == uiconst.ID_YES:
            self.GoCharacterCreation(session.charid, session.genderID, session.raceID, session.bloodlineID, dollState=dollState)
            stationSvc.ClearPaperdollStateCache()
        elif message == uiconst.ID_NO:
            self.GoCharacterCreation(session.charid, session.genderID, session.raceID, session.bloodlineID, dollState=paperdoll.State.no_recustomization)

    def GoCharacterCreation(self, charID = None, gender = None, raceID = None, bloodlineID = None, dollState = None, *args):
        if sm.GetService('undocking').IsExiting():
            return
        everesourceprefetch.PullToFront('ui_cc')
        self.viewState.ActivateView('charactercreation', charID=charID, gender=gender, raceID=raceID, bloodlineID=bloodlineID, dollState=dollState)

    def HasDisconnectionNotice(self):
        return MessageBox.IsOpen(windowID='DisconnectNotice')

    def MessageBox(self, text, title = 'EVE', buttons = None, icon = None, suppText = None, customicon = None, height = None, blockconfirmonreturn = 0, default = None, modal = True, msgkey = None, messageData = None, customMsgBox = None, isClosable = True):
        if not getattr(uicore, 'desktop', None):
            return
        if self.HasDisconnectionNotice():
            return (default, False)
        msgBoxClass = MessageBox
        msgBoxParams = {'useDefaultPos': True,
         'msgKey': msgkey}
        if customMsgBox is not None:
            msgBoxClass, extraMsgBoxParams = customMsgBox
            msgBoxParams.update(extraMsgBoxParams)
        elif msgkey in CUSTOM_MESSAGE_BOX_CLASSES:
            msgBoxClass = CUSTOM_MESSAGE_BOX_CLASSES[msgkey]
        if buttons is None:
            buttons = uiconst.ID_OK
        msgbox = msgBoxClass(**msgBoxParams)
        msgbox.state = uiconst.UI_HIDDEN
        msgbox.isModal = modal
        msgbox.blockconfirmonreturn = blockconfirmonreturn
        if msgkey is not None and msgkey in CUSTOM_MESSAGE_BOXES:
            msgbox.ExecuteCustomContent(CUSTOM_MESSAGE_BOXES[msgkey], title, buttons, icon, suppText, customicon, height, default=default, modal=modal, messageData=messageData, isClosable=isClosable)
        else:
            msgbox.Execute(text, title, buttons, icon, suppText, customicon, height, default=default, modal=modal, isClosable=isClosable)
        if modal:
            ret = msgbox.ShowModal()
        else:
            ret = msgbox.ShowDialog()
        return (ret, msgbox.suppress)

    def RadioButtonMessageBox(self, text, title = 'EVE', buttons = None, icon = None, suppText = None, customicon = None, radioOptions = None, height = None, width = None, blockconfirmonreturn = 0, default = None, modal = True):
        if radioOptions is None:
            radioOptions = []
        if not getattr(uicore, 'desktop', None):
            return
        if self.HasDisconnectionNotice():
            return (default, False)
        if buttons is None:
            buttons = uiconst.ID_OK
        msgbox = RadioButtonMessageBox(useDefaultPos=True)
        msgbox.isModal = modal
        msgbox.blockconfirmonreturn = blockconfirmonreturn
        msgbox.Execute(text, title, buttons, icon, suppText, customicon, height, radioOptions=radioOptions, width=width, default=default, modal=modal)
        if modal:
            buttonResult = msgbox.ShowModal()
            radioSelection = msgbox.GetRadioSelection()
            ret = (buttonResult, radioSelection)
        else:
            buttonResult = msgbox.ShowDialog()
            radioSelection = msgbox.GetRadioSelection()
            ret = (buttonResult, radioSelection)
        return (ret, msgbox.suppress)

    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::gameui')
        try:
            return self.DoBallsAdded_(*args, **kw)
        finally:
            t.PopTimer(timer)

    def DoBallsAdded_(self, lst):
        for each in lst:
            self.DoBallAdd(*each)

    def DoBallAdd(self, ball, slimItem):
        if ball.id == self.wannaBeEgo:
            self.LogNotice('Ego-wannabe', self.wannaBeEgo, 'added to park')
            bp = sm.GetService('michelle').GetBallpark()
            if bp.ego != self.wannaBeEgo:
                self.LogNotice('Post-ego change: ', bp.ego, '->', self.wannaBeEgo)
                bp.ego = self.wannaBeEgo
                self.OnNewState(bp)
            self.wannaBeEgo = -1
            sm.ScatterEvent('OnDoBallAddEgoChange')

    def DoBallClear(self, solItem):
        if sm.GetService('subway').Enabled() and sm.GetService('subway').InJump():
            return
        uthread.new(self._DoBallClear, solItem)

    def _DoBallClear(self, solItem):
        spaceToSpaceTransition = self.viewState.GetTransitionByName('inflight', 'inflight')
        sm.GetService('tactical').TearDownOverlay()
        sc = self.sceneManager.GetScene()
        if spaceToSpaceTransition.active:
            spaceToSpaceTransition.Finalize()
        else:
            self.sceneManager.UnregisterScene('default', ignoreCamera=True)
            self.sceneManager.LoadScene(sc, registerKey='default')
            self.sceneManager.ApplySpaceScene()
            EnvironmentManager.GetInstance().RefreshEnvironments()
        if eve.session.solarsystemid:
            sm.GetService('tactical').CheckInit()

    def OnNewState(self, bp):
        uthread.pool('GameUI::New shipui state', self._NewState, bp)

    @telemetry.ZONE_METHOD
    def _NewState(self, bp):
        if bp and bp.balls.get(bp.ego, None):
            if eveCfg.InSpace() and uicore.layer.shipui.isopen:
                uicore.layer.shipui.SetupShip(False)
            camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
            camera.LookAtMaintainDistance(bp.ego)

    def DoWindowIdentification(self):
        trinity.app.title = GetWindowName(session.charid)

    def UsingSingleSignOn(self):
        return getattr(self, 'usingSingleSignOn', False)

    def OnCreateNewMailWindow(self, recipients, corpOrAllianceRecipient, toListID, subject, body):
        sm.GetService('mailSvc').SendMsgDlg(toCharacterIDs=recipients, toCorpOrAllianceID=corpOrAllianceRecipient, toListID=toListID, subject=subject, body=body)

    def OnAntiAddictionOnlineTimeWarning(self, countdownSecond, playedSecond):
        accruedTime = localization.formatters.FormatTimeIntervalWritten(int(playedSecond) * const.SEC, showFrom='hour', showTo='second')
        leftTime = localization.formatters.FormatTimeIntervalWritten(int(countdownSecond) * const.SEC, showFrom='hour', showTo='second')
        eve.Message('AntiAddictionOnlineTimeWarning', {'accruedTime': accruedTime,
         'leftTime': leftTime})

    def OnAntiAddictionOnlineTimeBlockWarning(self, countdownSecond):
        leftTime = localization.formatters.FormatTimeIntervalWritten(int(countdownSecond) * const.SEC, showFrom='hour', showTo='second')
        eve.Message('AntiAddictionOnlineTimeBlockWarning', {'leftTime': leftTime})

    def OnStructureHacked(self, structureID, reinforceTiming):
        structureInfo = sm.GetService('structureDirectory').GetStructureInfo(structureID)
        reinforceWeekday, reinforceHour, nextReinforceWeekday, nextReinforceHour, applyAtTime = reinforceTiming
        reinforceTimers = ReinforcementBundle(reinforceHour=reinforceHour, nextReinforceHour=nextReinforceHour, nextReinforceApply=applyAtTime)
        wnd = StructureHackingResultWnd.GetIfOpen()
        if wnd:
            wnd.LoadWndWithResult(structureID, reinforceTimers, structureTypeID=structureInfo.typeID)
            wnd.Maximize()
        else:
            StructureHackingResultWnd.Open(structureID=structureID, reinforceTimers=reinforceTimers, structureTypeID=structureInfo.typeID)

    def OnPodKilled(self, destroyedPodID):
        self.podKillPodID = destroyedPodID

    def OnSafeLogoffTimerStarted(self, safeLogoffTime):
        if self.logoffTimer is not None:
            self.logoffTimer.Close()
        if AllowCharacterLogoff(sm.GetService('machoNet')):
            log.LogNotice('Starting safe logoff countdown for character %s' % cfg.eveowners.Get(session.charid).name)
            logoffTimerClass = SafeLogoffTimer2
        else:
            logoffTimerClass = SafeLogoffTimer
        self.logoffTimer = logoffTimerClass(parent=uicore.layer.abovemain, logoffTime=safeLogoffTime)
        self.logoffTimer.left = sm.GetService('window').GetCameraLeftOffset(self.logoffTimer.width, self.logoffTimer.align, self.logoffTimer.left)

    def OnSafeLogoffActivated(self):
        if self.logoffTimer is not None:
            self.logoffTimer.SetTimerCompleted()
        if self.logoffTimer.quitting:
            uicore.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/SafeLogoffDisconnect', {'charid': session.charid})})
            sm.GetService('clientStatsSvc').OnProcessExit()
            if AllowCharacterLogoff(sm.GetService('machoNet')):
                log.LogNotice('Safe logoff countdown for character %s complete. Exiting client.' % cfg.eveowners.Get(session.charid).name)
                bluepy.TerminateSilently(0, 'User exit after logoff')
        else:
            self.logoffTimer.Close()
            log.LogNotice('Safe logoff countdown for character %s complete. Returning to character selection screen.' % cfg.eveowners.Get(session.charid).name)
            sm.GetService('sessionMgr').PerformSessionChange('character logoff', sm.GetService('gameui').DoCharacterLogoff)
            self.logoffTimer = None

    def OnSafeLogoffAborted(self, reasonCode):
        self.AbortSafeLogoffTimer()
        uicore.Message('CustomNotify', {'notify': localization.GetByLabel(reasonCode)})

    def OnSafeLogoffFailed(self, failedConditions):
        self.AbortSafeLogoffTimer()
        uicore.Message('CustomNotify', {'notify': '<br>'.join([localization.GetByLabel('UI/Inflight/SafeLogoff/ConditionsFailedHeader')] + [ localization.GetByLabel(error) for error in failedConditions ])})

    def AbortSafeLogoffTimer(self):
        if self.logoffTimer is not None:
            self.logoffTimer.AbortLogoff()
            self.logoffTimer = None


def _ScheduleBackgroundDownloads():
    everesourceprefetch.PrepareFilesets()
    keys = ['staticdata',
     'ui_basics',
     'ui_classes',
     'black_files',
     'low_detail_ships',
     'low_detail_nebulas',
     'ui_cc']
    for each in keys:
        everesourceprefetch.Schedule(each)
