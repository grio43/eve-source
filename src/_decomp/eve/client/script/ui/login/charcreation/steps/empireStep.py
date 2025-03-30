#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\steps\empireStep.py
from carbonui.uicore import uicore
import charactercreator.const as ccConst
from eve.client.script.ui.login.charcreation.charCreation import BaseCharacterCreationStep
RACE_INFO_WIDTH = 500

class EmpireStep(BaseCharacterCreationStep):
    __guid__ = 'uicls.EmpireStep'
    stepID = ccConst.EMPIRESTEP

    def ApplyAttributes(self, attributes):
        self.raceID = None
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        self.raceInfoCont = attributes.stepContainer
        info = self.GetInfo()
        if info.raceID:
            self.raceID = info.raceID

    def OnRaceSelected(self, raceID, *args):
        self.raceInfoCont.ExpandRace(raceID)
        self.UpdateRaceInfo(raceID)

    def UpdateRaceInfo(self, raceID):
        self.raceID = raceID
        uicore.layer.charactercreation.controller.Approve()
