#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderSignatures.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.signatureSystemContentPiece import SignatureSystemContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProviderDungeons import BaseContentProviderDungeons
from eve.common.lib import appConst

class ContentProviderSignatures(BaseContentProviderDungeons):
    contentType = agencyConst.CONTENTTYPE_SIGNATURES
    contentGroup = contentGroupConst.contentGroupSignatures

    def ConstructContentPiece(self, solarSystemID, dungeonInstances):
        return SignatureSystemContentPiece(solarSystemID=solarSystemID, dungeonInstances=dungeonInstances, itemID=solarSystemID, typeID=appConst.typeSystem)

    def _GetAllDungeonInstances(self):
        dungeonInstances = sm.RemoteSvc('dungeonInstanceCacheMgr').GetSignatureInstances()
        result = {}
        for solarsystemID, dungeons in dungeonInstances.iteritems():
            if not dungeons:
                continue
            if isinstance(dungeons, int):
                result[solarsystemID] = [None] * dungeons
            else:
                result[solarsystemID] = dungeons

        currentSystemSites = sm.GetService('sensorSuite').GetSignatures()
        if currentSystemSites:
            result[session.solarsystemid2] = currentSystemSites
        else:
            result.pop(session.solarsystemid2, None)
        return result

    def OnSignalTrackerSignatureUpdate(self, *args):
        self.InvalidateContentPieces()
