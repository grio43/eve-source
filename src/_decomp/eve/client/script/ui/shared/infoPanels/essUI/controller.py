#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\essUI\controller.py
import blue
from carbon.common.lib.const import SEC
from dynamicresources.common.ess.formulas import GetPayout
MAIN_BANK_IDLE = 1
MAIN_BANK_HACKING = 2
RESERVE_BANK_LOCKED = 3
RESERVE_BANK_UNLOCKED = 4

class InfoPanelESSStateController:

    def __init__(self):
        self.dynamicResourceService = sm.GetService('dynamicResourceSvc')
        self._cache_manager = sm.RemoteSvc('dynamicResourceCacheMgr')
        self._essData = None
        self.essSettings = None
        self.RefreshEssData()

    def RefreshEssData(self):
        self._essData = self.dynamicResourceService.GetESSDataForCurrentSystem()
        self.essSettings = self._cache_manager.GetDynamicResourceSettings()
        if self._essData and self.essSettings:
            return True
        else:
            return False

    def GetEssData(self):
        return self._essData

    def Get(self, field, default = None):
        return self._essData.get(field, default)

    def GetSetting(self, field, default = None):
        return self.essSettings.get(field, default)

    def GetEnumeratedMainBankState(self):
        if self._is_main_bank_in_linked_state():
            return MAIN_BANK_HACKING
        else:
            return MAIN_BANK_IDLE

    def GetEnumeratedReserveBankState(self):
        pulsesRemaining = self._essData.get('reserveBankPulsesRemaining')
        if pulsesRemaining > 0:
            return RESERVE_BANK_UNLOCKED
        else:
            return RESERVE_BANK_LOCKED

    def GetMainBankLinkState(self):
        if not self._is_main_bank_in_linked_state():
            return
        linkedCharID = self._essData.get('mainBankLink', {}).get('characterID', None)
        return {'this_client': linkedCharID == session.charid,
         'link': self._essData.get('mainBankLink', {})}

    def GetTimeLeftForMainBankHack(self):
        currentSimTime = blue.os.GetSimTime()
        linkState = self._essData.get('mainBankLink', {})
        completesAt = linkState.get('completesAt', None)
        if completesAt is None:
            return 0
        return max(0, completesAt - currentSimTime)

    def GetProportionOfTimeLeftForMainBankHack(self):
        linkState = self._essData.get('mainBankLink', {})
        completesAt = linkState.get('completesAt', None)
        if completesAt is None:
            return 0.0
        currentSimTime = blue.os.GetSimTime()
        hackTime = float(self.GetSetting('bufferTimeSeconds')) * SEC
        return (completesAt - currentSimTime) / hackTime

    def CalculateReserveBankPayouts(self):
        windowAccessFactor = self.GetSetting('reserveWindowAccessFactor')
        exponentLead = self.GetSetting('reservePayoutExponentLead')
        exponentTail = self.GetSetting('reservePayoutExponentTail')
        payoutPaddingValue = self.GetSetting('reservePayoutPaddingValue')
        reserveBankMaxPayout = self.GetSetting('reserveBankMaxPayout')
        pulsesTotal = self.Get('reserveBankPulsesTotal')
        pulseValues = [ GetPayout(pulseNumber + 1, pulsesTotal, windowAccessFactor, reserveBankMaxPayout, exponentLead, exponentTail, payoutPaddingValue) for pulseNumber in xrange(pulsesTotal) ]
        return pulseValues

    def GetCurrentReserveBankPulsePayout(self):
        windowAccessFactor = self.GetSetting('reserveWindowAccessFactor')
        exponentLead = self.GetSetting('reservePayoutExponentLead')
        exponentTail = self.GetSetting('reservePayoutExponentTail')
        payoutPaddingValue = self.GetSetting('reservePayoutPaddingValue')
        reserveBankMaxPayout = self.GetSetting('reserveBankMaxPayout')
        pulsesRemaining = self.Get('reserveBankPulsesRemaining')
        pulsesTotal = self.Get('reserveBankPulsesTotal')
        currentPulseNumber = pulsesTotal - pulsesRemaining + 1
        amountInBank = self.Get('reserveValue', 0.0)
        maxPayoutThisPulse = GetPayout(currentPulseNumber, pulsesTotal, windowAccessFactor, reserveBankMaxPayout, exponentLead, exponentTail, payoutPaddingValue)
        return min(maxPayoutThisPulse, amountInBank)

    def _is_main_bank_in_linked_state(self):
        linkedChar = self._essData.get('mainBankLink', {}).get('characterID', None)
        if linkedChar:
            return True
        else:
            return False
