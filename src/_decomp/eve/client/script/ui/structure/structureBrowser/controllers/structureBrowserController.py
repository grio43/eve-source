#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\controllers\structureBrowserController.py
from eve.client.script.ui.structure.structureBrowser.controllers.structureEntryController import StructureEntryController
from localization import GetByLabel
from signals import Signal
import carbonui.const as uiconst
import eve.client.script.ui.structure.structureBrowser.browserUIConst as browserUIConst
import structures

class StructureBrowserController(object):
    __notifyevents__ = ['OnStructureStateChanged',
     'OnStructuresReloaded',
     'OnCorporationStructuresReloaded',
     'OnProfileSettingsChange']
    STATION_TYPE_CONFIGID = -const.categoryStation

    def __init__(self):
        self.tabSelected = 0
        self.categoryIDSelected = structures.CATEGORY_HULL_DOCKING
        self.profileChanged = False
        self.selectedProfile = browserUIConst.ALL_PROFILES
        self.on_structure_state_changed = Signal(signalName='on_structure_state_changed')
        self.on_structures_changed = Signal(signalName='on_structures_changed')
        self.on_corp_structures_changed = Signal(signalName='on_corp_structures_changed')
        self.on_category_selected = Signal(signalName='on_category_selected')
        self.on_profile_selected = Signal(signalName='on_profile_selected')
        self.on_profile_deleted = Signal(signalName='on_profile_deleted')
        self.on_default_profile_set = Signal(signalName='on_default_profile_set')
        self.myStructureControllers = {}
        self.allStructuresControllers = {}
        sm.RegisterNotify(self)

    def OnProfileSettingsChange(self, profileIDs):
        currentProfile = self.GetSelectedProfileID()
        if currentProfile in profileIDs:
            if self.HasProfileChanged():
                headerText = GetByLabel('UI/StructureBrowser/ProfileWasModifiedHeader')
                questionText = GetByLabel('UI/StructureBrowser/ProfileWasModifiedBody')
                if eve.Message('CustomQuestion', {'header': headerText,
                 'question': questionText}, uiconst.YESNO) != uiconst.ID_YES:
                    return
            self.selectedProfile = None
            self.SelectProfile(currentProfile, askQuestion=False)

    def GetMyStructures(self):
        structuresInfo = sm.GetService('structureDirectory').GetCorporationStructures()
        stationControllers = self._GetControllersFromStructureList(browserUIConst.IGNORE_RANGE, structuresInfo, self.myStructureControllers)
        return stationControllers

    def GetAllStructures(self, rangeSelected):
        structuresInfo = sm.GetService('structureDirectory').GetStructures()
        stationControllers = self._GetControllersFromStructureList(rangeSelected, structuresInfo, self.allStructuresControllers)
        return stationControllers

    def _GetControllersFromStructureList(self, rangeSelected, structuresInfo, cacheDict):
        cacheDict.clear()
        stationControllers = []

        def IsInRange(info):
            if rangeSelected == browserUIConst.IGNORE_RANGE:
                return True
            if rangeSelected == const.rangeSolarSystem and session.solarsystemid2 != info['solarSystemID']:
                return False
            if rangeSelected == const.rangeConstellation:
                solarsystemInfo = cfg.mapSystemCache.Get(info['solarSystemID'])
                if solarsystemInfo.constellationID != session.constellationid:
                    return False
            return True

        idsToPrime = {eachInfo['structureID'] for eachInfo in structuresInfo.itervalues()}
        idsToPrime.union({eachInfo['solarSystemID'] for eachInfo in structuresInfo.itervalues()})
        cfg.evelocations.Prime(idsToPrime)
        ownersToPrime = {eachInfo['ownerID'] for eachInfo in structuresInfo.itervalues()}
        cfg.eveowners.Prime(ownersToPrime)
        for eachInfo in structuresInfo.itervalues():
            if not IsInRange(eachInfo):
                continue
            eachInfo['services'] = self.PruneServices(eachInfo['typeID'], eachInfo['services'])
            sController = StructureEntryController(eachInfo)
            cacheDict[eachInfo['structureID']] = sController
            stationControllers.append(sController)

        return stationControllers

    @staticmethod
    def PruneServices(structureTypeID, structureServices):
        if structureTypeID in structures.STRUCTURES_WITHOUT_ONLINE_SERVICES:
            return {x:y for x, y in structureServices.iteritems() if x not in structures.ONLINE_SERVICES}
        return structureServices

    def SetTabSelected(self, tabSelected):
        self.tabSelected = tabSelected

    def GetSelectedTab(self):
        return self.tabSelected

    def OnStructureStateChanged(self, solarSystemID, structureID, state):
        sController = self.myStructureControllers.get(structureID, None)
        if sController is None:
            return
        sController.StructureStateChanged(structureID, state)

    def OnStructuresReloaded(self):
        self.on_structures_changed()

    def OnCorporationStructuresReloaded(self):
        self.on_corp_structures_changed()

    def SelectCategory(self, categoryID):
        self.categoryIDSelected = categoryID
        self.on_category_selected(categoryID)

    def GetSelectedCategory(self):
        return self.categoryIDSelected

    def SetProfileChangedValue(self, value):
        self.profileChanged = value

    def HasProfileChanged(self):
        return self.profileChanged

    def PlayerWantsToLeaveProfile(self):
        if not self.HasProfileChanged():
            return True
        headerText = GetByLabel('UI/StructureBrowser/UnsavedChanges')
        questionText = GetByLabel('UI/StructureBrowser/UnsavedChangesQuestion')
        ret = eve.Message('CustomQuestion', {'header': headerText,
         'question': questionText}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            return True
        return False

    def SelectProfile(self, profileID, sendSignal = True, askQuestion = True):
        validProfileIDs = sm.GetService('structureControllers').GetValidProfileIDs()
        if profileID not in validProfileIDs:
            profileID = browserUIConst.ALL_PROFILES
        newProfileSelected = self.selectedProfile != profileID
        if askQuestion and newProfileSelected and not self.PlayerWantsToLeaveProfile():
            return
        if newProfileSelected:
            self.SetProfileChangedValue(False)
        self.selectedProfile = profileID
        if sendSignal:
            self.on_profile_selected(profileID)

    def GetSelectedProfileID(self):
        return self.selectedProfile

    def ProfileDeleted(self, profileID):
        if self.GetSelectedProfileID() == profileID:
            selectedProfileChanged = True
            self.selectedProfile = browserUIConst.ALL_PROFILES
        else:
            selectedProfileChanged = False
        self.on_profile_deleted(profileID, selectedProfileChanged)

    @staticmethod
    def SetProfileSettingsSelected(settingID):
        settings.user.tabgroups.Set(settingID, 1)
        settings.user.tabgroups.Delete('%s_names' % settingID)
        settings.user.tabgroups.Set('profile_structuresAndsettings', 1)
        settings.user.tabgroups.Delete('%s_names' % 'profile_structuresAndsettings')
