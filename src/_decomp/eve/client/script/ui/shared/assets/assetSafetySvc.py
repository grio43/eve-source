#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\assets\assetSafetySvc.py
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from eve.common.script.sys.eveCfg import IsControllingStructure
from eve.common.script.sys.idCheckers import IsWormholeSystem, IsTriglavianSystem
from eveexceptions import UserError
from inventorycommon.const import containerGlobal

class AssetSafetySvc(Service):
    __guid__ = 'svc.assetSafety'
    __servicename__ = 'assetSafety'
    __notifyevents__ = ['OnAssetSafetyCreated', 'OnAssetSafetyDelivered']
    __dependencies__ = ['objectCaching']

    def Run(self, *args):
        self.wrapNames = {}

    @staticmethod
    def GetItemsInSafetyForCharacter():
        return sm.RemoteSvc('structureAssetSafety').GetItemsInSafetyForCharacter()

    @staticmethod
    def GetItemsInSafetyForCorp():
        return sm.RemoteSvc('structureAssetSafety').GetItemsInSafetyForCorp()

    @staticmethod
    def MoveItemsInStructureToAssetSafetyForCharacter(solarSystemID, structureID):
        if IsControllingStructure() and session.shipid == structureID:
            raise UserError('CannotPutItemsInSafetyWhileControllingStructure')
        itemsAtStructureExceptCurrentShip = [ item for item in sm.GetService('invCache').GetInventory(containerGlobal).ListStationItems(structureID) if item.itemID != session.shipid ]
        if 0 < len(itemsAtStructureExceptCurrentShip):
            if _IsAssetSafetyDisabledInSystem(solarSystemID):
                label = 'ConfirmAssetEjectionCharacter'
            else:
                label = 'ConfirmAssetSafetyCharacter'
            if eve.Message(label, {'structureID': structureID,
             'solarsystemID': solarSystemID}, uiconst.YESNO) == uiconst.ID_YES:
                sm.RemoteSvc('structureAssetSafety').MovePersonalAssetsToSafety(solarSystemID, structureID)
        else:
            raise UserError('NoItemsToPutInAssetSafety')

    @staticmethod
    def MoveItemsInStructureToAssetSafetyForCorp(solarSystemID, structureID):
        if _IsAssetSafetyDisabledInSystem(solarSystemID):
            label = 'ConfirmAssetEjectionCorp'
        else:
            label = 'ConfirmAssetSafetyCorp'
        if eve.Message(label, {'corpName': cfg.eveowners.Get(session.corpid).name,
         'structureID': structureID,
         'solarsystemID': solarSystemID}, uiconst.YESNO) == uiconst.ID_YES:
            sm.RemoteSvc('structureAssetSafety').MoveCorpAssetsToSafety(solarSystemID, structureID)

    def OnAssetSafetyCreated(self, ownerID, solarSystemID, locationID):
        if ownerID == session.corpid:
            self.objectCaching.InvalidateCachedMethodCall('corpmgr', 'GetAssetInventoryForLocation', session.corpid, locationID, 'offices')
            self.objectCaching.InvalidateCachedMethodCall('structureAssetSafety', 'GetItemsInSafetyForCorp')
            sm.ScatterEvent('OnReloadCorpAssets')

    def OnAssetSafetyDelivered(self, ownerID):
        if ownerID == session.corpid:
            self.objectCaching.InvalidateCachedMethodCall('structureAssetSafety', 'GetItemsInSafetyForCorp')
            sm.ScatterEvent('OnReloadCorpAssets')
        elif ownerID == session.charid:
            self.objectCaching.InvalidateCachedMethodCall('structureAssetSafety', 'GetItemsInSafetyForCharacter')

    def GetWrapName(self, wrapID):
        return self.GetWrapNames([wrapID])[wrapID]

    def GetWrapNames(self, wrapIDs):
        missing = set(wrapIDs) - set(self.wrapNames.keys())
        if missing:
            self.wrapNames.update(sm.RemoteSvc('structureAssetSafety').GetWrapNames(wrapIDs))
        return {wrapID:self.wrapNames.get(wrapID) for wrapID in wrapIDs}


def _IsAssetSafetyDisabledInSystem(solarSystemID):
    return IsWormholeSystem(solarSystemID) or IsTriglavianSystem(solarSystemID)
