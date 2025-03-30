#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureSettings\controllers\structureProfileController.py
from collections import defaultdict
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.structureSettings import CanHaveGroups
from eve.client.script.ui.structure.structureSettings.controllers.settingController import SettingController
from localization import GetByLabel
from ownergroups.ownergroupConst import NO_GROUP_ID
from signals import Signal
import structures
import log
REMOTE_SERVICE_NAME = 'structureProfiles'

class StructureProfileController(object):

    def __init__(self, profileID = None, profileInfo = None, profileSettings = None):
        self.profileID = profileID
        self.profileInfo = profileInfo
        self.originalProfileSettings = profileSettings
        self.groupsBySettingID = None
        self.remoteSvc = sm.RemoteSvc(REMOTE_SERVICE_NAME)
        self.on_profile_saved = Signal(signalName='on_profile_saved')
        self.on_groups_added = Signal(signalName='on_groups_added')
        self.on_group_changed = Signal(signalName='on_group_changed')
        self.on_profile_value_changed = Signal(signalName='on_profile_value_changed')

    def SaveProfile(self, profileData):
        if self.profileID is None:
            profileName = self.GetProfileName()
            profileDesc = self.GetProfileDescription()
            profileID = self.remoteSvc.CreateProfile(profileName, profileDesc)
        else:
            self.remoteSvc.SaveProfileSettings(self.profileID, profileData)
            profileID = self.profileID
        self.on_profile_saved(profileID)

    def GetProfileName(self):
        if self.profileInfo:
            return self.profileInfo.name
        return ''

    def GetProfileDescription(self):
        if self.profileInfo:
            return self.profileInfo.description
        return ''

    def GetProfileID(self):
        return self.profileID

    def LoadGroups(self):
        if self.groupsBySettingID is not None:
            return
        self.groupsBySettingID = defaultdict(set)
        if self.originalProfileSettings is None:
            return self.groupsBySettingID
        for settingID in self.originalProfileSettings:
            if settingID not in structures.SETTING_OBJECT_BY_SETTINGID:
                log.LogWarn('Trying to add invalid settingID = %s' % settingID)
                continue
            for groupData in self.originalProfileSettings[settingID]:
                sc = SettingController(settingID, groupData.groupID, groupData.value)
                self.ChangeSignalConnection(sc)
                self.groupsBySettingID[settingID].add(sc)

    def GetAllGroups(self):
        return self.groupsBySettingID.copy()

    def GetGroupsBySettingID(self, settingID):
        self.LoadGroups()
        return self.groupsBySettingID[settingID].copy()

    def GetSettingTextAndIcon(self, settingID):
        labelPath = structures.SETTINGS_LABELS[settingID]
        settingIcon = structures.SETTINGS_TEXTURES.get(settingID, None)
        text = GetByLabel(labelPath)
        descLabelPath = structures.SETTINGS_LABELS_DESC.get(settingID, None)
        return (text, GetByLabel(descLabelPath) if descLabelPath else '', settingIcon)

    def AddNewGroups(self, settingID, groupIDs):
        currentGroups = {g.groupID for g in self.groupsBySettingID[settingID]}
        newGroupIDs = [ gID for gID in groupIDs if gID not in currentGroups ]
        if not newGroupIDs:
            return
        initialValue = 0.0
        settingSpecification = structures.SETTING_OBJECT_BY_SETTINGID[settingID]
        if settingSpecification.valueRange is not None:
            minValue, maxValue = settingSpecification.valueRange
            initialValue = minValue
        for gID in newGroupIDs:
            self.AddGroup(settingID, groupID=gID, doSignal=False, value=initialValue)

        self.on_groups_added(settingID, newGroupIDs)

    def AddGroup(self, settingID, groupID, value = 0.0, doSignal = True):
        if not CanHaveGroups(settingID) and groupID != NO_GROUP_ID:
            return
        existingGroupIDs = {g for g in self.groupsBySettingID[settingID]}
        if groupID in existingGroupIDs:
            return
        sc = SettingController(settingID, groupID, value)
        self.groupsBySettingID[settingID].add(sc)
        self.OnProfileChanged()
        if doSignal:
            self.on_groups_added(settingID, [groupID])

    def RemoveGroup(self, groupController):
        settingID = groupController.GetSettingID()
        if groupController in self.groupsBySettingID[settingID]:
            self.groupsBySettingID[settingID].remove(groupController)
            self.on_group_changed()
            self.OnProfileChanged()

    def ChangeSignalConnection(self, sc, connect = True):
        signalAndCallback = [(sc.on_profile_value_changed, self.OnProfileChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnProfileChanged(self):
        self.on_profile_value_changed()
