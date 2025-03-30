#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\client\script\localization\localizationClient.py
import blue
from carbon.common.script.sys.service import Service, ROLE_QA
import localization
import localization.settings
from eve.client.script.ui.control.message import ShowQuickMessage
from localization.logger import LogInfo
from uthread2 import StartTasklet

class LocalizationClient(Service):
    __guid__ = 'svc.localizationClient'
    __notifyevents__ = ['OnCharacterSessionChanged', 'OnUpdateLocalizationTextCache']

    def Run(self, memStream = None):
        super(LocalizationClient, self).Run(memStream)
        self.broadcasting = False

    def OnCharacterSessionChanged(self, oldCharacterID, _newCharacterID):
        if oldCharacterID is None:
            if session.role & ROLE_QA == ROLE_QA:
                sm.RemoteSvc('localizationServer').UpdateLocalizationQAWrap(localization.settings.qaSettings.LocWrapSettingsActive())
            hashData = localization.GetHashDataDictionary()
            if len(hashData) > 0 and not blue.pyos.packaged:
                LogInfo('Localization Client: preparing to load initial text and label data from server')
                sm.RemoteSvc('localizationServer').GetAllTextChanges(hashData)
                LogInfo('Localization Client: done asking for initial text and label data from server')

    def OnUpdateLocalizationTextCache(self, cacheData):
        messagePerLanguage, metaDataPerLanguage, labelsDict = cacheData
        if messagePerLanguage or metaDataPerLanguage or labelsDict:
            localization.UpdateTextCache(messagePerLanguage, metaDataPerLanguage, labelsDict)
            if not self.broadcasting:
                self.broadcasting = True
                StartTasklet(self.DeferredBroadcastMessage)

    def DeferredBroadcastMessage(self):
        blue.synchro.SleepWallclock(30000)
        ShowQuickMessage('Your localization content has been updated.')
        self.broadcasting = False
