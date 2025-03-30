#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\fwEnlistmentSvc.py
from localization import GetByLabel
import carbonui.const as uiconst
from carbon.common.script.sys.service import Service
FACTION_ID_NOT_SET = 'FACTION_ID_NOT_SET'
TIMESTAMP_NOT_SET = 'TIMESTAMP_NOT_SET'

class FwEnlistmentSvc(Service):
    __guid__ = 'svc.fwEnlistmentSvc'
    __displayname__ = 'FW Enlistment client service'
    __startupdependencies__ = ['machoNet']
    __notifyevents__ = ['OnCharacterSessionChanged',
     'OnSessionReset',
     'OnEnlistmentStateUpdated',
     'OnSessionChanged',
     'OnEnlistmentCooldownCleared']

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        self._ResetLocalData()

    def _ResetLocalData(self):
        self._myFactionID = FACTION_ID_NOT_SET
        self._directFactionID = FACTION_ID_NOT_SET
        self._corpFactionID = FACTION_ID_NOT_SET
        self._enlistmentCooldownTimestamp = TIMESTAMP_NOT_SET

    def OnCharacterSessionChanged(self, oldCharacterID, newCharacterID):
        self._ResetLocalData()

    def OnSessionReset(self):
        self._ResetLocalData()

    def OnSessionChanged(self, isRemote, sess, change):
        if session.charid and 'warfactionid' in change:
            self._ResetLocalData()
            sm.ScatterEvent('OnEnlistmentStateUpdated_Local')

    def OnEnlistmentStateUpdated(self, factionID, directFactionID, corpFactionID):
        self.LogInfo('OnEnlistmentStateUpdated', factionID, directFactionID, corpFactionID)
        self._myFactionID = factionID
        self._directFactionID = directFactionID
        self._corpFactionID = corpFactionID
        self._enlistmentCooldownTimestamp = TIMESTAMP_NOT_SET
        sm.ScatterEvent('OnEnlistmentStateUpdated_Local')

    def GetMyFaction(self):
        if self._myFactionID == FACTION_ID_NOT_SET:
            self._UpdateMyEnlistmentState()
        return self._myFactionID

    def IsEnlistedDirectly(self):
        if self._directFactionID == FACTION_ID_NOT_SET:
            self._UpdateMyEnlistmentState()
        return self._directFactionID is not None

    def IsEnlistedViaCorp(self):
        self.GetCorpFactionID()
        return self._corpFactionID is not None

    def GetCorpFactionID(self):
        if self._corpFactionID == FACTION_ID_NOT_SET:
            self._UpdateMyEnlistmentState()
        return self._corpFactionID

    def _UpdateMyEnlistmentState(self):
        factionID, directFactionID, corpFactionID = sm.RemoteSvc('fwCharacterEnlistmentMgr').GetMyEnlistment()
        self._myFactionID = factionID
        self._directFactionID = directFactionID
        self._corpFactionID = corpFactionID

    def RequestDirectEnlistInFaction(self, factionID):
        if self.IsEnlistedDirectly():
            raise RuntimeError('Cannot request direct enlistment - character is already directly enlisted')
        if self.IsEnlistedViaCorp():
            if self.GetMyFaction() != self.GetCorpFactionID():
                text = GetByLabel('UI/FactionWarfare/Enlistment/CorpHasJoinPending')
                raise UserError('CustomNotify', {'notify': text})
            raise RuntimeError('Cannot request direct enlistment - character is already enlisted via corp')
        sm.RemoteSvc('fwCharacterEnlistmentMgr').CreateMyDirectEnlistment(factionID)

    def RemoveMyDirectEnlistment(self):
        if not self.IsEnlistedDirectly():
            raise RuntimeError('Cannot remove enlistment - character is not directly enlisted')
        sm.RemoteSvc('fwCharacterEnlistmentMgr').RemoveMyDirectEnlistment()

    def GetCorpAllowedEnlistmentFactions(self, corporationID):
        return sm.RemoteSvc('fwCharacterEnlistmentMgr').GetCorpAllowedEnlistmentFactions(corporationID)

    def SetCorpAllowedEnlistmentFactions(self, allowedFactionIDs):
        ret = sm.RemoteSvc('fwCharacterEnlistmentMgr').SetMyCorpAllowedEnlistmentFactions(allowedFactionIDs)
        sm.ScatterEvent('OnCorpAllowedEnlistmentFactionsSet')
        return ret

    def OnEnlistMeDirectly(self, factionID):
        ownerName = cfg.eveowners.Get(factionID).name
        headerLabel = GetByLabel('UI/FactionWarfare/JoinConfirmationHeader')
        bodyLabel = GetByLabel('UI/FactionWarfare/JoinConfirmationQuestionDirectEnlistment', factionName=ownerName)
        ret = eve.Message('CustomQuestion', {'header': headerLabel,
         'question': bodyLabel}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            self.RequestDirectEnlistInFaction(factionID)

    def GetEnlistmentCooldownTimestamp(self):
        if self._enlistmentCooldownTimestamp == TIMESTAMP_NOT_SET:
            self._enlistmentCooldownTimestamp = sm.RemoteSvc('fwCharacterEnlistmentMgr').GetMyDirectEnlistmentCooldownTimestamp()
        return self._enlistmentCooldownTimestamp

    def OnEnlistmentCooldownCleared(self):
        self._enlistmentCooldownTimestamp = TIMESTAMP_NOT_SET
