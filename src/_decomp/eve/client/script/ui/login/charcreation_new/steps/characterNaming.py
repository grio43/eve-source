#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\characterNaming.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from charactercreator import const as ccConst
from eve.client.script.ui.login.charcreation_new import soundConst
from eve.client.script.ui.login.charcreation_new.charCreation import BaseCharacterCreationStep
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.sidePanelFactionAndSchool import SidePanelFactionAndSchool
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.sidePanelShip import SidePanelShip
from eve.client.script.ui.login.charcreation_new.steps.sections.chooseNameSection import ChooseNameSection
from eve.common.lib import appConst
from localization.util import AmOnChineseServer
import geo2

class CharacterNaming(BaseCharacterCreationStep):
    __guid__ = 'uicls.CharacterNaming'
    __notifyevents__ = ['OnHideUI', 'OnShowUI']
    stepID = ccConst.NAMINGSTEP

    def ApplyAttributes(self, attributes):
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        self.sidePanelFactionAndSchool = None
        leftCont = ContainerAutoSize(name='leftCont', parent=self.leftSide, align=uiconst.TOPLEFT, pos=(50, 100, 436, 0))
        rightCont = Container(name='rightCont', parent=self.rightSide, align=uiconst.TORIGHT, width=520, padRight=50)
        raceID = uicore.layer.charactercreation.controller.raceID
        schoolID = uicore.layer.charactercreation.controller.schoolID
        factionID = appConst.factionByRace[raceID]
        SidePanelShip(parent=leftCont, align=uiconst.TOTOP, factionID=factionID, height=350, padTop=10)
        self.sidePanelFactionAndSchool = SidePanelFactionAndSchool(parent=rightCont, align=uiconst.TOTOP, factionID=factionID, schoolID=schoolID, padding=(100, 50, 0, 0))
        self.nameCont = ChooseNameSection(name='nameSelectionContainer', parent=rightCont, align=uiconst.TOBOTTOM, height=170 if AmOnChineseServer() else 200, padBottom=100, state=uiconst.UI_PICKCHILDREN, opacity=0.0)
        animations.FadeIn(self.nameCont, duration=0.6, timeOffset=1.0)
        PlaySound(soundConst.CUSTOMIZATION_LOOP)

    def _OnResize(self, *args):
        if not self.sidePanelFactionAndSchool:
            return
        if uicore.uilib.desktop.height < 850:
            self.sidePanelFactionAndSchool.HideSchoolPanel()
        else:
            self.sidePanelFactionAndSchool.ShowSchoolPanel()

    def CheckAvailability(self, *args):
        return self.nameCont.CheckAvailability()

    def InitAvatarPositions(self):
        info = self.GetInfo()
        avatar = sm.GetService('character').GetSingleCharactersAvatar(info.charID)
        avatar.translation = (0.0, 0.02, 0.0)
        avatar.rotation = geo2.QuaternionRotationSetYawPitchRoll(0.0, 0.0, 0.0)
        sm.GetService('character').UpdateDoll(info.charID, fromWhere='InitAvatarPositions_Naming', forceUpdate=True)

    def Close(self):
        PlaySound(soundConst.CUSTOMIZATION_LOOP_STOP)
        super(CharacterNaming, self).Close()
