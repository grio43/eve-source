#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\base.py
import sys
import blue
import evetypes
import localization
import log
import uthread
from carbon.common.script.sys import service
from carbon.common.script.sys.row import Row
from carbonui import uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.layer import LayerCore
from carbonui.window.underlay import WindowUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.environment.model import turretSet
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.shared.dockedUI import ReloadLobbyWnd
from eve.client.script.ui.shared.dockedUI.lobbyWnd import LobbyWnd
from eve.client.script.ui.shared.skillRequirementDialog import prompt_missing_skill_requirements
from eve.client.script.ui.station import stationServiceConst
from eve.client.script.ui.util import uix
from eve.common.lib.appConst import CLONE_STATION_SERVICES
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.sys.eveCfg import IsControllingStructure
from eve.common.script.sys.idCheckers import IsCapsule, IsNewbieShip
from eve.common.script.util.structuresCommon import IsStationServiceAvailable
from eveSpaceObject import spaceobjanimation
from fsdBuiltData.common.graphicIDs import GetSofFactionName
from reprocessing.ui.reprocessingWnd import ReprocessingWnd

class StationSvc(service.Service):
    __guid__ = 'svc.station'
    __update_on_reload__ = 0
    __exportedcalls__ = {'GetGuests': [],
     'IsGuest': [],
     'Setup': [],
     'GetSvc': [],
     'LoadSvc': [],
     'GiveHint': [],
     'ClearHint': [],
     'StopAllStationServices': [],
     'CleanUp': [],
     'SelectShipDlg': [],
     'GetServiceState': [],
     'GetStationItem': []}
    __dependencies__ = ['journal', 'insurance', 'crimewatchSvc']
    __notifyevents__ = ['OnCharNowInStation',
     'OnCharNoLongerInStation',
     'OnDogmaItemChange',
     'OnCharacterHandler',
     'OnDogmaAttributeChanged',
     'OnCharacterSelected',
     'OnSessionChanged',
     'OnActiveShipModelChange',
     'OnStanceActive',
     'ProcessSessionChange',
     'OnSessionReset']

    @property
    def stationItem(self):
        return self.GetStationItem()

    def OnCharacterSelected(self):
        self._stationItem = None
        self.CleanUp(clearGuestList=True)

    def OnSessionReset(self):
        self.CleanUp(clearGuestList=True)

    def OnSessionChanged(self, isRemote, session, change):
        if 'locationid' in change:
            oldLocation, newLocation = change['locationid']
            if idCheckers.IsStation(oldLocation):
                self.CleanUp(clearGuestList=True)

    def ProcessSessionChange(self, isRemote, session, change):
        if 'stationid' in change or 'structureid' in change:
            self.ClearStationItem()

    def OnCharNowInStation(self, rec):
        charID, corpID, allianceID, warFactionID = rec
        if charID not in self.guests:
            self.guests[charID] = (corpID, allianceID, warFactionID)

    def OnCharNoLongerInStation(self, rec):
        charID, corpID, allianceID, factionID = rec
        if charID in self.guests:
            self.guests.pop(charID)

    def GetGuests(self):
        currentStationID = session.stationid
        if not self.guestListReceived or self.guestListReceived != currentStationID:
            self.guests.clear()
            guests = sm.RemoteSvc('station').GetGuests()
            for charID, corpID, allianceID, warFactionID in guests:
                self.guests[charID] = (corpID, allianceID, warFactionID)

            self.guestListReceived = currentStationID
        return self.guests

    def IsGuest(self, whoID):
        if len(self.guests) == 0:
            self.GetGuests()
        return whoID in self.guests

    def Stop(self, memStream = None):
        self.LogInfo('Stopping Station Service')
        self.CleanUp(clearGuestList=True)

    def GetServiceDisplayName(self, service):
        s = self.GetStationServiceData(service)
        if s:
            return s.label
        return localization.GetByLabel('UI/Common/Unknown')

    def GetStationServiceData(self, serviceName):
        return stationServiceConst.serviceDataByNameID.get(serviceName, None)

    def IsCloneServiceAvailable(self):
        for stationServiceID in CLONE_STATION_SERVICES:
            if self.IsStationServiceAvailable(stationServiceID):
                return True

        return False

    def IsStationServiceAvailable(self, stationServiceID):
        return IsStationServiceAvailable(session.solarsystemid2, self.stationItem, stationServiceID)

    def CleanUp(self, storeCamera = 1, clearGuestList = False):
        try:
            if getattr(self, 'underlay', None):
                uicore.registry.UnregisterWindow(self.underlay)
                self.underlay.OnClick = None
                self.underlay.Minimize = None
                self.underlay.Maximize = None
        except:
            pass

        uix.Close(self, ['closeBtn',
         'hint',
         'underlay',
         'lobby'])
        self.lobby = None
        self.underlay = None
        self.closeBtn = None
        self.hint = None
        self.selected_service = None
        self.loading = None
        self.active_service = None
        self.refreshingfitting = False
        self.activeShipItem = None
        self.activeShipTypeID = None
        self.activeshipmodel = None
        self.loadingSvc = 0
        self.activatingShip = 0
        self.leavingShip = 0
        self.paperdollState = None
        self.station = None
        if clearGuestList:
            self.guests = {}
            self.guestListReceived = None

    def StopAllStationServices(self):
        for serviceData in stationServiceConst.serviceData:
            if sm.IsServiceRunning(serviceData.name):
                sm.services[serviceData.name].Stop()

    def Setup(self, reloading = 0):
        self.CleanUp(0)
        self.loading = 1
        if not reloading:
            eve.Message('OnEnterStation')
        if self.station is None and eve.session.stationid:
            self.station = sm.GetService('ui').GetStation(eve.session.stationid)
        sm.GetService('autoPilot').SetOff('toggled by Station Entry')
        if sm.GetService('viewState').IsViewActive('starmap', 'systemmap'):
            sm.StartService('map').MinimizeWindows()
        if sm.GetService('viewState').IsViewActive('planet'):
            sm.GetService('planetUI').MinimizeWindows()
        self.loading = 0
        self.sprite = None

    def GetPaperdollStateCache(self):
        if self.paperdollState is None:
            self.paperdollState = sm.RemoteSvc('charMgr').GetPaperdollState()
        return self.paperdollState

    def OnCharacterHandler(self):
        self.ClearPaperdollStateCache()

    def ClearPaperdollStateCache(self):
        self.paperdollState = None

    def BlinkButton(self, what):
        lobby = LobbyWnd.GetIfOpen()
        if lobby:
            lobby.BlinkButton(what)

    def TryActivateShip(self, invitem, onSessionChanged = 0, secondTry = 0):
        shipid = invitem.itemID
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if shipid == dogmaLocation.GetCurrentShipID():
            return
        if self.activatingShip or IsControllingStructure():
            return
        if len(dogmaLocation.GetMissingSkills(invitem.typeID)) > 0:
            prompt_missing_skill_requirements(invitem.typeID)
            return
        sm.GetService('invCache').TryLockItem(shipid, 'lockItemActivating', {'itemType': invitem.typeID}, 1)
        self.activatingShip = 1
        try:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            dogmaLocation.MakeShipActive(shipid)
            self.activeShipItem = invitem
            sm.GetService('fleet').UpdateFleetInfo()
        finally:
            self.activatingShip = 0
            sm.GetService('invCache').UnlockItem(shipid)

    def TryLeaveShip(self, invitem, onSessionChanged = 0, secondTry = 0):
        shipid = invitem.itemID
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if shipid != dogmaLocation.GetCurrentShipID():
            return
        if self.leavingShip:
            return
        sm.GetService('invCache').TryLockItem(shipid, 'lockItemLeavingShip', {'itemType': invitem.typeID}, 1)
        self.leavingShip = 1
        try:
            shipsvc = sm.GetService('gameui').GetShipAccess()
            shipsvc.LeaveShip(shipid)
        finally:
            self.leavingShip = 0
            sm.GetService('invCache').UnlockItem(shipid)

    def OnDogmaItemChange(self, item, change):
        if session.stationid is None:
            return
        if item.groupID in const.turretModuleGroups:
            self.FitHardpoints()

    def OnActiveShipModelChange(self, model, shipItem):
        self.activeshipmodel = model
        self.activeShipTypeID = shipItem.typeID
        self.FitHardpoints()

    def OnStanceActive(self, shipID, stanceID):
        if eveCfg.GetActiveShip() == shipID:
            if self.activeshipmodel is not None:
                spaceobjanimation.SetShipAnimationStance(self.activeshipmodel, stanceID)

    def FitHardpoints(self):
        if not self.activeshipmodel or self.activeShipTypeID is None or self.refreshingfitting:
            return
        self.refreshingfitting = True
        activeShip = eveCfg.GetActiveShip()
        sofFactionName = GetSofFactionName(evetypes.GetGraphicID(self.activeShipTypeID))
        turretSet.TurretSet.FitTurrets(activeShip, self.activeshipmodel, sofFactionName)
        self.refreshingfitting = False

    def GetUnderlay(self):
        if self.underlay is None:
            for each in uicore.layer.main.children[:]:
                if each is not None and not each.destroyed and each.name == 'services':
                    uicore.registry.UnregisterWindow(each)
                    each.OnClick = None
                    each.Minimize = None
                    each.Maximize = None
                    each.Close()

            self.underlay = Sprite(name='services', parent=uicore.layer.main, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
            self.underlay.scope = uiconst.SCOPE_STATION
            self.underlay.minimized = 0
            self.underlay.Minimize = self.MinimizeUnderlay
            self.underlay.Maximize = self.MaximizeUnderlay
            main = Container(name='mainparentXX', parent=self.underlay, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            main.OnClick = self.ClickParent
            main.state = uiconst.UI_NORMAL
            sub = Container(name='subparent', parent=main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            captionparent = Container(name='captionparent', parent=main, align=uiconst.TOPLEFT, left=128, top=36, idx=0)
            caption = eveLabel.CaptionLabel(text='', parent=captionparent)
            self.closeBtn = ButtonGroup(btns=[[localization.GetByLabel('UI/Commands/CmdClose'),
              self.CloseSvc,
              None,
              81]], parent=sub)
            self.sr.underlay = WindowUnderlay(parent=main)
            self.sr.underlay.padding = (-1, -10, -1, 0)
            svcparent = Container(name='serviceparent', parent=sub, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            self.underlay.sr.main = main
            self.underlay.sr.svcparent = svcparent
            self.underlay.sr.caption = caption
            uicore.registry.RegisterWindow(self.underlay)
        return self.underlay

    def MinimizeUnderlay(self, *args):
        self.underlay.state = uiconst.UI_HIDDEN

    def MaximizeUnderlay(self, *args):
        self.underlay.state = uiconst.UI_PICKCHILDREN
        self.ClickParent()

    def ClickParent(self, *args):
        for each in uicore.layer.main.children:
            if getattr(each, 'isDockWnd', 0) == 1 and each.state == uiconst.UI_NORMAL:
                each.SetOrder(-1)

    def LoadSvc(self, service, close = 1):
        serviceInfo = self.GetStationServiceData(service)
        if service is not None and serviceInfo is not None:
            self.ExecuteCommand(serviceInfo.command)
            return
        if getattr(self, 'loadingSvc', 0):
            return
        self.loadingSvc = 1
        while self.loading:
            blue.pyos.synchro.SleepWallclock(500)

        if self.selected_service is None:
            if service:
                self._LoadSvc(1, service)
        elif service == self.selected_service:
            if close:
                self._LoadSvc(0)
        else:
            self._LoadSvc(0, service)
        self.loadingSvc = 0

    def ExecuteCommand(self, cmdstr):
        func = getattr(uicore.cmd, cmdstr, None)
        if func:
            func()

    def GetSvc(self, svcname = None):
        if self.active_service is not None:
            if svcname is not None:
                if self.selected_service == svcname:
                    return self.active_service
            else:
                return self.active_service

    def ReloadLobby(self):
        ReloadLobbyWnd()

    def _LoadSvc(self, inout, service = None):
        self.loading = 1
        wnd = self.GetUnderlay()
        newsvc = None
        if inout == 1 and wnd is not None:
            self.ClearHint()
            newsvc, svctype = self.SetupService(wnd, service)
        if wnd.absoluteRight - wnd.absoluteLeft < 700 and inout == 1:
            sm.GetService('neocom').Minimize()
        height = uicore.desktop.height - 180
        wnd.state = uiconst.UI_PICKCHILDREN
        if inout == 1:
            sm.GetService('neocom').SetLocationInfoState(0)
        topStart = -height if inout else height
        topEnd = 0 if inout else -height
        animations.MorphScalar(wnd, 'top', startVal=topStart, endVal=topEnd, duration=0.5)
        snd = service
        if inout == 0:
            snd = self.selected_service
        if snd is not None:
            eve.Message('LoadSvc_%s%s' % (snd, ['Out', 'In'][inout]))
        blue.pyos.synchro.SleepWallclock([750, 1250][inout])
        if inout == 0:
            sm.GetService('neocom').SetLocationInfoState(1)
        if newsvc is not None:
            if svctype == 'form':
                newsvc.Startup(self)
            elif settings.user.ui.Get('nottry', 0):
                newsvc.Initialize(wnd.sr.svcparent)
            else:
                try:
                    newsvc.Initialize(wnd.sr.svcparent)
                except:
                    log.LogException(channel=self.__guid__)
                    sys.exc_clear()

            self.active_service = newsvc
            self.selected_service = service
        else:
            wnd.sr.svcparent.Flush()
            if self.active_service and hasattr(self.active_service, 'Reset'):
                self.active_service.Reset()
            self.active_service = None
            self.selected_service = service
        self.loading = 0
        if inout == 0 and service is not None:
            self._LoadSvc(1, service)
        if inout == 0 and service is None:
            wnd.sr.svcparent.Flush()

    def Startup(self, svc):
        uthread.new(svc.Startup, self)

    def GiveHint(self, hintstr, left = 80, top = 320, width = 300):
        self.ClearHint()
        if self.hint is None:
            par = Container(name='captionParent', parent=self.GetUnderlay().sr.main, align=uiconst.TOPLEFT, top=top, left=left, width=width, height=256, idx=0)
            self.hint = eveLabel.CaptionLabel(text='', parent=par, align=uiconst.TOALL, left=0, top=0)
        self.hint.parent.top = top
        self.hint.parent.left = left
        self.hint.parent.width = width
        self.hint.text = hintstr or ''

    def ClearHint(self):
        if self.hint is not None:
            self.hint.text = ''

    def SetupService(self, wnd, servicename):
        wnd.sr.svcparent.Flush()
        svc = None
        topheight = 128
        btmheight = 0
        icon = 'ui_9_64_14'
        sz = 128
        top = -16
        icon = eveIcon.Icon(icon=icon, parent=wnd.sr.svcparent, left=0, top=top, size=sz, idx=0)
        iconpar = Container(name='iconpar', parent=wnd.sr.svcparent, align=uiconst.TOTOP, height=96, clipChildren=1, state=uiconst.UI_PICKCHILDREN)
        bigicon = icon.CopyTo()
        bigicon.width = bigicon.height = sz * 2
        bigicon.top = -64
        bigicon.opacity = 0.1
        iconpar.children.append(bigicon)
        closeX = eveIcon.Icon(icon='ui_38_16_220')
        closeX.align = uiconst.TOPRIGHT
        closeX.left = closeX.top = 2
        closeX.OnClick = self.CloseSvc
        iconpar.children.append(closeX)
        Line(parent=iconpar, align=uiconst.TOPRIGHT, height=1, left=2, top=16, width=18)
        icon.state = uiconst.UI_DISABLED
        wnd.sr.caption.text = self.GetServiceDisplayName(servicename)
        wnd.sr.caption.state = uiconst.UI_DISABLED
        return (svc, 'service')

    def CloseSvc(self, *args):
        uthread.new(self.LoadSvc, None)

    def UndockAttempt(self, shipID):
        return self._DoUndockAttempt(False, True, shipID)

    def _DoUndockAttempt(self, ignoreContraband, observedSuppressed, shipID):
        try:
            shipsvc = sm.GetService('gameui').GetShipAccess()
            undockingLogLabel = localization.GetByLabel('UI/Station/UndockingFromStationToSystem', fromStation=eve.session.stationid, toSystem=eve.session.solarsystemid2)
            sm.GetService('logger').AddText(undockingLogLabel)
            if observedSuppressed:
                ignoreContraband = settings.user.suppress.Get('suppress.ShipContrabandWarningUndock', None) == uiconst.ID_OK
            onlineModules = sm.GetService('clientDogmaIM').GetDogmaLocation().GetOnlineModules(shipID)
            try:
                sm.GetService('space').PrioritizeLoadingForIDs([session.stationid])
                sm.GetService('sessionMgr').PerformSessionChange('undock', shipsvc.Undock, shipID, ignoreContraband, onlineModules=onlineModules)
            except UserError as e:
                if e.msg == 'ShipNotInHangar':
                    capsuleID = e.dict.get('capsuleID', None)
                    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                    if capsuleID is not None:
                        dogmaLocation.MakeShipActive(capsuleID)
                    raise
                elif e.msg == 'ShipContrabandWarningUndock':
                    if eve.Message(e.msg, e.dict, uiconst.OKCANCEL, suppress=uiconst.ID_OK) == uiconst.ID_OK:
                        sys.exc_clear()
                        return self._DoUndockAttempt(True, False, shipID)
                    else:
                        return False
                else:
                    raise

            self.CloseStationWindows()
        except Exception as e:
            sm.GetService('undocking').AbortUndock()
            raise

        return True

    def CloseStationWindows(self):
        ReprocessingWnd.CloseIfOpen()

    def SelectShipDlg(self):
        hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
        items = hangarInv.List(const.flagHangar)
        tmplst = []
        activeShipID = eveCfg.GetActiveShip()
        for item in items:
            if item[const.ixCategoryID] == const.categoryShip and item[const.ixSingleton]:
                tmplst.append((evetypes.GetName(item[const.ixTypeID]), item, item[const.ixTypeID]))

        if not tmplst:
            eve.Message('NeedShipToUndock')
            return
        ret = uix.ListWnd(tmplst, 'item', localization.GetByLabel('UI/Station/SelectShip'), None, 1)
        if ret is None or ret[1].itemID == activeShipID:
            return
        newActiveShip = ret[1]
        try:
            self.TryActivateShip(newActiveShip)
        except:
            raise

    def OnDogmaAttributeChanged(self, shipID, itemID, attributeID, value):
        if self.activeshipmodel and attributeID == const.attributeIsOnline and shipID == eveCfg.GetActiveShip():
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            slot = None
            if not dogmaLocation.IsItemLoaded(shipID):
                dogmaLocation.LoadItem(shipID)
            if dogmaLocation.IsItemLoading(shipID):
                dogmaLocation.loadingItems[shipID].receive()
            for module in dogmaLocation.GetDogmaItem(shipID).GetFittedItems().itervalues():
                if module.itemID != itemID:
                    continue
                slot = module.flagID - const.flagHiSlot0 + 1
                sceneShip = self.activeshipmodel
                for turretSet in sceneShip.turretSets:
                    if turretSet.slotNumber == slot:
                        if module.IsOnline():
                            turretSet.EnterStateIdle()
                        else:
                            turretSet.EnterStateDeactive()

    def GetStationItem(self):
        if session.stationid and self.HasInvalidStationItem():
            self.SetStationItemBits(sm.RemoteSvc('stationSvc').GetStationItemBits())
        return self._stationItem

    def ClearStationItem(self):
        self._stationItem = None

    def SetStationItemBits(self, bits):
        self._stationItem = Row(['ownerID',
         'itemID',
         'operationID',
         'stationTypeID'], bits)

    def HasInvalidStationItem(self):
        return self._stationItem is None or self._stationItem.itemID != session.stationid

    def OnStationInformationUpdated(self, stationID):
        sm.GetService('objectCaching').InvalidateCachedMethodCall('stationSvc', 'GetStation', stationID)

    def IsInNewbieShip(self):
        shipItem = sm.GetService('clientDogmaIM').GetDogmaLocation().GetShipItem()
        return shipItem and IsNewbieShip(shipItem.groupID)

    def CreateNewbieShip(self):
        locationID = session.stationid or session.structureid
        if not locationID:
            raise stationServiceConst.NewbieShipError('MustBeDocked')
        shipItem = sm.GetService('clientDogmaIM').GetDogmaLocation().GetShipItem()
        if not shipItem:
            raise stationServiceConst.NewbieShipError('ErrorCreatingNewbieShip')
        shipID = shipItem.itemID
        shipGroupID = shipItem.groupID
        if IsNewbieShip(shipGroupID):
            raise stationServiceConst.NewbieShipError('AlreadyInNewbieShip')
        if not IsCapsule(shipGroupID):
            areYouSureMessage = localization.GetByLabel('UI/Station/ConfirmMoveToNewbieShip')
            if eve.Message('AskAreYouSure', {'cons': areYouSureMessage}, uiconst.YESNO) != uiconst.ID_YES:
                return
        try:
            sm.RemoteSvc('dogmaIM').CreateNewbieShip(shipID, locationID)
        except UserError:
            raise
        except Exception:
            raise stationServiceConst.NewbieShipError('ErrorCreatingNewbieShip')


class StationLayer(LayerCore):
    __guid__ = 'form.StationLayer'

    def OnCloseView(self):
        sm.GetService('station').CleanUp()

    def OnOpenView(self, **kwargs):
        pass
