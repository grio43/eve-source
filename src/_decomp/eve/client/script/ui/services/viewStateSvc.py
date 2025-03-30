#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\viewStateSvc.py
import math
import blue
import carbonui.const as uiconst
import eveexceptions
import gametime
import localization
import log
import uthread
from billboards import load_billboard_playlist_for_view, unload_billboard_playlist_for_view
from carbon.common.script.sys.service import Service
from carbonui.control.layer import LayerCore
from carbonui.uicore import uicore
from eve.client.script.ui.services.message_bus.viewMessenger import ViewMessenger
from eve.client.script.ui.view import overlaySettings
from eve.client.script.ui.view.viewStateConst import ViewOverlay, is_entering_character_selection, is_entering_game
from eve.common.script.sys.idCheckers import IsTriglavianSystem
from eveprefs import boot
from fsdBuiltData.client.billboards import AreVideosSupportedForView
from globalConfig import BillboardTakeoverEnabled

class ViewStateError(Exception):
    __guid__ = 'viewstate.ViewStateError'


class View(object):
    __guid__ = 'viewstate.View'
    __notifyevents__ = []
    __dependencies__ = []
    __layerClass__ = LayerCore
    __progressMessageLabel__ = None
    __subLayers__ = None
    __overlays__ = set()
    __suppressedOverlays__ = set()
    __exclusiveOverlay__ = set()

    def __init__(self):
        self.name = None
        self.layer = None
        self.scene = None
        self._dynamicViewType = None

    def GetDynamicViewType(self):
        if self._dynamicViewType is None:
            raise RuntimeError('View %s was activated without being set to Primary or Secondary' % self.name)
        return self._dynamicViewType

    def SetDynamicViewType(self, viewType):
        self._dynamicViewType = viewType

    def LoadView(self, **kwargs):
        self.LogInfo('LoadView called on view', self.name, 'kwargs', kwargs)

    def UnloadView(self):
        self.LogInfo('UnloadView called on view', self.name)

    def ShowView(self, **kwargs):
        self.LogInfo('ShowView called on view', self.name, 'with', kwargs)

    def HideView(self):
        self.LogInfo('HideView called on view', self.name)

    def ZoomBy(self, amount):
        if self.layer:
            self.layer.ZoomBy(amount)

    def IsActive(self):
        return sm.GetService('viewState').IsViewActive(self.name)

    def GetProgressText(self, **kwargs):
        if self.__progressMessageLabel__:
            return localization.GetByLabel(self.__progressMessageLabel__)

    def CanEnter(self, **kwargs):
        return True

    def CanExit(self):
        return True

    def CheckShouldReopen(self, newKwargs, cachedKwargs):
        return newKwargs == cachedKwargs

    def LoadCamera(self, cameraID = None, reopen = False):
        pass

    def __repr__(self):
        return '%s(name=%s)' % (self.__class__.__name__, self.name)

    def LogInfo(self, *args, **kwargs):
        sm.GetService('viewState').LogInfo(self, *args, **kwargs)

    def LogWarn(self, *args, **kwargs):
        sm.GetService('viewState').LogWarn(self, *args, **kwargs)

    def LogError(self, *args, **kwargs):
        sm.GetService('viewState').LogError(self, *args, **kwargs)


class Transition(object):
    __guid__ = 'viewstate.Transition'

    def __init__(self, allowReopen = True, fallbackView = None):
        self.allowReopen = allowReopen
        self.fallbackView = fallbackView
        self.transitionReason = None
        self.animatedOut = set()

    def StartTransition(self, fromView, toView):
        sm.GetService('viewState').LogInfo('Transition starting for', fromView, 'to', toView, '(' + self.__class__.__name__ + ')')

    def EndTransition(self, fromView, toView):
        sm.GetService('viewState').LogInfo('Transition ending for', fromView, 'to', toView)
        self.transitionReason = None

    def IsActive(self):
        return self.active

    def SetTransitionReason(self, reason, allowOverwrite = False):
        if reason is None or self.transitionReason is not None and not allowOverwrite:
            return
        self.transitionReason = reason

    def AnimateUIIn(self, duration = 2):
        uthread.new(self._AnimateUIIn, duration)

    def _AnimateUIIn(self, duration = 2):
        curveSet = None
        for layer, doSleep in ((uicore.layer.main, False), (uicore.layer.viewstate, True)):
            if layer in self.animatedOut:
                layer.display = True
                self.animatedOut.remove(layer)
            uicore.animations.FadeIn(layer, curveSet=curveSet, duration=duration, sleep=doSleep)

        self.animatedOut = set()

    def AnimateUIOut(self, duration = 0.5):
        uthread.new(self._AnimateUIOut, duration)

    def _AnimateUIOut(self, duration = 0.5):
        curveSet = None
        myCallback = lambda : self.FadeOutEndCallback(uicore.layer.main)
        uicore.animations.FadeOut(uicore.layer.main, duration=duration, curveSet=curveSet, callback=myCallback)
        myCallback = lambda : self.FadeOutEndCallback(uicore.layer.viewstate)
        uicore.animations.FadeOut(uicore.layer.viewstate, duration=duration, sleep=True, curveSet=curveSet, callback=myCallback)

    def FadeOutEndCallback(self, layer, *args):
        if layer.display:
            self.animatedOut.add(layer)
            layer.display = False

    def GetCameraID(self):
        return None


class ViewType:
    __guid__ = 'viewstate.ViewType'
    Primary = 0
    Secondary = 1
    Dynamic = 2


class ViewInfo(object):
    __guid__ = 'viewstate.ViewInfo'

    def __init__(self, name, view, viewType = ViewType.Primary):
        self.name = name
        self.view = view
        self.viewType = viewType
        self.entryArguments = None

    def GetViewType(self):
        if self.viewType == ViewType.Dynamic:
            return self.view.GetDynamicViewType()
        else:
            return self.viewType

    def IsPrimary(self):
        return self.GetViewType() == ViewType.Primary

    def IsSecondary(self):
        return self.GetViewType() == ViewType.Secondary

    def __repr__(self):
        return 'ViewInfo(view=%s type=%d)' % (self.view, self.viewType)


class ViewStateSvc(Service):
    __guid__ = 'svc.viewState'
    __servicename__ = 'view state manager'
    __displayname__ = 'View State Manager'
    __notifyevents__ = ['OnShowUI']
    __dependencies__ = ['loading']

    def Run(self, memStream = None):
        self.viewLayerParent = None
        self.viewInfosByName = {}
        self.transitionsByNames = {}
        self.overlaysByName = {}
        self.overlayLayerParent = None
        self.primaryInfo = None
        self.secondaryInfo = None
        self.activeViewInfo = None
        self.activeTransition = None
        self.isOpeningView = None
        self.lastViewOpenTime = None
        self.initialized = False

    def Initialize(self, viewLayerParent):
        self.viewLayerParent = viewLayerParent
        self.overlayLayerParent = self.viewLayerParent.AddLayer('l_view_overlays', LayerCore)
        self.lastViewOpenTime = blue.os.GetWallclockTime()
        self.initialized = True

    def ActivateView(self, name, **kwargs):
        self.LogInfo('Activating view', name, 'with key words', kwargs)
        transitionFailed = False
        if self.isOpeningView is not None:
            self.LogInfo("Can't activate view", name, '. already busy opening view', self.isOpeningView)
            return
        self.isOpeningView = name
        error = None
        try:
            newInfo = self.GetViewInfo(name)
            oldInfo = self.secondaryInfo or self.primaryInfo
            if newInfo.viewType == ViewType.Dynamic:
                if self.primaryInfo is None:
                    newInfo.view.SetDynamicViewType(ViewType.Primary)
                else:
                    newInfo.view.SetDynamicViewType(ViewType.Secondary)
            transition = self.GetTransition(oldInfo, newInfo)
            if transition is None and oldInfo is not None and newInfo.name == oldInfo.name:
                self.LogInfo('No valid transition found for view', name, 'to view', name, '. Skipping since it is is already active')
            else:
                if oldInfo:
                    try:
                        if not oldInfo.view.CanExit():
                            oldInfo.view.LogInfo('Unable to exit view at present')
                            return False
                    except:
                        log.LogException()

                try:
                    if not newInfo.view.CanEnter(**kwargs):
                        newInfo.view.LogInfo('Unable to enter view now. Arguments:', kwargs)
                        return False
                except:
                    log.LogException()

                viewOpenTime = blue.os.GetWallclockTime()
                self.activeTransition = transition
                oldViewName = oldInfo.name if oldInfo else None
                newViewName = newInfo.name
                sm.ScatterEvent('OnBeforeViewStateChanged', oldViewName, newViewName)
                try:
                    self.activeTransition.StartTransition(oldInfo.view if oldInfo else None, newInfo.view)
                    cameraID = self.activeTransition.GetCameraID()
                except:
                    cameraID = None
                    log.LogException()

                progressText = newInfo.view.GetProgressText(**kwargs)
                if progressText:
                    sm.GetService('loading').ProgressWnd(progressText, '', 1, 2)
                reopen = False
                if newInfo.GetViewType() == ViewType.Secondary:
                    if self.secondaryInfo:
                        reopen = self.activeTransition.allowReopen and newInfo == self.secondaryInfo
                        if reopen:
                            try:
                                reopen = newInfo.view.CheckShouldReopen(kwargs, newInfo.entryArguments)
                            except:
                                log.LogException()
                                reopen = False

                        self._CloseView(self.secondaryInfo, unload=not reopen)
                    else:
                        self._CloseView(self.primaryInfo, unload=False)
                else:
                    if self.secondaryInfo:
                        self._CloseView(self.secondaryInfo)
                    if self.primaryInfo:
                        if self.activeTransition.allowReopen and newInfo == self.primaryInfo:
                            try:
                                self.primaryInfo.view.CheckShouldReopen(kwargs, newInfo.entryArguments)
                                reopen = True
                            except:
                                log.LogException()

                            self._CloseView(self.primaryInfo, unload=False)
                        else:
                            self._CloseView(self.primaryInfo)
                self.activeViewInfo = newInfo
                uthread.new(sm.GetService('audio').LoadBanksForView, newInfo.name)
                if newInfo.GetViewType() == ViewType.Primary:
                    self._PrepareBillboards(newInfo, oldInfo)
                    self._OpenPrimaryView(newInfo, reopen=reopen, cameraID=cameraID, **kwargs)
                else:
                    self._OpenView(newInfo, reopen=reopen, cameraID=cameraID, **kwargs)
                self.UpdateOverlays()
                if progressText is not None:
                    sm.GetService('loading').ProgressWnd(progressText, '', 2, 2)
                try:
                    transitionFailed = self.activeTransition.EndTransition(oldInfo, newInfo)
                except:
                    log.LogException()

                self._LogViewActivated()
                if oldInfo:
                    integer, fractions = self.GetSplitTimeFromTimestamp(self.lastViewOpenTime)
                    self._LogViewDeactivated(oldInfo.name, int(integer), int(fractions))
                self.lastViewOpenTime = viewOpenTime
                if newInfo.GetViewType() == ViewType.Primary:
                    sm.ScatterEvent('OnClientReady', newInfo.name)
                self.LogInfo('View', name, 'was activated')
                self._NotifyOfViewStateChange(oldViewName, newViewName)
        except eveexceptions.UserError as e:
            self.LogInfo('UserError raised while making a transition. UserError', e)
            if newInfo.GetViewType() == ViewType.Secondary:
                error = e
            else:
                raise RuntimeError('UserError raised while transitioning from %s to %s UserError: %s' % (oldInfo, newInfo, e))
        finally:
            self.isOpeningView = None
            if transitionFailed:
                self.ActivateView(self.activeTransition.fallbackView, **kwargs)
            self.activeTransition = None
            sm.GetService('loading').HideAllLoad()

        if error:
            self.LogInfo('Trying to re-enter primary view', self.primaryInfo.name, 'using cached entry arguments', self.primaryInfo.entryArguments)
            uthread.new(self.ActivateView, self.primaryInfo.name, **self.primaryInfo.entryArguments).context = 'viewStateSvc::AttemptToRecoverFromUserError'
            raise error
        return True

    def _NotifyOfViewStateChange(self, old_state, new_state):
        sm.ScatterEvent('OnViewStateChanged', old_state, new_state)
        if is_entering_character_selection(new_state):
            sm.ScatterEvent('OnCharacterSelectionViewEntered')
        elif is_entering_game(old_state, new_state):
            sm.ScatterEvent('OnGameViewEntered')

    def GetSplitTimeFromTimestamp(self, timestamp):
        if not timestamp:
            return
        secondsSinceTimestamp = gametime.GetSecondsSinceWallclockTime(timestamp)
        fractions, integer = math.modf(secondsSinceTimestamp)
        return (integer, fractions * 1000000000.0)

    @eveexceptions.EatsExceptions('protoClientLogs')
    def _LogViewActivated(self):
        message_bus = ViewMessenger(sm.GetService('publicGatewaySvc'))
        message_bus.view_activated(self.activeViewInfo.name)

    @eveexceptions.EatsExceptions('protoClientLogs')
    def _LogViewDeactivated(self, view_name, seconds_active, nanoseconds_active):
        message_bus = ViewMessenger(sm.GetService('publicGatewaySvc'))
        message_bus.view_deactivated(view_name, seconds_active, nanoseconds_active)

    def _PrepareBillboards(self, newInfo, oldInfo):
        if oldInfo:
            unload_billboard_playlist_for_view(oldInfo.name)
        if AreVideosSupportedForView(newInfo.name):
            locale = str(blue.os.languageID.lower())
            if boot.role == 'optic':
                locale = 'zh'
            videoOverrides = {}
            if IsTriglavianSystem(session.solarsystemid2):
                videoOverrides['triglavianOvertaken'] = True
            else:
                videoOverrides['triglavianInvasion'] = BillboardTakeoverEnabled(sm.GetService('machoNet'))
            load_billboard_playlist_for_view(newInfo.name, locale, **videoOverrides)

    def StartDependantServices(self, viewInfo):
        for serviceName in viewInfo.view.__dependencies__:
            setattr(viewInfo.view, serviceName, sm.StartServiceAndWaitForRunningState(serviceName))
            self.LogInfo('Dependant service', serviceName, 'has started')

        self.LogInfo('All dependant services started for view', viewInfo.name)

    def _OpenPrimaryView(self, viewInfo, reopen = False, cameraID = None, **kwargs):
        blue.SetCrashKeyValues('ViewState', viewInfo.name)
        blue.statistics.SetTimelineSectionName(viewInfo.name)
        self._OpenView(viewInfo, reopen=reopen, cameraID=cameraID, **kwargs)

    def _OpenView(self, viewInfo, reopen = False, cameraID = None, **kwargs):
        self.LogInfo('Re-open view' if reopen else 'Opening view', viewInfo, 'with kwargs', kwargs)
        self.StartDependantServices(viewInfo)
        showView = True
        oldView = self.primaryInfo
        if viewInfo.GetViewType() == ViewType.Primary:
            if self.activeViewInfo.GetViewType() == ViewType.Secondary:
                showView = False
            self.primaryInfo = viewInfo
            sm.ScatterEvent('OnPrimaryViewChanged', oldView, self.primaryInfo)
        else:
            self.secondaryInfo = viewInfo
        try:
            if showView:
                self.LogInfo('Opening layer', viewInfo.view.layer.name)
                viewInfo.view.layer.OpenView(**kwargs)
                viewInfo.view.layer.pickState = uiconst.TR2_SPS_ON
                viewInfo.view.layer.display = True
            else:
                self.LogInfo('Changing the primary layer while a secondary view', self.activeViewInfo.name, 'is active')
        except:
            log.LogException()

        try:
            if reopen:
                self.LogInfo('View', viewInfo.name, 'is being re-opened')
            else:
                self.LogInfo('View', viewInfo.name, 'is being loaded.')
                viewInfo.view.LoadView(**dict(lastView=oldView, **kwargs))
            if showView:
                self.LogInfo('Showing view', viewInfo.name)
                viewInfo.view.ShowView(**kwargs)
            viewInfo.view.LoadCamera(cameraID, reopen)
        except:
            log.LogException()

        sm.RegisterNotify(viewInfo.view)
        sm.ScatterEvent('OnViewLoaded', oldView, self.primaryInfo)
        viewInfo.entryArguments = kwargs
        self.LogInfo('view', viewInfo, 'opened')

    def _CloseView(self, viewInfo, unload = True):
        try:
            viewInfo.view.layer.CloseView(recreate=False)
        except:
            log.LogException()

        viewInfo.view.layer.display = False
        try:
            viewInfo.view.HideView()
            if unload:
                sm.UnregisterNotify(viewInfo.view)
                viewInfo.view.UnloadView()
                self.LogInfo('Unloading view', viewInfo.name)
        except:
            log.LogException()

        if viewInfo.GetViewType() == ViewType.Primary:
            if unload:
                viewInfo.entryArguments = None
        else:
            self.secondaryInfo = None
        sm.ScatterEvent('OnViewClosed', viewInfo.name)

    def ChangePrimaryView(self, name, **kwargs):
        self.LogInfo('ChangePrimaryView', name)
        while self.isOpeningView:
            blue.pyos.synchro.Yield()

        if self.secondaryInfo:
            if (self.secondaryInfo.name, name) not in self.transitionsByNames:
                raise ViewStateError('Changing primary view to %s from current active secondary view %s will leave the viewStateSvc in an undefined state' % (name, self.secondaryInfo.name))
            viewInfo = self.GetViewInfo(name)
            self._CloseView(self.primaryInfo)
            self._OpenView(viewInfo, **kwargs)
            self.UpdateOverlays()
        else:
            return self.ActivateView(name, **kwargs)

    def GetTransition(self, oldInfo, newInfo):
        oldViewName = oldInfo.name if oldInfo else None
        transition = self.transitionsByNames.get((oldViewName, newInfo.name))
        if transition is None:
            transition = self.transitionsByNames.get((None, newInfo.name))
        if transition is None:
            raise ViewStateError('There is not a valid transition from %s to %s' % (oldViewName, newInfo.name))
        self.LogInfo('Found transition from', oldViewName, 'to', newInfo.name)
        return transition

    def GetTransitionByName(self, fromName, toName):
        if (fromName, toName) in self.transitionsByNames:
            return self.transitionsByNames[fromName, toName]

    def GetView(self, name):
        return self.GetViewInfo(name).view

    def HasView(self, name):
        return name in self.viewInfosByName

    def GetViewInfo(self, name):
        try:
            return self.viewInfosByName[name]
        except KeyError:
            raise ViewStateError('There is no view registered by the name %s' % name)

    def GetCurrentViewInfo(self):
        return self.activeViewInfo

    def GetCurrentView(self):
        return getattr(self.activeViewInfo, 'view', None)

    def IsInitialized(self):
        return self.initialized

    def IsViewActive(self, *names):
        return getattr(self.activeViewInfo, 'name', None) in names

    def IsPrimaryViewActive(self, *names):
        return getattr(self.primaryInfo, 'name', None) in names

    def GetActiveViewName(self):
        return getattr(self.activeViewInfo, 'name', None)

    def HasActiveTransition(self):
        if self.activeTransition is not None:
            return True
        else:
            return False

    def AddView(self, name, view, viewType = ViewType.Primary):
        self.LogInfo('Adding view', name, view, viewType)
        view.name = name
        info = ViewInfo(name, view, viewType)
        view.layer = self.viewLayerParent.AddLayer('l_%s' % name, view.__layerClass__, view.__subLayers__)
        view.layer.state = uiconst.UI_HIDDEN
        self.viewInfosByName[name] = info

    def AddTransition(self, fromName, toName, transition = Transition()):
        self.LogInfo('Adding transition', fromName or '[All]', toName, transition)
        self.transitionsByNames[fromName, toName] = transition

    def AddTransitions(self, fromNames, toNames, transition = Transition()):
        for fromName in fromNames:
            for toName in toNames:
                self.AddTransition(fromName, toName, transition)

    def GetPrimaryView(self):
        try:
            return self.primaryInfo.view
        except AttributeError:
            raise ViewStateError('There is no primary view set')

    def CloseSecondaryView(self, name = None):
        while self.isOpeningView:
            blue.pyos.synchro.Yield()

        if self.secondaryInfo is None:
            self.LogInfo("Can't close secondary view since none is active")
        else:
            if name is None or self.activeViewInfo.name == name:
                self.LogInfo('closing secondary view', self.secondaryInfo.name)
                args = self.primaryInfo.entryArguments if self.primaryInfo.entryArguments is not None else dict()
                return self.ActivateView(self.primaryInfo.name, **args)
            self.LogInfo('The secondary view', name, 'was not closed as is not active')

    def ToggleSecondaryView(self, name, **kwargs):
        self.LogInfo('Toggling view', name)
        while self.isOpeningView:
            blue.pyos.synchro.Yield()

        info = self.GetViewInfo(name)
        if info.GetViewType() != ViewType.Secondary:
            raise RuntimeError('You can only toggle secondary views (tools)')
        if self.IsViewActive(name):
            return self.CloseSecondaryView(name)
        else:
            return self.ActivateView(name, **kwargs)

    def IsCurrentViewPrimary(self):
        return self.activeViewInfo.GetViewType() == ViewType.Primary

    def IsCurrentViewSecondary(self):
        activeViewInfo = getattr(self, 'activeViewInfo', None)
        if activeViewInfo:
            return activeViewInfo.GetViewType() == ViewType.Secondary
        else:
            return False

    def AddOverlay(self, name, overlayClass, subLayers = None):
        if name not in self.overlaysByName:
            overlay = self.overlayLayerParent.AddLayer('l_%s' % name, overlayClass, subLayers)
            overlay.display = False
            self.overlaysByName[name] = overlay

    def UpdateOverlays(self, forcedUpdateOnOverlays = ()):
        activeOverlays = self._GetOverlaysToEnable()
        self.LogInfo('Overlays to enable', activeOverlays)
        for name, overlay in self.overlaysByName.items():
            try:
                if name in activeOverlays or name in self.activeViewInfo.view.__exclusiveOverlay__:
                    if overlay in forcedUpdateOnOverlays:
                        overlay.CloseView(recreate=False)
                    overlay.OpenView()
                    overlay.display = True
                    sm.ScatterEvent('OnOverlayActivated', name)
                    self.LogInfo('Overlay', name, 'activated')
                else:
                    overlay.display = False
                    overlay.CloseView(recreate=False)
                    self.overlaysByName[name] = uicore.layer.Get(name)
                    sm.ScatterEvent('OnOverlayClosed', name)
                    self.LogInfo('Overlay', name, 'closed')
            except:
                log.LogException()

        if sm.GetService('ui').IsUISuppressed():
            sm.GetService('ui').SuppressUI()

    def _GetOverlaysToEnable(self):
        activeOverlays = self.primaryInfo.view.__overlays__.copy()
        if self.secondaryInfo:
            activeOverlays.update(self.secondaryInfo.view.__overlays__)
        activeOverlays.difference_update(self.primaryInfo.view.__suppressedOverlays__)
        if self.secondaryInfo:
            activeOverlays.difference_update(self.secondaryInfo.view.__suppressedOverlays__)
            activeOverlays.difference_update(overlaySettings.GetOverlaysDisabledInFullscreen())
        return activeOverlays

    def SafeLogoffInProgress(self):
        shipUI = self.overlaysByName.get(ViewOverlay.ShipUI, None)
        if shipUI is None or shipUI.destroyed:
            return False
        logoffTimer = getattr(shipUI, 'logoffTimer', None)
        if logoffTimer is None or logoffTimer.destroyed:
            return False
        return logoffTimer.IsVisible()

    def SetTransitionReason(self, fromName, toName, reason):
        self.LogInfo('Adding transition reason ', fromName or '[All]', toName, reason)
        self.transitionsByNames[fromName, toName].SetTransitionReason(reason)

    def GetActiveTransitionReason(self):
        if self.activeTransition is None:
            return
        return self.activeTransition.transitionReason

    def GetActiveTransition(self):
        return self.activeTransition

    def OnShowUI(self):
        if sm.GetService('ui').IsUiVisible():
            self.UpdateOverlays()
