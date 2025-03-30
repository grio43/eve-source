#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\empireSelection\empireSelectionHeader.py
import uthread
from carbonui.uianimations import animations
from eve.client.script.ui.login.charcreation_new import charCreationSignals
from eve.client.script.ui.login.charcreation_new.steps.empireSelection import empireSelectionConst
from eve.client.script.ui.login.charcreation_new.steps.stepHeader import StepHeader
from localization import GetByLabel

class EmpireSelectionHeader(StepHeader):
    default_name = 'EmpireSelectionHeader'
    default_title = GetByLabel('UI/CharacterCreation/EmpireSelection/OriginSelection')
    default_subtitle = ''

    def ApplyAttributes(self, attributes):
        charCreationSignals.onEmpireFactionSelected.connect(self.OnEmpireFactionSelected)
        attributes['title'] = GetByLabel('UI/CharacterCreation/EmpireSelection/OriginSelection')
        attributes['subtitle'] = GetByLabel('UI/CharacterCreation/EmpireSelection/EmpireSelectionDescription')
        super(EmpireSelectionHeader, self).ApplyAttributes(attributes)

    def OnEmpireFactionSelected(self, factionID):
        uthread.new(self.ShowSelectSchoolText)

    def ShowSelectSchoolText(self):
        animations.FadeOut(self, duration=empireSelectionConst.FACTIONSELECT_ANIMATION_DURATION / 2, sleep=True)
        self.caption.text = GetByLabel('UI/CharacterCreation/EmpireSelection/SchoolSelection')
        self.description.text = '<center>' + GetByLabel('UI/CharacterCreation/EmpireSelection/SchoolSelectionDescription')
        animations.FadeIn(self, duration=empireSelectionConst.FACTIONSELECT_ANIMATION_DURATION, timeOffset=empireSelectionConst.FACTIONSELECT_ANIMATION_DURATION * 2)
