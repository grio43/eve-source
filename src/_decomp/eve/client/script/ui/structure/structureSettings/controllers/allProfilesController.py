#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureSettings\controllers\allProfilesController.py
from eve.client.script.ui.structure.structureSettings.controllers.slimProfileController import SlimStructureProfileController
from signals import Signal
REMOTE_PROFILE_SVC = 'structureProfiles'

class AllStructureProfileController(object):

    def __init__(self):
        self.allSlimProfileControllers = {}
        self.on_profile_saved = Signal(signalName='on_profile_saved')
        self.on_profile_assigned = Signal(signalName='on_profile_assigned')
        self.profileControllersLoad = False
        self.remoteStructureSvc = sm.RemoteSvc(REMOTE_PROFILE_SVC)

    def GetProfiles(self, force = False):
        if not self.profileControllersLoad or force:
            self.BuildProfileDict()
        return self.allSlimProfileControllers.copy()

    def GetProfileKeys(self):
        if not self.profileControllersLoad:
            self.BuildProfileDict()
        return self.allSlimProfileControllers.keys()

    def BuildProfileDict(self, onlyAddMissing = False):
        profileData = self.remoteStructureSvc.GetProfiles()
        for eachProfile in profileData:
            if onlyAddMissing and eachProfile.profileID in self.allSlimProfileControllers:
                continue
            self.AddControllerToDict(eachProfile)

        self.profileControllersLoad = True

    def AddControllerToDict(self, eachProfile):
        profileController = SlimStructureProfileController(eachProfile.profileID, profileData=eachProfile)
        self.allSlimProfileControllers[eachProfile.profileID] = profileController
        profileController.on_profile_saved.connect(self.OnProfileSaved)

    def OnProfileSaved(self, profileID):
        self.GetProfiles(force=True)
        self.on_profile_saved(profileID)

    def GetNewProfileController(self, name, desc):
        profileID = self.remoteStructureSvc.CreateProfile(name, desc)
        if profileID not in self.allSlimProfileControllers:
            self.BuildProfileDict(onlyAddMissing=True)
        return self.allSlimProfileControllers.get(profileID, None)

    def GetSlimProfileController(self, profileID):
        return self.allSlimProfileControllers.get(profileID, None)

    def UpdateProfileIDForStructures(self, profileID, structureIDs):
        self.remoteStructureSvc.ChangeProfiles(structureIDs, profileID)

    def DeleteProfile(self, profileID):
        self.remoteStructureSvc.DeleteProfile(profileID)
        self.allSlimProfileControllers.pop(profileID)

    def DuplicateProfile(self, profileID):
        newProfileID = self.remoteStructureSvc.DuplicateProfile(profileID)
        if newProfileID not in self.allSlimProfileControllers:
            self.BuildProfileDict(onlyAddMissing=True)
        self.OnProfileSaved(newProfileID)

    def Reset(self):
        self.allSlimProfileControllers.clear()
        self.profileControllersLoad = False
