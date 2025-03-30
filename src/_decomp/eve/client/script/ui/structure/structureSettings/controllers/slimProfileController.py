#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureSettings\controllers\slimProfileController.py
from eve.client.script.ui.structure.structureSettings.controllers.structureProfileController import StructureProfileController
from eve.client.script.ui.structure.structureSettings.structureSettingsWnd import StructureProfileSettingCont
from signals import Signal
REMOTE_PROFILE_SVC = 'structureProfiles'

class SlimStructureProfileController(object):

    def __init__(self, profileID = None, profileData = None):
        self.profileID = profileID
        self.profileInfo = profileData
        self.on_profile_saved = Signal(signalName='on_profile_saved')

    def GetProfileID(self):
        return self.profileID

    def GetProfileName(self):
        if self.profileInfo:
            return self.profileInfo.name
        return ''

    def GetProfileDescription(self):
        if self.profileInfo:
            return self.profileInfo.description
        return ''

    def IsDefault(self):
        if self.profileInfo:
            return self.profileInfo.isDefault
        return False

    def SetDefaultProfile(self):
        if self.profileInfo:
            if self.IsDefault():
                return
            sm.RemoteSvc(REMOTE_PROFILE_SVC).SetDefaultProfile(self.GetProfileID())

    def GetProfileInfo(self):
        return self.profileInfo

    def GetFullProfileController(self):
        profileData = sm.RemoteSvc(REMOTE_PROFILE_SVC).GetProfileSettings(self.profileID)
        fullProfileController = StructureProfileController(self.profileID, profileSettings=profileData, profileInfo=self.profileInfo)
        fullProfileController.on_profile_saved.connect(self.OnProfileSaved)
        return fullProfileController

    def OnProfileSaved(self, profileID):
        self.on_profile_saved(profileID)

    def UpdateProfile(self, profileID, name, description):
        if self.GetProfileDescription() != description or self.GetProfileName() != name:
            sm.RemoteSvc(REMOTE_PROFILE_SVC).UpdateProfile(profileID, name, description)
        self.on_profile_saved(profileID)


class SlimStructureAllProfilesController(SlimStructureProfileController):

    def GetFullProfileController(self):
        fullProfileController = StructureProfileController(self.profileID, nameAndDecInfo=self.profileInfo)
        return fullProfileController
