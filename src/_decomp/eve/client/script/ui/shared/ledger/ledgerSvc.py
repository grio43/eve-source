#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\ledger\ledgerSvc.py
from caching.memoize import Memoize
from carbon.common.script.sys.service import Service
from utillib import KeyVal

class LedgerSvc(Service):
    __guid__ = 'svc.ledger'
    __servicename__ = 'LedgerSvc'
    __notifyevents__ = ['OnSessionReset']

    def Run(self, memStream = None):
        self.LogInfo('Starting Ledger Service')
        self.personalDataVersion = 0

    def OnSessionReset(self):
        self.GetPersonalData.clear_memoized()
        self.personalDataVersion = 0

    @Memoize(5)
    def GetPersonalData(self):
        self.personalDataVersion += 1
        return (sm.RemoteSvc('characterMiningLedger').GetCharacterLogs(), self.personalDataVersion)

    def GetStructuresForCorpData(self):
        structuresWithMiningEvents = sm.RemoteSvc('corpMiningLedger').GetObserversWithMiningEvents()
        myCorpStructures = {}
        solarSystemIDs = set()
        for eachStructure in structuresWithMiningEvents:
            solarSystemIDs.add(eachStructure.solarSystemID)
            keyVal = KeyVal(itemID=eachStructure.itemID, solarSystemID=eachStructure.solarSystemID, itemName=eachStructure.itemName)
            myCorpStructures[eachStructure.itemID] = keyVal

        return (myCorpStructures, list(solarSystemIDs))

    def GetCorpData(self, structureID):
        return sm.RemoteSvc('corpMiningLedger').GetObserverLedger(structureID)
