#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\essSystemContentPiece.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece

class ESSSystemContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_ESS

    def __init__(self, bountiesOutput, mainBankAmount, reserveBankAmount, reserveBankUnlocked, *args, **kwargs):
        super(ESSSystemContentPiece, self).__init__(*args, **kwargs)
        self.bountiesOutput = bountiesOutput
        self.mainBankAmount = mainBankAmount
        self.reserveBankAmount = reserveBankAmount
        self.reserveBankUnlocked = reserveBankUnlocked

    def GetESSSystemDetails(self):
        return sm.RemoteSvc('dynamicResourceCacheMgr').GetESSSystemDetails(self.solarSystemID)

    def GetDynamicResourceSettings(self):
        return sm.RemoteSvc('dynamicResourceCacheMgr').GetDynamicResourceSettings()

    def GetLocationID(self):
        data = sm.GetService('dynamicResourceSvc').GetESSDataForCurrentSystem()
        if data is None:
            return
        return data.get('beaconID', None)
