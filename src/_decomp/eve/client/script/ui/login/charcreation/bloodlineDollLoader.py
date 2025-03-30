#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\bloodlineDollLoader.py
import eve.client.script.ui.login.charcreation.bloodlineSelector as BS
import grannyLoader
from eve.client.script.paperDoll.paperDollSpawnWrappers import PaperDollCharacter

class BloodlineDollLoader(object):

    def GetClothedDoll(self, raceID, bloodlineID, genderID, scene):
        for bloodline in BS.RACE_PATHS_MAPPING[raceID]:
            resources, blood, poseID = bloodline
            if blood != bloodlineID:
                continue
            else:
                break

        factory = sm.GetService('character').factory
        if genderID == 0:
            doll = PaperDollCharacter.ImportCharacter(factory, scene, resources[0])
        else:
            doll = PaperDollCharacter.ImportCharacter(factory, scene, resources[1])
        self.SetAnimationNetwork(doll.avatar, genderID, poseID)
        return doll

    def SetAnimationNetwork(self, avatar, genderID, poseID):
        grannyLoader.GrannyBloodlineAnimationLoader(avatar, genderID, poseID)
