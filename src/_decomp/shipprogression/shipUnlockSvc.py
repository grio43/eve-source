#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\shipUnlockSvc.py
import os
import blue
import yaml
from carbonui.services.setting import CharSettingBool
from eve.common.script.sys.eveCfg import eveConfig
from eve.common.script.util import notificationconst
from shipprogression.shipUnlockEntry import ShipUnlockEntry
import shipprogression.shipUnlockSignals as shipUnlockSignals
shipUnlockService = None

def GetShipUnlockService(skillSvc = None):
    global shipUnlockService
    if not session.charid:
        return
    if shipUnlockService is None:
        shipUnlockService = ShipUnlockService(skillSvc)
    return shipUnlockService


def ResetShipUnlockService():
    global shipUnlockService
    if shipUnlockService is not None:
        shipUnlockService = None


class ShipUnlockService(object):
    IGNORED_GROUPS = [4, 35]
    __guid__ = 'svc.shipUnlockSvc'
    __notifyevents__ = ['OnSkillsChanged', 'OnSessionReset']

    def __init__(self, skillSvc = None):
        self._skillSvc = skillSvc
        self._dataHandler = _ShipUnlockDataHandler()
        self._skillRequirementByGroupAndFactionID = {}
        self._groupAndFactionIDBySkillID = {}
        self._ignore_setting = CharSettingBool('ShipProgression_Ignore', False)
        self._ConstructSkillRequirements()
        self._InitializeExistingUnlocks()
        sm.RegisterNotify(self)

    def GetSkillSvc(self):
        if self._skillSvc is None:
            self._skillSvc = sm.GetService('skills')
        return self._skillSvc

    def OnSessionReset(self):
        ResetShipUnlockService()
        sm.UnregisterNotify(self)

    def _ConstructSkillRequirements(self):
        for groupID, entry in eveConfig.infoBubbleGroups.iteritems():
            if groupID in self.IGNORED_GROUPS:
                continue
            for factionID, obj in entry['preReqSkills'].iteritems():
                key = (int(factionID), int(groupID))
                skills = obj['skills']
                requirements = {}
                for skillID, info in skills.iteritems():
                    if int(skillID) not in self._groupAndFactionIDBySkillID:
                        self._groupAndFactionIDBySkillID[int(skillID)] = []
                    self._groupAndFactionIDBySkillID[int(skillID)].append(key)
                    requirements[int(skillID)] = info['level']

                self._skillRequirementByGroupAndFactionID[key] = requirements

    def _InitializeExistingUnlocks(self):
        if not self._dataHandler.IsFirstLaunch():
            return
        for shipGroupID in self._skillRequirementByGroupAndFactionID:
            self.CheckForGroupUnlocked(shipGroupID, forceSeen=True)

    def OnSkillsChanged(self, skills):
        shipsUnlocked = 0
        for skillID, skillInfo in skills.iteritems():
            if skillID not in self._groupAndFactionIDBySkillID:
                continue
            for group in self._groupAndFactionIDBySkillID[skillID]:
                if self.CheckForGroupUnlocked(group):
                    shipsUnlocked += self.GetShipCountInGroup(group)

        if shipsUnlocked > 0 and not self._ignore_setting.is_enabled():
            sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeShipGroupUnlocked, data={'unlockCount': shipsUnlocked})

    def GetShipCountInGroup(self, groupID):
        return len(sm.GetService('shipTree').GetShipTypeIDs(groupID[0], groupID[1]))

    def CheckForGroupUnlocked(self, shipGroupID, forceSeen = False):
        shipUnlockEntry = self.GetUnlockEntry(shipGroupID)
        if shipUnlockEntry.unlocked:
            return False
        requirements = self._skillRequirementByGroupAndFactionID[shipGroupID]
        skillSvc = self.GetSkillSvc()
        for skillID, level in requirements.iteritems():
            skill = skillSvc.GetSkill(skillID)
            if skill is None or skill.trainedSkillLevel < level:
                return False

        shipUnlockEntry.SetUnlocked(True)
        if forceSeen or self._ignore_setting.is_enabled():
            shipUnlockEntry.SetSeen(True)
        self._UpdateEntry(shipUnlockEntry)
        shipUnlockSignals.on_group_unlocked(shipUnlockEntry)
        return True

    def GetUnlockEntry(self, shipGroupID):
        return self._dataHandler.GetEntry(shipGroupID)

    def GetUnseenEntries(self):
        return self._dataHandler.GetUnseen()

    def DismissAll(self):
        entries = self._dataHandler.GetUnseen()
        for entry in entries:
            entry.SetSeen(True)

        self._dataHandler.UpdateEntries(entries)
        shipUnlockSignals.on_unlocks_dismissed()

    def MarkAsSeen(self, shipUnlockEntry):
        shipUnlockEntry.SetSeen(True)
        self._UpdateEntry(shipUnlockEntry)
        shipUnlockSignals.on_group_unlock_viewed(shipUnlockEntry)

    def _UpdateEntry(self, shipUnlockEntry):
        self._dataHandler.UpdateEntry(shipUnlockEntry)

    def QA_ResetAll(self):
        self._dataHandler.Clear()


class _ShipUnlockDataHandler(object):

    def __init__(self):
        self._path = os.path.join(blue.paths.ResolvePathForWriting(u'cache:/char_%d.unlocks.yaml' % session.charid))
        self._shipUnlockEntries = {}
        self._fileCreated = False
        if os.path.exists(self._path):
            self._shipUnlockEntries = self._ReadFile()
            if self._shipUnlockEntries is None or len(self._shipUnlockEntries) == 0:
                self._shipUnlockEntries = {}
        else:
            self._fileCreated = True
            newFile = file(self._path, 'w')
            newFile.close()

    def GetEntry(self, shipGroupID):
        if shipGroupID in self._shipUnlockEntries:
            return ShipUnlockEntry(shipGroupID, unlocked=True, seen=self._shipUnlockEntries[shipGroupID])
        return ShipUnlockEntry(shipGroupID, unlocked=False, seen=False)

    def IsFirstLaunch(self):
        return self._fileCreated

    def GetUnseen(self):
        if self._shipUnlockEntries is None or len(self._shipUnlockEntries) == 0:
            return []
        return sorted([ ShipUnlockEntry(key, unlocked=True, seen=seen) for key, seen in self._shipUnlockEntries.iteritems() if not seen ], key=lambda entry: entry.shipGroupID)

    def RemoveEntry(self, shipGroupID):
        self._shipUnlockEntries.pop(shipGroupID)
        self._WriteFile(self._shipUnlockEntries)

    def UpdateEntry(self, unlockEntry):
        self._shipUnlockEntries[unlockEntry.shipGroupID] = unlockEntry.seen
        self._WriteFile(self._shipUnlockEntries)

    def UpdateEntries(self, unlockEntries):
        for entry in unlockEntries:
            self._shipUnlockEntries[entry.shipGroupID] = entry.seen

        self._WriteFile(self._shipUnlockEntries)

    def Clear(self):
        self._shipUnlockEntries = {}
        self._WriteFile(self._shipUnlockEntries)

    def _ReadFile(self, default = None):
        with open(self._path) as openFile:
            data = yaml.load(openFile)
        return data or default

    def _WriteFile(self, data):
        with open(self._path, 'w') as openFile:
            yaml.dump(data, openFile)
