#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dynamicResource\dynamicResourceSvc.py
import datetimeutils
import dynamicresources.client
import locks
import threadutils
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.uicore import uicore
from dynamicresources.client import text
from dynamicresources.common.ess.data import get_key_by_type
from threadutils import expiring_memoize
from dynamicresources.common.ess.const import LINK_ERROR_ALREADY_LINKED, LINK_VALID, LINK_ERROR_SYSTEM_OFFLINE, LINK_ERROR_NOT_ON_GRID, LINK_ERROR_OUT_OF_RANGE, LINK_ERROR_INVALID_SHIP_TYPE, LINK_ERROR_LINK_OCCUPIED, ESS_LINKABLE_TYPES_LIST, ESS_MAX_LINK_DISTANCE_METERS, LINK_ERROR_NO_BALLPARK
from globalConfig import GetDynamicBountySystemEmergencyOffline, DYNAMIC_BOUNTY_SYSTEM_EMERGENCY_OFFLINE_CONFIG as DBS_OFFLINE_KEY, GetESSFeatureFlaggedOffline, ESS_FEATURE_FLAG_DISABLED_CONFIG as ESS_OFFLINE_KEY, GetESSReserveBankFeatureFlaggedOffline, ESS_RESERVE_BANK_DISABLED_CONFIG as RESERVE_OFFLINE_KEY
from evetypes import GetTypeIDsByListID
MAIN_BANK = 0
RESERVE_BANK = 1

class DynamicResourceSvc(Service):
    __guid__ = 'svc.dynamicResourceSvc'
    __servicename__ = 'DynamicResourceSvc'
    __startupdependencies__ = ['machoNet']
    __notifyevents__ = ['OnSystemDynamicBountyStateChanged',
     'OnSystemESSDataChanged',
     'OnSessionChanged',
     'OnGlobalConfigUpdated',
     'OnMainBankPlayerHackSuccess',
     'OnESSMainBankLinkNotification',
     'OnESSReserveBankLinkNotification',
     'OnMainBankPlayerLinkDisconnected',
     'OnReserveBankPlayerLinkDisconnected']

    def __init__(self):
        super(DynamicResourceSvc, self).__init__()
        self._ess_state_provider = None
        self._ess_settings = None
        self._is_ess_state_update_in_progress = False
        self._pending_ess_state_update = False

    def Run(self, memStream = None):
        super(DynamicResourceSvc, self).Run(memStream)
        self._ess_state_provider = dynamicresources.EssStateProvider(state=self._GetInitialEssState(), on_fetch_request=self._ForceUpdateEssStateProvider)
        self._ess_state_provider.mark_need_fetch()
        self._ess_settings = dynamicresources.EssSettings(service_manager=ServiceManager.Instance())

    @property
    def ess_state_provider(self):
        return self._ess_state_provider

    @property
    def ess_settings(self):
        return self._ess_settings

    @expiring_memoize(5400)
    def GetDynamicBountySettingForCurrentSystem(self):
        if GetDynamicBountySystemEmergencyOffline(self.machoNet):
            return (1.0, False)
        dynamicBountyMgr = sm.RemoteSvc('dynamicBountyMgr')
        output, dbsIsActive = dynamicBountyMgr.GetOutputForClientSolarSystem()
        return (output, dbsIsActive)

    @locks.SingletonCall
    @expiring_memoize(900)
    def GetESSDataForCurrentSystem(self):
        if GetESSFeatureFlaggedOffline(self.machoNet):
            return None
        return sm.RemoteSvc('essMgr').GetDataForClientSolarSystem()

    def IsPlayerLinkedToReserveBank(self):
        essSvc = sm.RemoteSvc('essMgr')
        return essSvc.IsClientLinkedToReserveBank()

    def CheckLinkEligibility(self, bank):
        if GetESSFeatureFlaggedOffline(self.machoNet):
            return LINK_ERROR_SYSTEM_OFFLINE
        state = self.ess_state_provider.state
        if state.offline:
            return LINK_ERROR_SYSTEM_OFFLINE
        if bank == MAIN_BANK:
            if state.reserve_bank.linked:
                return LINK_ERROR_ALREADY_LINKED
            if state.main_bank.link is not None:
                if state.main_bank.is_hacking(session.charid):
                    return LINK_ERROR_ALREADY_LINKED
                else:
                    return LINK_ERROR_LINK_OCCUPIED
        if bank == RESERVE_BANK:
            if state.main_bank.link is not None and state.main_bank.link.character_id == session.charid:
                return LINK_ERROR_ALREADY_LINKED
            if state.reserve_bank.linked:
                return LINK_ERROR_ALREADY_LINKED
        shipID = session.shipid
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return LINK_ERROR_NO_BALLPARK
        try:
            typeID = ballpark.slimItems[shipID].typeID
        except KeyError:
            typeID = None

        if typeID is None or typeID not in GetTypeIDsByListID(ESS_LINKABLE_TYPES_LIST):
            return LINK_ERROR_INVALID_SHIP_TYPE
        if ballpark.GetBall(state.ess_item_id) is None:
            return LINK_ERROR_NOT_ON_GRID
        dist = ballpark.DistanceBetween(shipID, state.ess_item_id)
        if dist > ESS_MAX_LINK_DISTANCE_METERS:
            return LINK_ERROR_OUT_OF_RANGE
        return LINK_VALID

    def RequestESSMainBankLink(self):
        eligibility = self.CheckLinkEligibility(MAIN_BANK)
        if eligibility != LINK_VALID:
            return eligibility
        essSvc = sm.RemoteSvc('essMgr')
        essSvc.AttemptLinkToMainBank()

    def RequestESSReserveBankLink(self):
        if GetESSReserveBankFeatureFlaggedOffline(self.machoNet) == True:
            return LINK_ERROR_SYSTEM_OFFLINE
        eligibility = self.CheckLinkEligibility(RESERVE_BANK)
        if eligibility != LINK_VALID:
            return eligibility
        essSvc = sm.RemoteSvc('essMgr')
        essSvc.AttemptLinkToReserveBank()

    def RequestESSMainBankUnlink(self):
        sm.RemoteSvc('essMgr').RequestMainBankUnlink()

    def RequestESSReserveBankUnlink(self):
        sm.RemoteSvc('essMgr').RequestReserveBankUnlink()

    def RequestUnlockReserveBank(self, typeID):
        essMgr = sm.RemoteSvc('essMgr')
        essMgr.RequestUnlockReserveBank(typeID)

    @expiring_memoize(300)
    def GetESSAccessHistoryForCurrentSystem(self):
        mainData = sm.RemoteSvc('essMgr').GetMainBankTheftsForClientSolarSystem()
        reserveData = sm.RemoteSvc('essMgr').GetReserveBankTheftsForClientSolarSystem()
        return {'main': mainData,
         'reserve': reserveData}

    def GetESSReserveBankKeysForCurrentSystem(self):
        dynamicResourceCacheMgr = sm.RemoteSvc('dynamicResourceCacheMgr')
        key_type_ids = dynamicResourceCacheMgr.GetESSReserveBankKeys(session.solarsystemid2)
        return [ get_key_by_type(type_id) for type_id in key_type_ids ]

    def OnSystemDynamicBountyStateChanged(self, systemID, rate):
        if systemID == session.solarsystemid2:
            self.GetDynamicBountySettingForCurrentSystem.prime_cache_result((self,), (rate, True))
            sm.ScatterEvent('OnDynamicBountyUpdate_Local')

    def OnSystemESSDataChanged(self, systemID, data):
        if systemID == session.solarsystemid2:
            self.GetESSDataForCurrentSystem.prime_cache_result((self,), data)
            self.GetESSAccessHistoryForCurrentSystem.clear_cache()
            self._NotifyEssDataChanged()

    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid2' in change:
            self.GetDynamicBountySettingForCurrentSystem.clear_cache()
            sm.ScatterEvent('OnDynamicBountyUpdate_Local')
            self.GetESSDataForCurrentSystem.clear_cache()
            self.GetESSAccessHistoryForCurrentSystem.clear_cache()
            self._NotifyEssDataChanged()

    def OnGlobalConfigUpdated(self, key, val):
        if key == DBS_OFFLINE_KEY:
            self.GetDynamicBountySettingForCurrentSystem.clear_cache()
            sm.ScatterEvent('OnDynamicBountyUpdate_Local')
        if key == ESS_OFFLINE_KEY or key == RESERVE_OFFLINE_KEY:
            self.GetESSDataForCurrentSystem.clear_cache()
            self._NotifyEssDataChanged()

    def OnESSMainBankLinkNotification(self, solar_system_id):
        if is_current_system(solar_system_id):
            self.GetESSDataForCurrentSystem.clear_cache()
            self._NotifyEssDataChanged()

    def OnESSReserveBankLinkNotification(self, solar_system_id):
        if is_current_system(solar_system_id):
            self._ess_state_provider.evolve(reserve_bank=self._ess_state_provider.state.reserve_bank.evolve(linked=True))

    def OnMainBankPlayerHackSuccess(self, hack_data):
        if is_current_system(hack_data['solarSystemID']):
            self._ess_state_provider.evolve(main_bank=self._ess_state_provider.state.main_bank.evolve(link_result=dynamicresources.MainBankLinkResult(link_id=hack_data['linkID'], character_id=int(hack_data['characterID']), successful=True)))

    def OnMainBankPlayerLinkDisconnected(self, data):
        if is_current_system(data['solarSystemID']):
            self._ess_state_provider.evolve(main_bank=self._ess_state_provider.state.main_bank.evolve(link_result=dynamicresources.MainBankLinkResult(link_id=data['linkID'], character_id=data['characterID'], successful=False)))
            if data['characterID'] == session.charid:
                message = text.unlink_reason_description(data['reason'])
                if message:
                    uicore.Message('CustomNotify', {'notify': message})

    def OnReserveBankPlayerLinkDisconnected(self, data):
        if is_current_system(data['solarSystemID']):
            self._ess_state_provider.evolve(reserve_bank=self._ess_state_provider.state.reserve_bank.evolve(linked=False))
            if data['characterID'] == session.charid:
                message = text.unlink_reason_description(int(data['reason']))
                if message:
                    uicore.Message('CustomNotify', {'notify': message})

    def _NotifyEssDataChanged(self):
        self._UpdateEssStateProvider()
        sm.ScatterEvent('OnESSDataUpdate_Local')

    @threadutils.threaded
    def _ForceUpdateEssStateProvider(self):
        self._UpdateEssStateProvider(force=True)

    def _UpdateEssStateProvider(self, force = False):
        if self._is_ess_state_update_in_progress:
            self._pending_ess_state_update = True
            return
        self._is_ess_state_update_in_progress = True
        try:
            self._pending_ess_state_update = True
            while self._pending_ess_state_update:
                self._pending_ess_state_update = False
                if is_current_system(None):
                    self._ess_state_provider.evolve(status=dynamicresources.EssStatus.offline, ess_item_id=None)
                    continue
                if not self._ess_state_provider.has_subscribers and not force:
                    self._ess_state_provider.mark_need_fetch()
                    continue
                ess_data = self.GetESSDataForCurrentSystem()
                if ess_data is None or ess_data['essID'] is None:
                    self._ess_state_provider.evolve(status=dynamicresources.EssStatus.offline, ess_item_id=None)
                    continue
                current_state = self._ess_state_provider.state
                main_bank_link = None
                if ess_data['mainBankLink']:
                    main_bank_link = dynamicresources.MainBankLink(link_id=ess_data['mainBankLink']['linkID'], character_id=ess_data['mainBankLink']['characterID'], start=datetimeutils.filetime_to_datetime(ess_data['mainBankLink']['startedAt']), end=datetimeutils.filetime_to_datetime(ess_data['mainBankLink']['completesAt']))
                last_pulse_start = ess_data['reserveBankLastPulseInitiated']
                if last_pulse_start is not None:
                    last_pulse_start = datetimeutils.filetime_to_datetime(last_pulse_start)
                pulses_remaining = ess_data['reserveBankPulsesRemaining']
                link_count = ess_data['reserveBankActiveLinks']
                linked = False
                if pulses_remaining > 0 and link_count > 0:
                    linked = self.IsPlayerLinkedToReserveBank()
                self._ess_state_provider.evolve(status=dynamicresources.EssStatus.online, ess_item_id=ess_data['essID'], main_bank=current_state.main_bank.evolve(balance=ess_data['mainValue'], link=main_bank_link), reserve_bank=dynamicresources.ReserveBankState(balance=ess_data['reserveValue'], pulses_total=ess_data['reserveBankPulsesTotal'], pulses_remaining=pulses_remaining, last_pulse_start=last_pulse_start, link_count=link_count, linked=linked))

        finally:
            self._is_ess_state_update_in_progress = False

    def _GetInitialEssState(self):
        return dynamicresources.EssState(status=dynamicresources.EssStatus.loading, ess_item_id=None, in_range=False, main_bank=dynamicresources.MainBankState(balance=0, link=None, link_result=None), reserve_bank=dynamicresources.ReserveBankState(balance=0, pulses_total=0, pulses_remaining=0, last_pulse_start=None, link_count=0, linked=False))


def is_current_system(solar_system_id):
    return getattr(session, 'solarsystemid2', None) == solar_system_id
