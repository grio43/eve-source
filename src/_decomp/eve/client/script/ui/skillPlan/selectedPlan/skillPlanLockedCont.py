#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\selectedPlan\skillPlanLockedCont.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.cloneGrade import ORIGIN_SKILLPLAN
from eve.client.script.ui.skillPlan.selectedPlan.lockButton import LOCK_BUTTON_SIZE, SkillPlanLockButton, OmegaLockButton, MissingSkillsLockButton
from eveui import Sprite
from localization import GetByLabel
from signals import Signal
from skills.skillplan.loggers.skillPlanLogger import log_certified_skill_plan_omega_button_clicked
LOCKED_COLOR = eveColor.HOT_RED
UNLOCKED_COLOR = (1.0, 1.0, 1.0, 1.0)

class SkillPlanLockedCont(ContainerAutoSize):
    default_height = LOCK_BUTTON_SIZE
    default_alignMode = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        super(SkillPlanLockedCont, self).ApplyAttributes(attributes)
        self.skillPlan = None
        self.onMissingSkillsButtonSignal = Signal()
        self.lockIndicator = Sprite(parent=self, name='lockIndicator', align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/SkillPlan/lockButtonIndicator.png', width=10, height=19, top=22)
        self.lockIcon = Container(parent=self, name='lockIcon', align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, bgTexturePath='res:/UI/Texture/classes/SkillPlan/lockIcon.png', bgColor=eveColor.HOT_RED, width=26, height=26, top=46)
        Sprite(name='lockIcon', parent=self.lockIcon, align=uiconst.CENTER, pos=(0, 0, 16, 16), texturePath='res:/UI/Texture/classes/Window/btnLock.png')
        self.omegaDot = Sprite(parent=self, name='omegaDot', align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/SkillPlan/lockButtonDot.png', width=4, height=4, top=25, left=85)
        self.missingSkillsDot = Sprite(parent=self, name='missingSkillsDot', align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/SkillPlan/lockButtonDot.png', width=4, height=4, top=25, left=85)
        self.omegaButton = OmegaLockButton(name='omegaButton', parent=self, align=uiconst.TOPLEFT, func=self.OnOmegaButton, left=96)
        self.missingSkillsButton = MissingSkillsLockButton(name='missingSkillsButton', parent=self, align=uiconst.TOPLEFT, func=self.onMissingSkillsButtonSignal, fixedwidth=LOCK_BUTTON_SIZE)

    def OnOmegaButton(self, *args):
        if self.skillPlan.IsCertified():
            log_certified_skill_plan_omega_button_clicked(self.skillPlan.GetID())
        uicore.cmd.OpenCloneUpgradeWindow(ORIGIN_SKILLPLAN)

    def SetSkillPlan(self, skillPlan):
        self.skillPlan = skillPlan

    def Update(self):
        self.UpdateMissingSkillsButton()
        self.UpdateOmegaButton()
        self.UpdateLock()

    def UpdateMissingSkillsButton(self):
        missingSkillbooks = self.skillPlan.GetMissingSkillbooks()
        if missingSkillbooks:
            numMissing = len(missingSkillbooks)
            self.missingSkillsButton.Lock(numMissing)
            self.missingSkillsButton.SetHint(GetByLabel('UI/SkillPlan/SkillbooksMissing', numMissing=numMissing))
        else:
            self.missingSkillsButton.Unlock()
            self.missingSkillsButton.SetHint(GetByLabel('UI/SkillPlan/NoSkillbooksMissing'))

    def UpdateOmegaButton(self):
        numOmegaSkills = self.skillPlan.GetNumOmegaSkills()
        if self.skillPlan.IsOmegaLocked():
            if sm.GetService('cloneGradeSvc').IsOmega():
                self.omegaButton.Unlock()
                self.omegaButton.SetHint(GetByLabel('UI/SkillPlan/NoOmegaMissing'))
            else:
                self.omegaButton.Lock()
                self.omegaButton.SetHint(GetByLabel('UI/SkillPlan/OmegaMissing', numMissing=numOmegaSkills))
        else:
            self.omegaButton.Hide()

    def UpdateLock(self):
        omegaLocked = self.skillPlan.IsOmegaLocked()
        skillbooksMissing = self.skillPlan.IsMissingSkillbooks()
        if not omegaLocked and not skillbooksMissing or not self.omegaButton.display:
            self.lockIcon.Hide()
            self.lockIndicator.Hide()
            self.omegaDot.Hide()
            self.missingSkillsDot.Hide()
        else:
            self._UpdateOmegaDot(omegaLocked)
            self.lockIcon.Show()
            self.lockIndicator.Show()
            self.lockIndicator.SetRGBA(*LOCKED_COLOR)
            self.missingSkillsDot.Show()
            if skillbooksMissing:
                self.missingSkillsDot.SetRGBA(*LOCKED_COLOR)
            else:
                self.missingSkillsDot.SetRGBA(*UNLOCKED_COLOR)

    def _UpdateOmegaDot(self, omegaLocked):
        if self.skillPlan.IsOmega():
            self.omegaDot.Show()
            if omegaLocked:
                self.omegaDot.SetRGBA(*LOCKED_COLOR)
            else:
                self.omegaDot.SetRGBA(*UNLOCKED_COLOR)
        else:
            self.omegaDot.Hide()
